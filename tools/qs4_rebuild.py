"""The rebuilder: QS4's replay repositories, round 6's plan and the outside
sources, and round 6's gate run on the host and in the sandbox at each repository.

    python tools/qs4_rebuild.py --parcelround <a ParcelRound checkout> --repos <the directory holding
        cft-fp256, HonestFramework and loganw.dev> [--honestharness <a HonestHarness checkout>]
        [--local <dir>] [--write-expected] [--no-gate] [--only ITEM ...]

Run tools/qs4_cut.py first: this reads the archive it wrote, <local>/archive/,
and refuses it unless it is the one qs4_expected.json pins.
1. ParcelRound is cloned with --no-hardlinks into <local>/work/parcelround,
   never as a worktree. Nothing is written in the source. f42242e's tree in the
   clone must equal the source's.
2. Each planted copy is rebuilt, by draft 4's verifier's method (lead.md
   17:47:24): the real tip's commit object, with only its tree line replaced by
   the tip's tree carrying the key's plants, each file's plants in turn. Its SHA
   must equal the key's copy_commit. A copy that does not reproduce it stops its
   item, which is reported, and nothing of it is built.
3. Each item's replay repository is made under <local>/repos/<12 hex digits of
   its commit>/: cloned locally with --no-hardlinks, detached and pruned to the
   commit's closure (qs.suites.qs4.make_replay_repo). It is checked: HEAD, tree,
   object closure, no ref, no remote, a clean working tree, and no archive blob
   and no CASE-STUDY-6.md.
4. Round 6's plan of record is read from HonestHarness at its pinned commit into
   <local>/plan/<digest>/. The outside files are read from <repos>/<name> at their
   pinned commits into <local>/sources/<digest>/<name>/. All are read with
   cat-file blob and GIT_OPTIONAL_LOCKS=0. Nothing is written in those
   repositories, and <repos>/cft-worktrees/ is never read.
5. Unless --no-gate, round 6's gate and its --control run at each repository:
   - on the host, in a fresh clone under <local>/tmp/, with TMP, TEMP and TMPDIR
     there;
   - in a DockerSandbox, the repository mounted read-only as a run mounts it.
   Their verdicts are compared, and the host's with the original verifier's.
   docker ps is read before each container, and each container is removed.
6. It writes <local>/built.json. With --write-expected, made once in phase 2, it
   also records in qs4_expected.json the commits, trees, object counts and file
   lists, the plants' spans, round 6's findings' lines at the real tips, and the
   plan's and the sources' digests. Without it, every value is checked against
   that file.

It prints no absolute path, and exits 0 only when every item it built holds.
"""
from __future__ import annotations

import argparse
import json
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.agent.sandbox import SandboxError  # noqa: E402
from qs.suites import qs4  # noqa: E402


def running_containers() -> list[str]:
    try:
        r = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True,
                           timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        raise qs4.InputError("docker ps did not answer") from None
    if r.returncode != 0:
        raise qs4.InputError("docker ps failed")
    return r.stdout.split()


