"""The loader's checks on the journal's subjects (docs/design/journal.md, "The content's side"), each naming ids and
fields, never text: a source names a cause the content writes, and no cause feeds two subjects; the slots each kind
needs are there, misremember and correction come together and only on a routine; every slot key has text; each
`line` person has a person subject for each way that moves them; every days note has a beat subject whose first slot
holds it. Raises ValueError naming the subject (refs.fail)."""
from typing import TYPE_CHECKING

from .journal_checks import check_sketch
from .people import mention_keys, moves, told
from .people_checks import check_band_list
from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening
    from .subject_entries import SlotEntry, SourceEntry, SubjectEntry

AWAITING_SLOTS: frozenset[str] = frozenset({
    "s_b11", "s_b12", "s_b13", "s_b14", "s_n5_joined", "s_n6_joined", "s_n7_joined",
})
"""Shipped subjects declared before their lines are written: the first and catch-up slots are not required of them.
tests/opening/test_journal_subjects.py holds this to exactly the shipped subjects still missing one."""

SHAPES: dict[str, tuple[bool, bool, str]] = {
    "trigger": (True, False, "an id"), "card": (True, False, "an id"), "lane": (True, True, "an id and a way"),
    "mentions": (False, True, "a way and no id"),
}
"""Whether each kind of source names an id and a way, and how a fault says so."""

CATCHUP_KINDS = frozenset({"beat", "person", "routine"})
"""The must kinds, whose subjects a catch-up names after a gap."""


def check_subjects(o: "Opening") -> None:
    sources: dict[tuple[str, str | None, str | None], str] = {}
    for s in o.subjects:
        _check_source(o, s)
        key = (s.source.source_kind, s.source.id, s.source.way)
        if key in sources:
            fail(f"subject {s.id}", f"feeds from {_named(s.source)}, as subject {sources[key]} does")
        sources[key] = s.id
        _check_slots(o, s)
    _check_people(o, set(sources))
    _check_days_notes(o)


def _check_source(o: "Opening", s: "SubjectEntry") -> None:
    src, where = s.source, f"subject {s.id}"
    names_id, names_way, words = SHAPES[src.source_kind]
    if (src.id is not None, src.way is not None) != (names_id, names_way):
        fail(where, f"a {src.source_kind} source names {words}")
    if (s.kind == "person") != (src.source_kind == "lane") or (s.kind == "crowd") != (src.source_kind == "mentions"):
        fail(where, "only a person feeds from a lane's coming or going, and only a crowd from a way's mentions")
    if not _writes(o, src):
        fail(where, f"its source, {_named(src)}, is not a cause the content writes lines of")


def _named(src: "SourceEntry") -> str:
    return " ".join(x for x in (src.source_kind, src.id, src.way) if x is not None)


def _writes(o: "Opening", src: "SourceEntry") -> bool:
    """Whether the content writes lines of this cause: an authored trigger or a card with lines, a `line` person moved
    that way, a mention person moved that way."""
    if src.source_kind == "trigger":
        return any(t.id == src.id and t.outcome.line_keys for t in o.triggers)
    if src.source_kind == "card":
        return any(c.id == src.id and (c.line_keys or c.outcome.line_keys or c.finished.line_keys
                                       or (c.fight is not None and (c.fight.won_line_keys or c.fight.lost_line_keys)))
                   for c in o.cards)
    if src.source_kind == "lane":
        return src.id in told(o, "line") and any(m == (src.way, src.id) for _, out in outcomes(o) for m in moves(out))
    return any(way == src.way for way, _ in mention_keys(o).values())


def _check_slots(o: "Opening", s: "SubjectEntry") -> None:
    where = f"subject {s.id}"
    if s.id not in AWAITING_SLOTS:
        if s.first is None:
            fail(where, "has no first slot")
        if s.kind in CATCHUP_KINDS and s.catchup is None:
            fail(where, f"is a {s.kind} and has no catchup slot")
    if s.kind == "crowd":
        if not s.mention:
            fail(where, "is a crowd and has no mention bands")
        check_band_list(o, f"{where} mention", s.mention)
    if (s.misremember is None) != (s.correction is None):
        fail(where, "has one of misremember and correction: they are written together")
    if s.misremember is not None and s.kind != "routine":
        fail(where, f"is a {s.kind}, and only a routine is misremembered")
    for name, slot in _slots(s):
        for key in slot.keys:
            if key not in o.text:
                fail(where, f"{name} key {key!r} is not in text")
        if slot.sketch is not None:
            check_sketch(f"{where} {name}", slot.sketch)


def _slots(s: "SubjectEntry") -> list[tuple[str, "SlotEntry"]]:
    named = [("first", s.first), ("repeat", s.repeat), ("catchup", s.catchup), ("late", s.late),
             ("misremember", s.misremember), ("correction", s.correction)]
    return [(name, slot) for name, slot in named if slot is not None]


def _check_people(o: "Opening", sources: set[tuple[str, str | None, str | None]]) -> None:
    line = told(o, "line")
    for where, out in outcomes(o):
        for way, lane in moves(out):
            if lane in line and ("lane", lane, way) not in sources:
                fail(where, f"{way} {lane}, a line person, and no person subject feeds from it")


def _check_days_notes(o: "Opening") -> None:
    days = {e.id for e in o.entries if e.section == "days"}
    retold = {k for s in o.subjects if s.kind == "beat" and s.first is not None for k in s.first.keys}
    for n in o.notes:
        if n.entry in days and n.id not in retold:
            fail(f"note {n.id}", "is a days note, and no beat subject's first slot holds it")
