"""Put QS6's local copy of round 6's ledger in place, check it, and measure its
cuts.

    python tools/qs6_extract.py --parcelround <a ParcelRound checkout>
    python tools/qs6_extract.py --zip <a copy of round6-ledger.zip>
    python tools/qs6_extract.py --cuts
    python tools/qs6_extract.py --unpack <directory>

--parcelround reads archive/round6-ledger.zip at f42242e from that checkout's
object store, with `git show` and GIT_OPTIONAL_LOCKS=0, so it writes nothing
there. --zip reads a file instead, such as one downloaded from the repository.
Either way the archive is refused unless its size, SHA-256, git blob id and
every member match qs/suites/qs6_source.json; then it is written, as it is, to
local/qs6/round6-ledger.zip (gitignored), or to --dest. The suite reads that
file at run time and checks it again.

--cuts renders each cut in qs/suites/qs6_cuts.json from the local copy and
checks its SHA-256, its measures, P0's estimate of its largest request and its
caps against the file. --unpack writes the members outside keys/, each checked,
for a reader such as the key's verifier. keys/ is never read: its members are
known by name only.

Two build modes write the data files from an archive, once, so their values
come from code: --build-source <out> and --build-cuts <out>. Neither is needed
to run the suite.

It prints no absolute path, and only ASCII. Exit status: 0 when everything
holds, 2 when something is refused or differs, 1 for a usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.suites import qs6  # noqa: E402

REPOSITORY = "github.com/loganw234/ParcelRound"
COMMIT = "f42242ecc1707a3d36c52e4b2a3b580ee2783e5b"
ARCHIVE_IN_REPO = "archive/round6-ledger.zip"
TOP = "parcelround-r6-ledger/"
KEPT_ZONE = "-07:00"
ARCHIVE_NAME = "round6-ledger.zip"


def git_blob_id(data: bytes) -> str:
    """The id git gives these bytes as a blob."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def shown(path: Path) -> str:
    """A path as printed: relative to the repository when inside it, else its
    name only, so no absolute path is printed."""
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return f"<outside>/{Path(path).name}"


