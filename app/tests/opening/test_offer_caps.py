"""offer_cap: the cap a store has for certain when something is offered (opening/offer_caps.py)."""
from ashfall_app.opening.entries import UnlockEntry
from ashfall_app.opening.offer_caps import Chain, offer_cap
from ashfall_app.opening.schema import Opening


def _smoked(o: Opening, after: UnlockEntry | None) -> float:
    return offer_cap(o, "smoked", after)


def test_smoked_by_the_family_has_every_rise_the_story_passes(shipped_opening: Opening):
    """The larder (3x) and the camp's levels 6, 10 and 12 (1.5x, 1.5x, 4/3x) all come before the family's meals, on
    a base of 4: 36 items."""
    assert abs(_smoked(shipped_opening, UnlockEntry(unlock_kind="action", id="n5_eating")) - 36) < 0.01


def test_a_store_offered_from_the_start_or_before_any_rise_keeps_its_own_cap(shipped_opening: Opening):
    """The control: no unlock gives the bare cap, and an early unlock has none of the later rises."""
    assert _smoked(shipped_opening, None) == 4
    assert _smoked(shipped_opening, UnlockEntry(unlock_kind="card", id="smoke_catch")) < 18


def test_a_later_unlock_has_more_behind_it_than_an_early_one(shipped_opening: Opening):
    chain = Chain(shipped_opening)
    early, late = chain.unlockers("card", "smoke_catch"), chain.unlockers("action", "n5_eating")
    assert early and late
    assert len(chain.before[late[0]]) > len(chain.before[early[0]]) > 0
