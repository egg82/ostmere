"""A save at a chapter's end written under the rules the next chapter ships after, rebased onto today's and played on
(docs/design/week-two-plan.md, item 13: "a save rebased from each earlier chapter's end loads and plays on"). The save is
the route's own: its decisions from the start replayed under the rules without the next chapter to the end of the visit
the chapter's last beat is seen in, each verb applied as it was (a verb that no longer fits fails the replay): day
eight's end under the shipped chapters without days nine to fifteen, day nine's without days eleven to fifteen, day
eleven's without days twelve and fifteen, day twelve's without day fifteen. The replay is written once, by tools/chapter_saves.py,
and the tests read it back (from_saved, ends.py). Ids only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from inspect import getsource

from ashfall_app.engine import (
    AnswerOffer, AtLeast, AtMost, Order, Rules, Save, SetOrders, StateFormatError, StoreValue, TapCard, TriggerId, Verb,
    advance, decide, decode, encode, new_save, rebase, verb_to_json,
)
from ashfall_app.engine.codec import Json, canonical
from ashfall_app.opening.convert import build_rules
from ashfall_app.opening.schema import CHAPTERS, DAY_ELEVEN, DAY_FIFTEEN, DAY_NINE, DAY_TWELVE, OPENING, load_opening
from tests.daythree.content import rules3
from tests.daytwo.player import DayTwoPlayer
from tests.weekone import verdicts as v1
from tests.weektwo import ends
from tests.weektwo.routes import played
from tests.weektwo.verdicts import EIGHT, ELEVEN, NINE, TWELVE

PLAYED_ON_S = 24 * 3600


@dataclass(frozen=True)
class Rebased:
    before: Save
    """The save at the chapter's end under the rules without the next chapter."""
    loaded: Save
    """The same save rebased onto today's rules."""
    later: Save
    """The loaded save PLAYED_ON_S later with nobody deciding."""


@cache
def rules8() -> Rules:
    """The rules through day eight: the shipped chapters without days nine to fifteen, day eight the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_NINE, DAY_ELEVEN, DAY_TWELVE, DAY_FIFTEEN))))


@cache
def rules9() -> Rules:
    """The rules through day nine: the shipped chapters without days eleven to fifteen, day nine the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_ELEVEN, DAY_TWELVE, DAY_FIFTEEN))))


def known(order: Order, rules: Rules) -> bool:
    """The order names only stores and cards `rules` has: one a player on those rules could have set."""
    stores, cards = {s.id for s in rules.stores}, {c.id for c in rules.cards}
    when = order.when
    if isinstance(when, (AtLeast, AtMost)) and isinstance(when.subject, StoreValue) and when.subject.store not in stores:
        return False
    return not (isinstance(order.then, TapCard) and order.then.card not in cards)


def as_then(verb: Verb, rules: Rules) -> Verb | None:
    """The verb as a player on `rules` made it: a rule on content `rules` lacks (day nine's chores, shown inside day
    eight's span) was never set, and an offer it lacks (day nine's first ask, the same) never answered: None. Every
    other verb is applied as it was."""
    if isinstance(verb, AnswerOffer) and verb.offer not in {o.id for o in rules.offers}:
        return None
    return SetOrders(tuple(o for o in verb.orders if known(o, rules))) if isinstance(verb, SetOrders) else verb


def replayed(p: DayTwoPlayer, until: int, rules: Rules) -> Save:
    """`p`'s decisions from the start applied at their times under `rules` (as_then), then advanced to `until`."""
    s = new_save(rules)
    for at, _, verb in p.decisions:
        if at > until:
            break
        if (then := as_then(verb, rules)) is not None:
            s = decide(advance(s, rules, at), rules, at, then)
    return advance(s, rules, until)


def loaded_on(before: Save, old: Rules) -> Rebased:
    """`before`, written under `old`, rebased onto today's rules and played on."""
    loaded = rebase(encode(before, old), rules3())
    return Rebased(before, loaded, advance(loaded, rules3(), loaded.time + PLAYED_ON_S))


def fired(save: Save, rules: Rules, trigger: str) -> bool:
    return dict(zip((t.id for t in rules.triggers), save.fired))[TriggerId(trigger)]


def eight_end(p: DayTwoPlayer) -> int:
    """The end of the visit B9 is seen in."""
    return v1.exit_save(p, EIGHT).time


def nine_end(p: DayTwoPlayer) -> int:
    """The end of the visit B10 is seen in."""
    return v1.exit_save(p, NINE).time


@cache
def rules11() -> Rules:
    """The rules through day eleven: the shipped chapters without days twelve and fifteen, day eleven the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_TWELVE, DAY_FIFTEEN))))


def eleven_end(p: DayTwoPlayer) -> int:
    """The end of the visit B11 is seen in."""
    return v1.exit_save(p, ELEVEN).time


@cache
def rules12() -> Rules:
    """The rules through day twelve: the shipped chapters without day fifteen, day twelve the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c != DAY_FIFTEEN)))


def twelve_end(p: DayTwoPlayer) -> int:
    """The end of the visit S4 is seen in."""
    return v1.exit_save(p, TWELVE).time


ENDS: dict[str, Callable[[DayTwoPlayer], int]] = {"eight": eight_end, "nine": nine_end, "eleven": eleven_end,
                                                  "twelve": twelve_end}
OLD: dict[str, Callable[[], Rules]] = {"eight": rules8, "nine": rules9, "eleven": rules11, "twelve": rules12}
"""Each saved chapter's end and the rules its save is written under: the shipped chapters without the ones after it."""


def inputs(p: DayTwoPlayer, end: int) -> str:
    """What replayed(p, end, old) reads besides `old`, whose digest the written save's envelope carries: `p`'s decisions
    to `end`, and the source of the engine (which imports nothing but itself) and of the replay's own functions."""
    code = sha256(ends.engine_digest().encode())
    for fn in (replayed, as_then, known):
        code.update(getsource(fn).encode())
    log: list[Json] = [[at, verb_to_json(verb)] for at, _, verb in p.decisions if at <= end]
    return sha256(canonical({"until": end, "decisions": log, "code": code.hexdigest()}).encode()).hexdigest()


def written(chapter: str, p: DayTwoPlayer) -> ends.SavedRebased:
    """`p`'s save at the chapter's end under its old rules, as tools/chapter_saves.py saves it."""
    end, old = ENDS[chapter](p), OLD[chapter]()
    return ends.SavedRebased(inputs(p, end), encode(replayed(p, end, old), old))


def from_saved(chapter: str) -> Rebased:
    """The chapter's saved save (ends.py), decoded under its old rules, rebased onto today's and played on; where none
    is saved, the save written from typical's play from the start."""
    old = OLD[chapter]()
    if not ends.available():
        return loaded_on(decode(written(chapter, played(chapter, "typical")).text, old), old)
    try:
        before = decode(ends.rebased_text(chapter).text, old)
    except StateFormatError as e:
        raise AssertionError(f"the saved save at {chapter}'s end is stale ({e}): {ends.REWRITE}") from e
    return loaded_on(before, old)
