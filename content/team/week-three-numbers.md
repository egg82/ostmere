# Week three: landing bands, targets and the arithmetic behind them

Spoilers: under `content/`, never shown to the owner. Ids and numbers only, no lines. The spec is `week-three.md`. Unlike
week two's first pass, the simulator exists: **where a figure is marked measured, it is** (week two's routes played to
S4's visit and advanced to 336 h, seed 0, main at 43f57c55; method below). Everything else is a target or an estimate,
labelled, for the week-three simulator (`docs/design/week-three-plan.md`, item 6) to replace.

## Measured: where a player stands at 336 h

How: `python -m tests.weektwo.report typical sharp whenever --twelve` (from `app/`), and a probe that takes
`tests.weektwo.routes.twelve(route)`'s save at the end of S4's visit, advances it to 1 209 600 s with no decisions, and
reads every store and skill (a scratch probe, not in the repo). Stores in items.

| Store | Typical | Sharp | Notes |
|---|---|---|---|
| smoked | 54.7 | 54.6 | cap 60 (Camp 16, o_rack's answer); near full on both: the table's sink |
| stew | 31.7 | 32.0 | |
| roots | 81.0 | 81.0 | at cap on both |
| pelt | 7.1 | 11.1 | sharp fails the cap-loss check at 24 h from night 14 |
| stakes | 17.3 | 20.2 | cap 36; nothing takes them past the lamps: the hall's input |
| stones | 18.0 | 18.0 | |
| cord | 11.5 | 11.5 | |
| dry wood | 23.2 | 5.0 | |
| damp wood | 12.0 | 12.0 | |
| scrap / clay | 6.0 / 8.0 | 6.0 / 8.0 | |
| bloom | 34.8 | 204.7 | the pool D-125 is first met on: typical's picking spends it a few hours into the Clear, sharp's about a day in |
| fungus | 18.0 | 18.0 | |
| ashed ground | 20.0 | 21.5 | her ground for the beds: six beds take 24 |
| ash | 0 | 0 | |
| roof ash | 16.0 | 16.0 | the chip `ash_laden`'s threshold: why B13 opens `roof_wind` (D-126) |
| wind torn | 2.8 | 6.0 | under its chip's 12; nothing makes it after 336 h |
| tallow | 0.4 | 0.9 | |
| arrivals | 9 | 9 | B16 needs 15 |

| Skill | Typical | Sharp |
|---|---|---|
| Scavenging | 21 | 21 |
| Woodcutting | 21 | 21 |
| Foraging | 12 | 9 |
| Cooking | 7 | 7 |
| Arcana | 10 | 11 |
| Melee | 5 | 5 |

So week two's finds at Scavenging 23, Woodcutting 23, Foraging 13, Cooking 9, Melee 7 and Arcana 11 are still ahead of
typical at the turn and land in week three (they require feature `drift`, which stays unlocked).

**Week two's last chapter (B11 to S4), measured, seed 0:**

| Route | Visits | With nothing to decide | Cap loss at the end | CPU s |
|---|---|---|---|---|
| typical | 10 (V52-V61), gaps cycling 3.2, 4.2, 9.2 h | 1 (V61, S4's: the edge, exempt) | passes | 206 |
| sharp | 36 (V86-V121), gaps 1.7-2.2 h and 8.2 h | 25 (V95-V102, V104-V117, V119-V121) | pelt at 24 h | 110 |
| whenever | 8 (V47-V54), gaps 5.2-11.5 h | 0 | smoked at 8 h and 24 h | 167 |

Fights to S4 (typical): pack 133 fought, 32 lost; rats 203 / 49; crows 202 / 40; the wolf hunt 66 / 10; the bear 6 / 2.
Typical had 61 visits by S4, sharp 121.

## Landing bands

D-93 (`pace_scale` 1.0), hours from the save's start. Week three opens on the calendar (B13 at 336 h), so sharp's lead
from week two is spent on extra visits again, and every play-driven beat but B14 needs a floor. Floors are the band's
sharp floor rounded up to the hour, each a hidden clock's action (week two's `b10_floor` shape).

| Beat | Target day | Typical band | Sharp floor (0.83 × (day − 0.5) × 24) | Content floor | Estimate, typical | Estimate, sharp |
|---|---|---|---|---|---|---|
| B13 (clock) | 15 | 336 | 336 | | 336 | 336 |
| B14 | 16 | 360-384 | 308.8 | none (the hall shows at 331 h) | 366-378 | 350-356 |
| B15 | 18 | 408-432 | 348.6 | 349 h | 414-426 | 349 (the floor likely binds) |
| B16 | 19 | 432-456 | 368.5 | 369 h, on the starer's arrival | 436-446 | 377 (369 + 8) |
| B17 ★ | 20 | 456-480 | 388.4 | 389 h | 460-472 | 389-400 |
| night 21 (dusk) | 21 | 498 | 498 | | 498 | 498 |
| the Still's turn (week four) | 22 | 504 | 504 | | 504 | 504 |

Lazy lands B14 near 395 h, B15 to B17 after 450 h, inside its 1.17× band if the table is fed; T12 and T13 do not wait
on B17's band (T13 waits on T12, which waits on B17: a lazy route past 494 h meets T12 and T13 in one night, the
accepted cost of a calendar end).

