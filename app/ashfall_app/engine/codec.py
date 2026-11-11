"""The save as text: canonical, so it round-trips exactly and equal saves encode to equal strings.

The server stores this string as the save (saves.state). Semantics: DESIGN.txt, "Codec".
stdlib json, sorted keys, no whitespace, a format number and the rules digest inside, and no checksum: the page never
edits the text, an unkeyed hash stops no deliberate edit, and transport already checks bytes. Tamper resistance, if a
page-held save ever needs it, is a keyed MAC the server adds outside the engine (the key is configuration).
"""
import json
from collections.abc import Callable, Iterable
from dataclasses import fields, is_dataclass
from enum import Enum
from hashlib import sha256
from typing import cast

from .answers import AnswerKind, AnswerOffer
from .events import CascadeLimit
from .errors import StateFormatError
from .index import derived
from .cards import Amount, CapRaise, CardState, HeldSpeed, Join, LaneState, Leave, Outcome, RuleInstall, WhileRunning
from .lanes import TapCard
from .mixes import CardShare, Mix, MixLayer, SubMix, SwitchMix
from .offers import AnswerDef, OfferDef
from .modifiers import (
    FlowKind, LaneSpeed, Modifier, ModifierKind, RateRef, SideStrength, StoreCap, ThreatStrength, WorkRef,
)
from .orders import (
    AfterTime, AtLeast, AtMost, CardCount, Order, QueueEntry, Running, SkillLevel, StoreValue, Unlocked,
)
from .rules import Rules
from .rules_check import features
from .segments import Segment
from .prestigeverbs import MovePick, Prestige, UndoPick
from .state import FIRST_PHASE, ParkedRank, Pause, PhaseState, Save, SkillState, StoreState
from .unlocks import Unlock, UnlockKind
from .verbs import DeleteMix, SaveMix, SetOrders, SetQueue, Verb

FORMAT = 9
"""Bumped whenever the encoding changes, with an UPGRADES entry from the old one (upgrade.py); decode raises
StateFormatError for a string of another format, and rebase upgrades one from OLDEST_FORMAT on."""


type Json = None | bool | int | str | list[Json] | dict[str, Json]

_CLASSES: dict[str, Callable[..., object]] = {c.__name__: c for c in (
    Save, StoreState, SkillState, PhaseState, ParkedRank, Segment, Mix, CardShare, SubMix, SwitchMix, TapCard, Pause, Order,
    QueueEntry, AtLeast, AtMost, AfterTime, StoreValue, SkillLevel, CardCount, Unlocked, Running, Modifier,
    RateRef, WorkRef, LaneSpeed, StoreCap, SideStrength, ThreatStrength, Unlock, LaneState, CardState, CascadeLimit, AnswerOffer, AnswerKind,
)}
_OUTCOMES = _CLASSES | {c.__name__: c for c in (
    Outcome, Amount, CapRaise, RuleInstall, Join, Leave, OfferDef, AnswerDef, WhileRunning, HeldSpeed)}
"""Saves never hold an outcome; the release lock keeps released ones (from_json)."""
_VERBS = _CLASSES | {c.__name__: c for c in (SaveMix, DeleteMix, SetOrders, SetQueue, Prestige, UndoPick, MovePick)}
_VERB_TYPES = (
    SwitchMix, SaveMix, DeleteMix, SetOrders, SetQueue, TapCard, AnswerOffer, AnswerKind, Prestige, UndoPick, MovePick)
_ENUMS: dict[str, type[Enum]] = {c.__name__: c for c in (ModifierKind, FlowKind, UnlockKind, MixLayer)}


def rules_digest(rules: Rules) -> str:
    """A hex sha256 of the rules' canonical encoding: two rules objects that compare equal share a digest."""
    return derived(rules, "_digest", lambda r: _digest(_enc_rules(r)))


