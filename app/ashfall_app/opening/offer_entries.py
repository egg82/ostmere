"""The content file's offers (engine DESIGN.txt, "Offers"): an offer and its answers, as Type Objects. Beside
entries.py, whose shapes they reuse."""
from pydantic import Field

from .entries import ConditionEntry, Entry, OutcomeEntry


class AnswerEntry(Entry):
    """One answer: its words, the words for what it costs ({d} the time its card takes), and what lands when given."""

    id: str
    label_key: str
    cost_key: str
    outcome: OutcomeEntry = OutcomeEntry()
    role: str | None = None
    """What this answer means in its offer's kind: set exactly when the offer has a `kind`, and the same set of roles
    in every offer of the kind (engine DESIGN.txt, "OFFER KINDS")."""


class OfferEntry(Entry):
    """Someone asks the player something: shown once `gate` and every `requires` hold (a trigger the loader makes,
    "offer_" + id), its line_keys written then; two or more answers; it never expires (engine DESIGN.txt, "Offers")."""

    id: str
    text_key: str
    gate: ConditionEntry
    requires: list[ConditionEntry] = []
    line_keys: list[str] = []
    kind: str | None = None
    """Offers of one kind are answered together by an AnswerKind order; see AnswerEntry.role."""
    answers: list[AnswerEntry] = Field(min_length=2)
