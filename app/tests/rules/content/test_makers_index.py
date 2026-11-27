"""makers_by_store answers what card_makers, made_by and rises_in_steps answer store by store, on the shipped content."""
from ashfall_app.rules.makers import card_makers, made_by, makers_by_store, rises_in_steps
from ashfall_app.rules.schema import Opening


def test_the_index_gives_each_store_its_makers_in_card_order(shipped_opening: Opening) -> None:
    index = makers_by_store(shipped_opening)
    made = [s.id for s in shipped_opening.stores if card_makers(shipped_opening, s.id)]
    assert len(made) > 1 and len(made) < len(shipped_opening.stores), "control: some stores are made by cards, some not"
    for s in shipped_opening.stores:
        assert card_makers(shipped_opening, s.id, index) == card_makers(shipped_opening, s.id)
        assert made_by(shipped_opening, s.id, index) == made_by(shipped_opening, s.id)
        assert rises_in_steps(shipped_opening, s.id, index) == rises_in_steps(shipped_opening, s.id)
