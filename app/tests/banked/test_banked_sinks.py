"""The sink policies (tests/dayone/sinks.py) on the fixture chapter, by route: typical and sharp mix the trip and queue
the comfort, lazy does neither, and no route sets an order for the arrival offer (it is of no kind, and the page builds
no per-offer rule), so it waits for a visit. The cap-loss check (dayone/capcheck.py) tells the two apart."""
import pytest

from ashfall_app.engine import (
    BP, AnswerOffer, CardShare, Mix, MixId, SaveMix, SetOrders, SetQueue, StoreId, SwitchMix, TapCard, advance, decide,
    new_save, value_at, view,
)
from ashfall_app.engine.offerstate import answer_given
from tests.banked.chapter import CHAPTER, COMFORT, FOUND, GATHER, NEWCOMER, STAY, TRIP, WOOD, rules
from tests.banked.play import Played, built, play
from tests.dayone import capcheck
from tests.dayone.sinks import SINKS, queue_comforts

H = 3600
VISITS = ((0, 3 * H), (30 * H, 31 * H))
"""Three hours at the start, in which the trip and the comfort show (at 30 min) and the wood fills (at 2 h), which is when
its ledger line is drawn and the trip can be mixed, and a visit past the night's offer (4 h)."""
NIGHT = 5 * H


def route(name: str, until: int = 40 * H) -> Played:
    return play(VISITS, SINKS[name], until)


def mixes(p: Played) -> bool:
    return any(isinstance(v, SaveMix) and any(isinstance(c, CardShare) and c.card == TRIP for c in v.mix.components)
               for _, v in p.log)


def queues(p: Played) -> bool:
    return any(isinstance(v, SetQueue) and any(e.verb == TapCard(COMFORT) for e in v.entries) for _, v in p.log)


def orders_answer(p: Played) -> bool:
    return any(isinstance(v, SetOrders) and any(o.then == AnswerOffer(NEWCOMER, STAY) for o in v.orders)
               for _, v in p.log)


@pytest.mark.parametrize("name", ["typical", "sharp"])
def test_typical_and_sharp_mix_the_trip_and_queue_the_comfort(name: str):
    p = route(name)
    assert mixes(p) and queues(p) and not orders_answer(p)
    assert built(p) == 1
    assert value_at(next(s for s in p.save.stores if s.store == FOUND).segment, p.save.time) > 0, "the trip ran"


def test_lazy_does_neither():
    p = route("lazy")
    assert not mixes(p) and not queues(p) and not orders_answer(p)
    assert built(p) == 0
    assert value_at(next(s for s in p.save.stores if s.store == FOUND).segment, p.save.time) == 0


def test_the_trip_is_mixed_at_its_visit_not_before():
    p = route("typical")
    assert [t for t, v in p.log if isinstance(v, SaveMix) and any(
        isinstance(c, CardShare) and c.card == TRIP for c in v.mix.components)] == [3 * H]


def test_no_route_sets_an_order_for_an_offer_of_no_kind_so_none_takes_it_in_the_night():
    r = rules()
    night = 4 * H + 60
    for name in ("whenever", "typical", "lazy"):
        assert answer_given(route(name, night).save, r, NEWCOMER) is None
        assert not orders_answer(route(name))


def test_the_check_tells_a_mixed_trip_from_none():
    """After the same visits, away 8 h and 24 h: the typical player's trip draws the wood down; the lazy player's sits
    at its cap and loses what the gatherer makes."""
    r = rules()
    assert capcheck.failing(route("typical", 4 * H).save, r) == {}
    assert capcheck.failing(route("lazy", 4 * H).save, r) == {"wood": (8, 24)}


def test_the_chapter_names_what_the_policies_read():
    assert [t.card for t in CHAPTER.trips] == [TRIP] and CHAPTER.comforts == (COMFORT,)
    assert StoreId("wood") in {t.supply for t in CHAPTER.trips}
    assert advance


def test_a_trip_whose_supply_line_is_not_drawn_yet_is_not_mixed():
    """At the first visit's first hour the wood is rising and not full: the page draws no wood line to offer the trip on."""
    r = rules()
    early = view(advance(route("lazy", H).save, r, H), r)
    assert any(ln.store == WOOD for ln in early.ledger), "the line exists in the view"
    p = route("typical", H + H // 2)
    assert not mixes(p), "not mixed before the wood is full and the line drawn"


def test_a_comfort_showing_no_ready_time_is_not_queued_and_one_that_will_be_ready_is():
    """The page offers When ready only with a ready time (client game/queue.ts); queued without one, the comfort would
    hold the queue's head forever. With nothing making wood the comfort shows no ready time; with the gatherer, one."""
    r = rules()
    bare = advance(new_save(r), r, H)
    v = view(bare, r)
    blocker = next(c for c in v.cards if c.card == COMFORT).blocker
    assert blocker is not None and blocker.ready_at is None
    assert queue_comforts(v, bare, CHAPTER) is None
    s = decide(bare, r, H, SaveMix(Mix(MixId("g"), (CardShare(GATHER, BP),))))
    s = decide(s, r, H, SwitchMix(MixId("g")))
    move = queue_comforts(view(s, r), s, CHAPTER)
    assert move is not None and isinstance(move[1][0], SetQueue) and move[1][0].entries[-1].verb == TapCard(COMFORT)
