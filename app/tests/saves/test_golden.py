"""Golden saves (golden/f<FORMAT>/, written by tools/save_corpus.py; every format's are kept, so a FORMAT bump runs
the older ones through UPGRADES for real) load under today's opening and under a test change of it
(a new card a new trigger unlocks, a renamed store with its mapping, a retuned work_s), keep everything they had
earned, and run on (engine DESIGN.txt, "Rebase", invariants 49 to 51).

Pushes advance each save one game day (the 2 s ceiling); the nightly tests-deep run sets SAVES_DAYS=30, and the
saves-forward CI job advances the saves of the commit before a push 30 days with the pushed code."""
import os
from functools import cache
from pathlib import Path

import pytest

from ashfall_app.engine import (
    BP, FORMAT, OLDEST_FORMAT, Rules, Save, Step, StoreId, TriggerId, Unlock, UnlockKind, advance, rebase, rebase_logged,
)
from ashfall_app.opening.renames import engine_renames, load_renames
from ashfall_app.opening.schema import load_opening, to_rules
from tests.saves.changes import RENAMES, RETUNED, changed_opening

GOLDEN = Path(__file__).resolve().parent / "golden"
SAVES = sorted(p for f in range(OLDEST_FORMAT, FORMAT + 1) for p in (GOLDEN / f"f{f}").glob("*.json"))
DAYS = int(os.environ.get("SAVES_DAYS", "1"))
DAY_S = 86_400


@cache
def today() -> Rules:
    return to_rules(load_opening())


@cache
def changed() -> Rules:
    return to_rules(changed_opening())


def text(path: Path) -> str:
    return path.read_text().strip()


def loaded(path: Path) -> Save:
    """The golden save under today's opening: decoded if it is today's format and rules, else rebased."""
    return rebase(text(path), today(), engine_renames(load_renames()))


@pytest.fixture(scope="module")
def all_loaded() -> dict[Path, Save]:
    """Every golden save under today's opening, built in setup so a test times only what it checks. Read-only."""
    return {p: loaded(p) for p in SAVES}


def test_the_golden_saves_cover_the_opening_and_every_readable_format(all_loaded: dict[Path, Save]):
    assert all(any((GOLDEN / f"f{f}").glob("*.json")) for f in range(OLDEST_FORMAT, FORMAT + 1))
    assert len(SAVES) >= 10, SAVES
    saves = list(all_loaded.values())
    assert any(s.time == 0 for s in saves) and any(s.ended_at is not None for s in saves)
    assert any(s.mixes for s in saves) and any(s.orders for s in saves)
    assert any(ls.card is not None for s in saves for ls in s.lanes)


@pytest.fixture
def under_todays_opening(path: Path) -> Save:
    return rebase_logged(text(path), today(), engine_renames(load_renames())).save


@pytest.mark.parametrize("path", SAVES, ids=lambda p: p.stem)
def test_a_golden_save_runs_on_under_todays_opening(path: Path, under_todays_opening: Save):
    save = under_todays_opening
    advance(save, today(), save.time + DAYS * DAY_S)


@pytest.fixture
def under_the_change(path: Path) -> Step:
    return rebase_logged(text(path), changed(), RENAMES)


@pytest.mark.parametrize("path", SAVES, ids=lambda p: p.stem)
def test_a_golden_save_survives_a_content_change(path: Path, all_loaded: dict[Path, Save], under_the_change: Step):
    before = all_loaded[path]
    step = under_the_change
    after = step.save
    _kept(before, after)
    assert Unlock(UnlockKind.CARD, "gather_more") in after.unlocked
    assert after.fired[[t.id for t in changed().triggers].index(TriggerId("t_gather_more"))]
    assert changed().cards[0].lines[0] in [ln.key for ln in step.lines]
    assert all(ln.time == before.time for ln in step.lines)


@pytest.mark.parametrize("path", SAVES, ids=lambda p: p.stem)
def test_a_golden_save_runs_on_under_a_content_change(path: Path, under_the_change: Step):
    after = under_the_change.save
    advance(after, changed(), after.time + DAYS * DAY_S)


def _kept(before: Save, after: Save) -> None:
    """Invariants 49 and 51 for this change: nothing earned is taken back, and the retuned card's bar is rescaled."""
    assert after.time == before.time and after.ended_at == before.ended_at
    rename = {StoreId("roots"): StoreId("tubers")}
    now = {st.store: st.segment.start_value for st in after.stores}
    for st in before.stores:
        assert now[rename.get(st.store, st.store)] >= st.segment.start_value, st.store
    xp = {st.skill: st.xp.start_value for st in after.skills}
    assert all(xp[st.skill] >= st.xp.start_value for st in before.skills)
    work = {cs.card: cs for cs in after.cards}
    for cs in before.cards:
        w = cs.work.start_value
        if cs.card == RETUNED:
            n, rem = divmod(w, 45 * BP)
            w = n * 60 * BP + rem * 60 // 45
        assert (work[cs.card].work.start_value, work[cs.card].raised) == (w, cs.raised), cs.card
    assert set(before.unlocked) <= {_unrename(u) for u in after.unlocked}
    fired = dict(zip((t.id for t in changed().triggers), after.fired))
    assert all(fired[t.id] for t, f in zip(today().triggers, before.fired) if f)
    assert [m.id for m in after.mixes] == [m.id for m in before.mixes] and len(after.orders) == len(before.orders)


def _unrename(u: Unlock) -> Unlock:
    return Unlock(u.kind, "roots") if u.kind is UnlockKind.STORE and u.id == "tubers" else u
