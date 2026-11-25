"""tools/scene: every build the player can finish (a craft card with a cap) has a scene state once done, a layer whose
condition names its completions or a feature its completion unlocks, or is named in `builds.NO_SCENE` (made, but no
standing thing in the scene) or held in `builds.HELD_UNSHOWN` (owed a state; only shrinks). What the layers show is
the committed shown.json, which tools/scene/build.py rewrites from the layers it seeds (shown.py)."""
import json
import sys
from collections.abc import Collection, Iterable
from functools import cache
from pathlib import Path

from ashfall_app.opening.entries import CardEntry
from ashfall_app.opening.schema import load_opening

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import builds   # tools/scene, on the path from the line above
from shown import facts_shown


def is_build(card: CardEntry) -> bool:
    return card.presentation == "craft" and card.cap is not None


def features_unlocked(card: CardEntry) -> set[str]:
    return {u.id for out in (card.outcome, card.finished) for u in out.unlocks if u.unlock_kind == "feature"}


def unshown(cards: Iterable[CardEntry], shown: dict[str, list[str]], excused: Collection[str]) -> list[str]:
    """The builds among `cards` with no scene state in `shown` and not in `excused`."""
    return sorted(c.id for c in cards if is_build(c) and c.id not in excused and c.id not in shown["cards"]
                  and not features_unlocked(c) & set(shown["features"]))


@cache
def opening_cards() -> tuple[CardEntry, ...]:
    return tuple(load_opening().cards)


def committed() -> dict[str, list[str]]:
    return json.loads((SCENE / "shown.json").read_text())


def card(card_id: str, **fields: object) -> CardEntry:
    return CardEntry.model_validate({"id": card_id, "presentation": "craft", "label_key": "k", "work_s": 1, "cap": 2, **fields})


def test_every_build_has_a_scene_state_unless_named():
    shown = committed()
    assert shown["cards"] and shown["features"], "shown.json lists nothing: rebuild the scene"
    assert unshown(opening_cards(), shown, builds.NO_SCENE | builds.HELD_UNSHOWN) == []


def test_the_held_and_named_lists_are_builds_with_no_state():
    """Fails when a held build gains a state (take it off the list) or a listed id is no build the opening has."""
    every = {c.id: c for c in opening_cards()}
    listed = builds.NO_SCENE | builds.HELD_UNSHOWN
    assert not builds.NO_SCENE & builds.HELD_UNSHOWN
    assert sorted(i for i in listed if i not in every or not is_build(every[i])) == []
    assert unshown([every[i] for i in listed], committed(), ()) == sorted(listed)


def test_a_build_with_no_state_is_reported_and_one_shown_is_not():
    """The planted case: a capped craft card no layer names fails; a named one, one shown through the feature it
    unlocks, an excused one and a card that is no build pass."""
    shown = {"cards": ["named"], "features": ["roofed"]}
    cards = [card("named"), card("bare"), card("excused"), card("uncapped", cap=None), card("told", presentation="narrative"),
             card("via_feature", finished={"unlocks": [{"unlock_kind": "feature", "id": "roofed"}]})]
    assert unshown(cards, shown, {"excused"}) == ["bare"]


def test_shown_reads_completions_and_features_from_every_condition():
    layers = [{"when": "always"}, {"when": "pushes:hall@2&running:x", "until": "pushes:hall@4"},
              {"when": "store:a|project:make_hut", "until": "feature:roofed"}]
    assert facts_shown(layers) == {"cards": ["hall", "make_hut"], "features": ["roofed"]}
