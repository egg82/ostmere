"""Rebase: a save written under other rules, made a save under these, what the new rules lack dropped.

Semantics and its seven steps: DESIGN.txt, "Rebase". Pure; only a text no encode gave fails (StateFormatError), and a
failed rebase is never written.
"""
import json
from dataclasses import replace

from .api import Step, numbered, recorder
from .codec import ENVELOPE, FORMAT, READ_ERRORS, Json, canonical, decode, rules_digest, save_from_json
from .dropping import Gone, dropped_save
from .errors import StateFormatError
from .full import is_full_pause
from .gates import store_cap
from .handlers import Emit, ignore
from .ids import CardId, IdKind, SkillId
from .index import index
from .instant import resolve_instant
from .manifest import Manifest, declared, read_manifest
from .rebuild import rebuild
from .rulelog import rule_changes
from .rules import Rules
from .segments import Segment
from .phases import xp_ceiling
from .state import FIRST_PHASE, PhaseState, Save, SkillState, StoreState
from .cards import CardState, LaneState
from .units import BP
from .unlocks import unlock_key
from .upgrade import upgrade


def rebase(text: str, rules: Rules) -> Save:
    """The save `text` holds, under `rules`: decode(text, rules) when it was written under them; otherwise upgraded,
    what these rules lack dropped, reshaped and its instant resolved with evaluation (DESIGN.txt, "Rebase").
    StateFormatError for a text no encode gave."""
    return _rebased(text, rules, ignore)[1]


def rebase_logged(text: str, rules: Rules) -> Step:
    """rebase(), plus the lines its instant emitted (all at the save's time, seq from 0), its rule changes (each
    order's latch that the instant turned, a rule an outcome installed included: DESIGN.txt, "Rebase" in part
    "TOWNSFOLK, INSTALLED RULES AND OFFERS") and how many ids of each kind it dropped."""
    lines, emit = recorder()
    before, after, gone = _rebased(text, rules, emit)
    return Step(after, numbered(lines), rule_changes=rule_changes(before, after, rules), dropped=gone.counts())


def _rebased(text: str, rules: Rules, emit: Emit) -> tuple[Save, Save, Gone]:
    """The save before step 6 (the reshaped save, or the decoded one), the result, and what was dropped."""
    envelope = _read(text)
    if envelope.get("format") == FORMAT and envelope.get("rules") == rules_digest(rules):
        same = decode(text, rules)
        return same, same, Gone({k: frozenset() for k in IdKind})
    manifest, save = _loose(upgrade(envelope))
    gone = _gone(manifest, rules)
    work_s = {CardId(c.id): c.work_s for c in manifest.cards}
    shaped = _reshape(dropped_save(save, gone, rules), rules, dict(zip(manifest.chips, zip(save.chips, save.chips_seen))),
                      dict(zip(manifest.triggers, save.fired)), work_s)
    return shaped, resolve_instant(rebuild(shaped, rules), rules, [], True, emit), gone


def _read(text: str) -> dict[str, Json]:
    """The envelope as JSON, if the text is its one canonical form."""
    try:
        envelope: Json = json.loads(text)
    except READ_ERRORS as e:
        raise StateFormatError(f"unreadable save: {type(e).__name__}") from e
    if not isinstance(envelope, dict) or canonical(envelope) != text:
        raise StateFormatError("not a canonical save envelope")
    return envelope


def _loose(envelope: dict[str, Json]) -> tuple[Manifest, Save]:
    """Step 2: the manifest and the save, with no digest check."""
    if frozenset(envelope) != ENVELOPE or not isinstance(envelope["rules"], str):
        raise StateFormatError("not a save envelope")
    manifest = read_manifest(envelope["manifest"])
    try:
        save = save_from_json(envelope["save"])
    except READ_ERRORS as e:
        raise StateFormatError(f"unreadable save: {type(e).__name__}") from e
    if len(save.chips) != len(manifest.chips) or len(save.chips_seen) != len(manifest.chips) \
            or len(save.fired) != len(manifest.triggers):
        raise StateFormatError("the save's chips or triggers do not match its manifest")
    return manifest, save


