# Week four: landing bands, targets and the arithmetic behind them

Spoilers: under `content/`, never shown to the owner. Ids and numbers only, no lines. The spec is `week-four.md`. Where a
figure is marked measured, it is (method below). Everything else is a target or an estimate, labelled, for the
week-four simulator (`docs/design/week-four-plan.md`, item 7) to replace.

## Measured: where a player stands at 504 h

How: a scratch probe (not in the repo) that loads day eighteen's saved end for a route from an older cache key
(`~/.cache/ashfall/chapter-saves/7c5938a8ac3cab97`, written on 2026-11-23 before #433), replays that route's decisions
under main's rules at `d7e94ba` (`tests.weektwo.rebased.replayed`), plays day nineteen on (`tests.weektwo.routes.play_on`
with day nineteen's chapters), advances to 1 814 400 s with no decisions, and reads every store, cap and skill. That
cache holds typical and whenever only, so **sharp is not measured here**; its rows below are week three's measured beat
times and estimates.

| Store | Typical | Whenever | Cap | Notes |
|---|---|---|---|---|
| smoked | 69.3 | 66.2 | 72 | the table at 4 an hour keeps it near full: the walks' and the boar's supplies come from here |
| stew | 0.2 | 12.5 | 36 | dry on typical: why the walk's supplies are smoked, not stew |
| meals | 140.0 | 138.9 | 8760 | the count week four's arrivals wait on; typical answered O-sun with the light (×1.25) |
| arrivals | 15 | 15 | **20** | B21 needs 25: the turn doubles the cap (D-164) |
| catch | 2.3 | 2.9 | 14 | |
| pelt | 7.9 | 6.9 | 12 | the Clear's covers are gone; the post's door and the book are its sinks |
| stakes | 15.2 | 23.1 | 36 | |
| stones | 18.0 | 17.9 | 18 | at its cap: the post |
| cord | 12.0 | 12.0 | 12 | at its cap: the post |
| clay / scrap | 12 / 12 | 12 / 12 | 12 / 12 | at their caps |
| cleared | 50.9 | 72.0 | 72 | no sink since the road: the post |
| barley | 36.0 | 35.8 | 36 | at its cap; the beds have stopped, so `barley_stew` drains it |
| dry wood | 178.2 | 178.2 | 178 | at its cap |
| roots | 81 | 81 | 81 | at its cap |
| rime | 7.8 | 7.8 | 24 | under the chip's 12; nothing drains it: `thaw` (D-154) |
| grow_left | 2.5 | 2.2 | 168 | the beds paused at times, so a little is left; nothing reads it |
| ash / ashed ground | 0.7 / 8.3 | 0.5 / 9.4 | 24 / 24 | |
| hurt | 3.0 | 0.0 | 3 | typical sits at the hurt cap at the turn |
| camp | 5 099 995 | 5 099 995 | | at Camp 19's held marker (5 100 000) |

| Skill (shown level, prestige phases) | Typical | Whenever |
|---|---|---|
| Scavenging | 16 | 17 |
| Woodcutting | 16 | 19 |
| Foraging | 10 | 9 |
| Cooking | 17 | 18 |
| Arcana | 14 | 15 |
| Melee | 21 | 21 |
| Spellcraft | 8 | 8 |

Lanes joined: n1-n12, n11 left. Fights to 504 h (typical): pack 314 fought, 67 lost; rats 384 / 75; crows 383 / 77.
Typical played 92 visits to 504 h, whenever 78. B17 at 460.2 h on typical in this probe (`b17_clock` 43.8 at 504 h;
week three's readouts: 460.1), so `r2_clock` 48 falls at 508 h.

## Landing bands

D-93 (`pace_scale` 1.0), hours from the save's start. Week four opens on the calendar (the Still's turn at 504 h), and
every sharp floor this week falls before the turn or before the season's clock that holds the beat, so no beat needs a
save-time floor; the clocks are `still_clock` (hours since the turn).

| Beat | Target day | Typical band | Sharp floor (0.83 × (day − 0.5) × 24) | What holds it | Estimate, typical | Estimate, sharp |
|---|---|---|---|---|---|---|
| I1 (clock) | 22 | 504 | 504 | `after_time` | 504 | 504 |
| B18 | 22 | 504-528 | 428.3 | the first walk, ready at 504 h | 505-510 | 505 |
| B19 | 23 | 528-552 | 448.2 | `still_clock` ≥ 30, I4 + 3 h, six walks | 533-540 | 534 |
| B20 ★ | 25 | 576-600 | 488.0 | A39, ready at `still_clock` 72 | 577-590 | 577 |
| B21 | 27 | 624-648 | 527.9 | arrivals 25 (meals), `kept`, 8 h | 626-640 | 650-660 (the cellar's meals: 1.0 an hour) |
| night 28 (dusk) | 28 | 666 | 666 | `after_time` | 666 | 666 |
| the Drift's turn (week five) | 29 | 672 | 672 | | 672 | 672 |
| B22 (week five) | 29 | 672-696 | 567.7 | the post's last stage and the Drift's turn | 675-690 | 672 |

Sharp lands B21 later than typical because it answered O-sun with the cellar, which leaves meals at 1.0 an hour: the
trade O-sun stated. The band is typical's; sharp is held only to its floor, which it clears by more than five days.
Lazy (no chip rule) lands B21 near 665 h, inside its 1.17× band if the table is fed. If sharp lands under a floor, the
floor is wrong, not the play.

## The chain that holds each beat

| Clock or gate | Condition | Sharp | Typical |
|---|---|---|---|
| the walk shown | T13 (`week_three_end`) | 499 | 499 (measured, week three) |
| I1 | `after_time` 1 814 400 s | 504 | 504 |
| B18 | `ashwood_trips` ≥ 1, the walk ready from 504 h | 505 | 505-510 |
| SL29 | `still_clock` ≥ 6 | 510 | 510 |
| I2 | `film` ≥ 12 (1 an hour from 0) | 516 | 516 |
| I3 | `still_clock` ≥ 26, once B18 | 530 | 530 |
| I4 | `ashwood_trips` ≥ 4, once I3 | 530 | 530-532 |
| B19 | `ashwood_trips` ≥ 6, I4 + 3 h, `still_clock` ≥ 30 | 534 | 534-540 |
| SL31 | `sorrel_clock` ≥ 6 | 540 | 540-546 |
| I5, O-fiddle | `meals` ≥ 175, `sorrel_clock` ≥ 4 | 543 (meals at 1.0) | 538-544 |
| I6, the post | `ashwood_trips` ≥ 14, `sorrel_clock` ≥ 12 | 546 | 546-552 |
| SL32 | `still_clock` ≥ 44, once I2 | 548 | 548 |
| O-book | `sorrel_clock` ≥ 24 | 558 | 558-564 |
| I7 | `post` stage 1, once I6 | 547-550 | 548-556 |
| SL33 (night 24) | `still_clock` ≥ 64 | 568 | 568 |
| A39 shown | `still_clock` ≥ 66, once I7 | 570 | 570 |
| A39 → B20 | ready at `still_clock` ≥ 72 (576 h), 3600 s at full hands | 577 | 577-590 |
| I8 | `kept_clock` ≥ 8 | 585 | 585-598 |
| I9, O-walkers | `meals` ≥ 230, `kept` | 595 | 580-598 |
| I10 | `kept_clock` ≥ 30, once I9 | 607 | 607-620 |
| O-widowers | `meals` ≥ 285, `walkers_6h` | 650 | 620-626 |
| B21 | arrivals ≥ 25, `belonging`, `kept`, `bede_wait` ≥ 8 | 658 | 628-634 |
| I11 | `bede_clock` ≥ 4 | 662 | 632-638 |
| I12, A40 shown | `bede_clock` ≥ 20 | 678 → past dusk: see below | 648-654 |
| dusk 28 | `after_time` 2 397 600 s | 666 | 666 |
| A40 → I13 | `still_clock` ≥ 163 (667 h) and I12 | 667 or I12's | 667 |

**Sharp past dusk 28.** On sharp's cellar answer B21 lands about 658 h, so I12 (`bede_clock` 20) falls after 667 h and
A40 waits on it: I13 lands at I12, in the Drift's first hours, as week three's lazy route met T12 and T13 in one night.
That is the accepted cost of a calendar end. If the simulator shows sharp's B21 past 650 h, the lever is the third
group's meals threshold (285), never the clock.

**The levers, in order:** the walk's supplies and makes, and the finds' counts, for B18 and B19 (never the season's
clocks, which are the story's mornings); A39's ready hour is the day, never moved; the meals thresholds and the table's
raise per group for B21; the post's charwood per stage for B22.

## The arithmetic (estimates)

**The walks.** `walk_ashwood` 3600 s on the hands; `{lane}_walk_ashwood` 14 400 s (a hands card's bar is a quarter of
its town copy's). At typical's expected 30% hands share and one lane at 25%: 0.30 + 0.06 = 0.36 walks an hour, about 8.7
a day; 2 smoked each, so 0.72 smoked an hour; 0.72 charwood and 0.36 fungus an hour. Walk 1 lands at 505 h when queued at
T13 (full hands); walks 4 and 6 near 513 and 519 h, so I3's and B19's clocks bind on typical as on sharp; walk 14 near
541 h, so I6 waits on B19's 12 h.

**The chore.** Film 1 an hour from 0 at 504 h, the chip at 12 (516 h). A lane's wash (2400 s) under a rule lands about
40 minutes after the chip shows, so it shows about 1.4 h a day: the table loses about 1.5% of its day's meals. Unruled,
the chip shows from 516 h to 672 h: meals ×0.75 for 156 h, about 49 meals fewer by night 28 on the light's rate.

**The table and the arrivals.** The table costs 4 smoked an hour at 504 h (2, +1 each for the choir and the pair: week
three applied), +1 an hour at each week-four group's join (an `add_bp` 5000 on its cost per join, as week three's): 5 from
the fiddler, 6 from the walkers, 7 from the widowers. Meals 140 at 504 h (measured), 1.25 an hour on the light while fed:
175 near 532 h, 230 near 576 h, 285 near 620 h. On the cellar, 1.0 an hour: 539, 594, 649 h. Arrivals read 25 after the
widowers (15 measured, +1, +2, +4, +3) and B21 lands 8 h after. **The risk** is the table running dry: from the
fiddler's join the table, the walks and (from B20) the boar take 5.7 to 7.9 smoked an hour together. Smoked sits at
69.3 of 72 at 504 h with the table at 4, so the smoke lane makes at least that; the fish (48 catch over the season) and the
boar's won share (about 4.8 catch a hunt) are the week's new meat. The target is a smoked line on typical that falls from
the walkers' join, never before I6, with the boar and the fish beneath it as the answers.

**The post.** 12 stages × 2400 s = 8 h of hands; 120 charwood, 72 cleared, 48 stakes, 36 stones, 24 cord, 3 pelts. At I6
(about 546 h) charwood sits at its cap (24), cleared at 50.9-72, stones and cord at their caps: two stages at once on
charwood alone, and the stages after wait on charwood at about 0.72 an hour, about 14 h a stage: the last near 680 h on
typical (band 672-696). A route that doubles the walk's share finishes near 615 h and waits for the Drift's turn.

**The boar.** `hunt_boar` 7200 s, 2 smoked; won share 6 catch, 1 pelt. The target: one hunt in five lost. At a 20% hands
share, 0.1 hunts an hour, 2.4 a day, about one death every two days; 1.9 catch an hour on the won share. Its supplies
come back in catch: a won hunt pays 6 catch for 2 smoked.

**The fish.** 24 in the pool, 2 catch each: 48 catch. At a 10% hands share, 0.3 an hour: the pool lasts about 80 h; a
lane added, about 40 h.

**Lucy's jobs.** 6 jobs at 10-20 min of hands, about 1.5 h over the week.

**The finite pools against what progress takes** (the owner's direction; issue #438's check reads it the same way):

| Store | Required this week | Its makers | Supply over the week |
|---|---|---|---|
| charwood | 120 (the post) | walks, uncapped | 0.72 an hour × 168 h ≈ 121 at typical's share, any amount at a higher one |
| cleared | 72 (the post) | `shovel_road`, every lane's clearing, uncapped | 50.9 banked, 1 an hour a lane |
| smoked | the walks (14 by I6), A39 (2), the table | the smoke lane on catch (snares, wolf hunt, fish, boar) | uncapped makers; the fish (48 catch) is the only finite part and nothing waits on it |
| pelt | 3 (the post) | wolf hunt, boar hunt | uncapped |
| fish_rising | nothing | the turn | 24, optional |

## Per visit (density)

The same targets as weeks one to three, held on typical from I1's visit to I13's.

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
| Visits, typical | day twenty-two 6-7; day twenty-three 8-9; day twenty-five 7-8; day twenty-seven 6-8 |
| Visits, sharp | about 60 over the week; at least three of every four with a decision |

**The bigger thing in each typical visit** (the design's expectation; the simulator replaces it):

| Visit | Bigger thing | Spend (store near cap) | Decide |
|---|---|---|---|
| 21a (week three's) | the walk shown | | queue it, or set its share |
| 22a | I1, the Still | the walk (smoked) | the walk's share against the town's; Wayfinding |
| 22b | B18, the forest | `barley_stew` (barley at cap) | a lane on the walk |
| 22c | SL29, the fish | `fog_fish` | the fish against the walk |
| 22d | I2, the chip | the wash | write the rule, or wash by hand, or leave it |
| 23a | I3 | the walk | the walks' share against the fish |
| 23b | I4, a Wayfinding find | | the walk against the table's smoked |
| 23c | B19, Sorrel | | their first task |
| 23d | SL31 | | Sorrel's share |
| 23e | I5, O-fiddle | | the answer; their shares |
| 24a | I6, the post | post stages (cleared, stones, cord at cap) | the walk's share (charwood) against the table |
| 24b | O-book | `bind_book` (pelts) | make the book or not now |
| 24c | SL32, a job | `stir_air` | the working against the wash |
| 24d | I7 | a post stage | the post against the walks |
| 24e | SL33 | | queue A39 or not |
| 25a | B20 ★ | | |
| 25b | I8, the boar hunt | `hunt_boar` (smoked) | the boar in the mix or not; a job |
| 25c | the boar's page | a post stage | the boar against the post |
| 25d | I9, O-walkers | | the answer; the group's share |
| 26a | Camp 19 | a post stage | the post against the boar |
| 26b | I10, a job | | the job |
| 26c-26d | the widowers, finds | post stages | the post's split |
| 27a | B21, the bedesman | | N4's first task |
| 27b | I11 | | N4's share |
| 27c | SL36 | a post stage | |
| 27d | I12, A40 shown | | queue A40 |
| 28a-28c | jobs, finds, post stages | post stages | the last stages against the boar |
| 28d | I13 | | (the edge of week four's content: the exception stands) |

## Per absence

At most two moments. Night 21 → 22a: I1 (its pools, the retired rules and the cap, one moment) and B18 when the walk was
queued at T13. 23b → 23c: B19 alone (I4 is the visit before, by B19's own 3 h clock). 23d → 23e: I5 with O-fiddle (one
moment). 23e → 24a: I6 with the post and its order card (one). 25c → 25d: I9 with O-walkers (one). 26b → 27a: the widowers'
mention and B21 (two). The jobs share absences with at most one moment (each shows on the countdown after the last job's
finish). A39 shows with SL33 (one moment: the card is the ask's).

## Cap loss, per chapter end

Target, as weeks one to three: from each chapter's last decision on typical, an 8 h and a 24 h absence lose at most half
of each gathered store's making. A readout since PR 412 (never failed); listed so the levers are known.

| Store | Day twenty-two | Day twenty-three | Day twenty-five | Day twenty-seven |
|---|---|---|---|---|
| charwood | nothing (the post shows at I6): the expected failure | the post (10 a stage, by its order) | the same | the same |
| cleared | nothing until I6 | the post | the same | the same |
| stones, cord | nothing until I6 | the post | the same | the same |
| stakes | as week three's | the post | the same | the same |
| smoked | the table, the walks | the same, more mouths | the same, the boar | the same |
| catch | the smoke lane | the same | the same | the same |
| fungus | `fungus_stew` | the same | the same | the same |
| pelt | nothing until the book | `bind_book`; the post's last stages | the post | the post |
| barley | `barley_stew` | the same | (spent) | |
| ash | her ground | the working pays more | the same | the same |

**Expected verdicts, by arithmetic only:** day twenty-two fails on charwood, cleared, stones and cord (no sink until I6);
the lever is I6's walk count (14), never a new sink. From day twenty-three the post drinks all four. Smoked passes while
the table runs.

## Odds targets (combat)

loss_bp = T / (T + P) (`engine/design/`, "FIGHTS").

| Fight | Prepared | Loss share | Notes |
|---|---|---|---|
| `pack` | the Still's step (+25% at `still_clock` ≥ 40, on top of the Clear's) | about 1 in 3.5 | the greycoats come close in the fog; the step is the threat's, never the defence's |
| `hunt_boar` | the hands, Melee 21 and the spear | about 1 in 5 | a loss is a death: the supplies spent, nothing caught |
| `hunt_boar` | after `r2_clock` ≥ 144 (+25%) | about 1 in 4 | R2's first ramp step |

The preparation check: a route that keeps the watch and the guard through the Still loses measurably fewer pack fights
from the step to night 28 than one that moves the watch to the post.

## The 2 AM test

Level across T13 to night 28: the walk queued from T13 and held in the mix; the post by its order card; the chore by a chip
rule the route writes at the chip's first showing (typical, sharp and whenever; the babysitter the same instant, the
whenever player within one gap, so the comparison is "given the same setup"); the arrivals by the kind's rule; the jobs
answered in the visit they show, one-offs queued When ready; A39 and A40 queued When ready from the visit they show; the
pack, the rats, the crows and the boar as flows; the fish yielding at its end (D-125). The babysitter and the whenever
player end week four with the same stores and tallies, or the report names the visit.

## Placeholders the simulator sets

| Placeholder | Set to |
|---|---|
| the walk's bar, supplies and makes (3600 s, 2 smoked, 2 charwood, 1 fungus) | B18 by 512 h on typical; the walks' smoked visible on the table's line |
| the finds' counts (1, 4, 6, 14) | B19 mid-band; I6 within a day of B19 |
| the meals thresholds (175, 230, 285) | typical lands B21 mid-band with a chip rule |
| the table's raise per group (+1 an hour) | smoked falls on typical from the walkers' join, never before I6 |
| the post's charwood per stage (10), stages (12) | typical's last stage in day 29 |
| `ash_boar` base (14), `hunt_boar` bar (7200 s) | one hunt in five lost; about one death every two days at a 20% share |
| `fish_rising` (24), `fog_fish` makes (2 catch) | the fish lasting into day 25 at a typical share |
| the chip's cost (meals −25%) | unruled, B21 inside the lazy band |
| the Still's step (+25%) | the odds target above |
| Camp 19 at stage 6, Camp 20 at | typical's bar at 20's marker by I12 |
| Lucy's jobs' countdown (day nine's `ask_wait`) | each typical and sharp return with no other decision finds one |
| `bind_book` (2 pelt, 2 cord, 1800 s) | a real cost beside the table's pelts |
