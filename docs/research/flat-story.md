# Keeping the story from going flat

What makes a long serial or game story go flat, and which causes can be checked rather than felt, as of 2026-10-11.
Source notes, one per source, marked measured, practitioner or opinion: `flat-story/notes.jsonl`. Several sources
were read only as abstracts or summaries; the notes say which.

## What makes a story flat

- **Nothing changes.** A scene that ends where it started is activity without an event (McKee, practitioner).
- **LLM stories drift upward and resolve early.** GPT-4 synopses took a "man in a hole" shape 51% of the time
  (human: 31%), downbeat arcs almost never, rising valence throughout, and an early setback and climax that left the
  middle less suspenseful; asked for a negative arc, it complied under 55% of the time. Planning turning points
  explicitly raised "best for suspense" from 8% to 48% (Tian et al., EMNLP'24, measured). For a grimdark story this
  is the largest single risk.
- **Clean wins stop a story;** "yes, but" and "no, and" keep it moving (Sanderson and Kowal's try–fail cycle).
- **Promises without visible progress** read as going nowhere (Sanderson).
- **Single-quality gates make grind and chains;** players need to see what they're reaching for (Failbetter).
- **Unattended orderings go undramatic;** run thousands of randomized playthroughs and look at which sequences come
  up (Emily Short).
- **LLM judges don't track experts on holistic quality** (Chakrabarty et al., measured, abstract only), so critics
  answer structural questions, not "is it good".

## What it means here

Beats in `content/beats.yaml` declare fields a writer can fill honestly, and code checks them over each simulated route
(sharp, typical, lazy), not only the authored order:

| Field | Values | Flags |
|---|---|---|
| `turn` | up, down, none | any `none`; three or more in a row the same way; a week netting `up` before the last region |
| `outcome` | yes, yes_but, no, no_and | two clean `yes` in a row; a week with no `no`/`no_and` |
| `opens` / `advances` / `pays` | promise or question ids | nothing open in a window; an open id unadvanced for N days; never paid; paying an unopened id |
| `cost` | none, time, people, stores, option, trust | a week with no cost; a week where every cost is one kind |
| `moves` | characters whose state changes | a mini-story moving no one; a recurring character unmoved for two weeks |
| `thread` | thread id, start/middle/end | orphan beats; threads that never end |
| `gate` | the qualities an unlock reads | gates on a single counter |
| `register` | dread, wry, warm, grim, wonder | four or more in a row in one register (inferred, not sourced) |

The critics' rubric gains four yes/no rows, each with a quoted span: does the situation end different from how it
started; is a clean success missing its cost; is the ending tidier or brighter than the beat's planned `turn`; is the
turn stated rather than left to the reader.

Code cannot check whether a turn lands, whether a detail is specific, or whether dread builds. The owner judges the first
hour (`CLAUDE.md`); later beats get a fresh reader agent given only the prose and the beat's declared fields, asked
whether they match; the late game's feel needs a human outsider.
