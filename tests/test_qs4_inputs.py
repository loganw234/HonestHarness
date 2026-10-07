"""QS4's inputs: the cut, the archive's pins, the rebuild of a planted copy, the
replay repository and its assertions, and the local inputs a run mounts. Each
check is shown failing on a planted state, on a synthetic world in round 6's
shape (test_qs4_support.py)."""
import json
import os

import pytest

from qs.suites import qs4
from test_qs4_support import (LEDGER, P1_PLANTS, build_inputs, build_world, copy_local, g, put,
                              remove_tree)


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    w = build_world(tmp_path_factory.mktemp("qs4world"))
    expected = build_inputs(w)
    return w, expected


def members_of(w):
    return qs4.archive_members(w.archive, json.loads(w.expected_path.read_text(encoding="utf-8"))["archive"])


# -- the cut -------------------------------------------------------------------------
def test_a_cut_holds_what_the_verifier_found_at_its_dispatch(world):
    w, _ = world
    files = qs4.build_cut(members_of(w), LEDGER, "2026-10-02 22:00:00", "P1")
    assert sorted(files) == ["P2.md", "README.md", "briefs/P1.md", "briefs/_verifier.md", "lead.md",
                             "verifier-P0.md"]
    lead = files["lead.md"].decode()
    assert "22:00:00" in lead and "22:05:00" not in lead and "22:30:00" not in lead   # cut at the stamp
    assert b"22:10:00" not in files["verifier-P0.md"] and b"19:00:00" in files["verifier-P0.md"]
    assert b"\r\n" in files["P2.md"]                         # bytes as archived, CRLF kept


def test_an_unstamped_file_enters_at_its_kept_time_and_not_a_second_before(world):
    w, _ = world
    m = members_of(w)
    assert "briefs/late.md" not in qs4.build_cut(m, LEDGER, "2026-10-02 22:59:59", "P1")
    assert "briefs/late.md" in qs4.build_cut(m, LEDGER, "2026-10-02 23:00:00", "P1")


def test_keys_and_the_parcels_own_file_never_enter(world):
    w, _ = world
    files = qs4.build_cut(members_of(w), LEDGER, "2026-10-03 23:59:59", "P1")
    assert not any(k.startswith("keys/") for k in files) and "P1.md" not in files and "P2.md" in files


def test_stamps_out_of_order_are_refused(world):
    w, _ = world
    m = dict(members_of(w))
    bad = b"# x\n\n## 2026-10-02 21:00:00 -0700 - b\n\nx\n\n## 2026-10-02 20:00:00 -0700 - a\n\ny\n"
    m[LEDGER + "verifier-P9.md"] = (bad, "2026-10-02 21:00:00")
    with pytest.raises(qs4.InputError, match="out of order"):
        qs4.build_cut(m, LEDGER, "2026-10-02 22:00:00", "P1")


def test_a_real_tips_cut_names_the_tip_where_the_lead_named_the_copy(world):
    w, _ = world
    files = qs4.build_cut(members_of(w), LEDGER, "2026-10-02 22:00:00", "P1")
    c, t = w.copies["P1"][:7], w.tips["P1"][:7]
    out = qs4.substitute_sha(files, c, t)
    assert out["lead.md"].count(t.encode()) == 1 and c.encode() not in out["lead.md"]
    assert {k: v for k, v in out.items() if k != "lead.md"} == {k: v for k, v in files.items() if k != "lead.md"}


@pytest.mark.parametrize("times", [0, 2], ids=["absent", "twice"])
def test_the_substitution_must_happen_exactly_once(world, times):
    w, _ = world
    files = qs4.build_cut(members_of(w), LEDGER, "2026-10-02 22:00:00", "P1")
    c = w.copies["P1"][:7].encode()
    files["lead.md"] = files["lead.md"].replace(c, b"zzzzzzz") + (c + b"\n") * times
    with pytest.raises(qs4.InputError, match="exactly once"):
        qs4.substitute_sha(files, c.decode(), w.tips["P1"][:7])


