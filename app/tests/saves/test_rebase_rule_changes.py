"""A save read under new content carries the rebase instant's rule changes, so the rule runs list a rule new content
installed from the load (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS", "Rebase"); an exact read
carries none. No database: the read itself (saves/load.py)."""
from datetime import UTC, datetime

from ashfall_app import engine as e
from ashfall_app.db.saves import SaveRecord
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.load import load

Q = e.QUANTITY_SCALE
A = e.CardId("a")
T0 = datetime(2026, 1, 1, tzinfo=UTC)


def rules(installs: bool) -> e.Rules:
    t = e.TriggerDef(e.TriggerId("arrive"), e.AfterTime(10), e.Outcome(orders=(e.RuleInstall(A),)))
    return e.Rules(stores=(e.StoreDef(e.StoreId("x"), 10 * Q),), skills=(e.SkillDef(e.SkillId("k")),), standing=(),
                   curve=e.PacingCurve((10 * Q,)), lanes=(e.LaneDef(e.LaneId("helper"), True),),
                   cards=(e.CardDef(A, 30, lane=e.LaneId("helper")),), triggers=(t,) if installs else ())


def ruleset(r: e.Rules) -> Ruleset:
    return Ruleset(rules=r, digest=e.rules_digest(r), renames=(), start_lines=(), line_renames={}, build="b",
                   release=2)


def row(save: e.Save, r: e.Rules) -> SaveRecord:
    return SaveRecord(id=1, account_id=1, started_at=T0, updated_at=T0, state=e.encode(save, r), format=e.FORMAT,
                      rules_digest=e.rules_digest(r), decisions=0, game_time=save.time, ended_at=None, build="a",
                      release=1, number=1, camp_level=None, deleted_at=None)


def test_a_load_under_new_content_carries_the_installed_rule_coming_on():
    old, new = rules(False), rules(True)
    loaded = load(row(e.advance(e.new_save(old), old, 20), old), ruleset(new))
    assert loaded.rebased and loaded.save.orders == (e.Order(e.AfterTime(0), e.TapCard(A)),)
    assert [(c.time, c.on) for c in loaded.rule_changes] == [(20, True)]


def test_an_exact_read_carries_none():
    r = rules(True)
    loaded = load(row(e.advance(e.new_save(r), r, 20), r), ruleset(r))
    assert not loaded.rebased and loaded.rule_changes == () and loaded.save.orders
