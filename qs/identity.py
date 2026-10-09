"""What model answered, as far as a hosted API lets anyone tell.

At each batch's start the runner records the provider's model list, with each
id's display name, and asks one fixed probe, recording the model and system
fingerprint the response reports. Neither field identifies weights: DeepSeek's
own examples echo the alias as `model`, and show two fingerprints for one alias.
So the fingerprint is recorded, and its stability measured, before it serves as
any tripwire; and the guard's billing signature is what tells two models apart.
"""
from __future__ import annotations

PROBE_MESSAGES = [{"role": "user", "content": "Reply with the single word: ready"}]
PROBE_MAX_PROMPT = 64      # the probe's prompt is a few tokens; this bounds its cost
PROBE_MAX_OUTPUT = 16


def display_names(models: list[dict]) -> dict:
    return {m.get("id"): m.get("name") for m in models}


def probe(client, provider, model: str):
    body = provider.build_request(model, PROBE_MESSAGES, thinking=False,
                                  max_tokens=PROBE_MAX_OUTPUT)
    return provider.chat(client, body)
