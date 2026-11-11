"""The release lock's checks: is this content change one a save from any released version survives?

Each problem has a class (engine DESIGN.txt, "Release lock"): needs_mapping (red until renames.toml maps it),
forbidden (red), out_of_date (red until tools/content_lock.py --write). Safe changes raise nothing. The server runs
these at start and tests/opening/test_released.py in CI.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from pydantic import JsonValue

from ..engine import IdKind, Outcome, RebaseError
from ..engine.codec import Json, from_json
from ..engine.upgrade import missing_upgrades
from .lock import KINDS, LOCK, Forwarding, Lock, forwarded, forwarding, load_lock, merged, snapshot
from .renames import RENAMES, RenameEntry, load_renames
from .schema import Opening, to_rules

type ProblemClass = Literal["needs_mapping", "forbidden", "out_of_date"]
WRITE = "run tools/content_lock.py --write"


@dataclass(frozen=True)
class Problem:
    cls: ProblemClass
    message: str


def problems(lock: Lock, now: Lock, renames: list[RenameEntry]) -> list[Problem]:
    """Every problem with the content `now` (lock.snapshot of it) against the released `lock`. --write may write only
    when every problem is out_of_date."""
    found = _rename_problems(lock, now, renames)
    if any(p.cls == "forbidden" for p in found):
        return found   # a cycle or a reuse: forwarding through the renames means nothing until it is fixed
    fwd = forwarding(renames)
    found += _removals(lock, now, fwd) + _caps(lock, now, fwd) + _outcomes(lock, now, fwd) + _ruled(lock, now, fwd)
    found += _answers(lock, now, fwd) + _kinds(lock, now, fwd)
    if lock.curve != now.curve[:len(lock.curve)]:
        found.append(Problem("forbidden", "a released curve threshold changed or went: append levels instead"))
    found += [Problem("forbidden", f"FORMAT has no upgrade from format {f} (engine/upgrade.py)")
              for f in missing_upgrades()]
    if merged(lock, now) != lock:
        found.append(Problem("out_of_date", f"the release lock does not hold this content: {WRITE}"))
    return found


def _rename_problems(lock: Lock, now: Lock, renames: list[RenameEntry]) -> list[Problem]:
    found: list[Problem] = []
    given = [{"kind": r.kind, "from": r.old, "to": r.new} for r in renames]
    found += [Problem("forbidden", f"a released rename was dropped: {r}") for r in lock.renames if r not in given]
    for r in renames:
        if {"kind": r.kind, "from": r.old, "to": r.new} not in lock.renames and r.new in lock.ids.get(r.kind, []):
            found.append(Problem("forbidden", f"{r.kind} {r.old} renamed to {r.new}, a released id: use a new one"))
        if r.old in now.ids.get(r.kind, []):
            found.append(Problem("forbidden", f"{r.kind} {r.old} was renamed away and is in the content again"))
    try:
        fwd = forwarding(renames)
        for r in renames:
            _ = fwd.engine.id(_kind(r.kind), r.old) if r.kind != "line" else fwd.line(r.old)
    except RebaseError as e:
        found.append(Problem("forbidden", f"the renames of {e.kind.value} {e.id} go round in a cycle"))
    return found


def _removals(lock: Lock, now: Lock, fwd: Forwarding) -> list[Problem]:
    found: list[Problem] = []
    for kind in KINDS:
        have = set(now.ids.get(kind, []))
        for x in lock.ids.get(kind, []):
            y = _fwd(fwd, kind, x)
            if y in have:
                continue
            if y != x:
                found.append(Problem("needs_mapping", f"{kind} {x} is renamed to {y}, which the content lacks"))
            elif any(x in now.ids.get(k, []) and x not in lock.ids.get(k, []) for k in KINDS if k not in (kind, "line")):
                found.append(Problem("forbidden", f"{kind} {x} became another kind of id: add a new id instead"))
            elif kind == "card":
                found.append(Problem("needs_mapping", f"card {x} was removed: retire it instead (an outcome's retired "
                                                      "unlock), or map it to a new card in renames.toml"))
            else:
                found.append(Problem("needs_mapping", f"{kind} {x} was removed: map it in renames.toml"))
    return found


def _caps(lock: Lock, now: Lock, fwd: Forwarding) -> list[Problem]:
    found: list[Problem] = []
    for x, cap in lock.store_caps.items():
        new = now.store_caps.get(_fwd(fwd, "store", x))
        if new is not None and new < cap:
            found.append(Problem("forbidden", f"store {x}'s cap went down: caps only rise"))
    for x, cap in lock.card_caps.items():
        y = _fwd(fwd, "card", x)
        if y in now.card_caps:
            new = now.card_caps[y]
            if new is not None and (cap is None or new < cap):
                found.append(Problem("forbidden", f"card {x}'s cap went down: caps only rise"))
    return found


def _outcomes(lock: Lock, now: Lock, fwd: Forwarding) -> list[Problem]:
    """A released trigger's outcome, both sides through today's renames, must be what it was: add a trigger instead."""
    found: list[Problem] = []
    for x, old in lock.outcomes.items():
        y = _fwd(fwd, "trigger", x)
        if y not in now.outcomes:
            continue
        was = _released(old)
        if not isinstance(was, Outcome) or forwarded(was, fwd) != now.outcomes[y]:
            found.append(Problem("forbidden", f"trigger {x}'s outcome changed: add a new trigger instead"))
    return found


def _released(old: JsonValue) -> object:
    """A released outcome as the lock keeps it, read back by the codec."""
    return from_json(cast(Json, old))  # cast -- JsonValue is Json's shape; list invariance blocks it


def _answers(lock: Lock, now: Lock, fwd: Forwarding) -> list[Problem]:
    """A released answer keeps its outcome and its offer, both compared after renames, and a card a released answer
    queues stays a hands card with a cap (engine DESIGN.txt, "Release lock" in part "TOWNSFOLK, INSTALLED RULES AND
    OFFERS")."""
    found: list[Problem] = []
    for x, old in lock.answer_outcomes.items():
        y = _fwd(fwd, "answer", x)
        was = _released(old)
        if y in now.answer_outcomes and (not isinstance(was, Outcome) or forwarded(was, fwd) != now.answer_outcomes[y]):
            found.append(Problem("forbidden", f"answer {x}'s outcome changed: saves that gave it keep the old one"))
        for card in was.queues if isinstance(was, Outcome) else ():
            c = _fwd(fwd, "card", card)
            if c in now.card_lanes and (now.card_lanes[c] != "hands" or now.card_caps.get(c) is None):
                found.append(Problem("forbidden", f"card {card}, which answer {x} queues, left the hands or lost its cap"))
    for x, offer in lock.answer_offers.items():
        y = _fwd(fwd, "answer", x)
        if y in now.answer_offers and now.answer_offers[y] != _fwd(fwd, "offer", offer):
            found.append(Problem("forbidden", f"answer {x} moved to another offer: add a new answer instead"))
    return found


def _kinds(lock: Lock, now: Lock, fwd: Forwarding) -> list[Problem]:
    """A released offer keeps its kind and a released answer its role, once given (compared after renames): a saved
    order that answers a kind means every offer of it, past and to come. Giving one to an offer that had none is safe
    (engine DESIGN.txt, "OFFER KINDS")."""
    found: list[Problem] = []
    for x, kind in lock.offer_kinds.items():
        y = _fwd(fwd, "offer", x)
        if y in now.ids["offer"] and now.offer_kinds.get(y) != kind:
            found.append(Problem("forbidden", f"offer {x}'s kind changed or went: a new offer instead"))
    for x, role in lock.answer_roles.items():
        y = _fwd(fwd, "answer", x)
        if y in now.ids["answer"] and now.answer_roles.get(y) != role:
            found.append(Problem("forbidden", f"answer {x}'s role changed or went: a new answer instead"))
    return found


def _ruled(lock: Lock, now: Lock, fwd: Forwarding) -> list[Problem]:
    """A released lane keeps its `ruled`, and a released card stays on, or off, a ruled lane, and a card on a ruled
    lane never moves to another and never gains an XP line (a cap given to it is _caps's): each would leave released
    content validation refuses, a save's queue holding a tap it can never make, or a saved town mix counting a share
    against the wrong person (engine DESIGN.txt, "Release lock" in parts "TOWNSFOLK, INSTALLED RULES AND OFFERS" and
    "THE TOWN'S MIX")."""
    found: list[Problem] = []
    for x, was in lock.lane_ruled.items():
        y = _fwd(fwd, "lane", x)
        if y in now.lane_ruled and now.lane_ruled[y] != was:
            found.append(Problem("forbidden", f"lane {x}'s ruled changed: a new lane id instead"))
    for x, lane in lock.card_lanes.items():
        y = _fwd(fwd, "card", x)
        if y in now.card_lanes and lock.lane_ruled.get(lane, False) != now.lane_ruled.get(now.card_lanes[y], False):
            found.append(Problem("forbidden", f"card {x} moved onto or off a ruled lane: a new card instead"))
        elif lock.lane_ruled.get(lane, False) and _fwd(fwd, "lane", lane) != now.card_lanes.get(y, lane):
            found.append(Problem("forbidden", f"card {x} moved from one ruled lane to another: a new card instead"))
        if y in now.card_lanes and lock.lane_ruled.get(lane, False) and now.card_xp.get(y, False):
            found.append(Problem("forbidden", f"card {x} on a ruled lane was given an XP line: a person's cards train nothing"))
    return found


def _fwd(fwd: Forwarding, kind: str, x: str) -> str:
    return fwd.line(x) if kind == "line" else fwd.engine.id(_kind(kind), x)


def _kind(kind: str) -> IdKind:
    return IdKind(kind)


def release_problems(o: Opening, lock_path: Path = LOCK, renames_path: Path = RENAMES) -> list[Problem]:
    """problems() for this content against the lock and renames.toml on disk: what the server checks at start."""
    renames = load_renames(renames_path)
    return problems(load_lock(lock_path), snapshot(o, to_rules(o), renames), renames)
