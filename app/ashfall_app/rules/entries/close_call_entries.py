"""A close call: content puts a notable in mortal danger and spares them (docs/decisions/people.md, "Death is
expected"). Authored here, never inferred from a line's words. Counting them and judging their spacing is a readout
(tests/rules/play/close_calls_readout.py); the loader checks structure only (close_call_checks.py)."""
from .entries import Entry


class CloseCallEntry(Entry):
    id: str
    person: str
    """The notable's lane id."""
    beat: str
    """The spine beat (content/beats.yaml) the close call lands with, which gives the readout its story day."""
    at: str
    """The trigger or answer whose outcome puts them in danger and spares them."""
    change: str | None = None
    """Where they change afterwards: a trigger or answer id, or a text key. None says the close call changed nobody,
    which the readout shows."""