def _gone(manifest: Manifest, rules: Rules) -> Gone:
    """Step 3's ids: each the manifest declares and the rules do not, and each answer the rules put under another offer
    than the manifest did."""
    now = declared(rules)
    ids = {kind: frozenset(x for x in xs if x not in now[kind]) for kind, xs in manifest.declared().items()}
    under: dict[str, str] = {a.id: o.id for o in rules.offers for a in o.answers}
    moved = frozenset(a for o in manifest.offers for a in o.answers if under.get(a, o.id) != o.id)
    return Gone({**ids, IdKind.ANSWER: ids[IdKind.ANSWER] | moved})


def _reshape(save: Save, rules: Rules, chips: dict[str, tuple[bool, bool]], fired: dict[str, bool],
             work_s: dict[CardId, int]) -> Save:
    """Step 5: the canonical save under the new rules, at the save's time, what they lack already dropped."""
    t = save.time
    stores = {st.store: st.segment.start_value for st in save.stores}
    xp = {st.skill: st.xp.start_value for st in save.skills}
    phases = {st.skill: st.phase for st in save.skills}
    pos = index(rules).runner_pos
    save = replace(
        save,
        stores=tuple(StoreState(d.id, Segment(t, stores.get(d.id, d.initial), 0)) for d in rules.stores),
        skills=tuple(_skill(t, rules, d.id, xp.get(d.id, 0), phases.get(d.id, FIRST_PHASE)) for d in rules.skills),
        chips=tuple(chips.get(c.id, (False, False))[0] for c in rules.chips),
        chips_seen=tuple(chips.get(c.id, (False, False))[1] for c in rules.chips),
        fired=tuple(fired.get(x.id, False) for x in rules.triggers),
        lanes=_lanes(save, rules), cards=_cards(save, rules, work_s),
        pauses=tuple(sorted((p for p in save.pauses if not is_full_pause(rules, p)), key=lambda p: pos[p.runner])),
        unlocked=tuple(sorted(set(save.unlocked), key=unlock_key)))
    return _clamped(save, rules)


def _skill(t: int, rules: Rules, skill: SkillId, xp: int, phase: PhaseState) -> SkillState:
    """A skill's state at t: its phase kept, its XP held at or under its phase's ceiling (phases.xp_ceiling)."""
    return SkillState(skill, Segment(t, min(xp, xp_ceiling(rules.curve, rules.prestige, phase.phase)), 0), phase)


def _lanes(save: Save, rules: Rules) -> tuple[LaneState, ...]:
    """HANDS then rules.lanes; a new lane free, and one whose card now runs on another lane freed (an interrupt)."""
    old = {ls.lane: ls for ls in save.lanes}
    cards = index(rules).cards
    found: list[LaneState] = []
    for lane in index(rules).lanes:
        ls = old.get(lane)
        if ls is None:
            ls = LaneState(lane)
        found.append(ls if ls.card is None or cards[ls.card].lane == lane else replace(ls, card=None, speed=None))
    return tuple(found)


def _cards(save: Save, rules: Rules, work_s: dict[CardId, int]) -> tuple[CardState, ...]:
    """Each card's state in rules order; a changed work_s W -> W' keeps completions and scales the bar."""
    old = {cs.card: cs for cs in save.cards}
    found: list[CardState] = []
    for c in rules.cards:
        cs = old.get(c.id)
        if cs is None:
            continue
        w, was = cs.work.start_value, work_s.get(c.id, c.work_s)
        if was != c.work_s:
            done, rem = divmod(w, was * BP)
            w = done * c.work_s * BP + rem * c.work_s // was
        found.append(CardState(c.id, Segment(save.time, w, 0), cs.raised))
    return tuple(found)


def _clamped(save: Save, rules: Rules) -> Save:
    """A store above its cap under the save's stack (only a lowered cap reaches it)
    held at that cap."""
    return replace(save, stores=tuple(
        replace(st, segment=replace(st.segment, start_value=min(st.segment.start_value, store_cap(save, rules, st.store))))
        for st in save.stores))
