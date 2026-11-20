# The daily journal

The Journal's `days` pages are the main character's own diary. They are written the way a person keeps one: firsts,
the people who matter and the turning points go in; routine drops out after a few tellings; entries start long and
frequent and thin as life becomes normal; a busy stretch leaves a gap and then a catch-up; a detail turns up a day late;
now and then something is misremembered and put right later. The Chronicle stays the exact record with a cause on every
line, so nothing the player needs depends on the journal. The pages' look does not change, except for the marks the
days leave on them ("Marks on the page", below); otherwise this note decides what is written on them, never how they
are drawn.

Every habit is decided in code from the save's history, with its numbers in a data file the tuning pass adjusts, and
every draw is seeded, so a save replays the same journal. The content authors the words, per subject and per slot.

The journal belongs to someone who writes things down as they go, so a day's page fills while the day goes on: a note
is written in the step that stores the line it is about, and once on the page it never changes or drops off. Every
choice about a note is made from what is known when it is written ("Written as the day goes", below).

## Fit pass

**What it is an instance of:** a reading of the save's own history, condensed by rules that count what has happened
before. The game already has one: Repeats (`app/ashfall_app/saves/repeats.py`), a pure count over the save's decision
log whose thresholds live in `opening.toml`'s `[repeat_offers]`. The journal is the same shape over the save's lines.

**What already does each part** (`docs/systems.md`):

| Part | Done by | How it is extended |
|---|---|---|
| What happened, when | The save's lines (`save_lines`: key and game second, never pruned), the Chronicle's own source | Read as they are; nothing new is recorded about the past |
| What a line is about | Line causes (`app/ashfall_app/api/line_causes.py`): the card, trigger or skill that writes each key, read from where the content authors it | A journal subject names the cause whose lines feed it, so no line is ever parsed |
| The pages, the notes and their hands and sketches | The Journal sheet and its notes as data (`api/CONTRACT.txt`, "JOURNAL") | The `days` section's notes come from the composed days instead of beat unlocks; creatures and places are untouched |
| Who is written up and who is a mention | People (`decisions.md`, "People, as built"): `line` or `mention`, authored per lane | A `line` person is a subject the journal always writes; a day's mentions are one crowd subject worded by band |
| Seeded draws | Chance (`systems.md`): draws hashed from (seed, stream, key), never a running counter | Its first server-side use. Keys use the save id, as the page's draws do |
| Variety among a slot's lines | The shuffle bag (`app/client/src/game/fights.ts`, `bagged`; the people's bands) | The same rule in the composer, keyed by save, subject and slot |
| When it is written | The save writer (`app/ashfall_app/saves/write.py`), which already stores each step's lines and reads repeats in the step's transaction | Composes the day in progress, and each day the step closed, in the same transaction |

**Patterns.** *Type Object* (Nystrom, read): a subject kind is data carrying its habit numbers, and a subject is an
instance of a kind carrying its slots, so a new kind of thing to write about is content, not code. Kinds are a closed
set chosen by data, the chapter's "fixed set of pre-defined behaviors"; no kind inherits from another. *Dirty Flag*
(read) does not fit: its own test is that the derived data must be hard to update incrementally, and the journal is a
fold over the save's lines, each note decided at its line and stored, which is the chapter's "pay as you go" case.
*Event Queue* does not fit for the reason `docs/design/reminders.md` gives: nothing is decoupled in time, because a note
is composed in the step that stores its line.

**Not a system.** One caller (the save writer; the simulator reads the same module), and nothing to swap. It is a
module beside Repeats.

**Fits into:** the Journal sheet and its notes as data (its `days` section re-sourced), fed by the save's lines through
line causes, written by the save writer in the step's transaction, with draws by Chance's rule; no new system or
`systems.md` row, a module (`app/ashfall_app/saves/journal.py`).

## What it reads, and when it writes

A **game day** is the span the people's mention counts: game seconds `d × 86400` up to the next. A day is **begun** by
the first step that carries the save into it and **ended** by the first step that carries the save past its last second.

