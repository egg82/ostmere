# Getting agents to write well-designed code

What the field says and what is measured, as of 2026-10-11. Two surveys: practitioner and vendor methods, and measured
evidence. Source notes, one record per source: `agentic-engineering/practice-notes.jsonl` and
`agentic-engineering/evidence-notes.jsonl`. The evidence survey read abstracts and vendor pages, not full papers, so
its numbers are leads; check the paper before quoting one.

## What is measured

- **Agent code erodes as the agent extends it, and prompting doesn't stop it.** SlopCodeBench (arXiv 2603.24755): 15
  agents extending their own code under changing specs; erosion rose in 77% of trajectories, and quality guidance in
  the prompt lowered the starting level by up to a third without changing the rate of decay.
- **Agent-written tests during a fix change nothing** (arXiv 2602.07900): mostly print statements, no effect on
  SWE-bench outcomes.
- **LLM-written property-based tests find real bugs** (Maaz et al., arXiv 2510.09907): 56% of reports valid across
  100 packages, 86% of the top-ranked.
- **A fresh-context reviewer is only mildly better than self-review** (arXiv 2603.12123, injected errors; the gain was
  not significant).
- **Context files like `AGENTS.md` don't generally help and cost 20%+** (arXiv 2602.11988); they help for the repo's
  non-standard rules.
- **Multi-agent** gained 90% on Anthropic's research eval at about 15x the tokens; nothing controlled exists for coding,
  and Anthropic says coding parallelises less.
- **Not measured by anyone:** whether design docs, test-first, or planner/implementer/reviewer pipelines improve design
  quality.

## What practitioners converge on

Anthropic's docs, Hashimoto, Willison, Beck, Böckeler (and OpenAI via her), Huntley and the Thoughtworks Radar agree
more than they differ:

- **Checks the agent runs into, not instructions it reads**: tests, types, linters as backpressure inside the loop.
- **Boundaries checked by machine**: dependency and import tests, custom lint rules. Prose boundaries drift.
- **Tests from a different agent than the code**, and tests proven able to fail (red first; mutation testing, since
  AI-written tests that are "perpetually green" are the commonest weak point).
- **Every defect becomes a permanent guard**, not just a fix.
- **Structure and behaviour in separate commits** (Beck).
- **Cleanup as a standing role** on integrated code (dedup, design drift), not only review before code.
- **Ceremony scaled to the task**: a one-sentence change skips the plan. Heavy spec frameworks (spec-kit, Kiro) and
  swarms of parallel writers are on the Radar's caution side.
- **Reviewers scoped to correctness and requirement gaps:** asked to "find gaps", a reviewer always finds some, and
  chasing them adds abstraction layers, defensive code and tests for impossible cases (Anthropic).

## What it means here

The only levers left standing are structural, so ashfall's rules live as gates wherever they can
(`docs/engineering.md`, "How code gets written"). The parts of our method nobody has measured (the blind contract-test
agent, the interface-first stage) are measured here instead: mutation score of the contract tests, and how many defects
escape to the later bug hunts.
