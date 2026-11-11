# Banked time: measurements and content calls

Spoilers: under `content/`, never shown to the owner. Ids and numbers only, no lines. The design is
`docs/design/banked-time-plan.md` and engine `DESIGN.txt`, "BANKED TIME"; this file holds what they cannot name.

## Measured: production lost to caps

Seed 0, `day_two.toml` at `5f2b4c1`, the day-two routes (`tests.daytwo.routes.day2`), each running store sampled
every 15 game minutes; lost = the ledger's unclamped net while the store is at its cap. XP still trains at a cap
(engine `DESIGN.txt`, "Cap"), so this is materials only. Probe: a scratch script outside the repo; plan item 1 makes it a report column.

Day two as played (B3 to the route's last decision), share of each store's making lost:

| Route | damp_wood | roots | stones | camp |
|---|---|---|---|---|
| sharp | 97% | 82% | not read | not read |
| typical | 98% | 94% | 100% | 14% |
| whenever | 100% | 93% | 100% | 36% |
| evenings | 98% | 95% | 100% | 70% |
| lazy | 99% | 99% | 100% | 86% |

("not read": the probe ran sharp but its output was cut before those rows; re-run to fill.)

Away 8 h, 24 h and 72 h from the route's last decision, nobody deciding: **96-100% of damp_wood, roots, stones and
camp lost on every route measured** (typical, whenever, lazy, evenings). dry_wood loses 0 (a conversion its consumers
draw). Camp's 100% after B4 is level 8 being the last level (cap 150 000, nothing above it yet), not a held lift.

What this says: every gathered store fills within the first hours of any absence from B3 on, and from then on the
hands and her lane make nothing but XP. It is not an attention bug today: the 2 AM test is level on day two, because
the babysitter has nothing to spend on either. It is the "nowhere to go" the item names: a return after 8 h looks
the same as a return after 2 h.

## Fit pass verdict, in content terms

Nothing takes overflow. The design adds no engine part: day three's sinks are three content shapes on existing
systems (the plan's table): trips (an uncapped card with inputs, run in the mix, held against a supply store),
comforts (capped crafts with big costs, queued), and arrivals (an offer whose yes queues a make-room one-off). Sizing
target the plan sets: over an 8 h and a 24 h absence from each chapter's end on typical, at most half of what the
gathered stores make is lost to caps.

Sizing a trip held against store S: a trip card with work_s w and input a of S, run held, draws S at exactly the rate
S is made beyond its level, up to share 100% × a × 3600 / w per hour. To absorb day two's end rates (24 h above:
damp_wood about 2 380/h, roots about 860/h, stones about 480/h across both lanes) one trip needs a × 3600 / w at least
those numbers for the stores it draws, at whatever share the route gives it.

## Open (content side)

Each needs a content answer before day three's sinks are written. Spoiler-free forms for the owner where one is needed.

- **BT1. Is there a trip in R1 before B7?** Expeditions in the spine start at R2 (B20 counts them). A near-camp trip
  in days 3-7 (scouting, salvage, a cache) is the cheapest sink for the gathered stores, and its discrete finds
  (completions 1..n, each a trigger) are where story can ride. If no trip fits the story before R2, day three's sinks
  are comforts and arrivals only, and the 50% target probably fails on stones and damp_wood. Recommendation: one R1
  trip with two or three finds, opened at or before B5.
- **BT2. What a trip makes after its last find.** An uncapped trip keeps paying its lumps forever. Either a material
  later recipes take (scrap, salvage) so it stays a real choice, or nothing past a token so the hold falls idle once
  the finds are done. Recommendation: a material a day-four-or-later recipe takes, with its own cap.
- **BT3. Which comforts, and what each changes in the scene.** "Surplus visibly makes the camp less miserable": each
  comfort a capped craft with a cost of several caps' worth of gathered stores, built across absences by the queue,
  each with a scene stamp (art) and either a small pay (a modifier) or a need an arrival reads. How many in day three:
  enough that their total cost covers the 24 h target on typical (the simulator's column says when it does).
- **BT4. Arrivals as the B7 gate's supply.** Day-two Open 7 needs three arrivals by about day 6, "food to spare" as the
  draw. Proposed idiom: a trigger on a food store's level shows the newcomer's offer; yes queues a make-room one-off
  (inputs: the pile); a trigger on its completion unlocks their lane and installs their default rule. Whether the
  second and third arrivals are lanes or the town's mix with shares is day-two Open 3's call, not this one's.
- **BT5. Does a trip carry a fight in week 1?** A trip with a FightDef (combat-plan) on the hands side makes its
  supplies a real stake ("a lost fight wastes the attempt"). Before B7 combat is not open, so week-1 trips are
  fight-free; whether the first post-B7 trip has one is content's (combat-open.md C-questions may already decide it).
- **BT6. Study that pays in rediscovery.** Arcana opens at B6. A study card that takes materials (salvaged pages,
  ink) is the same shape as a trip. Not needed for the 50% target in day three; noted so day five's content can use it.

## Answers (lead, day three's design, 2026-10-27)

Specs: `day-three.md` (cards, stores, finds, the arrival) and `day-three-numbers.md` (sizes and targets). The owner's own
play of day two weighs on all six: "guess I'll wait and come back in a few hours without having a use for the
resources". So the first sinks are reachable at B4 itself (and one in day two, `day-three.md`, "Day two's sinks"), and
every return in day three has a use for what piled up.

- **BT1: yes, one R1 trip, opened at B4.** `field_track`, the track out over the old fields, opened by A22 (the step
  that glows when B4 lands), fight-free, uncapped, hands lane, held against damp wood. It takes damp wood (logs laid
  over the wet ground), stones (cairns in the Still's fog) and roots (food carried), so one held trip drinks all three
  gathered stores; it trains Scavenging (salvage along the way), which is what B6's level gate reads. Three finds on
  completion counts: the warm stream (K2, first run: clay, opens `dig_clay`), the dead field (K4: scrap) and wolf sign
  (the B5-B6 chapter's first beat, so day three keeps its turns). The orchestrator's lean holds: without it nothing
  takes the stores before week 3, and the track is honest R1 ground (`regions.md`: old fields under ash, the warm
  stream, seam-warm clay, scrap).
- **BT2: scrap, cap 12, and nothing else.** Each run brings 1 scrap after the finds as before them. Scrap is what the
  spear takes at B7 (C6) and Smithing takes later, so a player who held the trip all week walks into B7 with the
  spear already affordable: preparation banked by the hold, never by watching. The cap keeps "everything has a cap";
  the trip's other output is Scavenging XP, which never caps. *Revised after measuring:* one scrap a run filled the
  cap in minutes on every route, so it was lost past the hold, not banked by it. Scrap now comes only from finds on
  the run count (`day-three.md`, "Sinks after measuring"), which every run away moves closer.
- **BT3: four comforts across days two and three, each staged, each with a scene state and a small pay.** Day two:
  `raised_bed` (3 stages; rest recovers faster). Day three: `larder_floor` (3 stages; roots hold half again),
  `rack_roof` (2 stages; the rack dries faster in the fog), `clay_hearth` (3 stages, needs clay; opens a stew).
  A stage costs up to a full store of what it takes, so a return with full stores always has a stage to pay for.
  Two of them are the cures C4 needs after B7 (the stone floor against ashrats, the roof against crows): no new
  mechanism, an entry each on the camp's side, added by combat's content (combat-plan item 8). Their upsides name only
  the comfort pay; the protection is learned at B7 ("No blind permanent choices": a minor choice names its upside).
- **BT4: the idiom as proposed, with D-87's equal answers.** Arrival 2 is day three's: a trigger on the stew store's
  level (the hearth's smell carries; "food to spare") shows offer O-stay; both answers build them a bay of the lean-to
  from the same stores in the same time, by the player's hands (`make_bay`, A23) or theirs (`n2_build_bay`, A24), so
  nobody is turned away and B7's arrival count never waits on an answer. On the bay's completion they join and the
  town's mix with people as shares arrives (day-two Open 3, decided). Arrival 3 (a broken pair) is the B6-B7
  chapter's, by the same idiom. O-stay is the second offer kind, so the answer order shows in the Rules tab from it
  (day-two Open 4, decided).
- **BT5: no fight on any week-1 trip.** After B7 the hunt is a fight card (C3), not a trip; the field track stays
  fight-free for good. The first fighting trip is week 2's call (wolf packs, days 8-14), if it comes at all.
- **BT6: Arcana's first card takes materials, from the B6-B7 chapter.** `hand_on_stone`: kindling (dry wood) in,
  Arcana XP out (rule 1: the heat is moved, so the kindling burns). Uncapped, held against dry wood, so it is a sink for
  the rack's output from the moment Arcana opens. Day three needs none of it.