### Written as the day goes

A day's page is a fold over its moments, in the order they happen:

1. **The day's start.** If an away gap runs on from an earlier day, the day is a gap from its start and nothing is
   written on it. Otherwise any catch-up owed is written first.
2. **Each line of the day**, in the order the save stored it. A line that feeds a subject is a moment for that subject:
   the first line of the day that shows it, and a later line carrying a key the subject has never held (a change). At
   the moment, the habits below decide whether the subject is written, from the lines up to and including that line
   and the notes already on the page. Once the day has turned into a gap, no more of its moments are written.
3. **The day's end**, once every line of it is known: the crowds' mentions, then the late additions, then the
   corrections due.

Every choice at a moment reads only what came before it in this order, so appending lines to a day only appends notes
to its page. The composer is a pure function: the save id, the day, the save's lines up to now before the day's end
(in the order stored), the days before it, whether the day has ended, the subjects (content) and the habits (data) in;
the day's page as it stands out. A step composes the day still being written, then each day it begins, oldest first,
the last of them still open. Live play, a long advance and a return all reach the same page, because the page is a
function of the lines alone, never of where the steps fell.

The writer keeps one row per begun day (`save_journal`: save id, day, the notes as subject, slot and text key, the gap
and why, the marks, and `through`, the save time it was composed through). The row of the day in progress is extended
by each step that adds to it, and the statement that writes it appends notes and marks and sets a gap that was unset;
it cannot remove or rewrite one. The stored rows are the journal's state: how often a subject has been written is a
count over them. Rows are earned history, like lines, and never pruned.

What is on the page stays. A later change to the habits or the slots applies from the next note composed
(`docs/decisions/saves.md`, "Developed live"): ink does not move when the tuning does. If such a change
lands while a day is open and its recomposed page no longer begins with the notes stored, the stored notes stand and
the day gains nothing more; the next day composes under the new rules. A row stored before notes were written as the
day goes (`through` unset) is a day composed whole, and is never recomposed; the day in progress when this ships is
composed from its start on the save's next step. A save that has no rows composes every day it has begun on its next
step. Slot keys are content ids, kept by the release lock and renamed by `renames.toml` like any other id, so a stored
key always resolves.

### What the day-end composition gave up

Before, a day was composed once, at its end, with the whole day in view. Each habit that compared across the whole day
now decides at its moment:

| Habit | With the whole day in view | Now |
|---|---|---|
| Budget | Musts took their room first; the passing non-musts with the highest care filled the rest | A non-must is written at its moment if it passes and the page holds fewer notes than the budget: first come, first written. A must later in the day is still written, past the budget if need be |
| Busy | A day with more subjects than `busy_ratio × budget` was not written at all | The moment the day's subjects so far pass that count, the rest of the day is a busy gap; what was written before it stays |
| Away | A subject with `away_days` made its whole day a gap | The gap begins at that subject's moment and runs to the end of the last away day |
| Change | Any line of the day with a new key made the subject news that day | A line with a new key is a moment of its own: a subject not yet written that day is weighed again then, at full care |
| Crowd band | Chosen by how many came or went that day | Kept: a crowd is written at the day's end, when the count is known, so crowds come after the day's own notes |
| Late addition | Written on the next day if that day was written | Kept: written at the next day's end, if that day holds a note by then |
| Correction | A must on the first written day at least `correct_after_days` later | At the end of the first such day that does not end in a gap |
| Order | Placed by the first line showing each subject, ties in a second by subject id | Placed by the line that wrote it, ties in a second by the order the lines were stored |
| Marks over `marks_most` | The first in a fixed order of kinds | The first drawn, in the order the notes holding them were written |
| Blank | A day with nothing that passed | Unchanged: a day whose page is empty when it ends; nothing is owed after it |

The journal never reads the player's own comings and goings, only the game's history.

## The habits, in code