@pytest.mark.parametrize("plant", ["keys", "parcel", "later", "text", "sha"])
def test_a_cut_holding_what_it_must_not_is_refused(world, plant):
    w, _ = world
    files = qs4.build_cut(members_of(w), LEDGER, "2026-10-02 22:00:00", "P1")
    absent = [P1_PLANTS[1]["old"].encode(), w.tips["P1"][:7].encode()]
    if plant == "keys":
        files["keys/key-x.json"] = b"{}"
    elif plant == "parcel":
        files["P1.md"] = b"# P1\n"
    elif plant == "later":
        files["lead.md"] += b"\n## 2026-10-02 22:30:00 -0700 - later\n\nx\n"
    elif plant == "text":
        files["README.md"] += b"it found five wrong answers\n"
    else:
        files["README.md"] += w.tips["P1"][:7].encode()
    assert qs4.cut_problems(files, "2026-10-02 22:00:00", "P1", absent)


# -- the archive -------------------------------------------------------------------
@pytest.mark.parametrize("change", ["byte", "member"])
def test_an_archive_that_is_not_the_pinned_one_is_refused(world, change):
    w, expected = world
    data = w.archive
    if change == "byte":
        data = data[:-1] + bytes([data[-1] ^ 1])
        with pytest.raises(qs4.InputError, match="pins"):
            qs4.archive_members(data, expected["archive"])
    else:
        spec = json.loads(json.dumps(expected["archive"]))
        spec["members"][LEDGER + "README.md"] = "0" * 64
        with pytest.raises(qs4.InputError, match="members"):
            qs4.archive_members(data, spec)


# -- the rebuild ---------------------------------------------------------------------
def test_a_rebuilt_copy_reproduces_the_sha_a_second_route_gives(world):
    w, _ = world
    work = w.local / "work" / "parcelround"
    keys = qs4.keys_of(members_of(w), w.items)
    for p in ("P1", "P2"):
        sha, _ = qs4.rebuild_copy(work, keys[p])
        assert sha == w.copies[p]      # the key's copy_commit came from commit-tree, not from the rebuilder


def test_a_file_holding_two_plants_gets_both(world):
    w, _ = world
    blobs = qs4.planted_blobs(w.local / "work" / "parcelround", w.tips["P1"], P1_PLANTS)
    text = blobs["METHOD.md"]
    assert all(p["new"].encode() in text for p in P1_PLANTS) and not any(p["old"].encode() in text for p in P1_PLANTS)


def test_a_copy_that_does_not_reproduce_its_sha_is_refused(world):
    w, _ = world
    work = w.local / "work" / "parcelround"
    key = {"real_tip": w.tips["P1"], "copy_commit": w.copies["P2"], "plants": P1_PLANTS}
    with pytest.raises(qs4.InputError, match="not the key's"):
        qs4.rebuild_copy(work, key)
    shifted = {"real_tip": w.tips["P1"], "copy_commit": w.copies["P1"],
               "plants": [dict(P1_PLANTS[0], new="the verifier must re-run from clean"), P1_PLANTS[1]]}
    with pytest.raises(qs4.InputError, match="not the key's"):
        qs4.rebuild_copy(work, shifted)


def test_a_plant_whose_text_is_not_found_once_is_refused(world):
    w, _ = world
    with pytest.raises(qs4.InputError, match="0 times"):
        qs4.planted_blobs(w.local / "work" / "parcelround", w.tips["P1"],
                          [{"file": "METHOD.md", "old": "no such text", "new": "x"}])


def test_lines_map_through_a_changed_block():
    a, b = [b"x", b"y", b"new", b"z"], [b"x", b"y", b"z"]
    m = qs4.map_lines(a, b)
    assert m[1] == 1 and m[2] == 2 and m[4] == 3


# -- the replay repository ------------------------------------------------------------
def test_each_replay_repository_holds_exactly_what_it_must(world):
    w, expected = world
    for iid, e in expected["repos"].items():
        repo = w.local / "repos" / e["commit"][:12]
        assert qs4.repo_problems(repo, e["commit"], e["tree"], e["objects"],
                                 forbidden_blobs=(expected["archive"]["blob"],)) == []
        assert "CASE-STUDY-6.md" not in e["files"] and "archive/round6-ledger.zip" not in e["files"]


PLANTED_REPO_STATES = ["a ref", "a remote", "an extra object", "a dirty tree", "another HEAD", "a branch HEAD",
                       "a forbidden blob", "a reflog", "a twin commit", "another tree", "another count",
                       "a forbidden name"]


