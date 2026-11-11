# Week two: what engineering builds

Week 2, from B8 (the season's turn at save time 168 h) to the end of story day 14: four chapter files. Its design is in
`content/` (`team/week-two.md`, `-numbers.md` and `-lines-brief.md`, never shown to the owner); this file holds only what the
code needs. Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a week or more.

## The chapters

| File | Spans | Lands | Carries |
|---|---|---|---|
| `day_eight.toml` | B8 → B9 | B9, at a fight's first unit | additions keyed on week 1's last feature (the week's joint project P1 and its materials), the season's turn and its content, a chip with an order-card cure, a standing fight on a new side, the journal's opening, U1-U3, SL15-SL16, Camp 13, the week's level finds |
| `day_nine.toml` | B9 → B10 | P1's last stage and a save-time floor | E1-E3, a threat ramp step, a comfort that raises the watch, a trip find, a story drain, SL17-SL18, Camp 14 lifted by P1 |
| `day_eleven.toml` | B10 → B11 | A31, a presence step in a story night | a group arrival (four from one offer, three lanes), a two-answer offer that queues a one-off and installs a lane's rule, a lane given a side, Z1-Z3, SL19, the night's clock |
| `day_twelve.toml` | B11 → night 14 | night 14, held to the calendar | a staged build run by an order card, a fight card on a finite pool, a comfort from its drop, S1-S4, SL20-SL21, Camp 15 and 16, the end card at the edge of week 2's content |

Each is merged after the one before it (new ids only, the release lock's additive rules). Landing bands are D-93's: B9
typical 192-216 h (sharp ≥ 169), B10 240-264 (≥ 209), B11 264-288 (≥ 229), B12 288-312 (≥ 249). Week 3 opens on B13,
the next season's turn at 336 h, so story day 14 ends by save time.

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| A season's turn, and what only that season brings | Clock (save time), Gates (`after_time`), Standing actions (the visitor's pause), Cards on season pools, Triggers | Week 1's nights already run a story clock on save time; a pool drained by a standing stops at the season's end with nothing retired and no mix greyed (item 6) |
| A threat step keyed to the season | Combat's ramp: a trigger on a clock store | The content check already accepts any clock store; the season's clock is one |
| A recurring bad state whose cure a lane runs | Chips, Standing orders (an order card on a chip, on a ruled lane) | Day one's hunger card plus D-91's lane order card |
| The week's joint project: a long staged build on the hands, fed by town cards | Cards (a staged craft), Standing orders (one order card covers every stage), Modifiers (each stage an entry on a side) | Week 1's comforts and its larder floor's side entry; the order card is item 8's check, not a new shape |
| A watch share or a guard raising a side while it works | Modifiers (an entry sourced by a running card), Lanes, Combat (sides) | The engine has no entry held while a card runs; combat-plan named this seam ("the guard is a townsperson's lane given a side"). Item 2 |
| The journal | Unlocks (an entry kind), Knowledge (a page reading of the fight view), Lessons, the page shell | One caller; the known set stays a page reading until a fork needs it (item 5) |
| A group arrival of four, three of whom take lanes | Offers (the arrival kind), Triggers (one outcome with three `joins`), Stores (arrivals) | Week 1's arrival idiom with a longer joins list |
| A guard chosen by an offer | Offers (answers queue a one-off, o_pelt's idiom), Triggers (an install on the one-off's count), Lanes | Installs land only from a trigger's or an answer's outcome, so the install rides a trigger on the arm card's count |
| A fight card bounded by a finite pool | Cards (an uncapped fight card whose input is a pool) | A fight card may not have a cap; its input stock ends it, as everything has a cap |
| A story drain on a store (one night's loss) | Standing actions (the visitor's idiom with a clock store) | B7's strip |
| Town cards repeated per lane | Catalogue (the loader expands one definition per lane) | Today each lane's copy is hand-written data; item 4 removes the copies |

**New engine work: one part** (item 2), and possibly one check on installs (item 7). Everything else is content on
existing systems, loader checks, page work and the simulator.

## Work, by item

Order: 4, 2-3 and 9 first (they change no content); 6-8 and 10 with `day_eight.toml`; 1 runs alongside each chapter;
5 before `day_eight.toml` ships; 11 with `day_eleven.toml`; 13 needs 1, 2, 4, 6-8 and 10; 14-16 follow the content.

1. **The simulator past night 7** (**M**, tests). Week 1's routes continued from G2 to night 14: policies that accept
   the content order cards (the staged builds', the lanes' stakes and picking, the chip's), answer the arrival offer by
   the kind's rule where the route set one, answer the two-answer offer in the visit it shows, queue the presence steps
   When ready from the visit before, and put the new fight card in the mix by a route's choice; the per-visit counters
   (spend, decide, with "queuing a stage" refused as a decision), per-absence counts, the four bands, the cap-loss check
   at each chapter's end, the 2 AM test across the week, the preparation check extended to the new side, and `--lines`
   state lists. Fits into: Simulator. Accept: every band inside on typical and above its floor on sharp; a planted
   fixture with a floor removed lands sharp under it (the floor is read, not copied); a planted visit whose only change
   is a queued stage fails the decide counter.
2. **Entries held while a card runs** (**M**, engine; interface first in `DESIGN.txt`, "FIGHTS", a new CHOICES entry and
   its REJECTED list). A card gains optional `while_running` entries aimed at a side's strength. While the card runs on a
   lane, the effective stack holds each entry scaled by the card's share of that lane's time (a tap or a ruled lane's
   repeating task: the whole; a town mix share s: amount × s, rounded down once), sourced by the card. Entries change only
   at instants where shares or tasks change, so rates stay constant between events; reading writes nothing. Aimed at
   sides only (a threat still rises only by clock triggers, invariant 83). Codec: a new optional field, no save field.
   Release lock: adding `while_running` to a released card is Safe (it pays more, as a retuned lump). Fits into:
   Modifiers (an entry with a source), Lanes (what runs where, at what share), Combat (sides). Rejected: a chip that
   raises (bends chips, which are bad states with cures); a store-backed side (modifiers never read stores); a capped
   "post a guard" one-off (permanent, so moving someone off the watch would not lower the side and the share would stop
   being a decision). Accept: invariants 80-86 still pass; new invariants as engine-contract tests: an entry is in the
   stack exactly while its card runs, scaled by share; a share change moves the odds at that instant and nowhere else;
   timing does not matter (invariant 81's shape) with a watching card in a town mix; a planted engine that holds the
   entry after the task changes goes red.
3. **Blind contract tests for item 2** (**S**, tests), by an agent that never reads item 2's code: from `DESIGN.txt` and
   the contract alone, with a `MUTANTS.txt` (the entry ignores share; it stays after the task ends; it applies to a
   threat; it applies to a card unlocked but not running; it rounds up). Accept: each mutant goes red; ambiguities
   logged and answered in `DESIGN.txt` before item 2 merges.
4. **Town cards defined once** (**S**, loader). A `[[town_cards]]` entry (a card's fields plus `lanes = [...]` and an id
   pattern) expands to one card per lane at load. Week 1's per-lane gathering copies move into it with their released
   ids unchanged; week 2's new lanes join by appending to `lanes`. Fits into: Catalogue (the loader), Cards. Accept: the
   rules digest of every released chapter is byte-identical before and after (the proof the move is structure only);
   the lock passes; a planted entry whose expansion would collide with an existing id fails the loader, naming it.
5. **The journal's first slice** (**L**, opening, api, client, art; interface first: a section in `CONTRACT.txt`).
   (a) An `entry` unlock kind; an entry's notes are unlocks of their own (a later note is a later outcome); the loader
   reads a chapter's `[[entries]]` and `[[notes]]` (ids, gates, which hand, a sketch id; text in `[text]`), and the
   content check refuses a note on no entry and an entry with no first note. (b) The page: a Journal sheet from the book
   (A3's feature), drawn from its first entry ("The screen arrives when it means something"), its button carrying the
   quiet dot while a note is unread; one page per entry in the hand font with the learned numbers below in Alegreya
   Sans, read from `View.fights` for a fought runner (unknown until fought, week 1's item 6 rule); portrait page on a
   phone, an open spread on desktop; layout seeded per entry; its first use a lesson on its own control. (c) The sketch
   method for the first entries (open-work item 4, `docs/research/sketch-test/process.md`), each looked at before it
   ships. Fits into: Unlocks (the entry kind), Knowledge (its first real use, as a page reading), Lessons (first use),
   the page shell (a sheet). Not a system: one caller, nothing to swap. Interface: api `CONTRACT.txt`, "JOURNAL", and
   `opening-screen.md`, "The journal". Accept: that section's numbered acceptance tests.
6. **The season's turn in content** (**S**, content and a loader check). The turn is an `after_time` trigger; what only
   the season brings is cards drawing a pool the turn fills and standing actions drawing a pool that empties at the next
   turn (the visitor's pause), plus a clock store for season-keyed ramp steps. No season state, no rate modifier (a raise
   that ends with its season would lower a saved mix's rates). The content check: a card or standing opened by a season's
   turn draws a pool that turn fills, so its season's end retires nothing and greys no mix. Fits into: Clock, Gates,
   Standing actions, Cards, Triggers. Accept: on fixture rules, the season's standing stops at the next turn's instant
   exactly; a planted season card with no pool input fails the check; a planted season rate modifier fails it.
7. **An order card on a chip, on a ruled lane** (**S**, opening; engine only if needed). Day one's chip order card runs
   on the hands; D-91's runs on a lane on a store. Check that the loader accepts a chip order card whose tap card is on a
   ruled lane, and that the page offers it under the chip. If the loader or page refuses, extend them; installs stay
   always-rules only (the engine's REJECTED list holds). Fits into: Standing orders (order cards), Chips. Accept: a
   fixture with a lane's chip order card accepted runs the cure on that lane at the chip's instant; a planted card on a
   lane with no such card fails the loader.
8. **One order covers every stage** (**S**, opening and tests). A content order card `at_least` on the store a staged
   build takes, tapping that build. Check: at the build's cap the order is passed over (its state served as such), the
   player's own mix runs on and nothing greys; a cure or a glowing step cuts in on the build's stage as on any queued or
   rule-run hands task. Fits into: Standing orders (order cards, the loader's at_least check), Lanes (cut-ins). Accept:
   a fixture build of three stages run by its order lands all three with no further decision and leaves the hands on
   the player's mix; a planted engine that greys the player's mix at the cap goes red.
9. **Side and threat rows drawn** (**S**, client). The fight card's strength sheet draws each side and threat by its
   label (`side_*`, `threat_*`, drawn nowhere today) with every entry and its source from `explain()`, including entries
   held while a card runs (item 2) with their share. Fits into: the Fights view (page), Modifiers' explain. Accept: a
   client test that every served entry appears with its source label; a render at phone width and in dark mode, looked
   at; nothing reachable only by hover.
10. **Lost-fight state with a draining cure** (**S**, engine and content; closes week 1's G7 and G8). Quarters were
    tried and reverted: with a fixed take no cure is tappable at every shown level and clears in one tap while hurts
    stack (engine `DESIGN.txt`, "DRAINS", FIT PASS). The self-heal runs at the designed rate through the loader's
    `every_hours`, the chip reads at a quarter through `every`, and the cure drains the store rather than taking a whole
    input; the store is never drawn: the chip is its face. Numbers: `content/team/week-two-numbers.md`. Retunes of
    released ids, Safe under the lock. Fits into: Cards (a drain is an input forgiven at 0), Chips. Accept: the chip
    and fight checks pass; week one's cures gate passes on typical and babysitter.
11. **A group arrival of four** (**S**, content). An arrival offer whose room's completion joins three lanes and adds
    four to the arrivals tally; the fourth takes no lane. Fits into: Offers, Triggers (joins take a list), People.
    Accept: the arrival kind's rule answers it at the instant it shows; the tally reads 8 after the join; three lanes
    join the town's mix.
12. **Week 1's edge card** (**S**, content). Week 1's last end card loses its "still being written" line once week 2
    ships (D-82's precedent); week 2's end card takes it. Accept: the lock passes (a text change).
13. **The chapters** (**M** each, content): `day_eight.toml`, `day_nine.toml`, `day_eleven.toml`, `day_twelve.toml`,
    each with its clocks and floors, builds, order cards, offers, fights, side layer, Camp levels, aims, end card, and
    its `beats.yaml` twin (item 14). Accept, each: the loader and the lock pass; the fight and chip checks pass; item 1's
    band holds for the chapter's beat; density targets hold on typical; the cap-loss check passes at the chapter's end or
    names the store that fails, with the content's lever applied before any sink is added; per absence at most two
    unlocks; a save rebased from each earlier chapter's end loads and plays on.
14. **`beats.yaml` and the flat check** (**S**, content and `content/team/flatcheck.py`). The chapters' twin lists, side
    entries SL15-SL21, the spine entries' changed gates (B10, B11, B12) and their `pays`, and the accepted exceptions
    (D-123). Accept: the flat check on the authored order raises nothing for week 2 beyond the accepted exceptions; a
    planted entry with a third turn in a row is flagged.
15. **Lines** (**M**, content, one batch per chapter plus one for the journal's notes). From the brief once item 1's
    `--lines` exist. Accept: every key filled; the code checks pass.
16. **Art** (**M**, after item 13's ids settle). The grades, world layers, made things, figures and journal sketches the
    content lists, picked from the packs first (`sprite-catalog`); two transient ids for one story night's poses; stages
    41-52 in `tools/scene`. Accept: composites at 390×844 and 3840×2160, looked at.

## Where this meets the other plans

- **Week 1** (`days-four-to-seven-plan.md`): its items 10-14 (offer kinds, the answer rule on the page, holds on the page,
  the cure reading) all come first; week 2 reads the arrival kind's rule and the cure reading through a completion count.
- **Combat** (`combat-plan.md`): item 2 here closes its seam for guards; its KNOWN GAPS for whole losses that are people,
  capped fights, stance and who you bring stay open (week 2 needs none).
- **Banked time** (`banked-time-plan.md`): its cap-loss target is held at each chapter's end (item 13); the season's pools
  are sinks' supply, not sinks.
- **Open work**: item 5 here is open-work item 4 (journal pages), first slice.

## After week 2, where it plugs in

- **B13** is the next season's turn (`clock: true`). The current season's pools run dry at that instant. A mix share on
  a card whose pool is empty must hand its time to the rest of the mix rather than idle: `decisions.md` says a re-tune is
  only ever set off by something the player chose, and a season's end is not one. Week 3 decides the engine's side
  (likely a dry card yielding its share, as a greyed mix falls through today).
- **B14** opens the next tier's project; the stores this week leaves without a sink at night 14 are named in the content's
  numbers file for it to take.
- **The journal** grows an entry per thing learned from here on; places and methods join creatures when content needs
  them.
