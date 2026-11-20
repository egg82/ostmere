"""The release lock's data: what content has released, read from `released/ids.json` and taken from the content now.

`released/ids.json` is generated (tools/content_lock.py --write) and alone in its directory. It holds every id ever
released by kind, each store's and card's cap, each lane's `ruled` and each card's lane, the curve, each trigger's outcome (ids taken through every rename, so a
mapped rename never reads as a changed outcome) and every rename applied, and the content release: a number raised
by one each time --write records content whose rules digest differs from the last one recorded, so builds of one
content share a release and a later content always has a higher one (the saves' multi-pod rule orders by it). The
checks: lock_checks.py. Semantics: engine DESIGN.txt, "Release lock".
"""
import json
from collections.abc import Iterable
from dataclasses import replace
from pathlib import Path
from typing import cast

from pydantic import BaseModel, ConfigDict, JsonValue

from ..engine import LineKey, Outcome, Rename, Rules, rules_digest
from ..engine.codec import Json, to_json
from ..engine.renaming import Renamer, renamed_outcome
from .line_kinds import line_keys
from .renames import LOCAL_KINDS, LockKind, RenameEntry, engine_renames
from .schema import Opening

LOCK = Path(__file__).resolve().parent / "released" / "ids.json"
KINDS: tuple[LockKind, ...] = (
    "store", "skill", "standing", "card", "lane", "chip", "trigger", "feature", "line", "offer", "answer",
    "entry", "note", "node", "subject", "slot_key")


