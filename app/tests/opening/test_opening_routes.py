"""The opening through the game API, end to end with FastAPI's TestClient on a database: content, a new save, decisions
and advances by the server's clock, and the errors a decision can meet. The scripted routes' later moments (which need
a save at a given point) go through the same conversion the routes answer with (api/service.py), not over HTTP."""
from typing import Any

import pytest
from fastapi.testclient import TestClient

from ashfall_app.api.convert import condition, order_verb
from ashfall_app.api.content_models import Content
from ashfall_app.api.models import Decision, Order, Step, View
from ashfall_app.api.saves_models import DecisionRequest
from ashfall_app.api.service import Game
from ashfall_app.engine import (
    CardId, CardShare, InvalidVerbError, SaveMix, SetOrders, SwitchMix, TapCard, Verb, decide,
    decide_logged, new_save, rules_digest, units,
)
from ashfall_app.main import create_app
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import load_opening
from ashfall_app.saves.ruleset import ruleset
from tests.game_client import GameClient
from tests.opening.playthrough import Player, opening_rules

Json = dict[str, Any]


@pytest.fixture
def played(typical: Player) -> Player:
    """The typical route (routes.py), under this file's old name for it."""
    return typical


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture(scope="module")
def game_wire() -> Game:
    o = load_opening()
    return Game(o, ruleset(o, load_renames(), "dev", 1))


def tap(card: str) -> Json:
    return {"kind": "tap_card", "card": card}


def step(r: Any) -> Step:
    assert r.status_code == 200, r.text
    return Step.model_validate(r.json())


def error(r: Any, status: int, code: str) -> None:
    assert r.status_code == status, r.text
    assert r.json()["code"] == code and r.json()["message"]


def wire_decision(d: Json) -> Decision:
    """A decision as the decisions route reads it."""
    return DecisionRequest.model_validate({"decision": d, "after": 0}).decision


def test_content_names_the_rules_and_every_label(client: TestClient):
    c = Content.model_validate(client.get("/api/content").json())
    assert c.rules_digest == rules_digest(opening_rules())
    keys = {t.key for t in c.text_entries}
    assert {x.label_key for x in c.card_infos} <= keys
    assert {s.label_key for s in c.store_infos} <= keys
    assert c.scales.quantity_per_item == 3_600_000 and c.scales.bp == 10_000
    stand = next(x for x in c.card_infos if x.card == "stand_up")
    assert stand.lane == "hands" and stand.presentation == "narrative"


def test_a_new_save_starts_at_zero_with_one_card_and_the_content_digest(game: GameClient):
    g = Step.model_validate(game.begin()["step"])
    c = Content.model_validate(game.client.get("/api/content").json())
    assert g.rules_digest == c.rules_digest and g.decisions == 0
    assert g.view.at == 0
    assert [x.card for x in g.view.cards] == ["stand_up"] and g.view.cards[0].blocker is None
    assert g.view.ledger == [] and g.view.chips == [] and g.view.completed == []


def test_an_advance_at_the_same_time_redraws_the_same_view(game: GameClient):
    g = Step.model_validate(game.begin()["step"])
    again = step(game.advance(g.save_id))
    assert again.view == g.view and again.lines == [] and again.decisions == 0


def test_decisions_and_advances_carry_the_game_through_the_first_minute(game: GameClient):
    """Stand up is a told step of three: each tap is one completion with its line; at its cap it moves to Completed
    and the next step shows. The server's clock decides when."""
    g = Step.model_validate(game.begin()["step"])
    heard: list[str] = []
    for n in range(3):
        game.clock.tick(1)
        g = step(game.decide(g.save_id, tap("stand_up"), after=n))
        bar = next(b for b in g.view.lanes if b.lane == "hands")
        assert bar.running_card == "stand_up" and bar.completes_at is not None
        game.clock.tick(bar.completes_at - g.view.at)
        g = step(game.advance(g.save_id))
        heard += [ln.key for ln in g.lines]
    assert heard == ["l_up_1", "l_up_2", "l_up_3"]
    assert [x.card for x in g.view.completed] == ["stand_up"] and [x.card for x in g.view.cards] == ["look_around"]
    game.clock.tick(1)
    g = step(game.decide(g.save_id, tap("look_around"), after=3))
    done = next(b for b in g.view.lanes if b.lane == "hands").completes_at
    assert done is not None
    game.clock.tick(done - g.view.at)
    g = step(game.advance(g.save_id))
    assert [ln.key for ln in g.lines] == ["l_look"]
    assert [x.card for x in g.view.cards] == ["search_coat"]


