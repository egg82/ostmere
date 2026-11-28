"""Wire models of the lanes in the game's static content (Content.lane_infos). The conventions in models.py hold here."""
from typing import Literal

from pydantic import BaseModel

from ..models import Unlock


class LaneLabel(BaseModel):
    after: Unlock
    label_key: str


class LaneInfo(BaseModel):
    """Every lane, "hands" included. Its label is the label_key of the last of later_labels whose `after`
    view.unlocked holds, else label_key (contract/a-lane-run-by-rules.txt, "A lane run by rules")."""

    lane: str
    label_key: str
    ruled: bool
    """A townsperson who works: the player's rules set its task, never their tap."""
    station: bool
    """A ruled lane that is a thing, not a person (the pot on the fire): its one task is its always rule, which a tap on
    a task of its page sets (contract/a-lane-run-by-rules.txt, "A lane run by rules")."""
    later_labels: list[LaneLabel]
    name_key: str | None
    """The person's name, filling every text's {<lane>} slot (contract/text-and-numbers.txt, "Text and numbers"); null: no name."""
    told: Literal["line", "mention"] | None
    """How a person's coming and going is written (contract/people.txt, "People"); null for a lane that is not a person."""
    pooled: bool
    """A group, not a person: the lane its members' shared cards sit on, labelled with the group's name (contract/groups.txt,
    "GROUPS"). Never joins, never taps."""
    group: str | None
    """On a person's lane, the pooled lane that is their group; null for every other lane."""
    tied: str | None
    """On a pooled lane, the lane of the one person tied to the group (contract/groups.txt, "GROUPS"); null when none is."""


class CastLane(BaseModel):
    lane: str
    feature: str
    """The feature a cast unlocks for this lane: the lane is the role's person when view.unlocked holds it."""


class CastInfo(BaseModel):
    """A role some outcome casts: the lanes it may go to, in join order (contract/casting.txt, "CASTING"). A text's
    {<role>} slot is the name of the lane whose feature view.unlocked holds."""

    role: str
    label_key: str
    """The role's display name: the title of the cast person's row in the town list, their own name beside it."""
    lanes: list[CastLane]
