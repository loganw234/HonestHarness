import socket
from decimal import Decimal

import httpx
import pytest

from qs.client import Client, LiveGateError, ProviderError, TransportError, is_local
from qs.fake import FakeReply, FakeServer
from qs.guard import Reservation
from qs.keys import KeyUnavailable, read_key, redact

# A variable name no one sets; tests never touch the real key's variable.
TEST_VAR = "QS_TEST_ONLY_KEY_VARIABLE"


def test_local_hosts():
    assert is_local("http://127.0.0.1:8080")
    assert is_local("http://localhost:1")
    assert not is_local("https://api.deepseek.com")


def test_provider_host_needs_live_mode():
    with pytest.raises(LiveGateError):
        Client("https://api.deepseek.com")


def test_live_mode_needs_a_reservation():
    with pytest.raises(LiveGateError):
        Client("https://api.deepseek.com", live=True, key_env=TEST_VAR)


def test_readonly_reservation_refuses_a_post(monkeypatch):
    monkeypatch.setenv(TEST_VAR, "dummy-value")
    ro = Reservation(batch="b", amount=Decimal("0"), readonly=True)
    c = Client("https://api.deepseek.com", live=True, key_env=TEST_VAR, reservation=ro)
    with pytest.raises(LiveGateError):
        c.post("/chat/completions", {})       # refused before any network I/O
    with pytest.raises(LiveGateError):
        next(c.stream_lines("/chat/completions", {}))
    c.close()


def test_local_client_has_no_key():
    c = Client("http://127.0.0.1:9", key_env=TEST_VAR)
    assert c._secret is None
    c.close()


def test_key_is_read_only_in_live_mode(monkeypatch):
    monkeypatch.setenv(TEST_VAR, "dummy-value")
    with pytest.raises(KeyUnavailable):
        read_key(TEST_VAR, live=False)
    assert read_key(TEST_VAR, live=True) == "dummy-value"


def test_missing_key(monkeypatch):
    monkeypatch.delenv(TEST_VAR, raising=False)
    with pytest.raises(KeyUnavailable):
        read_key(TEST_VAR, live=True)


def test_redact():
    assert redact("Authorization: Bearer abc123", "abc123") == "Authorization: Bearer <redacted>"
    assert redact("nothing", None) == "nothing"


def test_key_is_stripped_and_inner_whitespace_refused(monkeypatch):
    monkeypatch.setenv(TEST_VAR, "dummy-value \n")
    assert read_key(TEST_VAR, live=True) == "dummy-value"
    monkeypatch.setenv(TEST_VAR, "dummy value")
    with pytest.raises(KeyUnavailable) as e:
        read_key(TEST_VAR, live=True)
    assert "dummy" not in str(e.value)


def test_a_request_path_must_be_relative():
    c = Client("http://127.0.0.1:9")
    for path in ("http://127.0.0.1:9/x", "https://api.deepseek.com/chat/completions",
                 "//api.deepseek.com/x", "chat/completions"):
        with pytest.raises(LiveGateError):
            c.post(path, {})
        with pytest.raises(LiveGateError):
            c.get(path)
        with pytest.raises(LiveGateError):
            next(c.stream_lines(path, {}))
    c.close()


def test_readonly_reservation_allows_only_the_free_reads(monkeypatch):
    monkeypatch.setenv(TEST_VAR, "dummy-value")
    ro = Reservation(batch="b", amount=Decimal("0"), readonly=True)
    c = Client("https://provider.invalid", live=True, key_env=TEST_VAR, reservation=ro)
    with pytest.raises(LiveGateError):
        c.get("/user/other")      # refused before any network I/O
    c.close()


def test_provider_error_bodies_are_redacted():
    secret = "dummy-secret-value-123"
    reply = FakeReply(status=400, body={"error": {"message": "bad key " + secret}})
    with FakeServer(lambda body: reply) as url:
        c = Client(url)
        c._secret = secret            # as if it had been read in live mode
        with pytest.raises(ProviderError) as e:
            c.post("/chat/completions", {})
        c.close()
    assert secret not in str(e.value) and secret not in e.value.body


def test_transport_errors_are_redacted_and_cut_from_their_chain():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()                         # nothing listens on this port now
    c = Client(f"http://127.0.0.1:{port}")
    with pytest.raises(TransportError) as e:
        c.get("/models")
    assert e.value.__cause__ is None and e.value.__suppress_context__
    secret = "dummy-secret-value-123"
    c._secret = secret

    def boom(*a, **k):
        raise httpx.LocalProtocolError(f"Illegal header value b'Bearer {secret} '")
    c._http.get = boom
    with pytest.raises(TransportError) as e:
        c.get("/models")
    assert secret not in str(e.value)
    c.close()
