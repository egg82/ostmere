"""The full run's chapter-save jobs are planned from measured cost (tools/saves_plan.py, tools/ci_costs.json): every planned
job's predicted time fits its cap with the margin, a chapter added re-splits the plan with no list to edit, and the workflow
runs what the plan can produce."""
import copy
from pathlib import Path
from typing import Any

import yaml

from tests.test_ci_budget import CI, needs
from tests.weektwo import keys, rebased
from tests.weektwo.routes import CHAPTERS, SAVED
from tools import saves_plan
from tools.saves_plan import Plan, plan, problems

NEW = "planted"


def today_inputs() -> tuple[dict[str, Any], dict[str, list[str]], list[str], list[str]]:
    table = saves_plan.load()
    chains = {route: [c for c, names in SAVED.items() if route in names] for route in table["ends"]}
    return table, chains, [c for c in keys.ORDER if c in rebased.OLD], list(CHAPTERS)


def with_chapters(extra: int) -> Plan:
    """Today's plan with `extra` chapters planted after the last, none of them in the table."""
    table, chains, reb, reads = today_inputs()
    added = [f"{NEW}{i}" for i in range(extra)]
    return plan(table, {r: [*c, *added] for r, c in chains.items()}, [*reb, *added], [*reads, *added])


def with_measured_chapters(extra: int) -> Plan:
    """Today's plan with `extra` chapters planted after the last, each with the rows a chapter ships: the costliest measured
    chapter's end per route, rebased save and readings row."""
    table, chains, reb, reads = today_inputs()
    grown = copy.deepcopy(table)
    added = [f"{NEW}{i}" for i in range(extra)]
    for c in added:
        for by in grown["ends"].values():
            by[c] = max(by.values())
        grown["rebased"][c] = max(table["rebased"].values())
        grown["readings"][c] = copy.deepcopy(max(table["readings"].values(), key=lambda r: r["setup_s"] + sum(r["steps_s"])))
    return plan(grown, {r: [*c, *added] for r, c in chains.items()}, [*reb, *added], [*reads, *added])


def over_target(p: Plan) -> set[str]:
    return {part for part, s in p.jobs() if s > saves_plan.TARGET_S}


def test_every_planned_job_is_predicted_within_its_cap_less_the_margin():
    found = saves_plan.today()
    assert len(found.jobs()) > 10, "the plan holds the links, rebased groups and readings parts"
    assert problems(found) == []
    cap_s = saves_plan.CAP_MIN * 60
    assert all(s <= saves_plan.TARGET_S < cap_s for _, s in found.jobs())
    assert saves_plan.TARGET_S <= cap_s - saves_plan.MARGIN_MIN * 60


def test_the_check_sees_a_job_over_the_target_and_chains_over_the_ranks():
    """A chapter dearer than a whole job cannot be split: it is reported, not hidden in a job that times out."""
    table, chains, reb, reads = today_inputs()
    dear = copy.deepcopy(table)
    dear["ends"]["typical"]["eight"] = saves_plan.TARGET_S
    over = problems(plan(dear, chains, reb, reads))
    assert len(over) == 1 and over[0].startswith("typical-"), over
    longer = {r: [c for _ in range(saves_plan.RANKS * 4) for c in chs] for r, chs in chains.items()}
    assert any("ranks" in line for line in problems(plan(table, longer, reb, reads)))


def test_a_chapter_added_re_splits_the_plan_and_every_job_still_fits():
    """Chapters added with their rows (test_today_every_chapter_is_measured... holds every chapter to one): one with no row
    is planned at the unmeasured figures, which need not fit a job (the test below)."""
    base, grown = saves_plan.today(), with_measured_chapters(6)
    assert grown.estimated == ()
    assert problems(grown) == []
    assert len(grown.links) > len(base.links) or grown.ranks() > base.ranks() or len(grown.rebased) > len(base.rebased)
    assert len(grown.rebased) > len(base.rebased) and len(grown.readings) > len(base.readings)
    for route in {link.route for link in base.links}:
        chain = [c for link in grown.links if link.route == route for c in link.chapters]
        assert chain == [c for c, names in SAVED.items() if route in names] + [f"{NEW}{i}" for i in range(6)], route
    assert [c for g in grown.rebased for c in g.chapters][-6:] == [f"{NEW}{i}" for i in range(6)]


def test_a_chapter_added_far_enough_needs_a_link_the_workflow_lacks_and_says_so():
    found = with_chapters(60)
    assert found.ranks() > saves_plan.RANKS
    assert any("add a chapter-saves-link job" in line for line in problems(found))


def test_a_chapter_with_no_measurement_is_planned_at_the_unmeasured_figure_and_named():
    found = with_chapters(1)
    assert {f"ends:{r}:{NEW}0" for r in saves_plan.load()["ends"]} <= set(found.estimated)
    assert {f"rebased:{NEW}0", f"readings:{NEW}0"} <= set(found.estimated)
    base = saves_plan.today()
    assert sum(s for _, s in found.jobs()) > sum(s for _, s in base.jobs()), "an unmeasured chapter is never free"


