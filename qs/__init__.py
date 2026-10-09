"""Qualification suites (QS) for HonestHarness: measure which models can hold
which roles, with every number recorded against the stack that produced it.

The package's pieces:
- record:     the run record, one JSON line per item run, held to a schema;
- registry:   endpoints, one per (model, provider, version);
- prices:     pinned price tables and the provider's rate periods;
- guard:      the spending guard - cost per call, refusal, reconciliation;
- keys:       the provider key, read only in live mode, never written;
- client:     HTTP, with the live gate: no paid host without live mode;
- providers:  what each provider needs beyond the OpenAI format;
- identity:   what model answered, as far as a hosted API lets anyone tell;
- suite:      the suite interface, and the runner that drives batches;
- fake:       a local scripted endpoint, so tests never reach a paid API.
"""

__version__ = "0.1.0"
