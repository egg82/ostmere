# Combat, first slice: what engineering builds

Combat opens at B7 (target day 6, the end of week 1). This slice is what week 1 needs: fights the player chooses, threats
that come to the camp on their own, preparation that changes the odds, the region's ramp, and the log of wins and
losses. Its design is in `content/` (`team/combat-open.md`, questions C1–C9, never shown to the owner); this file holds only
what the code needs. Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a week or
more.

Interface for items 1–5: engine `DESIGN.txt`, "FIGHTS", and `api/CONTRACT.txt`, "FIGHTS". An implementer gets one
item, those two sections and this file.

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| A fight the player chooses (a hunt) | Cards: an uncapped card with a FightDef | Fighting is an action in the mix (`core-loop.md`); tap, mix, queue, rules and lanes come with it, so every verb already has an order |
| A threat that comes on its own (at the camp's stores) | Standing actions with a FightDef | It runs whenever unlocked whatever the player does: no response window, as decided |
| Odds | Modifiers: MUL_BP entries in the effective stack, sourced by the fight | Losses are flows (the engine contract); odds as entries make "why is it that number" the existing query |
| Power and threat strength | Modifiers: two new targets with a base (Store caps' arithmetic) | Gear, skill pays, walls and guards are modifiers already; a roster entry is a Type Object |
| The region's ramp | Triggers on a clock store, the night's and the visitor's idiom | No region state and no Save field (the held list refuses one) |
| A fight's win or loss in the log | Chronicle and unwrap: the arrival queue labels exact counts with a shuffle-bag draw | The engine has no per-fight result; chance only picks which fight in a window carries a loss |
| B7's own moment and what it costs | Cards or triggers with lines; a standing drain with a clock store | A beat never rolls; day one's visitor already takes stores this way |
| A lost fight's bad state, and its cure | Chips (a cost under its word, a cure in reach), Stores, Cards | Unchanged shape |

## Work, by system

Each item merges on its own, in this order. Items 1–3 are the engine, 4 the wire, 5–6 the loader, 7 the page, 8 the
content, 9–10 the simulator and tests, 11 art.

1. **Strength targets** (**S**, engine). SideDef and ThreatDef in Rules; SideStrength and ThreatStrength as Targets,
   their value and explain(); validation of who may aim at a threat (trigger outcomes only, raises only, sourced by
   the trigger); codec tags. Accept: invariants 82 (its strength half) and 83 as engine-contract tests, each with a
   planted control (a ThreatStrength entry in a card's finished is refused; a lowering entry is refused); an old save
   from `app/tests` fixtures decodes unchanged.
2. **FightDef and odds** (**M**, engine). The component on CardDef and StandingDef; the loses, wounds and tally lines;
   loss_bp; the odds entries in `gates.effective_stack`; a tap keeping its odds in LaneState.speed; validation (no cap
   on a fight card, per_hour only on a standing fight, tallies unshared and never cost, no "odds:" source in content).
   Accept: invariants 80, 81, 82, 84, 85 and 86 as engine-contract tests from the interface alone (a blind writer),
   and a `MUTANTS.txt` run on loss_bp's rounding direction and on costs being left unscaled.
3. **The fights view** (**S**, engine). View.fights from DESIGN.txt, "FIGHTS", "View". Accept: a test that reading a
   view changes nothing (the snapshot test's shape), and a running tap reports its kept loss_bp after a side entry is
   appended mid-tap.
4. **The wire** (**S**, api). SideInfo, ThreatInfo, FightInfo on CardInfo and StandingInfo, View.fights with
   Strength, the `combat` feature, the new text keys. Accept: `openapi.json` shows the new models with no bare dicts,
   and a decision round trip over a fixture rules set with one fight card and one standing fight serves them.
5. **The loader's schema** (**M**, opening). TOML for sides, threats and a `fight` table on cards and standing
   actions; tally stores; the ramp written as triggers. Accept: a fixture chapter with one of each loads, and each of
   the item 6 checks has a planted failing fixture.
6. **Content checks for fights** (**S**, opening). Refuse: a trigger aiming at a ThreatStrength whose `when` reads
   anything but a clock store (a store made only by fight-free standing actions and costed by nothing); a fight runner
   unlocked before or without `combat`; a fight's loses or wounds store with no cure in reach the moment it shows
   (`decisions.md`, "Every bad state has a cure in reach"), reusing the chip checks' reading; a tally store any
   outcome unlocks. Ids and fields only, never text. Accept: each check names the failing id and has its control.
7. **The page's fights** (**M**, client). A fight card's odds, strengths and on-loss line; a strength's entries opened
   by a tap; standing fights in the ledger with their tallies; the arrival queue's fight entries with the shuffle-bag
   labels and the summary line. Accept: a client test that a window's labels are the same on every call and hold
   exactly the served lost count; a render at phone width and in dark mode, looked at (`headless-render`); every
   control 24 px or more, nothing reachable only by hover.
8. **The content** (**M**, content, after C1–C9 are answered). The chapter carrying B7 (C1): B7's own moment and what
   it takes, the `combat` feature card, and the fights, threats, gear, skill pays and lost-fight bad state with its
   cure that C2–C6 settle, the ramp's clock and triggers, and the lines. Accept: the loader and item 6's checks pass, and item 9's report
   shows B7 inside its band.
9. **The simulator past B7** (**M**, tests). Policies for the hunt in the mix, the week's gear and the threats' cures on the
   routes; per-visit and per-absence counters; B7's landing band; fought and lost per runner in `report`; the line
   state lists for the writers' brief. A timing check: the same route under two visit schedules ends week 1 with the
   same stores and tallies (invariant 81 at the scale of a week, "a prepared town fares the same whatever the timing").
   A preparation check: a route that builds the week's gear loses measurably fewer hunts than one that never does. Accept:
   both checks proven able to fail by a planted engine mutant (odds read from the visit time; a side entry ignored).
10. **The day-one and 2 AM tests past B7** (**S**, tests). `test_dayone_two_am.py` replays with fight runners running
    across the babysitter's and the whenever player's visits; the cures check covers a lost fight's chip and the threats'
    stores; "Leaving and coming back always pays" covers every fight card's drawn times. Accept: each extended check
    goes red on a planted fight that pays on looking, and the held ledger of today's failures does not rise.
11. **Art** (**M**, after C9). The figures and props C9 lists, picked from the packs first; the changed world states it lists.

## What this slice leaves for later, and where it plugs in

Each is a KNOWN GAP in engine `DESIGN.txt`, "FIGHTS", with what decides it. Walls and guards are entries on a camp or
town side (no new mechanism); the guard is a townsperson's lane given a side. Expeditions bring a side made of who goes.
Later regions' rosters are ThreatDefs with their own clocks. A companion dying needs a whole loss landing at each unit
of a tally. The out-of-place threat enters as logged input, never a roll in the engine. Capped fights and stance wait
for the first region gate behind a fight and the first expedition.
