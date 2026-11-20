"""The dry rule's cost, as built (engine DESIGN.txt, "Pause"): it pauses one consumer at a time and reads the store's
net after each, but rebuilds the save once, when it is done. A running-mix change clears every pause and the stores
that ran dry pause their consumers again at that instant, so on a save with several stores held empty for good this
rule runs at most instants (issue 400)."""
import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, ActionId, Flow, PacingCurve, Rules, Save, SkillDef, SkillId, StandingDef, StoreDef, StoreId,
    advance, new_save, per_hour, segment, validate_rules,
)
from ashfall_app.engine import handlers

X = StoreId("x")
EATERS = tuple(ActionId(f"eat{i}") for i in range(5))


def world() -> tuple[Rules, Save]:
    """x starts at one item, made at half an item an hour and eaten by five standing actions at a quarter each: it
    empties at 4,800 s, and pausing the last three eaters brings its net to 0."""
    standing = (StandingDef(ActionId("make"), (Flow(X, per_hour(1) // 2),), ()),
                *(StandingDef(a, (), (Flow(X, per_hour(1) // 4),)) for a in EATERS))
    r = Rules(stores=(StoreDef(X, 100 * Q, Q),), skills=(SkillDef(SkillId("k")),), standing=standing,
              curve=PacingCurve((10**15,)), cards=())
    validate_rules(r)
    return r, new_save(r)


def test_the_dry_rule_pauses_the_last_three_eaters_and_holds_x_at_0():
    r, s = world()
    s = advance(s, r, 4800)
    assert [p.runner for p in s.pauses] == list(EATERS[2:])
    assert segment(s, r, X).start_value == 0 and segment(s, r, X).rate == 0


def test_pausing_three_consumers_rebuilds_the_save_once(monkeypatch: pytest.MonkeyPatch):
    r, s = world()
    s = advance(s, r, 4799)
    calls: list[int] = []
    real = handlers.rebuild

    def counted(save: Save, rules: Rules) -> Save:
        calls.append(save.time)
        return real(save, rules)

    monkeypatch.setattr(handlers, "rebuild", counted)
    s = advance(s, r, 4800)
    assert len(s.pauses) == 3
    assert calls == [4800]