@pytest.mark.parametrize("state", PLANTED_REPO_STATES)
def test_a_replay_repository_in_a_planted_state_is_refused(world, tmp_path, state):
    """Each state but "another HEAD" and "a branch HEAD" trips one check alone, so
    that removing that check lets it through: a plant's test."""
    w, expected = world
    e = dict(expected["repos"]["p1-planted"])
    local = copy_local(w, tmp_path / "local")
    repo = local / "repos" / e["commit"][:12]
    forbidden, names = (expected["archive"]["blob"],), qs4.FORBIDDEN_NAMES
    if state == "a twin commit":
        # the same tree and parent under another message: only HEAD differs, not the tree or the count
        work = local / "work" / "parcelround"
        twin = g(work, "commit-tree", e["tree"], "-p", w.base, "-m", "a twin").strip()
        repo = tmp_path / "twin"
        qs4.make_replay_repo(work, twin, repo)
    elif state == "another tree":
        e["tree"] = w.base
    elif state == "another count":
        e["objects"] += 1
    elif state == "a forbidden name":
        names = ("METHOD.md",)
    elif state == "a ref":
        g(repo, "tag", "t1")
    elif state == "a remote":
        g(repo, "remote", "add", "origin", "https://example.invalid/x.git")
    elif state == "an extra object":
        g(repo, "hash-object", "-w", "--stdin", input=b"an object HEAD does not reach\n")
    elif state == "a dirty tree":
        put(repo, "METHOD.md", "changed\n")
    elif state == "another HEAD":
        g(repo, "checkout", "-q", "--detach", "HEAD^")
    elif state == "a branch HEAD":
        g(repo, "checkout", "-q", "-b", "x")
    elif state == "a forbidden blob":
        forbidden = (g(repo, "rev-parse", "HEAD:METHOD.md").strip(),)
    elif state == "a reflog":
        (repo / ".git" / "logs").mkdir(exist_ok=True)
        (repo / ".git" / "logs" / "HEAD").write_text("0 1 a <a@example.invalid> 0 +0000\tmoved\n")
    assert qs4.repo_problems(repo, e["commit"], e["tree"], e["objects"], forbidden_blobs=forbidden,
                             forbidden_names=names)


def test_a_worktree_is_refused_as_a_replay_repository(world, tmp_path):
    w, expected = world
    e = expected["repos"]["p1-planted"]
    repo = copy_local(w, tmp_path / "local") / "repos" / e["commit"][:12]
    wt = tmp_path / "wt"
    g(repo, "worktree", "add", "-q", "--detach", str(wt), e["commit"])
    assert qs4.repo_problems(wt, e["commit"], e["tree"], e["objects"])[0].startswith("it is not a repository")


# -- the local inputs ----------------------------------------------------------------
def inputs(w, expected, local, image="test-image"):
    return qs4.LocalInputs(local, items=w.items, expected=expected, image_id=lambda: image)


def test_prepared_inputs_mount_each_input_read_only_by_name(world):
    w, expected = world
    prep = inputs(w, expected, w.local).prepare("p1-real")
    names = [m.name for m in prep.mounts]
    assert names == ["r6-vcopy-P1", "parcelround-r6-ledger", "HonestHarness", "srcrepo"]
    assert prep.repo_files == expected["repos"]["p1-real"]["files"] and "lead.md" in prep.cut_files
    assert prep.source_files == {"srcrepo": ["docs/V.md"]}


def test_no_host_directory_tells_a_copy_from_a_tip(world):
    w, expected = world
    for iid in ("p1-planted", "p1-real", "p2-planted", "p2-real"):
        for m in inputs(w, expected, w.local).prepare(iid).mounts:
            rel = os.path.relpath(m.source, w.local).lower()
            assert not any(word in rel for word in ("planted", "real", "key", "copy", "tip")), rel


PLANTED_LOCAL_STATES = ["a cut byte", "the repository", "no gate record", "a gate not held",
                        "another image", "the plan", "a source", "nothing built"]


