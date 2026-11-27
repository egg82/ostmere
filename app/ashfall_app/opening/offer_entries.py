"""The content file's offers (engine design/townsfolk.txt, "Offers"): an offer and its answers, as Type Objects. Beside
entries.py, whose shapes they reuse."""
from pydantic import Field

from .entries import ConditionEntry, Entry, ModifierEntry, OutcomeEntry


class EchoEntry(Entry):
    """What an answer that keeps nothing else leaves behind, `after_h` game hours after it is given: a line that refers
    back to the offer and one lasting modifier (its `source` names the answer). The loader makes the triggers and the
    clock (echoes.py), so an answer given before the echo existed echoes at rebase."""

    after_h: int = Field(ge=6, le=12)
    line_key: str
    modifier: ModifierEntry


class AnswerEntry(Entry):
    """One answer: its words, the words for what it costs ({d} the time its card takes), and what lands when given."""

    id: str
    label_key: str
    cost_key: str
    outcome: OutcomeEntry = OutcomeEntry()
    role: str | None = None
    """What this answer means in its offer's kind: set exactly when the offer has a `kind`, and the same set of roles
    in every offer of the kind (engine design/offer-kinds.txt, "OFFER KINDS")."""
    echo: EchoEntry | None = None
    """A lasting part for an answer with none of its own (echoes.py)."""


class KindRoleEntry(Entry):
    """One role of an offer kind, worded for whoever asks."""

    role: str
    label_key: str
    tally: str | None = None
    """The hidden tally store that counts this role's answers across the kind's offers: the loader makes a trigger for
    each such answer that adds one when it is given, so the count holds for a save that answered before (answer_checks.py)."""


class OfferKindEntry(Entry):
    """An offer kind's own words: a label for each role its offers' answers carry, written for every future ask of the
    kind, which is what an AnswerKind rule answers (contract/offers.txt, "Offers"). An offer's own answer labels are written
    for that one ask."""

    kind: str
    roles: list[KindRoleEntry] = Field(min_length=2)


class OfferEntry(Entry):
    """Someone asks the player something: shown once `gate` and every `requires` hold (a trigger the loader makes,
    "offer_" + id), its line_keys written then; two or more answers; it never expires (engine design/townsfolk.txt, "Offers")."""

    id: str
    text_key: str
    gate: ConditionEntry
    requires: list[ConditionEntry] = []
    line_keys: list[str] = []
    kind: str | None = None
    """Offers of one kind are answered together by an AnswerKind order; see AnswerEntry.role."""
    answers: list[AnswerEntry] = Field(min_length=2)
    askers: list[str] = []
    """The ruled lanes whose people ask, in the order the page names them; empty when no one person asks."""
    waiting_key: str | None = None
    """What waiting costs, for an offer whose waiting is not free; None says nothing (an open offer pauses only itself)."""
    expiry_key: str | None = None
    """When the offer goes unanswered; None says nothing, and every offer has None until the engine has offer expiry
    (engine design/, KNOWN GAPS)."""
    gates_read_feature: list[str] = []
    """Features that later gates read in place of this offer's answers: each is unlocked by the finish of a card every
    answer unlocks, and no condition anywhere reads this offer as answered or one of its answers (ask_checks.py)."""
    permanence_key: str | None = None
    """What the answer settles for good, for an offer whose permanence the player should weigh; None says nothing."""