## The chain that holds each floor

| Clock or gate | Condition | Starting value | Sharp | Typical |
|---|---|---|---|---|
| the hall shown | S4's visit (`week_two_end`) | | 331 | 331 (measured) |
| B13 | `after_time` 1 209 600 s | 336 h | 336 | 336 |
| SL22 | B13 + 2 h | | 338 | 338 |
| T1 (night 15) | B13 + 10 h | | 346 | 346 |
| T2 (morning 16) | `clear_clock` ≥ 18 | | 354 | 354 |
| T3 | `hall` stage 4 | 4 stages × 16 stakes | 342-345 | 350-358 |
| B14 | `hall` stage 8 | 8 stages | 350-356 | 366-378 |
| T4 | B14 + 4 h | | 354-360 | 370-382 |
| T5 | `clear_clock` ≥ 50 (386 h), once T4 | | 386 | 386 |
| T6 | the covers finished 4 times, once T5 | 12 rime a cover, 1 an hour | 386-392 | 392-398 |
| A35 → B15 | Arcana L (13), T5, save time ≥ 349 h (1 256 400 s) | Arcana 10-11 at 336 | 386 (T5 binds) | 414-426 |
| T7, O-choir | `meals` ≥ 24 and B15 + 2 h | | 388 | 416-428 |
| T8 | the choir joined + 3 h | | 391 | 419-431 |
| T9, O-pair | `meals` ≥ 40 and the choir joined + 6 h | | 394 | 422-434 |
| the starer | `meals` ≥ 56, the pair joined, save time ≥ 369 h | | 394-400 | 428-438 |
| B16 | arrivals 15, `belonging`, `starer_clock` ≥ 8 | 8 h | 402-408 | 436-446 |
| T10 | `cut_road` stage 7 | | 395-405 | 448-458 |
| T11 | `cut_road` stage 8, the pair joined | | 400-410 | 452-462 |
| B17 | `cut_road` stage 10, B16, save time ≥ 389 h (1 400 400 s) | 10 stages × 12 cleared | 410-420 | 460-472 |
| T12 | B17 + 4 h | | 414-424 | 464-476 |
| dusk 21 | save time ≥ 498 h (1 792 800 s) | | 498 | 498 |
| A38 → T13 | `clear_clock` ≥ 163 (499 h) and T12 | | 499 | 499 |

**Note on sharp:** T5's clock (386 h) is later than B15's floor (349 h), so on sharp B15 waits on T5 and lands near
386 h, past its floor and well under typical's band. That is the shape the floors are for. B16 then waits on the
arrivals the table draws, so sharp's T7-B16 run from about 388 to 408 h, and B17 on the road.

**The levers, in order:** the hall's stakes per stage for B14; Arcana L for B15 (never T5's clock, which is the frost
story's); the table's cost and the `meals` thresholds for B16; the road's cleared per stage for B17. If sharp lands
under a floor, the floor is wrong, not the play: raise its hours. Never lengthen a hands bar to move a band.

## The arithmetic (estimates)

**The hall:** 8 stages × 2400 s = 5.3 h of hands; 112 stakes, 24 stones, 16 cord, 8 beams, 4 pelts. Stakes at 17.3 at
336 h (measured) and about 3 an hour from two lanes on their week-two stakes rules (1200 s, "under 15, until 23"),
which typical keeps after B12: 95 more stakes in about 32 h, so the last stage near 368-378 h. Sharp, both lanes whole
and the hands on `cut_stakes` (600 s, about 1.5× with Woodcutting 21): about 8 an hour, the last stage near 350 h.
Beams: 8 from `pull_beams` (1200 s each, Scavenging) is 2.7 h of hands, the second-largest hands cost of the chapter;
the stages that take them are 5-8, so the beams can trail the stakes.