@pytest.mark.parametrize("state", PLANTED_LOCAL_STATES)
def test_local_inputs_in_a_planted_state_are_refused(world, tmp_path, state):
    w, expected = world
    local = copy_local(w, tmp_path / "local")
    built = json.loads((local / "built.json").read_text(encoding="utf-8"))
    cuts = json.loads((local / "cuts.json").read_text(encoding="utf-8"))
    image = "test-image"
    if state == "a cut byte":
        p = local / cuts["p1-planted"]["dir"] / "README.md"
        data = p.read_bytes()
        p.write_bytes(data[:1] + bytes([data[1] ^ 1]) + data[2:])      # the same length, one byte changed
    elif state == "the repository":
        put(local / built["items"]["p1-planted"]["repo"], "README-extra.md", "x\n")
    elif state == "no gate record":
        built["items"]["p1-planted"]["gate"] = None
    elif state == "a gate not held":
        built["items"]["p1-planted"]["gate"]["held"] = False
    elif state == "another image":
        image = "another-image"
    elif state == "the plan":
        p = local / built["plan"]["dir"] / "Rounds" / "ParcelRound-R6" / "PLAN.md"
        p.write_bytes(p.read_bytes() + b"x")
    elif state == "a source":
        p = local / built["sources"]["dir"] / "srcrepo" / "docs" / "V.md"
        p.write_bytes(b"other\n")
    else:
        del built["items"]["p1-planted"]
    (local / "built.json").write_text(json.dumps(built), encoding="utf-8")
    with pytest.raises(qs4.InputError):
        inputs(w, expected, local, image).prepare("p1-planted")


