"""QS6's test support: a synthetic archive in round 6's shape, its data and key,
and a fake endpoint that answers QS6 from them. The other tests/test_qs6*.py
files import it; its own tests check the builders.

Nothing here is round 6's ledger: every line is written for the tests. The
archive has what the real one has: a file whose lines end CRLF, files with and
without a preamble, two entries sharing one stamp, briefs kept before and
after entries, and a keys/ member that must never be read."""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from qs import identity
from qs.fake import FakeServer, reply
from qs.guard import SpendGuard
from qs.prices import PriceTable
from qs.registry import Endpoint
from qs.suite import Runner
from qs.suites import qs6

ROOT = Path(__file__).resolve().parent.parent
PRICES = PriceTable.load(ROOT / "prices" / "deepseek-2026-10-06.json")
OFF_PEAK = datetime(2026, 10, 6, 17, 25, tzinfo=timezone.utc)     # a Tuesday, off-peak
PEAK = datetime(2026, 10, 6, 2, 0, tzinfo=timezone.utc)           # a Tuesday, peak
ZONE = timezone(timedelta(hours=-7))
TOP = "parcelround-r6-ledger/"
KEYS_SENTINEL = "KEYS-SENTINEL-9b1e"
KEY_HASH = "0123456789abcdef" * 4


def _lines(*xs: str) -> str:
    return "\n".join(xs) + "\n"


# name -> (kept time, text). Kept times are DOS times: even seconds.
MEMBERS: dict[str, tuple[tuple, str]] = {
    "README.md": ((2026, 10, 2, 9, 0, 0), _lines(
        "# The synthetic ledger", "", "## The rules", "", "One file per author; stamps from date.")),
    "briefs/P1.md": ((2026, 10, 2, 9, 5, 0), _lines("# P1's brief", "", "## Your job", "", "Write the rows.")),
    "lead.md": ((2026, 10, 2, 11, 0, 0), _lines(
        "# The lead's ledger", "", "Append only.", "",
        "## 2026-10-02 09:10:00 -0700 - the round opens", "",
        "Measured: P0 landed at abc1234.", "",
        "## 2026-10-02 09:30:00 -0700 - verifier-P0 reports", "",
        "Measured: of 9 faults, 7 were caught.",
        "Measured: one gate run took 4.5 s in a tree copy; three passes cost 2.5 M tokens.", "",
        "## 2026-10-02 10:15:00 -0700 - merged", "",
        f"Measured: the merge is def5678; the key's SHA-256 is {KEY_HASH}.", "",
        "## 2026-10-02 11:00:00 -0700 - the last entry", "", "Done.")),
    "verifier-P0.md": ((2026, 10, 2, 10, 15, 0), "\r\n".join([
        "", "## 2026-10-02 09:20:00 -0700 - verifier-P0 starts", "", "It reads.", "",
        "## 2026-10-02 09:40:00 -0700 - its view", "", "Seven caught.", "",
        "## 2026-10-02 10:15:00 -0700 - its last", "", "Done.", ""])),
    "P1.md": ((2026, 10, 2, 10, 30, 0), _lines(
        "# P1", "", "## 2026-10-02 10:30:00 -0700 - P1's design", "", "Design A.", "",
        "## 2026-10-02 10:30:00 -0700 - P1's appendix", "", "Appendix B.")),
    "briefs/P2.md": ((2026, 10, 2, 10, 46, 0), _lines("# P2's brief", "", "Written late.")),
}
KEYS_MEMBER = ("keys/key-abc1234.json", (2026, 10, 2, 10, 0, 0),
               json.dumps({"plants": KEYS_SENTINEL}) + "\n")
CUT_TIMES = {"c016k": "2026-10-02T09:35:00-07:00", "c032k": "2026-10-02T10:20:00-07:00",
             "c064k": "2026-10-02T10:40:00-07:00", "c128k": "2026-10-02T10:50:00-07:00",
             "whole": "2026-10-02T11:00:00-07:00"}


def cite(name: str, marker: str) -> str:
    """file:line of the first line of a synthetic member holding marker."""
    text = MEMBERS[name][1].replace("\r\n", "\n")
    for i, line in enumerate(text.split("\n"), 1):
        if marker in line:
            return f"{name}:{i}"
    raise KeyError(marker)


