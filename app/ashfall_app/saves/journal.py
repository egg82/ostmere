"""The journal composer (docs/design/journal.md): the notes the `days` pages write for one game day, chosen from the
save's history by the writer's habits, as the day goes. Pure: no engine, no database, no clock; every draw is a hash of
its own key (`roll`, and the bag's shuffle in statement 19). The save writer stores each result as the day's
`save_journal` row, extending the row of a day still open, and passes the stored rows back in as `composed`.

Terms. Game day `d` is game seconds `[d * 86400, (d + 1) * 86400)`. A line *shows* subject S on day d when its `at` is
in day d and its `source` equals S's `source`. The day's lines run by `at`, ties in the order `lines` holds them (the
order the save stored them). A *moment* of S on day d is the first line that shows S that day, or a later one whose key
no earlier line of S held (a *change*). A *telling* of S is a note of S by its first, repeat, catchup, misremember or
mention slot (never late or correction); `w(S)` is the number of tellings of S before the moment, in `composed` and on
the day's page so far. S is *told* once `w(S) > 0`. A day is *written* when its notes are non-empty. `s`, the
settledness, is the number of written days in `composed` less `beat_refresh` for each note in `composed` whose subject
is a `beat` in `subjects` (a note of a subject no longer in `subjects` has no kind and takes nothing back; its day still
counts as written), never below 0. `round_half_up(x)` is `floor(x + 0.5)`. A crowd is told first by `first`, then by
`mention`, which stands in for its `repeat`: the band whose `at_least` is the highest at most that day's count of its
lines. On a day that count is below every band's `at_least`, a told crowd has no slot to tell it by and is not written;
it still shows (statement 14).

A day is composed in three parts: its start (an away gap running into it, else the catch-ups owed), its moments in order,
and, once `ended`, its end (its crowds, then late additions, then corrections). A day *breaks off* into a gap at a moment
(statements 13, 14); no later moment of it writes, and it has no end.

The contract, each statement checkable from inputs and output alone:

Shape
 1. The same arguments give an equal result, in any process (no salted `hash()`, no clock, no global state). So
    composing a day once with all its lines or again and again as they arrive stores the same row (statement 22).
 2. The result's `day` is the argument `day`. A day with `gap` set holds only notes written before it broke off.
 3. Every note's subject is in `subjects`, its key is in that subject's slot named by the note's `slot` (for `mention`,
    in one of its bands' keys), and that slot is non-empty.
 4. No subject has two notes on one day, except a catch-up note beside its own day's note, a late addition or a
    correction.
 5. Adding or removing a line whose source matches no subject never changes the result.
 6. With the same `composed`, adding a subject and lines showing only it never changes `roll` for another subject, nor
    which other subjects pass their write roll (the budget and busy may still change: they count notes and subjects).

Must
 7. A `beat` or `person` subject that shows on day d and has a slot to tell it by is a must on day d; so is a `routine`
    subject that shows and is not yet told. A subject already told with an empty `repeat` is never written again by
    first, repeat, catchup or misremember slot ("written once"), must or not. A subject that showed on a gap day with no
    note of it that day is a must of that gap when it would be one on its own day and its `catchup` slot, which writes
    it, is non-empty; one with an empty `catchup` is dropped with the gap run's other subjects.
 8. Every must is written at its first moment of the day unless the day broke off before it: by `first` if not told,
    else `repeat` (a `routine` first by `misremember` instead when its misremember roll passes, statement 17). Musts are
    not limited by the budget.
 9. The run of gap days ending on day d - 1 reaches back to the first of them, the one with notes or else the earliest.
    Every must of the run is written exactly once, by `catchup`, at the start of day d when day d does not open in an
    away gap (else the run goes on); the run's other subjects are never written later. A catch-up note is a telling
    for the rest of its day.

Care, diligence, budget
10. Care of a `routine` or `crowd` subject is `base * fade ** w`, its kind's numbers, with `w = 0` at a change (for a
    crowd, weighed at the day's end, when any of the day's lines of it has a key no line of it held before the day's
    start; lines of other subjects, or of none, never count). Care of a `worry` is
    `min(1, base * (1 + press * (r - 1)))`, `r` the consecutive days ending at d on which it showed.
11. Diligence is `floor + (1 - floor) * 0.5 ** (s / halflife)`. A non-must not yet written that day passes at a moment
    when `roll(save_id, d, subject, "write") < care * diligence` (strict: a product of 0 never passes, of 1 always does).
    A crowd is weighed once, at the day's end.
12. The budget is `round_half_up(lines_floor + (lines_start - lines_floor) * 0.5 ** (s / lines_halflife))`. A passing
    non-must is written only while the day's page holds fewer notes than the budget (first come). Diligence and budget
    depend on `composed`, never on `day` itself.

Gaps and blanks
13. Away: a subject with `away_days = k > 0` breaks day d off at its first moment there, and days d + 1 .. d + k - 1 are
    an away gap from their start, with no notes. Away is judged before busy at a moment.
14. Busy: at a subject's first moment of the day, when the subjects the day has shown so far, it included, number more
    than `busy_ratio * budget`, the day breaks off with `gap = "busy"`. What is owed from earlier days (catch-up, late
    addition, correction) is not counted.
15. Blank: an ended day with no gap and no notes. Nothing is owed after a blank.

Late additions, misremembering
16. A subject with a non-empty `late` slot, written on day d by any slot but late or correction, gets a late note at
    day d + 1's end when `roll(save_id, d, subject, "late") < late_rate` and the page holds a note or a correction is
    due; never on any other day.
17. A subject with non-empty `misremember` and `correction` slots, told for the first time on its own day (not in a
    catch-up), is written by `misremember` instead of `first` when `roll(save_id, d, subject, "misremember") <
    misremember_rate`. Its correction is written at the end of the first day at least `correct_after_days` later that
    does not break off, and exactly one correction follows each misremembering. `correct_after_days` is at least 1 (the
    loader's range check), so the correction is always on a later day than its misremembering.

Order and lines
18. Notes stand in the order they are written: catch-up notes, by the earliest `at` among the lines that showed each on
    a run day it has no note of, ties by subject id; then the day's own notes, each at the moment that wrote it; then crowds, by their first moments; then
    late additions, then corrections, each by subject id.
19. Within one subject and slot (for `mention`, within one band), the n-th note drawn (n counted over `composed` and the
    page so far) completes a round of the slot's keys before any key repeats: notes with equal `n // len(keys)` are
    different keys. n counts only stored notes whose key the slot still holds: a retired key does not advance the
    round. Which of a round's unused keys comes next is a shuffle keyed by save, subject, slot (and band) and round,
    never a counter.

Forward only
20. `composed` is read as given, never recomposed: rows stored under other habits or subjects count as they stand, so
    changing the habits or the slots changes only notes not yet composed.

Marks
21. A day's `marks` are kinds of mark, each at most once, in the order drawn. A note by a slot other than `late` or
    `correction` *holds* its subject's `mark` (if any), and a `catchup` note also holds `smudge`. When a note is written,
    each kind it holds that the page does not carry is drawn when `roll(save_id, d, kind, "mark") <
    getattr(habits.marks, kind)` (the kind in the subject's place) and the page carries fewer than `marks_most`. Marks
    never change which notes a day has, nor their order.

Written as the day goes
22. With `ended` false the day has no end: no crowd, late addition or correction. A day composed with `lines` holding
    more of its lines (appended in order), or with `ended` true, begins with the notes and marks it had, and keeps its
    gap once set.
"""
import hashlib
from dataclasses import dataclass
from typing import Literal

