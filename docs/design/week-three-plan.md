# Week three: what engineering builds

Week 3, from B13 (the next season's turn at save time 336 h) to the end of story day 21: four chapter files. Its design
is in `content/` (`team/week-three.md`, `-numbers.md` and `-lines-brief.md`, never shown to the owner); this file holds only
what the code needs. Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a week or
more. From week 3 a week's chapter beats share one letter, numbered through the week (T1-T13), since the single
letters ran out.

## The chapters

| File | Spans | Lands | Carries |
|---|---|---|---|
| `day_fifteen.toml` | B13 → B14 | B14, a joint project's last stage | additions keyed on week 2's last feature (the next tier's joint project, a finite pool its later stages take), the season's turn and its content, the last season's chores retired (item 3), a chip with an order-card cure on a ruled lane, a staged lane build that raises a season standing per stage (item 9), a fight card on a finite pool, T1-T3, SL22-SL23, two asks, Camp 17 |
| `day_sixteen.toml` | B14 → B15 | B15, a glowing one-off held to a floor | the tier's standing and a count it makes, offers whose yes queues a one-off, a two-answer offer that opens the week's joint project, a story drain, a second magic skill opening on its first card (item 10), notes on an existing journal page, T4-T6, SL24-SL26 |
| `day_eighteen.toml` | B15 → B16 | B16, a clock after an arrival, held to a floor | two arrival groups (three lanes; two lanes, one with an installed rule), a lane-less arrival on a clock, offers gated on the tier's count, T7-T9, SL27 |
| `day_nineteen.toml` | B16 → night 21 | night 21, held to the calendar | the joint project's last stages and a floor, the next region's feature and clock, the map's first slice (item 7), a story night, T10-T13, SL28, Camp 18 and 19, the end card at the edge of week 3's content |

Each is merged after the one before it (new ids only, the release lock's additive rules). Landing bands are D-93's: B14
typical 360-384 h (sharp ≥ 309: no floor needed, the project shows at 331 h), B15 408-432 (≥ 349), B16 432-456 (≥ 369),
B17 456-480 (≥ 389). Week 4 opens on the next season's turn at 504 h, so story day 21 ends by save time.

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| A mix share on a store that can no longer be made | Mixes (the flattened shares), Stores and caps (the dry rule), Modifiers' explain | Today a dry share idles until the store refills; a pool refills only at its season's next turn. The yield is derived and sourced, never stored (item 1) |
| A season's chore rules retired at the next turn | Standing orders (the installed rule's inverse), Triggers (an outcome part), Chronicle and unwrap (the rule log) | `decisions.md`, "Each season brings its own chores": the rule goes away when its season ends; order cards already come back while their chip shows uncovered (item 3) |
| The second season's turn | Clock, Gates, Standing actions, Cards on season pools, Triggers, Chips | Week 2's item 6 shape, a second season; the season check runs on it unchanged |
| A staged build on a ruled lane, each stage raising a standing's rate | Cards (a staged lane card), Standing orders (an order card on a ruled lane), Modifiers (an entry per stage on a standing's rate) | The palisade's stage entries on a side, aimed at a rate; week 2's item 7 put an order card on a ruled lane (items 8, 9) |
| A standing that makes a count arrivals wait on | Standing actions, Stores (a count, never drawn), Gates, Offers (the arrival kind), People | The visitor's idiom and week 1's arrivals; the People row's arrival policy stays planned until a second tier needs the same shape |
| Offers whose yes queues a one-off and whose no costs nothing | Offers (no kind), Cards (a queued one-off), Triggers | Day nine's asks with o_pelt's queued one-off |
| A second magic skill, opened on its first card | Pacing curve, Cards, Chips (its first card is a cure), Lessons | Arcana's row. The Spells row (an interpreter combining rules) waits until there is something to combine (item 10) |
| A person leaving the town | People (the inverse of a join), Lanes, Mixes, Standing orders, Unlocks (an only-growing "left" kind) | Joins add a lane's person; nothing removes one, and `decisions.md` expects people to come and go (item 4) |
| The next region opening | Unlocks (a feature), Clock (a clock store, as R1's) | The Regions row's engine state waits until a second region's threat ramp needs time-in-region as a policy |
| The map | Town map and world map (its first caller), the page shell (a sheet), Lessons | Planned since `decisions.md`, "A world map"; one caller, so a module, not yet a system (item 7) |
| A lane-less arrival on a clock | Triggers, Stores (arrivals), the scene | Week 2's B10 idiom |

**New engine work: two parts** (items 1 and 4) and one outcome part (item 3). Everything else is content on existing
systems, loader and page checks, the map, and the simulator.

## Work, by item

Order: 1-5 first (they change no content; 2 and 5 blind, beside 1 and 4); 8-10 with `day_fifteen.toml` and
`day_sixteen.toml`; 6 runs alongside each chapter; 7 before `day_nineteen.toml` ships; 12 needs 1, 3, 4 and 6-10, and its
last chapter needs 7; 13-15 follow the content; 11 with the last chapter.

1. **A share on a spent store yields** (**M**, engine; interface first in `DESIGN.txt`, a new section "SPENT", a
   CHOICES entry and its REJECTED list). A mix card paused dry on a store that no unlocked card or standing can make
   (a pool, or a store whose every unlocked maker is itself spent, resolved as a fixpoint) is spent: its share is
   handed to the rest of its mix in proportion to their shares, rounded down once, the remainder idle as today; each
   receiving line's `explain()` names the spent card as a source; an outcome that makes the store again (a season's
   turn refilling a pool) takes the share back at that instant. A store a running maker can refill yields the same way,
   its share back at the hourly resume, so the split changes at most at the dry rule's own instants (`decisions.md`, "A
   mix keeps going without a dry store"; the page shows the split that runs under the one set). Derived wherever shares are read, never stored: no save field. Release
   lock: a saved mix holding a spent card runs differently after the deploy, forward-only at load, the decision's own
   point (`decisions.md`: a re-tune is only ever set off by something the player chose). Fits into: Mixes, Stores and
   caps, Modifiers. Rejected: idling (the 2 AM test fails at every pool's end, and the player must re-tune for a season);
   greying the mix (a season's end would stop saved mixes); retiring the card (the next season brings it back, and a
   retired card greys its mix); a hidden redistribution (`DESIGN.txt`'s rule against a number with no source). Accept:
   invariants 16 and 19 still pass; new invariants as engine-contract tests: a pool emptying mid-mix raises the other
   cards' shares in proportion at that instant and nowhere else; explain names the source; a refill restores the saved
   shares at its instant; a store with a running maker pauses and yields until its resume; a store whose only maker is
   spent is spent; on a fixture with a pool, the 2 AM test passes where it fails before the change; a planted engine
   whose yield follows the store rather than the pause (the share back before the hourly resume) goes red.
2. **Blind contract tests for item 1** (**S**, tests), by an agent that never reads item 1's code: from `DESIGN.txt`
   and the contract alone, with a `MUTANTS.txt` (yields on a refillable store; yields across lanes or mixes; keeps the
   yield after a refill; ignores the fixpoint; rounds up; stores the yield in the save). Accept: each mutant goes red;
   ambiguities logged and answered in `DESIGN.txt` before item 1 merges.
3. **A season's end retires its chores** (**S**, engine and loader; interface first in `DESIGN.txt`, beside "Installed
   rule"). An outcome part `retire_orders = [card ids]` removes every order, the player's own included, whose task taps
   one of the named cards; each removal is logged by the rule log (`engine/rulelog.py`), so the Rules tab's Lately
   block says the rule ended with its season. The loader refuses a named card that is not the cure of a chip whose
   store only a season's standing makes, and an outcome that is not a season's turn. The order cards need nothing: they
   are offered again while their chip shows uncovered. The chore's leftover state is emptied by content (a standing
   drain on its own pool, the visitor's idiom). Fits into: Standing orders, Triggers, Chronicle and unwrap (the rule
   log). Rejected: leaving the rules (`decisions.md`: the rule goes away when its season ends); an outcome part that
   takes stores (rejected in `DESIGN.txt`, FIGHTS; the visitor's idiom does it). Accept: on fixture rules, a turn
   removes exactly the orders tapping the named cures and logs each; an order tapping anything else survives; the
   order card is offered again at the chip's next showing; a planted retirement naming a non-chore card fails the
   loader, naming it.
4. **A person leaves the town** (**M**, engine; interface first in `DESIGN.txt`, a new section "LEAVES", beside
   `engine/joins.py`). An outcome part `leaves = [{lane, stops = [standing ids]}]`: the lane's person leaves at that
   instant. Their lane stops (its tap or task ends; work in progress is dropped, never paid), the orders on that lane
   are removed and logged, their shares leave the town's mix (nobody else's shares change: each person's shares are
   their own time), the lane's cards retire without greying any mix (a card retired by a leave drops out of the mixes
   holding it; a completed card still greys, as today), the listed standings stop, and a new only-growing unlock kind
   `left` records it. Codec: the unlock kind; no save field. The view stops drawing the lane; the page's town list and
   the Rules tab drop it. Fits into: People, Lanes, Mixes, Standing orders, Unlocks. Rejected: a lane left idle (a
   person-shaped hole in the Rules tab, with no reason on it); greying the town's mix (every lane stops for one
   person); a lane-less stand-in (a person the player never set to work, which content cannot always use).
   Combat's KNOWN GAP for whole losses that are people (a fight's tally crossing a unit) stays open: this is an
   outcome, not a fight. Accept: new invariants as engine-contract tests: after a leave, every other lane's rates are
   what they were; no mix greys; the lane's orders are gone and logged; a leave mid-task pays nothing; a rebased save
   with the leave already past loads; a planted engine that greys the town's mix on a leave goes red.