def gate_record(repo: Path, item: dict, items: dict, work: Path) -> dict:
    """Round 6's gate on the host and in the sandbox at one repository."""
    parcel = items["parcels"][item["parcel"]]
    names = running_containers()
    host = qs4.run_gate_host(repo, work)
    box = qs4.run_gate_sandbox(repo, f"r6-vcopy-{item['parcel']}", work / f"sbx-{secrets.token_hex(4)}")
    held, detail = qs4.compare_gate(host, box)
    og = parcel["original_gate"]
    as_original = (host["gate"]["parsed"]["verdict"] == ["PASS", *og["gate"]]
                   and host["control"]["parsed"]["controls"] == og["control"])
    summary = lambda r: {"exit": r["exit"], "verdict": r["parsed"]["verdict"],  # noqa: E731
                         "controls": r["parsed"]["controls"], "checks": r["parsed"]["checks"],
                         "complete": r["complete"]}
    return {"held": held and box["removed"] and host["clean_after"], "detail": detail,
            "commit": qs4.git(repo, "rev-parse", "HEAD").decode().strip(), "image_id": box.get("image_id"),
            "as_original": as_original, "running_before": len(names), "removed": box["removed"],
            "host_clean_after": host["clean_after"],
            "host": {m: summary(host[m]) for m in ("gate", "control")},
            "sandbox": {m: summary(box[m]) for m in ("gate", "control")}}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--parcelround", required=True, help="a ParcelRound checkout holding f42242e")
    ap.add_argument("--repos", required=True, help="the directory holding the outside sources' repositories")
    ap.add_argument("--honestharness", default=str(ROOT), help="a HonestHarness checkout holding the plan's commit")
    ap.add_argument("--local", default=str(qs4.LOCAL))
    ap.add_argument("--items", default=str(qs4.ITEMS_PATH), help=argparse.SUPPRESS)       # tests' worlds
    ap.add_argument("--expected", default=str(qs4.EXPECTED_PATH), help=argparse.SUPPRESS)
    ap.add_argument("--write-expected", action="store_true")
    ap.add_argument("--no-gate", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args(argv)
    items, local, source = qs4.load_json(Path(a.items)), Path(a.local), Path(a.parcelround)
    expected_path = Path(a.expected)
    expected = qs4.load_json(expected_path) if expected_path.exists() else {"format": 1}
    wanted = [i for i in items["items"] if a.only is None or i["id"] in a.only]
    try:
        members = qs4.archive_members((local / "archive" / "round6-ledger.zip").read_bytes(), expected["archive"])
        keys = qs4.keys_of(members, items)
    except (qs4.InputError, OSError, KeyError) as e:
        print(f"REFUSED: the archive under <local> is missing or not as pinned (run tools/qs4_cut.py first): "
              f"{type(e).__name__}")
        return 2
    # 1. the work clone
    work = local / "work" / "parcelround"
    qs4._remove(work)
    work.parent.mkdir(parents=True, exist_ok=True)
    commit = items["archive"]["parcelround"]
    try:
        qs4.git(work.parent, "clone", "-q", "--no-hardlinks", str(source.resolve()), str(work.resolve()))
        tree = qs4.git(work, "rev-parse", f"{commit}^{{tree}}").decode().strip()
        if tree != qs4.git(source, "rev-parse", f"{commit}^{{tree}}").decode().strip():
            raise qs4.InputError("the clone's f42242e tree differs from the source's")
    except qs4.InputError as e:
        print(f"REFUSED: the work clone of <parcelround>: {e}")
        return 2
    if a.write_expected:
        expected["parcelround_tree"] = tree
    elif expected.get("parcelround_tree") != tree:
        print("REFUSED: f42242e's tree is not the pinned one")
        return 2
    print(f"work clone: <parcelround> cloned with --no-hardlinks; f42242e tree {tree[:12]}: as the source's")
    # 2. the copies, their plants' spans, and round 6's findings at the tips
    stopped, spans, tip_lines = set(), {}, {}
    for p, key in keys.items():
        spec = items["parcels"][p]
        try:
            sha, blobs = qs4.rebuild_copy(work, key)
            for pl in spec["plants"]:
                kp = key["plants"][pl["index"]]
                spans[pl["id"]] = {"file": kp["file"], "lines": qs4.plant_span(blobs[kp["file"]], kp["new"])}
            print(f"{p}: rebuilt {sha[:7]} from tip {spec['tip'][:7]}: REPRODUCED the key's copy_commit; plants at "
                  + ", ".join(f"{spans[pl['id']]['file']}:{spans[pl['id']]['lines'][0]}-"
                              f"{spans[pl['id']]['lines'][1]}" for pl in spec["plants"]))
        except qs4.InputError as e:
            stopped.add(p)
            print(f"{p}: STOPPED, the planted copy does not reproduce: {e}")
            continue
        for r in spec["r6_findings"]:
            if not r["lines"] or r["file"].startswith(("ledger/", "<")):     # the cut's lines, or none
                tip_lines[r["id"]] = r["lines"]
                continue
            a_lines = blobs[r["file"]].split(b"\n") if r["file"] in blobs else \
                qs4.git(work, "cat-file", "blob", f"{spec['copy']}:{r['file']}").split(b"\n")
            b_lines = qs4.git(work, "cat-file", "blob", f"{spec['tip']}:{r['file']}").split(b"\n")
            m = qs4.map_lines(a_lines, b_lines)
            if any(s not in m or e not in m for s, e in r["lines"]):
                print(f"REFUSED: {r['id']} cites a line its file at the copy does not have")
                return 1
            tip_lines[r["id"]] = [[m[s], m[e]] for s, e in r["lines"]]
    if a.write_expected:
        expected["plant_spans"], expected["r6_tip_lines"] = spans, tip_lines
    elif any(expected.get("plant_spans", {}).get(k) != v for k, v in spans.items()) or \
            any(expected.get("r6_tip_lines", {}).get(k) != v for k, v in tip_lines.items()):
        print("REFUSED: a plant's span or a recorded finding's line differs from the pinned one")
        return 1
    # 3. the replay repositories (an earlier build's other items are kept)
    old = local / "built.json"
    built = qs4.load_json(old) if old.is_file() else {"format": 1, "items": {}}
    for item in wanted:
        built["items"].pop(item["id"], None)
    repos = expected.setdefault("repos", {}) if a.write_expected else expected.get("repos", {})
    bad = 0
    for item in wanted:
        iid = item["id"]
        if item["parcel"] in stopped and item["kind"] == "planted":
            print(f"{iid:11} STOPPED: its copy did not reproduce")
            bad += 1
            continue
        c = qs4.item_commit(items, item)
        dest = local / "repos" / c[:12]
        try:
            if not dest.exists():
                qs4.make_replay_repo(work, c, dest)
            facts = {"commit": c, "tree": qs4.git(dest, "rev-parse", "HEAD^{tree}").decode().strip(),
                     "objects": len(qs4.git(dest, "rev-list", "--objects", "HEAD").splitlines()),
                     "files": qs4.repo_files(dest)}
            if a.write_expected:
                repos[iid] = facts
            e = repos.get(iid)
            if e is None or e["commit"] != c:
                raise qs4.InputError("no pinned commit for it, or another")
            probs = qs4.repo_problems(dest, e["commit"], e["tree"], e["objects"],
                                      forbidden_blobs=(expected["archive"]["blob"],))
            if probs or facts["files"] != e["files"]:
                raise qs4.InputError("; ".join(probs) or "its file list differs")
            built["items"][iid] = {"repo": f"repos/{c[:12]}"}
            print(f"{iid:11} repository at {c[:7]}: tree {e['tree'][:12]}, {e['objects']} objects, "
                  f"{len(e['files'])} files, no refs, no remote, clean: ok")
        except qs4.InputError as e:
            bad += 1
            print(f"{iid:11} REFUSED: {e}")
    # 4. the plan and the outside sources
    try:
        plan = qs4.extract_files(Path(a.honestharness), items["plan"]["commit"], [items["plan"]["path"]])
        src: dict[str, bytes] = {}
        for s in items["sources"]:
            for rel, data in qs4.extract_files(Path(a.repos) / s["name"], s["commit"], s["paths"]).items():
                src[f"{s['name']}/{rel}"] = data
    except qs4.InputError as e:
        print(f"REFUSED: the plan or an outside source could not be read: {e}")
        return 2
    plan_sha, src_digest = qs4.sha256(next(iter(plan.values()))), qs4.tree_digest(src)
    if a.write_expected:
        expected["plan"] = {"sha256": plan_sha}
        expected["sources"] = {"digest": src_digest, "files": {k: qs4.sha256(v) for k, v in sorted(src.items())}}
    if expected["plan"]["sha256"] != plan_sha or expected["sources"]["digest"] != src_digest:
        print("REFUSED: the plan or the outside sources are not the pinned ones")
        return 2
    for name, files, digest in (("plan", plan, plan_sha), ("sources", src, src_digest)):
        dest = local / name / digest[:12]
        if dest.exists():
            if qs4.tree_digest(qs4.read_files(dest)) != qs4.tree_digest(files):
                print(f"REFUSED: <local>/{name}/{digest[:12]} holds other files")
                return 2
        else:
            qs4.write_files(files, dest)
        built[name] = {"dir": f"{name}/{digest[:12]}"}
    print(f"plan: {items['plan']['path']} at {items['plan']['commit'][:7]}, sha256 {plan_sha[:12]}: ok")
    print(f"sources: {len(src)} files at " + ", ".join(f"{s['name']}@{s['commit'][:7]}" for s in items["sources"])
          + f", digest {src_digest[:12]}: ok")
    # 5. round 6's gate on the host and in the sandbox
    tmp = local / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    for item in wanted:
        iid = item["id"]
        if iid not in built["items"]:
            continue
        if a.no_gate:
            built["items"][iid]["gate"] = None
            continue
        try:
            g = gate_record(local / built["items"][iid]["repo"], item, items, tmp)
        except (qs4.InputError, SandboxError, subprocess.TimeoutExpired) as e:
            g = {"held": False, "detail": f"{type(e).__name__}: {e}"}     # a sandbox's text is redacted
        built["items"][iid]["gate"] = g
        bad += not (g["held"] and g.get("as_original"))
        hv, bv = (g.get("host") or {}).get("gate", {}), (g.get("sandbox") or {}).get("gate", {})
        hc, bc = (g.get("host") or {}).get("control", {}), (g.get("sandbox") or {}).get("control", {})
        print(f"{iid:11} gate host {hv.get('verdict')} / sandbox {bv.get('verdict')}; control host "
              f"{hc.get('controls')} / sandbox {bc.get('controls')}: "
              f"{'held' if g['held'] else 'NOT HELD'} ({g['detail']}); as the original recorded: "
              f"{g.get('as_original')}")
    qs4._remove(tmp)
    (local / "built.json").write_text(json.dumps(built, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if a.write_expected:
        expected_path.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8",
                                 newline="\n")
        print("wrote qs4_expected.json: repositories, spans, lines, plan and sources")
    print(f"items: {len([i for i in wanted if i['id'] in built['items']])} of {len(wanted)} built; "
          f"{bad} not held")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
