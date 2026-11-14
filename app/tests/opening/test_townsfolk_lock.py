"""The release lock's day-two classes on the test chapter (fixtures/townsfolk.toml): a released lane keeps its
`ruled`, and a released card stays on, or off, a ruled lane (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND
OFFERS", "Release lock")."""
from functools import cache
from pathlib import Path

import pytest

from ashfall_app.engine import Rules
from ashfall_app.opening.lock import Lock, snapshot
from ashfall_app.opening.lock_checks import Problem, problems
from ashfall_app.opening.renames import RenameEntry, load_renames
from ashfall_app.opening.schema import Opening, merge_chapters, to_rules
from tests.opening.test_townsfolk_loader import broken, loaded, shipped

pytestmark = pytest.mark.usefixtures("townsfolk_opening")


@cache
def released_lock() -> Lock:
    o = loaded()
    return snapshot(o, to_rules(o), load_renames())


@pytest.fixture(scope="module", autouse=True)
def built_released_lock(townsfolk_opening: Opening) -> None:
    released_lock()   # in setup, not charged to the first test's call


def now_lock(path: Path | None = None) -> Lock:
    if path is None:
        return released_lock()
    o = merge_chapters(shipped(), (path,))
    return snapshot(o, to_rules(o), load_renames())


def forbidden(path: Path) -> list[Problem]:
    return [p for p in problems(now_lock(), now_lock(path), load_renames()) if p.cls == "forbidden"]


def test_a_reworded_test_chapter_is_safe(tmp_path: Path):
    assert forbidden(broken(tmp_path, 't_c_help_rest = "Rest"', 't_c_help_rest = "Sit"')) == []


def test_a_lanes_ruled_changed_is_forbidden(tmp_path: Path):
    """The installs go too: on an unruled lane they would not load, nor would the trigger reading its rules."""
    path = broken(tmp_path, 'ruled = true\ntold = "line"\n', "ruled = false\n")
    kept = [line for line in path.read_text().splitlines(keepends=True) if not line.startswith("orders = [")]
    assert len(kept) == len(path.read_text().splitlines()) - 2
    text = "".join(kept)
    rule_set = text.index('[[triggers]]\nid = "t_rule_set"')
    path.write_text(text[:rule_set] + text[text.index("[[triggers]]", rule_set + 1):])
    found = forbidden(path)
    assert any("lane t_helper's ruled changed" in p.message for p in found), found


def test_a_card_moved_off_a_ruled_lane_is_forbidden(tmp_path: Path):
    found = forbidden(broken(tmp_path, 'lane = "t_helper"\npresentation = "action"\nlabel_key = "t_c_help_rest"',
                             'lane = "hands"\npresentation = "action"\nlabel_key = "t_c_help_rest"'))
    assert any("card t_help_rest moved onto or off" in p.message for p in found), found


def test_a_released_answers_outcome_changed_is_forbidden(tmp_path: Path):
    found = forbidden(broken(tmp_path, 'line_keys = ["t_l_yes"]', 'line_keys = ["t_l_yes", "t_l_asked"]'))
    assert any("answer t_yes's outcome changed" in p.message for p in found), found


def test_a_queued_card_made_uncapped_is_forbidden(tmp_path: Path):
    path = broken(tmp_path, 'work_s = 40\ncap = 1\n', 'work_s = 40\n')
    found = [p for p in problems(now_lock(), now_lock_without_queue_check(path), load_renames())
             if p.cls == "forbidden"]
    assert any("card t_one_off, which answer t_no queues" in p.message for p in found), found


def now_lock_without_queue_check(path: Path) -> Lock:
    """The lock of content that queues an uncapped card, which the loader refuses: built from a copy of the released
    lock with that card's cap gone, as content that moved the card would give."""
    lock = now_lock()
    return lock.model_copy(update={"card_caps": {**lock.card_caps, "t_one_off": None}})


def test_an_answer_moved_to_another_offer_is_forbidden():
    lock = now_lock()
    moved = lock.model_copy(update={"answer_offers": {**lock.answer_offers, "t_yes": "t_other"}})
    found = [p for p in problems(lock, moved, load_renames()) if p.cls == "forbidden"]
    assert any("answer t_yes moved to another offer" in p.message for p in found), found


