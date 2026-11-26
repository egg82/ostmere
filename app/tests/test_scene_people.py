"""tools/scene/people.py: every outcome that joins or leaves a person names, per person, the scene layer that shows it or
says why none does (`whereabouts`). The cases the scene shows nothing of today are held (`HELD_UNPLACED`, only shrinks);
a field's layer must be one the committed shown.json lists."""
import json
import sys
from collections.abc import Collection, Iterable
from functools import cache
from pathlib import Path

from ashfall_app.opening.entries import OutcomeEntry, WhereaboutsEntry
from ashfall_app.opening.schema import Opening, load_opening

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import people   # tools/scene, on the path from the line above

Outcomes = dict[str, OutcomeEntry]


def outcomes(o: Opening) -> Outcomes:
    """Every outcome the content has, by its owner: a trigger, a card's outcome and finish, an offer's answer."""
    found: Outcomes = {f"trigger:{t.id}": t.outcome for t in o.triggers}
    for c in o.cards:
        found[f"card:{c.id}/outcome"], found[f"card:{c.id}/finished"] = c.outcome, c.finished
    for x in o.offers:
        found.update({f"offer:{x.id}/{a.id}": a.outcome for a in x.answers})
    return found


def moved(out: OutcomeEntry) -> set[str]:
    """The people the outcome joins or leaves."""
    return {j.lane for j in out.joins} | {x.lane for x in out.leaves}


def placed(out: OutcomeEntry) -> set[str]:
    return {w.person for w in out.whereabouts}


def unplaced(found: Outcomes, held: Collection[str]) -> list[str]:
    """Joins and leaves with no whereabouts entry for the person and not held."""
    return sorted(f"{owner}:{p}" for owner, out in found.items() for p in moved(out) - placed(out) if f"{owner}:{p}" not in held)


def stale(found: Outcomes, held: Iterable[str]) -> list[str]:
    """Held cases that name no outcome, no person it has to do with or one whose outcome has since gained the entry."""
    bad: list[str] = []
    for case in sorted(held):
        owner, _, person = case.rpartition(":")
        out = found.get(owner)
        if out is None or person in placed(out):
            bad.append(case)
    return bad


def unresolved(found: Outcomes, lanes: Collection[str], layers: Collection[str]) -> list[str]:
    """Entries naming a person with no lane or a layer the scene lacks."""
    return sorted(f"{owner}:{w.person}" for owner, out in found.items() for w in out.whereabouts
                  if w.person not in lanes or (w.layer is not None and w.layer not in layers))


@cache
def opening() -> Opening:
    return load_opening()


def committed_layers() -> set[str]:
    return set(json.loads((SCENE / "shown.json").read_text())["layers"])


def lane_ids() -> set[str]:
    return {lane.id for lane in opening().lanes if lane.told is not None}


def test_every_join_and_leave_places_the_person_or_is_held():
    assert unplaced(outcomes(opening()), people.HELD_UNPLACED) == []


def test_the_held_cases_are_outcomes_still_without_the_entry():
    """Fails when a held case gains its entry (take it off the list) or names an outcome the content lacks."""
    assert stale(outcomes(opening()), people.HELD_UNPLACED) == []


def test_every_entry_names_a_person_and_a_layer_the_scene_has():
    assert committed_layers(), "shown.json lists no layers: rebuild the scene"
    assert unresolved(outcomes(opening()), lane_ids(), committed_layers()) == []
    assert any(out.whereabouts for out in outcomes(opening()).values()), "no outcome carries a whereabouts entry"


def out(**fields: object) -> OutcomeEntry:
    return OutcomeEntry.model_validate(fields)


def test_a_join_without_an_entry_and_a_stale_or_unresolved_one_are_reported():
    """The planted cases: an unplaced join fails unless held; a held case that gained its entry or names no outcome is
    stale; an entry naming a missing layer or a person with no lane is unresolved; an entry with both or neither answer
    does not load."""
    join = {"lane": "n9", "mix": "town:camp", "own_split": True}
    bare = out(joins=[join])
    shown = out(joins=[join], whereabouts=[{"person": "n9", "layer": "figure_n9"}])
    found = {"trigger:a": bare, "trigger:b": shown, "trigger:c": out(leaves=[{"lane": "n9"}])}
    assert unplaced(found, set()) == ["trigger:a:n9", "trigger:c:n9"]
    assert unplaced(found, {"trigger:a:n9"}) == ["trigger:c:n9"]
    assert stale(found, {"trigger:a:n9", "trigger:b:n9", "trigger:z:n9"}) == ["trigger:b:n9", "trigger:z:n9"]
    assert unresolved(found, {"n9"}, {"figure_n9"}) == []
    assert unresolved(found, {"n9"}, set()) == ["trigger:b:n9"]
    assert unresolved(found, set(), {"figure_n9"}) == ["trigger:b:n9"]
    for fields in ({"person": "n9"}, {"person": "n9", "layer": "x", "no_scene": "y"}):
        try:
            WhereaboutsEntry.model_validate(fields)
        except ValueError:
            continue
        raise AssertionError(f"{fields} loaded")


def test_the_audit_finds_outcomes_in_every_owner_kind():
    found = outcomes(opening())
    kinds = {owner.partition(":")[0] for owner in found}
    assert kinds == {"trigger", "card", "offer"}
    assert "trigger:t_joins" in found and any(o.joins for o in found.values())