def test_a_tap_is_one_completion(game: GameClient):
    g = Step.model_validate(game.begin()["step"])
    game.decide(g.save_id, tap("stand_up"), after=0)
    game.clock.tick(100)
    g = step(game.advance(g.save_id))
    assert [ln.key for ln in g.lines] == ["l_up_1"]
    assert g.lines[0].at == 3 and g.lines[0].seq == 0
    assert g.view.cards[0].completions == 1 and g.view.cards[0].cap == 3


def test_set_orders_and_set_queue_come_back_in_the_view(game: GameClient):
    g = Step.model_validate(game.begin()["step"])
    order = {"when": {"kind": "after_time", "at": 5}, "then": tap("stand_up")}
    g = step(game.decide(g.save_id, {"kind": "set_orders", "orders": [order]}, after=0))
    assert len(g.view.orders) == 1 and g.view.orders[0].then.kind == "tap_card"
    entry = {"verb": tap("stand_up"), "until": {"kind": "after_time", "at": 50}}
    game.clock.tick(1)
    g = step(game.decide(g.save_id, {"kind": "set_queue", "entries": [entry]}, after=1))
    assert len(g.view.queue) == 1 and len(g.view.orders) == 1


def test_a_store_rule_the_page_writes_is_taken_both_ways_with_a_band(game: GameClient):
    """Run when…'s two shapes (api/CONTRACT.txt, "a store rule"): "10 or more, until under 5" on a full store and
    "under 2, until 4" on an empty one are accepted, come back as sent, and hold at once."""
    g = Step.model_validate(game.begin()["step"])
    q = units(1)
    full = {"kind": "at_least", "watched": {"kind": "store_value", "store": "fullness"}, "value": 10 * q, "release": 5 * q}
    empty = {"kind": "at_most", "watched": {"kind": "store_value", "store": "dry_wood"}, "value": 2 * q - 1,
             "release": 4 * q - 1}
    orders = [{"when": full, "then": tap("gather_wood")}, {"when": empty, "then": tap("gather_wood")}]
    after = step(game.decide(g.save_id, {"kind": "set_orders", "orders": orders}, after=0))
    assert [o.model_dump(mode="json") for o in after.view.orders] == orders
    assert after.view.orders_on == [True, True]
    assert after.rules_digest == rules_digest(opening_rules())


def test_an_order_or_queue_condition_cannot_watch_running(game: GameClient):
    """The page builds no `running` subject (api/CONTRACT.txt, "Decisions"): one in set_orders or set_queue is refused
    and writes nothing, while the page's own store rule is taken."""
    g = Step.model_validate(game.begin()["step"])
    watching = {"kind": "at_least", "watched": {"kind": "running", "runner": "stand_up"}, "value": 1, "release": 1}
    error(game.decide(g.save_id, {"kind": "set_orders", "orders": [{"when": watching, "then": tap("stand_up")}]}, 0),
          422, "invalid_decision")
    error(game.decide(g.save_id, {"kind": "set_queue", "entries": [{"verb": tap("stand_up"), "until": watching}]}, 0),
          422, "invalid_decision")
    assert step(game.advance(g.save_id)).decisions == 0
    q = units(1)
    rule = {"kind": "at_least", "watched": {"kind": "store_value", "store": "fullness"}, "value": 10 * q, "release": 5 * q}
    taken = step(game.decide(g.save_id, {"kind": "set_orders", "orders": [{"when": rule, "then": tap("stand_up")}]}, 0))
    assert len(taken.view.orders) == 1


def test_a_decision_that_does_not_fit_is_invalid_decision(game: GameClient):
    g = Step.model_validate(game.begin()["step"])
    s = g.save_id
    error(game.decide(s, tap("build_fireback"), 0), 422, "invalid_decision")  # locked
    error(game.decide(s, tap("ghost"), 0), 422, "invalid_decision")  # unknown
    busy = step(game.decide(s, tap("stand_up"), 0))
    error(game.decide(s, tap("stand_up"), busy.decisions), 422, "invalid_decision")  # busy lane
    error(game.decide(s, {"kind": "switch_mix", "mix_id": "none"}, 1), 422, "invalid_decision")
    mix = {"id": "m", "components": [{"kind": "card_share", "card": "fire", "share_bp": 100}]}
    error(game.decide(s, {"kind": "save_mix", "mix": mix}, 1), 422, "invalid_decision")  # standing
    error(game.decide(s, {"kind": "nope"}, 1), 422, "invalid_decision")  # not even a decision
    assert step(game.advance(s)).decisions == 1   # the refusals wrote nothing


