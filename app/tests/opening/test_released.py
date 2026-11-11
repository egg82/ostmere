"""The release lock in CI: the shipped opening against released/ids.json and renames.toml, and each change class on a
test edit of the opening or of the lock (engine DESIGN.txt, "Release lock"; ashfall_app/opening/lock_checks.py)."""
from dataclasses import replace
from functools import cache

import pytest

from ashfall_app.engine import NodeDef, NodeId, Rules, StoreCap
from ashfall_app.engine import upgrade as upgrade_module
from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.lock import LOCK, Lock, content_ids, load_lock, merged, snapshot
from ashfall_app.opening.lock_checks import Problem, problems, release_problems
from ashfall_app.opening.renames import RenameEntry, load_renames
from ashfall_app.opening.schema import Opening, to_rules
from tests.opening.edited import edited, roots_renamed
from tests.opening.playthrough import opening
from tests.saves.changes import retuned_opening
from tools import content_lock


type Built = tuple[Opening, Rules]
"""An opening with its rules, so a test that checks one opening twice converts it once."""


def built(o: Opening) -> Built:
    return o, to_rules(o)


@pytest.fixture(scope="module")
def with_roots_renamed() -> Built:
    """The content with the store `roots` renamed `tubers` everywhere in its data (its text keys unchanged), built in
    setup: it re-parses and merges every chapter. Tests only read it."""
    o = edited(roots_renamed)
    assert any(s.id == "tubers" for s in o.stores) and not any(s.id == "roots" for s in o.stores)
    return built(o)


def shipped(extra: list[RenameEntry] | None = None) -> list[RenameEntry]:
    """renames.toml's renames, then `extra`: a test edit starts from what has shipped."""
    return [*load_renames(), *(extra or [])]


@cache
def shipped_built() -> Built:
    return built(opening())


@pytest.fixture(scope="module", autouse=True)
def shipped_opening_loaded() -> Built:
    """The shipped opening and its rules, built in setup so no test's timed call pays for them."""
    return shipped_built()


def found(o: Opening | Built, renames: list[RenameEntry] | None = None, lock: Lock | None = None) -> list[Problem]:
    o, rules = built(o) if isinstance(o, Opening) else o
    rs = shipped(renames)
    return problems(load_lock() if lock is None else lock, snapshot(o, rules, rs), rs)


def classes(ps: list[Problem]) -> set[str]:
    return {p.cls for p in ps}


def rename(kind: str, old: str, new: str) -> RenameEntry:
    return RenameEntry.model_validate({"kind": kind, "from": old, "to": new})


def released(**ids: list[str]) -> Lock:
    """The lock as if these ids had also been released."""
    lock = load_lock()
    return lock.model_copy(update={"ids": {k: sorted([*v, *ids.get(k, [])]) for k, v in lock.ids.items()}})


def test_the_shipped_opening_matches_the_lock():
    """What the server checks at start: nothing out of date, unmapped or forbidden."""
    assert release_problems(opening()) == []


def test_the_lock_is_alone_in_its_directory():
    assert [p.name for p in LOCK.parent.iterdir()] == ["ids.json"]


@pytest.fixture(scope="module")
def safe_changes() -> Built:
    """Reworded text, a retuned work_s, raised caps, an appended curve level, reordered cards and a new card, built in
    setup (it re-parses every chapter); the test only reads it."""
    o = edited(lambda d: d.replace("work_s = 45", "work_s = 60"), lambda t: t.replace('"roots"', '"tubers"'))
    extra = o.cards[4].model_copy(update={"id": "gather_more", "glows": False})
    o = o.model_copy(update={
        "curve_items": [*o.curve_items, o.curve_items[-1] * 2], "cards": [*o.cards[1:], o.cards[0], extra],
        "stores": [s.model_copy(update={"cap_items": s.cap_items + 1}) if s.id == "stones" else s for s in o.stores],
    })
    return built(o)


def test_safe_changes_are_green_once_written(safe_changes: Built):
    """The safe changes (`safe_changes`): only the lock wanting a write; once written, nothing."""
    o, rules = safe_changes
    check_opening(o)
    assert classes(found((o, rules))) == {"out_of_date"}
    assert found((o, rules), lock=merged(load_lock(), snapshot(o, rules, shipped()))) == []


def test_a_renamed_store_needs_its_mapping(with_roots_renamed: Built):
    assert "needs_mapping" in classes(found(with_roots_renamed))
    assert classes(found(with_roots_renamed, [rename("store", "roots", "tubers")])) == {"out_of_date"}


