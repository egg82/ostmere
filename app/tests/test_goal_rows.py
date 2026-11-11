"""View.goal_rows on a fixture world (api/goalrows.py; CONTRACT.txt, "Goal rows"): when each goal lands at the rates as
set, a tap of the hands set aside, and the dry store that binds it.

Skill k is trained by `chop` (an hour per level at a full share) and `saw`, which turns plank input `log` into `plank`
and trains k at half chop's rate; `fell` makes `log`; `press` turns `glue` into `plank`. `nap` is a capped tap, so a
tap can hold the hands."""
from ashfall_app import engine as e
from ashfall_app.api import goal_models as g
from ashfall_app.api.goalrows import goal_rows
from ashfall_app.engine import BP, CardDef, CardId, CardShare, MixId, PacingCurve, Rules, Save, SkillDef, SkillId
from ashfall_app.engine.flows import Flow
from ashfall_app.engine.lanes import TapCard
from ashfall_app.engine.mixes import Mix, SwitchMix
from ashfall_app.engine.ids import ActionId
from ashfall_app.engine.rules import StandingDef, StoreDef
from ashfall_app.engine.units import per_hour, units
from ashfall_app.engine.verbs import SaveMix
from tests.worth import goaltime as gt

K = SkillId("k")
LOG, PLANK, OIL, GLUE = e.StoreId("log"), e.StoreId("plank"), e.StoreId("oil"), e.StoreId("glue")
LEVEL_XP = units(100)
XP = LEVEL_XP // 3600
"""chop's XP per hour in rate units: a level an hour at a full share."""


def world(logs: int = 0, watch: bool = False) -> tuple[Rules, Save]:
    """`watch`: a standing action training k that costs `oil`, a store the ledger never draws, at 0."""
    cards = (CardDef(CardId("chop"), 60, skill=K, xp_per_hour=XP),
             CardDef(CardId("saw"), 60, skill=K, xp_per_hour=XP // 2, makes=(Flow(PLANK, per_hour(6)),),
                     costs=(Flow(LOG, per_hour(6)),)),
             CardDef(CardId("fell"), 60, makes=(Flow(LOG, per_hour(3)),)),
             CardDef(CardId("nap"), 600, cap=5),
             CardDef(CardId("press"), 60, makes=(Flow(PLANK, per_hour(2)),), costs=(Flow(GLUE, per_hour(2)),)))
    standing = (StandingDef(ActionId("watch"), costs=(Flow(OIL, per_hour(1)),), skill=K, xp_per_hour=XP),) if watch else ()
    r = Rules(stores=(StoreDef(LOG, units(50), units(logs)), StoreDef(PLANK, units(20)), StoreDef(OIL, units(5)),
                      StoreDef(GLUE, units(5))),
              skills=(SkillDef(K),), standing=standing,
              curve=PacingCurve((LEVEL_XP, 10 * LEVEL_XP)), max_firings_per_instant=100, lanes=(), cards=cards, chips=(),
              triggers=(), opening=(e.Unlock(e.UnlockKind.SKILL, K), e.Unlock(e.UnlockKind.STORE, LOG),
                                    e.Unlock(e.UnlockKind.STORE, PLANK), e.Unlock(e.UnlockKind.STORE, GLUE),
                                    *(e.Unlock(e.UnlockKind.CARD, c.id) for c in cards),
                                    *(e.Unlock(e.UnlockKind.ACTION, a.id) for a in standing)))
    return r, e.new_save(r)


def running(r: Rules, s: Save, shares: dict[str, int]) -> Save:
    mix = Mix(MixId("m"), tuple(CardShare(CardId(c), bp) for c, bp in shares.items()))
    return e.decide(e.decide(s, r, s.time, SaveMix(mix)), r, s.time, SwitchMix(MixId("m")))


def plank_goal(target: int) -> g.Goal:
    return g.Goal(kind=g.GoalKind.STORE, store=str(PLANK), card=None, skill=None, target=target, value=None, at=None, feeds=[])


def rows(r: Rules, s: Save, goals: list[g.Goal] | None = None) -> list[g.GoalRow]:
    return goal_rows(s, r, e.view(s, r), goals or [])


def test_a_skills_next_level_lands_at_its_rate_from_every_card_training_it() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"chop": BP // 2, "saw": BP // 2})
    [row] = rows(r, s)
    rate = XP // 2 + XP // 4
    assert (row.kind, row.skill, row.target, row.per_hour, row.limit) == (g.GoalKind.LEVEL, "k", 2, rate, None)
    assert row.lands_at == s.time + e.ceil_div(LEVEL_XP, rate)


