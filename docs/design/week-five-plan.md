# Week five: what engineering builds

Week 5, from the season after's second turn at save time 672 h to the end of story day 35: four chapter files. Its
design is in `content/` (`team/week-five.md`, `-numbers.md` and `-lines-brief.md`, never shown to the owner); this file
holds only what the code needs. Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a
week or more. Week 5's chapter beats are Y1-Y15 (one letter a week, as week 4's I).

## The chapters

| File | Spans | Lands | Carries |
|---|---|---|---|
| `day_twenty_nine.toml` | Y1 → B22 | B22, the finish of a one-off either answer of an offer runs, held to the season's clock | the season's second turn (item 1), the last season's chip machinery drained, a returning chip with no order card offered, a two-answer offer whose answers both move the beat, the outpost and its supply line (item 2), a risen notable cast from counts (item 3), the week's second trip and its twin, Y1-Y3, SL37 |
| `day_thirty.toml` | B22 → B23 | B23, a glowing story step held to the season's clock | a standing fight on the supply line and the cards that hold its side, a second season chip with cures and no order card, a finite pool and the card on it, a new input store and the cards that make it, a card that holds the gap's side, the working that resolves a chain (item 6, beside the chapter), a story night, Y4-Y7, SL38-SL39 |
| `day_thirty_one.toml` | B23 → B24 | B24, a glowing step after the week's joint project | a second standing fight on the same threat and a staged build adding to its side, the week's joint project and its order card, an arrival offer of the work kind, asks whose yes queues a one-off, Y8-Y11, SL40-SL41, Camp 20 |
| `day_thirty_three.toml` | B24 → night 35 | B25 and night 35, held to the calendar | a glowing step with a level row, the map's places (item 8), a story night with its own short list, Y12-Y15, Camp 21, the end card at the edge of week 5's content |

Each is merged after the one before it (new ids only, the release lock's additive rules). Landing bands are D-93's: B22
typical 672-696 h, B23 720-744, B24 768-792, B25 816-840. Every sharp floor falls before the turn except B25's (687 h),
which its step carries as a save-time requirement. Week 6 opens on the next season's turn at 840 h.

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| A season's second turn | Clock, Triggers, Standing actions, Cards on season pools, Chips | Weeks 2-4's season shape; the season reads the first turn's clock store, offset (no new clock) |
| A returning chore, with no order card | Chips (the hint dot), Standing orders (a rule the player writes) | `docs/design/choice-not-protection.md`, row 43 (decided); the shipped order card is not offered again (item 1) |
| The first outpost and its supply line | Stores, Cards (a trip-shaped card and its town twin), Standing actions (an upkeep that pauses dry), Combat (a standing fight whose losses take a store) | `decisions.md`, "The town": an outpost is a building far away and its upkeep a line in the ledger, no new system (item 2) |
| A risen notable cast from the save's history | People, Unlocks (an only-growing fact), Catalogue (a town card per lane, each requiring its lane's cast), text slots | `decisions.md`, "Nothing appears; everything is made" (people rise into roles); the first cast that reads counts needs an outcome part and a role slot (item 3) |
| Workings as data | Catalogue (an authored entry expanded into cards, as town cards are), Spells | `docs/systems.md`'s Spells row: rules as data; its first slice, deferred until there was something to combine (item 5) |
| A working that resolves a chain on a group threat | Spells, Combat, Triggers (same-instant events under the firing cap), Chronicle | The Spells row's cascades; nothing built resolves a chain (item 6) |
| A place labelled when reached; places revealed together | Town map and world map | The map reveals places one by one, unlabelled or labelled for good (item 8) |

**New engine work:** item 6 (L), and item 3's outcome part (M). Items 1, 2, 5 and 8 are loader checks, wire fields and
page work on existing shapes; everything else is content, the map and the simulator.

## Work, by item

Order: 1, 2, 3 and 5 first (3 interface first, 4 blind beside it); 6 interface first and on its own track, never in
front of a chapter (its chapter ships the card that uses it only once it merges; until then the beat is told and the
card is absent); 8 before `day_thirty_three.toml`; 9 runs alongside each chapter and **first measures the figures the
design estimates at 672 h**; 10 needs 1-3, 5 and 9; 11-13 follow the content; 14 with the last chapter.

