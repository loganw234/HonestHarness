"""QS4h's inputs on a synthetic world in this round's shape: the rebuild rule, against a
second route to each copy's SHA; the plants' edits; the replay repositories; the cut,
its brief rebuild, its SHA mapping and its refusals; the two conditions reading alike;
and every refusal of LocalInputs before anything is mounted."""
import json
import os
import shutil
import subprocess

import pytest

from qs.suites import qs4, qs4h
from test_qs4h_support import (STAMPS, build_inputs, build_world, copy_local, g, load_tool, put, sha, tool_args)

rebuild_tool, cut_tool = load_tool("qs4h_rebuild"), load_tool("qs4h_cut")


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    w = build_world(tmp_path_factory.mktemp("qs4h-world"))
    w.expected = build_inputs(w)
    return w


def items_of(w):
    return json.loads(w.items_path.read_text(encoding="utf-8"))


def members_of(w):
    entries = qs4h.snapshot_ledger(w.ledger)
    return {qs4h.LEDGER_ROOT + e["path"]: (e["data"], e["kept"]) for e in entries}


# -- the rebuild rule (A1.3) ----------------------------------------------------------------
def test_each_copy_reproduces_its_key_by_the_rule_and_by_a_second_route(world):
    work = world.local / "work" / "honestharness"
    for p in ("P1", "P2"):
        r = qs4h.rebuild_parcel(work, world.keys[p], world.base)
        assert r["copy"] == world.copies[p]                  # the key's copy_commit, built independently
        assert r["oldest"] == world.oldest[p]


def test_a_squashed_tip_builds_to_a_new_commit_and_a_one_commit_tip_to_itself(world):
    b = world.expected["builds"]
    assert b["P1"] != world.tips["P1"] and b["P2"] == world.tips["P2"]
    work = world.local / "work" / "honestharness"
    raw = g(work, "cat-file", "commit", b["P1"])
    assert f"parent {world.base}\n" in raw and raw.count("parent ") == 1
    assert g(work, "rev-parse", f"{b['P1']}^{{tree}}") == g(work, "rev-parse", f"{world.tips['P1']}^{{tree}}")
    assert "95 tests" in raw                                  # the oldest commit's message, stale as P1's was


def test_a_copy_that_does_not_reproduce_stops_its_planted_item(world, tmp_path):
    """The brief's first control: a key one byte off, and the item stops."""
    work = world.local / "work" / "honestharness"
    bad = json.loads(json.dumps(world.keys["P1"]))
    bad["plants"][2]["new"] = bad["plants"][2]["new"].replace("arguments", "argument")
    with pytest.raises(qs4.InputError, match="not the key's"):
        qs4h.rebuild_parcel(work, bad, world.base)
    wrong_base = json.loads(json.dumps(world.keys["P2"]))
    with pytest.raises(qs4.InputError):
        qs4h.rebuild_parcel(work, wrong_base, world.tips["P1"])
    # through the tool: the parcel stops, its planted item is not built, and the tool says so
    items = items_of(world)
    items["parcels"]["P2"]["copy"] = "0" * 40
    keys = world.ledger / items["parcels"]["P2"]["key"]
    w2 = tmp_path / "w2"
    shutil.copytree(world.ledger, w2 / "ledger")
    key = json.loads(keys.read_text(encoding="utf-8"))
    key["copy_commit"] = "0" * 40
    data = json.dumps(key, indent=2).encode()
    (w2 / "ledger" / items["parcels"]["P2"]["key"]).write_bytes(data)
    items["parcels"]["P2"]["key_sha256"] = sha(data)
    (w2 / "items.json").write_text(json.dumps(items), encoding="utf-8")
    args = tool_args(world)["rebuild"]
    args = [x if x not in (str(world.ledger), str(world.items_path), str(world.local), str(world.expected_path))
            else {str(world.ledger): str(w2 / "ledger"), str(world.items_path): str(w2 / "items.json"),
                  str(world.local): str(w2 / "local"), str(world.expected_path): str(w2 / "e.json")}[x] for x in args]
    assert rebuild_tool.main(args + ["--write-expected"]) == 1
    built = json.loads((w2 / "local" / "built.json").read_text(encoding="utf-8"))
    assert "h2-planted" not in built["items"] and "h2-real" not in built["items"]
    assert "h1-planted" in built["items"]


