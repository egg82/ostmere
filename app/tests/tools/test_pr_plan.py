"""A pull request's plan (tools/pr_plan.py) follows which chapters' own inputs changed, and falls to the smoke wherever no
chapter's saved end before it could be the base's."""
from dataclasses import replace

from tools.pr_plan import Snap, here, plan
from tools.weektwo_shards import NIGHTLY_ONLY, SHARDS, WHOLE_GAME

BASE = here()


def changed(**edits: str) -> Snap:
    return replace(BASE, own={**BASE.own, **edits})


def test_nothing_changed_plays_nothing_of_week_two():
    assert plan(BASE, False, [])["mode"] == "none"


def test_a_touched_chapter_is_sliced_and_one_before_it_is_not_touched():
    got = plan(changed(twelve="x", nineteen="y"), False, [])
    assert (got["mode"], got["chapters"]) == ("slice", ["twelve", "nineteen"])
    assert got["base_keys"] == BASE.key
    assert got["shards"] == ["twelve-typical", "twelve", "nineteen"] and got["left"] == []


def test_a_chapter_with_two_routes_plays_one_job_per_shard_and_a_long_shard_is_left_to_the_nightly():
    got = plan(changed(twentyfive="x"), False, [])
    assert (got["shards"], got["left"]) == (["twentyfive-whenever"], ["twentyfive-sharp", "twentyfive"])
    assert NIGHTLY_ONLY >= {"twentyfive-sharp", "twentyfive"}
    got = plan(changed(twentyseven="x"), False, [])
    assert (got["shards"], got["left"]) == (["twentyseven-whenever"], ["twentyseven-sharp", "twentyseven"])
    got = plan(changed(twentynine="x"), False, [])
    assert (got["shards"], got["left"]) == (["twentynine-whenever"], ["twentynine-sharp", "twentynine"])
    got = plan(changed(thirty="x"), False, [])
    assert (got["shards"], got["left"]) == (["thirty-whenever"], ["thirty-sharp", "thirty"])
    got = plan(changed(thirtyone="x"), False, [])
    assert (got["shards"], got["left"]) == (["thirtyone-whenever"], ["thirtyone-sharp", "thirtyone"])
    got = plan(changed(thirtythree="x"), False, [])
    assert (got["shards"], got["left"]) == (["thirtythree-whenever"], ["thirtythree-sharp", "thirtythree", "thirtythree-typical-b", "thirtythree-whenever-b"])
    assert plan(changed(eighteen="x"), False, [])["shards"] == ["eighteen"]
    assert plan(changed(fifteen="x"), False, [])["shards"] == ["fifteen"]


def test_a_changed_week_two_test_file_is_sliced_with_no_chapter_touched():
    got = plan(BASE, False, ["app/tests/weektwo/chapters/test_weektwo_twelve.py", "app/tests/weektwo/ends.py", "docs/x.md"])
    assert (got["mode"], got["chapters"], got["files"]) == ("slice", [], ["app/tests/weektwo/chapters/test_weektwo_twelve.py"])
    assert got["shards"] == [n for n in SHARDS if n not in NIGHTLY_ONLY]


def test_week_one_a_changed_shared_input_and_a_base_without_keys_are_the_smoke():
    assert plan(changed(week1="x"), False, [])["mode"] == "smoke"
    assert plan(replace(BASE, shared="another"), False, [])["mode"] == "smoke"
    assert plan(None, False, [])["mode"] == "smoke"


def test_a_change_every_chapter_reads_also_plays_the_whole_game_shards_from_the_start():
    for got in (plan(replace(BASE, shared="another"), False, []), plan(changed(week1="x"), False, [])):
        assert got["mode"] == "smoke" and got["shards"] == ["smoke"] and got["left"] == []
        assert got["whole_game"] == ["makers"]
    for got in (plan(None, False, []), plan(changed(fifteen="x"), False, [], lambda key: False), plan(changed(twelve="x"), False, [])):
        assert got["whole_game"] == []
    assert plan(None, False, [])["shards"] == ["smoke"]
    assert plan(changed(fifteen="x"), False, [], lambda key: False)["shards"] == ["smoke"]
    assert "makers" in WHOLE_GAME and WHOLE_GAME <= set(SHARDS) - NIGHTLY_ONLY


def test_the_label_asks_for_everything():
    assert plan(changed(twelve="x"), True, [])["mode"] == "full"


def test_a_slice_whose_chapter_before_has_no_saved_end_in_the_last_nightly_plays_the_smoke():
    got = plan(changed(fifteen="x"), False, [], lambda key: False)
    assert (got["mode"], got["shards"], got["why"]) == (
        "smoke", ["smoke"], "the last nightly holds no saved end of the chapter before fifteen")
    held = {BASE.key["twelve"], BASE.key["eleven"]}
    assert plan(changed(fifteen="x", twelve="y"), False, [], lambda key: key in held)["mode"] == "slice"
    assert plan(changed(eighteen="x"), False, [], lambda key: False)["mode"] == "smoke"
