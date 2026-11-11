# Week two: landing bands, targets and the arithmetic behind them

Spoilers: under `content/`, never shown to the owner. Ids and numbers only, no lines. The spec is `week-two.md`. **Nothing
here is measured.** No simulator runs past night 7 yet (`docs/design/week-two-plan.md`, item 1), so every figure is a
target or an estimate built on `days-four-to-seven-numbers.md` and its measured notes; the simulator replaces each.
Where an estimate rests on another estimate, it says so.

## Landing bands

D-93 (`pace_scale` 1.0), hours from the save's start. Week 2 opens on the calendar (B8 at 168 h), so sharp's lead from
week 1 is spent on extra visits, and every play-driven beat below needs a floor.

| Beat | Target day | Typical band | Sharp floor | Estimate, typical | Estimate, sharp |
|---|---|---|---|---|---|
| B8 (clock) | 8 | 168 | 168 | 168 | 168 |
| B9 | 9 | 192-216 | 169 | 193-202 | 180-182 |
| B10 ★ | 11 | 240-264 | 209 | 238-250 | 209 (the floor binds) |
| B11 | 12 | 264-288 | 229 | 266-280 | 234-236 |
| B12 | 13 | 288-312 | 249 | 286-298 | 249 (the floor binds) |
| B13 (clock, week 3) | 15 | 336 | 336 | 336 | 336 |

Week 2's end (S4, night 14) is not a spine beat; its dusk is held to the calendar (330 h). Lazy lands B10 near 300 h and
B11 and B12 after 336 h, inside its 1.17× band; the chapters hold for it (S3 and S4 do not wait on B12).

## The chain that holds each floor