class Lock(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ids: dict[str, list[str]]
    """Kind (KINDS) to every id of it ever released, sorted."""
    store_caps: dict[str, int]
    card_caps: dict[str, int | None]
    curve: list[int]
    outcomes: dict[str, JsonValue]
    """Trigger id to its outcome as the engine codec writes it, ids forwarded through the renames."""
    renames: list[dict[str, str | None]]
    """Every rename applied, as {kind, from, to}, in file order; `to` is None for a retired id."""
    release: int = 0
    """The content release this lock records; 0 before the first."""
    digest: str = ""
    """The rules digest of that release's content."""
    lane_ruled: dict[str, bool] = {}
    """Each declared lane's LaneDef.ruled."""
    lane_pooled: list[str] = []
    """Every released pooled lane, sorted."""
    card_lanes: dict[str, str] = {}
    """Each card's lane ("hands" included)."""
    card_xp: dict[str, bool] = {}
    """Whether each card has an XP line (a skill or xp_per_hour)."""
    answer_outcomes: dict[str, JsonValue] = {}
    """Answer id to its outcome, kept as a trigger's is."""
    answer_offers: dict[str, str] = {}
    """Answer id to the offer it answers."""
    offer_kinds: dict[str, str] = {}
    """Offer id to its kind, kinded offers only."""
    answer_roles: dict[str, str] = {}
    """Answer id to its role, answers with a role only."""


def load_lock(path: Path = LOCK) -> Lock:
    return Lock.model_validate_json(path.read_text())


def lock_text(lock: Lock) -> str:
    return json.dumps(lock.model_dump(mode="json"), indent=1, sort_keys=True) + "\n"


def snapshot(o: Opening, rules: Rules, renames: list[RenameEntry]) -> Lock:
    """What the content releases now, alone (no history): the lock --reset writes."""
    fwd = forwarding(renames)
    return Lock(
        ids={k: sorted(set(v)) for k, v in content_ids(o, rules).items()},
        store_caps={s.id: s.cap for s in rules.stores},
        card_caps={c.id: c.cap for c in rules.cards},
        curve=list(rules.curve.thresholds),
        outcomes={str(t.id): _json_value(forwarded(t.outcome, fwd)) for t in rules.triggers},
        renames=[_rename_json(r) for r in renames],
        release=1,
        digest=rules_digest(rules),
        lane_ruled={d.id: d.ruled for d in rules.lanes},
        lane_pooled=sorted(d.id for d in rules.lanes if d.pooled),
        card_lanes={c.id: c.lane for c in rules.cards},
        card_xp={c.id: c.skill is not None or c.xp_per_hour > 0 for c in rules.cards},
        answer_outcomes={str(a.id): _json_value(forwarded(a.outcome, fwd)) for x in rules.offers for a in x.answers},
        answer_offers={str(a.id): str(x.id) for x in rules.offers for a in x.answers},
        offer_kinds={str(x.id): str(x.kind) for x in rules.offers if x.kind is not None},
        answer_roles={str(a.id): str(a.role) for x in rules.offers for a in x.answers if a.role is not None},
    )


def merged(lock: Lock, now: Lock) -> Lock:
    """The lock --write writes: every id ever released kept, the content's caps, curve and outcomes over the old
    ones (the checks have passed, so each only rose or stayed), the content's renames, and the release raised by one
    when the content's rules are not the last recorded."""
    return Lock(
        ids={k: sorted(set(lock.ids.get(k, [])) | set(now.ids.get(k, []))) for k in KINDS},
        store_caps={**lock.store_caps, **now.store_caps},
        card_caps={**lock.card_caps, **now.card_caps},
        curve=now.curve,
        outcomes={**lock.outcomes, **now.outcomes},
        renames=now.renames,
        release=lock.release + (now.digest != lock.digest),
        digest=now.digest,
        lane_ruled={**lock.lane_ruled, **now.lane_ruled},
        lane_pooled=sorted(set(lock.lane_pooled) | set(now.lane_pooled)),
        card_lanes={**lock.card_lanes, **now.card_lanes},
        card_xp={**lock.card_xp, **now.card_xp},
        answer_outcomes={**lock.answer_outcomes, **now.answer_outcomes},
        answer_offers={**lock.answer_offers, **now.answer_offers},
        offer_kinds={**lock.offer_kinds, **now.offer_kinds},
        answer_roles={**lock.answer_roles, **now.answer_roles},
    )


def content_ids(o: Opening, rules: Rules) -> dict[str, list[str]]:
    """Every id the content declares now, by lock kind."""
    return {
        "store": [s.id for s in rules.stores], "skill": [s.id for s in rules.skills],
        "standing": [a.id for a in rules.standing], "card": [c.id for c in rules.cards],
        "lane": [d.id for d in rules.lanes], "chip": [c.id for c in rules.chips],
        "trigger": [t.id for t in rules.triggers], "feature": [f.id for f in o.features], "line": line_keys(o),
        "offer": [x.id for x in rules.offers], "answer": [a.id for x in rules.offers for a in x.answers],
        "entry": [e.id for e in o.entries], "note": [n.id for n in o.notes], "node": [n.id for n in rules.nodes],
        "subject": [s.id for s in o.subjects], "slot_key": slot_keys(o),
    }


def slot_keys(o: Opening) -> list[str]:
    """Every text key a subject's slots, or a crowd's mention bands, can write into a day."""
    slots = [slot for s in o.subjects for slot in (s.first, s.repeat, s.catchup, s.late, s.misremember, s.correction)]
    return [k for slot in slots if slot is not None for k in slot.keys] + [
        k for s in o.subjects for band in s.mention for k in band.keys]


class Forwarding:
    """Ids through the renames, transitively: the engine's Renamer for engine kinds, a table per kind for LOCAL_KINDS."""

    def __init__(self, renames: Iterable[RenameEntry], standing: Iterable[str], cards: Iterable[str]) -> None:
        entries = list(renames)
        self.engine = Renamer((r for r in engine_renames(entries) if isinstance(r, Rename)), standing, cards)
        self._local = {kind: {r.old: r.new for r in entries if r.kind == kind and r.new is not None}
                       for kind in LOCAL_KINDS}
        self.retired = frozenset((r.kind, r.old) for r in entries if r.new is None)
        """Each retired id as (kind, id): lines, journal notes and entries, and a retired note's trigger."""

    def local(self, kind: str, key: str) -> str:
        """`key` of a LOCAL_KINDS kind through every rename of it (a cycle stops where it closes)."""
        table, seen = self._local[kind], {key}
        while key in table and table[key] not in seen:
            key = table[key]
            seen.add(key)
        return key


def forwarding(renames: list[RenameEntry]) -> Forwarding:
    """Runners are told apart by the renames' own kinds: a runner is a card unless a standing rename names it."""
    standing = {n for r in renames if r.kind == "standing" for n in (r.old, r.new) if n is not None}
    cards = {n for r in renames if r.kind == "card" for n in (r.old, r.new) if n is not None}
    return Forwarding(renames, standing, cards)


def forwarded(outcome: Outcome, fwd: Forwarding) -> Json:
    """The outcome with every id and line key through the renames, as the codec writes it."""
    o = renamed_outcome(outcome, fwd.engine)
    return to_json(replace(o, lines=tuple(LineKey(fwd.local("line", k)) for k in o.lines)))


def _json_value(j: Json) -> JsonValue:
    return cast(JsonValue, j)  # cast -- one shape under two names; list invariance blocks it


def _rename_json(r: RenameEntry) -> dict[str, str | None]:
    return {"kind": r.kind, "from": r.old, "to": r.new}
