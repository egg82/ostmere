"""A save at a chapter's end written under the rules the next chapter ships after, rebased onto today's and played on
(docs/design/week-two-plan.md, item 13: "a save rebased from each earlier chapter's end loads and plays on"). The save is
the route's own: its save at the end of the saved chapter before (CHECKPOINT) with what the rules without the next
chapter lack dropped, then its decisions after that replayed under those rules to the end of the visit the chapter's
last beat is seen in, each verb applied as it was (a verb that no longer fits fails the replay); the first chapter's
decisions are replayed from the start. Each chapter's end is under the shipped chapters without the ones after it (day
nineteen's without days twenty-two and twenty-three, day twenty-two's without day twenty-three). A replay so costs one
chapter's decisions, however deep the chapter. Where content after the chapter acts before the checkpoint (a rule that
applies from early on), its effects on what the chapter's rules share stay in the save while its own ids go, so the save
is the old build's shape but not, there, a fresh old-build player's numbers. The replay is written once, by
tools/chapter_saves.py, and the tests read it back (from_saved, ends.py). Ids only (CLAUDE.md, "Never spoil the
owner")."""
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
from ashfall_app.rules.expand.convert import build_rules
from ashfall_app.rules.schema import (
    CHAPTERS, DAY_EIGHTEEN, DAY_ELEVEN, DAY_FIFTEEN, DAY_NINE, DAY_NINETEEN, DAY_SIXTEEN, DAY_TWELVE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN,
    DAY_TWENTY_NINE,
    DAY_TWENTY_THREE, DAY_TWENTY_TWO, OPENING,
    load_opening,
)
from tests.daythree.content import rules3
from tests.daytwo.player import DayTwoPlayer
from tests.weekone import verdicts as v1
from tests.weektwo import ends, keys
from tests.weektwo.routes import played
from tests.weektwo.verdicts import (
    EIGHT, EIGHTEEN, ELEVEN, FIFTEEN, NINE, NINETEEN, SIXTEEN, TWELVE, TWENTYFIVE, TWENTYSEVEN, TWENTYTHREE, TWENTYTWO,
)

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
    """The rules through day eight: the shipped chapters without days nine to nineteen, day eight the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_NINE, DAY_ELEVEN, DAY_TWELVE, DAY_FIFTEEN, DAY_SIXTEEN, DAY_EIGHTEEN, DAY_NINETEEN, DAY_TWENTY_TWO, DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


@cache
def rules9() -> Rules:
    """The rules through day nine: the shipped chapters without days eleven to nineteen, day nine the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_ELEVEN, DAY_TWELVE, DAY_FIFTEEN, DAY_SIXTEEN, DAY_EIGHTEEN, DAY_NINETEEN, DAY_TWENTY_TWO, DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


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


def replayed(p: DayTwoPlayer, until: int, rules: Rules, start: Save | None = None) -> Save:
    """`p`'s decisions after `start` (from the start when None) applied at their times under `rules` (as_then), then
    advanced to `until`."""
    s = new_save(rules) if start is None else start
    for at, _, verb in p.decisions:
        if at > until:
            break
        if start is not None and at <= start.time:
            continue
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
    """The rules through day eleven: the shipped chapters without days twelve to nineteen, day eleven the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_TWELVE, DAY_FIFTEEN, DAY_SIXTEEN, DAY_EIGHTEEN, DAY_NINETEEN, DAY_TWENTY_TWO, DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def eleven_end(p: DayTwoPlayer) -> int:
    """The end of the visit B11 is seen in."""
    return v1.exit_save(p, ELEVEN).time


@cache
def rules12() -> Rules:
    """The rules through day twelve: the shipped chapters without days fifteen to nineteen, day twelve the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_FIFTEEN, DAY_SIXTEEN, DAY_EIGHTEEN, DAY_NINETEEN, DAY_TWENTY_TWO, DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def twelve_end(p: DayTwoPlayer) -> int:
    """The end of the visit S4 is seen in."""
    return v1.exit_save(p, TWELVE).time


@cache
def rules15() -> Rules:
    """The rules through day fifteen: the shipped chapters without days sixteen to nineteen, day fifteen the last of
    them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_SIXTEEN, DAY_EIGHTEEN, DAY_NINETEEN, DAY_TWENTY_TWO, DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def fifteen_end(p: DayTwoPlayer) -> int:
    """The end of the visit B14 is seen in."""
    return v1.exit_save(p, FIFTEEN).time


@cache
def rules16() -> Rules:
    """The rules through day sixteen: the shipped chapters without days eighteen and nineteen, day sixteen the last of
    them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_EIGHTEEN, DAY_NINETEEN, DAY_TWENTY_TWO, DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def sixteen_end(p: DayTwoPlayer) -> int:
    """The end of the visit B15 is seen in."""
    return v1.exit_save(p, SIXTEEN).time


@cache
def rules18() -> Rules:
    """The rules through day eighteen: the shipped chapters without days nineteen and twenty-two, day eighteen the last
    of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_NINETEEN, DAY_TWENTY_TWO, DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def eighteen_end(p: DayTwoPlayer) -> int:
    """The end of the visit B16 is seen in."""
    return v1.exit_save(p, EIGHTEEN).time


@cache
def rules19() -> Rules:
    """The rules through day nineteen: the shipped chapters without days twenty-two and twenty-three, day nineteen the
    last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_TWENTY_TWO, DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def nineteen_end(p: DayTwoPlayer) -> int:
    """The end of the visit T13 is seen in."""
    return v1.exit_save(p, NINETEEN).time