| Clock or gate | Condition | Starting value | Sharp | Typical |
|---|---|---|---|---|
| the palisade shown | G2's visit (`still_end`) | | 150-160 | 160-166 |
| B8 | `after_time` 604 800 s | 168 h | 168 | 168 |
| U1 | B8 + 6 h | | 174 | 174 |
| U3 | `r1_clock` ≥ 70 (combat's clock from A27) and `drift_clock` ≥ 12 | 70 h | 180-182 | 192-201 |
| B9 | `entries` ≥ 3 (the first pack fight, about an hour after U3) | | 181-183 | 193-202 |
| E1 | B9 + 2 h | | 183 | 195-204 |
| B10 | `palisade` stage 12 and save time ≥ 209 h (752 400 s) | 12 × 24 stakes | 209 | 238-250 |
| Z1 | the hut done (10 800 s after O-family's answer) | | 212 | 241-256 |
| Z3 | `stranger_clock` ≥ 20 | 20 h | 232 | 261-276 |
| dusk 12 | `stranger_clock` ≥ 22 and save time ≥ 228 h | | 234 | 263-278 |
| B11 | A31 (night 12 ≥ 5, guard made), queued When ready | | 234-236 | 264-280 |
| B12 | `dig_cellar` stage 4 and save time ≥ 249 h (896 400 s) | 4 × 12 stakes | 249 | 286-298 |
| S3 | `drift_clock` ≥ 150 (built; was `r1_clock` ≥ 175) | 318 h | 318 | 318 |
| dusk 14 | save time ≥ 330 h (1 188 000 s) | | 330 | 330 |

**The levers, in order:** U3's clock for B9; the palisade's stakes per stage and the stakes cards' bars for B10; the
stranger's clock for B11; the dig's stakes per stage for B12. If sharp lands under a floor, the floor is wrong, not the
play: raise its hours. Never lengthen a hands bar to move a band (the mix stops).

**The palisade's arithmetic (estimate):** 12 stages × 24 stakes = 288 stakes, 48 cord, 72 stones, 6 h of hands.
Typical from G2's visit: Lucy and him at half shares on stakes (1800 s a stake on a lane: 2 an hour together) and
`cut_stakes` at 20% of the hands (600 s, with Woodcutting's speed about 1.5×: 1.8 an hour), about 3.8 stakes an hour:
76 h, so B10 near 240-250. Sharp: both lanes whole, her half, the hands at half (about 8.5 an hour): 34 h, under the
floor. Cord is never the binding input on typical (the old man at half a share makes 2 an hour against 0.6 used), only
on a route that leaves him whole on the watch and the hands off `twist_cord`.

## Per visit (density)

The same targets as week 1 (`days-four-to-seven-numbers.md`, "Per visit"), held on typical from B8's visit to S4's.

| Check | Target |
|---|---|
| New things per visit | mean ≥ 6 over each chapter's visits; none under 3 |
| Bigger things | ≥ 1 per visit |
| First new thing | within 60 s of opening |
| Something to spend | ≥ 1 per return: an affordable card taking a store at ≥ 80% of its cap |
| Something to decide | ≥ 1 per visit from content (an answer, a choice of two, a share or rule change that moves which of two goals lands first); queuing a build's stage never counts (lesson 1) |
| Idle | no stretch over 90 s inside the activity window |
| Runs | no run of one card over 3 |
| Effort between bigger things | at most 10 |
| Visits, typical | day eight 4-5; day nine 6-8; day eleven 4-6; day twelve 7-9 |
| Visits, sharp | about 30 over the week (its chapters longer by the floors) |

**The bigger thing in each typical visit** (the design's expectation; the simulator replaces it):

| Visit | Bigger thing | Spend (store near cap) | Decide |
|---|---|---|---|
| G2's | the palisade shown (a new kind of build) | `hide_flaps` (pelts; stakes start at 0) | the town's split: stakes, cord, the watch |
| 8a | B8, U1, the bloom | `fungus_stew` on full fungus; a palisade stage from the night's stakes | her share, picking or roots; accept the stakes order card |
| 8b | U2, SL15 | a palisade stage; `hide_flaps` | her share, ground or picking; the roofs' order card on him or the hands |
| 8c | SL16, Camp 13 | a palisade stage | the old man's share, mending or the watch |
| 8d | U3, B9, the journal | `hand_on_stone` on damp wood; a stage | watch shares against stakes, with the pack's odds on the card |
| 9a | E1 | a stage | the watch against stakes; cord by hand or by him |
| 9b | SL18, the pack's step | `gap_fire` (stones, dry wood) | the gap fire against the palisade's stones |
| 9c | SL17 | `set_snare_4` (wire) | the snare or the wire held; the hunt's share |
| 9d | E2 | re-hang the rack (the hunt's catch) | the hunt's share against stakes |
| 9e | Woodcutting 23, Camp 14's marker | a stage | stakes ahead for the hut against the stone card |
| 9f | E3 | a stage | stakes past the palisade against the watch |
| 9g | B10, O-family | the hut (stakes, ash, pelts, stones) | the answer |
| 11b | Z1, O-guard | the stew pot for eight | the seven-way split; who guards |
| 11c | Z2, SL19 | `n6_posts` (stakes) | his posts against stakes held for later |
| 11d | Z3 | the stew pot | queue the vigil; shares |
| 11e | B11, the dig | a dig stage (stakes) | accept the dig's order card; stakes between the dig and the posts |
| 12a | S1 | a dig stage | her ground against picking |
| 12b | SL20 | `hunt_bear` (smoked) | hunt the bear or not |
| 12c | S2, the bear's page | a dig stage | the bear's share against the wolf hunt's |
| 12d | B12, Camp 15 | roots and fungus with room again | re-tune the larder's makers and the stone |
| 12e | SL21 | `tallow_lamps` (tallow) | lamps or tallow held |
| 12f | finds | the pot, her ground | the hunt against the watch |
| 12g | S3, Camp 16's marker | | queue A32; the watch against gathering |
| 12h | S4, Camp 16 | | (the edge of week 2's content: the exception stands) |

Sharp's extra visits get their bigger thing from Arcana 9-12, Melee 7, Cooking 9 and the Camp markers; a sharp visit with
none gets a find at the level it reaches, never a wait.

## Per absence

At most two unlocks. Night 7 → 8a: B8 (with its cards, one moment) and U1. 8c → 8d: U3 and B9. 9c → 9d: E2 alone. 11c →
11d: Z3 alone (dusk 12 is a clock, not an unlock). A return that brings O-family answered by its rule and Z1 together
counts two. SL15 and SL16 sit at B8 + 12 h and + 14 h so night 7's return holds two.

## Cap loss, per chapter end

Target, as week 1: from each chapter's last decision on typical, an 8 h and a 24 h absence lose at most half of each
gathered store's making. What drinks each store, by chapter:

| Store | Day eight | Day nine | Day eleven | Day twelve |
|---|---|---|---|---|
| damp wood | `hand_on_stone` (held); stakes on two lanes and the hands; cord | the same | stakes on three lanes; the hut | stakes; the dig's shoring |
| stones | the palisade (6 a stage); the track | the palisade; `gap_fire` | the hut (12) | the track |
| roots | five mouths; the rats; the track | the same | eight mouths | eight mouths; the rats, less after B12 |
| fungus | `fungus_stew` | the same | the pot for eight | the same; B12 raises its cap |
| stakes | the palisade (24 a stage, run by its order) | the same | the hut (24); `n6_posts` (12) | the dig (12 a stage) |
| ash | her ground (4 a run, uncapped till `ashed_ground` 24) | the same | the hut (12) | her ground |
| pelt | `hide_flaps` (2 a stage) | `hide_flaps`; E2's strip | the hut (4) | (week 3's hall) |
| tallow | | | | `tallow_lamps` |
| smoked | the pack, the crows, the hunt | the same; E2's strip | the same | the bear hunt |

**Stakes on lanes are run by an order card** offered under the stakes line once a second lane cuts them: "under 20
stakes, {lane} cuts stakes, until 24" (D-91's at_most shape), so a full stack sends the lane to its next rule instead of
filling past the cap. The same for picking: "under 20 fungus, {n3} picks, until 24".

**Expected verdicts, by arithmetic only:** stakes, stones and damp wood pass while the palisade runs (288 stakes take
about 1 150 damp wood over the chapter). Ash is likely to fail day eight's 24 h absence before her card has run (about
12 ash a day, cap 24): the lever is the clear's yield, then SL15's gate. Pelt likely fails day twelve's 24 h absence
(the bear adds 2 a hunt, nothing takes them after the hut): the lever is the hunt's pelt yield; week 3's hall is the
sink. Roots as week 1 measured (15-27%).

## Odds targets (combat)

loss_bp = T / (T + P) (engine `DESIGN.txt`, "FIGHTS"). "Watch" is the watch shares' entries at the shares the
typical policy sets (n4 at half, the others off), "ring" the palisade's stages built.

| Fight | Prepared | P : T | Loss share | Expected losses in 24 h |
|---|---|---|---|---|
| `pack` | U3: bare gap, watch | 5 : 8 | about 3 in 5 | 15, 15 smoked |
| `pack` | half the ring, watch, after the step | 17 : 10 | about 1 in 3 | 9 |
| `pack` | the ring closed, watch, guard | 35 : 10 | about 2 in 9 | 5 |
| `pack` | and the gap fire, the posts, the lamps | 41 : 10 | about 1 in 5 | 5 |
| `rats` | the floor, the Drift's step | 16 : 6 | about 1 in 4 | 7, 14 roots |
| `rats` | and the cellar | 24 : 6 | 1 in 5 | 5 |
| `hunt_bear` | spear, Melee 4 | 22 : 16 | about 2 in 5 | at most 6 hunts this week |

The preparation check (combat-plan item 9, extended): a route that builds the palisade and sets a guard loses
measurably fewer pack fights over day nine to night 14 than one that leaves the gap bare; the cellar likewise against
the rats.

**`hurt` with a draining cure (G7, G8; applied).** No fixed take gives a cure tappable at every shown level that
clears in one tap with hurts stacking (engine `DESIGN.txt`, "DRAINS", FIT PASS), so `b7.toml` uses a drain and the
loader's fractions: `hurt` stays whole items, cap 3; `hunt_wolf` still wounds 1; `heal` costs
`{ items_per_hour = 1, every_hours = 4 }` (one hurt every 4 h, the designed rate); the `hurt` chip's `when` takes
`{ value = 1, every = 4 }` with release the same (shows from a quarter hurt, about 3 h for a first hurt); `poultice`
moves `hurt` from `inputs` to `drains = [{ store = "hurt", items = 3 }]` (one tap clears any level, and taps whenever
the chip shows), keeping its clay and roots as inputs. The store is never drawn: the chip is its face (G8's answer).
The chip sits at a quarter, not lower, because `heal` pauses at 0 and resumes only at one hour of its cost, a quarter
hurt: a lower chip could show with nothing healing it (engine `DESIGN.txt`, "DRAINS", KNOWN GAPS). All retunes of
released b7 ids, Safe under the release lock.

## The 2 AM test

Level across G2's visit to night 14: the palisade and the dig by their order cards; the stakes and picking by their
lanes' order cards; the roofs by their chip's order card; O-family by the arrival kind's rule; O-guard answered in the
visit it shows (a babysitter answers it the instant it shows; the whenever player within one gap; the arm card it
queues is 600 s, and the guard's entry is small against the ring, so the gap must stay inside the preparation check's
noise: the simulator reports it); the vigil and the last night queued When ready from the visit before; the pack, the
rats and the bear as flows. The babysitter and the whenever player end week 2 with the same stores and tallies, or the
report names the visit.

## Placeholders the simulator sets

| Placeholder | Set to |
|---|---|
| U3's `r1_clock` (70 h) | typical lands B9 mid-band |
| the palisade's stakes per stage, the stakes bars | typical lands B10 mid-band; stakes per stage never above the stakes cap at the stage's earliest reach |
| the floors (209, 228, 249 h) | the sharp floors; raise if sharp lands under |
| `stranger_clock` (20, 22 h) | typical lands B11 mid-band |
| the dig's stakes per stage | typical lands B12 mid-band |
| S3's `r1_clock` (175 h) | S3 before dusk 14 on every route |
| the bloom (2000) | typical never empties it by night 14 |
| `ashfall` (2 an hour), the chip (16), the clear's yield (4) | two clears a day; ash's cap-loss verdict |
| bases: `gap` 4, `wolf_pack` 8, `ash_bear` 16; the entries | the odds targets above |
| Camp 13-16 at | typical reaching 13 in day eight, 14's marker in day nine, 15 by B12, 16's marker by S3 |
| `hide_flaps`, `gap_fire`, `tallow_lamps` bars | a stage per typical visit at most |

## Applied numbers (day eight)

What `day_eight.toml` carries where it differs from the targets above, and why. Measured with the week-two simulator
(`python -m tests.weektwo.report`, from `app/`): week one's routes copied at G2's visit and played on to B9's.

| Id | Was (target) | Now | Why |
|---|---|---|---|
| `n4_cord` (new card) | `n4_mend` gains makes (cord) | his own card, 900 s, 2 damp wood → 1 cord | `n4_mend` shipped in day five making nothing, and a store this chapter declares cannot be named from an earlier file. SL16 reads `n4_cord`'s first finish |
| order card `cord` → `n4_cord` (new) | his share on cord | at_most 7, release 11 | Cap loss: with cord as a share, typical's cord sat full and lost over half its making at the chapter's end, 8 h and 24 h (the palisade takes 4 a stage). Run by the rule, a full stack sends him back to the watch (the stakes lanes' shape in "Cap loss") |
| order card `pelt` → `hide_flaps` (new) | stages queued When ready | at_least 2, release 2 | The 2 AM test: queued a stage at a time (one queue entry a stage), the whenever player's stages 2-4 landed 0.8-5.1 h behind the babysitter's; run by the order, 0.8 h each (seed 0), the rest week 1's bedding lead carried in (below). Lesson 1's shape, as the palisade's |
| `t_stakes_full` (new trigger) | the palisade's order card offered at G2 | offered once stakes first reach 24 | As `week-two.md` asks ("offered once stakes first reach 24"): the card needs a feature to be offered after |
| the season's clock (`drift_clock`) | opened by B8 | opened by its own trigger on feature `drift`, the same instant | The season check refuses a standing the turn opens that draws no pool the turn fills; a clock is not something the season brings, and it runs on past it |
| U3's gate | `r1_clock` ≥ 70 and `drift_clock` ≥ 12 | `drift_clock` ≥ 12, requiring feature `pack_near` (`r1_clock` ≥ 70) | A trigger's requires reads unlocks only; the same instant |
| B9's gate | `entries` ≥ 3 | the three entries unlocked (`e_wolf`, `e_ashrat`, `e_crow`) and B7 | The journal contract keeps no `entries` store and no `journal` feature: the book is the opening's `book`, each page's first note is gated on the first pack fight, and a gate reads entries as unlocks |
| `n_rat_2`'s gate | the season's rat step | `drift_clock` ≥ 1 | The step lands before the book opens on every route, so the note is written with the page's first |
| `ash_laden`'s order card | (day one's shape) | at_least on `roof_ash`, the chip's `when` | The loader refused an at_least chip card; it now takes one whose task takes the store |

## Measured (day eight, seeds 0-2)

B9 in hours from the save's start; B8 lands at 168.0 on every route. Typical and sharp read the same on all three seeds;
evenings too (B9 214.0 on each).

| Route | B9 seed 0 | seed 1 | seed 2 | Band |
|---|---|---|---|---|
| typical | 199.8 | 199.8 | 199.8 | 192-216: inside |
| sharp | 187.6 | 187.6 | 187.6 | floor 169.3: above |
| evenings | 214.0 | 214.0 | 214.0 | 192-216: inside, 2 h under the top |
| whenever | 223.5 | 206.7 | 217.2 | not banded |
| babysitter | 181.3 | 181.3 | 181.3 | not banded |

- **U3's clock** (`r1_clock` ≥ 70) is not moved: typical lands under mid-band (204), but evenings, also banded, sits 2 h
  under the band's top, so a later clock pushes evenings out. B9 rides `r1_clock`, combat's clock from A27, so the
  routes' spread is week 1's A27 spread; the season's twelve hours (`drift_clock`) bind only the babysitter.
- **Density (typical, seed 0):** every visit has something to spend (2-8 cards); 1 of 8 visits has a decision once a
  queued stage is refused. Day eight's decisions are share and rule changes that trade the one build against the pack's
  odds or a store, which the counter does not see (it counts a change that moves which of two capped goals lands
  first). Open, for a decision: not tuned.
- **Cap loss at the chapter's end (typical):** passes on all three seeds, with the cord rule above.
- **The 2 AM test (whenever, seed 0):** fails; the babysitter's lead is week 1's bedding carried in (`pelt_bedding` 1-6
  land 7.6-9.4 h sooner), which moves when pelts reach `hide_flaps` (stage 1 19.7 h later, 2-4 0.8 h sooner) and the
  stores downstream. No day-eight step is queued.

## Applied numbers (day nine)

What `day_nine.toml` carries where it differs from the targets above, and the day-eight numbers it moved. Measured with
`python -m tests.weektwo.report typical --nine` (from `app/`): day eight's plays copied at B9's visit and played on to
B10's.

| Id | Was (target) | Now | Why |
|---|---|---|---|
| `palisade` (day eight) | 24 stakes a stage | 16 | B10's band: at 24, typical had 9 of 12 stages at 294 h (stakes about 2.5 an hour from B9); at 16, 278 h. Stakes per stage is the first lever named under "The chain that holds each floor" |
| `{lane}_stakes` (day eight) | 1800 s | 1200 s | The second lever: at 16 a stage and 1200 s, typical lands B10 at 260.5 h. A lane's bar, not a hands bar |
| the palisade's order card, `t_stakes_full` (day eight) | at 24 | at 16 | A stage's worth, as before |
| B10's floor | 209 h | 210 h (756 000 s) | The band's sharp floor is 0.83 × 10.5 days = 209.2 h, past the spec's 209 |
| the pack's step | `r1_clock` ≥ 130 | `drift_clock` ≥ 40 (208 h on every route) | 130 on combat's clock lands near 257 h, after B10, not at 9b; and the ramp check refuses `r1_clock` (the card that opens combat unlocks its standing, so the check counts the clock as made by a card). The season's clock passes it |
| `gap_fire` stage 2 | the watch shares' entries half again (+75% each) | the gap side +25%, flat | No modifier scales a card's held entries; an entry that did would need an engine change. A flat entry is the existing shape |
| `gap_fire`'s order card (new) | stages queued When ready | at_least 8 stones, release 8 | The 2 AM test: queued a stage at a time, the babysitter's stages landed 0.9 h and 2.1 h ahead; run by the order, the test passes. Lesson 1's shape, as `hide_flaps` |
| E2's gate | `palisade` stage 6 and B9 + 6 h | stage 6, requiring the strip's clock standing `e2_clock` unlocked, which `gap_fire`'s first stage or B9 + 24 h unlocks | Requiring the gap fire's showing (B9 + 5 h) put E2 on SL18's instant on any route ahead on the palisade, and whenever seed 2 opened SL17, SL18 and E2 in one absence. The first stage needs the gap fire's order card or a tap, so a visit lies between SL18 and E2; the standing moves only its own unshown store, so its unlock opens nothing (a helper feature would count as an opening) |
| SL17's gate | `field_track`'s run count n5 | 6750 runs, requiring `gap_fire` unlocked (B9 + 5 h) | Typical runs the track about 28 times an hour from 6491 at B9, so SL17 lands near B9 + 14 h (9c); sharp reaches B10 first and meets SL17 in day eleven. Requiring B9 only, a route whose track passed 6750 before B9 met SL17 in B9's own absence (whenever seed 2: with U3's clock and B9, three) |
| Camp 14 | stew 18 → 30 | stew 27 → 36 (×1.3334, as Camp 12's smoked) | Stew holds 27 at B9 (pot shelf and Camp 11, ×1.5 each) |
| Camp 15 | (day twelve) | held "?" at 2 100 000 | A goal on screen past the chapter, as day eight held 14 |
| the flaps' chore (new) | (item 9(b) in `week-two.md`) | `wind_torn` 1 an hour from day nine's `wind` standing (its pool `wind_left`, 168, filled at the turn, so it ends at 336 h), cap 18; `draughty` at 12 (rest −10%); `peg_flaps` / `n1_peg_flaps` take 12 `wind_torn`, 3 pelts, 4 stones; its order card on n1; shown at `drift_clock` 23 (191 h) | Cap loss at day nine's end: without it, pelt lost all its making from 8 h. Shown when due rather than with E3, so it lands in day eight's empty stretch (typical's V36, sharp's first visit after its night). With 3 stakes and shown at 184 h, typical's B10 moved to 266 h, past its band. With 2 cord instead, n4's cord rule took him off the watch often enough that his whole watch share moved the pack's odds by 155 bp at U3's visit (under the counter's 250, so the decide controls' odds step failed); stones sit full through most of the Drift and nobody's rule makes them, so stones replace the stakes |
| typical's and sharp's split (simulator) | day eight's, carried unchanged | typical: at E2 (the strip unlocked) n2's foraging goes to the watch (stakes 50%, watch 50%); typical and sharp: once the ring is closed n2's stakes go to foraging | The pack in round the open side is the moment to weigh the watch (9d, "the hunt's share against stakes"); with the ring closed nothing takes stakes until day eleven, and typical's stakes failed the cap-loss check at 24 h with the lanes still on them (sharp's did on every seed) |
| `l_smoke_1`, `l_smoke_2` | the spec's keys | `l_road_smoke_1`, `l_road_smoke_2` | Day one's text already has `l_smoke_1` |
| the camp's asks (new; `week-two.md`, "The asks") | none | ten offers of no kind: `o_posts` at `palisade` stage 2, `o_margin` with B9, then eight from E2, the first with it and each later one 1.5 h after the last answer (the hidden countdown `ask_wait`: each answer puts in 3, drained 2 an hour) | Typical's V35, V38 and V41-V47 had nothing to decide. The first ask shares E2's moment: at E2 + 5 h it shared a long absence with E2 and SL17's step on whenever seed 2 (three); 1.5 h is under every typical and sharp gap of the chapter, so each return finds one |
| B10's gate | after 210 h, requiring `ring_closed` | `palisade` stage 12 (`t_ring_closed`'s condition), requiring `b10_floor`, a hidden clock's action unlocked at 210 h | Where the last stage lands after 210 h, B10 and the ring's closing are one moment, so B10's absence opens one thing and an ask may share it; sharp's last stage before 210 h still waits on the floor |

## Measured (day nine, seeds 0-2)

B10 in hours from the save's start, with day nine's content, its chore shown at 191 h, the camp's asks and the
simulator's splits and answers above (B9 does not move: typical 199.8, sharp 187.6).

| Route | B10 seed 0 | seed 1 | seed 2 | Band |
|---|---|---|---|---|
| typical | 257.6 | 257.6 | 257.6 | 240-264: inside, 6.4 h under the top |
| sharp | 211.1 | 211.1 | 211.1 | floor 209.2: above (the content's floor, 210 h, does not bind) |
| whenever | 253.8 | 252.9 | 259.7 | not banded |

- **Density (typical, every seed):** every visit has something to spend (2 or more cards) and something to decide.
  Day eight: V31-V33, V35 (`o_posts`), V36 the wind's order card, V37 the pack's split; V34 is a return during a long
  wait and owes only something new. Day nine: V38 (`o_margin`), V39 the gap fire's order card, V40 the watch at E2 and
  `o_rack`, V41-V47 one ask each, V48 the split at the ring's closing. Sharp (information only, seed 0) counts one on
  every visit of day nine.
- **Per absence:** at most two unlocks in every absence of day nine on typical, sharp and whenever, seeds 0-2 (B10
  is one moment with the ring's closing, so an ask can share its absence). Day
  eight's (not held by a test) open three or more in one absence on every route: SL15's and SL16's moments on typical
  and whenever 0 (three), B8's night on sharp and whenever 1 (four, week one's last clock with it), and on whenever 2
  the wind's chore makes a fourth in its 12 h absence over 181-193 h.
- **Cap loss at the chapter's end:** passes on typical and sharp, seeds 0-2, and on whenever 0-2.
- **The 2 AM test (whenever, seed 0, B9's visit to an hour past B10):** passes; the asks are answered at the whenever
  player's own times in both replays.
- **SL17** lands on typical and whenever; sharp reaches B10 before its track count does.

## Applied numbers (day eleven)

What `day_eleven.toml` carries where it differs from `week-two.md`, "Day eleven", and why. Measured with
`python -m tests.weektwo.report typical --eleven` (from `app/`): day nine's plays copied at B10's visit and played on to
B11's.

| Id | Was (target) | Now | Why |
|---|---|---|---|
| the family's arrival | four from the offer: three adults, one the stranger | the offer's four are the three who take lanes and their child (no lane, `t_child_in` at Z1's instant, since each join adds one to the tally); the stranger comes in with B10's moment on his own (`t_stranger`), arrivals 9 after Z1 | `decisions.md`, "Never" (2026-10-30): children live in the town, never workers, a cost or a fight outcome |
| `stranger_clock` | from Z1, 20 h to Z3 | from B10, in twentieths of an hour: Z3 at 400 once Z1 has landed, dusk 12 at 440 after Z3, A31 at 445 with a guard made | Starting at his arrival lands typical's B11 at 279.8 h; Z3 waits on Z1 so the order holds on a route slow to the hut. B10's 210 h floor keeps A31 past B11's sharp floor, so no save-time floor of its own |
| `make_hut` / `n5_build_hut` | 24 stakes, 12 ash, 4 pelt, 12 stones | 16 stakes, 12 stones | Her ground drinks every ash and the flaps' chore every pelt, so the hut waited past Z3 (typical's Z1 at 283 h); at 24 stakes Z1, O-guard and an ask shared one typical absence. At 16 typical's Z1 is B10 + 10 h |
| O-guard | Z1 + 2 h | with Z1 (the hut's condition: one moment) | Z1, O-guard and day nine's last ask in one whenever absence opened three |
| `guard_made` | a feature | a hidden clock's action either arm card's finish unlocks | A31 requires it; as a feature Z2 was an opening, and Z2, SL19 and an ask shared whenever's absences. The guard card itself is shown by the answer |
| `arm_n2` / `arm_n7` | 6 scrap, 4 dry wood | 6 scrap, 1 stake (the shaft) | With three at the watch, whenever's dry wood never held 4 and its spear never started |
| `{lane}_watch` on n5-n7 (new) | none | town cards, 1200 s, 1 dry wood, "Gap +50%" while running; n6 joins on it | n6 on forage lost over half the roots made at the chapter's end (54%), on gather or cut over half the dry wood (70%), on stakes all of it |
| `n6_stakes`'s order card (new) | | at_most 15, release 23, offered with the join | His stakes when the stack is low, never past it; the check refuses a release at or past the cap when offered (24) |
| day eleven's asks (new) | none | `o_door` once day nine's last ask is answered and B10 has landed, then `o_pot`, `o_ditch`, each on day nine's countdown | Typical's first return after B10 (V49) had nothing to decide while the hut waited on stakes |
| typical's split (simulator) | | n2 at stakes 50%, watch 50% from the hut's answer (the hands' build) to Z1, then forage 50%, watch 50% | The hut's stakes: with n2 off stakes since the ring closed, typical's hut waited 9 h on them |
| sharp's split (simulator) | | n2 at stakes from the answer, the watch from Z1 | Sharp's roots lost 51-54% at the chapter's end with n2 foraging whole beside n5 |

## Measured (day eleven, seeds 0-2)

B11 in hours from the save's start (B10 does not move: typical 257.6, sharp 211.1).

| Route | B11 seed 0 | seed 1 | seed 2 | Band |
|---|---|---|---|---|
| typical | 279.8 | 279.8 | 279.8 | 264-288: inside, 8.2 h under the top |
| sharp | 233.4 | 233.4 | 233.4 | floor 229: above |
| whenever | 277.8 | 280.5 | 284.0 | not banded |

- **Density (typical, seed 0):** five visits, V48 to V52; each of V48-V51 has something to spend and something to
  decide (the hut's answer and the split; `o_pot`; Z1's split, `o_ditch`, O-guard and the stakes rule; the posts' rule
  and the vigil queued); V52 is B11's, the edge of written content.
- **Per absence:** at most two unlocks in every absence of day eleven on typical, sharp and whenever, seeds 0-2.
- **Cap loss at the chapter's end:** passes on typical, seeds 0-2. Sharp (0-2) and whenever (1, 2) lose over half the
  stakes made in a 24 h absence: with the posts done nothing in day eleven takes stakes, and day twelve's dig is their
  sink.
- **The 2 AM test (whenever, seed 0, B10's visit to an hour past B11):** passes.
- **Calendar days (typical, seed 0, non-line arrivals):** day 10 one (a level), day 11 seven, day 12 to B11's visit
  (279.8 h) twenty-five, most of them the family's lane cards at Z1.
- **The bloom:** about 556 left at typical's B11 (seed 0); day twelve's picking against `week-two.md`'s "never empty
  by night 14" is day twelve's to weigh.

## Applied numbers (day twelve)

What `day_twelve.toml` carries where it differs from `week-two.md`, "Day twelve", and why. Measured with
`python -m tests.weektwo.report typical --twelve` (from `app/`): day eleven's plays copied at B11's visit and played on to
S4's, the edge of week two's content. Week one's plays now schedule visits to 16 days (`weekone/routes.py`), since
week two's end at 336 h is past the 12 they had.

| Id | Was (target) | Now | Why |
|---|---|---|---|
| `dig_cellar` | 12 stakes a stage | 16 | At 12 the dig took 11.6 h on typical and B12 landed 291.4 h, 3.4 h inside the band's bottom; at 16 it lands 295.6 h. Stakes per stage is the lever named under "The chain that holds each floor". The order card reads 16 |
| the dig's order card | offered with A31's finish | the same, and set in B11's visit by every route that takes rules | The stakes' sink day eleven lacked: with day twelve merged, day eleven's end loses no stakes on any route (sharp and whenever 1-2 lost over half at 24 h before) |
| the cellar's finish | roots, fungus and the larder | roots +50% and the larder +200%; fungus is Camp 15's; every pick (`pick_fungus`, `{lane}_pick`) draws 75% of a bloom | Camp 15 is lifted by the same last stage, so fungus's room lands with B12 once, not twice. The bloom's draw: at B8's 2000 typical's picking (n3's, 12 an hour) runs it dry at 329 h, before A32; drawing less keeps the fungus, and so the stew, it fed (cutting n3's picking share instead to 30% or 25% at B12 kept the bloom but ran the stew from 32 to under 1) |
| B12's floor | 249 h | 250 h (900 000 s), a hidden clock's action | The band's sharp floor is 0.83 × 12.5 days = 249.0 h exactly; a floor on it rounds either side. Sharp lands on it |
| SL20 | `drift_clock` ≥ 96 | B11 + 5 h (`dig_clock` 5), in the bear's season (`drift_clock` 96, a hidden clock's action) | At 96 alone typical met SL20 at 264 h, in day eleven. At B11 + 6 h whenever seed 2 met SL20, B12 and an ask in one absence |
| `e_bear` | at the first hunt's finish | with SL20 (its condition), odds unknown until the first hunt | At the first hunt the page shared B12's absence with an ask on whenever seed 0 (three) |
| `hunt_bear` | 6 catch, 2 pelt, 2 tallow; `hurt` +8 in quarters | 3 catch, 1 pelt, 2 tallow; `hurt` +2 | The drain keeps `hurt` in whole items (D-117's note). The yields are the cap-loss lever: at 6 and 2, typical lost over half of smoked and pelt in 24 h from night 14 |
| `tallow_lamps` | 2 tallow a stage | 2 tallow and 2 stakes a stage, run by its order card (at least 2 tallow) | D-119: a staged hands build from week 2 on is run by one order card |
| SL21 | tallow ≥ 2 | `sign_clock` ≥ 15: a hidden clock SL20 starts | tallow is made only by `hunt_bear`, so the old gate counted one card's taps (`test_no_gate_counts_taps_of_one_card`). At 10 and 12 SL21 met B12 and an ask in one absence on typical (10 on whenever 0 and 1 too); at 15 every route's absences hold. SL21 is seen at V56 on typical (V54 at tallow ≥ 2), V103 on sharp (V102), V50 and V50 on whenever 0 and 2, V45 on whenever 1 (V44) |
| S3 | `r1_clock` ≥ 175 | `drift_clock` ≥ 150 (318 h on every route) | At 175, typical met S3 in SL21's absence with an ask (three), 26 h before the night; whenever's `r1_clock` runs 23 h behind typical's, so no later reading keeps every route before 330 h |
| A32 | `night_14` ≥ 5 | `drift_clock` ≥ 163 (331 h) | A countdown needs a clock already running when S3 shows the card; `night_14` starts at dusk |
| n_day_s1, n_day_s3, n_day_s4 | days notes on S1, S3 and S4 | none: the days page `e_days_6` takes B12 alone | A days note names a spine beat (`tests/opening/test_journal_beats.py`); S1, S3 and S4 are day-list steps. S1's note had also shared B11's next absence with an ask and SL20 on whenever |
| Camp 15 | 2 100 000, not held | held since day nine, lifted by `dig_cellar`'s last stage | Typical's bar waits at the marker from day eleven; lifted, it lands with B12 |
| Camp 16 | smoked 36 → 48 | smoked 45 → 60 | Every route answers `o_rack_high` (smoked +25%) in day nine |
| day twelve's asks (new) | none | nine offers of no kind on day nine's countdown, the first with the dig | Typical's visits after B12 had nothing to decide; the ninth gives the visit before night 14 its decision |
| typical's and sharp's hands (simulator) | `cut_stakes` at 15% (30% sharp) to the end | taken out of the hands' mix at B12 | Nothing after the cellar takes stakes but the lamps' 6 |
| the bear's share (simulator) | | 15% of the hands from SL20, taken out once the sign is spent | A share on a dry card idles (week 3's open question) |

## Measured (day twelve, seeds 0-2)

B12 in hours from the save's start (B11 does not move: typical 279.8, sharp 233.4). Dusk 14 lands at 330.0 h and S4 at
331.0 h on every route measured, A32 queued When ready from S3's visit.

| Route | B12 seed 0 | seed 1 | seed 2 | Band |
|---|---|---|---|---|
| typical | 295.6 | 295.6 | (as 0 and 1) | 288-312: inside, 7.6 h over the bottom |
| sharp | 250.0 | | | floor 249.0: on the content's floor (250 h) |
| whenever | 289.1 | 291.3 | 295.4 | not banded |

- **Hours (typical):** S1 283.1, SL20 285.8, S2 291.2, B12 295.6, SL21 303.6, S3 318.0, A32 and S4 331.0.
- **The bear:** six hunts, two lost, on every route measured; the share leaves the hands' mix once the sign is spent.
- **Density (typical, seed 0):** every visit has something to spend and something to decide; the last is S4's, the edge
  of written content.
- **Per absence:** at most two unlocks in every absence of day twelve on typical, sharp and whenever, seeds 0-2.
- **Cap loss at the chapter's end (night 14):** typical loses over half of smoked's making at 24 h at a full bloom a
  pick (53.4%); with the cellar's finish drawing 75%, 46.5%, and the check passes;
  sharp pelt at 24 h; whenever 1 and 2 smoked at 8 h and 24 h and pelt at 24 h (seed 0 read before the last ask's
  answer changed: smoked at 8 h and 24 h). Below, "Stores without
  a sink at night 14".
- **Day eleven's end, day twelve merged:** stakes pass on every route measured (the dig's order card is set in B11's
  visit). Typical passes; sharp and whenever 1-2 lose over half their roots at 8 h. Measured from day eleven's exit
  save, 8 h away: roots lost 55.9% (sharp), 55.0% and 54.8% (whenever 1, 2), 49.3% (typical), against 41.4%, 40.1%,
  39.3% and 39.3% without day twelve, the making the same. Each dig stage is a tap that holds the hands' mix for its
  2400 s, and `field_track`, roots' sink, is in that mix: sharp's three stages in the 8 h cut it from 192 runs to 144
  (`cook_roots` the same, `smoke_roots` idle either way). At 1200 s a stage the four routes lose 48.7%, 47.6%, 46.8%
  and 44.5% (1800 s leaves sharp and whenever over half), but whenever's B12 then comes about 4 h sooner and lands in
  an absence with SL20 and an ask on seed 0 (three unlocks), and with SL21 and an ask on seed 1. A roots input on the
  dig (2 or 3 a stage) changes nothing measurable, nor does moving part of the cellar's +50% roots cap to stage 1's
  finish (S1; 125%, 135% or 150% there and the rest at the finish: sharp 55.8-55.9%, whenever 0-2 54.7-54.9%): the
  loss is a rate, the paused sink against the making, so a one-time room barely moves it. Accepted as a known miss: the
  check is typical's (49.3%, passes), stages stay 2400 s (week-two.md's 30-40 minutes), and sharp's and whenever's
  roots lose about 55% at 8 h from day eleven's end.
- **The 2 AM test (whenever, seed 0, the visit before B11's to an hour past S4):** passes, the babysitter tapping A32
  the second it is ready (it keeps no queue).
- **Rebased:** typical's day-eleven end, under the rules without day twelve, loads with the dig open and runs a day,
  SL20 landing and the dig waiting for its order card.
- **Calendar days (seed 0, non-line arrivals, whole days after week one's):** typical days 7-13: 23, 14, 7, 1, 7, 32,
  6; sharp: 24, 16, 9, 31, 7, 3, 1; whenever days 7-14: 38, 14, 4, 7, 26, 12, 6, 4. None dead.
- **The bloom (typical, seed 0):** at a full bloom a pick, 607 left at 278 h, 10 at 328 h, dry at about 329 h, before
  A32. With the cellar's finish drawing 75% a pick: 78 left at A32's landing (331 h), 67 at its visit's end, 33 at
  336 h; sharp, its B12 on the floor, 250 at A32. Stew's low after B12 is the same (32).

## Stores without a sink at night 14

Week two leaves these filling past their caps from night 14 (the cap-loss check at day twelve's end, levers applied:
the bear's catch and pelt halved, the cellar's finish drawing 75% of a bloom a pick; measured on sharp and whenever
seeds 0-2; typical passes). B14 opens the next tier's project (`docs/design/week-two-plan.md`, "After week 2"),
and it takes them:

| Store | Fails | Why nothing takes it |
|---|---|---|
| smoked | whenever seed 0 8 h and 24 h, seeds 1-2 24 h. Typical's now holds (46.5% lost at 24 h, 53.4% before the cellar's finish drew less bloom a pick) | the rack keeps smoking the hunts' catch, and the bear's two a hunt end with its sign; the pack, the crows and the wolf hunt take less than it makes |
| pelt | sharp 24 h; whenever seeds 1-2 24 h | `hide_flaps` has four stages, and the wind's chore (three a pegging) stops with the wind at 336 h; the wolf hunt still brings one a hunt |

Stakes have no sink after the cellar but the lamps' six; the routes take the hands off stakes at B12, and no route
fails them at night 14.
