# The Breaking of Ostmere (Ostmere)

A single-player idle game, *The Breaking of Ostmere* (`ostmere.yggdrasil.pub`), made for its owner and played by them. The package and cluster names still say ashfall. Design rules: read the index `docs/decisions.md`, then the files in `docs/decisions/` for the systems a change touches, before designing anything.
The queue, and where the design canvas and tests live: `docs/open-work.md`.
How code is built and shipped, and the rules carried over from habits' mistakes: `docs/engineering.md`.
**Load the `agentic-engineering` skill before changing anything here**, and name it in every writer's brief.
Every change reaches `main` through a pull request (`gh pr create`); GitHub Actions runs the full suite and the merge
waits on its `ci-ok` check. Locally, run only the tests a change touches plus the structural gates. A push to `main`
releases the image `ghcr.io/egg82/ostmere` (and `egg82/ostmere` on Docker Hub), and Flux deploys it from the registry.

**An ask that adds a new kind of thing (a system, something placed in the world, new data, a new roll or schedule)
starts with a fit pass, not a design:** what is it an instance of, which system in `docs/systems.md` already does that
kind of thing, and how do games usually solve it (Nystrom's Game Programming Patterns, gameprogrammingpatterns.com: read
the chapter, not a summary; the Gang of Four; what has been built on them since)? Extend that system or combine the
two; build a new one only when none fits, and say why. Its open-work item carries a "Fits into:" line. Tweaks to
lines, art and numbers need no fit pass. `docs/engineering.md`, "Patterns", has the dos and don'ts.

**Never raise a held count to get a change through; split, reduce or report instead.** The structural gates' ledgers are in
`docs/engineering.md`, "Structural gates".

## Never spoil the owner

The owner plays this game, so story content must stay a surprise to them, as much as can reasonably be done. The owner gives
direction at the level of a CEO (tone, vague ideas, what to feel); everything more specific is below the line.
- Story specifics (beats, clues, twists, mini-stories, exact costs and numbers, the map past the next hill) live
  under `content/`. Never quote, summarise or paraphrase them to the owner, and never put them in `docs/`.
- Commit messages, PR text, reports and simulation output name beats by id or number ("beat 7 lands day 41"), never
  by what happens.
- When content needs the owner's judgment, ask in spoiler-free terms ("is a betrayal by an ally fair game?") or say
  a spoiler is behind the question and let the owner choose to look.
- The owner's own requests to see something override this for that one thing.