def test_a_real_tip_build_or_an_edit_that_differs_from_its_pin_is_refused(world, tmp_path):
    """The brief's first control, for the real tip: the rebuilder, pinned values in hand,
    refuses a build that is not the pinned one, and so does an edit's span; prepare()
    refuses a repository whose HEAD is not the item's pinned commit."""
    for key, change in (("builds", lambda e: e["builds"].update(P1="0" * 40)),
                        ("plant_spans", lambda e: e["plant_spans"]["P2-A"][0]["lines"].__setitem__(0, 1))):
        expected = json.loads(world.expected_path.read_text(encoding="utf-8"))
        change(expected)
        p = tmp_path / f"{key}.json"
        p.write_text(json.dumps(expected), encoding="utf-8")
        swap = {str(world.expected_path): str(p), str(world.local): str(tmp_path / f"l-{key}")}
        assert rebuild_tool.main([swap.get(x, x) for x in tool_args(world)["rebuild"]]) == 1
    expected = json.loads(world.expected_path.read_text(encoding="utf-8"))
    expected["repos"]["h1-real"]["commit"] = expected["builds"]["P1"] = world.tips["P1"]
    li = qs4h.LocalInputs(world.local, items=items_of(world), expected=expected, image_id=lambda: "sha256:test-image")
    with pytest.raises(qs4.InputError):
        li.prepare("h1-real")


def test_without_the_gate_the_rebuild_says_no_gate_was_compared(world, tmp_path, capsys):
    """verifier-P5's L1: under --no-gate the tool's last line says that no gate was
    compared, not that every item held, and the items it built hold no gate record."""
    swap = {str(world.local): str(tmp_path / "l")}
    capsys.readouterr()
    assert rebuild_tool.main([swap.get(x, x) for x in tool_args(world)["rebuild"]]) == 0
    last = capsys.readouterr().out.strip().splitlines()[-1]
    assert last.startswith("items: 4 of 4 built, 0 refused; no gate compared (--no-gate)")
    assert "not held" not in last
    built = json.loads((tmp_path / "l" / "built.json").read_text(encoding="utf-8"))
    assert sorted(built["items"]) == ["h1-planted", "h1-real", "h2-planted", "h2-real"]
    assert not any("gate" in b for b in built["items"].values())


def test_a_key_whose_hash_is_not_the_sealed_one_is_refused(world, tmp_path):
    items = items_of(world)
    items["parcels"]["P1"]["key_sha256"] = "0" * 64
    p = tmp_path / "items.json"
    p.write_text(json.dumps(items), encoding="utf-8")
    args = [str(p) if x == str(world.items_path) else x for x in tool_args(world)["rebuild"]]
    assert rebuild_tool.main(args + ["--local", str(tmp_path / "l")]) == 2


def test_a_commit_with_another_header_or_two_roots_is_refused(world, tmp_path):
    work = world.local / "work" / "honestharness"
    raw = g(work, "cat-file", "commit", world.tips["P2"]).encode()
    head, _, msg = raw.partition(b"\n\n")
    odd = g(work, "hash-object", "-t", "commit", "-w", "--stdin", input=head + b"\nencoding ISO-8859-1\n\n" + msg).strip()
    with pytest.raises(qs4.InputError, match="header"):
        qs4h.squash_commit(work, world.base, odd, g(work, "rev-parse", f"{odd}^{{tree}}").strip())
    # two lines of work above the base, neither below the other: no one oldest commit
    a = g(work, "commit-tree", g(work, "rev-parse", f"{world.base}^{{tree}}").strip(), "-p", world.base,
          input=b"a\n").strip()
    b = g(work, "commit-tree", g(work, "rev-parse", f"{world.base}^{{tree}}").strip(), "-p", world.base,
          input=b"b\n").strip()
    m = g(work, "commit-tree", g(work, "rev-parse", f"{a}^{{tree}}").strip(), "-p", a, "-p", b, input=b"m\n").strip()
    with pytest.raises(qs4.InputError, match="not one"):
        qs4h.oldest_above(work, world.base, m)


