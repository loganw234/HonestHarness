"""HTTP to an OpenAI-compatible endpoint, behind the live gate.

The gate: a host that is not this machine is a provider, and a provider is
reached only when the caller is in live mode and holds a reservation from the
spending guard. Every request goes to the client's base URL: a path that names
its own host or scheme is refused, so no request reaches a host the gate did
not judge. A read-only reservation allows only the free reads (the balance and
the model list), so no POST, and so no paid call, can happen without a guard
reservation for its batch. Local hosts (the fake endpoint) need neither, and
never see a key.

Errors leave this module redacted: a provider's error body, and a transport
error's text, with the key removed and the original exception's chain cut.
"""
from __future__ import annotations

from typing import Iterator
from urllib.parse import urlparse

import httpx

from .guard import Reservation
from .keys import read_key, redact

LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
FREE_READS = frozenset({"/models", "/user/balance"})


class LiveGateError(Exception):
    """A call the live gate refuses."""


class ProviderError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status = status
        self.body = body


class TransportError(Exception):
    """A request that failed below HTTP: refused, timed out, or cut off. Its
    text is redacted, and it carries no chain to the library's exception."""


def is_local(base_url: str) -> bool:
    return urlparse(base_url).hostname in LOCAL_HOSTS


def _relative(path: str) -> str:
    p = urlparse(path)
    if p.scheme or p.netloc or path.startswith("//") or not path.startswith("/"):
        raise LiveGateError("a request path must be relative to the client's base URL")
    return path


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
    def _check_get(self, path: str) -> str:
        path = _relative(path)
        if not self.local and path.rstrip("/") not in FREE_READS:
            raise LiveGateError(f"GET {path} is not one of the free reads")
        return path

    def _check_post(self, path: str) -> str:
        path = _relative(path)
        if not self.local and (self.reservation is None or self.reservation.readonly):
            raise LiveGateError("a read-only reservation allows no paid call")
        return path

    def _transport(self, e: httpx.HTTPError) -> TransportError:
        return TransportError(f"{type(e).__name__}: {self.redact(str(e))}")

    # -- requests -----------------------------------------------------------------
    def get(self, path: str) -> dict:
        path = self._check_get(path)
        try:
            r = self._http.get(path)
        except httpx.HTTPError as e:
            raise self._transport(e) from None
        return self._json(r)

    def post(self, path: str, body: dict) -> dict:
        path = self._check_post(path)
        try:
            r = self._http.post(path, json=body)
        except httpx.HTTPError as e:
            raise self._transport(e) from None
        return self._json(r)

    def stream_lines(self, path: str, body: dict) -> Iterator[str]:
        path = self._check_post(path)
        try:
            with self._http.stream("POST", path, json=body) as r:
                if r.status_code >= 400:
                    r.read()
                    raise ProviderError(r.status_code, redact(r.text, self._secret))
                for line in r.iter_lines():
                    yield line
        except httpx.HTTPError as e:
            raise self._transport(e) from None

    def _json(self, r: httpx.Response) -> dict:
        if r.status_code >= 400:
            raise ProviderError(r.status_code, redact(r.text, self._secret))
        try:
            return r.json()
        except ValueError:
            raise TransportError(f"HTTP {r.status_code} with a body that is not JSON") from None

    def redact(self, text: str) -> str:
        return redact(text, self._secret)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
