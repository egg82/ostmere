"""What held at a decision's instant before it applied, kept in the decision log beside the verb (DESIGN.txt,
"Decision context"): the mix the hands ran, whether a tap's card was in it, and the chips shown. The log alone then
says what the player keeps doing under which state, without a replay; a replay of the log reproduces each context
exactly, since each is read off the save the replay reaches at that decision."""

from dataclasses import dataclass

from .codec import Json
from .gates import shown_chips
from .ids import ChipId, MixId
from .lanes import TapCard
from .mixes import flatten_shares
from .plan import running_mix_id
from .rules import Rules
from .state import Save
from .verbs import Verb


@dataclass(frozen=True)
class DecisionContext:
    mix: MixId | None
    """The mix the hands ran (plan.running_mix_id), or None."""
    in_mix: bool
    """The verb is a TapCard of a card that mix holds, nested mixes flattened; False for every other verb."""
    chips: tuple[ChipId, ...]
    """The chips shown, in rules.chips order."""


def decision_context(save: Save, rules: Rules, verb: Verb) -> DecisionContext:
    """The context of `verb` decided on `save`, already advanced to the decision's time. Reads only."""
    mix = running_mix_id(save, rules)
    saved = mix is not None and any(m.id == mix for m in save.mixes)
    in_mix = isinstance(verb, TapCard) and saved and mix is not None and any(
        s.card == verb.card for s in flatten_shares(save.mixes, mix))
    return DecisionContext(mix=mix, in_mix=in_mix, chips=shown_chips(save, rules))


def context_to_json(c: DecisionContext) -> Json:
    return {"mix": c.mix, "in_mix": c.in_mix, "chips": list[Json](c.chips)}


def context_from_json(value: Json) -> DecisionContext | None:
    """The context a log row kept, or None for a row written before contexts were (or one not of this shape)."""
    if not isinstance(value, dict):
        return None
    mix, in_mix, chips = value.get("mix"), value.get("in_mix"), value.get("chips")
    if not (mix is None or isinstance(mix, str)) or not isinstance(in_mix, bool) or not isinstance(chips, list):
        return None
    ids = tuple(ChipId(c) for c in chips if isinstance(c, str))
    return DecisionContext(mix=None if mix is None else MixId(mix), in_mix=in_mix, chips=ids)