# -- the plants' edits ------------------------------------------------------------------------
def test_each_edit_is_its_own_span_and_a_deletion_is_its_join(world):
    s = world.expected["plant_spans"]
    assert [e["kind"] for e in s["P1-A"]] == ["replacement", "replacement"] and len(s["P1-B"]) == 1
    assert s["P1-A"][0]["file"] == "qs/cases.json" and s["P1-B"][0]["file"] == "qs/scan.py"
    a, b = s["P2-A"][0], s["P2-B"][0]
    assert a["kind"] == b["kind"] == "deletion"
    assert b["tip_lines"] == [20, 22] and b["lines"] == [19, 20]       # the block's three lines, joined after 19
    assert a["tip_lines"][0] - a["tip_lines"][1] == 0 and a["lines"][1] - a["lines"][0] == 1


def test_qs4s_anchoring_would_place_a_deletion_at_line_1(world):
    """Why the edits come from the line diff: QS4's plant_span anchors on the new text,
    and a deletion's new text is empty (A1.5)."""
    work = world.local / "work" / "honestharness"
    r = qs4h.rebuild_parcel(work, world.keys["P2"], world.base)
    assert qs4.plant_span(r["blobs"]["qs/loop.py"], "") == [1, 1]


def test_a_diff_block_no_single_plant_explains_is_refused(world):
    work = world.local / "work" / "honestharness"
    key = world.keys["P2"]
    r = qs4h.rebuild_parcel(work, key, world.base)
    blobs = {"qs/loop.py": r["blobs"]["qs/loop.py"].replace(b"line_50 = 50\n", b"")}   # an edit no key names
    with pytest.raises(qs4.InputError, match="no single plant"):
        qs4h.plant_edits(work, world.tips["P2"], key, blobs)


def test_a_recorded_findings_lines_follow_the_deletions_to_the_real_tip(world):
    # P2-v1 cites the copy's line 50; the plants removed four lines above it
    assert world.expected["recorded_tip_lines"]["P2-v1"] == [[[54, 54]]]
    assert world.expected["recorded_tip_lines"]["P1-v2"] == [[[5, 6]]]


# -- the repositories ------------------------------------------------------------------------
def test_each_repository_is_one_commit_above_the_base_and_holds_no_forbidden_blob(world):
    built = json.loads((world.local / "built.json").read_text(encoding="utf-8"))
    for iid, e in world.expected["repos"].items():
        repo = world.local / built["items"][iid]["repo"]
        assert qs4.repo_problems(repo, e["commit"], e["tree"], e["objects"], forbidden_blobs=tuple(e["forbidden_blobs"]),
                                 forbidden_names=()) == []
        assert g(repo, "rev-parse", "HEAD^") .strip() == world.base
    # the planted repository holds the planted blobs, never the tip's versions of those files
    p1 = world.expected["repos"]["h1-planted"]
    tip_blob = g(world.hh, "rev-parse", f"{world.tips['P1']}:qs/scan.py").strip()
    assert tip_blob in p1["forbidden_blobs"]


def test_parcelround_is_mounted_as_the_path_the_ledger_names(world):
    built = json.loads((world.local / "built.json").read_text(encoding="utf-8"))
    holder = world.local / built["parcelround"]["dir"]
    assert os.listdir(holder) == [qs4h.PR_DIR]
    assert g(holder / qs4h.PR_DIR, "rev-parse", "HEAD").strip() == world.items["parcelround"]["commit"]


def test_a_documentation_copy_newer_than_the_first_stamp_is_refused(world, tmp_path):
    """Pinned afresh each time, so the digest cannot refuse it: only its time does."""
    ds = tmp_path / "ds"
    shutil.copytree(world.ds, ds)
    put(ds, "late.txt", "a later page\n", "2026-10-06 13:00:01")
    e = tmp_path / "e.json"
    shutil.copy(world.expected_path, e)
    swap = {str(world.ds): str(ds), str(world.local): str(tmp_path / "l"), str(world.expected_path): str(e)}
    args = [swap.get(x, x) for x in tool_args(world)["rebuild"]] + ["--write-expected"]
    assert rebuild_tool.main(args) == 2
    put(ds, "late.txt", "a later page\n", "2026-10-06 12:59:59")
    assert rebuild_tool.main(args) == 0


