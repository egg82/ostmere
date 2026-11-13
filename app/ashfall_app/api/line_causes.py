"""Content.line_infos: every key a log line can carry, with its kind and what writes it (CONTRACT.txt, "Line causes"),
read from where the content authors the key. A key is written in one place, or by several levels of one skill (a
phase's pool of lines); any other sharing fails the content's load, since its cause would be unknown."""
from collections.abc import Iterable

from ..opening import convert as authored
from ..opening.entries import ConditionEntry
from ..opening.lock import line_keys
from ..opening.refs import fail
from ..opening.schema import Opening
from . import convert
from .decision_models import AtLeast, SkillLevel
from .line_models import AnswerCause, CampCause, LineCause, LineInfo, RunnerCause, SkillCause, WhenCause


def line_infos(o: Opening) -> list[LineInfo]:
    causes = _causes(o)
    return [LineInfo(key=k, kind=o.line_kinds[k], cause=causes.get(k)) for k in dict.fromkeys(line_keys(o))]


def _causes(o: Opening) -> dict[str, LineCause]:
    cards = {c.id for c in o.cards}
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
        put(t.outcome.line_keys, _when(t.when, cards))
    for x in o.offers:
        put(x.line_keys, _when(x.gate, cards))
        put([k for a in x.answers for k in a.outcome.line_keys], AnswerCause(offer=x.id))
    for ch in o.chips:
        put([k for k in (ch.on_line_key, ch.off_line_key) if k is not None], WhenCause(when=convert.condition(authored.condition(ch.when, cards))))
    for i, lv in enumerate(o.camp.levels if o.camp is not None else []):
        put(lv.line_keys, CampCause(level=i + 1))
    return found


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


def _when(c: ConditionEntry, cards: set[str]) -> WhenCause | None:
    """A beat waiting on a lane's rules has no condition the page can read (the lesson on screen is its step)."""
    return None if c.subject_kind == "lane_rules" else WhenCause(when=convert.condition(authored.condition(c, cards)))
