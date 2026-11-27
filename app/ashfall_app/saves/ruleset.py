"""The Ruleset a pod plays saves under, from the opening's content, the build's name, and its release number
(`build_release`)."""
import os

from .. import engine as e
from ..rules.expand.convert import camp_trigger_id
from ..rules.line_kinds import line_keys
from ..rules.schema import Opening, to_rules
from .interface import Ruleset
from .journal_rules import journal_rules
from .repeats import RepeatRules


def build_release() -> int:
    """This build's place in deploy order: CI numbers each image build (BUILD_RELEASE), later builds higher. A save
    written by a later release than a pod's own is left to the later pod (saves/builds/load.py `newer`). 0 for a local run."""
    return int(os.environ.get("BUILD_RELEASE", "0"))


def ruleset(opening: Opening, build: str, release: int) -> Ruleset:
    rules = to_rules(opening)
    return Ruleset(rules=rules, digest=e.rules_digest(rules), start_lines=tuple(e.LineKey(k) for k in opening.start_line_keys),
                   line_keys=frozenset(line_keys(opening)), build=build, release=release,
                   camp_triggers=camp_triggers(opening, rules), repeats=repeat_rules(opening),
                   journal=journal_rules(opening))


def repeat_rules(opening: Opening) -> RepeatRules:
    r = opening.repeat_offers
    return RepeatRules(hand_taps=r.hand_taps, hand_taps_within_s=r.hand_taps_within_s, switches=r.switches,
                       switches_within_s=r.switches_within_s)


def camp_triggers(opening: Opening, rules: e.Rules) -> tuple[int, ...]:
    """Where in rules.triggers the triggers that land Camp levels are."""
    levels = len(opening.camp.levels) if opening.camp is not None else 0
    ids = {camp_trigger_id(n) for n in range(1, levels + 1)}
    return tuple(i for i, t in enumerate(rules.triggers) if t.id in ids)