5. **Blind contract tests for item 4** (**S**, tests), as item 2, with a `MUTANTS.txt` (greys the town's mix; moves the
   leaver's shares to another lane; pays the task in progress; leaves the lane's orders; keeps the listed standings
   running). Accept: each mutant goes red; ambiguities answered in `DESIGN.txt` before item 4 merges.
6. **The simulator through week 3** (**M**, tests). Week 2's routes played on from S4's saved ends (`tests/weektwo/`,
   `ends.py`) through the four chapters to the visit night 21's step lands in: policies that accept the content order
   cards (both joint projects', the ruled lane's staged build, the reap and cover cards), answer the arrival offers by
   the kind's rule where the route set one, answer the asks and the yes/no offers in the visit they show (yes on every
   route, one no on sharp so both answers are measured), tap the glowing one-off in its visit, queue the story night's
   step When ready from the visit before, and put the new fight card in the mix by a route's choice; the per-visit
   counters, per-absence counts, the four bands, the cap-loss check at each chapter's end, the 2 AM test across the
   week, the preparation check through the season's threat step, calendar days, sharp's decision ratio (at least three
   visits of every four with a decision), and `--lines` state lists. The policies' hand-made removal of shares on
   spent cards goes once item 1 ships. Fits into: Simulator. Accept: every band inside on typical and above its floor
   on sharp; a planted fixture with a floor removed lands sharp under it; a planted visit whose only change is a
   queued stage fails the decide counter.
