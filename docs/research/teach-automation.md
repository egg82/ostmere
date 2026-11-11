# Teaching automation without a tutorial

How idle and incremental games get a player to find automation and then keep extending it. It answers galaxy.click's
review (`galaxy-review.md`): the reviewer made the first mix, then hand-tapped 91 times instead of adding each new card
to it, because nothing said a new card could join. Source rows are in `teach-automation/notes.jsonl`.

## Findings

The findings and their sources are in the `game-design` skill:

- When automation arrives, and how it affects decisions: `references/genres/idle.md`, "Automation".
- Showing the core automation concept first, and the red dot as the one developer-stated way to point a beginner at
  something new: `references/onboarding.md`, "Show the core automation concept in the first level". No source
  describes teaching that a new item can join existing automation.
- Where automation confuses (the failure is understanding its rules, not finding it): `references/legibility.md`,
  "State the ordering rule on an automation control".

One finding the skill does not hold: Antimatter Dimensions unlocks autobuyers through achievements and challenges
(practitioner, fan guides); its wiki returned an error, so no unlock sequence or design intent was read.

## What it means here

Proposals inferred from the above; no source showed any of them in a game like this.

- **Offer the mix early.** The reviewer reached it at four minutes, in line with the early-automation finding; the gap was after it.
- **Each new task card should carry the quiet dot until the player puts it to work**, which `decisions.md` already
  specifies and the Atom Idle dot supports. The 91 taps suggest the dot alone did not say "this can join the mix",
  so the card's own line, shown once on arrival, should say it in plain words.
- **State the mix's ordering rule on the control itself** (which card runs first, what happens when two are ready),
  since the reported confusion is about rules, not discovery.
- No tutorial screen or modal popup; the docked, dismissable feature card is the vehicle.

**Proposal to test:** when a card unlocks that the mix does not hold, its docked card says it can be added to the mix,
once, and dismissing it leaves the dot.
