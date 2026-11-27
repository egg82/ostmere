"""Every store a served cause names (a chronicle line's, an ask's) is one the player is shown, or a clock worded as a
part of the day (StoreEntry.clock): a store the player never sees has no amount to read, so "20 day" is never a
cause (api/contract/endpoints.txt, "Line causes"; docs/decisions/principles.md, "Progress is stated, never hinted")."""
import pytest

from ashfall_app.api.world.content_models import Content
from ashfall_app.api.goals.decision_models import AtLeast, AtMost, StoreValue
from ashfall_app.api.world.line_causes import line_infos
from ashfall_app.api.world.line_models import LineCause, WhenCause
from ashfall_app.api.service import Game
from ashfall_app.opening.face_checks import shown_stores, timed_stores
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.ruleset import ruleset


@pytest.fixture(scope="module")
def served(shipped_opening: Opening) -> Content:
    return Game(shipped_opening, ruleset(shipped_opening, "dev", 1)).content()


def named(content: Content) -> list[tuple[str, str]]:
    """(where, store) for each served cause that reads a store's amount."""
    causes: list[tuple[str, LineCause | None]] = [(f"line {i.key}", i.cause) for i in content.line_infos]
    causes += [(f"offer {x.offer}", x.cause) for x in content.offer_infos]
    return [(where, c.when.watched.store) for where, c in causes
            if isinstance(c, WhenCause) and isinstance(c.when, (AtLeast, AtMost)) and isinstance(c.when.watched, StoreValue)]


def unworded(o: Opening, content: Content) -> list[str]:
    shown, timed = shown_stores(o), timed_stores(o)
    return [f"{where}: {store}" for where, store in named(content) if store not in shown and store not in timed]


def test_every_store_a_cause_names_is_shown_or_a_time(shipped_opening: Opening, served: Content):
    assert len(named(served)) > 10, "found almost no store causes: the check is blind"
    found = unworded(shipped_opening, served)
    assert not found, "\n".join(found)


def test_a_cause_on_a_clock_with_no_time_of_day_is_dropped(shipped_opening: Opening, served: Content):
    beat = next(t for t in shipped_opening.triggers if t.when.subject_kind == "store" and t.when.id == "night_5"
                and t.outcome.line_keys)
    caused = {i.key: i.cause for i in served.line_infos}
    assert isinstance(caused[beat.outcome.line_keys[0]], WhenCause), "the control beat lost its time-of-day cause"
    stores = [s.model_copy(update={"clock": None}) if s.id == "night_5" else s for s in shipped_opening.stores]
    dropped = {i.key: i.cause for i in line_infos(shipped_opening.model_copy(update={"stores": stores}))}
    assert dropped[beat.outcome.line_keys[0]] is None
