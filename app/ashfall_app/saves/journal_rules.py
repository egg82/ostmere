"""The journal's content as the composer reads it (docs/design/journal.md, "The content's side"): the opening's subjects
and `[journal_habits]` in the composer's types, each line key a subject's source writes resolved to that source, and
each slot's hand and sketch for serving its notes."""
from collections.abc import Iterator
from dataclasses import dataclass

from ..opening.people import mention_keys, moves, told
from ..opening.refs import outcomes
from ..opening.schema import Opening
from ..opening.setting_entries import FadeEntry, JournalHabitsEntry
from ..opening.subject_entries import SlotEntry, SourceEntry, SubjectEntry
from .journal import Band, Fade, Habits, MarkRates, Press, Source, Subject

DIARY_HAND = "ink"
"""The hand of a note whose slot names none: the `days` pages' own."""
LOSS_LOOK_HAND = "pencil"
"""The hand of a loss or fold note (api/contract/loss-lines.txt, "LOSS LINES"): a jotting beside the day's own notes."""


@dataclass(frozen=True)
class LossRunner:
    """A card whose fight carries loss_notes: its id, its lost tally store and its pool."""

    runner: str
    tally: str
    keys: tuple[str, ...]


@dataclass(frozen=True)
class Look:
    hand: str
    sketch: str | None


@dataclass(frozen=True)
class JournalRules:
    subjects: tuple[Subject, ...]
    habits: Habits
    sources: dict[str, tuple[Source, ...]]
    """Each line key a subject's source writes, to those sources: one outcome joining two `line` people writes lines of
    two causes, each a person subject's. A key no subject feeds from is absent."""
    looks: dict[tuple[str, str], Look]
    """(subject, slot) to the hand and sketch its notes are drawn in, for every slot the content gives one, and for each
    loss runner's loss and fold notes."""
    losses: tuple[LossRunner, ...] = ()


def journal_rules(o: Opening) -> JournalRules:
    sources: dict[str, tuple[Source, ...]] = {}
    for s in o.subjects:
        for k in dict.fromkeys(_keys(o, s.source)):
            sources[k] = (*sources.get(k, ()), _source(s.source))
    losses = tuple(LossRunner(c.id, c.fight.lost, tuple(c.fight.loss_notes))
                   for c in o.cards if c.fight is not None and c.fight.loss_notes is not None)
    looks = {(s.id, name): Look(slot.hand or DIARY_HAND, slot.sketch) for s in o.subjects for name, slot in _slots(s)}
    looks |= {(r.runner, slot): Look(LOSS_LOOK_HAND, None) for r in losses for slot in ("loss", "fold")}
    return JournalRules(subjects=tuple(_subject(s) for s in o.subjects), habits=habits(o.journal_habits),
                        sources=sources, looks=looks, losses=losses)


def habits(h: JournalHabitsEntry) -> Habits:
    return Habits(routine=_fade(h.routine), worry=Press(h.worry.base, h.worry.press), crowd=_fade(h.crowd),
                  floor=h.floor, halflife=h.halflife, beat_refresh=h.beat_refresh, lines_start=h.lines_start,
                  lines_floor=h.lines_floor, lines_halflife=h.lines_halflife, busy_ratio=h.busy_ratio,
                  late_rate=h.late_rate, misremember_rate=h.misremember_rate,
                  correct_after_days=h.correct_after_days, marks=MarkRates(**h.marks.model_dump()),
                  marks_most=h.marks_most)


def _fade(f: FadeEntry) -> Fade:
    return Fade(f.base, f.fade)


def _source(s: SourceEntry) -> Source:
    return Source(s.source_kind, s.id, s.way)


def _keys(o: Opening, s: SourceEntry) -> Iterator[str]:
    """The line keys the content writes for this source (subject_checks.py `_writes` holds that there are some)."""
    if s.source_kind == "trigger":
        yield from (k for t in o.triggers if t.id == s.id for k in t.outcome.line_keys)
    elif s.source_kind == "card":
        for c in o.cards:
            if c.id == s.id:
                yield from (*c.line_keys, *c.outcome.line_keys, *c.finished.line_keys)
                if c.fight is not None:
                    yield from (*c.fight.won_line_keys, *c.fight.lost_line_keys)
    elif s.source_kind == "lane":
        line = told(o, "line")
        yield from (k for _, out in outcomes(o) if s.id in line and any(m == (s.way, s.id) for m in moves(out))
                    for k in out.line_keys if o.line_kinds.get(k) == "story")
    else:
        yield from (k for k, (way, _) in mention_keys(o).items() if way == s.way)


def _subject(s: SubjectEntry) -> Subject:
    return Subject(id=s.id, kind=s.kind, source=_source(s.source), away_days=s.away_days, first=_k(s.first),
                   repeat=_k(s.repeat), catchup=_k(s.catchup),
                   mention=tuple(Band(b.at_least, tuple(b.keys)) for b in s.mention),
                   late=_k(s.late), misremember=_k(s.misremember), correction=_k(s.correction), mark=s.mark)


def _k(slot: SlotEntry | None) -> tuple[str, ...]:
    return () if slot is None else tuple(slot.keys)


def _slots(s: SubjectEntry) -> Iterator[tuple[str, SlotEntry]]:
    named = (("first", s.first), ("repeat", s.repeat), ("catchup", s.catchup), ("late", s.late),
             ("misremember", s.misremember), ("correction", s.correction))
    yield from ((name, slot) for name, slot in named if slot is not None)