@pytest.mark.parametrize("kind", ["symlink", "reparse point"])
def test_a_link_or_reparse_point_in_an_input_directory_is_refused(tmp_path, monkeypatch, kind):
    """lstat is made to report one entry as a link, or as a regular file carrying
    WSL's reparse tag 0xa000001d: the form a link made inside the sandbox takes on
    the host (P2.md 13:30:32)."""
    import stat
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "a.md").write_text("x")
    (tmp_path / "d" / "b.md").write_text("y")
    real = os.lstat

    def lstat(p, *a, **k):
        if os.path.basename(p) != "b.md":
            return real(p, *a, **k)
        if kind == "symlink":
            return os.stat_result((stat.S_IFLNK | 0o777, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        return os.stat_result((stat.S_IFREG | 0o644, 0, 0, 0, 0, 0, 0, 0, 0, 0), {"st_reparse_tag": 0xA000001D})
    monkeypatch.setattr(qs4.os, "lstat", lstat)
    with pytest.raises(qs4.InputError, match="link"):
        qs4.read_files(tmp_path / "d")


def test_a_real_symbolic_link_in_an_input_directory_is_refused(tmp_path):
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "a.md").write_text("x")
    try:
        os.symlink(tmp_path / "d" / "a.md", tmp_path / "d" / "link.md")
    except OSError as e:
        pytest.skip(f"this account cannot make a symbolic link here ({type(e).__name__})")
    with pytest.raises(qs4.InputError, match="link"):
        qs4.read_files(tmp_path / "d")


# -- round 6's gate, compared --------------------------------------------------------
GATE_OUT = ("links      ok    42 relative links read\nquoted     ok    29 loganw.dev patterns read\n"
            "PASS: 10 of 10 checks hold\n")
CONTROL_OUT = ("control links      a link that does not resolve        caught\n"
               "control anchors    a commit written without 'at'       caught\ncontrols: 48 of 48 caught\n")


def side(gate=GATE_OUT, control=CONTROL_OUT, exits=(0, 0), complete=True):
    return {"gate": {"exit": exits[0], "parsed": qs4.parse_gate(gate), "complete": complete},
            "control": {"exit": exits[1], "parsed": qs4.parse_gate(control), "complete": complete}}


def test_round_6s_gate_output_is_parsed_into_checks_and_verdicts():
    p = qs4.parse_gate(GATE_OUT + CONTROL_OUT)
    assert p["checks"] == {"links": "ok", "quoted": "ok"} and p["verdict"] == ["PASS", 10, 10]
    assert p["controls"] == [48, 48] and len(p["control_lines"]) == 2


@pytest.mark.parametrize("box,why", [
    (side(gate=GATE_OUT.replace("quoted     ok", "quoted     FAIL")), "gate: the verdicts differ"),
    (side(gate=GATE_OUT.replace("PASS: 10 of 10", "FAIL: 9 of 10")), "gate: the verdicts differ"),
    (side(gate="links ok\n"), "gate: a verdict line is missing"),
    (side(exits=(1, 0)), "gate: exit 0 on the host, 1 in the sandbox"),
    (side(complete=False), "gate: the sandbox's output was cut short or timed out"),
    (side(control=CONTROL_OUT.replace("48 of 48", "47 of 48")), "control: the verdicts differ"),
    (side(control=CONTROL_OUT.replace("caught\ncontrols", "NOT CAUGHT\ncontrols")), "control: the verdicts differ"),
], ids=["check", "verdict", "no-verdict", "exit", "cut-short", "controls", "control-line"])
def test_a_gate_that_means_another_thing_in_the_sandbox_is_not_held(box, why):
    assert qs4.compare_gate(side(), side()) == (True, "the verdicts match")
    assert qs4.compare_gate(side(), box) == (False, why)


def test_the_tools_refuse_inputs_that_differ_from_the_pinned_ones(world, tmp_path):
    w, expected = world
    from test_qs4_support import load_tool
    cut, rebuild = load_tool("qs4_cut"), load_tool("qs4_rebuild")
    exp = json.loads(json.dumps(expected))
    exp["cuts"]["p2-real"]["digest"] = "0" * 64
    exp["repos"]["p1-real"]["tree"] = w.base
    (tmp_path / "expected.json").write_text(json.dumps(exp), encoding="utf-8")
    common = ["--local", str(tmp_path / "local"), "--items", str(w.items_path), "--expected", str(tmp_path / "expected.json")]
    assert cut.main(["--parcelround", str(w.repo), *common]) == 1
    assert rebuild.main(["--parcelround", str(w.repo), "--repos", str(w.repos), "--honestharness", str(w.hh),
                         "--no-gate", *common]) == 1
    built = json.loads((tmp_path / "local" / "built.json").read_text(encoding="utf-8"))
    assert "p1-real" not in built["items"] and "p1-planted" in built["items"]
    remove_tree(tmp_path / "local")


def test_the_rebuilder_refuses_a_recorded_finding_at_a_line_the_copy_does_not_have(world, tmp_path, capsys):
    w, _ = world
    from test_qs4_support import load_tool
    rebuild = load_tool("qs4_rebuild")
    items = json.loads(w.items_path.read_text(encoding="utf-8"))
    items["parcels"]["P1"]["r6_findings"][0]["lines"] = [[9999, 9999]]
    (tmp_path / "items.json").write_text(json.dumps(items), encoding="utf-8")
    local = copy_local(w, tmp_path / "local")                  # the cutter's archive, as built
    common = ["--local", str(local), "--items", str(tmp_path / "items.json"), "--expected", str(w.expected_path)]
    assert rebuild.main(["--parcelround", str(w.repo), "--repos", str(w.repos), "--honestharness", str(w.hh),
                         "--no-gate", *common]) == 1
    assert "REFUSED: P1-r1 cites a line its file at the copy does not have" in capsys.readouterr().out
    remove_tree(local)


def test_the_rebuilder_records_a_sandbox_that_fails_as_a_gate_not_held(world, tmp_path, monkeypatch, capsys):
    w, _ = world
    from qs.agent.sandbox import SandboxError
    from test_qs4_support import load_tool
    rebuild = load_tool("qs4_rebuild")

    def no_sandbox(*args, **kwargs):
        raise SandboxError("the sandbox did not start")
    monkeypatch.setattr(rebuild, "gate_record", no_sandbox)
    local = copy_local(w, tmp_path / "local")
    common = ["--local", str(local), "--items", str(w.items_path), "--expected", str(w.expected_path)]
    assert rebuild.main(["--parcelround", str(w.repo), "--repos", str(w.repos), "--honestharness", str(w.hh),
                         *common]) == 1
    built = json.loads((local / "built.json").read_text(encoding="utf-8"))
    assert sorted(built["items"]) == ["p1-planted", "p1-real", "p2-planted", "p2-real"]
    assert all(b["gate"] == {"held": False, "detail": "SandboxError: the sandbox did not start"}
               for b in built["items"].values())
    assert "items: 4 of 4 built; 4 not held" in capsys.readouterr().out
    remove_tree(local)
