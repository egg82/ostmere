# Telling a player about a wait, and marking the end of content

How games say that a real-time wait is coming, and how they mark where current content stops. It answers galaxy.click's
review (`galaxy-review.md`): the reviewer took the wait after dusk for the end of the game and left; another player
retried the blocked card 31 times over 40 minutes, and left. Source rows are in `waits-and-ends/notes.jsonl`.

## Findings

The findings and their sources are in the `game-design` skill, `references/feedback.md`, "Real-time waits and the
end of content". In short:

- A wait that fits the fiction reads as acceptable and an arbitrary cap as a block; Fallen London states its refill
  rate in plain text beside a persistent counter, and no source shows wording that stops repeated retries.
- Players want an explicit out-of-fiction statement that content has ended. In Abiotic Factor the in-world cues were
  missed or read as a missing item; a player blamed "reading while exploring in this game being a liability" (verbatim,
  Arts 101).

## What it means here

Proposals inferred from the above; no source showed them for a game like this.

- **Say, in plain words on the waiting card, that this is a real-time wait and how long**, as Fallen London states its
  rate. The reviewer's screen showed only the aim line changing.
- **A blocked card should say why it is blocked and what it waits for**, so retrying it 31 times has no appeal.
- **The end of current content gets its own docked, dismissable card**, worded out of fiction ("This is as far as the
  game goes for now"), with a date only if one is true. Never the vaguer in-world line alone.
- Keep the wait wording free of anything that reads as selling the skip.

**Proposal to test:** a wait card carries its duration and a one-line reason, and the last chapter ends in a plain
end-of-current-content card that is distinct from any wait.
