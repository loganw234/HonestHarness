"""The provider key: read only in live mode, never written anywhere.

The key lives in an environment variable the owner sets. A process started
before the variable was set does not inherit it, so on Windows the machine and
user environments are read from the registry as well. Nothing here returns the
key except read_key(), and nothing here logs it.
"""
from __future__ import annotations

import os
import sys


class KeyUnavailable(Exception):
    pass


def read_key(env_name: str, *, live: bool) -> str:
    if not live:
        raise KeyUnavailable("a key is read only in live mode")
    value = os.environ.get(env_name) or _windows_env(env_name)
    if not value:
        raise KeyUnavailable(f"{env_name} is not set")
    return value


def key_present(env_name: str) -> bool:
    """Whether the variable is set, without returning its value."""
    return bool(os.environ.get(env_name) or _windows_env(env_name))


def redact(text: str, secret: str | None) -> str:
    """Remove a secret from text before it is written anywhere."""
    if not secret:
        return text
    return text.replace(secret, "<redacted>")


def _windows_env(name: str) -> str | None:
    if sys.platform != "win32":
        return None
    import winreg
    places = [
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        (winreg.HKEY_CURRENT_USER, r"Environment"),
    ]
    for hive, sub in places:
        try:
            with winreg.OpenKey(hive, sub) as k:
                value, _ = winreg.QueryValueEx(k, name)
                if value:
                    return str(value)
        except OSError:
            continue
    return None
