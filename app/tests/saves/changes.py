"""A test change of today's opening (a renamed store with its mapping, a retuned work_s, a new card a new trigger
unlocks), shared by the golden saves and the saves service's rebase tests."""
from functools import cache

from ashfall_app.engine import CardId, IdKind, Rename
from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.schema import OPENING, CardEntry, Opening, TriggerEntry
from tests.opening.edited import edited, roots_renamed

RENAMES = (Rename(IdKind.STORE, "roots", "tubers"),)
RETUNED = CardId("lay_to_dry")


def _retuned(part: str) -> str:
    return part.replace("work_s = 45", "work_s = 60")


@cache
def changed_opening() -> Opening:
    """The test change: roots renamed tubers, lay_to_dry retuned 45 s -> 60 s, a new card unlocked by a new trigger
    that is true from time 0 (so it fires at every save's rebase) and lands a line."""
    assert OPENING.read_text().partition("[text]")[0].count("work_s = 45") == 1
    o = edited(lambda d: _retuned(roots_renamed(d)))
    line = o.cards[0].line_keys[0]
    card = CardEntry.model_validate({**o.cards[4].model_dump(), "id": "gather_more", "glows": False})
    trigger = TriggerEntry.model_validate({
        "id": "t_gather_more", "when": {"test": "after_time", "value": 0},
        "outcome": {"unlocks": [{"unlock_kind": "card", "id": "gather_more"}], "line_keys": [line]}})
    o = o.model_copy(update={"cards": [*o.cards, card], "triggers": [*o.triggers, trigger]})
    check_opening(o)
    return o


@cache
def retuned_opening() -> Opening:
    """A change an older build could rebase back from (lay_to_dry retuned 45 s -> 60 s, nothing added or renamed): only
    the build order keeps the older build from writing a save the newer one wrote."""
    assert OPENING.read_text().partition("[text]")[0].count("work_s = 45") == 1
    return edited(_retuned)
