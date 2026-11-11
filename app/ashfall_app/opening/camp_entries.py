"""The Camp's entries: the bar to work toward and its levels (engine DESIGN.txt, "THE CAMP")."""
from pydantic import Field

from .entries import Entry, ModifierEntry


class CampLevelEntry(Entry):
    """One Camp level: reached when the camp store holds `at_items`; its outcome lands then (a trigger the loader makes)."""

    at_items: int = Field(ge=1)
    pays_key: str
    pays_from: int | None = None
    pays_to: int | None = None
    """What the level pays as a number, in items before and after (the wall takes 3, then 5); a story unlock has none.
    Both or neither; a test holds them to what the engine does."""
    line_keys: list[str] = []
    modifiers: list[ModifierEntry] = []
    held: bool = False
    """A marker past the content: the bar fills to just below it and holds there, pays_unknown on its marker. Without
    a lifted_by it never lands (a later chapter replaces it): only the last level, with no lines or modifiers."""
    lifted_by: list[str] = []
    """The capped cards any one of whose finish lifts a held level: the loader adds a raise of the camp store's cap to
    each card's `finished`, so the bar fills on and the level lands. Two or more are alternatives an offer's answers
    unlock (engine DESIGN.txt, "THE CAMP"). A lifted level may be any level, and lands what it names."""


class CampEntry(Entry):
    """The bar to work toward: a store every hands card fills by work done, `items_per_hour` at a full share, so a
    tap and a mix share count alike by the time they take (the loader adds that make flow to every hands card).
    Its levels are reached in order; the store's cap is what its levels allow (convert.camp_cap): the last level's
    at_items, or one under the first held level a step lifts, raised from there by the steps of convert.camp_chain."""

    store: str
    items_per_hour: int = Field(ge=1)
    levels: list[CampLevelEntry]
