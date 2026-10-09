"""The endpoint registry: one entry per (model, provider, version).

A hosted model's version cannot be pinned on every provider (DeepSeek upgrades
names in place), so an entry pins what can be pinned - the model name, the
base URL, the price table - and the run records carry what each response
reports, which is the rest.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Endpoint:
    name: str
    provider: str
    base_url: str
    model: str
    price_table: str
    key_env: str | None


def load(path: str | Path = "registry.json") -> dict[str, Endpoint]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = {}
    for e in data["endpoints"]:
        ep = Endpoint(name=e["name"], provider=e["provider"], base_url=e["base_url"],
                      model=e["model"], price_table=e["price_table"], key_env=e.get("key_env"))
        if ep.name in out:
            raise ValueError(f"registry names {ep.name} twice")
        out[ep.name] = ep
    return out