def test_a_renamed_id_inside_a_trigger_outcome_is_not_a_changed_outcome(with_roots_renamed: Built):
    """`roots` is named in an outcome; mapped, the outcome compares equal through the rename."""
    ps = found(with_roots_renamed, [rename("store", "roots", "tubers")])
    assert not any("outcome" in p.message for p in ps), ps


def test_a_removed_card_is_told_to_retire_it():
    ps = found(shipped_built(), lock=released(card=["ghost_card"]))
    assert any(p.cls == "needs_mapping" and "card ghost_card" in p.message and "retire it instead" in p.message
               for p in ps), ps


def test_a_removed_store_needs_a_mapping():
    ps = found(shipped_built(), lock=released(store=["ghost_store"]))
    assert any(p.cls == "needs_mapping" and "store ghost_store" in p.message for p in ps), ps


@pytest.mark.parametrize("kind", ["entry", "note", "node"])
def test_a_removed_entry_note_or_node_needs_a_mapping(shipped_opening: Opening, kind: str):
    """The journal's pages and notes are released ids as any (CONTRACT.txt, "JOURNAL"), and so are prestige nodes, which
    a save's picks name; only a rename onto an id the content has answers it, so a rename to nothing is still told
    so."""
    lock = released(**{kind: [f"ghost_{kind}"]})
    ps = found(shipped_built(), lock=lock)
    assert any(p.cls == "needs_mapping" and f"{kind} ghost_{kind} was removed" in p.message for p in ps), (kind, ps)
    ps = found(shipped_built(), [rename(kind, f"ghost_{kind}", f"{kind}_gone")], lock=lock)
    assert any(f"{kind} ghost_{kind} is renamed to {kind}_gone, which the content lacks" in p.message for p in ps), ps


def test_reusing_a_renamed_away_id_is_forbidden():
    """roots renamed away while the content still declares roots."""
    assert "forbidden" in classes(found(shipped_built(), [rename("store", "roots", "tubers")]))


def test_renaming_onto_a_released_id_is_forbidden():
    assert "forbidden" in classes(found(shipped_built(), [rename("store", "brand_new", "stones")]))


def test_a_lowered_store_cap_is_forbidden():
    o = opening()
    lower = o.model_copy(update={"stores": [s.model_copy(update={"cap_items": s.cap_items - 1}) if s.id == "stones"
                                            else s for s in o.stores]})
    assert any(p.cls == "forbidden" and "store stones" in p.message for p in found(lower))


def test_a_lowered_card_cap_and_a_new_cap_are_forbidden():
    """Released with a higher cap, or with none (the content's cap is then a cap given where there was none)."""
    o = opening()
    lock = load_lock()
    capped = next(c.id for c in o.cards if c.cap is not None)
    cap = lock.card_caps[capped]
    assert cap is not None
    for was in (cap + 1, None):
        ps = found(o, lock=lock.model_copy(update={"card_caps": {**lock.card_caps, capped: was}}))
        assert any(p.cls == "forbidden" and f"card {capped}" in p.message for p in ps), (was, ps)


def test_an_uncapped_card_is_a_raised_cap():
    """A card released with a cap that the content now leaves uncapped."""
    o = opening()
    uncapped = next(c.id for c in o.cards if c.cap is None)
    lock = load_lock()
    was_capped = lock.model_copy(update={"card_caps": {**lock.card_caps, uncapped: 3}})
    assert not any(p.cls == "forbidden" for p in found(o, lock=was_capped))


def test_a_changed_curve_threshold_is_forbidden():
    o = opening()
    changed = o.model_copy(update={"curve_items": [o.curve_items[0] + 1, *o.curve_items[1:]]})
    assert any(p.cls == "forbidden" and "curve" in p.message for p in found(changed))


def _with_outcome_lines(o: Opening, trigger: str, extra: int) -> Opening:
    def out(t_lines: list[str]) -> list[str]:
        return [*t_lines, *t_lines[:extra]]
    return o.model_copy(update={"triggers": [
        t.model_copy(update={"outcome": t.outcome.model_copy(update={"line_keys": out(t.outcome.line_keys)})})
        if t.id == trigger else t for t in o.triggers]})


def test_a_changed_trigger_outcome_is_forbidden():
    o = opening()
    t = next(t.id for t in o.triggers if t.outcome.line_keys)
    assert any(p.cls == "forbidden" and f"trigger {t}" in p.message for p in found(_with_outcome_lines(o, t, 1)))


