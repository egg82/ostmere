# Human readers and a human editor

Where to get blind readers who do not use LLMs, where to get a human editor, what each costs, and how to run the blind
comparison. It serves `writing-craft.md` section 7: a rewrite is judged by such readers, old against new. Sources are
in `human-readers/notes.jsonl`, one row each with its URL and whether it was read in full or only as a snippet.
Evidence is marked in a word: **rates** (a published rate chart), **policy** (a platform's own text), **practitioner**,
**opinion**, **snippet** (seen only in a search result). As of 2026-10-21.

## 1. Blind readers who do not use LLMs

**Finding: no source offers a way to verify "does not use LLMs"; every route rests on the reader's say-so or on the
community's norms.**

- **Prolific** (policy, read in full): no documented filter or prescreener for AI use. Screening is by demographic
  filters, expert groups, or a custom in-study screener with a screen-out payment (minimum GBP 0.10). Self-reported
  screening can be unreliable. Pay minimum is GBP 6 an hour, recommended GBP 9, judged on actual completion time, plus
  a platform fee whose percentage was not retrieved (snippet).
- **intfiction.org beta-testing threads** (practitioner, snippet): authors routinely recruit free testers, who return
  spelling, grammar, story and language comments. A text-game audience, so skilled readers; recruitment is by message.
- **Critique groups** (policy, snippet): Brooklyn SF Writers, Critters and Manchester SF bar AI-written work or
  critiques, which makes their members a reasonable proxy for non-LLM readers. Scribophile and Critique Circle policies
  and prices were not verified.
- **itch.io** (policy, snippet): since late 2024 it asks creators to disclose generative AI, and its community is
  broadly hostile to undisclosed AI. This bears on audience attitude, not on recruiting.
- **r/incremental_games**: a Feedback Friday thread stays open; no AI rule was found and the rulebook was not read.
  Its readers know the genre but are not screened for LLM use.

## 2. A human editor

**Finding: book-editing rates are well documented and game-narrative rates are not.** (rates)

- EFA 2026 chart (read in full, survey median of 2025 rates): fiction copyediting 2.0-2.7 cents a word ($40-50 an
  hour); line editing 2.7-3.5 cents ($50-60); developmental 3.0-3.5 cents ($52.50-70); proofreading 1.2-2.0 cents.
  No game-specific rows.
- Reedsy marketplace averages (snippet): about $0.027 a word copyedit, $0.036 developmental, $0.020 proofreading;
  book-oriented.
- The Australian Writers' Guild publishes minimum rates for freelance narrative designers on indie games; the figures
  are behind a member login (snippet). One itch.io freelancer quoted about $10 per 1000 words, self-described as cheap
  (anecdote, snippet).

## 3. The blind comparison

**Finding: the only method guidance found is for LLM judges, not human raters** (opinion, snippet): randomise which
version is A, show both orders, and map back before aggregating. No sample-size guidance for human raters was found.

## What it means here

Proposals inferred from the above; no source tested them on game text.

- Run the comparison as a batch: old and new versions of the same lines, labels randomised per reader, order varied,
  the question "which says what it means, which sounds written by a person". Ask readers to state whether they use
  LLMs, and treat that as unverified.
- Start free (intfiction.org, a critique group that bars AI), then pay for Prolific readers if free ones are too few.
  Budget Prolific at the recommended hourly rate times actual reading time, plus the fee.
- Hire the editor by word count at line-edit rates from the EFA chart, as an upper bound for game text.

**Proposal to test:** one batch of old and new lines, randomised A/B, read by intfiction.org volunteers first.