def test_a_tap_of_the_hands_is_set_aside() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"chop": BP})
    tapped = e.decide(s, r, s.time, TapCard(CardId("nap")))
    assert any(ls.card == CardId("nap") for ls in tapped.lanes), "control: the tap holds the hands"
    assert e.view(tapped, r).skills[0].xp.rate == 0, "control: the mix yields to the tap"
    assert rows(r, tapped) == rows(r, s)


def test_a_store_goal_lands_at_its_net_and_names_no_limit_while_its_inputs_hold() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"saw": BP})
    [store, _] = rows(r, s, [plank_goal(units(12))])
    assert (store.kind, store.store, store.per_hour, store.limit) == (g.GoalKind.STORE, "plank", per_hour(6), None)
    assert store.lands_at == s.time + 2 * 3600


def test_a_dry_input_binds_the_goal_with_what_comes_into_it() -> None:
    r, s = world(logs=0)
    s = running(r, s, {"saw": BP // 2, "fell": BP // 2})
    s = e.advance(s, r, s.time + 60)
    assert any(p.store == LOG for p in s.pauses), "control: saw is paused on the dry log"
    store, level = rows(r, s, [plank_goal(units(12))])
    fed = g.GoalLimit(store="log", in_per_hour=per_hour(3))   # the paused saw hands its share to fell
    assert (store.limit, level.limit) == (fed, fed)


def test_a_target_over_the_cap_and_a_met_goal() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"saw": BP})
    [over, _] = rows(r, s, [plank_goal(units(21))])
    assert over.lands_at is None and over.per_hour > 0
    [met, _] = rows(r, s, [plank_goal(0)])
    assert met.lands_at == s.time


def test_nothing_training_the_skill_never_lands_it() -> None:
    r, s = world(logs=40)
    s = running(r, s, {"fell": BP})
    [row] = rows(r, s)
    assert (row.per_hour, row.lands_at) == (0, None)


def test_a_store_the_ledger_never_draws_binds_nothing() -> None:
    r, s = world(logs=40, watch=True)
    s = e.advance(running(r, s, {"chop": BP}), r, s.time + 60)
    assert any(p.store == OIL for p in s.pauses), "control: watch is paused on the dry oil"
    [row] = rows(r, s)
    assert (row.limit, row.per_hour) == (None, XP)


def test_the_worth_readouts_rates_agree_on_the_players_own_mix() -> None:
    """tests/worth/goaltime.py scores probe mixes no save holds; on the mix the save runs, its XP rate is the row's."""
    r, s = world(logs=40)
    s = running(r, s, {"chop": BP // 4, "saw": 3 * BP // 4})
    [row] = rows(r, s)
    assert gt.rates(gt.board(s, e.view(s, r), r), gt.own_mix(s)) == {"k": row.per_hour}


def test_of_two_dry_inputs_the_first_in_the_mix_binds_not_the_first_in_the_ledger() -> None:
    r, s = world(logs=0)
    for first, second, binds in (("press", "saw", "glue"), ("saw", "press", "log")):
        t = e.advance(running(r, s, {first: BP // 2, second: BP // 2}), r, s.time + 60)
        assert {p.store for p in t.pauses} >= {LOG, GLUE}, "control: both makers wait on a dry store"
        [store, _] = rows(r, t, [plank_goal(units(12))])
        assert store.limit is not None and store.limit.store == binds, (first, store.limit)


def test_a_met_goal_names_no_limit() -> None:
    r, s = world(logs=0)
    s = e.advance(running(r, s, {"saw": BP}), r, s.time + 60)
    assert any(p.store == LOG for p in s.pauses), "control: saw is paused on the dry log"
    [unmet, _] = rows(r, s, [plank_goal(units(12))])
    [met, _] = rows(r, s, [plank_goal(0)])
    assert (unmet.limit is not None, met.limit, met.lands_at) == (True, None, s.time)


def test_a_skill_at_its_top_level_has_no_row() -> None:
    r, s = world(logs=40)
    s = e.advance(running(r, s, {"chop": BP}), r, s.time + 11 * 3600)
    assert e.view(s, r).skills[0].level == 3, "control: the curve's last level"
    story = g.Goal(kind=g.GoalKind.LEVEL, store=None, card=None, skill="k", target=4, value=None, at=None, feeds=[])
    assert rows(r, s, [story]) == []