**The beds:** six stages of `n3_sow` (1800 s, 4 ashed ground each): 3 h of her lane and 24 ground (20 at 336 h,
measured; the sixth bed waits on her card or the working's ash). Each bed 0.5 ripe an hour, so six make 3 an hour, 2.25
frosted. Reaped (3 ripe → 2 barley) and stewed (4 barley → 4 stew): about 2 stew an hour at six beds, from about 350 h
to 504 h, roughly 250 stew over the Clear against the town's 1 an hour a person. Ripe caps at 18 (six hours' growth):
the cap-loss check's store for the beds.

**The frost:** rime 1 an hour; the chip at 12; a cover takes 12 rime and 2 pelt, so two covers a day, 4 pelts a day
with the order on. Over the Clear (168 h) about 28 pelts if covers alone answer it; from B15 the working takes some of
that for no pelts and 2 ash a time. The wolf hunt brought about 0.33 pelts an hour in week two (66 hunts to S4 on
typical, 1 pelt a hunt), about 8 a day: the covers, the hall's 4, T6's 4 and SL28's 2 take about 60% of a day's making,
so the cap-loss target is reachable without a further sink.

**The table:** 2 smoked an hour from B14, 3 from the choir's join, 4 from the pair's. Smoked at 54.7 of 60 at 336 h
(measured) and making faster than the week-two sinks took (it failed cap loss on whenever). The target is a falling
smoked line on typical from the choir's join, never before B14 + 12 h, so B14's moment shows the table's line before it
shows red; the deer (4 catch a won hunt, about 8 a day if the hands give it a share) and the wolf hunt's share are what
put it back. `meals` 1 an hour while fed: 24 from B14 is a day of meals, 40 and 56 are the next arrivals.

**The road:** 10 stages × 2400 s = 6.7 h of hands; 120 cleared, 60 stones, 40 stakes, 4 beams. Cleared at 1 an hour per
lane at 1800 s: typical's split puts half of one lane on clearing from SL24 (about 380 h) and the choir's "to the road"
answer or the cutter from about 425 h, so 0.5 an hour to 425 h (about 22) and 3 an hour after (the rest in about 33 h):
the last stage near 460-470 h. Stones are the binding input on a route that built the hall hearth (8) and sank its
stones into the asks' "stones now" answers.

**Lucy's jobs:** 8 jobs at 5-30 min of hands, about 2.2 h over the week: the yes is never a large cost.

## Per visit (density)

The same targets as weeks one and two, held on typical from B13's visit to T13's.