ITEMS = [
    {"id": "S01", "set": "length", "type": "sha", "question": "At which commit did P0 land?",
     "evidence": [cite("lead.md", "P0 landed at")]},
    {"id": "S02", "set": "length", "type": "count", "question": "Of the 9 faults, how many were caught?",
     "evidence": [cite("lead.md", "7 were caught")]},
    {"id": "S03", "set": "length", "type": "figure", "units": ["s", "sec", "second", "seconds"],
     "question": "How long did one gate run take?", "evidence": [cite("lead.md", "4.5 s")]},
    {"id": "S04", "set": "length", "type": "figure", "units": ["tokens", "token"],
     "question": "What did three passes cost?", "evidence": [cite("lead.md", "2.5 M tokens")]},
    {"id": "S05", "set": "reach", "type": "time", "question": "When is the merge entry stamped?",
     "evidence": [cite("lead.md", "- merged")]},
    {"id": "S06", "set": "reach", "type": "hex", "question": "What are the first eight hex digits of the key's SHA-256?",
     "evidence": [cite("lead.md", "the key's SHA-256")]},
    {"id": "S07", "set": "reach", "type": "file", "question": "Which file holds the entry stamped 2026-10-02 10:30:00?",
     "evidence": [cite("P1.md", "P1's design")]},
    {"id": "S08", "set": "reach", "type": "count", "question": "How many entries has verifier-P0 written?",
     "evidence": [cite("verifier-P0.md", "starts"), cite("verifier-P0.md", "its view"),
                  cite("verifier-P0.md", "its last")]},
]
VALUES = {
    "S01": {"value": "abc1234"}, "S02": {"value": 7},
    "S03": {"value": "4.5", "unit": "s", "written": "4.5 s"},
    "S04": {"value": "2500000", "unit": "tokens", "written": "2.5 M tokens"},
    "S05": {"value": "10:15:00"}, "S06": {"value": "01234567"}, "S07": {"value": "P1.md"},
}
FIRST = {"S01": "c016k", "S02": "c016k", "S03": "c016k", "S04": "c016k", "S05": "c032k",
         "S06": "c032k", "S07": "c064k"}
S08_BY_CUT = {"c016k": 1, "c032k": 3, "c064k": 3, "c128k": 3, "whole": 3}


def build_zip(members=None, *, keys: bool = True) -> bytes:
    members = MEMBERS if members is None else members
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        entries = [(n, kept, text) for n, (kept, text) in members.items()]
        if keys:
            entries.append(KEYS_MEMBER)
        for name, kept, text in entries:
            z.writestr(zipfile.ZipInfo(TOP + name, date_time=kept), text.encode("utf-8"))
    return buf.getvalue()


def source_for(data: bytes, members=None) -> dict:
    """The source spec, computed with hashlib alone, apart from qs6's code."""
    members = MEMBERS if members is None else members
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        raw = {i.filename[len(TOP):]: z.read(i) for i in z.infolist()
               if not i.filename[len(TOP):].startswith("keys/")}
        excluded = sorted(i.filename[len(TOP):] for i in z.infolist()
                          if i.filename[len(TOP):].startswith("keys/"))
    return {
        "qs6_source": 1, "git_blob": hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest(),
        "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "top": TOP,
        "kept_time_zone": "-07:00", "excluded": excluded,
        "members": [{"name": n, "sha256": hashlib.sha256(raw[n]).hexdigest(),
                     "kept": datetime(*members[n][0], tzinfo=ZONE).isoformat()}
                    for n in sorted(raw)],
    }


def key_doc(source: dict, cuts: dict, items=None) -> dict:
    items = ITEMS if items is None else items
    order = list(qs6.CUT_NAMES)
    out = {}
    for it in items:
        iid = it["id"]
        out[iid] = {}
        for cut in qs6.CUT_NAMES:
            if iid == "S08":
                n = S08_BY_CUT[cut]
                out[iid][cut] = {"value": n, "evidence": it["evidence"][:n]}
            elif order.index(cut) >= order.index(FIRST[iid]):
                out[iid][cut] = dict(VALUES[iid], evidence=it["evidence"])
            else:
                out[iid][cut] = {"nil": True}
    return {"qs6_key": 1, "source_sha256": source["sha256"],
            "cuts": {c["name"]: c["sha256"] for c in cuts["cuts"]}, "items": out}


def key_bytes(doc: dict) -> bytes:
    return (json.dumps(doc, indent=1, sort_keys=True) + "\n").encode("utf-8")


def cuts_for(archive: bytes, source: dict, prompt: dict, items=None) -> dict:
    items = ITEMS if items is None else items
    units = qs6.timeline(qs6.read_archive(archive, source))
    cuts = []
    for name in qs6.CUT_NAMES:
        t = datetime.fromisoformat(CUT_TIMES[name])
        text = qs6.cut_text(units, t)
        est = qs6.largest_request(prompt, text, [it["question"] for it in items])
        cuts.append({"name": name, "time": CUT_TIMES[name], "sha256": qs6.sha256_text(text),
                     "p0_largest_request": est,
                     "caps": {"max_prompt_tokens": qs6.MAX_PROMPT_TOKENS,
                              "max_output_tokens": qs6.MAX_OUTPUT_TOKENS,
                              "max_call_prompt_tokens": qs6.cap_for(est)}})
    return {"qs6_cuts": 1, "cuts": cuts}