7. **The map's first slice** (**L**, opening, api, client, art; interface first: a section "MAP" in `CONTRACT.txt`).
   (a) Content: a chapter's `[[places]]` (id, stamp kind, a coarse position, the unlock that reveals it, a label key
   or none), served on `Content`; the loader refuses a place with no reveal and two places on one position. (b) The
   page: a Map sheet from a button that arrives with its first place (the screen arrives when it means something);
   stamps placed by code from the sourced set (`docs/research/art-sourcing.md`), never overlapping, never repeating
   until the pool is used, each label in clear space beside its place with a dark halo, never over another stamp
   (`decisions.md`, "A world map"); a phone-portrait and a desktop layout; its first use a lesson on its own control.
   (c) The stamps for the first sheet, looked at before they ship. Fits into: Town map and world map (its first
   caller; a module until a second caller or variant), the page shell (a sheet), Unlocks, Lessons. Accept: the
   section's numbered acceptance tests; composites at 390×844 and 3840×2160, light and dark, looked at; nothing
   reachable only by hover.
8. **An order card on a ruled lane tapping a staged lane card** (**S**, opening; engine only if needed). Week 2's
   item 7 put a chip's order card on a ruled lane; here an `at_least` order card on a ruled lane taps a staged card on
   that lane. Check the loader accepts it and the page offers it under its store's line; that at the cap it is passed
   over and the lane goes to its next rule. Extend only if refused. Fits into: Standing orders, Lanes. Accept: a fixture
   lane build of three stages run by its order lands all three and leaves the lane on its next rule; a planted card
   tapping another lane's card fails the loader.