type SubjectKind = Literal["beat", "person", "routine", "worry", "crowd"]
type SourceKind = Literal["trigger", "card", "lane", "mentions"]
type Way = Literal["joined", "left"]
type SlotName = Literal["first", "repeat", "catchup", "mention", "late", "misremember", "correction"]
type Gap = Literal["busy", "away"]
type Purpose = Literal["write", "late", "misremember", "mark"]
type MarkKind = Literal["blood", "soot", "water", "mud", "smudge"]

MARK_KINDS: tuple[MarkKind, ...] = ("blood", "soot", "water", "mud", "smudge")
"""Every kind of mark, in the order a day's marks are kept (statement 21). `smudge` is the day's own (a catch-up); the
others are a subject's `mark`."""

DAY_S = 86400


@dataclass(frozen=True)
class Source:
    """The cause whose lines feed a subject, as the content authors it (opening SourceEntry): a trigger's or card's
    lines (`id`), a `line` person's coming or going (`id` the lane, and `way`), or one way's mention lines (`way`)."""

    kind: SourceKind
    id: str | None = None
    way: Way | None = None


@dataclass(frozen=True)
class Line:
    """One of the save's lines: its key, its game second, and its cause resolved to a source (None: feeds nothing)."""

    key: str
    at: int
    source: Source | None