# -- the cut -----------------------------------------------------------------------------------
def test_the_briefs_are_rebuilt_where_the_mtime_rule_drops_them(world):
    cuts = json.loads((world.local / "cuts.json").read_text(encoding="utf-8"))
    p1 = qs4.read_files(world.local / cuts["h1-planted"]["dir"])
    p2 = qs4.read_files(world.local / cuts["h2-planted"]["dir"])
    for f in ("briefs/_common.md", "briefs/_verifier.md"):
        assert b"lowprio" not in p1[f] and b"15:35:17" not in p1[f]     # rebuilt for P1
        assert b"lowprio" in p2[f]                                      # P2's stamp is after them: as kept
    assert "briefs/late.md" not in p1 and "briefs/late.md" in p2        # the mtime rule
    assert "P1.md" not in p1 and "P2.md" not in p2 and "P2.md" in p1    # the parcel's own file
    assert not any(k.startswith("keys/") for k in list(p1) + list(p2))
    assert b"the keys" not in p1["lead.md"] and b"later" not in p1["verifier-P0.md"]


def test_both_shas_are_mapped_in_every_length_and_the_conditions_read_alike(world):
    cuts = json.loads((world.local / "cuts.json").read_text(encoding="utf-8"))
    pl = qs4.read_files(world.local / cuts["h1-planted"]["dir"])["lead.md"]
    rl = qs4.read_files(world.local / cuts["h1-real"]["dir"])["lead.md"]
    c, t, b = world.copies["P1"], world.tips["P1"], world.expected["builds"]["P1"]
    assert t[:7].encode() not in pl and c.encode() in pl and c[:7].encode() in pl
    assert c[:7].encode() not in rl and c.encode() not in rl and b.encode() in rl and t[:7].encode() not in rl
    assert world.oldest["P1"][:7].encode() in pl and world.oldest["P1"][:7].encode() in rl   # other SHAs stay
    p2 = qs4.read_files(world.local / cuts["h2-planted"]["dir"])["lead.md"]
    assert world.tips["P2"][:12].encode() not in p2 and world.copies["P2"][:12].encode() in p2    # 12 characters too
    assert qs4h.mask_own(qs4.read_files(world.local / cuts["h1-planted"]["dir"]), c) == \
        qs4h.mask_own(qs4.read_files(world.local / cuts["h1-real"]["dir"]), b)


def test_a_cut_that_holds_an_unmapped_sha_or_a_keys_text_is_refused(world, monkeypatch):
    """The brief's fifth control, on each kind of leak."""
    items, keys = items_of(world), world.keys
    members = members_of(world)
    item = qs4h.item_spec(items, "h1-real")
    assert qs4h.cut_for(members, items, world.expected, item, keys)      # as built, it holds
    c, t, b = world.copies["P1"], world.tips["P1"], world.expected["builds"]["P1"]
    # the check behind the mapping: every length and case of the other commits is found
    for leak in (c[:7], c, c[:12], t[:7], t.upper()[:9]):
        assert qs4h.sha_problems({"README.md": b"see " + leak.encode() + b"\n"}, [c, t])
    assert not qs4h.sha_problems({"README.md": b"see " + b[:7].encode() + b" and " + c[:6].encode()}, [c, t])
    # the cut as QS4's rule leaves it names the tip and the copy; without the mapping it is refused
    raw = qs4.build_cut(members, qs4h.LEDGER_ROOT, items["parcels"]["P1"]["stamp"], "P1")
    assert qs4h.sha_problems(raw, [c, t]) == ["lead.md: a SHA the cut should have mapped"]
    monkeypatch.setattr(qs4h, "map_shas", lambda files, shas, own: files)
    with pytest.raises(qs4.InputError, match="should have mapped"):
        qs4h.cut_for(members, items, world.expected, item, keys)
    monkeypatch.undo()
    for text in (keys["P1"]["plants"][2]["old"], keys["P1"]["plants"][0]["new"], keys["P1"]["plants"][1]["shape"]):
        m = dict(members)
        data, kept = m[qs4h.LEDGER_ROOT + "README.md"]
        m[qs4h.LEDGER_ROOT + "README.md"] = (data + text.encode(), kept)
        with pytest.raises(qs4.InputError, match="must not hold"):
            qs4h.cut_for(m, items, world.expected, item, keys)