1. **The season's second turn** (**S**, opening, client, tests). (a) An `after_time` turn whose outcome refills the
   season's shipped pools and adds a one-item pool a standing drains, which drains the last season's chip store and its
   gift pool within the hour (week 4's `thaw` idiom). (b) No rule is retired at this turn: a rule the player wrote on the
   last season's chip stays, unfired, because its chip cannot show. (c) The season's shipped order card for its returning
   chip is not offered again: check how the page decides to offer an order card whose rule an earlier turn retired; if it
   would offer it again, add an authored field on the order card (offered once), never a match on its id. Fits into:
   Clock, Standing actions, Chips, Standing orders. Accept: a fixture turn drains the old chip store to zero inside the
   hour and the chip never shows after; a player-written rule on that chip survives the turn and fires nothing; a fixture
   order card retired at one turn is not offered at the chip's next showing, and a planted field-less copy is.
2. **The supply line** (**S**, opening, tests). The outpost's store, filled by a trip-shaped card and its town twin from a
   town store; an upkeep standing that draws it and pauses dry; trips and a staged build that take it as an input; a
   standing fight whose losses take it, with two cards that hold its side while they run. Check: the loader's finite
   checks (#438) treat the store as made by an uncapped maker, so no progress gate reading it is flagged; the upkeep
   standing resumes when the store refills; the 2 AM test holds the filling card in the mix. No engine work. Fits into:
   Stores, Cards, Standing actions, Combat. Rejected: a supply-line system with routes or cargo (a second copy of Cards and
   Stores); an outpost state. Accept: a fixture outpost store with its filler, upkeep and a fight lands the same tallies
   watched or away; a planted progress gate on a store whose only maker is a finite pool is flagged.
3. **A role cast from per-lane counts** (**M**, engine, opening, api, client; interface first: a section "CASTING" in
   `api/contract/`). (a) Content: an outcome part `casts` with a role id, one or more town-card patterns in priority order
   and the eligibility rule (single lanes only, never a group, never a lane already cast). (b) At the outcome's instant
   the engine picks the eligible lane with the most completions of the first pattern's card on that lane; a tie or none
   goes to the next pattern; then the earliest join. It unlocks feature `<role>_<lane>`, an only-growing fact, so a
   rebase replays the same cast. (c) A lane's `later_labels` may key on that feature; a town card expanded on every lane
   may require it. (d) Text: a slot `{<role>}` resolves on the page to the cast lane's name; the loader refuses the slot in
   any text that can show before the casting outcome (`docs/adding-content.md`, item 9: nothing is named before it exists). Fits into: People, Unlocks,
   Catalogue, text and numbers. Rejected: a fixed person (the role's words would be false on a route where that lane never
   did the work); a model choosing (behaviour is never a model's); the page choosing (the client never decides what
   exists). Accept: a fixture with three lanes and planted counts casts the expected lane, the tie and none cases go down
   the order, a group with the highest count is passed over, the cast survives a rebase, and a planted text using the slot
   before the cast fails the loader naming the key.
4. **Blind contract tests for item 3** (**S**, tests), by an agent that never reads item 3's code: from `contract/`
   "CASTING" alone, with a `MUTANTS.txt` (counts a group; breaks a tie to the latest join; reads the total over all lanes
   instead of per lane; recasts when counts change later; resolves the slot before the cast). Accept: each mutant goes
   red; ambiguities answered in `contract/` before item 3 merges.
5. **Workings as data** (**M**, opening, tests). A chapter's `[[workings]]` entry (the axes the content's rules name, an
   optional input store, its base bar and skill) is expanded by the loader into one ordinary card, as `[[town_cards]]`
   are; its cost is a pure function of those axes, read from a rules table in data, so a new working is a data row. The
   two shipped working cards stay as they are (released); a parity test computes their rows and matches their shipped
   costs. Fits into: Catalogue, Spells (first slice). Rejected: an interpreter at runtime (the engine sees only cards);
   re-expressing the shipped cards (a release break for no behaviour). Accept: a fixture working expands to the expected
   card; changing one axis changes its computed cost by the table's step; a planted entry whose declared cost differs
   from the computed one is refused naming the id.
6. **A working that resolves a chain on a group threat** (**L**, engine, opening, api, client, tests; interface first: a
   section "SPELLS" in `engine/design/` and `api/contract/`). The content contract: a working cast on a threat the content
   marks as a group (several members, fought one after another) resolves, at its finish, a chain of that threat's due fights, up to the working's reach, each
   one won and each its own chronicle line, in one instant under the firing cap; the reach is on the card before the tap
   ("reaches up to n"), from the skill's level pays and the input the working takes; chance never sets the length.
   The engine design names what "due" means for a standing fight (fights are flows, never events: design/fights.txt
   "FIGHTS"), so the chain is exact against the tallies. Fits into: Spells, Combat, Triggers, Chronicle. Rejected: a
   timed bonus on the side (no chain, nothing runs); a random chain length (`decisions.md`, "Chance decides how nice,
   never how far"); an event per fight in the engine (FIGHTS' REJECTED). Accept: a fixture group threat with a known due
   count lands a chain of min(due, reach) won fights and as many lines; the same chain queued and landed while away; the
   reach shown equals the reach run; a planted random length and a planted chain past the firing cap each go red; nothing
   on the page totals the chain beyond the served tallies.
7. **Blind contract tests for item 6** (**S**, tests), from `contract/` "SPELLS" alone, with a `MUTANTS.txt` (a chain on a
   threat not marked a group; a chain longer than due; a reach shown that differs from the reach run; a chain that draws
   on the engine's random state; lines folded into one). Accept: each mutant goes red.
8. **The map's places** (**S**, content, client). (a) A place first shown unlabelled takes its label when a later unlock
   the content names is reached (an authored field on the place). (b) One outcome reveals several places at the larger
   scale together, one of them sitting on an existing place (a stamp on a stamp); unlabelled. (c) Two more places
   revealed by a beat and a skill find. Accept: the map checks pass; composites at 390×844 and 3840×2160, light and dark,
   looked at, with the earlier places.
9. **The simulator through week 5** (**M**, tests). First: store night 28's ends for sharp, typical and whenever, and
   post the figures the design estimates at 672 h (every store, level and the joint project's stage) on the issue before
   any chapter's numbers are set. Then week 4's routes played on through the four chapters to the visit night 35's beat
   lands in: policies that write a rule for each chip at its first showing (none for lazy), hold the filling card and the
   week's second trip in the mix at a route's share, put the cast notable's card on the line by a route's choice, answer
   the two-answer offer in the visit it shows (the yes on typical, the other answer once on sharp, so both paths are
   measured), accept both builds' order cards, answer the arrival offer by the kind's rule where set, answer the asks, tap
   or queue the glowing steps, and make the new input store by a route's choice. Readouts: the four bands, the per-visit decide
   counter (the target is every visit; day 25's chapter measured 5 of 12), per-absence counts, the cap-loss readout at
   each chapter's end, the 2 AM test across the week, the preparation checks (the line held against unheld; the gap with
   the new card against without), the cast lane per route, the chain's length per cast once item 6 ships, calendar days,
   sharp's decision ratio, and `--lines` state lists. Fits into: Simulator. Accept: every band inside on typical; a planted
   visit whose only change is a queued stage fails the decide counter; a planted fixture whose filling card opens before
   its outcome's beat fails the unlock-order check.
10. **The chapters** (**M** each, content): the four files, each with its clocks, builds, order cards, offers, fights,
    side layer, Camp levels, aims, journal notes, end card, and its `beats.yaml` twin (item 11). Accept, each: the loader
    and the lock pass; the fight, chip, season and finite checks pass with every week-5 pool listed as feeding nothing
    progress needs; item 9's band holds for the chapter's beat; density targets hold on typical; per absence at most two
    moments; a save rebased from each earlier chapter's end loads and plays on. The season's thaw standing (item 1)
    costs the old chip store and its gift pool together, so it stops when either runs dry: size them equal at the turn,
    or the other is left over.
11. **`beats.yaml` and the flat check** (**S**, content). The chapters' twin lists (Y1-Y15, a night list for the last
    two), side entries SL37-SL41, the spine entries' changed gates and `pays` (B22-B25), B25's system unlock removed
    (prestige ships already), and the accepted exceptions recorded as accepted. Accept: the flat check raises nothing for
    week 5 beyond them; a planted entry with a third turn in a row is flagged.
12. **Lines** (**M**, content, one batch per chapter, one for the journal's notes, one small for item 6's chain lines when
    it ships). From the brief once item 9's `--lines` exist. Accept: every key filled; the code checks pass.
13. **Art** (**M**, after item 10's ids settle). The season's grade and two story nights, world layers, figures and five
    transient ids for poses (one posed on whichever lane item 3 cast: the pose keys on the transient id, never a lane),
    three journal sketches and the map's stamps, picked from the packs first (`sprite-catalog`); stages 84-102 in
    `tools/scene`. Accept: composites at 390×844 and 3840×2160, looked at.
14. **Week 4's edge card** (**S**, content). Nothing to edit: the content's one end card moves to week 5's last chapter's
    end feature when it ships in `CHAPTERS`.

## Where this meets the other plans

- **Week 4** (`week-four-plan.md`): its "After week 4" is answered: the turn at 672 h retires no rule (a player-written
  chip rule stays, unfired: item 1 (b)); B22 opens week 5 on the joint project's last stage, the turn and a one-off; its
  system (outposts and supply lines) is item 2, with no engine work; the map gains places by item 8.
- **Banked time** (`banked-time-plan.md`): the week's second trip is the trip shape again, its input an outpost's store.
  "Who goes" stays a KNOWN GAP: every trip this week is one person.
- **Combat** (`combat-plan.md`): two standing fights on one new threat; item 6 is the first content to resolve fights as a
  chain. "Whole losses that are people" stays open.
- **Prestige** (`prestige-phases.md`): the first skill may reach its phase's top this week on typical; the click is the
  player's, shipped. B25's old system unlock is dropped (item 11).
- **Choice, not protection** (issue #37 (g)): item 1 (c) closes the last shipped order card offered for a chore.
- **Issue #438** (finite resources): item 2's check, and item 10's acceptance runs its content check.
- **Open work**: issue #30 (journal pages) gains three entries and a sketch page.

## After week 5, where it plugs in

- **The next season's turn** at 840 h drains this season's two chip stores (item 1's shape) and retires no rule.
- **B26** opens week 6: the next joint project, reached from B25's place. Its build is week 6's.
- **The Spells row** grows a second group threat and more workings as data rows (item 5's table); the interpreter of
  item 5 never moves into the engine.