def test_a_job_a_chapter_with_no_row_pushes_over_the_target_is_reported_not_assumed_to_fit():
    found = with_chapters(1)
    assert f"readings:{NEW}0" in found.estimated
    assert {line.split(" ")[0] for line in problems(found) if "target" in line} == over_target(found)
    table, chains, reb, reads = today_inputs()
    dear = copy.deepcopy(table)
    dear["unmeasured"]["readings"]["steps_s"] = [saves_plan.TARGET_S]
    planted = plan(dear, chains, reb, [*reads, f"{NEW}0"])
    mine = {r.part for r in planted.readings if any(span[0] == f"{NEW}0" for span in r.spans)}
    assert mine & over_target(planted), "the control: an unmeasured step as dear as a whole job"
    assert mine & over_target(planted) <= {line.split(" ")[0] for line in problems(planted)}


def test_today_every_chapter_is_measured_and_the_table_names_no_chapter_the_code_lacks():
    table, chains, reb, reads = today_inputs()
    assert saves_plan.today().estimated == ()
    known = set(keys.ORDER)
    rows = {c for by in table["ends"].values() for c in by} | set(table["rebased"]) | set(table["readings"])
    assert rows <= known, sorted(rows - known)
    assert set(table["ends"]) == set(chains) and set(table["rebased"]) == set(reb) and set(table["readings"]) == set(reads)


def test_no_measured_cost_is_zero_and_an_unmeasured_one_is_over_every_measured():
    table = saves_plan.load()
    ends = [s for by in table["ends"].values() for s in by.values()]
    steps = [s for row in table["readings"].values() for s in row["steps_s"]]
    assert ends and steps and min(ends) > 0 and min(steps) > 0 and min(table["rebased"].values()) > 0
    assert all(row["setup_s"] > 0 for row in table["readings"].values())
    for route, by in table["ends"].items():
        assert table["unmeasured"]["ends"][route] > max(by.values()), route
    assert table["unmeasured"]["rebased"] > max(table["rebased"].values())
    assert table["unmeasured"]["readings"]["setup_s"] > max(r["setup_s"] for r in table["readings"].values())
    assert max(table["unmeasured"]["readings"]["steps_s"]) > max(steps)


def test_a_link_starts_from_the_link_before_and_every_rank_has_a_leg():
    found = saves_plan.matrix(saves_plan.today())
    assert len(found["ranks"]) == saves_plan.RANKS and all(found["ranks"])
    parts = {link.part: link for link in saves_plan.today().links}
    for rank, legs in enumerate(found["ranks"], 1):
        for leg in legs:
            if leg["part"] == "idle":
                assert leg == {"part": "idle", "names": "", "after": ""}
                continue
            assert parts[leg["part"]].rank == rank
            assert (leg["after"] == "") == (rank == 1) and (not leg["after"] or parts[leg["after"]].rank == rank - 1)


def test_each_readings_part_covers_a_chapters_steps_once_from_its_first_with_the_last_span_open():
    table = saves_plan.load()
    seen: dict[str, list[int]] = {}
    for part in saves_plan.today().readings:
        for chapter, first, after in part.spans:
            stop = after if after is not None else saves_plan.heavy_count(table, chapter)
            seen.setdefault(chapter, []).extend(range(first, stop))
    assert {c: v for c, v in seen.items()} == {c: list(range(saves_plan.heavy_count(table, c))) for c in CHAPTERS}


def jobs() -> dict[str, dict[str, Any]]:
    return dict(yaml.safe_load(Path(CI).read_text())["jobs"])


def test_the_workflow_has_the_jobs_the_plan_feeds_and_gives_each_the_cap_the_plan_assumes():
    found = jobs()
    ranks = [f"chapter-saves-link-{k}" for k in range(1, saves_plan.RANKS + 1)]
    assert all(name in found for name in ranks)
    assert not [n for n in found if n.startswith("chapter-saves-link-") and n not in ranks]
    for name in (*ranks, "chapter-saves-rebased", "chapter-saves-readings"):
        assert found[name]["timeout-minutes"] == saves_plan.CAP_MIN, name
    for k, name in enumerate(ranks, 1):
        assert needs(found[name]) == ["saves-plan", *([ranks[k - 2]] if k > 1 else [])], name
        assert f"outputs.rank{k})" in found[name]["strategy"]["matrix"]["include"]
        assert f"rank{k}" in found["saves-plan"]["outputs"]
    for name in ("chapter-saves-rebased", "chapter-saves-readings"):
        assert needs(found[name]) == ["saves-plan", ranks[-1]], name
        assert "fromJSON(needs.saves-plan.outputs" in found[name]["strategy"]["matrix"]["part"]
    assert {"rebased", "readings"} <= set(found["saves-plan"]["outputs"])
    for name in ("playthrough-week-two", "playthrough-week-one-saved", "publish-ends"):
        assert ranks[-1] in needs(found[name]), name


def test_an_idle_leg_skips_every_step_of_the_shared_steps_and_the_check_sees_one_that_does_not():
    steps = jobs()["chapter-saves-link-1"]["steps"]
    assert steps and all("env.NAMES != ''" in (step.get("if") or "") or step.get("if") == "env.AFTER != ''" for step in steps)
    loose = [*steps, {"uses": "actions/upload-artifact@v4"}]
    assert not all("env.NAMES != ''" in (step.get("if") or "") or step.get("if") == "env.AFTER != ''" for step in loose)