| Check | Target |
|---|---|
| New things per visit | mean ≥ 6 over each chapter's visits; none under 3 |
| Bigger things | ≥ 1 per visit |
| First new thing | within 60 s of opening |
| Something to spend | ≥ 1 per return: an affordable card taking a store at ≥ 80% of its cap |
| Something to decide | ≥ 1 per visit from content (an answer, a choice of two, a share or rule change that moves which of two goals lands first); queuing a build's stage never counts |
| Idle | no stretch over 90 s inside the activity window |
| Runs | no run of one card over 3 |
| Effort between bigger things | at most 10 |
| Visits, typical | day fifteen 6-7; day sixteen 8-10; day eighteen 5-6; day nineteen 4-5, then 6-7 to night 21 |
| Visits, sharp | about 60 over the week; at least three of every four with a decision (week two's day twelve: 11 of 36) |

**The bigger thing in each typical visit** (the design's expectation; the simulator replaces it):

| Visit | Bigger thing | Spend (store near cap) | Decide |
|---|---|---|---|
| S4's | the hall shown | a hall stage (stakes), `pull_beams` | the town's split: stakes, beams, the watch |
| 15a | B13, the beds | a hall stage; `fungus_stew` on the last fungus | her share to sowing (SL22); beams in the hands' mix |
| 15b | T1, the chip | `cover_beds` | the covers' order card on her or the hands |
| 15c | T2, the deer | `hunt_deer` (smoked) | hunt or not; the deer's share against beams |
| 15d | SL23, `o_door_ice` | a hall stage | beams against stakes; the ask |
| 15e | T3, `o_sun_rack` | a hall stage | stakes against stones for the roof stages |
| 15f | B14, the table, Camp 17 | barley stew | O-road; the table against the hunts |
| 16a | T4 | `n3_sow` again (ashed ground) | her lane: sowing, reaping, covers |
| 16b | SL24, the road | a road stage once cleared reaches 12 | lanes on clearing against stakes and reaping |
| 16c | SL25, a job | `hall_hearth` (stones) | the hearth against the road's stones |
| 16d | T5, a job | the stew pot | the job |
| 16e | a road stage, a job | a road stage | the deer's share against the road |
| 16f | T6 | the covers again (pelts) | covers by hand, by rule, or let it frost |
| 16g | SL26, a job | | his share |
| 16h | the greycoat page, finds | | the watch against clearing |
| 16i | B15, Spellcraft | `warm_beds` | the working's rule against the covers' |
| 18a | SL27 | `warm_beds` | the working against the covers |
| 18b | T7, O-choir | | the answer; their shares |
| 18c | T8 | barley stew; `hunt_deer` | the hunts against the road |
| 18d | T9, O-pair | a road stage | the answer; the road's split |
| 18e | the starer, a job | | the job |
| 18f | B16 | | (the snares: nothing to spend on them) a job |
| 19a | T10 | a road stage | stages against reaping |
| 19b | T11 | a road stage | stones: road against hearth |
| 19c | SL28, Camp 18's marker | `road_cloths` (pelts) | her share |
| 19d | B17, the map, Camp 18 | | the lanes re-tuned without him |
| 20a | T12, a job | barley stew | the job |
| 20b-20d | jobs, finds, the beds' last reaping | the beds' ripe | Spellcraft 4 against the beds' sixth |
| 21a | T13 | | (the edge of week three's content: the exception stands) |

## Per absence

At most two unlocks. Night 14 → 15a: B13 (its cards and the rules' removal, one moment) and SL22. 15a → 15b: T1 and
the chip (one moment with the covers' order card: the chip is T1's frost). 18a → 18b: T7 with O-choir (one moment).
18c → 18d: T9 with O-pair. 18e → 18f: B16 alone (the starer's arrival is the visit before). 19c → 19d: B17 (the leave,
`r2_open` and the map, one moment). The jobs share absences with at most one unlock (each shows on the countdown after
the last job's finish).

## Cap loss, per chapter end

Target, as weeks one and two: from each chapter's last decision on typical, an 8 h and a 24 h absence lose at most half
of each gathered store's making. What drinks each store, by chapter:

| Store | Day fifteen | Day sixteen | Day eighteen | Day nineteen |
|---|---|---|---|---|
| stakes | the hall (16 a stage, run by its order) | the road (4 a stage) | the same | the same |
| stones | the hall | the road; `hall_hearth` | the road | the road |
| pelt | the hall's doors; covers | covers; T6's strip | covers | covers; `road_cloths` |
| smoked | the hunts' takes | the table | the table, raised | the table |
| ripe | reaping (hands, lanes) | the same | the same, more hands | the same |
| barley | `barley_stew` | the same | the same | the same |
| cleared | | the road (12 a stage, run by its order) | the same | the same |
| ash | her ground | her ground; the working pays more | the same | the same |
| beams | the hall | the road's stage 6 | | |
| roots | eleven mouths; the rats | the same | fourteen mouths | the same |

**Expected verdicts, by arithmetic only:** stakes pass while the hall and the road run; ripe is the beds' risk at 24 h
(18 cap, 3 an hour) unless a lane's reap rule covers it: the reap order card ("over 12 ripe, {lane} reaps, until 3")
offered with the beds is the lever. Smoked passes once the table runs. Pelt passes with the covers on. Fungus and the
bloom are spent early (D-125), not a cap-loss case.

## Odds targets (combat)

loss_bp = T / (T + P) (engine `DESIGN.txt`, "FIGHTS").

| Fight | Prepared | P : T | Loss share | Notes |
|---|---|---|---|---|
| `pack` | week two's end: the ring, the watch, the guard, the gap fire, the posts, the lamps | 41 : 10 | about 1 in 5 | measured shape: 32 of 133 lost to S4 on typical (24%) |
| `pack` | the Clear's step (+25% at `clear_clock` ≥ 40) | 41 : 12.5 | about 1 in 4 | the greycoats join; the step is the threat's, never the defence's |
| `hunt_deer` | spear, Melee 5 | 20 : 10 | about 1 in 3 | a loss takes the smoked the hunt carried and nothing else |

The preparation check (combat-plan item 9): a route that keeps the guard and the watch through the Clear loses
measurably fewer pack fights from the step to night 21 than one that moves the watch to clearing the road. That trade is
day sixteen's and nineteen's decision, so the check doubles as a density check.

## The 2 AM test

Level across S4's visit to night 21: the hall and the road by their order cards; the beds by her lane's sowing order
and the reap order cards; the covers by the chip's order card; the arrivals by the kind's rule; the jobs answered in
the visit they show (a babysitter answers the instant they show; the whenever player within one gap; the one-off queued
When ready); the field stone and night 21's step as glowing taps queued When ready from the visit before where
queueable (A35 is a first-of-its-kind step, shown and tapped in the same visit on every route: the simulator reports
its lag); the pack, the rats, the crows and the deer as flows; spent pools yielding (D-125). The babysitter and the
whenever player end week three with the same stores and tallies, or the report names the visit.

## Placeholders the simulator sets

| Placeholder | Set to |
|---|---|
| the hall's stakes per stage (16, 12) | typical lands B14 mid-band |
| Arcana L for A35 (13) | typical lands B15 mid-band |
| the table's cost (2 smoked an hour, +1 a group) | smoked falls on typical from the choir's join, never before B14 + 12 h |
| `meals` thresholds (24, 40, 56) | typical lands B16 mid-band; the lazy route inside its band |
| the road's cleared per stage (12) | typical lands B17 mid-band |
| the floors (349, 369, 389 h) | the sharp floors; raise if sharp lands under |
| `beds`' rate (0.5 ripe an hour a bed), `ripe`'s cap (18) | ripe's cap-loss verdict at each chapter's end |
| the cover's pelts (2), T6's strip (4) | pelt's cap-loss verdict at day fifteen's and day sixteen's ends |
| bases: `ash_deer` 10; the Clear's step on `wolf_pack` (+25%) | the odds targets above |
| Camp 17-19 at | typical's bar waiting at 17's marker by T3, 18's by T10 |
| `hall_hearth`, `road_cloths` bars | a stage per typical visit at most |
| the jobs' countdown (day nine's `ask_wait`, 3 an answer, 2 an hour) | each typical and sharp return with no other decision finds one |

## Applied and measured

Each chapter's applied numbers and its measured bands, density, absences, cap loss, 2 AM test and calendar days, in
week two's shape.

**Day fifteen (`day_fifteen.toml`, in IN_WRITING), applied:**

- The hall takes the same at every stage (a card's inputs are per stage): 16 stakes, 3 stones, 2 cord, 1 beam and half
  a pelt, so 128 stakes, 24 stones, 16 cord, 8 beams, 4 pelts; its order card at stakes 16. The beams are taken from the
  first stage, so `pull_beams` goes into the hands' mix at S4's visit. Rest +10% at T3 (a trigger), +20% finished.
- The beds: 0.5 ripe an hour, each bed sown +100% (an entry per stage, item 9), so one bed grows 1 an hour and six 3.5;
  the chip takes a quarter. The reap order card is offered on her lane only (`n3_reap`); the other lanes' reap cards are
  shares.
- The rime starts at 2 with B13, so it reaches the chip's 12 at B13 + 10 h: T1, the chip and its cures are one moment.
- The table (2 smoked an hour), `meals` and `aim_table` open with B14, as "The table" says ("Opened by B14"), so smoked
  has its sink from the chapter's end; the table's raise per arrival group, O-road and what `meals` draws stay day
  sixteen's and later.
- `o_door_ice`'s second answer gives 6 dry wood (the door burned, a hide hung), not a pelt. Neither ask is in day
  twelve's chain or fills `ask_wait`: `o_sun_rack` shows with B13 (the sun), `o_door_ice` at `clear_clock` 18 (the
  morning after night 15), not on hall stages that only spaced them apart.
- B14's feature carries the edge's end card (`dayend15_*`); once the chapter ships, week two's (`dayend14`) drops its
  still-being-written line.
- Foraging's find is at 14: 15 pays a find already. The other four are as "Levels and finds".

**Measured** on a scratch route (a scratch script, not the simulator: week two's routes from S4's
visit with day fifteen's order cards set once offered, beams at a 15% hands share, 30% on sharp, the deer at 10%, barley
stew as a trip, both asks answered with the first answer), seed 0:

| Route | B13 | T1 | T3 | T2 | B14 | Absences over two | Cap loss at B14's visit |
|---|---|---|---|---|---|---|---|
| typical | 336 | 346 | 350.8 | 354 | 372.1 (band 360-384) | none | smoked 8 h and 24 h; roots 8 h |
| sharp | 336 | 346 | 348.3 | 354 | 369.6 (floor 308.8) | none | smoked 8 h and 24 h |
| whenever | 336 | 346 | 356.0 | 354 | 377.3 | two, each with a day-twelve ask (`o_crows`, `o_sag`) as the third | smoked; roots |

The hall's fourth stage lands before the deer's clock on typical and sharp, so `beats.yaml` authors T3 before T2 (D-139
accepts 15d, T2's visit, as near_untouched). Smoked's sink is the table (day sixteen); its lever comes there.
