# Week four: what engineering builds

Week 4, from the next season's turn at save time 504 h to the end of story day 28: four chapter files. Its design is in
`content/` (`team/week-four.md`, `-numbers.md` and `-lines-brief.md`, never shown to the owner); this file holds only what
the code needs. Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a week or more.
Week 4's chapter beats are I1-I13 (one letter a week, as week 3's T).

## The chapters

| File | Spans | Lands | Carries |
|---|---|---|---|
| `day_twenty_two.toml` | I1 → B19 | B19, a find on the week's trip held to the season's clock | an addition keyed on week 3's last feature (the trip shown unready), the season's turn and its content, the last season's chores retired (week 3's retirement part, unchanged), a chip with cures and no order card (item 4), a gift card on a finite pool, a raised cap on the arrivals' count (item 9), the first expeditions: a trip, its town twin, a shared count store, a new skill (item 5), I1-I4, SL29-SL30 |
| `day_twenty_three.toml` | B19 → B20 | B20, a glowing story step held to the season's clock | a fixed notable joining as a lane with a later label, a two-answer offer whose second answer unlocks the one-off the first queues (item 3), an arrival offer of the work kind, the week's joint project and its order card, a story drain, asks whose yes queues a one-off, a second card for the second magic skill, a story night, I5-I7, SL31-SL33 |
| `day_twenty_five.toml` | B20 → B21 | B21, a clock after an arrival | a player-only fight trip whose losses are told from pools of its own (item 1), the next region's first threat step on its clock store, two arrival offers forming pooled groups (item 6), a fixed notable joining, I8-I10, SL34-SL35, Camp 19 |
| `day_twenty_seven.toml` | B21 → night 28 | night 28, held to the calendar | a story night and its glowing step, I11-I13, SL36, the map's places (item 8), Camp 20, the end card at the edge of week 4's content |

