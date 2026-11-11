# LLM-written fiction: what goes wrong and what fixes it

Evidence from a literature pass and a volume test on 2026-10-11. Files in `writing-test/`; the literature notes, with
which sources were read in full and which only as snippets, are in `writing-test/llm-fiction-notes.txt`.

## What the literature says

- **Tells:** unnecessary exposition (spelling out what the scene implies), cliché, awkward phrasing, tidy and positive
  endings, "tone policing" that softens dark registers, inserted morals. Same across GPT-4o, Claude and Llama
  (Chakrabarty et al., CHI'25).
- **Readers mostly can't tell single short pieces apart** (about chance in one large study), and often prefer the
  LLM's fluent tidiness. A blind test of single pieces is weak evidence.
- **The measurable deficit is sameness across outputs**: few themes, the same shapes (Ismayilzada et al.; Kreminski
  et al. C&C'24). Prompt style and personas did not reduce it.
- **Mitigations, strongest first:** fine-tuning on a target author; few-shot human exemplars (weaker); a critique
  pass (helps, often swaps one cliché for another); "avoid clichés" instructions (barely help). Reliability falls
  past about five simultaneous constraints.
- No study found on horror or dread specifically.

## What the volume test showed

30 stateless runtime-style calls (Sonnet), one arrival line each, the way the game would generate them.

- **v1** (`arrivals.jsonl`): five facts per call as JSON. Every line recited all five in the same order, one sentence
  shape thirty times. Randomly sampled facts that didn't cohere ("a girl of about twelve… her husband") were used
  faithfully.
- **v2** (`arrivals2.jsonl`): facts made coherent before sending, only one or two per call, and a seeded "lens" per
  call (only the object carried; one quoted line; what a townsperson noticed; a ledger line; where they slept; what
  they asked for first). Shapes varied and several lines were genuinely good. Remaining tell: a fact's own wording
  leaked verbatim ("a girl of about twelve" four times).

## What the owner rated (blind test, 2026-10-11)

39 shuffled pieces rated 1–5 on "how much do I want this in Ashfall": 13 published human pieces, 13 of mine written
before the research ("baseline"), 13 written after it, following the rules below ("revised"). Pieces and ratings
are in `writing-test/` (the published page holds the text; ratings are in the rater's summary, piece order =
`DATA.items`).

| Group | All | Horror | Humor | Vignette | Event | Lore |
|---|---|---|---|---|---|---|
| Human | 2.9 | 3.5 | 3.5 | 3.0 | 2.7 | 1.5 |
| Baseline | 3.8 | 3.8 | 4.0 | 5.0 | 2.7 | 4.5 |
| Revised | 3.2 | 3.3 | 3.0 | 4.0 | 3.3 | 2.0 |

Two pieces per cell for most kinds, so read the shape, not the decimals. What it shows about the taste the game is written for:
- **The research-driven revision made things worse.** Its main move was restraint (understatement, plain records,
  no twist), and the game wants the twist. Every 5 lands a turn the reader completes: "we stopped counting the dead when
  the numbers started going down", the lantern whose way out "isn't up", the trader's unnamed meat.
- **Plain records belong in the event log, and only there.** Events score about 3 for everyone, ADR included; a
  plain ledger line ("six sacks of meal spoiled… damp, or rats") got a 4. Fine as texture, never the payload.
- **Lore is short and hooked, never a long journal.** Both Grim Dawn journal entries scored 1–2; a two-line item
  description and a three-line ledger scored 4–5. The Gravity Falls journal (see `decisions.md`) holds short
  annotated entries, not pages.
- **Why the low scores were low:** they didn't fit, were too much, or were too on the nose. So the turn
  must be implied, never stated (the 5s all leave the last step to the reader), and short of overwrought.
  Examples among the 1s and 2s: arch phrasing ("in the current climate, that counts as a reference"), a moral said
  outright (Pratchett's heroes line), and the long journal entries.
- Caveat: the baseline was written by Opus in a long session with full context; runtime calls are Sonnet with a
  few facts. This says what to aim for, not that runtime output will hit it. The volume test is that gate.

The owner on the v1 column: repeats everywhere (cooking pots, dead-bird cages, smells of bread, bundles wrapped in coats,
sacks of potatoes, "would not say who they left behind", "drawn by"), and odd lines where a fact's wording leaked
("she asked the lamps on the wall", "had heard there was a guard"). Objects with heart were missing, such as a dead
person's stuffed toy. The repeats are arithmetic, not the model: ten carried objects and
five lures across thirty calls must repeat. "drawn by" is the JSON key (`drawn_by`) leaking into the prose.

On v2: good, with no real repeats beyond a few pots, bread, potatoes and bundles, some small oddities, and one
line too on the nose ("we came, all three, and not one left behind"). The line singled out ("a boy's wool cap,
small, held between them by both hands") was the model's own invention from "missing: their son": given room, it
supplies the heart itself.

**v3** (`run3.py`, `arrivals3.jsonl`): rules 3–5 below applied (attribute facts, 30-item shuffle-bag pools, the
implied-turn rule, about a third plain ledger lenses), the same 30 jobs on Haiku, Sonnet and Opus. Shown to the owner
blind as the model test on the writing-test page. Rated blind: Sonnet punchy and varied, with only a couple of oddities and
overexplanations, the pick; Haiku solid with no real notes, close behind; Opus more flowery and more on the nose,
delivering the obvious line instead of leaving it hanging, very slightly last. So Opus is not the ceiling for
short lines. **Arrival lines use Sonnet.** Haiku was close but still reached for "drawn by" in 3 of 30 lines and
copied a fact literally ("a sword too large for its carrier"), habits that become repeats at volume, and arrivals are a handful a day, so the saving is pennies.

## Rules for runtime writing

1. **Variety comes from the code, not the model:** few facts per call, a seeded lens or shape per call, never the
   whole state.
2. **Make facts coherent before sending;** the model will use nonsense faithfully.
3. **Pass facts as attributes, not finished phrases,** so the model chooses the words; key names are prose too
   (`drawn_by` became "drawn by" on every line).
4. **Pools are big and drawn without repeats:** a shuffle bag per pool plus recently-used exclusion from stored
   history, sized so a month of play rarely repeats an item. Pools hold things with heart (a dead child's toy),
   not only the useful ones.
5. **Plain records are event-log texture; everything curated lands a turn.** Event-log lenses may ask for the plain
   record (A Dark Room style). Lore, vignettes, horror and humor end on a turn the reader completes: implied, not
   stated, and not overwrought. Restraint everywhere was tried and lost (above).
6. **Each kind of line gets the cheapest model that does it adequately** (Opus is fine where needed). Pick
   by a blind batch per kind and model, rated by the owner, not by assumption: event-log texture may hold up on a small
   model while lore and vignettes need Opus, and those are rarer, so the cost stays small.
7. **Check a batch, not a line:** compare new output against recent output for repeated shapes and phrases.
