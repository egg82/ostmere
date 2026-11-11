"""The codec for day two (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Codec"; invariant 65).
FORMAT is 7; the manifest gains `offers`, [{"id", "answers"}] in rules order; UPGRADES[6] adds "offers": [] to a format
6 manifest and changes nothing else; AnswerOffer round-trips in saves' orders and queue and in the decision log; the
rules digest covers a lane's `ruled` and the offers."""
import json
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    FORMAT, UPGRADES, AnswerOffer, Order, Outcome, QueueEntry, Rules, Save, SetOrders, SetQueue, StateFormatError,
    Unlock, UnlockKind, advance, decode, encode, rebase, rules_digest, verb_from_json, verb_to_json,
)
from town_world import ASK, LATER, NEVER, NO, OTHER, SECOND, T1, YES, always, answer, started, town, unruled

type Json = None | bool | int | str | list[Json] | dict[str, Json]


def as_obj(v: Json) -> dict[str, Json]:
    assert isinstance(v, dict), f"not a JSON object: {v!r}"
    return v


def envelope(text: str) -> dict[str, Json]:
    loaded: Json = json.loads(text)
    return as_obj(loaded)


def canonical(value: Json) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def answered_world() -> tuple[Rules, Save]:
    """ask answered (yes) at 60; other never shown, so its answer order and queued answer wait in the save."""
    r = town(offers=(SECOND,))
    plan = (Order(NEVER, AnswerOffer(OTHER, LATER)), always(T1))
    s = started(r, SetOrders(plan), SetQueue((QueueEntry(AnswerOffer(OTHER, LATER), NEVER),)))
    return r, answer(advance(s, r, 60), r, 60, YES)


def format_7(text: str) -> str:
    """A format 8 text whose taps keep no speed, as format 7 wrote it: format 7 and no lane `speed`."""
    env = envelope(text)
    save = as_obj(env["save"])
    lanes = save["lanes"]
    assert isinstance(lanes, list)
    bare: list[Json] = [{k: v for k, v in as_obj(ls).items() if k != "speed"} for ls in lanes]
    assert all(as_obj(ls)["speed"] is None for ls in lanes)
    kept: dict[str, Json] = {**save, "lanes": bare}
    return canonical({**env, "format": 7, "save": kept})


def format_6(text: str) -> str:
    """A format 8 text of rules with no offers, as format 6 wrote it: format 7's (format_7) with format 6 and no
    manifest `offers` (DESIGN.txt: a format 6 save predates offers)."""
    env = envelope(format_7(text))
    manifest = as_obj(env["manifest"])
    assert manifest["offers"] == []
    return canonical({**env, "format": 6, "manifest": {k: v for k, v in manifest.items() if k != "offers"}})


def no_offers() -> Rules:
    """The town world before day two's offers: no offer, no showing trigger, nothing ruled."""
    return unruled(replace(town(show_at=None, yes=Outcome(), no=Outcome()), offers=()))


def test_format_is_9_with_upgrades_from_6_7_and_8():
    assert FORMAT == 9 and 6 in UPGRADES and 7 in UPGRADES and 8 in UPGRADES


def test_a_save_holding_answers_round_trips():
    """Codec: AnswerOffer in orders and queue, and the three new unlock kinds, decode to the save encoded."""
    r, s = answered_world()
    assert {u.kind for u in s.unlocked} >= {UnlockKind.ANSWERED, UnlockKind.ANSWER}
    assert any(isinstance(e.verb, AnswerOffer) for e in s.queue) and any(isinstance(o.then, AnswerOffer) for o in s.orders)
    assert decode(encode(s, r), r) == s


def test_answer_offer_round_trips_in_the_decision_log():
    """AnswerOffer joins the decision log's verbs (verb_to_json, verb_from_json)."""
    v = AnswerOffer(ASK, NO)
    assert verb_from_json(verb_to_json(v)) == v


def test_the_manifest_lists_the_offers_and_their_answers_in_rules_order():
    """The manifest gains `offers`: [{"id": offer id, "answers": [answer ids]}] in rules order."""
    r, s = answered_world()
    offers = as_obj(envelope(encode(s, r))["manifest"])["offers"]
    assert offers == [{"id": "ask", "answers": ["yes", "no"]}, {"id": "other", "answers": ["later", "sooner"]}]


def test_the_rules_digest_covers_ruled_and_the_offers():
    """RuleInstall, OfferDef and AnswerDef join the rules digest, and a lane's `ruled` is part of the rules."""
    r = town()
    assert rules_digest(unruled(r)) != rules_digest(r)
    assert rules_digest(town(yes=Outcome())) != rules_digest(r)
    assert rules_digest(town(offers=(SECOND,))) != rules_digest(r)


def test_upgrade_6_adds_empty_offers_and_changes_nothing_else():
    """UPGRADES[6] adds "offers": [] to a format 6 manifest and changes nothing else (the format number aside)."""
    r = no_offers()
    s = advance(started(r, SetOrders((always(T1),))), r, 500)
    text = encode(s, r)
    assert UPGRADES[6](envelope(format_6(text))) == envelope(format_7(text))


def test_a_format_6_text_does_not_decode_and_rebases_as_its_format_7_twin():
    """Invariant 65: rebase of a format 6 text gives what rebasing it with "offers": [] under format 7 gives, under the
    same rules and under day two's (which show the offer at 50, so it shows at the rebase instant); the result holds
    nothing new but what that instant lands. decode refuses the format 6 text (another format)."""
    r = no_offers()
    s = advance(started(r, SetOrders((always(T1),))), r, 500)
    text = encode(s, r)
    old = format_6(text)
    with pytest.raises(StateFormatError):
        decode(old, r)
    assert rebase(old, r) == rebase(text, r) == s
    day_two = town()
    s2 = rebase(old, day_two)
    assert s2 == rebase(text, day_two)
    assert set(s2.unlocked) - set(s.unlocked) <= {Unlock(UnlockKind.OFFER, ASK)}
    assert s2.orders == s.orders and s2.queue == s.queue