Each line feeds at most one **subject**: the authored subject whose source is the line's cause. A line that feeds none
is never journaled. A subject is a **candidate** at its moments (the mention lines of one way are one crowd candidate,
weighed once, at the day's end); what is owed from earlier days (a catch-up, a late addition, a correction) is written
at the day's start or end.

A subject's **kind** is one of a closed set, each with its numbers in data:

| Kind | Fed by | Habit |
|---|---|---|
| `beat` | a turning point or a loss: the lines of a story trigger or a one-off card | **must**: always written, never dropped |
| `person` | a `line` person joining or leaving | **must** |
| `routine` | work and finds that recur | **must** the first time (a first); after that it fades with each telling |
| `worry` | what presses: a trigger's lines the content marks as a plan, a fear or the body's want | grows with each consecutive day it shows, falls away when it stops |
| `crowd` | a day's `mention` people of one way | a short mention at most, worded by how many |

The rules, for day `d`, each applied at the moment it names:

- **Must.** A must candidate is written at its first moment of the day, or in the catch-up after a gap. It is never
  dropped and is not held to the day's budget.
- **Care** (non-must candidates): `base × fade^w`, where `w` is how many times this subject has been told (written by
  any slot but late or correction). A line key of the subject that no earlier line of it has held is a change: at that
  line `w` counts as 0, so routine that changes is news again, and a subject not yet written that day is weighed again
  there; a change is judged against the subject's own earlier lines only. A worry's care is
  `base × (1 + press × (days in a row it has shown − 1))`, capped at 1. Every weighing of a subject on one day uses
  the same roll.
- **Diligence:** `floor + (1 − floor) × 0.5^(s / halflife)`, where `s` is how settled the journal is: the entries
  written so far, less `beat_refresh` for each beat written, never below 0; a note of a subject no longer in the
  content has no kind and takes nothing back. A non-must candidate is written when its roll falls under
  `care × diligence`. Thinning follows how much has been written and what has happened, never the day number.
- **Budget:** the most notes an entry holds, `lines_floor + (lines_start − lines_floor) × 0.5^(s / lines_halflife)`,
  rounded half up, fixed for the day by the days before it. A non-must that passes its roll is written while the page
  holds fewer notes than the budget; musts are written regardless. A late addition or a correction is outside it.
- **Busy:** at a subject's first moment of the day, if the subjects the day has shown so far number more than
  `busy_ratio × budget`, the rest of the day is a busy gap, that subject included. What was written before it stays. A
  full day early on, when the budget is large, is written through; the same day later, when entries are short, breaks
  off. Only the day's own subjects count, never what is owed, so a catch-up cannot make its own day busy.
- **Away:** a subject may carry `away_days`, authored. From its first moment on day `d`, the rest of that day and the
  `away_days − 1` days after it are not written: an away gap. A later day that an away gap covers from its start is a
  gap all day.
- **Blank:** a day whose page is empty when it ends, with no gap. A blank is not a gap: nothing is owed after it.
- **Catch-up:** the first day after a run of gap days that does not open in a gap starts with every must of the run,
  each by its catch-up slot, in the order they happened (by the first line each showed by in the run). A run is the gap
  days back to the first of them, which is the one that broke off after notes were written, or the earliest; a must of
  the run is a subject that showed on a gap day after the gap began there (it has no note of its own that day) and is a
  must now. The run's other candidates are dropped; the Chronicle has them. A must with no catch-up slot cannot be
  caught up and is dropped with them. A catch-up note is a telling for the rest of its day, so a subject it told is not
  a first again that day.
- **Late addition:** each subject written on day `d` that has a late slot draws one under `late_rate`. Its late slot is
  written at day `d + 1`'s end if that day's page holds a note by then, and dropped if it does not.
- **Misremembering:** a subject with a misremember slot, told for the first time on its own day (never in a catch-up),
  draws one under `misremember_rate`; it is then written by its misremember slot instead of its first. Its correction
  is written at the end of the first day at least `correct_after_days` later that does not end in a gap; that wait is
  at least 1, so the correction is always a later note.
- **Which line of a slot:** a slot may hold several lines. A shuffle bag keyed by the save, the subject and the slot
  draws them, its draw count the times that slot has been written for that subject, so the lines take turns and none
  repeats before the bag is empty; a stored key the slot no longer holds does not count toward the bag's draws. A
  crowd is weighed at the day's end, its band chosen by how many came or went that day, as the people's mention bands
  are; on a day fewer came or went than its lowest band, a told crowd has no line and is not written.
- **Order on the page:** the order notes are written, which is the order things happened. Catch-up notes come first,
  then the day's own notes, musts and the rest together, each where the line that wrote it falls; then crowds, by the
  first line each showed by; then late additions and corrections, each by subject id. A day stored whole before notes
  were written as the day goes is read in the order this section gave then (catch-ups, own notes by the first line
  showing each, ties in a second by subject id, late additions, corrections) when a save opens, its row untouched.

## The habits as data

One table, declared once in `opening.toml` beside `[repeat_offers]` (`[journal_habits]`), loaded and range checked
by the content loader. Starting values are set in build step 3 by reading the simulator's readout, not chosen here;
until then the table holds placeholders nothing reads.

| Knob | Meaning |
|---|---|
| `base`, `fade` (per kind) | A kind's care on its first telling, and what each telling multiplies it by |
| `press` (worry) | What each further day in a row adds to a worry's care |
| `floor`, `halflife` | Diligence's lowest share, and the settledness at which it is halfway there |
| `beat_refresh` | How much settledness a written beat takes back |
| `lines_start`, `lines_floor`, `lines_halflife` | The budget at the first entry, its lowest, and how fast it falls |
| `busy_ratio` | The day's subjects so far, over budget, that break the day off as busy |
| `late_rate` | The chance a written subject with a late slot gets its late addition |
| `misremember_rate`, `correct_after_days` | The chance a first telling is misremembered, and the shortest wait for its correction |
| `marks` (per mark kind), `marks_most` | The chance a mark the day holds is drawn on its page, and the most event marks one day keeps |

## Determinism

Each roll is a fixed hash of `save id | journal | day | subject | purpose` (purpose one of write, late, misremember;
a mark's roll is keyed by its kind in the subject's place, purpose mark), mapped to [0, 1): the SHA-256 of the key's UTF-8 bytes joined by `|`, its first eight bytes big-endian over 2^64, never Python's salted `hash()`. No draw depends on a
counter, so a new subject or a new purpose shifts no other roll. The shuffle bag's position is a count over the stored
rows. With the stored rows, the history, the content and the habits fixed, a day composes to the same notes on every
build and every pod, and a day composed with more of its lines only adds notes after those it had; storing each note
keeps it fixed after the content or the habits change. The composer runs only on the server, so no rule exists twice.

## The content's side

Content declares journal subjects in the chapter files, each with an id, a kind, a source (the cause whose lines feed
it: a trigger, a card, a lane's coming or going, or a way's mentions), an optional `away_days`, and its slots. Each slot
is one or more text keys in the character's journal voice (`decisions.md`, "The journal is the player-character's own
voice"), with an optional hand and sketch as a note has today.

| Slot | Written | Who needs it |
|---|---|---|
| `first` | the first telling | every subject |
| `repeat` | later tellings; several lines take turns | optional: with none, a subject is written once |
| `catchup` | in a catch-up, short enough to stand in a list of the gap's events | every `beat`, `person` and `routine` subject |
| `mention` | a crowd's later tellings (its first is `first`), one set per band of how many | every crowd subject |
| `late` | the day after, a detail the first telling left out | optional |
| `misremember` and `correction` | a first telling with a detail wrong, and a later note putting it right | optional, always together |

Each line is written as if it is the only one: what this person writes on this occasion. No slot, rule or prompt says
how often something happens, or that the writer grows lazy, since the code decides that and a line cannot keep a rate.
Numbers are words, as every note's are (the loader refuses a digit), and appear only where the number is the news.
A misremembering and its correction are authored together, so the correction is canon and the wrong version never
contradicts it.

A generic example, invented for this note: a subject `kettle` of kind `routine`. `first`: "the kettle's handle came off
in my hand. wrapped it in rag." `repeat`: "kettle." and "the rag is holding." `late`: "forgot. the rag was the last of
the blanket."

The loader's checks name ids and fields, never text: every subject has a first slot; every `beat`, `person` and
`routine` subject has a catch-up slot; misremember and correction come together, and only on a `routine` subject,
never a `beat`, `person` or `worry` (owner, 2026-11-14: the journal never misleads about the story); a source names a
cause the content writes a kept line of (a fight's won and lost lines are drawn by the page, never saved), and no cause feeds two subjects; each `line` person has a person subject for each way that
moves them; every slot key has text; no entry is a `days` page. Each check is shown red on a planted chapter first. A
cause is a source, so two people one outcome joins are two causes; only a `person` feeds from a lane and only a
`crowd` from a way's mentions; and a beat that lands by either of two triggers has a subject for each.

## What the page draws

The page draws written days the way a notebook fills (owner, 2026-11-14): each day's notes in order under its day's
heading, days running on down a `days` page, with the hands and sketches the slots name, in today's page look. A day
begins on the page in hand if its heading and first note fit there; a note that does not fit begins a new page, headed
again by its day, so a day still being written runs on over the page instead of leaving it. Whether a note fits is a
fixed measure of its words, rows of the hand at the desktop page's width (`opening-screen.md`, "The days pages"), never
the window, so the same days are the same pages on every device and width, and a page, once a later one is begun,
never changes. Opened carries every written day, the day in progress with the notes it has so far; Step carries each
day it added to, whole, and the page takes the copy with more notes. A day added to while its page is open grows on
it.
`SavePresentation.newest_day_read` is the newest day the player has turned to, which only grows; a day past it is
unread and dots the Journal button. The creatures and places sections, their unlocks and their numbers are unchanged.
The `days` entries and notes that were the days pages before the written days are retired through the release lock
(`renames.toml`); a save keeps their unlocks, and their loader-made triggers go (engine `DESIGN.txt`, "Retired").

## Marks on the page

Pages that are too clean don't read like a journal (owner, 2026-11-14). This amends "the journal pages are kept exactly
as they are" (`redesign.md`, "Book"): the parchment, the hand and the drawings stay; marks are added, in two layers.

**Wear**, on every page of the journal (days, creatures and places): one light mark, now and then two, from a set of everyday
ones (a stray smudge, a faint thumbprint, specks where the ink skipped, a ring, a crease, scratches). Which, and
where, are draws keyed by the save and the page's id, so a page looks the same each time it is opened and no two
pages match. Wear has no history and no rate to keep, so the page draws it alone.

Every mark is turned to any angle, mirrored, scaled and faded by its own seeded draw, and one page never carries the same
art twice while another of its kind is unused; a forced repeat is mirrored and turned against the first and lies far from it.

**Event marks**, rarer and stronger, come from what the day held, never at random:

| Mark | Caused by |
|---|---|
| `blood` | a subject the content marks `blood`: a fight, an injury, a kill |
| `soot` | a subject marked `soot`: a day at the fire, smoke, burnt ground |
| `water` | a subject marked `water`: rain, frost and thaw, a crossing |
| `mud` | a subject marked `mud`: digging, building, tracks, a long day outside |
| `smudge` | a day that opens with a catch-up: the entry written in a hurry after a busy or away stretch |

A subject's mark is an explicit field where the content authors it (`mark`, optional), never read from its words. The
composer chooses a day's marks as its notes are written (statement 21 of `saves/journal.py`): when a day's own or
catch-up note holds a kind, that kind passes a seeded roll under its rate in `[journal_habits.marks]`, and a day keeps
the first `marks_most` drawn. Marks are stored with the day as they are drawn, so like the ink they never change once
there. Late additions and corrections are about another day and cause none. A day that runs over two pages carries its
marks on both.

**Legibility.** A mark never covers the words. The page places each mark at a seeded spot, keeps it only where its box
crosses no line of words, no day heading and no drawing, and otherwise tries the next spot; one that finds no room is
not drawn. So marks sit in the margins, the gaps between days and the room beside short lines, often bleeding off an
edge. They are drawn with the parchment's own multiply blend, wear at about a third of full strength and event marks
at about four fifths, and a page carries at most two event marks besides its wear; no mark sits on another, so they
never pile into one corner. A place is chosen against where the words lie at the page's size, so a page is marked the
same each time at one size; only the newest days page gains words, so only its marks can move, to stay off them. A
page whose last day runs on to the next page can still gain that day's marks while the day is being written.

**The art** is Starshine Scribbles' "Stains and Damage" (CC BY 4.0, credited in the game), bought art outside the repo:
`tools/pagemarks.py` crops, cleans, recolours (blood is the splatter recoloured) and scales the overlays into
`journal/marks/` on the assets volume with a manifest of each kind's variants, and the page picks a variant by seed.

## What must stay true

- Every must subject is written exactly once (by its first, its catch-up or its misremember slot) within its gap's
  length plus a day.
- Every misremembering is followed by exactly one correction, at least `correct_after_days` later, unless the history
  ends first.
- A late addition appears only on the day after its subject was written.
- A note, once stored, is never removed, moved or changed; a day's marks only grow, and its gap, once set, stays.
- A day composed with more of its lines begins with the notes it had with fewer.
- Stepping a save in many small steps, in one long advance, or on a return stores the same rows.
- Changing the habits or the slots leaves every stored note unchanged.
- Within one subject and slot, no line repeats before every line of the slot has been drawn.
- A new subject's lines change no other subject's rolls.

## How it is tested

- **A blind contract suite** for the composer: an agent that did not write it gets the function's signature and this
  note's rules, and writes behaviour tests from them (first, repeat, change, busy, away, blank, catch-up, late,
  misremember and correction, budget, order). The implementer adds no duplicate.
- **Property tests** (Hypothesis) over generated histories: each invariant above; thinning (with steady activity, the
  mean notes per entry and the share of days written fall from the first half of a long history to the second); and
  each rate (over many save ids, the observed share of late additions and misrememberings sits within a binomial bound
  of the data's rate). A fast profile on every push, a deep one nightly.
- **A planted-mutant list** (`MUTANTS.txt`, with the script that plants them): the must bypass removed, diligence keyed
  to the day number, Python's `hash()` for the roll, `w` counted from lines instead of written notes, a late addition
  kept across a blank day.
- **Append-only, in the composer:** for generated histories, a day composed with its lines cut after any line, open,
  is a prefix of the day composed with all of them, and of the ended day.
- **The writer's path:** a save advanced in many small steps through its days and the same save advanced in one jump
  store identical rows; every note a small step stored is still there, unchanged, at every later step; a return's
  catch-up stores what live play stores; a habits change after composition leaves the stored notes alone; rows stored
  whole before this model are never recomposed.
- **A simulator readout**, nightly and never failing (`decisions.md`, "Tuned means checked"): per route and game week,
  days written, notes per entry, gaps by cause, catch-ups, late additions and corrections. The tuning pass reads it.
- **The page** gets render-and-look, never a snapshot.

## Rejected, and why

- **The Chronicle as the lossy journal.** The owner chose to keep the Chronicle exact, a cause on every line; a record
  that skips is no record, and the player would lose facts to a habit.
- **An LLM writing entries freely at runtime.** A stateless call cannot keep a rate, so thinning, gaps and the rare
  misremembering would come out at whatever rate the model drifts to; it cannot see what it wrote before without the
  whole journal in every call; its output repeats in shape at volume (`docs/research/llm-writing.md`); and a
  misremembering it invents is not canon, so the correction could contradict the story. The Writer may later draft
  slot lines offline, as content that is reviewed like any other.
- **A fixed thinning schedule by day number.** The game's length is set by play, so a day number lands on different
  story moments in different saves; it would thin through a turning point and could not pick up after one.
- **Composing on the page.** The page holds the last 200 lines, and a first is only a first against the whole history;
  the simulator, which the tuning pass reads, is Python; and the client has no property-test library.
- **Composing afresh on every read instead of storing.** Any change to the habits or the slots would rewrite pages the
  player has already read.
- **Composing a day once, at its end** (this note's first model). A page of things that happened hours before, filled
  all at once, is not how someone who writes as they go keeps a journal.
- **A provisional page, rewritten at the day's end with the whole day in view.** It would keep the budget's choice by
  care and a whole busy day, but notes the player has read would vanish or change.
- **Composing only each step's own lines, behind a stored cursor of lines composed.** The page would depend on every
  step having composed (a path that stores lines without composing would leave a hole), and the cursor is one more
  thing to keep in step; recomposing the day in progress from its lines is pure and lands on the same notes.
- **Weighing a crowd at its first line.** Its band needs the day's count, which is only known at the day's end.
- **Moving a day that outgrows its page to the next page whole.** Notes the player has read would leave the page they
  were read on.
- **Recomposing an open day under new rules and patching its page.** The stored notes would change; the day keeps them
  and gains nothing more instead.
- **`days` notes as engine unlocks with habit gates.** The engine takes no chance (`systems.md`, the engine's contract),
  and encoding skips and catch-ups as gates multiplies triggers per subject and slot to store a presentation in engine
  state.
- **Gaps from the player's absence.** Attention earns nothing (`decisions.md`, "Fun, but never vying for attention"), a
  journal that goes quiet whenever the player is away reads as guilt, and absence is not in the kept history: decisions
  are pruned after thirty days and visits are page-written presentation, so a replay would differ.
- **Habits on the creatures and places pages.** Those are the perfect-information layer, exact once known.
- **Striking through the misremembered note on its old page.** A page changing after it is written is not how ink
  works, and it would be a new look; the correction is a later note.
- **A count threshold for who is written up.** Who matters is authored per person (`decisions.md`, "People, as built").
- **Paging the days by the window's height.** A phone and a desktop would break the same days onto different pages, a
  page would reflow when the window changed, and a page once read could change; a fixed measure of the words keeps
  every page put.
- **Keeping the old `days` notes beside the written days.** Two sources for one section would draw each beat twice;
  the beat subjects' first slots already hold those notes' words.

## Build order

Each step is one PR with its tests, proven able to fail.

1. **This note and the decision** (docs only).
2. **Subjects in the content.** The subject and slot schema in the chapter files, the loader's checks (each red on a
   planted chapter), and `[journal_habits]` loaded and range checked. Beat subjects for today's `days` notes, their
   first slots reusing those notes' text, and person subjects for the `line` people's comings and goings. Subjects still
   missing a first or catch-up slot are held by id until step 6 writes them (`AWAITING_SLOTS`, which only shrinks).
   Nothing reads them yet; the journal is unchanged.
3. **The composer and its readout.** The pure module with the hashed roll and the shuffle bag, the blind contract suite,
   the property tests, the mutant list, and the nightly simulator readout. Starting habit values are set from the
   readout. Nothing calls it from the API yet.
4. **Stored and served.** The `save_journal` table and migration; composition in the step's transaction for every day
   the step closes (a save with no rows composes all of its closed days); Opened and Step carry the written days;
   `SavePresentation`'s newest day turned to; `CONTRACT.txt` "JOURNAL" rewritten for the `days` section; subject ids and
   slot keys taken into the release lock. Tests: the
   day-by-day and one-jump saves match; a habits change leaves stored rows alone; one row per day under two writers.
5. **The page.** The `days` section drawn from the served days in today's layout, the dot from the newest day turned
   to; the `days` notes' unlocks retired from the page, and their released `note_` triggers handled through the
   release lock. Render-and-look. After the Book (PR #51) lands.
6. **The shipped chapters' slots.** People who matter, routine, worries, catch-ups, late additions and a
   misremembering or two, through a fresh agent's voice pass; the readout read before and after.
