"""A local, scripted, OpenAI-compatible endpoint for tests.

It listens on 127.0.0.1 only and forwards nothing anywhere. A responder decides
each chat reply. It also keeps a balance and bills each chat call from a price
table, so the runner's reconciliation is exercised end to end without a paid
call; billing at another model's rates simulates a provider routing requests.
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable

from .prices import PriceTable
from .providers.deepseek import parse_usage


@dataclass
class FakeReply:
    status: int = 200
    body: dict | None = None
    stream: list[str] | None = None     # raw SSE lines, sent as they are


def usage_dict(hit: int = 0, miss: int = 10, out: int = 5, reasoning: int = 0) -> dict:
    return {"prompt_tokens": hit + miss, "prompt_cache_hit_tokens": hit,
            "prompt_cache_miss_tokens": miss, "completion_tokens": out,
            "total_tokens": hit + miss + out,
            "completion_tokens_details": {"reasoning_tokens": reasoning}}


def reply(content: str | None = "ok", *, reasoning: str | None = None,
          tool_calls: list[dict] | None = None, finish: str = "stop",
          usage: tuple = (0, 10, 5, 0), model: str = "deepseek-flash",
          fingerprint: str = "fp_fake") -> FakeReply:
    msg: dict = {"role": "assistant", "content": content}
    if reasoning is not None:
        msg["reasoning_content"] = reasoning
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return FakeReply(body={"id": "fake", "object": "chat.completion", "model": model,
                           "system_fingerprint": fingerprint,
                           "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
                           "usage": usage_dict(*usage)})


def stream_reply(content: str = "ok", *, reasoning: str | None = None, finish: str = "stop",
                 usage: tuple = (0, 10, 5, 0), model: str = "deepseek-flash",
                 fingerprint: str = "fp_fake", keepalive: bool = True) -> FakeReply:
    lines = []
    if keepalive:
        lines.append(": keep-alive")
    base = {"id": "fake", "object": "chat.completion.chunk", "model": model,
            "system_fingerprint": fingerprint}
    if reasoning:
        lines.append("data: " + json.dumps({**base, "choices": [
            {"index": 0, "delta": {"reasoning_content": reasoning}, "finish_reason": None}]}))
    lines.append("data: " + json.dumps({**base, "choices": [
        {"index": 0, "delta": {"content": content}, "finish_reason": None}]}))
    lines.append("data: " + json.dumps({**base, "choices": [
        {"index": 0, "delta": {}, "finish_reason": finish}], "usage": usage_dict(*usage)}))
    lines.append("data: [DONE]")
    return FakeReply(stream=lines)


def error(status: int, message: str) -> FakeReply:
    return FakeReply(status=status, body={"error": {"message": message, "type": "fake_error"}})


class FakeServer:
    def __init__(self, responder: Callable[[dict], FakeReply] | None = None, *,
                 balance: str = "12.00", prices: PriceTable | None = None,
                 billing_model: str | None = None, models: list[dict] | None = None,
                 clock: Callable[[], datetime] | None = None):
        self.responder = responder or (lambda body: reply())
        self.balance = Decimal(balance)
        self.prices = prices
        self.billing_model = billing_model
        self.models = models or [{"id": "deepseek-flash", "object": "model",
                                  "name": "DeepSeek-V4.1-Flash"}]
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.requests: list[dict] = []
        self.paths: list[str] = []
        self._lock = threading.Lock()
        self._server: ThreadingHTTPServer | None = None

    # -- billing ------------------------------------------------------------------
    def _bill(self, body: dict, usage: dict | None) -> None:
        if self.prices is None or usage is None:
            return
        model = self.billing_model or body.get("model")
        cost = self.prices.cost(model, self.prices.period(self.clock()), parse_usage(usage))
        with self._lock:
            self.balance -= cost

    def _usage_of(self, fr: FakeReply) -> dict | None:
        if fr.body and fr.status < 400:
            return fr.body.get("usage")
        for line in fr.stream or []:
            if line.startswith("data:") and "usage" in line and line[5:].strip() != "[DONE]":
                u = json.loads(line[5:].strip()).get("usage")
                if u:
                    return u
        return None

    # -- server -------------------------------------------------------------------
    def start(self) -> str:
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, status: int, obj: dict) -> None:
                data = json.dumps(obj).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                fake.paths.append(self.path)
                if self.path.rstrip("/").endswith("/models"):
                    self._send(200, {"object": "list", "data": fake.models})
                elif self.path.rstrip("/").endswith("/user/balance"):
                    self._send(200, {"is_available": True, "balance_infos": [
                        {"currency": "USD", "total_balance": f"{fake.balance:.2f}",
                         "granted_balance": "0.00", "topped_up_balance": f"{fake.balance:.2f}"}]})
                else:
                    self._send(404, {"error": {"message": "not found"}})

            def do_POST(self):
                fake.paths.append(self.path)
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                fake.requests.append(body)
                fr = fake.responder(body)
                fake._bill(body, fake._usage_of(fr))
                if fr.stream is not None and fr.status < 400:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.end_headers()
                    for line in fr.stream:
                        self.wfile.write((line + "\n\n").encode("utf-8"))
                    self.wfile.flush()
                else:
                    self._send(fr.status, fr.body or {})

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def __enter__(self) -> str:
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()
