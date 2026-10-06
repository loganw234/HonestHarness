from decimal import Decimal

import pytest

from qs.client import Client, LiveGateError, is_local
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
