"""Content.line_infos: every key a log line can carry, with its kind and what writes it (CONTRACT.txt, "Line causes"),
read from where the content authors the key. A key is written in one place, or by several levels of one skill (a
phase's pool of lines); any other sharing fails the content's load, since its cause would be unknown."""
from collections.abc import Iterable

from ..opening import convert as authored
from ..opening.entries import ConditionEntry
from ..opening.line_kinds import line_keys
from ..opening.face_checks import shown_stores, timed_stores
from ..opening.offer_entries import OfferEntry
from ..opening.people import mention_keys, person_keys
from ..opening.refs import fail
from ..opening.schema import Opening
from . import convert
from .decision_models import AtLeast, SkillLevel
from .line_models import AnswerCause, CampCause, LineCause, LineInfo, Mention, RunnerCause, SkillCause, WhenCause


def line_infos(o: Opening) -> list[LineInfo]:
    causes, people, mentions = _causes(o), person_keys(o), mention_keys(o)
    return [LineInfo(key=k, kind=o.line_kinds[k], cause=causes.get(k), person=k in people,
                     mention=None if k not in mentions else Mention(way=mentions[k][0], lane=mentions[k][1]))
            for k in dict.fromkeys(line_keys(o))]


def _causes(o: Opening) -> dict[str, LineCause]:
    cards, worded = {c.id for c in o.cards}, worded_stores(o)
    found: dict[str, LineCause] = {}

    def put(keys: Iterable[str], cause: LineCause | None) -> None:
        for key in keys:
            got = cause if key not in found else _shared(found[key], cause)
            if key in found and got is None:
                fail(f"line {key}", "is written in two places, so what caused it is unknown")
            if got is not None:
                found[key] = got

    for c in o.cards:
        put([*c.line_keys, *c.outcome.line_keys, *c.finished.line_keys], RunnerCause(runner=c.id))
    for runner, fight in [*((c.id, c.fight) for c in o.cards), *((a.id, a.fight) for a in o.standing)]:
        if fight is not None:
            put([*fight.won_line_keys, *fight.lost_line_keys], RunnerCause(runner=runner))
    for t in o.triggers:
        put(t.outcome.line_keys, _when(t.when, cards, worded))
    for x in o.offers:
        put(x.line_keys, offer_cause(x, cards, worded))
        put([k for a in x.answers for k in a.outcome.line_keys], AnswerCause(offer=x.id))
    for ch in o.chips:
        put([*([] if ch.on_line_key is None else [ch.on_line_key]), *ch.off_line_keys], _when(ch.when, cards, worded))
    for i, lv in enumerate(o.camp.levels if o.camp is not None else []):
        put(lv.line_keys, CampCause(level=i + 1))
    return found


def worded_stores(o: Opening) -> frozenset[str]:
    """The stores a cause may name: one whose amount the page draws, or a clock that reads as a time of day."""
    return shown_stores(o) | timed_stores(o)


def offer_cause(x: OfferEntry, cards: set[str], worded: frozenset[str]) -> LineCause | None:
    """What led to an offer: its gate, unless the page cannot word it (worded_stores, _when); then none. An earlier
    answer it requires only sequences it, and reads as unrelated beside it."""
    return _when(x.gate, cards, worded)


def _shared(a: LineCause, b: LineCause | None) -> SkillCause | None:
    """Two places writing one key: a level of one skill when both are that skill's levels, else unknown (None)."""
    skill = _skill(a)
    return SkillCause(skill=skill) if skill is not None and skill == _skill(b) else None


def _skill(c: LineCause | None) -> str | None:
    if isinstance(c, SkillCause):
        return c.skill
    if isinstance(c, WhenCause) and isinstance(c.when, AtLeast) and isinstance(c.when.watched, SkillLevel):
        return c.when.watched.skill
    return None


def _when(c: ConditionEntry, cards: set[str], worded: frozenset[str]) -> WhenCause | None:
    """None where the page has nothing honest to word: a lane's rules (the lesson on screen is its step), or a store
    whose amount the player is never shown and that reads as no time of day."""
    if c.subject_kind == "lane_rules" or (c.subject_kind == "store" and c.id not in worded):
        return None
    return WhenCause(when=convert.condition(authored.condition(c, cards)))
