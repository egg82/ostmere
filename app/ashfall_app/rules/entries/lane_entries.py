"""The lane entries: a lane besides the hands, and the label it takes once something is unlocked."""
from typing import Literal

from pydantic import model_validator

from .entries import Entry, UnlockEntry


class LodgingEntry(Entry):
    """Where a person sleeps, as the content has it (app/tests/scene/test_scene_lodging.py): `build` the card whose build houses
    them, `elsewhere` the reason no build does. Exactly one; words only to the engine."""

    build: str | None = None
    elsewhere: str | None = None

    @model_validator(mode="after")
    def _one_answer(self) -> "LodgingEntry":
        if (self.build is None) == (self.elsewhere is None):
            raise ValueError("lodging: name exactly one of build and elsewhere")
        return self


class ByDayEntry(Entry):
    """Where a person is by day when no card of theirs is running (app/tests/scene/test_scene_day.py): `card` the card of their
    lane (or their crew's) whose work they stand at (its `site` names the scene layer), `at_fire` why the content seats them
    at the camp fire instead, `off_scene` why their work or place is outside what the scene draws (the scene keeps drawing
    them as before). Exactly one; words only to the engine."""

    card: str | None = None
    at_fire: str | None = None
    off_scene: str | None = None

    @model_validator(mode="after")
    def _one_answer(self) -> "ByDayEntry":
        if sum(x is not None for x in (self.card, self.at_fire, self.off_scene)) != 1:
            raise ValueError("by_day: name exactly one of card, at_fire and off_scene")
        return self


class LaneLabelEntry(Entry):
    """The lane row's label once `after` is unlocked (the last one held wins, as aims do)."""

    after: UnlockEntry
    label_key: str


class LaneEntry(Entry):
    """A lane besides the hands. ruled: a townsperson who works, whose task the player's rules set; its cards have no
    skill and no XP, and fill the camp store as hands cards do (engine design/townsfolk.txt, "Ruled lane")."""

    id: str
    label_key: str
    ruled: bool = False
    station: bool = False
    """A ruled lane that is a thing, not a person (the pot on the fire): its one task is set by the player's rules, and
    its cards do no work for the camp."""
    later_labels: list[LaneLabelEntry] = []
    name_key: str | None = None
    """The person's name, as a label writes it: the page fills a text's `{<lane id>}` slot with it (api/contract/text-and-numbers.txt,
    "Text and numbers")."""
    told: Literal["line", "mention"] | None = None
    """How a ruled lane's person coming and going is written: in its outcome's story line, or a day's mention (people.py)."""
    pooled: bool = False
    """A group, not a person: a ruled lane its members' shared cards sit on. `label_key` is the group's name on screen; it
    has no `name_key` and no `told` (engine design/groups.txt, "GROUPS (pooled lanes)")."""
    notable: bool = False
    """A person the story keeps: the only kind a close call (close_call_entries.py) is about. Authored, never inferred."""
    group: str | None = None
    """On a person's ruled lane, the pooled lane that is their group."""
    crews: list[str] = []
    """The pooled lanes this person can join, in preference order: the loader sets `group` to the smallest of them
    (most members among the lanes declared before this one; a tie goes to the first listed). A person only one crew can
    take lists that one. Never set beside `group`."""
    lodging: LodgingEntry | None = None
    """On a person's ruled lane, where they sleep (the scene shows who is at home at night). Authored on every person."""
    by_day: ByDayEntry | None = None
    """On a person's ruled lane, where they stand by day when idle: at the site of one of their cards, or at the fire for a
    reason the content gives (the scene's idle poses follow it). Authored on every person."""
    tied: str | None = None
    """On a pooled lane, the person's lane the group is tied to: one townsperson who looks after it (api/contract/groups.txt,
    "GROUPS"). Authored, never inferred."""
