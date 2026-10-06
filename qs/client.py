"""HTTP to an OpenAI-compatible endpoint, behind the live gate.

The gate: a host that is not this machine is a provider, and a provider is
reached only when the caller is in live mode and holds a reservation from the
spending guard. A read-only reservation allows GET requests only (the balance
and the model list, which cost nothing), so no POST, and so no paid call, can
happen without a guard reservation for its batch. Local hosts (the fake
endpoint) need neither, and never see a key.
"""
from __future__ import annotations

from typing import Iterator
from urllib.parse import urlparse

import httpx

from .guard import Reservation
from .keys import read_key, redact

LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class LiveGateError(Exception):
    """A call the live gate refuses."""


class ProviderError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status = status
        self.body = body


def is_local(base_url: str) -> bool:
    return urlparse(base_url).hostname in LOCAL_HOSTS


class Client:
    def __init__(self, base_url: str, *, key_env: str | None = None, live: bool = False,
                 reservation: Reservation | None = None, timeout: float = 600.0):
        self.base_url = base_url.rstrip("/")
        self.local = is_local(self.base_url)
        self.reservation = reservation
        secret = None
        if not self.local:
            host = urlparse(self.base_url).hostname
            if not live:
                raise LiveGateError(f"{host} is a provider host: live mode is required")
            if not isinstance(reservation, Reservation):
                raise LiveGateError("live mode needs a reservation from the spending guard")
            if not key_env:
                raise LiveGateError("live mode needs the name of the key's variable")
            secret = read_key(key_env, live=live)
        self._secret = secret
        headers = {"Content-Type": "application/json"}
        if secret:
            headers["Authorization"] = f"Bearer {secret}"
        self._http = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    # -- the gate on each request -------------------------------------------------
    def _check_post(self) -> None:
        if not self.local and (self.reservation is None or self.reservation.readonly):
            raise LiveGateError("a read-only reservation allows no paid call")

    # -- requests -----------------------------------------------------------------
    def get(self, path: str) -> dict:
        return self._json(self._http.get(path))

    def post(self, path: str, body: dict) -> dict:
        self._check_post()
        return self._json(self._http.post(path, json=body))

    def stream_lines(self, path: str, body: dict) -> Iterator[str]:
        self._check_post()
        with self._http.stream("POST", path, json=body) as r:
            if r.status_code >= 400:
                r.read()
                raise ProviderError(r.status_code, redact(r.text, self._secret))
            for line in r.iter_lines():
                yield line

    def _json(self, r: httpx.Response) -> dict:
        if r.status_code >= 400:
            raise ProviderError(r.status_code, redact(r.text, self._secret))
        return r.json()

    def redact(self, text: str) -> str:
        return redact(text, self._secret)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
