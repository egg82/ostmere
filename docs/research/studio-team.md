# An agent studio team for writing and design

Whether a studio-shaped team of agents (a lead, writers, editors, a continuity keeper) writes better than one model
plus critique, as of 2026-10-11. Source notes, one per source, marked by human raters, LLM judge or none:
`studio-team/notes.jsonl`. Several sources were read only as abstracts; the notes say which.

## What is measured

- **No compute-matched comparison exists for fiction.** Every multi-agent story paper beats an unmatched single call;
  on reasoning tasks, compute-matched single agents tie or win (Tran & Kiela, arXiv 2604.02460, abstract only).
- **Teams can make writing more alike.** Agents' Room (ICLR'25): expert raters preferred its stories, which were ~2.5x
  longer than the baseline, and its trigram repetition within and across stories was higher than the single call's.
- **Debate makes output more alike; fixed lenses fix it.** Plain debate raised quality and cut diversity below a
  single agent; giving each agent a fixed lens and showing it only its most dissimilar peers raised lexical
  diversity (69 to 83) at equal quality (EMNLP'26, LLM judge, small models, not fiction).
- **Planning artifacts help.** DOC: a detailed outline won human-rated coherence 68% to 45% and interest 60% to 39%
  (20 stories). HoLLMwood's editor rounds on outlines won 93–95%, judged by GPT-4 only.
- **Draft alone, critique blind, revise your own** beat debate by a small margin (LLM Review, LLM judge).
- **Diversity comes from many rotated seeds, not a persona**, and mixing model vendors adds almost none.
- **Rereading prose is a weak continuity check:** ~0.60 on long stories against 0.50 chance; LLM rewrites added plot
  holes at 1.5–2x the originals' rate. Studios keep continuity in keyed records instead (Lucasfilm's canon database,
  a TV script coordinator's continuity bible, a game studio's historian).

Not measured anywhere: separate writer/designer/editor roles beating one model doing every step, grimdark or horror,
landing an implied turn, cost.

## What it means here

- **The story bible gets a small team.** One lead (Opus) owns the canon (`content/canon.jsonl`, a fact per line with
  an id, its source and status) and a decision log; only the lead writes canon. Four to six proposers (Sonnet) work
  alone, each through a lens chosen by code, never seeing each other's drafts. Blind critics score other proposers'
  first drafts on a narrow rubric (turn implied or stated, on the nose, repeating a shape the bible already used);
  each writer revises only its own. A continuity keeper checks each proposal against the canon facts it touches,
  a chunk at a time, and code checks id references and repeated n-grams. The owner rates blind batches. Expect about
  5–8x a single pass (an estimate, unmeasured).
- **Runtime lines get no team.** One Sonnet call per line, a seeded lens, a few facts, shuffle-bag pools
  (`llm-writing.md`). Per-line critics cost 2–3x and make output more alike; quality is checked offline over batches
  (repeated n-grams and shapes against recent output), feeding the pools and the lens list.
- **Canon survives turnover through files, not memory**: the canon file, the decision log and the bible are what any
  agent reads to take a seat, the lead's included.
