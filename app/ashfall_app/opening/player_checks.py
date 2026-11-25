"""Who can do which job (docs/decisions/people.md): a card on a player's lane (the hands, or any lane not ruled) has a
town twin, a card on a townsperson's lane naming it in `twin_of`, or says in `only_player` why it has none. This checks
that both fields point the right way and that a card and its twin add the same to every tally store (the count their
completions share); tests/opening/test_player_only.py holds the cards that have neither. Structural
fields only, never ids or words. Raises ValueError naming the card (refs.fail)."""
from typing import TYPE_CHECKING

from .refs import fail

if TYPE_CHECKING:
    from .entries import CardEntry
    from .schema import Opening


def check_player_only(o: "Opening") -> None:
    town = town_lanes(o)
    cards = {c.id: c for c in o.cards}
    twinned = {c.twin_of for c in o.cards if c.twin_of is not None}
    tallies = {x.id for x in o.stores if x.tally}
    for c in o.cards:
        if c.twin_of is not None:
            if c.lane not in town:
                fail(f"card {c.id}", "twin_of is set, but the card is not on a townsperson's lane")
            twin = cards.get(c.twin_of)
            if twin is None or twin.lane in town:
                fail(f"card {c.id}", f"twin_of {c.twin_of} is not a card on a player's lane")
            elif counted(twin, tallies) != counted(c, tallies):
                fail(f"card {c.id}", f"adds to a tally store differently from its twin_of {c.twin_of}: a count both "
                                     "share must grow by the same amount from either")
        if c.only_player is not None and (c.lane in town or c.id in twinned):
            fail(f"card {c.id}", "only_player is set, but the card is on a townsperson's lane or has a town twin")


def counted(c: "CardEntry", tallies: set[str]) -> list[tuple[str, int, int]]:
    """What a completion adds to the tally stores, which only outcomes add to: the count a trip and its twin share."""
    return sorted((a.store, a.items, a.every) for a in c.outcome.stores if a.store in tallies)


def town_lanes(o: "Opening") -> set[str]:
    return {x.id for x in o.lanes if x.ruled and not x.station}


def unmarked(o: "Opening") -> list["CardEntry"]:
    """The player's cards with neither a town twin nor an only_player tag."""
    town = town_lanes(o)
    twinned = {c.twin_of for c in o.cards if c.twin_of is not None}
    return [c for c in o.cards if c.lane not in town and c.id not in twinned and c.only_player is None]