@cache
def rules22() -> Rules:
    """The rules through day twenty-two: the shipped chapters without days twenty-three and twenty-five, day twenty-two
    the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def twentytwo_end(p: DayTwoPlayer) -> int:
    """The end of the visit B19 is seen in."""
    return v1.exit_save(p, TWENTYTWO).time


@cache
def rules23() -> Rules:
    """The rules through day twenty-three: the shipped chapters without days twenty-five and twenty-seven, day
    twenty-three the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def twentythree_end(p: DayTwoPlayer) -> int:
    """The end of the visit B20 is seen in."""
    return v1.exit_save(p, TWENTYTHREE).time


@cache
def rules25() -> Rules:
    """The rules through day twenty-five: the shipped chapters without days twenty-seven and twenty-nine, day twenty-five
    the last of them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c not in (DAY_TWENTY_SEVEN, DAY_TWENTY_NINE))))


def twentyfive_end(p: DayTwoPlayer) -> int:
    """The end of the visit B21 is seen in."""
    return v1.exit_save(p, TWENTYFIVE).time


@cache
def rules27() -> Rules:
    """The rules through day twenty-seven: the shipped chapters without day twenty-nine, day twenty-seven the last of
    them."""
    return build_rules(load_opening(OPENING, tuple(c for c in CHAPTERS if c != DAY_TWENTY_NINE)))


def twentyseven_end(p: DayTwoPlayer) -> int:
    """The end of the visit I13 is seen in."""
    return v1.exit_save(p, TWENTYSEVEN).time


ENDS: dict[str, Callable[[DayTwoPlayer], int]] = {"eight": eight_end, "nine": nine_end, "eleven": eleven_end,
                                                  "twelve": twelve_end, "fifteen": fifteen_end, "sixteen": sixteen_end,
                                                  "eighteen": eighteen_end, "nineteen": nineteen_end,
                                                  "twentytwo": twentytwo_end, "twentythree": twentythree_end,
                                                  "twentyfive": twentyfive_end, "twentyseven": twentyseven_end}
OLD: dict[str, Callable[[], Rules]] = {"eight": rules8, "nine": rules9, "eleven": rules11, "twelve": rules12,
                                       "fifteen": rules15, "sixteen": rules16, "eighteen": rules18,
                                       "nineteen": rules19, "twentytwo": rules22, "twentythree": rules23,
                                       "twentyfive": rules25, "twentyseven": rules27}
"""Each saved chapter's end and the rules its save is written under: the shipped chapters without the ones after it."""
_order = [c for c in keys.ORDER if c in OLD]
CHECKPOINT: dict[str, str | None] = dict(zip(_order, [None, *_order]))
"""The saved chapter at whose end each chapter's replay starts: the one before it, None for the first."""


def checkpoint(chapter: str, p: DayTwoPlayer) -> Save | None:
    """`p`'s own save, under its rules, at the end of the chapter's CHECKPOINT (the exit of that visit); None for the
    first chapter."""
    prev = CHECKPOINT[chapter]
    if prev is None:
        return None
    at = ENDS[prev](p)
    found = [v.exit for v in p.visits if v.exit is not None and v.exit.time == at]
    assert len(found) == 1, (chapter, prev, at, len(found))
    return found[0]


def inputs(p: DayTwoPlayer, end: int, start: str | None) -> str:
    """What written() reads besides the old rules, whose digest the written save's envelope carries: the checkpoint's
    save as encoded under `p`'s rules (`start`, None from the start), `p`'s decisions to `end`, and the source of the
    engine (which imports nothing but itself) and of the replay's own functions."""
    code = sha256(ends.engine_digest().encode())
    for fn in (replayed, as_then, known, checkpoint, written):
        code.update(getsource(fn).encode())
    log: list[Json] = [[at, verb_to_json(verb)] for at, _, verb in p.decisions if at <= end]
    begun = None if start is None else sha256(start.encode()).hexdigest()
    return sha256(canonical({"until": end, "decisions": log, "code": code.hexdigest(), "from": begun}).encode()).hexdigest()


def todays_inputs(chapter: str, p: DayTwoPlayer) -> str:
    """inputs() of the chapter's save written from `p` today."""
    at = checkpoint(chapter, p)
    return inputs(p, ENDS[chapter](p), None if at is None else encode(at, p.rules))


def written(chapter: str, p: DayTwoPlayer) -> ends.SavedRebased:
    """`p`'s save at the chapter's end under its old rules, as tools/chapter_saves.py saves it: `p`'s save at the
    checkpoint rebased onto the old rules (what they lack dropped), then `p`'s decisions after it replayed under them."""
    end, old, at = ENDS[chapter](p), OLD[chapter](), checkpoint(chapter, p)
    text = None if at is None else encode(at, p.rules)
    start = None if text is None else rebase(text, old)
    return ends.SavedRebased(inputs(p, end, text), encode(replayed(p, end, old, start), old))


def from_saved(chapter: str) -> Rebased:
    """The chapter's saved save (ends.py), decoded under its old rules, rebased onto today's and played on; where none
    is saved, the save written from typical's play from the start."""
    old = OLD[chapter]()
    if not ends.available(chapter):
        return loaded_on(decode(written(chapter, played(chapter, "typical")).text, old), old)
    try:
        before = decode(ends.rebased_text(chapter).text, old)
    except StateFormatError as e:
        raise AssertionError(f"the saved save at {chapter}'s end is stale ({e}): {ends.REWRITE}") from e
    return loaded_on(before, old)
