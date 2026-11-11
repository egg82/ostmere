"""Rebase: a save written under other rules, made a save under these, losing nothing it had earned.

Semantics and its seven steps: DESIGN.txt, "Rebase". Pure; a failure (RebaseError, StateFormatError) returns nothing,
so a failed rebase is never written.
"""
import json
from dataclasses import replace

from .api import Step, numbered, recorder
from .codec import ENVELOPE, FORMAT, READ_ERRORS, Json, canonical, decode, rules_digest, save_from_json
from .errors import RebaseError, StateFormatError
from .gates import store_cap
from .handlers import Emit, ignore
from .ids import AnswerId, CardId, IdKind, OfferId, SkillId
from .index import index
from .instant import resolve_instant
from .manifest import Manifest, ManifestOffer, declared, read_manifest
from .rebuild import rebuild
from .renaming import Rename, Renamer, renamed_save
from .rulelog import rule_changes
from .rules import Rules
from .segments import Segment
from .phases import xp_ceiling
from .state import FIRST_PHASE, PhaseState, Save, SkillState, StoreState
from .cards import CardState, LaneState
from .units import BP
from .unlocks import unlock_key
from .upgrade import upgrade


def rebase(text: str, rules: Rules, renames: tuple[Rename, ...] = ()) -> Save:
    """The save `text` holds, under `rules`: decode(text, rules) when it was written under them; otherwise upgraded,
    renamed, reshaped and its instant resolved with evaluation (DESIGN.txt, "Rebase"). RebaseError for an id the
    save's rules declared that these lack and no rename maps; StateFormatError for a text no encode gave."""
    return _rebase(text, rules, renames, ignore)


def rebase_logged(text: str, rules: Rules, renames: tuple[Rename, ...] = ()) -> Step:
    """rebase(), plus the lines its instant emitted (all at the save's time, seq from 0) and its rule changes: each
    order's latch that the instant turned, a rule an outcome installed included (DESIGN.txt, "Rebase" in part
    "TOWNSFOLK, INSTALLED RULES AND OFFERS")."""
    lines, emit = recorder()
    before, after = _rebased(text, rules, renames, emit)
    return Step(after, numbered(lines), rule_changes=rule_changes(before, after, rules))


def _rebase(text: str, rules: Rules, renames: tuple[Rename, ...], emit: Emit) -> Save:
    return _rebased(text, rules, renames, emit)[1]


def _rebased(text: str, rules: Rules, renames: tuple[Rename, ...], emit: Emit) -> tuple[Save, Save]:
    """The save before step 6 (the reshaped save, or the decoded one) and the result."""
    envelope = _read(text)
    if envelope.get("format") == FORMAT and envelope.get("rules") == rules_digest(rules):
        same = decode(text, rules)
        return same, same
    manifest, save = _loose(upgrade(envelope))
    m = Renamer(renames, manifest.standing, (c.id for c in manifest.cards))
    _check_known(m, manifest, rules)
    chips = tuple(m.id(IdKind.CHIP, c) for c in manifest.chips)
    triggers = tuple(m.id(IdKind.TRIGGER, t) for t in manifest.triggers)
    work_s = {CardId(m.id(IdKind.CARD, c.id)): c.work_s for c in manifest.cards}
    shaped = _reshape(renamed_save(save, m), rules, dict(zip(chips, zip(save.chips, save.chips_seen))),
                      dict(zip(triggers, save.fired)), work_s)
    return shaped, resolve_instant(rebuild(shaped, rules), rules, [], True, emit)


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


def _check_known(m: Renamer, manifest: Manifest, rules: Rules) -> None:
    """Step 4: every id the manifest declares is declared by the new rules once renamed; nothing is ever dropped. An
    answer the save's rules put under one offer stays under that offer (renamed), and a kind or role the save's rules
    gave stays (an offer that had none may gain one: DESIGN.txt, "OFFER KINDS")."""
    now = declared(rules)
    for kind, ids in manifest.declared().items():
        for x in ids:
            if m.id(kind, x) not in now[kind]:
                raise RebaseError(kind, x)
    under = {a.id: o.id for o in rules.offers for a in o.answers}
    for o in manifest.offers:
        for a in o.answers:
            if under[AnswerId(m.id(IdKind.ANSWER, a))] != m.id(IdKind.OFFER, o.id):
                raise RebaseError(IdKind.ANSWER, a)
        _check_kind(m, o, rules)


def _check_kind(m: Renamer, o: ManifestOffer, rules: Rules) -> None:
    """The kind the manifest gave offer `o`, and each answer's role, are the new rules' (RebaseError(OFFER) if not)."""
    if o.kind is None:
        return
    now = index(rules).offers[OfferId(m.id(IdKind.OFFER, o.id))]
    roles = {a.id: a.role for a in now.answers}
    if now.kind != o.kind or any(roles[AnswerId(m.id(IdKind.ANSWER, a))] != r for a, r in zip(o.answers, o.roles)):
        raise RebaseError(IdKind.OFFER, o.id)


def _reshape(save: Save, rules: Rules, chips: dict[str, tuple[bool, bool]], fired: dict[str, bool],
             work_s: dict[CardId, int]) -> Save:
    """Step 5: the canonical save under the new rules, at the save's time, every id already renamed."""
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
        pauses=tuple(sorted(save.pauses, key=lambda p: pos[p.runner])),
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
        found.append(ls if ls is not None and (ls.card is None or cards[ls.card].lane == lane) else LaneState(lane))
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
    """A store above its cap under the save's stack (only a lowered cap reaches it, which the release lock forbids)
    held at that cap."""
    return replace(save, stores=tuple(
        replace(st, segment=replace(st.segment, start_value=min(st.segment.start_value, store_cap(save, rules, st.store))))
        for st in save.stores))
