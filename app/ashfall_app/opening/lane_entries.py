"""The lane entries: a lane besides the hands, and the label it takes once something is unlocked."""
from typing import Literal

from .entries import Entry, UnlockEntry


class LaneLabelEntry(Entry):
    """The lane row's label once `after` is unlocked (the last one held wins, as aims do)."""

    after: UnlockEntry
    label_key: str


class LaneEntry(Entry):
    """A lane besides the hands. ruled: a townsperson who works, whose task the player's rules set; its cards have no
    skill and no XP, and fill the camp store as hands cards do (engine DESIGN.txt, "Ruled lane")."""

    id: str
    label_key: str
    ruled: bool = False
    station: bool = False
    """A ruled lane that is a thing, not a person (the pot on the fire): its one task is set by the player's rules, and
    its cards do no work for the camp."""
    later_labels: list[LaneLabelEntry] = []
    name_key: str | None = None
    """The person's name, as a label writes it: the page fills a text's `{<lane id>}` slot with it (api/CONTRACT.txt,
    "Text and numbers")."""
    told: Literal["line", "mention"] | None = None
    """How a ruled lane's person coming and going is written: in its outcome's story line, or a day's mention (people.py)."""
    pooled: bool = False
    """A group, not a person: a ruled lane its members' shared cards sit on. `label_key` is the group's name on screen; it
    has no `name_key` and no `told` (engine DESIGN.txt, "GROUPS (pooled lanes)")."""
    group: str | None = None
    """On a person's ruled lane, the pooled lane that is their group."""
    tied: str | None = None
    """On a pooled lane, the person's lane the group is tied to: one townsperson who looks after it (api/CONTRACT.txt,
    "GROUPS"). Authored, never inferred."""