@dataclass(frozen=True)
class Band:
    """A crowd's lines for a day on which at least `at_least` of its way came or went."""

    at_least: int
    keys: tuple[str, ...]


@dataclass(frozen=True)
class Subject:
    """One thing the journal writes about (opening SubjectEntry). An empty slot is an absent one."""

    id: str
    kind: SubjectKind
    source: Source
    away_days: int = 0
    first: tuple[str, ...] = ()
    repeat: tuple[str, ...] = ()
    catchup: tuple[str, ...] = ()
    mention: tuple[Band, ...] = ()
    late: tuple[str, ...] = ()
    misremember: tuple[str, ...] = ()
    correction: tuple[str, ...] = ()
    mark: MarkKind | None = None
    """The mark a day that writes this subject may carry (statement 21); never `smudge`."""


@dataclass(frozen=True)
class Fade:
    base: float
    fade: float


@dataclass(frozen=True)
class Press:
    base: float
    press: float


@dataclass(frozen=True)
class MarkRates:
    """Each mark kind's chance of being drawn on a day that holds it (statement 21)."""

    blood: float = 0.0
    soot: float = 0.0
    water: float = 0.0
    mud: float = 0.0
    smudge: float = 0.0


@dataclass(frozen=True)
class Habits:
    """opening.toml's [journal_habits] (docs/design/journal.md, "The habits as data")."""

    routine: Fade
    worry: Press
    crowd: Fade
    floor: float
    halflife: float
    beat_refresh: float
    lines_start: int
    lines_floor: int
    lines_halflife: float
    busy_ratio: float
    late_rate: float
    misremember_rate: float
    correct_after_days: int
    marks: MarkRates = MarkRates()
    marks_most: int = 0


@dataclass(frozen=True)
class Note:
    """One note on a day's page: the subject, the slot it was written by, and the text key drawn from that slot."""

    subject: str
    slot: SlotName
    key: str


@dataclass(frozen=True)
class ComposedDay:
    """One stored `save_journal` row: written when `notes` is non-empty; a gap (and why) when `gap` is set; the marks
    its page carries (statement 21)."""

    day: int
    notes: tuple[Note, ...]
    gap: Gap | None
    marks: tuple[MarkKind, ...] = ()


def roll(save_id: int, day: int, subject: str, purpose: Purpose) -> float:
    """The draw for one subject's purpose on one day, in [0, 1): the SHA-256 of the UTF-8 bytes of
    f"{save_id}|journal|{day}|{subject}|{purpose}", its first eight bytes read big-endian, divided by 2**64. Depends on
    nothing else, so no draw shifts another."""
    digest = hashlib.sha256(f"{save_id}|journal|{day}|{subject}|{purpose}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def compose_day(
    save_id: int,
    day: int,
    lines: tuple[Line, ...],
    composed: tuple[ComposedDay, ...],
    subjects: tuple[Subject, ...],
    habits: Habits,
    ended: bool = True,
) -> ComposedDay:
    """Compose game day `day` of save `save_id` as it stands (the module docstring's contract).

    `lines`: the save's lines known so far with `at < (day + 1) * DAY_S`, in the order stored. `composed`: the stored
    rows for days 0 .. day - 1, oldest first. `subjects`: the content's, ids distinct and no two with one source.
    `ended`: every line of the day is known, so its end is composed.
    Raises ValueError when a line is at or past the day's end, or `composed` is not exactly days 0 .. day - 1 in order.
    """
    from .journal_composer.day import compose  # the implementation imports this module's types

    return compose(save_id, day, lines, composed, subjects, habits, ended)