Each is merged after the one before it (new ids only, the release lock's additive rules). Landing bands are D-93's: B18
typical 504-528 h, B19 528-552, B20 576-600, B21 624-648; every sharp floor falls before the turn or the season's clock
that holds the beat, so no beat gets a save-time floor. Week 5 opens on the season after's turn at 672 h, and B22 (the
joint project's last stage) waits on that turn.

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| The third season's first turn as content | Clock, Gates, Standing actions, Cards on season pools, Triggers, Chips, Combat (a threat step on the season's clock) | Weeks 2 and 3's season shape; the season check runs on it unchanged |
| A season chore with no order card | Chips (the hint dot), Standing orders (a rule the player writes on a chip condition), the simulator's policies | `docs/design/choice-not-protection.md`, row 43 (decided): the chore arrives with its problem and a hint; the rule is the player's (item 4) |
| Expeditions into the next region: a trip, its town twin, finds on a shared count | Cards (the trip shape), Triggers (finds on a store), Stores (a count every trip adds to), the Pacing curve (a new skill row), Town map and world map (places by unlock) | design/banked-time.txt "BANKED TIME": a trip is an uncapped card with inputs; a town twin is the existing `{lane}_` expansion. Backup ("who goes") stays a KNOWN GAP: every trip this week is one person (item 5) |
| A fight whose losses are told from its own pools | Combat (a FightDef's lost tally), Chronicle and unwrap (the loss lines), Knowledge (the composer's notes from history), Catalogue (two authored fields) | The engine already pays a lost fight as a wasted attempt and counts it exactly; what is new is how the page tells it, keyed on authored fields, never a card's name (item 1) |
| An offer whose "not now" leaves its one-off on the tasks | Offers (an answer's outcome unlocks a card; the other answer queues it), Cards, Unlocks (a feature at the card's finish) | Day 9's queued one-off and an answer's unlock, combined; no blind permanent choice (item 3) |
| Arrivals that join as a pooled group | Offers (the work kind), Triggers (joins), GROUPS (a pooled lane over members' lanes), People (`told`: line or mention) | GROUPS was built for people; week 3's arrivals joined one lane each (item 6) |
| A raised cap on a count store | Modifiers (a cap entry sourced by the turn) | A released store's cap is never edited (the release lock); an outcome cap entry is the existing way (item 9) |
| The next region's threat ramp | Combat (a trigger on R2's clock store aiming at a threat's strength) | D-138: still a clock store, no region state |

**New engine work: none.** Items 1, 3, 5 and 6 are loader checks, wire fields, page and journal work on existing
shapes; everything else is content, the map, and the simulator.

## Work, by item

Order: 1-2 and 4-6, 9 first (they change no content; 2 blind, beside 1); 3 with `day_twenty_three.toml`; 7 runs
alongside each chapter; 8 before `day_twenty_seven.toml`; 10 needs 1 and 3-9; 11-13 follow the content; 14 with the
first chapter.

1. **A fight whose losses are told from its own pools** (**M**, opening, api, client, journal; interface first: a
   section "LOSS LINES" in `api/CONTRACT.txt`). (a) Content: a fight card's `fight` table may carry `loss_pool` (a line
   pool's key, used for its lost labels instead of the shipped lost pool) and `loss_notes` (a journal note pool), and an
   `on_loss_key` for the card's on-loss wording. The loader refuses them on a town card, on a card with a town twin, on a
   standing fight, on a card whose `only_player` is not `"self"`, and on a card that can be unlocked before a feature the
   chapter names (`loss_after`). (b) The wire: the three keys on `CardInfo.fight`, absent for an ordinary fight. (c) The
   page: the card's on-loss line reads its key; the chronicle's lost labels for that runner draw from its pool; a scene
   pose keyed by a transient id. (d) The journal: the composer adds one margin note per whole unit the runner's lost
   tally crosses on a day, from `loss_notes` by a shuffle bag keyed by (save, stream, n) from Chance, never the engine;
   one shown per day's page, the rest folded into a count line in the journal's register; a trigger's own note from the
   same pool counts as the first draw. No engine change: the lost tally, the odds and the wasted inputs are FIGHTS' as
   built. Fits into: Combat, Chronicle and unwrap, Knowledge, Catalogue. Rejected: an event or timer in the engine (an
   instant per fight: design/fights.txt "FIGHTS", REJECTED); a loss that takes stores or levels beyond the attempt's inputs, or
   adds a wounded store (the content's guardrail); keying the telling on the card's id or name (no behaviour from
   names: authored fields); notes per loss without a fold (a long absence would write a page of them). Accept: a
   fixture with a pooled card and a plain fight card: the pooled card's labels come only from its pool and the plain
   card's never do; each planted loader refusal fails naming the id; the composer writes exactly one note per unit
   crossed and the same notes on every read of the same day; a long absence folds to one note and a count line; nothing
   on the page totals these losses beyond the served tally.
2. **Blind contract tests for item 1** (**S**, tests), by an agent that never reads item 1's code: from `CONTRACT.txt`
   "LOSS LINES" alone, with a `MUTANTS.txt` (labels a plain fight's loss from the card pool; notes per fight instead of per whole
   unit; draws notes from the engine's state; repeats a note in a row; folds nothing). Accept: each mutant goes red;
   ambiguities answered in `CONTRACT.txt` before item 1 merges.
3. **An offer whose second answer leaves the one-off** (**S**, opening). One answer queues a capped hands card (and
   unlocks it); the other unlocks the same card without queuing it; the card's finish unlocks a feature, which later
   content reads instead of the answer. Check the loader and the ask checks accept it, and that the page shows the
   unqueued card in the Tasks list from the answer on. Extend only if refused. Fits into: Offers, Cards, Unlocks.
   Accept: a fixture offer answered each way ends with the card unlocked; tapped later, the feature lands the same as
   on the first answer; a planted later gate reading the answer instead of the feature is flagged by a content check
   that no gate reads this offer's answers (an id list beside the offer, `gates_read_feature`).
4. **A season chore with no order card** (**S**, opening, client, tests). The chapter's chip has cures and no
   `[[order_cards]]` entry. Check the loader's chip and season checks pass without one; that the page's hint dot shows on
   the chip's first showing with no card offered; and the simulator's policy writes a chip-condition rule (the cure on
   the route's chosen lane) at the chip's first showing for the tool-using routes, none for lazy. Fits into: Chips,
   Standing orders, the Simulator. Accept: a fixture chip with no order card loads; the 2 AM test is level with the
   policy's rule on babysitter and whenever; a planted policy that writes the rule only when present at the instant the
   chip shows goes red.
5. **Expeditions: a trip, its town twin, a shared count, a new skill** (**S**, opening, tests). The trip is an uncapped
   hands card with inputs whose outcome adds to a count store (never drawn); its town twin carries the same outcome; finds
   are triggers on the count store. Check: the player-only check takes the twin (`twin_of`); a find's trigger on a
   store some uncapped card's outcome makes is accepted by the find checks; the per-skill pacing check covers the new
   skill row from its first card; the 2 AM test holds a trip in the mix with finds landing away. Fits into: Cards,
   Triggers, Stores, Pacing curve. Rejected: finds on each card's own count (a find would wait on whoever the player
   sent); a roster or destination state (design/banked-time.txt "BANKED TIME", REJECTED). Accept: a fixture of a hands trip and a twin on
   one lane lands its nth find at the same instant however the count is split between them; a planted twin with a
   different outcome fails the player-only check. **Meets #438:** the count store always has room, so a trip whose
   material makes are at their caps keeps running and keeps counting under the rule that a job does not spend inputs on
   an outcome lost *entirely* to caps. If #438 lands as "any full output pauses the job", finds would stall at a full
   material store: check this item's fixture against #438's final rule before either merges.
6. **Arrivals that join as a pooled group** (**S**, opening). An offer of the work kind whose answer's outcome joins
   several lanes and a group naming them as members, the group's share set by the answer, `told = mention` on the
   members allowed (the loader gives the outcome its mention line). Check the people and group checks accept it and the
   kind's rule answers it while away. Extend only if refused. Fits into: Offers, GROUPS, People. Accept: a fixture group
   of four joins on either answer with the answer's share; a planted group joining a lane already in another group fails
   the group checks.
7. **The simulator through week 4** (**M**, tests). Week 3's routes played on from night 21's saved ends through the four
   chapters to the visit night 28's step lands in: policies that queue the trip from the visit it shows and hold it in
   the mix at a route's share (and a twin on one lane), write the chip rule (item 4), accept the joint project's order
   card, answer the arrival offers by the kind's rule where set, answer the asks and the two-answer offer in the visit
   they show (one "not now" on sharp, then the card tapped two visits later, so both paths are measured), tap or queue
   the glowing steps, and put the pooled fight in the mix by a route's choice; the per-visit counters, per-absence counts,
   the four bands, the cap-loss readout at each chapter's end, the 2 AM test across the week, the preparation check
   through the season's step, calendar days, item 1's told losses per day per route (a readout), sharp's decision ratio, and `--lines`
   state lists. Store the night-21 ends for sharp as well as typical and whenever. Fits into: Simulator. Accept: every
   band inside on typical; a planted fixture whose trip opens at the turn instead of at the prior visit fails the 2 AM
   test; a planted visit whose only change is a queued stage fails the decide counter.
8. **The map's places** (**S**, content). Four `[[places]]` across the chapters, revealed by unlocks (a beat's feature, the
   project's card, two skill finds), one unlabelled. Accept: the map checks pass; composites at 390×844 and 3840×2160,
   light and dark, looked at, with the earlier places.
9. **A raised cap on a count store** (**S**, opening, tests). The turn's outcome carries a cap entry on the arrivals' count
   (×2, sourced). Check the arrival checks and People read the effective cap, not the store's base, and nothing on the
   page draws the count. Accept: a fixture past the base cap counts the next arrival; a planted check reading the base cap
   goes red.
10. **The chapters** (**M** each, content): the four files, each with its clocks, builds, order cards, offers, fights,
    side layer, Camp levels, aims, journal notes, end card, and its `beats.yaml` twin (item 11). Accept, each: the loader
    and the lock pass; the fight, chip and season checks pass; #438's finite-supply check passes with every week-4 pool
    listed as feeding nothing progress needs; item 7's band holds for the chapter's beat; density targets hold on
    typical; per absence at most two moments; a save rebased from each earlier chapter's end loads and plays on.
11. **`beats.yaml` and the flat check** (**S**, content and `content/team/flatcheck.py`). The chapters' twin lists (week 4's
    ids I1-I13), side entries SL29-SL36, the spine entries' changed gates (B18, B19, B20, B21) and their `pays`, and the
    accepted exceptions. Accept: the flat check on the authored order raises nothing for week 4 beyond the accepted
    exceptions; a planted entry with a third turn in a row is flagged.
12. **Lines** (**M**, content, one batch per chapter, one for the journal's notes, one for the two pools item 1 reads).
    From the brief once item 7's `--lines` exist. Accept: every key filled; the code checks pass.
13. **Art** (**M**, after item 10's ids settle). The season's grade and two story nights, world layers, figures, three
    transient ids for poses, two journal sketches and four map stamps, picked from the packs first (`sprite-catalog`);
    stages 67-83 in `tools/scene`. Accept: composites at 390×844 and 3840×2160, looked at.
14. **Week 3's edge card** (**S**, content). Nothing to edit: the content's one end card moves to week 4's last chapter's
    end feature when it ships in `CHAPTERS`.

## Where this meets the other plans

- **Week 3** (`week-three-plan.md`): its "After week 3" is answered: the turn retires week 3's chore rules (its item 3,
  unchanged) and refills none of its pools; B18 opens week 4 on the trip's first finish; the map gains four places.
- **Banked time** (`banked-time-plan.md`): item 5 is the Expeditions row's first content past day 3's track. Its KNOWN
  GAP "Who goes" names R2's first expedition with backup as the decider; week 4's trips are all one person, so the
  decider moves to the first expedition whose fight needs a side made of who goes (week 7, by the spine): a one-line
  edit to design/banked-time.txt "BANKED TIME" when item 5 lands.
- **Combat** (`combat-plan.md`): item 1 uses the lost tally as built. "Whole losses that are people" stays open (nobody
  goes with the player); capped fights and stance stay open.
- **Issue #438** (finite resources): item 5's note above; item 10's acceptance runs its content check.
- **Choice, not protection** (issue #37 (g)): item 4 is its first chore written to row 43.
- **Open work**: issue #30 (journal pages) gains three entries and a notable's own pages.

## After week 4, where it plugs in

- **The season after's turn** at 672 h retires nothing (week 4's chore has no rule of the game's making; a rule the player
  wrote on its chip is theirs, and the retirement part is the game's tool for the season's own order cards, so week 5
  must decide whether a player-written chore rule retires with its season: `decisions.md`, "Each season brings its own
  chores", says it "probably" does).
- **B22** opens week 5: the joint project's last stage and the turn. Its system (outposts and supply lines) is week 5's.
- **The map** gains a place per region reached and per find; the Regions row's engine state still waits for a region
  whose ramp needs time-in-region as a policy.
