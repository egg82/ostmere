# The daily journal

The Journal's `days` pages are the main character's own diary. They are written the way a person keeps one: firsts,
the people who matter and the turning points go in; routine drops out after a few tellings; entries start long and
frequent and thin as life becomes normal; a busy stretch leaves a gap and then a catch-up; a detail turns up a day late;
now and then something is misremembered and put right later. The Chronicle stays the exact record with a cause on every
line, so nothing the player needs depends on the journal. The pages' look does not change: this note decides what is
written on them, never how they are drawn.

Every habit is decided in code from the save's history, with its numbers in a data file the tuning pass adjusts, and
every draw is seeded, so a save replays the same journal. The content authors the words, per subject and per slot.

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
| When it is written | The save writer (`app/ashfall_app/saves/write.py`), which already stores each step's lines and reads repeats in the step's transaction | Composes each game day the step closed, in the same transaction |

**Patterns.** *Type Object* (Nystrom, read): a subject kind is data carrying its habit numbers, and a subject is an
instance of a kind carrying its slots, so a new kind of thing to write about is content, not code. Kinds are a closed
set chosen by data, the chapter's "fixed set of pre-defined behaviors"; no kind inherits from another. *Dirty Flag*
(read) does not fit: its own test is that the derived data must be hard to update incrementally, and the journal is a
fold over days, composed once per day and stored, which is the chapter's "pay as you go" case. *Event Queue* does not
fit for the reason `docs/design/reminders.md` gives: nothing is decoupled in time, because a day is composed when a step
crosses its end.

**Not a system.** One caller (the save writer; the simulator reads the same module), and nothing to swap. It is a
module beside Repeats.

**Fits into:** the Journal sheet and its notes as data (its `days` section re-sourced), fed by the save's lines through
line causes, written by the save writer in the step's transaction, with draws by Chance's rule; no new system or
`systems.md` row, a module (planned: `app/ashfall_app/saves/journal.py`).

## What it reads, and when it writes

A **game day** is the span the people's mention counts: game seconds `d × 86400` up to the next. A day is **composed**
once its last second has passed, by whichever step first carries the save past it. Live, that is the first advance after
the day ends; on a return, the step that catches up composes every day it closed, oldest first. Composition reads only
the save's lines with `at` before the day's end and the days already composed, so a day comes out the same whichever
step composes it: live and on return are one path.

The composer is a pure function: the save id, the day, that day's lines, the days composed before it, the subjects
(content) and the habits (data) in; the day's notes out. The writer stores the result as one row per composed day,
written or not (`save_journal`, planned: save id, day, the notes as subject, slot and text key, and whether the day was
a gap and why). The stored rows are the journal's state: how often a subject has been written is a count over them, and
the next day to compose is the one after the newest row. Rows are earned history, like lines, and never pruned.

Stored once, a day never changes. A later change to the habits or the slots applies from the next composed day on
(`decisions.md`, "Developed live, forward-only by preference"): ink does not move when the tuning does. A save that has
no rows when this ships composes all of its closed days on its next step. Slot keys are content ids, kept by the
release lock and renamed by `renames.toml` like any other id, so a stored key always resolves.

The journal never reads the player's own comings and goings, only the game's history.

## The habits, in code

Each line of a closed day feeds at most one **subject**: the authored subject whose source is the line's cause. A line
that feeds none is never journaled. The day's **candidates** are its subjects, each once (the mention lines of one way
are one crowd candidate), plus anything owed from earlier days (a catch-up, a late addition, a correction).

A subject's **kind** is one of a closed set, each with its numbers in data:

| Kind | Fed by | Habit |
|---|---|---|
| `beat` | a turning point or a loss: the lines of a story trigger | **must**: always written, never dropped |
| `person` | a `line` person joining or leaving | **must** |
| `routine` | work and finds that recur | **must** the first time (a first); after that it fades with each telling |
| `worry` | what presses: a trigger's lines the content marks as a plan, a fear or the body's want | grows with each consecutive day it shows, falls away when it stops |
| `crowd` | a day's `mention` people of one way | a short mention at most, worded by how many |

The rules, in the order the composer applies them for day `d`:

- **Must.** A must candidate is written on its own day, or in the catch-up after a gap. It is never dropped and is not
  held to the day's budget.
- **Care** (non-must candidates): `base × fade^w`, where `w` is how many times this subject has been written. A line key
  of the subject that the save's history has never held before is a change, and that day `w` counts as 0, so routine
  that changes is news again. A worry's care is `base × (1 + press × (days in a row it has shown − 1))`, capped at 1.
- **Diligence:** `floor + (1 − floor) × 0.5^(s / halflife)`, where `s` is how settled the journal is: the entries
  written so far, less `beat_refresh` for each beat written, never below 0. A non-must candidate is written when its
  roll falls under `care × diligence`. Thinning follows how much has been written and what has happened, never the day
  number.
- **Budget:** the most notes an entry holds, `lines_floor + (lines_start − lines_floor) × 0.5^(s / lines_halflife)`,
  rounded. Musts first, then the rest by care, ties by roll.
- **Busy:** a day whose candidates number more than `busy_ratio × budget` is not written: a busy gap. A full day early
  on, when the budget is large, is written; the same day later, when entries are short, is not.
