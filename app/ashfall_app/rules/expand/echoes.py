"""An answer's echo (`echo` on an answer, offer_entries.EchoEntry), expanded to ordinary entries: a trigger on the
answer's unlock that starts a moment clock (clocks.py), and a trigger on that clock that tells the line and lands the
modifier. The clock starts when the answer is seen unlocked, so a save that answered before echoes after its rebase."""
from typing import TYPE_CHECKING

from .clocks import PER_HOUR
from ..entries.entries import ConditionEntry, OutcomeEntry, TriggerEntry
from ..refs import fail

if TYPE_CHECKING:
    from ..schema import Opening


def with_answer_echoes(o: "Opening") -> "Opening":
    """`o` with the two triggers of each echo; an echo already expanded is left alone. Run before with_moment_clocks."""
    have = {t.id for t in o.triggers}
    made: list[TriggerEntry] = []
    for x in o.offers:
        for a in x.answers:
            if a.echo is None or f"t_echo_{a.id}" in have:
                continue
            e = a.echo
            if e.modifier.source != a.id:
                fail(f"answer {a.id}", f"echo modifier source is {e.modifier.source!r}, not the answer")
            clock = f"echo_{a.id}_clock"
            given = ConditionEntry(test="at_least", subject_kind="unlocked", unlock_kind="answer", id=a.id, value=1)
            made += [
                TriggerEntry(id=f"t_echo_{a.id}_start", when=given, outcome=OutcomeEntry(clock=clock)),
                TriggerEntry(id=f"t_echo_{a.id}", outcome=OutcomeEntry(line_keys=[e.line_key], modifiers=[e.modifier]),
                             when=ConditionEntry(test="at_least", subject_kind="store", id=clock, value=e.after_h * PER_HOUR)),
            ]
    return o.model_copy(update={"triggers": [*o.triggers, *made]}) if made else o
