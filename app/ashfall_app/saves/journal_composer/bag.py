"""The shuffle bag (statement 19): the next key of a slot completes the current round of its keys before any repeats,
in an order shuffled per save, subject, slot and round."""
import hashlib
from collections.abc import Sequence

from ..journal import ComposedDay, Note
from .ledger import drawn
from .telling import Telling


def pick(save_id: int, subject: str, bag: str, keys: tuple[str, ...], stored: list[str]) -> str:
    """The next key of `keys` after `stored` (this subject and bag's stored keys, oldest first)."""
    size = len(keys)
    round_no = len(stored) // size
    used = set(stored[round_no * size:])
    unused = [k for k in keys if k not in used]
    return min(unused, key=lambda k: _shuffle(save_id, subject, bag, round_no, k))


def note(save_id: int, composed: Sequence[ComposedDay], t: Telling) -> Note:
    stored = drawn(composed, t.subject, t.slot, t.keys)
    return Note(t.subject, t.slot, pick(save_id, t.subject, t.bag, t.keys, stored))


def _shuffle(save_id: int, subject: str, bag: str, round_no: int, key: str) -> bytes:
    return hashlib.sha256(f"{save_id}|journal|bag|{subject}|{bag}|{round_no}|{key}".encode()).digest()