- **Away:** a subject may carry `away_days`, authored. From its day, that many days are not written: an away gap.
- **Blank:** a day with no must and no candidate that passes its roll is not written. A blank is not a gap: nothing is
  owed after it.
- **Catch-up:** the first written day after a busy or away gap opens with every must of the gap, each by its catch-up
  slot, oldest first. The gap's other candidates are dropped; the Chronicle has them.
- **Late addition:** each subject written on day `d` that has a late slot draws one under `late_rate`. Its late slot is
  written in day `d + 1`'s entry if that day is written, and dropped if it is not.
- **Misremembering:** a subject with a misremember slot, written for the first time, draws one under
  `misremember_rate`; it is then written by its misremember slot instead of its first. Its correction becomes a must on
  the first written day at least `correct_after_days` later.
- **Which line of a slot:** a slot may hold several lines. A shuffle bag keyed by the save, the subject and the slot
  draws them, its draw count the times that slot has been written for that subject, so the lines take turns and none
  repeats before the bag is empty. A crowd's band is chosen by how many came or went, as the people's mention bands are.
- **Order on the page:** catch-up notes, then the day's own by care, then a late addition or a correction.

## The habits as data

One table, declared once in `opening.toml` beside `[repeat_offers]` (`[journal_habits]`, planned), loaded and range
checked by the content loader. Starting values are set in build step 3 by reading the simulator's readout, not chosen
here.

| Knob | Meaning |
|---|---|
| `base`, `fade` (per kind) | A kind's care on its first telling, and what each telling multiplies it by |
| `press` (worry) | What each further day in a row adds to a worry's care |
| `floor`, `halflife` | Diligence's lowest share, and the settledness at which it is halfway there |
| `beat_refresh` | How much settledness a written beat takes back |
| `lines_start`, `lines_floor`, `lines_halflife` | The budget at the first entry, its lowest, and how fast it falls |
| `busy_ratio` | Candidates over budget that make a day busy |
| `late_rate` | The chance a written subject with a late slot gets its late addition |
| `misremember_rate`, `correct_after_days` | The chance a first telling is misremembered, and the shortest wait for its correction |

## Determinism

Each roll is a fixed hash of `save id | journal | day | subject | purpose` (purpose one of write, late, misremember,
order), mapped to [0, 1): a stable hash of the key's bytes, never Python's salted `hash()`. No draw depends on a
counter, so a new subject or a new purpose shifts no other roll. The shuffle bag's position is a count over the stored
rows. With the stored rows, the history, the content and the habits fixed, a day composes to the same notes on every
build and every pod; storing it once keeps a day fixed after the content or the habits change. The composer runs only
on the server, so no rule exists twice.

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
| `mention` | a crowd, one set per band of how many | every crowd subject |
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
`routine` subject has a catch-up slot; misremember and correction come together; a source names a cause the content
writes, and no cause feeds two subjects; each `line` person has a
person subject for each way that moves them; every `days` note shipped before this has a beat subject; every slot key
has text. Each check is shown red on a planted chapter first.

## What the page draws

The page draws a composed day as a `days` page, one page per written day, its notes in order, with the hands and
sketches the slots name, in today's page layout. Opened carries every written day; Step carries the days it composed.
`SavePresentation` gains the newest day the player has turned to, which only grows; a page past it is unread and
dots the Journal button. The creatures and places sections, their unlocks and their numbers are unchanged.

## What must stay true

- Every must subject is written exactly once (by its first, its catch-up or its misremember slot) within its gap's
  length plus a day.
- Every misremembering is followed by exactly one correction, at least `correct_after_days` later, unless the history
  ends first.
- A late addition appears only on the day after its subject was written.
- Composing day by day and composing a span in one step store the same rows.
- Changing the habits or the slots leaves every stored row unchanged.
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
- **The writer's path:** a save advanced a day at a time and the same save advanced in one jump store identical rows;
  a habits change after composition leaves the rows alone.
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

## Build order

Each step is one PR with its tests, proven able to fail.

1. **This note and the decision** (docs only).
2. **Subjects in the content.** The subject and slot schema in the chapter files, the loader's checks (each red on a
   planted chapter), and `[journal_habits]` loaded and range checked. Beat subjects for today's `days` notes, their
   first slots reusing those notes' text. Nothing reads them yet; the journal is unchanged.
3. **The composer and its readout.** The pure module with the hashed roll and the shuffle bag, the blind contract suite,
   the property tests, the mutant list, and the nightly simulator readout. Starting habit values are set from the
   readout. Nothing calls it from the API yet.
4. **Stored and served.** The `save_journal` table and migration; composition in the step's transaction for every day
   the step closes (a save with no rows composes all of its closed days); Opened and Step carry the written days;
   `SavePresentation`'s newest day turned to; `CONTRACT.txt` "JOURNAL" rewritten for the `days` section. Tests: the
   day-by-day and one-jump saves match; a habits change leaves stored rows alone; one row per day under two writers.
5. **The page.** The `days` section drawn from the served days in today's layout, the dot from the newest day turned
   to; the `days` notes' unlocks retired from the page, and their released `note_` triggers handled through the
   release lock. Render-and-look. After the Book (PR #51) lands.
6. **The shipped chapters' slots.** People who matter, routine, worries, catch-ups, late additions and a
   misremembering or two, through a fresh agent's voice pass; the readout read before and after.
