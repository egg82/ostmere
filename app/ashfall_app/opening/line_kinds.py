"""The kind of every log line, authored beside its text in a `[line_kinds]` table (api/CONTRACT.txt, "Line kinds"): the page
sets a line by its kind and reads nothing from its key or words."""
from typing import TYPE_CHECKING, Literal

from .fight_refs import fights
from .refs import fail

if TYPE_CHECKING:
    from .schema import Opening

LineKind = Literal["story", "tap", "find", "level", "body", "fight"]
"""story: a moment told. tap: a plain reply to a card the player runs again and again. find: what a
find turned up. level: a camp or skill level reached. body: a chip's line (hunger, cold, tiredness). fight: a fight's
result."""


def line_keys(o: "Opening") -> list[str]:
    """Every text key a log line can carry: cards' lines, outcomes', chips' on and off, the camp's,
    the start's and the end's, and the fights' pools (the page writes those into the log)."""
    keys = [*o.start_line_keys, *o.end_line_keys]
    for c in o.cards:
        keys += [*c.line_keys, *c.outcome.line_keys, *c.finished.line_keys]
    for t in o.triggers:
        keys += t.outcome.line_keys
    for x in o.offers:
        keys += [*x.line_keys, *(k for a in x.answers for k in a.outcome.line_keys)]
    for ch in o.chips:
        keys += [*([] if ch.on_line_key is None else [ch.on_line_key]), *ch.off_line_keys]
    if o.camp is not None:
        keys += [k for lv in o.camp.levels for k in lv.line_keys]
    for _, f in fights(o):
        keys += [*f.won_line_keys, *f.lost_line_keys, *(f.loss_pool or ())]
    return keys


def check_line_kinds(o: "Opening") -> None:
    """Fails, naming the key, for a log line with no kind."""
    for key in sorted(set(line_keys(o)) - o.line_kinds.keys()):
        fail(f"line {key}", "has no kind in [line_kinds]")
    check_beat_lines(o)
    check_line_doings(o)


def check_line_doings(o: "Opening") -> None:
    """Fails for a `[line_doings]` key that is no story line of the content, or one naming a person with no lane."""
    known, lanes = set(line_keys(o)), {x.id for x in o.lanes}
    for key, entry in o.line_doings.items():
        if key not in known or o.line_kinds.get(key) != "story":
            fail(f"line_doings {key}", "is not a story line")
        for who in (*entry.doings, *(w.person for w in entry.whereabouts)):
            if who not in lanes:
                fail(f"line_doings {key}", f"names {who}, who has no lane")


def check_beat_lines(o: "Opening") -> None:
    """Fails for a beat's first line that is no story line, or one that opens two beats."""
    known, seen = set(line_keys(o)), dict[str, str]()
    for beat, keys in o.beat_lines.items():
        for key in keys:
            if key not in known or o.line_kinds.get(key) != "story":
                fail(f"beat {beat}", f"first line {key} is not a story line")
            if seen.setdefault(key, beat) != beat:
                fail(f"beat {beat}", f"first line {key} also opens {seen[key]}")
