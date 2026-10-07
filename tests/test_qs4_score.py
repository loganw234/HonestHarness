"""QS4's score, as pure functions: a finding's file and lines normalised to
closed sets, a plant located by its span, the fault screen's markers, and the
match against round 6's recorded findings."""
import pytest

from qs.suites import qs4

REPO = ["METHOD.md", "ADOPTION.md", "templates/brief.md", "tools/check_method.py", "README.md"]
CUT = ["README.md", "lead.md", "briefs/P3.md", "verifier-P0.md"]
SOURCES = {"cft-fp256": ["docs/VALIDATION.md"]}


@pytest.mark.parametrize("raw,want", [
    ("METHOD.md", ("METHOD.md", None)),
    ("./METHOD.md", ("METHOD.md", None)),
    ("method.md", ("METHOD.md", None)),
    ("/work/ro/r6-vcopy-P3/METHOD.md", ("METHOD.md", None)),
    ("<repos>/r6-vcopy-P3/templates/brief.md", ("templates/brief.md", None)),
    ("`METHOD.md:850`", ("METHOD.md", [850, 850])),
    ("METHOD.md:648-649", ("METHOD.md", [648, 649])),
    ("METHOD.md#L414", ("METHOD.md", [414, 414])),
    ("templates\\brief.md", ("templates/brief.md", None)),
    ("the commit message", (qs4.COMMIT_MESSAGE, None)),
    ("lead.md", ("ledger/lead.md", None)),
    ("/work/ro/parcelround-r6-ledger/briefs/P3.md", ("ledger/briefs/P3.md", None)),
    ("README.md", ("README.md", None)),                       # the repository's, before the ledger's
    ("/work/ro/cft-fp256/docs/VALIDATION.md:15260", ("cft-fp256/docs/VALIDATION.md", [15260, 15260])),
    ("METHOD.md (section 6)", (qs4.UNLISTED, None)),
    ("/etc/passwd", (qs4.UNLISTED, None)),
], ids=lambda x: str(x)[:20])
def test_a_findings_file_is_normalised_to_a_closed_set(raw, want):
    assert qs4.normalise_file(raw, "P3", REPO, CUT, SOURCES) == want


@pytest.mark.parametrize("v,want", [("414", [414, 414]), ("648-649", [648, 649]), ("9-3", [3, 9]), (None, None),
                                    ("x", None), ("1–2", None)])
def test_lines_are_read_as_two_integers(v, want):
    assert qs4.parse_lines(v) == want


def test_a_plants_span_is_met_within_the_tolerance_and_not_beyond():
    span = [[694, 695]]
    assert qs4.meets([694, 696], span, 0) and qs4.meets([697, 697], span, 2)
    assert not qs4.meets([698, 698], span, 2) and not qs4.meets([691, 691], span, 2)
    assert not qs4.meets(None, span, 2)


@pytest.mark.parametrize("statement,markers,hit", [
    ("CASE-STUDY-3 says 5 of 38", [["38"]], True),
    ("it says 5 of 28", [["38"]], False),
    ("line 380 says", [["38"]], False),
    ("the source says five", [["five"]], True),
    ("fivefold", [["five"]], False),
    ("it adopts CS5#3, which is pending", [["CS5#3"]], True),
    ("CS5#30 is something else", [["CS5#3"]], False),
    ("the rule is section 3's", [["section 3"]], True),
    ("tagged (§3) in brief.md", [["§3"]], True),
    ("tagged (§30)", [["§3"]], False),
    ("the condition was WEAKENED", [["weaken*"]], True),
    ("the ledger entry comes first", [["entry comes first"]], True),
    ("first, the entry", [["entry first"]], False),
    ("the source re-runs it", [["re-runs"]], True),
    ("the order is reversed", [["entry first"], ["order"]], True),
    ("", [["x"]], False),
], ids=lambda x: str(x)[:24])
def test_the_screens_markers_match_whole_words_case_folded(statement, markers, hit):
    assert qs4.markers_hit(statement, markers) is hit


def items_for(kind):
    parcel = {"copy": "c" * 40, "tip": "t" * 40, "base": "b" * 40, "wave": 1,
              "plants": [{"id": "P9-p1", "index": 0, "shape": "figure", "markers": [["38"]]},
                         {"id": "P9-p2", "index": 1, "shape": "rule", "markers": [["records"]]}],
              "r6_findings": [
                  {"id": "P9-r1", "class": "restate", "file": "METHOD.md", "lines": [[700, 702]], "in_view": True,
                   "copy_only": False},
                  {"id": "P9-r2", "class": "other", "file": "tools/check_method.py", "lines": [], "in_view": False,
                   "copy_only": False},
                  {"id": "P9-r3", "class": "restate", "file": qs4.COMMIT_MESSAGE, "lines": [], "in_view": True,
                   "copy_only": True}]}
    items = {"settings": {"tolerance": 2}, "parcels": {"P9": parcel}}
    expected = {"plant_spans": {"P9-p1": {"file": "METHOD.md", "lines": [414, 414]},
                                "P9-p2": {"file": "METHOD.md", "lines": [694, 695]}},
                "r6_tip_lines": {"P9-r1": [[600, 602]], "P9-r2": [], "P9-r3": []}}
    item = {"id": f"p9-{kind}", "parcel": "P9", "kind": kind}
    prep = qs4.Prepared(mounts=[], repo_files=REPO, cut_files=CUT, source_files=SOURCES)
    return items, item, expected, prep


def finding(file, lines, statement, cls="wrong answer"):
    f = {"class": cls, "file": file, "statement": statement}
    if lines is not None:
        f["lines"] = lines
    return f