def test_a_brief_whose_pinned_lines_do_not_hash_is_refused(world):
    items = items_of(world)
    members = members_of(world)
    item = qs4h.item_spec(items, "h1-planted")
    items["briefs_rebuild"]["edits"][0]["lines"][1] += 1                 # one line too many
    with pytest.raises(qs4.InputError, match="not the pinned ones"):
        qs4h.cut_for(members, items, world.expected, item, world.keys)
    items = items_of(world)
    m = dict(members)
    data, kept = m[qs4h.LEDGER_ROOT + "briefs/_common.md"]
    m[qs4h.LEDGER_ROOT + "briefs/_common.md"] = (data + b"an edit since\n", kept)
    with pytest.raises(qs4.InputError, match="pinned on"):
        qs4h.cut_for(m, items, world.expected, item, world.keys)


def test_a_cut_that_lacks_a_brief_its_verifier_read_is_refused(world):
    items = items_of(world)
    members = {k: v for k, v in members_of(world).items() if not k.endswith("briefs/verifier-P2.md")}
    with pytest.raises(qs4.InputError, match="missing"):
        qs4h.cut_for(members, items, world.expected, qs4h.item_spec(items, "h2-planted"), world.keys)


def test_the_cutter_refuses_a_pinned_digest_that_differs(world, tmp_path):
    expected = json.loads(world.expected_path.read_text(encoding="utf-8"))
    expected["cuts"]["h2-real"]["digest"] = "0" * 64
    p = tmp_path / "e.json"
    p.write_text(json.dumps(expected), encoding="utf-8")
    args = [str(p) if x == str(world.expected_path) else x for x in tool_args(world)["cut"]]
    args = [str(tmp_path / "l") if x == str(world.local) else x for x in args]
    assert cut_tool.main(args) == 1


def test_the_ledgers_copy_keeps_each_files_time_at_the_stamps_zone(world):
    entries = {e["path"]: e for e in qs4h.snapshot_ledger(world.ledger)}
    assert entries["briefs/_common.md"]["kept"] == "2026-10-06 16:39:42"
    assert entries["briefs/late.md"]["kept"] == "2026-10-06 13:30:00"
    assert entries["lead.md"]["sha256"] == sha((world.ledger / "lead.md").read_bytes())


# -- the inputs, prepared ------------------------------------------------------------------------
def inputs(w, local, items=None, image="sha256:test-image"):
    return qs4h.LocalInputs(local, items=items or items_of(w),
                            expected=json.loads(w.expected_path.read_text(encoding="utf-8")),
                            image_id=lambda: image)


def test_every_item_prepares_with_its_mounts(world):
    for iid, mounts in (("h1-planted", ["r1-vP1-copy", qs4h.LEDGER_MOUNT, "ds"]),
                        ("h2-real", ["r1-vP2-copy", qs4h.LEDGER_MOUNT, qs4h.PR_MOUNT, "srcrepo"])):
        prep = inputs(world, world.local).prepare(iid)
        assert [m.name for m in prep.mounts] == mounts
        assert prep.facts["gate_held"] is True


@pytest.mark.parametrize("change", ["cut byte", "a ref", "a remote", "gate not held", "another image", "ds byte",
                                    "source byte", "a second directory beside P0", "a missing brief",
                                    "a gate under another pin"])
def test_a_changed_input_is_refused_before_anything_is_mounted(world, tmp_path, change):
    local = copy_local(world, tmp_path / "local")
    built = json.loads((local / "built.json").read_text(encoding="utf-8"))
    cuts = json.loads((local / "cuts.json").read_text(encoding="utf-8"))
    iid = "h2-planted" if change in ("source byte", "a second directory beside P0") else "h1-planted"
    repo = local / built["items"][iid]["repo"]
    image = "sha256:test-image"
    if change == "cut byte":
        f = local / cuts[iid]["dir"] / "lead.md"
        f.write_bytes(f.read_bytes() + b"x")
    elif change == "a ref":
        g(repo, "tag", "t")
    elif change == "a remote":
        g(repo, "remote", "add", "origin", "https://example.invalid/r.git")
    elif change == "gate not held":
        built["items"][iid]["gate"]["held"] = False
        (local / "built.json").write_text(json.dumps(built), encoding="utf-8")
    elif change == "another image":
        image = "sha256:other"
    elif change == "ds byte":
        f = local / built["ds"]["dir"] / "thinking.txt"
        f.write_bytes(f.read_bytes() + b"x")
    elif change == "source byte":
        f = local / built["sources"]["dir"] / "srcrepo" / "docs" / "V.md"
        f.write_bytes(f.read_bytes() + b"x")
    elif change == "a second directory beside P0":
        (local / built["parcelround"]["dir"] / "P1").mkdir()
    elif change == "a missing brief":
        os.remove(local / cuts[iid]["dir"] / "briefs" / "verifier-P1.md")
    elif change == "a gate under another pin":
        built["items"][iid]["gate"]["platform_tests"] = ["tests/t.py::t"]
        (local / "built.json").write_text(json.dumps(built), encoding="utf-8")
    with pytest.raises(qs4.InputError):
        inputs(world, local, image=image).prepare(iid)