def fetch_git(checkout: Path, commit: str = COMMIT, path: str = ARCHIVE_IN_REPO) -> bytes:
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    r = subprocess.run(["git", "-C", str(checkout), "show", f"{commit}:{path}"],
                       capture_output=True, env=env, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise qs6.SourceError(f"git show {commit[:7]}:{path} failed in the checkout given")
    return r.stdout


def verify(data: bytes, source: dict) -> dict:
    """The members outside keys/, after every check: size, SHA-256, blob id,
    and each member's hash and kept time (qs6.read_archive)."""
    if git_blob_id(data) != source["git_blob"]:
        raise qs6.SourceError("the archive's git blob id is not the one qs6_source.json records")
    return qs6.read_archive(data, source)


def install(data: bytes, source: dict, dest: Path) -> Path:
    verify(data, source)
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / ARCHIVE_NAME
    tmp = dest / (ARCHIVE_NAME + ".part")
    tmp.write_bytes(data)
    tmp.replace(out)
    if qs6.sha256_bytes(out.read_bytes()) != source["sha256"]:
        raise qs6.SourceError("the written copy's SHA-256 differs from the archive's")
    return out


def unpack(data: bytes, source: dict, dest: Path) -> list[str]:
    """Write each member outside keys/, after the checks, and check it again
    as written. Returns the names written."""
    members = verify(data, source)
    specs = {m["name"]: m for m in source["members"]}
    written = []
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in sorted(members):
            raw = z.read(source["top"] + name)
            target = dest.joinpath(*name.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            if qs6.sha256_bytes(target.read_bytes()) != specs[name]["sha256"]:
                raise qs6.SourceError(f"{name} differs as written")
            written.append(name)
    return written


def build_source(data: bytes) -> dict:
    """qs6_source.json from the archive: its identity, each member outside keys/
    with its hash, size and kept time, and keys/ by name only. For each stamped
    member, its kept time less its last stamp, the evidence for reading kept
    times as -07:00."""
    zone = qs6.kept_zone({"kept_time_zone": KEPT_ZONE})
    members, excluded = [], []
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            if not info.filename.startswith(TOP):
                raise qs6.SourceError("a member outside the archive's top directory")
            name = info.filename[len(TOP):]
            if name.startswith("keys/"):
                excluded.append(name)
                continue
            raw = z.read(info)
            kept = datetime(*info.date_time, tzinfo=zone)
            text = raw.decode("utf-8").replace("\r\n", "\n")
            units = qs6.split_units(name, text, kept)
            m = {"name": name, "bytes": len(raw), "sha256": qs6.sha256_bytes(raw),
                 "kept": kept.isoformat(), "stamped_entries": sum(u.kind == "entry" for u in units)}
            if units[-1].kind == "entry":
                m["last_stamp"] = units[-1].t.isoformat()
                m["kept_minus_last_stamp_s"] = int((kept - units[-1].t).total_seconds())
            members.append(m)
    return {
        "qs6_source": 1,
        "note": ("ParcelRound round 6's archived ledger, the QS6 slice's only source. Hashes, "
                 "sizes and kept times only: none of its text. keys/ members are named and "
                 "never read. The zip keeps DOS times, with no zone; they are read as "
                 "-07:00, the zone of every stamp, and each stamped member's kept time less "
                 "its last stamp is recorded as the evidence (the zip's resolution is two "
                 "seconds). Written by tools/qs6_extract.py --build-source."),
        "repository": REPOSITORY, "commit": COMMIT, "path": ARCHIVE_IN_REPO,
        "git_blob": git_blob_id(data), "bytes": len(data), "sha256": qs6.sha256_bytes(data),
        "top": TOP, "kept_time_zone": KEPT_ZONE,
        "members": sorted(members, key=lambda m: m["name"]), "excluded": sorted(excluded),
    }


def build_cuts(data: bytes, source: dict, items: dict) -> dict:
    """qs6_cuts.json from the archive: each cut's time by bytes / 4, its
    measures and hash, P0's estimate of its largest request, and its caps."""
    members = verify(data, source)
    units = qs6.timeline(members)
    times = qs6.choose_cut_times(units)
    questions = [it["question"] for it in items["items"]]
    cuts = []
    for name in qs6.CUT_NAMES:
        t = times[name]
        text = qs6.cut_text(units, t)
        est = qs6.largest_request(items["prompt"], text, questions)
        cuts.append({
            "name": name, "target_bytes_over_4": qs6.TARGETS.get(name), "time": t.isoformat(),
            "units": len(qs6.cut_units(units, t)), **qs6.measures(text),
            "sha256": qs6.sha256_text(text), "p0_largest_request": est,
            "caps": {"max_prompt_tokens": qs6.MAX_PROMPT_TOKENS,
                     "max_output_tokens": qs6.MAX_OUTPUT_TOKENS,
                     "max_call_prompt_tokens": qs6.cap_for(est)},
        })
    return {
        "qs6_cuts": 1,
        "note": ("The five cuts of round 6's ledger. A cut's time is the latest at which its "
                 "rendered text is at or under its target by UTF-8 bytes / 4, the plan's "
                 "measure; 'whole' is the ledger's last unit. deepseek_ratio is DeepSeek's "
                 "rough 0.3 tokens a character (ds/quick_start_token_usage.txt:11). "
                 "p0_largest_request is P0's estimate_tokens of the cut's longest request, as "
                 "Context.chat makes it; max_call_prompt_tokens is that plus 2%, rounded up to "
                 "a thousand. The API's prompt tokens measure each cut at run time. Written by "
                 "tools/qs6_extract.py --build-cuts."),
        "units_in_ledger": len(units), "cuts": cuts,
    }


def cuts_report(data: bytes, committed: dict) -> tuple[bool, list[str]]:
    """Render each committed cut from the archive and compare it with the
    committed file, field by field."""
    members = verify(data, committed["source"])
    units = qs6.timeline(members)
    questions = [it["question"] for it in committed["items"]["items"]]
    chosen = qs6.choose_cut_times(units)
    ok, lines = True, []
    for spec in committed["cuts"]["cuts"]:
        t = datetime.fromisoformat(spec["time"])
        text = qs6.cut_text(units, t)
        got = {"time": chosen[spec["name"]].isoformat(), "units": len(qs6.cut_units(units, t)),
               **qs6.measures(text), "sha256": qs6.sha256_text(text),
               "p0_largest_request": qs6.largest_request(committed["items"]["prompt"], text,
                                                         questions)}
        got["max_call_prompt_tokens"] = qs6.cap_for(got["p0_largest_request"])
        want = dict(spec, max_call_prompt_tokens=spec["caps"]["max_call_prompt_tokens"])
        bad = [k for k in got if got[k] != want.get(k)]
        ok = ok and not bad
        lines.append(f"{spec['name']:6} {spec['time']}  units {got['units']:3}  chars "
                     f"{got['chars']:7}  bytes/4 {got['bytes_over_4']:7}  P0 {got['p0_largest_request']:7}  "
                     f"cap {got['max_call_prompt_tokens']:7}  sha256 {got['sha256'][:12]}  "
                     + ("ok" if not bad else "DIFFERS: " + ", ".join(bad)))
    return ok, lines


def _write_json(path: Path, obj: dict) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, ensure_ascii=True) + "\n", encoding="utf-8",
                          newline="\n")


