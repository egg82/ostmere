"""Day twelve's one new pose: the player digging at the ruin's north wall, back to the camp, with the shovel.
The wolf that sits at the light's edge is the found world's (`daytwelve_world`); the bear has no pose (off the scene).
Story spoilers (content/team/week-two.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image

from daythree_poses import shovel
from daytwelve_made import CELLAR
from figures import from_behind

DIGS = (CELLAR[0] - 6, CELLAR[1] + 24)
"""Where the player stands to dig: just out from the wall, a little left of the pit's middle, back to the camp."""


def digging() -> Image.Image:
    """Day three's digging pose (the shovel down at the wall's foot), at the cellar."""
    tool = shovel()
    return from_behind(DIGS, held=[(tool, 6, -tool.height + 2)])