def test_the_gate_record_holds_only_when_both_sides_agree_and_leave_nothing(world, tmp_path, monkeypatch):
    """The rebuilder's comparison, without Docker: the host's and the sandbox's results
    stand in, and each way the record must not hold is tried."""
    def side(verdict=("PASS", 2, 2), controls=(2, 2), exit=0, complete=True):
        parsed = {"checks": {"tests": "ok" if verdict[0] == "PASS" else "FAIL"}, "verdict": list(verdict),
                  "controls": list(controls), "control_lines": []}
        return {"exit": exit, "parsed": parsed, "complete": complete, "sha256": "x", "duration_s": 1.0}

    def record(host_kw=None, box_kw=None, removed=True, clean=True):
        monkeypatch.setattr(rebuild_tool, "running_containers", lambda: [])
        monkeypatch.setattr(qs4h, "run_gate_host", lambda repo, work, timeout: {
            "gate": side(**(host_kw or {})), "control": side(**(host_kw or {})), "clean_after": clean})
        monkeypatch.setattr(qs4h, "run_gate_sandbox", lambda repo, mount, scratch, image, timeout, platform_tests: {
            "gate": side(**(box_kw or {})), "control": side(**(box_kw or {})), "removed": removed,
            "image_id": image, "clone": {"exit": 0}})
        repo = world.local / json.loads((world.local / "built.json").read_text(encoding="utf-8"))["items"]["h1-planted"]["repo"]
        return rebuild_tool.gate_record(repo, qs4h.item_spec(items_of(world), "h1-planted"), items_of(world),
                                        tmp_path, "sha256:img", 60)
    ok = record()
    assert ok["held"] and ok["as_original"] and ok["image_id"] == "sha256:img"
    assert not record(box_kw={"verdict": ("FAIL", 1, 2), "exit": 1})["held"]
    assert not record(box_kw={"complete": False})["held"]
    assert not record(removed=False)["held"]
    assert not record(clean=False)["held"]
    both_fail = record(host_kw={"verdict": ("FAIL", 1, 2), "exit": 1}, box_kw={"verdict": ("FAIL", 1, 2), "exit": 1})
    assert both_fail["held"] and not both_fail["as_original"]        # alike, but not what the original recorded


def test_a_pinned_platform_test_holds_only_as_the_sandboxs_one_difference():
    """lead.md 15:13:14: h4's comparison holds with P4's one Linux-only test pinned, and
    only when that test is the sandbox's sole difference."""
    pinned = ["tests/test_x.py::test_y[case]"]
    ok = {"tests": "ok", "schema": "ok", "privacy": "ok"}

    def mode(verdict, checks, controls, exit):
        return {"exit": exit, "complete": True, "parsed": {"checks": checks, "verdict": verdict, "controls": controls,
                                                            "control_lines": []}}
    host = {"gate": mode(["PASS", 3, 3], ok, None, 0), "control": mode(None, {}, [9, 9], 0)}

    def box(**kw):
        b = {"gate": mode(["FAIL", 2, 3], dict(ok, tests="FAIL"), None, 1), "control": mode(None, {}, None, 1),
             "platform": {"without": {"exit": 0, "counts": {"passed": 700}, "complete": True},
                          "alone": {"exit": 1, "counts": {"failed": 1}, "complete": True}}}
        for k, v in kw.items():
            b[k] = v
        return b
    held, detail = qs4h.compare_gate(host, box(), pinned)
    assert held and "pinned platform" in detail
    assert not qs4h.compare_gate(host, box(), [])[0]                      # no pin, no exception
    other = box(gate=mode(["FAIL", 1, 3], dict(ok, tests="FAIL", privacy="FAIL"), None, 1))
    assert not qs4h.compare_gate(host, other, pinned)[0]                 # another check differs
    p = box()["platform"]
    assert not qs4h.compare_gate(host, box(platform=dict(p, without={"exit": 1, "counts": {"failed": 1},
                                                                    "complete": True})), pinned)[0]
    assert not qs4h.compare_gate(host, box(platform=dict(p, alone={"exit": 0, "counts": {"passed": 1},
                                                                  "complete": True})), pinned)[0]
    assert not qs4h.compare_gate(host, box(control=mode(None, {}, [9, 9], 0)), pinned)[0]
    failing_host = dict(host, gate=mode(["FAIL", 2, 3], dict(ok, tests="FAIL"), None, 1))
    assert not qs4h.compare_gate(failing_host, box(), pinned)[0]


