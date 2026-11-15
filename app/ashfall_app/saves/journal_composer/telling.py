"""Which slot tells a subject, and whether it is a must (statements 7, 8 and "Terms"), shared by a subject's own day
and its catch-up after a gap."""
from dataclasses import dataclass

from ..journal import Band, SlotName, Subject


@dataclass(frozen=True)
class Telling:
    """A note to write: its subject, its slot, the keys it draws from, and the bag those keys take turns in (the slot's
    name, or a crowd's band within `mention`)."""

    subject: str
    slot: SlotName
    keys: tuple[str, ...]
    bag: str


def keys_of(subject: Subject, slot: SlotName) -> tuple[str, ...]:
    """A slot's keys; `mention` has bands instead (`band`)."""
    slots = {
        "first": subject.first, "repeat": subject.repeat, "catchup": subject.catchup, "late": subject.late,
        "misremember": subject.misremember, "correction": subject.correction,
    }
    return slots.get(slot, ())


def plain(subject: Subject, slot: SlotName) -> Telling | None:
    """The telling by a slot other than `mention`, or None when that slot is empty."""
    keys = keys_of(subject, slot)
    return Telling(subject.id, slot, keys, slot) if keys else None


def band(subject: Subject, count: int) -> Band | None:
    """The band whose `at_least` is the highest at most `count`; None below every band."""
    reached = [b for b in subject.mention if b.at_least <= count]
    return max(reached, key=lambda b: b.at_least) if reached else None


def own_slot(subject: Subject, told: int) -> SlotName | None:
    """The slot that tells the subject on a day it shows, before misremembering: `first` until told, then `mention` for
    a crowd, else `repeat`, or none for a told subject with an empty `repeat` ("written once")."""
    if told == 0:
        return "first"
    if subject.kind == "crowd":
        return "mention"
    return "repeat" if subject.repeat else None


def is_must(subject: Subject, told: int) -> bool:
    """A beat or person with a slot to tell it by, or a routine not yet told."""
    if subject.kind in ("beat", "person"):
        slot = own_slot(subject, told)
        return slot is not None and bool(keys_of(subject, slot))
    return subject.kind == "routine" and told == 0 and bool(subject.first)