def test_a_renamed_trigger_is_followed():
    """Mapped, a renamed trigger with its outcome unchanged is fine; with its outcome changed it is still caught."""
    o = opening()
    t = next(t.id for t in o.triggers if t.outcome.line_keys)
    renamed = o.model_copy(update={"triggers": [x.model_copy(update={"id": "t_renamed"}) if x.id == t else x
                                                for x in o.triggers]})
    mapping = [rename("trigger", t, "t_renamed")]
    assert classes(found(renamed, mapping)) == {"out_of_date"}
    changed = _with_outcome_lines(renamed, "t_renamed", 1)
    assert any(p.cls == "forbidden" and f"trigger {t}" in p.message for p in found(changed, mapping))


def test_inserting_a_camp_level_is_forbidden():
    """Camp triggers are numbered, so a level inserted before the last shifts every later level's outcome."""
    o = opening()
    assert o.camp is not None
    first = o.camp.levels[0]
    levels = [first.model_copy(update={"at_items": 1, "line_keys": [], "modifiers": []}), *o.camp.levels]
    changed = o.model_copy(update={"camp": o.camp.model_copy(update={"levels": levels})})
    assert any(p.cls == "forbidden" and "outcome" in p.message for p in found(changed))


def test_a_changed_kind_is_forbidden():
    """An id released as a store that the content now declares as a lane (and no longer as a store)."""
    o = opening()
    as_lane = o.model_copy(update={"lanes": [*o.lanes, o.lanes[0].model_copy(update={"id": "ghost"})]})
    ps = found(as_lane, lock=released(store=["ghost"]))
    assert any(p.cls == "forbidden" and "store ghost" in p.message and "another kind" in p.message for p in ps), ps


def test_dropping_a_released_rename_is_forbidden(with_roots_renamed: Built):
    o, rules = with_roots_renamed
    mapping = [rename("store", "roots", "tubers")]
    lock = merged(load_lock(), snapshot(o, rules, shipped(mapping)))
    assert found(with_roots_renamed, mapping, lock) == []
    assert any(p.cls == "forbidden" and "dropped" in p.message for p in found(with_roots_renamed, [], lock))


def test_a_cycle_of_renames_is_forbidden():
    ps = found(shipped_built(), [rename("store", "a_new", "b_new"), rename("store", "b_new", "a_new")])
    assert any(p.cls == "forbidden" and "cycle" in p.message for p in ps), ps


def test_a_format_bump_without_an_upgrade_is_forbidden(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(upgrade_module, "FORMAT", upgrade_module.FORMAT + 1)
    assert any(p.cls == "forbidden" and "no upgrade" in p.message for p in found(shipped_built()))


@pytest.fixture(scope="module")
def today_and_retuned() -> tuple[Lock, Lock, Lock, list[Problem]]:
    """(today's snapshot, a numbers-only retune's snapshot, the lock merged with it, the retune's problems), built in
    setup: each snapshot digests every shipped chapter."""
    current, retuned = opening(), retuned_opening()
    later = snapshot(retuned, to_rules(retuned), shipped())
    return snapshot(current, to_rules(current), shipped()), later, merged(load_lock(), later), found(retuned)


def test_the_release_rises_by_one_with_each_change_of_the_rules_and_only_then(
        today_and_retuned: tuple[Lock, Lock, Lock, list[Problem]]):
    """The content release orders builds for saves (api/CONTRACT.txt): a numbers-only retune is a new release; writing
    the same content again is not."""
    lock = load_lock()
    today, retuned, later, retuned_found = today_and_retuned
    assert lock.release >= 1 and lock.digest == today.digest   # the lock on disk holds today's content
    assert merged(lock, today).release == lock.release
    assert (later.release, later.digest) == (lock.release + 1, retuned.digest)
    assert retuned_found and all(p.cls == "out_of_date" for p in retuned_found)   # --write may record it


def test_the_lock_is_never_reset_after_launch(capsys: pytest.CaptureFixture[str]):
    """Saves persist for players now (the cutover): --reset refuses, so the lock is only ever extended."""
    before = LOCK.read_text()
    assert content_lock.LAUNCHED and content_lock.main(["--reset"]) == 1
    assert LOCK.read_text() == before and "refused" in capsys.readouterr().err


def test_the_lock_takes_the_rules_node_ids(shipped_opening: Opening):
    rules = to_rules(shipped_opening)
    node = NodeDef(NodeId("n_x"), rules.skills[0].id, StoreCap(rules.stores[0].id), ranks=1, per_rank_bp=1)
    shipped = [str(n.id) for n in rules.nodes]
    assert shipped and content_ids(shipped_opening, rules)["node"] == shipped
    assert content_ids(shipped_opening, replace(rules, nodes=(*rules.nodes, node)))["node"] == [*shipped, "n_x"]
