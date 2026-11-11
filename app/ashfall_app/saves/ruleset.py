"""The Ruleset a pod plays saves under, from the opening's content and renames, the build's name, and the content
release the release lock numbers this content (opening/lock.py; the app's start refuses content the lock does not
hold, so the number is this content's)."""

from .. import engine as e
from ..opening.convert import camp_trigger_id
from ..opening.renames import RenameEntry, engine_renames
from ..opening.schema import Opening, to_rules
from .interface import Ruleset
from .repeats import RepeatRules


def ruleset(opening: Opening, renames: list[RenameEntry], build: str, release: int) -> Ruleset:
    rules = to_rules(opening)
    return Ruleset(rules=rules, digest=e.rules_digest(rules), renames=engine_renames(renames),
                   start_lines=tuple(e.LineKey(k) for k in opening.start_line_keys),
                   line_renames=line_renames(renames), build=build, release=release,
                   camp_triggers=camp_triggers(opening, rules), repeats=repeat_rules(opening))


def repeat_rules(opening: Opening) -> RepeatRules:
    r = opening.repeat_offers
    return RepeatRules(hand_taps=r.hand_taps, hand_taps_within_s=r.hand_taps_within_s, switches=r.switches,
                       switches_within_s=r.switches_within_s)


def camp_triggers(opening: Opening, rules: e.Rules) -> tuple[int, ...]:
    """Where in rules.triggers the triggers that land Camp levels are."""
    levels = len(opening.camp.levels) if opening.camp is not None else 0
    ids = {camp_trigger_id(n) for n in range(1, levels + 1)}
    return tuple(i for i, t in enumerate(rules.triggers) if t.id in ids)


def line_renames(entries: list[RenameEntry]) -> dict[str, str]:
    """Each renamed text key to the key it is now, through every rename after it (a -> b and b -> c map a to c), for
    lines stored before a rename."""
    step = {r.old: r.new for r in entries if r.kind == "line"}
    out: dict[str, str] = {}
    for old in step:
        seen, now = {old}, step[old]
        while now in step and now not in seen:
            seen.add(now)
            now = step[now]
        out[old] = now
    return out
