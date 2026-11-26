"""A pull request's plan (tools/pr_plan.py) follows which chapters' own inputs changed, and falls to the smoke wherever no
chapter's saved end before it could be the base's."""
from dataclasses import replace

from tools.pr_plan import Snap, here, plan

BASE = here()


def changed(**edits: str) -> Snap:
    return replace(BASE, own={**BASE.own, **edits})


def test_nothing_changed_plays_nothing_of_week_two():
    assert plan(BASE, False, [])["mode"] == "none"


def test_a_touched_chapter_is_sliced_and_one_before_it_is_not_touched():
    got = plan(changed(twelve="x", nineteen="y"), False, [])
    assert (got["mode"], got["chapters"]) == ("slice", ["twelve", "nineteen"])
    assert got["base_keys"] == BASE.key


def test_a_changed_week_two_test_file_is_sliced_with_no_chapter_touched():
    got = plan(BASE, False, ["app/tests/weektwo/test_weektwo_twelve.py", "app/tests/weektwo/ends.py", "docs/x.md"])
    assert (got["mode"], got["chapters"], got["files"]) == ("slice", [], ["app/tests/weektwo/test_weektwo_twelve.py"])


def test_week_one_a_changed_shared_input_and_a_base_without_keys_are_the_smoke():
    assert plan(changed(week1="x"), False, [])["mode"] == "smoke"
    assert plan(replace(BASE, shared="another"), False, [])["mode"] == "smoke"
    assert plan(None, False, [])["mode"] == "smoke"


def test_the_label_asks_for_everything():
    assert plan(changed(twelve="x"), True, [])["mode"] == "full"
