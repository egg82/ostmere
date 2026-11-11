"""The checks on people's names (LaneEntry.name_key): a text's `{<lane id>}` slot is that lane's person's name, which
the page fills (api/CONTRACT.txt, "Text and numbers"). Raises ValueError naming the entry (refs.fail)."""
import re
from typing import TYPE_CHECKING

from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening

SLOT = re.compile(r"\{([A-Za-z]\w*)\}")
"""A named slot; its name may hold a digit (a person's, `{n2}`), the text around it may not."""


def without_slots(text: str) -> str:
    return SLOT.sub("", text)


def check_names(o: "Opening") -> None:
    """Every slot that names a lane names one with a name_key, so no text names a person the content has not named."""
    lanes = {x.id: x.name_key for x in o.lanes}
    for key, text in o.text.items():
        for slot in SLOT.findall(text):
            if slot in lanes and lanes[slot] is None:
                fail(f"text {key}", f"names lane {slot}, which has no name_key")