def _archive_bytes(a, dest: Path) -> bytes:
    if a.parcelround:
        return fetch_git(Path(a.parcelround))
    if a.zip:
        return Path(a.zip).read_bytes()
    local = dest / ARCHIVE_NAME
    if not local.is_file():
        raise qs6.SourceError(f"no local copy at {shown(local)}: give --parcelround or --zip")
    return local.read_bytes()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--parcelround", metavar="CHECKOUT")
    src.add_argument("--zip", metavar="FILE")
    ap.add_argument("--dest", metavar="DIR", default=str(qs6.LOCAL_DIR))
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--cuts", action="store_true")
    mode.add_argument("--unpack", metavar="DIR")
    mode.add_argument("--build-source", metavar="OUT")
    mode.add_argument("--build-cuts", metavar="OUT")
    a = ap.parse_args(argv)
    dest = Path(a.dest)
    try:
        data = _archive_bytes(a, dest)
        if a.build_source:
            _write_json(Path(a.build_source), build_source(data))
            print(f"wrote {shown(Path(a.build_source))}")
            return 0
        committed = qs6.load_data()
        if a.build_cuts:
            _write_json(Path(a.build_cuts), build_cuts(data, committed["source"], committed["items"]))
            print(f"wrote {shown(Path(a.build_cuts))}")
            return 0
        if a.cuts:
            ok, lines = cuts_report(data, committed)
            print("\n".join(lines))
            print("cuts: " + ("all as qs6_cuts.json records" if ok else "DIFFER from qs6_cuts.json"))
            return 0 if ok else 2
        if a.unpack:
            names = unpack(data, committed["source"], Path(a.unpack))
            print(f"unpacked {len(names)} members, each checked, to {shown(Path(a.unpack))}")
            return 0
        if not (a.parcelround or a.zip):
            ap.error("give --parcelround or --zip to install, or a mode")
        out = install(data, committed["source"], dest)
        print(f"installed {shown(out)}: {len(data)} bytes, sha256 {committed['source']['sha256'][:12]}..., "
              f"{len(committed['source']['members'])} members checked")
        return 0
    except qs6.SourceError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
