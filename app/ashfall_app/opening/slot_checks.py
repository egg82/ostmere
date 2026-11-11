"""The slots a text may hold: each is one the page fills for that text's key (api/CONTRACT.txt, "Text and numbers"), else
its braces would show. A `{<lane id>}` is a person's name in any text (name_checks.py checks it has one) and `{found}` is a
find line's (find_checks.py checks where). Raises ValueError naming the key and the slot (refs.fail)."""
from collections.abc import Iterable
from typing import TYPE_CHECKING

from .find_checks import SLOT_NAME as FOUND
from .name_checks import SLOT
from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening

PERCENT = frozenset({"pct", "pct_b"})
BY_KIND: dict[str, frozenset[str]] = {
    "skill": PERCENT, "card": PERCENT, "chip": PERCENT, "camp": PERCENT | {"from", "to"},
    "answer": PERCENT | {"d", "gain", "gain_b"},
}
"""The slots beyond a lane's and `{found}` that a text is filled with, by the kind of entry that names its key (the first
word of the `where` in checks._key_fields)."""
UI = frozenset({
    "a", "after", "ago", "answer", "b", "before", "build", "cap", "card", "chip", "costs", "d", "days", "fought", "from", "goal", "h", "have",
    "level", "lost", "m", "max", "minutes", "mix", "n", "name", "need", "node", "number", "of", "pays", "pct", "percent", "person",
    "played", "power", "rule", "runner", "s", "seen", "side_name", "skill", "started", "store", "store_b", "task", "threat",
    "threat_name", "until", "when", "won",
})
"""The slots the page fills in the fixed `ui.` texts (CONTRACT, "Text and numbers" and the section of each key's feature)."""


def _union(sets: Iterable[frozenset[str]]) -> frozenset[str]:
    return frozenset(slot for s in sets for slot in s)


def check_slots(o: "Opening", key_fields: Iterable[tuple[str, str]]) -> None:
    """Every slot of every text is a lane's, `{found}`, or one its key's kind is filled with. `key_fields` is each
    (entry, text key) the opening names; a key nothing names (dead text) may hold any kind's slot but a `ui.` one's."""
    kinds: dict[str, set[str]] = {}
    for where, key in key_fields:
        kinds.setdefault(key, set()).add(where.split()[0])
    lanes = {x.id for x in o.lanes}
    anywhere = _union(BY_KIND.values())
    for key, text in o.text.items():
        if key.startswith("ui."):
            allowed = UI
        elif key in kinds:
            allowed = _union(BY_KIND.get(k, frozenset()) for k in kinds[key])
        else:
            allowed = anywhere
        for slot in SLOT.findall(text):
            if slot not in allowed and slot not in lanes and slot != FOUND:
                fail(f"text {key}", f"holds the slot {{{slot}}}, which nothing fills in this text")