def _enc_rules(rules: Rules) -> Json:
    """_enc(rules), leaving out sides, threats and nodes while empty, prestige while None, a runner's `fight` while None and a card's `glows` while
    False and `while_running` and `drains` while empty, so rules that declare none keep the digest they had before those existed and the saves under them decode
    without a rebase."""
    out = _enc(rules)
    assert isinstance(out, dict)
    for name in ("sides", "threats", "nodes", "prestige"):
        if not out[name]:
            del out[name]
    for name in ("cards", "standing"):
        runners = out[name]
        assert isinstance(runners, list)
        for runner in runners:
            assert isinstance(runner, dict)
            if runner["fight"] is None:
                del runner["fight"]
            if runner.get("glows") is False:
                del runner["glows"]
            if runner.get("while_running") == []:
                del runner["while_running"]
            if runner.get("drains") == []:
                del runner["drains"]
    return out


def manifest(rules: Rules) -> Json:
    """The slice of the rules a later rebase needs (DESIGN.txt, "Manifest"), as plain JSON."""
    return derived(rules, "_manifest", _manifest)


def encode(save: Save, rules: Rules) -> str:
    """The save as canonical text, carrying FORMAT, rules_digest(rules) and manifest(rules). encode(s1) == encode(s2)
    iff s1 == s2."""
    return canonical({"format": FORMAT, "rules": rules_digest(rules), "manifest": manifest(rules), "save": _enc(save)})


def decode(text: str, rules: Rules) -> Save:
    """The save encode() produced: decode(encode(s, r), r) == s. Accepts exactly the texts encode gives for some Save
    under these rules (it re-encodes the result and compares) and raises StateFormatError for any other: truncated,
    reformatted or reordered, another FORMAT, other rules, an unknown class or field. An edit that is itself the
    encoding of some Save decodes; the engine's behaviour on a save it did not produce is unspecified."""
    try:
        envelope: Json = json.loads(text)
        if not isinstance(envelope, dict) or frozenset(envelope) != ENVELOPE:
            raise StateFormatError("not a save envelope")
        if envelope["format"] != FORMAT or envelope["rules"] != rules_digest(rules):
            raise StateFormatError("another format or other rules")
        save = _dec(envelope["save"])
        if not isinstance(save, Save) or encode(save, rules) != text:
            raise StateFormatError("not the encoding of a save")
        return save
    except StateFormatError:
        raise
    except READ_ERRORS as e:
        raise StateFormatError(f"unreadable save: {type(e).__name__}") from e


ENVELOPE = frozenset({"format", "rules", "manifest", "save"})
READ_ERRORS = (ValueError, KeyError, TypeError, AttributeError, RecursionError)
"""What reading a malformed text raises on the way; each becomes StateFormatError."""


def save_from_json(value: Json) -> Save:
    """The Save an envelope's "save" holds; StateFormatError unless it re-encodes to exactly that JSON."""
    save = _dec(value)
    if not isinstance(save, Save) or _enc(save) != value:
        raise StateFormatError("not the encoding of a save")
    return save


def to_json(value: object) -> Json:
    """An engine value (a dataclass, enum, tuple or scalar) as the codec writes it."""
    return _enc(value)


def from_json(value: Json) -> object:
    """The engine value to_json wrote (a save's parts or an Outcome); KeyError or TypeError for anything else."""
    return _dec(value, _OUTCOMES)


def verb_to_json(verb: Verb) -> Json:
    """A player's verb as the decision log keeps it (Command): the codec's form, read back by verb_from_json."""
    return _enc(verb)


def verb_from_json(value: Json) -> Verb:
    """The verb verb_to_json wrote, or one logged before FORMAT 9 (a SaveMix whose mix carries an empty "holds");
    StateFormatError for anything else."""
    value = _without_holds(value)
    try:
        verb = _dec(value, _VERBS)
    except (KeyError, TypeError) as ex:
        raise StateFormatError("not the encoding of a verb") from ex
    if not isinstance(verb, _VERB_TYPES) or _enc(verb) != value:
        raise StateFormatError("not the encoding of a verb")
    return verb


