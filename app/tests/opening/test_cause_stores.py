"""Every store a served cause names (a chronicle line's, an ask's) is one the player is shown, or a clock worded as a
part of the day (StoreEntry.clock): a store the player never sees has no amount to read, so "20 day" is never a
cause (api/CONTRACT.txt, "Line causes"; docs/decisions/principles.md, "Progress is stated, never hinted")."""
import pytest

from ashfall_app.api.content_models import Content
from ashfall_app.api.decision_models import AtLeast, AtMost, StoreValue
from ashfall_app.api.line_models import LineCause, WhenCause
from ashfall_app.api.service import Game
from ashfall_app.opening.face_checks import shown_stores
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def served(shipped_opening: Opening) -> Content:
    return Game(shipped_opening, ruleset(shipped_opening, load_renames(), "dev", 1)).content()


def named(content: Content) -> list[tuple[str, str]]:
    """(where, store) for each served cause that reads a store's amount."""
    causes: list[tuple[str, LineCause | None]] = [(f"line {i.key}", i.cause) for i in content.line_infos]
    causes += [(f"offer {x.offer}", x.cause) for x in content.offer_infos]
    return [(where, c.when.watched.store) for where, c in causes
            if isinstance(c, WhenCause) and isinstance(c.when, (AtLeast, AtMost)) and isinstance(c.when.watched, StoreValue)]


def unworded(o: Opening, content: Content) -> list[str]:
    shown = shown_stores(o)
    timed = {s.id for s in o.stores if getattr(s, "clock", None) is not None}
    return [f"{where}: {store}" for where, store in named(content) if store not in shown and store not in timed]


@pytest.mark.xfail(strict=True, reason="#59: a beat on a clock is caused by \"20 day\"")
def test_every_store_a_cause_names_is_shown_or_a_time(shipped_opening: Opening, served: Content):
    assert len(named(served)) > 10, "found almost no store causes: the check is blind"
    found = unworded(shipped_opening, served)
    assert not found, "\n".join(found)