@pytest.fixture(scope="module")
def offer_renamed(tmp_path_factory: pytest.TempPathFactory, shipped_opening: Opening) -> tuple[list[RenameEntry], Opening, Rules]:
    """The test chapter with offer t_ask renamed t_asked, and the renames that say so (renames.toml names the offer only),
    built in setup: the content and its rules are the cost."""
    tmp_path = tmp_path_factory.mktemp("offer_renamed")
    renames = tmp_path / "renames.toml"
    renames.write_text('[[renames]]\nkind = "offer"\nfrom = "t_ask"\nto = "t_asked"\n')
    entries = [*load_renames(), *load_renames(renames)]
    path = broken(tmp_path, 'id = "t_ask"\n', 'id = "t_asked"\n')
    path.write_text(path.read_text().replace('id = "t_ask", value = 1', 'id = "t_asked", value = 1'))
    o = merge_chapters(shipped_opening, (path,))
    return entries, o, to_rules(o)


def test_an_offers_rename_adds_the_trigger_that_shows_it(tmp_path: Path):
    """renames.toml names the offer only; load_renames adds offer_t_ask -> offer_t_asked."""
    renames = tmp_path / "renames.toml"
    renames.write_text('[[renames]]\nkind = "offer"\nfrom = "t_ask"\nto = "t_asked"\n')
    mine = load_renames(renames)
    assert [(r.kind, r.old, r.new) for r in mine] == [("offer", "t_ask", "t_asked"),
                                                      ("trigger", "offer_t_ask", "offer_t_asked")]


def test_an_offers_rename_with_its_trigger_leaves_only_out_of_date(offer_renamed: tuple[list[RenameEntry], Opening, Rules]):
    entries, o, rules = offer_renamed
    found = problems(now_lock(), snapshot(o, rules, entries), entries)
    assert [p for p in found if p.cls != "out_of_date"] == [], found


def test_the_same_offer_rename_without_it_needs_mapping(offer_renamed: tuple[list[RenameEntry], Opening, Rules]):
    """The control: without the rename it is red."""
    _, o, rules = offer_renamed
    unmapped = problems(now_lock(), snapshot(o, rules, load_renames()), load_renames())
    assert {p.cls for p in unmapped} >= {"needs_mapping"}


def messages(lock: Lock, now: Lock) -> list[str]:
    return [p.message for p in problems(lock, now, load_renames()) if p.cls == "forbidden"]


@pytest.fixture(scope="module")
def capped_lock(tmp_path_factory: pytest.TempPathFactory, shipped_opening: Opening) -> Lock:
    """The lock of the test chapter with a cap given to a released ruled lane card, built in setup."""
    capped = broken(tmp_path_factory.mktemp("capped"), 'lane = "t_helper"\npresentation = "action"\nlabel_key = "t_c_help_rest"',
                    'lane = "t_helper"\ncap = 2\npresentation = "action"\nlabel_key = "t_c_help_rest"')
    o = merge_chapters(shipped_opening, (capped,))
    return snapshot(o, to_rules(o), load_renames())


def test_a_cap_given_to_a_released_ruled_lane_card_is_forbidden(capped_lock: Lock):
    """Saved town mixes hold only uncapped cards (engine DESIGN.txt, "THE TOWN'S MIX", "Release lock")."""
    assert any("card t_help_rest's cap went down" in m for m in messages(now_lock(), capped_lock))
    assert messages(now_lock(), now_lock()) == []   # control: the same content is clean


def test_an_xp_line_given_to_a_released_ruled_lane_card_is_forbidden():
    """The loader refuses such content, so the changed lock is built as the other planted cases are."""
    lock = now_lock()
    xp = lock.model_copy(update={"card_xp": {**lock.card_xp, "t_help_rest": True}})
    assert any("card t_help_rest on a ruled lane was given an XP line" in m for m in messages(lock, xp))
    hands = lock.model_copy(update={"card_xp": {**lock.card_xp, "t_one_off": True}})
    assert messages(lock, hands) == []   # control: a hands card may gain one


def test_a_card_moved_between_ruled_lanes_is_forbidden():
    lock = now_lock()
    moved = lock.model_copy(update={"card_lanes": {**lock.card_lanes, "t_help_rest": "n1"}})
    assert any("card t_help_rest moved from one ruled lane to another" in m for m in messages(lock, moved))
    kept = lock.model_copy(update={"card_lanes": {**lock.card_lanes, "t_help_gather": "t_helper"}})
    assert messages(lock, kept) == []   # control: a card that stays on its ruled lane is clean
