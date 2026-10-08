"""The rebuilder: QS4h's replay repositories, ParcelRound's, the outside sources and
DeepSeek's documentation copies, built under <local> and checked; and the project's
gate run on the host and in the sandbox at each repository.

    python tools/qs4h_rebuild.py --ledger <the round's ledger> --parcelround <a ParcelRound checkout>
        --repos <the directory holding cft-fp256, HonestFramework and loganw.dev> --ds <DeepSeek's copies>
        [--honestharness <a HonestHarness checkout>] [--local <dir>] [--write-expected]
        [--no-gate | --gate-only] [--only ITEM ...] [--gate-timeout SECONDS]

1. The keys are read from <ledger>/keys/, each refused unless its SHA-256 is the hash
   the lead sealed before its verifier's dispatch (qs4h_items.json). Nothing in the
   ledger is written.
2. HonestHarness is cloned with --no-hardlinks into <local>/work/honestharness, never
   as a worktree. Each parcel's copy is rebuilt by A1.3's rule and must reproduce its
   key's copy_commit, or the parcel's planted item stops; its real-tip build is made by
   the same rule with the tip's tree, and for a tip one commit above its base it must
   be the tip itself.
3. Each plant's edits come from the line diff of the planted files against the real
   tip's; each recorded finding's lines are mapped to the real-tip build's.
4. Each item's replay repository is made under <local>/repos/<12 hex of its commit>/
   (qs4.make_replay_repo) and checked (qs4.repo_problems): its forbidden blobs are the
   other condition's versions of the planted files, and the keys.
5. ParcelRound is cloned the same way into <local>/work/parcelround; its f42242e tree
   must equal the source's; its replay repository is <local>/pr/<12 hex>/P0, the
   directory mounted as parcelround-worktrees.
6. The twelve outside files are read at QS4's pins with cat-file and GIT_OPTIONAL_LOCKS=0
   into <local>/sources/<digest>/, and must have QS4's digest. DeepSeek's copies are
   copied into <local>/ds/<digest>/, each refused unless its mtime is before the first
   stamp of an item that mounts them. <repos>/cft-worktrees/ is never read.
7. Unless --no-gate, tools/check.py and its --control run at each repository, on the
   host (a fresh clone, Docker unreachable) and in the sandbox (QS4hSandbox with the
   image recorded by tools/qs4h_image.py, a clone under the scratch); their verdicts are
   compared (qs.suites.qs4h.compare_gate, which accepts a parcel's pinned platform tests
   only as the sandbox's one difference, checked by two pytest runs there), the host's
   with what the original verifier recorded, and each run is timed. `docker ps` is read
   before each container, and each container is removed. --gate-only runs this step
   alone, on repositories already built. --no-gate skips it, and the tool says that no
   gate was compared: the items it built hold no gate record, so QS4h's inputs refuse
   each, and the data test that prepares them skips, until --gate-only runs.
8. It writes <local>/built.json after each item's gate. With --write-expected, made
   once, it records in qs4h_expected.json the builds, the repositories, the plants'
   edits, the recorded findings' lines at the real-tip builds, ParcelRound's repository,
   and the sources' and the ds files' hashes. Without it, every value is checked
   against that file.

It prints no absolute path, and exits 0 only when every item it built holds.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.agent.sandbox import SandboxError  # noqa: E402
from qs.suites import qs4, qs4h  # noqa: E402
from qs.suites.qs4h import InputError, git, sha256  # noqa: E402


def running_containers() -> list[str]:
    try:
        r = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        raise InputError("docker ps did not answer") from None
    if r.returncode != 0:
        raise InputError("docker ps failed")
    return r.stdout.split()


def read_keys(ledger: Path, items: dict) -> dict[str, dict]:
    keys = {}
    for p, spec in items["parcels"].items():
        data = (ledger / spec["key"]).read_bytes()
        if sha256(data) != spec["key_sha256"]:
            raise InputError(f"{spec['key']} is not the key whose hash the lead sealed")
        keys[p] = json.loads(data)
        if (keys[p]["real_tip"], keys[p]["copy_commit"], keys[p]["base"]) != (spec["tip"], spec["copy"], spec["base"]):
            raise InputError(f"{spec['key']} names other commits than qs4h_items.json")
    return keys


def fresh_clone(source: Path, dest: Path) -> None:
    qs4._remove(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    git(dest.parent, "clone", "-q", "--no-hardlinks", str(Path(source).resolve()), str(dest.resolve()))


def forbidden_blobs(work: Path, tip: str, blobs: dict[str, bytes], kind: str, keys_bytes: list[bytes]) -> list[str]:
    """For a planted item, the real tip's versions of the planted files; for a real one,
    the planted versions; for both, the keys."""
    if kind == "planted":
        own = [git(work, "rev-parse", f"{tip}:{f}").decode().strip() for f in blobs]
    else:
        own = [qs4.blob_id(b) for b in blobs.values()]
    return sorted(set(own) | {qs4.blob_id(k) for k in keys_bytes})


def gate_record(repo: Path, item: dict, items: dict, work: Path, image: str, timeout: float) -> dict:
    """The project's gate on the host and in the sandbox at one repository, timed."""
    parcel = items["parcels"][item["parcel"]]
    platform = (parcel.get("platform_failures") or {}).get("tests") or []
    names = running_containers()
    host = qs4h.run_gate_host(repo, work, timeout=timeout)
    box = qs4h.run_gate_sandbox(repo, qs4h.copy_mount(item["parcel"]), work / f"sbx-{secrets.token_hex(4)}",
                                image=image, timeout=timeout, platform_tests=platform)
    held, detail = qs4h.compare_gate(host, box, platform)
    og = parcel["original_gate"]
    as_original = (host["gate"]["parsed"]["verdict"] == ["PASS", *og["gate"]]
                   and host["control"]["parsed"]["controls"] == og["control"])
    summary = lambda r: {"exit": r["exit"], "verdict": r["parsed"]["verdict"],  # noqa: E731
                         "controls": r["parsed"]["controls"], "checks": r["parsed"]["checks"],
                         "complete": r["complete"], "duration_s": r["duration_s"]}
    return {"held": held and box["removed"] and host["clean_after"], "detail": detail,
            "commit": git(repo, "rev-parse", "HEAD").decode().strip(), "image_id": box.get("image_id"),
            "as_original": as_original, "running_before": len(names), "removed": box["removed"],
            "host_clean_after": host["clean_after"], "sandbox_clone": box.get("clone"),
            "platform_tests": platform, "platform": box.get("platform"),
            "host": {m: summary(host[m]) for m in ("gate", "control")},
            "sandbox": {m: summary(box[m]) for m in ("gate", "control")},
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", required=True, help="the round's ledger directory, read only")
    ap.add_argument("--parcelround", help="a ParcelRound checkout holding f42242e")
    ap.add_argument("--repos", help="the directory holding the outside sources' repositories")
    ap.add_argument("--ds", help="DeepSeek's documentation copies")
    ap.add_argument("--honestharness", default=str(ROOT), help="a HonestHarness checkout holding round1")
    ap.add_argument("--local", default=str(qs4h.LOCAL))
    ap.add_argument("--items", default=str(qs4h.ITEMS_PATH), help=argparse.SUPPRESS)       # tests' worlds
    ap.add_argument("--expected", default=str(qs4h.EXPECTED_PATH), help=argparse.SUPPRESS)
    ap.add_argument("--qs4-expected", default=str(qs4.EXPECTED_PATH), help=argparse.SUPPRESS)
    ap.add_argument("--write-expected", action="store_true")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--no-gate", action="store_true")
    mode.add_argument("--gate-only", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--gate-timeout", type=float, default=2400.0)
    a = ap.parse_args(argv)
    items, local = qs4.load_json(Path(a.items)), Path(a.local)
    expected_path = Path(a.expected)
    expected = qs4.load_json(expected_path) if expected_path.exists() else {"format": 1}
    wanted = [i for i in items["items"] if a.only is None or i["id"] in a.only]
    local.mkdir(parents=True, exist_ok=True)
    old = local / "built.json"
    built = qs4.load_json(old) if old.is_file() else {"format": 1, "items": {}}
    bad = 0
    if not a.gate_only:
        if not (a.parcelround and a.repos and a.ds):
            print("REFUSED: --parcelround, --repos and --ds are needed unless --gate-only")
            return 2
        try:
            keys = read_keys(Path(a.ledger), items)
            keys_bytes = [(Path(a.ledger) / s["key"]).read_bytes() for s in items["parcels"].values()]
        except (InputError, OSError, KeyError, ValueError) as e:
            print(f"REFUSED: the keys: {type(e).__name__}: {e}")
            return 2
        print(f"keys: {len(keys)} read, each the hash the lead sealed")
        # 2. the work clone, the copies and the real-tip builds
        work = local / "work" / "honestharness"
        try:
            fresh_clone(Path(a.honestharness), work)
        except InputError as e:
            print(f"REFUSED: the work clone of <honestharness>: {e}")
            return 2
        stopped, rebuilt, builds, spans, tip_lines = set(), {}, {}, {}, {}
        for p, key in keys.items():
            spec = items["parcels"][p]
            try:
                r = qs4h.rebuild_parcel(work, key, spec["base"])
                if len(qs4h.commits_above(work, spec["base"], spec["tip"])) == 1 and r["build"] != spec["tip"]:
                    raise InputError("a tip one commit above its base must build to itself")
                edits = qs4h.plant_edits(work, spec["tip"], key, r["blobs"])
                for pl in spec["plants"]:
                    if pl["key_id"] not in edits:
                        raise InputError(f"{pl['id']} has no edit in the line diff")
                    spans[pl["id"]] = edits.pop(pl["key_id"])
                if edits:
                    raise InputError("the line diff holds an edit no listed plant owns")
                for rf in spec["recorded"]:
                    tip_lines[rf["id"]] = [
                        qs4h.tip_lines_of(pl["lines"], r["blobs"].get(pl["file"]),
                                          git(work, "cat-file", "blob", f"{spec['tip']}:{pl['file']}")
                                          if pl["file"] in r["blobs"] else None)
                        for pl in rf["places"]]
            except InputError as e:
                stopped.add(p)
                print(f"{p}: STOPPED, the copy or its build does not hold: {e}")
                continue
            rebuilt[p], builds[p] = r, r["build"]
            print(f"{p}: rebuilt {r['copy'][:7]} from tip {spec['tip'][:7]} on base {spec['base'][:7]} "
                  f"(message of {r['oldest'][:7]}): REPRODUCED the key's copy_commit; real-tip build "
                  f"{r['build'][:7]}; plants at " + ", ".join(
                      f"{pl['id']} {e['file']}:{e['lines'][0]}-{e['lines'][1]} ({e['kind']})"
                      for pl in spec["plants"] for e in spans[pl["id"]]))
        if a.write_expected:
            expected.update(builds=builds, plant_spans=spans, recorded_tip_lines=tip_lines)
        elif any(expected.get("builds", {}).get(p) != v for p, v in builds.items()) or \
                any(expected.get("plant_spans", {}).get(k) != v for k, v in spans.items()) or \
                any(expected.get("recorded_tip_lines", {}).get(k) != v for k, v in tip_lines.items()):
            print("REFUSED: a build, a plant's edits or a recorded finding's lines differ from the pinned ones")
            return 1
        # 4. the replay repositories
        repos = expected.setdefault("repos", {}) if a.write_expected else expected.get("repos", {})
        for item in wanted:
            iid, p = item["id"], item["parcel"]
            built["items"].pop(iid, None)
            if p in stopped:
                print(f"{iid:11} STOPPED: its parcel's copy or build did not hold")
                bad += 1
                continue
            r = rebuilt[p]
            c = r["copy"] if item["kind"] == "planted" else r["build"]
            dest = local / "repos" / c[:12]
            try:
                if not dest.exists():
                    qs4.make_replay_repo(work, c, dest)
                facts = {"commit": c, "tree": git(dest, "rev-parse", "HEAD^{tree}").decode().strip(),
                         "objects": len(git(dest, "rev-list", "--objects", "HEAD").splitlines()),
                         "files": qs4.repo_files(dest),
                         "forbidden_blobs": forbidden_blobs(work, items["parcels"][p]["tip"], r["blobs"],
                                                            item["kind"], keys_bytes)}
                if a.write_expected:
                    repos[iid] = facts
                e = repos.get(iid)
                if e is None or e != facts:
                    raise InputError("no pinned repository for it, or another")
                probs = qs4.repo_problems(dest, e["commit"], e["tree"], e["objects"],
                                          forbidden_blobs=tuple(e["forbidden_blobs"]), forbidden_names=())
                if probs:
                    raise InputError("; ".join(probs))
                built["items"][iid] = {"repo": f"repos/{c[:12]}"}
                print(f"{iid:11} repository at {c[:7]}: tree {e['tree'][:12]}, {e['objects']} objects, "
                      f"{len(e['files'])} files, no refs, no remote, clean, no forbidden blob: ok")
            except InputError as e:
                bad += 1
                print(f"{iid:11} REFUSED: {e}")
        # 5. ParcelRound
        prc = items["parcelround"]["commit"]
        pwork = local / "work" / "parcelround"
        try:
            fresh_clone(Path(a.parcelround), pwork)
            tree = git(pwork, "rev-parse", f"{prc}^{{tree}}").decode().strip()
            if tree != git(Path(a.parcelround), "rev-parse", f"{prc}^{{tree}}").decode().strip():
                raise InputError("the clone's f42242e tree differs from the source's")
            holder = local / "pr" / prc[:12]
            if not (holder / qs4h.PR_DIR).exists():
                qs4.make_replay_repo(pwork, prc, holder / qs4h.PR_DIR)
            pr = {"commit": prc, "tree": tree,
                  "objects": len(git(holder / qs4h.PR_DIR, "rev-list", "--objects", "HEAD").splitlines()),
                  "files": qs4.repo_files(holder / qs4h.PR_DIR)}
            if a.write_expected:
                expected["parcelround"] = pr
            if expected.get("parcelround") != pr:
                raise InputError("ParcelRound's repository is not the pinned one")
            probs = qs4.repo_problems(holder / qs4h.PR_DIR, pr["commit"], pr["tree"], pr["objects"],
                                      forbidden_names=())
            if probs or sorted(os.listdir(holder)) != [qs4h.PR_DIR]:
                raise InputError("; ".join(probs) or "its holder holds more than P0")
            built["parcelround"] = {"dir": f"pr/{prc[:12]}"}
            print(f"parcelround: {prc[:7]}, tree {tree[:12]}, {pr['objects']} objects, {len(pr['files'])} files: ok")
        except InputError as e:
            print(f"REFUSED: ParcelRound: {e}")
            return 2
        # 6. the outside sources and DeepSeek's copies
        try:
            src: dict[str, bytes] = {}
            for s in items["sources"]:
                for rel, data in qs4.extract_files(Path(a.repos) / s["name"], s["commit"], s["paths"]).items():
                    src[f"{s['name']}/{rel}"] = data
            digest = qs4.tree_digest(src)
            if digest != qs4.load_json(Path(a.qs4_expected))["sources"]["digest"]:
                raise InputError("the outside sources are not the ones QS4 pins")
            ds = qs4.read_files(Path(a.ds))
            first = min(items["parcels"][i["parcel"]]["stamp"] for i in items["items"]
                        if "ds" in items["parcels"][i["parcel"]]["inputs"])
            late = [n for n in ds if qs4h.kept_time(os.stat(Path(a.ds) / n).st_mtime) > first]
            if late:
                raise InputError(f"{len(late)} of DeepSeek's copies postdate the first dispatch that mounts them")
        except (InputError, OSError) as e:
            print(f"REFUSED: the outside sources or DeepSeek's copies: {e}")
            return 2
        ds_digest = qs4.tree_digest(ds)
        if a.write_expected:
            expected["sources"] = {"digest": digest, "files": {k: sha256(v) for k, v in sorted(src.items())}}
            expected["ds"] = {"digest": ds_digest, "files": {k: sha256(v) for k, v in sorted(ds.items())}}
        if expected["sources"]["digest"] != digest or expected["ds"]["digest"] != ds_digest:
            print("REFUSED: the sources or DeepSeek's copies are not the pinned ones")
            return 2
        for name, files, d in (("sources", src, digest), ("ds", ds, ds_digest)):
            dest = local / name / d[:12]
            if dest.exists():
                if qs4.tree_digest(qs4.read_files(dest)) != d:
                    print(f"REFUSED: <local>/{name}/{d[:12]} holds other files")
                    return 2
            else:
                qs4.write_files(files, dest)
            built[name] = {"dir": f"{name}/{d[:12]}"}
        print(f"sources: {len(src)} files at QS4's pins, digest {digest[:12]}, as QS4's: ok")
        print(f"ds: {len(ds)} files, each before {first}, digest {ds_digest[:12]}: ok")
        if a.write_expected:
            save(expected_path, expected)
            print("wrote qs4h_expected.json: builds, edits, lines, repositories, ParcelRound, sources and ds")
        save(old, built)
    # 7. the gate on the host and in the sandbox
    if not a.no_gate:
        try:
            image = qs4h.current_image_id(local)
        except InputError as e:
            print(f"REFUSED: the image: {e}")
            return 2
        tmp = local / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        for item in wanted:
            iid = item["id"]
            b = built["items"].get(iid)
            if not b:
                continue
            repo = local / b["repo"]
            e = expected.get("repos", {}).get(iid)
            probs = qs4.repo_problems(repo, e["commit"], e["tree"], e["objects"],
                                      forbidden_blobs=tuple(e["forbidden_blobs"]), forbidden_names=()) if e else ["unpinned"]
            if probs:
                print(f"{iid:11} REFUSED before the gate: {'; '.join(probs)}")
                bad += 1
                continue
            try:
                g = gate_record(repo, item, items, tmp, image, a.gate_timeout)
            except (InputError, SandboxError, subprocess.TimeoutExpired, OSError) as ex:
                g = {"held": False, "detail": f"{type(ex).__name__}: {ex}"}
            b["gate"] = g
            save(old, built)
            bad += not (g["held"] and g.get("as_original"))
            h, s = g.get("host") or {}, g.get("sandbox") or {}
            dur = lambda side, m: (side.get(m) or {}).get("duration_s")  # noqa: E731
            print(f"{iid:11} gate host {(h.get('gate') or {}).get('verdict')} / sandbox "
                  f"{(s.get('gate') or {}).get('verdict')}; control host {(h.get('control') or {}).get('controls')} "
                  f"/ sandbox {(s.get('control') or {}).get('controls')}: {'held' if g['held'] else 'NOT HELD'} "
                  f"({g['detail']}); as the original recorded: {g.get('as_original')}; seconds host "
                  f"{dur(h, 'gate')}+{dur(h, 'control')}, sandbox {dur(s, 'gate')}+{dur(s, 'control')}")
        qs4._remove(tmp)
    save(old, built)
    n = len([i for i in wanted if i["id"] in built["items"]])
    if a.no_gate:
        print(f"items: {n} of {len(wanted)} built, {bad} refused; no gate compared (--no-gate), so no item "
              "prepares until --gate-only records its gate")
    else:
        print(f"items: {n} of {len(wanted)} built; {bad} not held")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
