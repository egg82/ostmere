# Day three: landing bands, targets and the arithmetic behind them

Spoilers: under `content/`, never shown to the owner. Ids and numbers only, no lines. The spec is `day-three.md`. Measured
with a scratch probe outside the repo on day two's routes at `de9af51`,
seed 0. Everything under "Targets" is a target for the day-three simulator (`docs/design/day-three-plan.md`, item 6) to
hold or to set; nothing there is measured yet.

## Measured: where the routes stand at B4

Hours from the save's start:

| Route | B3 | B4 | Last day-two decision |
|---|---|---|---|
| sharp | 5.8 | 19.7 | 21.3 |
| typical | 12.6 | 24.0 | 29.2 |
| evenings (the simulator's) | 25.5 | 53.5 | 73.5 |
| lazy | 48.7 | 125.4 | 145.6 |

The owner's own save reached B4 at about 30-38 h (1.25-1.6 real days), between typical and the simulator's evenings route.

At B4 on every route: damp wood cap 18, stones 18, roots 36, dry wood 36, smoked 18, catch 9-14; every gathered
store full. The hands and her lane make about 2 200 damp wood, 800 roots and 400 stones an hour between them
(`banked-time-open.md`'s 24 h figures; this probe's per-hour column is on another unit and agrees in ratio). Levels at
B4: Scavenging 13-19, Woodcutting 16-21, Foraging 4-6 (no XP in day two: Lucy forages), Cooking 2-4.

## The pace scale and the bands

`pace_scale` is one number in `beats.yaml` (1.0; D-93). For a spine beat from B5 on with target day d:

- **typical** lands in [(d − 1) × S, d × S] days from the save's start;
- **sharp** lands no sooner than 0.83 × (d − 0.5) × S days. The floor is taken on the day's middle, because 0.83 × the
  day's end would sit above typical's own lower edge.
- **lazy** is reported, not banded: it reaches B4 at 125 h, past B7's band, and day one and day two are not retuned.

| Beat | Target day | Typical band (h from start) | Sharp floor (h) | Typical span after B4 (h, from 24.0) |
|---|---|---|---|---|
| B4 | 3 | not banded (shipped; typical measures 24.0) | not banded | - |
| B5 | 4 | 72-96 | 70 | 48-72 |
| B6 | 5 | 96-120 | 90 | 72-96 |
| B7 | 6 | 120-144 | 110 | 96-120 |

The same formula serves every later beat, so a change of scale is one edit.

## Targets: day three's chain (typical, h after B4)

| Moment | Target | What sets it |
|---|---|---|
| A22, K1, K2 | 0-0.2 | A22 glows with B4; the track's first run |
| K3, morning 4 | 0.35, 1.25 after A22 | the clock |
| SL1 | morning 4 | the clock |
| SL2 (larder floor done) | 2-12 | three stages of 2400 s, queued |
| K4 (`track_end`) | 14-24 | its Scavenging level (16): the level typical reaches here |
| first stew, O-stay (with it) | 12-30 | the hearth's first course (clay from K2 and `dig_clay`) |
| K5 (the bay done) | 24-40 | the answer, then 21 600 s on either lane |
| SL6 (third course laid) | 34-50 | courses and cures |
| night 4, A20, B5 | 48-72 | the fourth course cured, + 0.25 h, then A20 at the next visit |

## Sizing the chain for the sharp floor

Sharp reaches B4 4.3 h before typical, so the floor (70 h) asks sharp for at least 50 h after B4, and the difference
between the routes is mostly visit gaps. So the chain is work the player queues, never a wait on presence alone:

- four courses × (1800 s laid + `cure_hearth` 30 000 s) ≈ 43.7 h, the cures on their own lane while the
  hands work;
- the bay (21 600 s) runs beside a cure, so it adds nothing on a route that answers O-stay promptly;
- presence steps that wait for a visit: A22, O-stay's answer, each course's lay (unless queued with When ready), A20.

Sharp: 19.7 + about 46.5 + a few short gaps ≈ 68-72 h, at the floor. Typical: 24.0 + 46.5 + visit gaps (about 10-20 h
over nine visits) ≈ 80-90 h, inside 72-96. **The lever is `cure_hearth`'s bar:** raise it if sharp lands under 70,
lower it if typical lands past 96. Never lengthen a hands bar to move the band: that stops the mix.

## Sizing the track

A trip held against a store draws it at up to share × a × 3600 / w an hour (`banked-time-open.md`). With
`field_track` at w = 120 s and a = 12 damp wood, 6 stones, 6 roots, at a 50% share it draws 180 damp wood, 90 stones
and 90 roots an hour. Against the hands' making of about 2 200 / 400 / 800 an hour that absorbs about a tenth of damp
wood and a quarter of stones. Two things close the gap, and the check (banked-time plan item 2) decides between them:

1. A held trip's share comes out of the gatherers' shares, so the making falls as the share rises; the 50% target is on
   what is made, so a route that holds the track at a high share makes less to lose.
2. If that is not enough at day three's end, **shorten the bar** (60 s doubles the draw) before adding a sink. A bar
   under 30 s reads as a gathering card, not a trip: past that, raise a and the stores' caps together.

The comforts add a fixed sink of their stages: about 54 stones and 18 damp wood (larder floor), 36 damp wood and 12 dry
wood (rack roof), 24 clay, 48 stones, 8 dry wood (hearth), 24 stones and 12 dry wood (watch fire), 12 damp wood and 12
stones (bay), 36 damp wood and 18 stones (day two's raised bed). Small against an hour's making; their job is the
decision and the spend on return, not the cap-loss figure.

## Sinks after measuring

The decisions are `day-three.md`, "Sinks after measuring". Measured with `python -m tests.daythree.report` (from
`app/`) on typical and sharp, seed 0, before and after.

**What made the stores overflow** (typical, at day three's end, items an hour): the hands' woodcutting 1 250 damp wood
and scavenging 310 stones at the route's sixth shares each, Lucy's foraging 860 roots, and from K5 his cutting 1 800
damp wood. The old track at its half share drew 360 / 180 / 180. A gatherer's share made about ten times the damp wood
the same share of track drew, so no bar inside the floor could close it, and stones bound the draw before damp wood
did.

**The sizing rule now:** a run's takes follow the ratio of what the camp makes into the three stores, and share ×
a × 3600 / w at the route's share is at least half of each store's making, with no take above what its maker refills
(a take past it pauses the trip dry and drains the store the stew needs). At w = 30 s and a half share: 60 runs an
hour, 1 080 damp wood (of 1 250, or 1 250 + his share), 240 stones (of 310), 840 roots (of 860 before K5, 1 580 after).

| Number | Was | Now |
|---|---|---|
| `field_track` bar | 60 s | 30 s (the floor) |
| `field_track` takes | 12 damp wood, 6 stones, 6 roots | 18 damp wood, 4 stones, 14 roots |
| `field_track` makes | 1 scrap a run | nothing (scrap from finds) |
| scrap line shows | A22 | K4 |
| K4's n₂ | 270 runs | 540 runs |
| his share at the join | `n2_cut` | `n2_forage` |
| `n2_eating` | stew 1, roots 1 an hour | stew 1, smoked 1, roots 1 an hour |
| `cure_hearth` bar | 30 000 s | 37 500 s |
| `clay_hearth` inputs | token last | token first (same takes) |
| new | | `wood_stack`, `pot_shelf` (3 stages each; `day-three.md`) |

| Measured (seed 0) | Before | After |
|---|---|---|
| typical, share lost away 8 h / 24 h | damp wood 88/88%, roots 71/73%, scrap 100/100%, stones 43/44% | damp wood 13/13%, roots 47/47%, stones 23/26%, smoked 0/50% (scrap is no longer made by a card) |
| typical, visits with nothing to decide | V10, V14, V15 | none but B5's own (the edge visit) |
| typical B5 (days from start; band 3-4) | 3.47 | 3.60 |
| sharp B5 (floor 2.905) | inside (cure 30 000 s, with the course stall) | 3.08 (without the stall it fell to 2.67 at 30 000 s) |
| typical, h after B4: O-stay, K5, K4, SL2, SL6 | about 29, 38, 22, 26, 42 (by the visit each was seen in) | 12.6, 17.6, 20.9, 39.1, 33.4 |

Thin margins, each a number to watch when later content lands: roots at 47% (his foraging, past K5) and smoked at
50% over 24 h (his eating pauses when the stew runs out, about half a day in). K5 now lands before its 24-40 h target
on typical: O-stay comes with the first stews, at the first return after the hearth's first course.

## Gates on shipping

Day three's move into CHAPTERS put it under the opening's gates (`decisions.md`, "No gate counts taps"; "A card that
shows every need met does the thing"), and the engine's `ready_at` became the latest unmet need's (invariant 31). The
changes: K4 is `track_end` at Scavenging 16 (was run 540); O-stay comes with the first stew (was stew 6); night 4 reads
`cure_hearth`'s count, capped at 4 (was the `cure_done` store); morning 4 opens the watch fire (was shown at A22 behind
a flag); the buckle moves to Scavenging 17; `pot_shelf` opens at the third course (was the fourth; now the second, below); `rack_roof` takes 6 dry
wood a stage (was 12: the dry wood rule lays only to 6); the bay takes 12 damp wood (was 18: a hold may keep damp wood
at no more than its own cap, 12). Measured with `python -m tests.daythree.report`,
seed 0, on the corrected engine:

| Measured | Before (cure 37 500 s) | After (cure 30 000 s) |
|---|---|---|
| typical B5 (days; band 3-4) | 4.29 | 3.98 |
| sharp B5 (floor 2.905) | 3.47 | 3.24 |
| typical, visits with nothing to decide | V8, V13 (V20 is B5's edge) | V8 |
| typical, h after B4: K4, O-stay, K5, B5 | 15.2, 38.5, 43.6, 79.0 | 22.5, 62.4, 67.4, 71.6 |

On the corrected simulator (clock schedules visit at every listed hour; the player taps a ready step before queueing,
the hearth's next course first among comforts), with the dry wood and bay takes above. The second column set adds
three changes. A hearth course takes 2 dry wood (was 6): the dry wood rule keeps the store between 2 and 6, and
`ready_at` does not count the rule's refills, so a larger take showed no ready time while the store fell. On evenings, the
third course waited a whole night for a visit. `pot_shelf` opens at the hearth's second course and `wood_stack` at the
larder's second stage (both were the third), so typical's queue is empty at B5 and the hands are back on the track, the
roots sink. Also, `t_bay_begun` logs a line when the hands start the bay, the something new that a return during that
long wait owes.

| Measured | typical | sharp | evenings | typical | sharp | evenings |
|---|---|---|---|---|---|---|
| | before | | | after | | |
| B5 (days; band 3-4, sharp floor 2.905) | 3.60 | 3.08 | 3.96 | 3.47 | 3.08 | 3.48 |
| O-stay, h after B4 (target 12-30) | 26.0 | 15.4 | 16.9 | 26.0 | 15.4 | 16.9 |
| SL5, h after B4 | 24.3 | 42.8 | 40.2 | 24.4 | 45.0 | 34.4 |
| visits with nothing to decide | V11 (the bay on the hands across a 3.2 h return) | not checked | not measured | none (V11 and V13 are long-wait returns, each with a line) | not checked | not measured |
| cap loss away 8 h | roots 48%, stones 26% | not checked | not checked | roots 47% | not checked | not checked |

The cure bar is no longer the lever it was: on the corrected engine, before the step and O-stay changes, 30 000 s put
typical later than 37 500 s did (4.67 against 4.29), because B5 moves with which visit finds A20 ready and the hands
free. O-stay on typical now lands late (target
12-30 h): the first stew waits for free hands at a visit, as stew 6 did.

## Targets: per visit (density)

Held on the typical route by the day-three simulator, as day one and day two are, from the visit B4 is seen in to the
visit B5 is seen in. Day two's typical route measured 10, 12, 6 and 4 new things over its four visits (mean 8), with a
bigger thing in each. Day three must match that rate per visit, not per day ("The opening is the bar"):

| Check | Target |
|---|---|
| New things per visit | mean ≥ 6 over day three's visits; none under 3 |
| Bigger things | ≥ 1 per visit (a chapter beat, a side beat, an arrival, a new system or card kind) |
| First new thing | within 60 s of opening |
| **Something to spend** | ≥ 1 per return: a card the player can afford whose takes include a store at ≥ 80% of its cap |
| **Something to decide** | ≥ 1 per visit: an answer, a choice of two builds, or a mix or queue change that moves which of two goals lands first |
| Idle | no stretch over 90 s inside the activity window |
| Runs | no run of one card over 3 |
| Effort between bigger things | at most 10 |
| Visits | 8-10 on typical between B4 and B5 |

The two exceptions stand (`decisions.md`, "Tuned means checked"): the visit at the edge of written content, and a return
during a long wait the player chose. A hearth cure is not one: it is work the chain needs, so the visit still owes
something to spend and decide.

## Targets: per absence and per week

- **Per absence:** at most two unlocks. Day three adds no dusk feature, so V1→V2 brings night 3 and morning 4 (SL1 rides
  morning 4's outcome).
- **Per week:** week 1 counts spine, chapter and side beats together. Later weeks' shape: 4-5 spine beats and 4-6 side
  beats, so events per week roughly double the spine's. The simulator reports each kind per week; the flat check reads
  only the spine and the chapters.

## Targets: cap loss and the 2 AM test

- **Cap loss** (banked-time plan item 2): from day three's last decision, an 8 h and a 24 h absence on typical lose at
  most half of each gathered store's making. Day two's held entry stays until day two's own sink is measured.
- **2 AM:** level with the track held and the comforts and courses queued across the babysitter's and the whenever
  player's visits. Every sink is in view unready before it can be afforded (`day-three.md`, "Away from the screen").

## Day two's sink

`raised_bed` must not move day two's landing: B4's band on every route within 0.5 h of the measured table above, and
day two's per-visit and per-absence verdicts unchanged. Report cap loss over day two as played before and after.

## Placeholders the simulator sets

| Placeholder | Set to |
|---|---|
| K4's Scavenging level | the level typical reaches 14-24 h after B4 (16); never inside V1 on sharp |
| n₃ (the B5-B6 chapter's L2) | the run count typical reaches 24-30 h after B4 |
| B5's Foraging level | the level typical reaches by the fourth course's cure (expected 6-9) |
| B6's Scavenging level | the level typical reaches about 12 h after B5 (day-two numbers proposed 16) |
| `cure_hearth` bar | as "Sizing the chain" |
| O-stay | the first stew, unless it shows inside V1 on sharp |
