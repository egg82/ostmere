"""Every card says where its work is shown: a `site` (entries.SiteEntry) naming a scene layer, or why it has none. A card and its
`twin_of` name the same site, and a site's layer is one the committed tools/scene/shown.json lists. The cards without a
site are held per chapter file in tests/held/card_sites.json, and the count only shrinks:
`python -m tests.test_scene_sites --write` (from app/) lowers it once one is authored; never run it to let a new one through."""
import json
import sys
import tomllib
from pathlib import Path

import pytest

from ashfall_app.opening.entries import CardEntry
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, OPENING, Opening, load_opening
from ashfall_app.opening.site_entries import SiteEntry
from ashfall_app.opening.site_checks import check_sites, unsited
from tests.held_ledger import Ledger, dump, load, problems, tally, total

APP = Path(__file__).resolve().parents[1]
HELD = APP / "tests/held/card_sites.json"
SHOWN = APP.parent / "tools/scene/shown.json"
FILES = (OPENING, *CHAPTERS, *IN_WRITING)


def full() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def home() -> dict[str, str]:
    """Each hand-written card's id to the file that authors it."""
    out: dict[str, str] = {}
    for path in FILES:
        with path.open("rb") as f:
            for c in tomllib.load(f).get("cards", []):
                out[c["id"]] = str(path.relative_to(APP))
    return out


def ledger(o: Opening) -> Ledger:
    where = home()
    return tally([(where.get(c.id, "?"), "no site") for c in unsited(o)])


def scene_layers() -> set[str]:
    return set(json.loads(SHOWN.read_text())["layers"])


def bad_layers(o: Opening, layers: set[str]) -> list[str]:
    return sorted(f"{c.id}: {c.site.layer}" for c in o.cards if c.site is not None and c.site.layer is not None
                  and c.site.layer not in layers)


@pytest.fixture(scope="module")
def content() -> Opening:
    return full()


def test_every_card_has_a_site_or_is_held(content: Opening):
    assert sum(1 for c in content.cards if c.site is not None) > 5, "almost no sites seen: the check is blind"
    found = problems(ledger(content), load(HELD), "author a `site` on the card (a scene layer, or `no_site` and why)",
                     "python -m tests.test_scene_sites --write")
    assert not found, "\n".join(found)


def test_every_site_names_a_layer_the_scene_has(content: Opening):
    layers = scene_layers()
    assert layers, "shown.json lists no layers: rebuild the scene"
    assert bad_layers(content, layers) == []


def planted(o: Opening, *cards: CardEntry) -> Opening:
    return o.model_copy(update={"cards": [*o.cards, *cards]})


def card(id: str, **fields: object) -> CardEntry:
    return CardEntry.model_validate({"id": id, "presentation": "action", "label_key": "c_stew", "work_s": 10, **fields})


def test_a_card_without_a_site_is_counted_and_one_with_it_is_not(content: Opening):
    bare, sited = card("plant"), card("plant", site={"no_site": "done anywhere"})
    assert [c.id for c in unsited(planted(content, bare))][-1] == "plant"
    assert "plant" not in {c.id for c in unsited(planted(content, sited))}


def test_a_site_naming_a_missing_layer_is_reported(content: Opening):
    found = bad_layers(planted(content, card("plant", site={"layer": "no_such_layer"})), scene_layers())
    assert "plant: no_such_layer" in found


def test_a_twin_naming_another_site_fails(content: Opening):
    base = card("plant", site={"layer": "fire_lit"})
    apart = card("n1_plant", lane="n1", twin_of="plant", site={"layer": "watch_lit"})
    same = apart.model_copy(update={"site": SiteEntry(layer="fire_lit")})
    check_sites(planted(content, base, same))
    with pytest.raises(ValueError, match="card n1_plant: site differs from its twin_of plant"):
        check_sites(planted(content, base, apart))
    with pytest.raises(ValueError, match="card n1_plant: site differs"):
        check_sites(planted(content, base, apart.model_copy(update={"site": None})))


@pytest.mark.parametrize("fields", [{}, {"layer": "x", "no_site": "y"}])
def test_a_site_needs_exactly_one_answer(fields: dict[str, str]):
    with pytest.raises(ValueError, match="exactly one of layer and no_site"):
        SiteEntry.model_validate(fields)


if __name__ == "__main__" and "--write" in sys.argv:
    led = ledger(full())
    HELD.write_text(dump(led))
    print(f"wrote {HELD}: {total(led)} held")