def test_a_plant_is_caught_when_located_and_its_fault_stated():
    items, item, expected, prep = items_for("planted")
    report = {"verdict": "NOT READY", "text": "", "findings": [
        finding("METHOD.md", "414", "it says 5 of 28; the case study says 5 of 38"),
        finding("METHOD.md", "694-696", "the bold rule leaves out its records")]}
    sc, detail = qs4.score_report(report, items, item, expected, prep)
    assert [p["caught"] for p in sc["plants"]] == [True, True]
    assert [f["matched"] for f in sc["findings"]] == ["plant:P9-p1", "plant:P9-p2"]
    assert qs4.counts(sc)["plants_caught"] == 2 and detail[0]["statement"].startswith("it says")


def test_a_finding_at_the_line_without_the_fault_is_located_and_not_caught():
    items, item, expected, prep = items_for("planted")
    report = {"verdict": "NOT READY", "text": "", "findings": [finding("METHOD.md", "414", "this line looks off")]}
    sc, _ = qs4.score_report(report, items, item, expected, prep)
    assert sc["plants"][0] == {"id": "P9-p1", "shape": "figure", "located": True, "stated": False, "caught": False}


def test_a_finding_beside_the_plant_or_in_another_file_is_not_located():
    items, item, expected, prep = items_for("planted")
    report = {"verdict": "NOT READY", "text": "", "findings": [
        finding("METHOD.md", "420", "5 of 38"), finding("ADOPTION.md", "414", "5 of 38"),
        finding("METHOD.md", None, "5 of 38")]}
    sc, _ = qs4.score_report(report, items, item, expected, prep)
    assert not sc["plants"][0]["located"] and qs4.counts(sc)["unmatched"] == 3


def test_other_findings_match_round_6s_record_by_location_and_by_file():
    items, item, expected, prep = items_for("planted")
    report = {"verdict": "NOT READY", "text": "", "findings": [
        finding("METHOD.md", "701", "x", "restate"), finding("tools/check_method.py", "12", "x", "other"),
        finding("the commit message", None, "x", "restate"), finding("METHOD.md", "100", "x")]}
    sc, _ = qs4.score_report(report, items, item, expected, prep)
    assert [(f["matched"], f["matched_by"]) for f in sc["findings"]] == [
        ("r6:P9-r1", "lines"), ("r6:P9-r2", "file"), ("r6:P9-r3", "file"), (None, None)]
    assert [r["located"] for r in sc["r6"]] == [True, True, True]


def test_a_real_tip_uses_the_tips_lines_and_skips_what_only_the_copy_shows():
    items, item, expected, prep = items_for("real")
    report = {"verdict": "READY", "text": "", "findings": [
        finding("METHOD.md", "601", "x", "restate"), finding("the commit message", None, "x")]}
    sc, _ = qs4.score_report(report, items, item, expected, prep)
    assert sc["plants"] == [] and [r["id"] for r in sc["r6"]] == ["P9-r1", "P9-r2"]
    assert sc["findings"][0]["matched"] == "r6:P9-r1" and sc["findings"][1]["matched"] is None


def test_no_report_scores_nothing():
    items, item, expected, prep = items_for("planted")
    sc, detail = qs4.score_report(None, items, item, expected, prep)
    assert sc == {"reported": False, "verdict": None, "findings": [], "plants": [], "r6": []} and detail == []


def record(rid, item, parcel, kind, wave, status, caught, plants=("P9-p1", "P9-p2")):
    q = {"item": item, "parcel": parcel, "kind": kind, "wave": wave, "verdict": "NOT READY",
         "plants": [{"id": p} for p in plants] if kind == "planted" else [],
         "counts": {"plants_caught": caught, "findings": 3, "unmatched": 1, "r6_in_view": 2, "r6_in_view_located": 1}}
    return {"record_id": rid, "outcome": {"status": status, "data": {"qs4": q}}, "calls": 9, "cost_usd": "0.1",
            "usage": {"cache_hit": 900, "cache_miss": 100, "output": 50, "reasoning": 10}}


def test_the_table_reports_the_screen_and_the_lead_judgement_by_wave():
    recs = [record("a", "p1-planted", "P1", "planted", 1, "fail", 1),
            record("b", "p5-planted", "P5", "planted", 2, "pass", 2),
            record("c", "p1-real", "P1", "real", 1, "pass", 0),
            {"record_id": "x", "outcome": {"status": "pass", "data": {}}}]
    judged = [{"record_id": "a", "plant": "P9-p1", "verdict": "caught"},
              {"record_id": "a", "plant": "P9-p2", "verdict": "caught"},
              {"record_id": "b", "plant": "P9-p1", "verdict": "missed"}]
    t = qs4.table(recs, judged)
    assert sorted(t["rows"]) == ["a", "b", "c"]
    assert t["rows"]["a"]["plants_caught_screen"] == 1 and t["rows"]["a"]["plants_caught_judged"] == 2
    assert t["rows"]["b"]["plants_caught_judged"] is None          # one of its two plants judged: no count
    assert t["rows"]["a"]["read"] == 1000 and t["rows"]["a"]["cache_hit"] == 900
    assert t["planted_by_wave"] == {"wave1": {"runs": 1, "plants_caught_screen": 1},
                                    "wave2": {"runs": 1, "plants_caught_screen": 2}}


def test_scored_data_holds_only_closed_values():
    items, item, expected, prep = items_for("planted")
    report = {"verdict": "NOT READY", "text": "SENTINEL-TEXT", "findings": [
        finding("SENTINEL-FILE.md", "414", "SENTINEL-STATEMENT 5 of 38")]}
    sc, detail = qs4.score_report(report, items, item, expected, prep)
    assert "SENTINEL" not in repr(sc) and "SENTINEL" in repr(detail)
    assert sc["findings"][0]["file"] == qs4.UNLISTED
