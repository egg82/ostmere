"""Week five's route policies (policy.py) on fixtures: the data `later` builds from a chapter's table for each route, and the
cast notable's card put on the line by the casting contract's fixture world. Ids are the fixtures' own."""
from collections.abc import Callable
from pathlib import Path

from ashfall_app.engine import (
    AfterTime, AnswerId, CardId, CardShare, ChipId, Mix, OfferId, Order, Rules, Save, SaveMix, StoreId, TapCard, Unlock, UnlockKind, decide,
    view,
)
from ashfall_app.engine.mixes.mixes import flatten_shares
from ashfall_app.engine.mixes.mixruns import running_town_mix
from tests.daythree.chapter import ChipRule, Keep, Later
from tests.dayone.player.policy import Move
from tests.weekfive import fixtures, policy
from tests.weekfive.policy import CastCard, RouteShare, TwoAnswer, Week
from tests.weektwo import weekfour as w4

casting = fixtures.world("casting_world", "casting")
CHIP = ChipRule(ChipId("c1"), CardId("cure1"))
ORDER = (Unlock(UnlockKind.CARD, CardId("b1")), Order(AfterTime(0), TapCard(CardId("b1"))))


def _no_story(save: Save, rules: Rules) -> set[str]:
    return set()


WEEK = Week(
    start="Y0", stop="Y9", landed=_no_story, news=("Y1",), chips=(CHIP,),
    shares=(RouteShare(CardId("fill"), {"typical": 1500, "sharp": 2500}), RouteShare(CardId("trip2"), {"typical": 1000, "sharp": 0})),
    two_answers=(TwoAnswer(OfferId("o_two"), {"typical": AnswerId("o_two_yes"), "sharp": AnswerId("o_two_other")}),),
    order_cards=(ORDER,), arrivals=((OfferId("o_arr"), AnswerId("o_arr_stay")),),
    asks=((OfferId("o_ask"), AnswerId("o_ask_yes")),), steps=(CardId("glow"),), queued=(CardId("night"),),
    keeps=((Keep(CardId("make_input"), StoreId("input"), 5), frozenset({"sharp"})),))


def built(route: str) -> Later:
    return policy.later(w4.day_twenty_seven(route), WEEK, route)


def test_a_chapter_is_played_on_from_the_one_before():
    prev, now = w4.day_twenty_seven("typical"), built("typical")
    assert (now.start, now.stop) == ("Y0", "Y9") and now.news == ("Y1",)
    assert now.shares[:len(prev.shares)] == prev.shares and now.chip_rules[:len(prev.chip_rules)] == prev.chip_rules
    assert now.answers[:len(prev.answers)] == prev.answers and now.sinks.comforts == prev.sinks.comforts


def test_a_two_answer_offer_is_answered_each_way_across_the_routes():
    given = {r: dict(built(r).answers)[OfferId("o_two")] for r in ("typical", "sharp", "whenever")}
    assert given == {"typical": "o_two_yes", "sharp": "o_two_other", "whenever": "o_two_yes"}


def test_shares_follow_the_route_and_a_zero_share_is_not_in_the_mix():
    ours = {r: {s.card: s.share_bp for s in built(r).shares if s.card in ("fill", "trip2")} for r in ("typical", "sharp")}
    assert ours == {"typical": {"fill": 1500, "trip2": 1000}, "sharp": {"fill": 2500}}


def test_a_lazy_route_writes_no_chip_rule_and_the_others_write_it():
    assert policy.lazy("lazy") and not policy.lazy("typical") and not policy.lazy("whenever")
    assert CHIP in built("typical").chip_rules and CHIP not in built("lazy").chip_rules


def test_the_input_store_is_kept_only_by_the_routes_that_make_it():
    keeps = {r: [k for k in built(r).keeps if k.card == "make_input"] for r in ("typical", "sharp")}
    assert keeps["typical"] == [] and len(keeps["sharp"]) == 1


def test_orders_arrivals_asks_and_steps_come_through():
    now = built("typical")
    assert ORDER in now.order_cards and ((OfferId("o_arr"), AnswerId("o_arr_stay")) in now.sinks.arrivals)
    assert (OfferId("o_ask"), AnswerId("o_ask_yes")) in now.answers
    assert now.steps == (CardId("glow"),) and now.queued == (CardId("night"),)


HAUL = CastCard("lead", "{lane}_haul", {"typical": 2500, "sharp": 0})


def cast_scene(tmp_path: Path, at: int) -> tuple[Rules, Save]:
    """The casting fixture with t_b ahead on chops (the lead is cast on it), the haul card not in the town mix."""
    r = casting.rules_of(tmp_path)
    return r, casting.at(r, dict(t_a_chop=1000, t_b_chop=3000, t_c_chop=1000, t_m_chop=1000), at)


def own(route: str) -> Callable[..., Move | None]:
    return policy.cast_move((HAUL,), route)


def test_the_cast_lanes_card_is_put_in_the_mix_at_the_routes_share_once_cast(tmp_path: Path):
    r, before = cast_scene(tmp_path, casting.CAST_AT - 5)
    assert own("typical")(view(before, r), before, r) is None, "nothing is put on the line before the cast"
    r, after = cast_scene(tmp_path, casting.CAST_AT + 5)
    kind, verbs = own("typical")(view(after, r), after, r) or ("", ())
    mix = next(v.mix for v in verbs if isinstance(v, SaveMix))
    assert kind == "decision" and CardShare(CardId("t_b_haul"), 2500) in mix.components
    town = running_town_mix(after, r)
    assert town is not None and mix.id == town.id, "a card on a person's lane goes in the running town mix"
    for verb in verbs:   # the engine takes it: no mix holds the player's time and the town's together
        after = decide(after, r, after.time, verb)


def test_a_route_at_zero_share_keeps_the_card_off_the_line(tmp_path: Path):
    r, after = cast_scene(tmp_path, casting.CAST_AT + 5)
    assert own("sharp")(view(after, r), after, r) is None


def test_a_town_split_that_resets_the_cast_lane_keeps_the_cast_card_and_settles(tmp_path: Path):
    """The week-two splits save a lane's town shares whole; on the cast lane that would drop the cast card, and the cast
    move would put it back, one move each, for ever. With keep_casts the pair settles with the card on at its share."""
    r, s = cast_scene(tmp_path, casting.CAST_AT + 5)
    town = running_town_mix(s, r)
    assert town is not None
    split = SaveMix(Mix(town.id, flatten_shares(s.mixes, town.id)))

    def resets(v: object, save: Save, rules: Rules) -> Move | None:
        now = running_town_mix(save, rules)
        return None if now is not None and now == split.mix else ("decision", (split,))
    own_moves = policy.keep_casts(resets, (HAUL,), "typical")
    found: Move | None = None
    for _ in range(6):
        found = own_moves(view(s, r), s, r)
        if found is None:
            break
        for verb in found[1]:
            s = decide(s, r, s.time, verb)
    assert found is None, "the split and the cast card kept undoing each other"
    now = running_town_mix(s, r)
    assert now is not None and CardShare(CardId("t_b_haul"), 2500) in now.components

