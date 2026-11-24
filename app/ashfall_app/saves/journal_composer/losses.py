"""The notes a day's end writes from the loss runners' lost tallies (api/CONTRACT.txt, "LOSS LINES", L1-L6): what each
runner still owes the journal, one loss note drawn from its pool, and a fold note counting the rest."""
import hashlib
from collections.abc import Iterable, Sequence

from ..journal import ComposedDay, Loss, Note

FOLD_KEY = "ui.journal.fold"


def notes(save_id: int, composed: Sequence[ComposedDay], page: Sequence[Note], losses: Iterable[Loss]) -> list[Note]:
    """The loss and fold notes at the end of a day whose page so far is `page` (L1-L3), runners in id order."""
    out: list[Note] = []
    for loss in sorted(losses, key=lambda x: x.runner):
        owed = loss.lost - told(composed, loss.runner)
        if owed < 1:
            continue
        out.append(Note(loss.runner, "loss", key(save_id, loss, [*_notes(composed), *page, *out])))
        if owed > 1:
            out.append(Note(loss.runner, "fold", FOLD_KEY, owed - 1))
    return out


def told(composed: Sequence[ComposedDay], runner: str) -> int:
    """L2: the runner's loss notes and its folds' counts, over the stored days."""
    return sum(1 if n.slot == "loss" else n.count or 0
               for n in _notes(composed) if n.subject == runner and n.slot in ("loss", "fold"))


def key(save_id: int, loss: Loss, before: Sequence[Note]) -> str:
    """L5: the next key of the pool after every earlier draw from it, by any subject, a round at a time and never the
    key just drawn."""
    pool = loss.keys
    drawn = [n.key for n in before if n.slot != "fold" and n.key in pool]
    round_no = len(drawn) // len(pool)
    used = set(drawn[round_no * len(pool):])
    candidates = [k for k in pool if k not in used]
    if not used and drawn and len(pool) > 1:
        candidates.remove(drawn[-1])
    return min(candidates, key=lambda k: _shuffle(save_id, loss.runner, round_no, k))


def _notes(composed: Sequence[ComposedDay]) -> list[Note]:
    return [n for r in composed for n in r.notes]


def _shuffle(save_id: int, runner: str, round_no: int, k: str) -> bytes:
    return hashlib.sha256(f"{save_id}|journal|loss|{runner}|{round_no}|{k}".encode()).digest()