@pytest.mark.playthrough
def test_a_retired_card_is_refused_and_shown_retired(game_wire: Game, played: Player):
    """After the edge, gathering by hand is retired: in Completed, a `retired` unlock, a tap refused."""
    knapped = max(i for i, (_, _, v) in enumerate(played.decisions) if v == TapCard(CardId("knap_edge"))) + 1
    mine = played.replay(knapped)
    mine.advance(mine.save.time + 10)
    v = game_wire.view(mine.save)
    assert "gather_wood" in {x.card for x in v.completed}
    assert any(u.category == "retired" and u.id == "gather_wood" for u in v.unlocked)
    with pytest.raises(InvalidVerbError):
        decide(mine.save, opening_rules(), mine.save.time, game_wire.verb(wire_decision(tap("gather_wood"))))


@pytest.mark.playthrough
def test_the_wire_reproduces_the_opening_to_the_first_mix_decision_by_decision(game_wire: Game, played: Player):
    """The scripted player's decisions up to its first mix, sent as the page sends them (wire decisions, converted as
    the decisions route converts them), end in exactly the save the engine made."""
    switched = next(i for i, (_, _, v) in enumerate(played.decisions) if isinstance(v, SwitchMix)) + 1
    mine = played.replay(switched)
    save = new_save(opening_rules())
    for at, _, verb in played.decisions[:switched]:
        save = decide(save, opening_rules(), at, game_wire.verb(wire_decision(_wire(verb))))
    assert any(isinstance(v, SaveMix) for _, _, v in played.decisions[:switched])
    assert save == mine.save


def _wire(verb: Verb) -> Json:
    if isinstance(verb, SaveMix):
        shares = [c for c in verb.mix.components if isinstance(c, CardShare)]
        assert len(shares) == len(verb.mix.components)
        components = [{"kind": "card_share", "card": c.card, "share_bp": c.share_bp} for c in shares]
        return {"kind": "save_mix", "mix": {"id": verb.mix.id, "components": components}}
    if isinstance(verb, SwitchMix):
        return {"kind": "switch_mix", "mix_id": verb.mix}
    if isinstance(verb, SetOrders):
        orders = [Order(when=condition(o.when), then=order_verb(o.then)).model_dump(mode="json") for o in verb.orders]
        return {"kind": "set_orders", "orders": orders}
    assert isinstance(verb, TapCard)
    return tap(verb.card)


@pytest.mark.playthrough
def test_the_order_card_sets_an_order_that_covers_the_falling_line(game_wire: Game, played: Player):
    """The page's flow: the fire is lit, dry wood falls uncovered, the card's order is sent as set_orders."""
    card = next(o for o in game_wire.content().order_cards if o.store == "dry_wood")
    first_order = next(i for i, (_, _, v) in enumerate(played.decisions) if isinstance(v, SetOrders))
    mine = played.replay(first_order)
    mine.advance(played.decisions[first_order][0])
    before: View = game_wire.view(mine.save)
    line = next(ln for ln in before.ledger if ln.store == "dry_wood")
    assert line.falling and not line.covered and not before.all_covered
    order = {"when": card.when.model_dump(mode="json"), "then": card.then.model_dump(mode="json")}
    verb = game_wire.verb(wire_decision({"kind": "set_orders", "orders": [order]}))
    after = game_wire.view(decide(mine.save, opening_rules(), mine.save.time, verb))
    assert next(ln for ln in after.ledger if ln.store == "dry_wood").covered
    assert len(after.orders) == 1


@pytest.mark.playthrough
def test_a_failed_tap_sends_its_line_to_the_log_and_the_card_shows_what_it_is_short(game_wire: Game,
                                                                                     played: Player):
    """The scripted ring too early: before it, the card lists its stones short; the tap takes no time, the hands stay
    free, and its lines carry the card's failed line at once."""
    ring = next(i for i, (_, _, v) in enumerate(played.decisions) if v == TapCard(CardId("ring_it")))
    mine = played.replay(ring)
    at = played.decisions[ring][0]
    mine.advance(at)
    card = next(x for x in game_wire.view(mine.save).cards if x.card == "ring_it")
    assert card.blocker is not None and [(n.store, n.quantity) for n in card.needs] == [("stones", units(5))]
    assert card.needs[0].segment.start_value < card.needs[0].quantity   # short
    step = decide_logged(mine.save, opening_rules(), at, TapCard(CardId("ring_it")))
    hands = next(b for b in game_wire.view(step.save).lanes if b.lane == "hands")
    assert hands.running_card is None and step.failed == CardId("ring_it")
    assert [(ln.time, ln.key) for ln in step.lines] == [(at, "l_ring_fail")]