9. **A stage's finish raising a standing's rate** (**S**, opening and tests). Each finished stage of a staged card adds
   an entry on a standing's make rate (an outcome modifier aimed at a standing runner). Check the loader and `explain()`
   take a standing as the target, each stage's entry sourced; the season check still passes with the standing on its
   own pool. Fits into: Modifiers, Standing actions. Accept: a fixture of three stages raising a standing's rate shows
   three sourced entries and the summed rate; the standing stops at its pool's end with the entries kept, and runs at
   the same rate when the pool refills.
10. **A second magic skill opening on its first card** (**S**, opening and client). The skill row arrives with B15's
    outcome; its first card is a cure for the season's chip, offered with its own order card beside the chip's
    existing one; its first use is a lesson on the card. Check the per-skill pacing check covers the new skill and that
    two order cards on one chip are offered side by side. Fits into: Pacing curve, Cards, Chips, Lessons. Not the
    Spells row: nothing is combined yet. Accept: the skill check passes with the row; a fixture chip with two order
    cards offers both while uncovered and neither once one is set.
11. **Week 2's edge card** (**S**, content). Nothing to edit: the content's one end card moves to week 3's first
    chapter's `end_feature` when it ships in `CHAPTERS`.
12. **The chapters** (**M** each, content): `day_fifteen.toml`, `day_sixteen.toml`, `day_eighteen.toml`,
    `day_nineteen.toml`, each with its clocks and floors, builds, order cards, offers, fights, side layer, Camp levels,
    aims, journal notes, end card, and its `beats.yaml` twin (item 13). Accept, each: the loader and the lock pass; the
    fight, chip and season checks pass; item 6's band holds for the chapter's beat; density targets hold on typical;
    the cap-loss check passes at the chapter's end or names the store that fails, with the content's lever applied
    before any sink is added; per absence at most two unlocks; a save rebased from each earlier chapter's end loads and
    plays on.
13. **`beats.yaml` and the flat check** (**S**, content and `content/team/flatcheck.py`). The chapters' twin lists
    (week 3's ids T1-T13), side entries SL22-SL28, the spine entries' changed gates (B15, B16, B17) and their `pays`,
    and the accepted exceptions. Accept: the flat check on the authored order raises nothing for week 3 beyond the
    accepted exceptions; a planted entry with a third turn in a row is flagged.
14. **Lines** (**M**, content, one batch per chapter, one for the journal's notes, one for a pool of lines after a yes).
    From the brief once item 6's `--lines` exist. Accept: every key filled; the code checks pass.
15. **Art** (**M**, after item 12's ids settle). The grades (the new season, two story nights), world layers, made
    things, figures, two journal sketches and the first map sheet's stamps, picked from the packs first
    (`sprite-catalog`); two transient ids for poses; stages 53-66 in `tools/scene`. Accept: composites at 390×844 and
    3840×2160, looked at.

## Where this meets the other plans

- **Week 2** (`week-two-plan.md`): its "After week 2" questions are answered here: the dry share is item 1; the next
  tier's project takes the stores week 2's numbers file names; the journal grows by entries and notes on places.
  Week 2's content open item on retiring a season's chore rule is item 3.
- **Combat** (`combat-plan.md`): the season's threat step is the ramp idiom; item 4 is a story's leave, so the KNOWN
  GAP for whole losses that are people from a fight's tally stays open; capped fights, stance and who you bring stay
  open (week 3 needs none).
- **Banked time** (`banked-time-plan.md`): its cap-loss target is held at each chapter's end (item 12); item 1 makes a
  spent pool's share go to work instead of idling, which is the same lost time seen from the mix.
- **Open work**: item 7 is the map's first piece; issue #30 (journal pages) gains two entries.

## After week 3, where it plugs in

- **The next season's turn** at 504 h retires week 3's chore rules (item 3 applies unchanged) and refills nothing of
  week 3's pools; item 1 hands their shares on.
- **B18** opens week 4. Its gate is the next region open alone, which B17 meets at once, so week 4 adds its floor.
- **The map** gains a place per region reached; the Regions row's engine state is built when a second region's
  threat ramp needs time-in-region as a policy rather than a clock store.