@dataclass
class World:
    archive: Path
    key: Path
    data: dict
    key_doc: dict
    archive_bytes: bytes

    @property
    def specs(self) -> dict:
        return {it["id"]: it for it in self.data["items"]["items"]}

    def suite(self, cut: str):
        return qs6.CUT_CLASSES[cut](archive=self.archive, key=self.key, data=self.data)


def make_world(tmp_path: Path, *, members=None, items=None, doc_edit=None) -> World:
    """Write a synthetic archive and key under tmp_path, with data naming them.
    doc_edit(doc) may change the key before it is written and hashed."""
    archive = build_zip(members)
    source = source_for(archive, members)
    prompt = qs6.load_data()["items"]["prompt"]
    cuts = cuts_for(archive, source, prompt, items)
    doc = key_doc(source, cuts, items)
    if doc_edit is not None:
        doc_edit(doc)
    kb = key_bytes(doc)
    d = tmp_path / "local"
    d.mkdir(parents=True, exist_ok=True)
    (d / "round6-ledger.zip").write_bytes(archive)
    (d / "qs6_key.json").write_bytes(kb)
    data = {"source": source, "cuts": cuts,
            "items": {"qs6_items": 1, "key_sha256": hashlib.sha256(kb).hexdigest(),
                      "prompt": prompt, "items": ITEMS if items is None else items}}
    return World(d / "round6-ledger.zip", d / "qs6_key.json", data, doc, archive)


# -- a fake endpoint, and a batch through P0's runner ------------------------------------------
def question_of(body: dict) -> str:
    user = body["messages"][1]["content"]
    return user.rsplit("QUESTION: ", 1)[1].split("\n\n", 1)[0]


class Answers:
    """A responder for qs/fake.py. content(item_id, body) gives each reply's
    content, or a FakeReply to send instead. Every request is kept."""

    def __init__(self, world: World, content, *, reasoning=None, finish: str = "stop",
                 usage=(0, 3000, 40, 0)):
        self.by_question = {it["question"]: it["id"] for it in world.data["items"]["items"]}
        self.content, self.reasoning, self.finish, self.usage = content, reasoning, finish, usage
        self.bodies: list[dict] = []

    def __call__(self, body):
        if body["messages"] == identity.PROBE_MESSAGES:
            return reply("ready")
        self.bodies.append(body)
        iid = self.by_question[question_of(body)]
        out = self.content(iid, body)
        if not isinstance(out, str) and out is not None:
            return out
        reasoning = self.reasoning(iid) if callable(self.reasoning) else self.reasoning
        return reply(out, reasoning=reasoning, finish=self.finish, usage=self.usage)


def endpoint(url: str) -> Endpoint:
    return Endpoint(name="fake", provider="deepseek", base_url=url, model="deepseek-flash",
                    price_table="prices/deepseek-2026-10-06.json", key_env=None)


def run(tmp_path: Path, suite, responder, *, thinking: bool = False, repeats: int = 1,
        clock=OFF_PEAK, allow_peak: bool = False):
    srv = FakeServer(responder, prices=PRICES, clock=lambda: clock)
    with srv as url:
        guard = SpendGuard(Decimal("250"), tmp_path / "records" / "spend.jsonl")
        runner = Runner(endpoint(url), PRICES, guard, records_dir=tmp_path / "records",
                        transcripts_dir=tmp_path / "transcripts", clock=lambda: clock,
                        allow_peak=allow_peak, retry_delays=(0, 0))
        summary = runner.run_batch(suite, repeats=repeats, thinking=thinking)
    path = tmp_path / "records" / "runs" / f"{suite.name}.jsonl"
    records = ([json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
               if path.exists() else [])
    return summary, {r["item"]: r for r in records if r["repeat"] == 0}, records


# -- the builders' own tests ----------------------------------------------------------------------
def test_the_synthetic_archive_has_the_real_ones_shapes():
    data = build_zip()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [i.filename for i in z.infolist()]
    assert TOP + KEYS_MEMBER[0] in names and len(names) == len(MEMBERS) + 1
    assert "\r\n" in MEMBERS["verifier-P0.md"][1] and not MEMBERS["verifier-P0.md"][1].startswith("#")
    assert MEMBERS["lead.md"][1].startswith("# The lead's ledger")
    assert MEMBERS["P1.md"][1].count("## 2026-10-02 10:30:00 -0700") == 2


def test_the_synthetic_world_is_one_the_suite_accepts(tmp_path):
    w = make_world(tmp_path)
    qs6.check_data(w.data)
    for cut in qs6.CUT_NAMES:
        s = w.suite(cut)
        assert s.name == f"qs6-{cut}" and len(s.items()) == len(ITEMS)
        assert KEYS_SENTINEL not in s.text
