"""Nothing is named ahead of a store or action it names (rules/checks/cards/unlock_order_checks.py): a chip's effect, a card's
inputs, drains and costs, an order card's store and a standing action's costs, on a standing action or a store only
the player's progress opens, unlock only once that is open. The controls put the defect back: a chip, a card and a drain
opened by the frost, the choir's arrival and the rows' night while no bed exists."""
import pytest

from ashfall_app.rules.entries.entries import UnlockEntry
from ashfall_app.rules.offer_caps import Chain
from ashfall_app.rules.schema import CHAPTERS, IN_WRITING, Opening, load_opening
from ashfall_app.rules.checks.cards.unlock_order_checks import sealed, unordered


@pytest.fixture(scope="module")
def content() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def named(o: Opening) -> set[str]:
    return {w for w, _, _, _ in unordered(o)}


def unlocking(o: Opening, trigger: str, *unlocks: UnlockEntry) -> Opening:
    """`o` with `unlocks` added to a trigger's outcome."""
    ts = [t.model_copy(update={"outcome": t.outcome.model_copy(update={"unlocks": [*t.outcome.unlocks, *unlocks]})})
          if t.id == trigger else t for t in o.triggers]
    return o.model_copy(update={"triggers": ts})


def test_nothing_is_named_ahead_of_what_it_names(content: Opening):
    chain = Chain(content)
    shut = {k for k in chain.unlocked_by if k[0] == "store" and sealed(content, chain, k[1])}
    assert ("store", "ripe") in shut and len(shut) > 3, "found too few locked stores: the check is blind"
    assert unordered(content) == []


def test_a_chip_opened_by_the_frost_ahead_of_the_beds_is_named(content: Opening):
    gone = content.model_copy(update={"triggers": [t.model_copy(update={"requires": []}) if t.id == "t_frost_beds" else t
                                                   for t in content.triggers]})
    assert named(gone) == set(), "the beds' gate is the trigger's `when`, not its requires"
    early = unlocking(content, "t_frost", UnlockEntry(unlock_kind="chip", id="frosted"))
    assert "chip frosted" in named(early)


@pytest.mark.parametrize(("trigger", "requires"), [("t_rows_black", "action rows_black")])
def test_a_drain_on_the_beds_opened_without_them_is_named(content: Opening, trigger: str, requires: str):
    ts = [t.model_copy(update={"requires": []}) if t.id == trigger else t for t in content.triggers]
    assert requires in named(content.model_copy(update={"triggers": ts}))


@pytest.mark.parametrize("offer", ["o_choir", "o_cutter"])
def test_reapers_who_arrive_without_beds_are_named(content: Opening, offer: str):
    offers = [x.model_copy(update={"requires": [c for c in x.requires if c.id != "beds"]}) if offer in x.id else x
              for x in content.offers]
    found = named(content.model_copy(update={"offers": offers}))
    assert any(w.endswith("_reap") for w in found), found