STAND_IN_GATE = '''import sys
if "--control" in sys.argv:
    print("controls: 1 of 1 caught")
else:
    print("tests     ok    1 passed")
    print("PASS: 1 of 1 checks hold")
'''


def test_the_hosts_gate_must_leave_its_clone_clean_ignored_files_included(tmp_path, monkeypatch):
    """verifier-P5's F3: a gate that writes even an ignored file leaves its clone
    unclean, and the comparison then does not hold (tools/qs4h_rebuild.py). A gate that
    imports a module of its own stays clean: run_gate_host itself sets
    PYTHONDONTWRITEBYTECODE, as the sandbox does, so no bytecode cache is written."""
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    writes = ('import pathlib\npathlib.Path("out").mkdir(exist_ok=True)\npathlib.Path("out/x.txt").write_text("x")\n'
              + STAND_IN_GATE)
    for name, script, clean in (("quiet", STAND_IN_GATE, True), ("writes", writes, False),
                                ("imports", "import helper\n" + STAND_IN_GATE, True)):
        repo = tmp_path / name / "repo"
        repo.mkdir(parents=True)
        g(repo, "init", "-q", "-b", "main")
        put(repo, ".gitignore", "out/\n")
        put(repo, "tools/check.py", script)
        put(repo, "tools/helper.py", "X = 1\n")
        g(repo, "add", "-A")
        g(repo, "commit", "-q", "-m", "a gate")
        (tmp_path / name / "work").mkdir()
        host = qs4h.run_gate_host(repo, tmp_path / name / "work", timeout=120)
        assert host["gate"]["parsed"]["verdict"] == ["PASS", 1, 1] and host["clean_after"] is clean


def test_the_pytest_count_line_is_read():
    assert qs4h._pytest_counts("1 failed, 750 passed, 16 skipped, 2 errors in 3.10s") == \
        {"failed": 1, "passed": 750, "error": 2}
    assert qs4h._pytest_counts("..........\n") == {}


def test_qs4hs_sandbox_is_p2s_with_home_one_level_deeper(tmp_path):
    """lead.md 15:13:14: HOME=/tmp/home on its own tmpfs, and nothing else changed."""
    from qs.agent import DockerSandbox
    (tmp_path / "s").mkdir()
    ours, p2s = qs4h.QS4hSandbox(tmp_path / "s", [], image="img"), DockerSandbox(tmp_path / "s", [], image="img")
    ours.name, ours.run_id = p2s.name, p2s.run_id
    a, b = ours.run_args(), p2s.run_args()
    assert "HOME=/tmp/home" in a and "HOME=/tmp" not in a and "HOME=/tmp" in b
    i = a.index("--tmpfs", a.index("--tmpfs") + 1)
    assert a[i + 1].startswith("/tmp/home:") and a[i + 2] == "img"
    assert [x for x in a if x not in ("HOME=/tmp/home", "--tmpfs", a[i + 1])] == \
        [x for x in b if x not in ("HOME=/tmp", "--tmpfs")]
    assert qs4h.BuildSandbox(tmp_path / "s", [], image="img").name.startswith("hh-qs4h-")


def test_the_images_record_must_name_the_committed_dockerfile(tmp_path):
    (tmp_path / "image.json").write_text(json.dumps({"id": "sha256:x", "dockerfile_sha256": "0" * 64}),
                                         encoding="utf-8")
    with pytest.raises(qs4.InputError, match="another sandbox"):
        qs4h.current_image_id(tmp_path)
    with pytest.raises(qs4.InputError, match="no image.json"):
        qs4h.current_image_id(tmp_path / "absent")