def _without_holds(value: Json) -> Json:
    """A SaveMix logged before FORMAT 9 as it is logged now: its mix's empty "holds" dropped (DESIGN.txt, "Codec")."""
    if isinstance(value, dict) and value.get("@") == "SaveMix" and isinstance(mix := value.get("mix"), dict) \
            and mix.get("holds") == []:
        return {**value, "mix": {k: v for k, v in mix.items() if k != "holds"}}
    return value


def canonical(value: Json) -> str:
    """Sorted keys, no whitespace: the one text of a JSON value."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _digest(value: Json) -> str:
    return sha256(canonical(value).encode()).hexdigest()


def _manifest(rules: Rules) -> Json:
    def ids(found: Iterable[str]) -> Json:
        return [str(x) for x in found]
    stores: list[Json] = [{"id": str(s.id), "cap": s.cap} for s in rules.stores]
    cards: list[Json] = [{"id": str(c.id), "work_s": c.work_s, "lane": str(c.lane), "cap": c.cap} for c in rules.cards]
    return {
        "stores": stores, "skills": ids(s.id for s in rules.skills), "standing": ids(a.id for a in rules.standing),
        "lanes": ids(d.id for d in rules.lanes), "cards": cards, "chips": ids(c.id for c in rules.chips),
        "triggers": ids(t.id for t in rules.triggers), "features": ids(sorted(features(rules))),
        "offers": [_manifest_offer(o) for o in rules.offers],
    }


def _manifest_offer(o: OfferDef) -> Json:
    """An offer's ids; a kinded one adds its kind and its answers' roles in answer order (an unkinded one is written as
    it was before kinds, so rules that use none keep their manifest text: DESIGN.txt, "OFFER KINDS")."""
    found: dict[str, Json] = {"id": str(o.id), "answers": [str(a.id) for a in o.answers]}
    if o.kind is not None:
        found |= {"kind": str(o.kind), "roles": [str(a.role) for a in o.answers]}
    return found


_OMITTED_WHEN_EMPTY = frozenset({("Outcome", "joins"), ("Outcome", "retire_orders"), ("Outcome", "leaves"),
                                 ("OfferDef", "kind"), ("AnswerDef", "role"), ("PhaseState", "parked")})
"""Fields left out of the encoding while empty, so rules that use none keep the digest they had before the field
existed; decoding supplies the empty default."""


_OMITTED_AT_DEFAULT: dict[tuple[str, str], object] = {
    ("Mix", "layer"): MixLayer.HANDS, ("SkillState", "phase"): FIRST_PHASE}
"""Fields left out of the encoding while at their default, so a save or a logged verb written before the field existed
keeps its text and decodes with it."""


def _enc(v: object) -> Json:
    """Dataclasses become objects tagged "@" with their class name, enums {"@", "v"}, tuples arrays."""
    if v is None or isinstance(v, (bool, int, str)):
        return v
    if isinstance(v, Enum):
        return {"@": type(v).__name__, "v": _enc(v.value)}
    if isinstance(v, tuple):
        return [_enc(x) for x in cast(tuple[object, ...], v)]  # cast -- isinstance leaves tuple[Unknown, ...]
    if is_dataclass(v) and not isinstance(v, type):
        return {"@": type(v).__name__, **{f.name: _enc(getattr(v, f.name)) for f in fields(v)
                                          if _written(v, f.name)}}
    raise TypeError(f"cannot encode {type(v).__name__}")


def _written(v: object, name: str) -> bool:
    key, value = (type(v).__name__, name), getattr(v, name)
    return (key not in _OMITTED_WHEN_EMPTY or bool(value)) and value != _OMITTED_AT_DEFAULT.get(key, object())


def _dec(v: Json, classes: dict[str, Callable[..., object]] = _CLASSES) -> object:
    if isinstance(v, list):
        return tuple(_dec(x, classes) for x in v)
    if not isinstance(v, dict):
        return v
    name = v["@"]
    if not isinstance(name, str):
        raise TypeError("a tag must be a name")
    if name in _ENUMS:
        return _ENUMS[name](v["v"])
    return classes[name](**{k: _dec(x, classes) for k, x in v.items() if k != "@"})
