# Week five: landing bands, targets and the arithmetic behind them

Spoilers: under `content/`, never shown to the owner. Ids and numbers only, no lines. The spec is `week-five.md`. A
figure marked **measured** is; everything else is a target or an estimate, labelled, for the week-five simulator
(`docs/design/week-five-plan.md`, item 9) to replace.

## What is measured, and what is not

**Measured, from the readouts committed on main at `db115109`** (`app/tests/readouts/`, played by CI on day twenty-five's
chapters; week four's last chapter is not shipped, so nothing past B21 is played):

| Beat | Typical (day, hours) | Sharp | Whenever | Band (typical) |
|---|---|---|---|---|
| B18 | 21.13 (507.1 h) | 21.07 (505.7) | 21.13 (507.1) | 504-528 |
| B19 | 22.25 (534.0 h) | 22.25 (534.0) | 22.25 (534.0) | 528-552 |
| B20 | 24.08 (577.9 h) | 24.14 (579.4) | 24.20 (580.8) | 576-600 |
| B21 | 26.45 (634.8 h) | 27.66 (663.8) | 25.96 (623.0) | 624-648 |

(`weektwo-pacing-<route>.txt`; "day" there is hours ÷ 24, so day 26.45 is story day 27.)

Day twenty-five's chapter on typical (`weektwo-twentyfive.txt`): 12 visits; **decide 0 on 7 of the 12**; per absence,
2-8 h returns decided twice in 8, 8 h+ returns five times in 4. Cap loss at the chapter's end, away 8 h: charwood 19%,
dry wood 15%, roots 98%, stakes 100%, stones 71%, windbreak and wraps 100%; away 24 h: charwood 73%. The week-four
absences from B20 to B21 bring at most two moments each (the same file). Typical's chapter twenty-two to twenty-five
visits brought 96 new things over days 22-26 (`weektwo-pacing-typical.txt`).

**Measured in week four at 504 h** (`week-four-numbers.md`, an older cache and code): smoked 69.3 of 72, meals 140.0,
arrivals 15, stones 18 of 18, cord 12 of 12, Arcana 14, Melee 21, Spellcraft 8; Arcana stood at 10-11 at 336 h and
reached 13 at 427 h (`week-three-numbers.md`).

**Not measured: everything at 672 h.** A probe was tried: load a day-twenty-three end saved by CI and play day
twenty-five's chapter on under main's rules, then read every store and level at 666 h and 672 h. Every saved end
available was written under content that has since changed (a card it held was removed), and replaying its decisions
under main's rules refused a mix naming that card, so no figure came out. The rows below marked estimate are
arithmetic from the measured rates above; the plan's simulator item stores night 28's ends and measures them first.

## Landing bands

D-93 (`pace_scale` 1.0), hours from the save's start. Week five opens on the calendar (the Drift's turn at 672 h). Sharp
floors are 0.83 × (day − 0.5) × 24; only B25's falls after the turn.

| Beat | Target day | Typical band | Sharp floor | What holds it | Estimate, typical | Estimate, sharp |
|---|---|---|---|---|---|---|
| Y1 (clock) | 29 | 672 | 672 | `after_time` 2 419 200 s | 672 | 672 |
| B22 | 29 | 672-696 | 567.7 | A41 ready at `drift_clock` 516 (684 h), the post's twelfth stage | 686-705 | 685 |
| B23 | 31 | 720-744 | 607.6 | A42 ready at `drift_clock` 552 (720 h), 3 hair, Arcana L1 | 721-735 | 721 |
| B24 ★ | 33 | 768-792 | 647.4 | P5's eighth stage, then A43 | 775-795 | 760-775 |
| B25 | 35 | 816-840 | 687.2 | A44 at `ward_clock` 36, `drift_clock` 520, Wayfinding L2 | 812-832 | 797-812 |
| dusk 35 | 35 | 834 | 834 | `after_time` 3 002 400 s | 834 | 834 |
| the Clear's turn (week six) | 36 | 840 | 840 | | 840 | 840 |

B22's risk is the post: typical's last stage is estimated 680-700 h (week four's estimate was 672-696, and day
twenty-five's readout shows the post's door, at stage 6, landing about 622 h), so B22 can land past 696 on typical.
The lever is week four's (the post's charwood per stage), never A41's morning. Sharp reaches B25 before typical's band
because B24's build is faster there; its floor (687 h) binds no route, and a sharp B25 early in day 34 is not a
defect.

## The chain that holds each beat

| Clock or gate | Condition | Sharp | Typical |
|---|---|---|---|
| Y1 | `after_time` 2 419 200 s | 672 | 672 |
| SL37 | `drift_clock` ≥ 508 | 676 | 676 |
| the roofs' chip | roof ash ≥ 16 (2 an hour from about 0 at the turn) | 680 | 680 |
| Y2 | `drift_clock` ≥ 510, `post_door` done | 678 | 678 |
| Y3, O-first-run | `drift_clock` ≥ 516, Y2; the offer also the post's twelfth stage | 684 | 684 (the offer 684-700) |
| A41 → B22 | ready at `drift_clock` ≥ 516, 3600 s at full hands; or "Someone else" + 2 h | 685 | 686-705 |
| the track's chip | road ash ≥ 12 (1 an hour from B22) | 697 | 698-717 |
| SL38 | the tracker's card's first finish | 690 | 692-710 |
| Y4 | `line_lost` ≥ 1 (the shuffle bag's first loss) | 692-700 | 692-712 |
| Y5 | `line_clock` ≥ 14 | 699 | 700-719 |
| SL39 | `line_clock` ≥ 18 | 703 | 704-723 |
| Y6 (night 30) | `drift_clock` ≥ 540, B22 | 708 | 708 |
| Y7 | hair ≥ 3, Y6 (one comb at 900 s) | 709 | 709-714 |
| A42 → B23 | ready at `drift_clock` ≥ 552, 600 s | 721 | 721-735 |
| Y8 | `call_clock` ≥ 6 | 727 | 727-741 |
| Y9, P5 shown | `hill_trips` ≥ 2, B23 | 722 | 725-740 |
| O-burners | `meals` ≥ 380, `call_clock` ≥ 12 | 733 (meals at 1.0: 744) | 733-747 |
| SL40 | `call_clock` ≥ 14 | 735 | 735-749 |
| Y10 | P5 stage 3 | 740 | 745-760 |
| SL41 | `drift_clock` ≥ 590 | 758 | 758 |
| Y11 | the latch's fourth stage, Y8 | 740-760 | 745-770 |
| Camp 20 | P5 stage 4 | 745 | 750-765 |
| A43 → B24 | P5 stage 8, 600 s | 760-775 | 775-795 |
| Y12 | `ward_clock` ≥ 6 | 766-781 | 781-801 |
| Y13, A44 shown | `ward_clock` ≥ 20 | 780-795 | 795-815 |
| A44 → B25 | `ward_clock` ≥ 36, `drift_clock` ≥ 520, Wayfinding L2, 60 s | 797-812 | 812-832 |
| Y14 | `mark_clock` ≥ 6 (B25 + 6 h) | 803-818 | 818-838 |
| dusk 35, Y15 | `after_time` 3 002 400 s, Y14 | 834 | 834 (Y14 past it: Y15 at Y14) |

**The levers, in order:** the post's twelfth stage is week four's; A41's and A42's ready hours are mornings and never move;
the hair is one comb; P5's post stores per stage, then charwood per stage, for B24; `ward_clock`'s 36 for B25 (a day and a
half is a story fact: the tracker's try, a night, the next day); Wayfinding L2 set to what typical reaches by 810 h.

## The arithmetic (estimates)

**The line.** `run_cart` 2400 s on the hands, `{lane}_run_cart` 9600 s, 4 smoked → 4 post stores. At a typical 15% hands
share and one lane at 25%: 0.15 × 1.5 + 0.25 × 0.375 = 0.32 carts an hour, 1.3 post stores in and 1.3 smoked out an hour.
Drawn: the upkeep line 1 an hour (making 1 charwood), the hill's walks (0.13 an hour, 2 each: 0.26), P5 (16 over about
50 h: 0.32), the line's raids (0.5 fights an hour; held at about 1 in 5 lost, 2 each: 0.2; unheld about 1 in 2: 0.5).
Draws total 1.8 an hour against 1.3 in at that share: the post's store binds, the upkeep line pauses first (it pauses
dry; the walks and P5 queue their stages), and the cart's share is the week's real dial. The target is a post-stores
line on typical that never sits at its cap and never sits empty for more than an hour.

**The table.** Smoked costs 7 an hour at the turn (week four's estimate: 4 at 504 h, +1 for each of three groups), +1 from
the burners, and the line's 1.3: 9.3 an hour from day 31 against the smoke lane, the boar and the bear. Smoked sat at
69.3 of 72 at 504 h with the table at 4 (measured), so the smoke lane makes at least 4 an hour at that share; week five
asks for more. **The risk** is the table running dry, which pauses eating and slows arrivals, never more (`decisions.md`,
"Food drives growth, not survival"). The target: a smoked line on typical that falls from B22 and recovers when the
route moves a lane to the smoke lane or the boar, so the line against the table is a choice a player sees.

**The chores.** Roof ash 2 an hour from the turn, the chip at 16: 8 h, then two cures a day under a rule (as week two).
Road ash 1 an hour from B22, the chip at 12: one cure a day under a rule. Unruled, the track's chip shows from about 12 h
after B22 to the turn: every cart a third slower, about 0.4 fewer post stores an hour at typical's share, so P5 about a day
later and B24 near the band's top; never stopped.

**Hair.** `comb_pelts` 900 s, 1 pelt → 3 hair. A42 takes 3; `ward_gate` 1 a run (1200 s): at a 10% share, 0.3 runs an hour,
0.3 hair, so a pelt every 10 h. Pelt stood at 7.9 of 12 at 504 h (measured); the wolf and boar hunts make it.

**The hill and P5.** `walk_hill` 7200 s, 2 post stores, 2 stones, `hill_trips` +1; the twin 28 800 s. At 20% hands and one
lane at 25%: 0.1 + 0.031 = 0.13 walks an hour. Two walks by about 15 h after B22, so Y9 waits on B23 (725-740 h). P5's
stages: 6 charwood (the upkeep line's 1 an hour and the Ashwood walks' 0.72: about 1.7 an hour), 4 stones (the hill's
0.26 an hour, everyday cards, and stones banked at their cap, 18), 2 cord, 2 post stores. Shown about 730 h; stone and
post stores bind; the eighth stage about 780 h on typical (band 768-792).

**The arrivals.** Meals 140 at 504 h (measured), 1.25 an hour on typical's light while fed (week four's rate), less while
`ashed` showed: 380 near 700-715 h, so O-burners waits on `call_clock` 12 (733-747 h). On sharp's cellar (1.0 an hour), 380
near 744 h. Arrivals read 28 after the burners (26 after B21 on week four's design).

**Arcana L1 and Wayfinding L2.** Arcana 10 at 336 h, 13 at 427 h, 14 at 504 h (measured): about 77 h a level and growing,
so 15 near 590-620 h on typical: L1 = 15 binds nothing on any route that kept Arcana in a mix, and shows as a row on A42 on
one that didn't. Wayfinding opened at 504 h at 360 XP an hour on the walks; week four expected level 8 by night 28. Level
12 by about 810 h is a guess: the simulator sets L2 to the level typical holds at 800 h.

**The finite pools against what progress takes** (the owner's direction; issue #438's check reads it the same way):

| Store | Required this week | Its makers | Supply over the week |
|---|---|---|---|
| post stores | 16 (P5), 4 (the two walks Y9 waits on) | the carts, uncapped, from smoked | 1.3 an hour at typical's share, any amount at a higher one |
| smoked | A41 (6), the carts, the table | the smoke lane on catch (snares, hunts), uncapped | as week four, plus the boar |
| charwood | 48 (P5) | the Ashwood walks, the upkeep line, uncapped | about 1.7 an hour |
| stones | 32 (P5) | the hill's walks, everyday cards, uncapped | banked 18; about 0.5 an hour |
| hair | 3 (A42) | `comb_pelts` from pelt (hunts, uncapped) | one comb |
| `moths_up`, `bloom`, `bear_sign` | nothing | the turn, Y5 | optional |

## Per visit (density)

The same targets as weeks one to four, held on typical from Y1's visit to Y15's.

| Check | Target |
|---|---|
| New things per visit | mean ≥ 6 over each chapter's visits; none under 3 |
| Bigger things | ≥ 1 per visit |
| First new thing | within 60 s of opening |
| Something to spend | ≥ 1 per return: an affordable card taking a store at ≥ 80% of its cap |
| Something to decide | ≥ 1 per visit from content (an answer, a choice of two, a share or rule change that moves which of two goals lands first); queuing a build's stage never counts. Day twenty-five measured 5 of 12; week five's target is every visit, which is why the line, the latch, the hill and the hair are each a share against something else |
| Idle | no stretch over 90 s inside the activity window |
| Runs | no run of one card over 3 |
| Effort between bigger things | at most 10 |
| Visits, typical | day twenty-nine 5-6; day thirty 5-6; day thirty-one 8-9; day thirty-three 6-7 |
| Visits, sharp | about 60 over the week; at least three of every four with a decision |

**The bigger thing in each typical visit, and its decision** (the design's expectation; the simulator replaces it):

| Visit | Bigger thing | Spend (store near cap) | Decide |
|---|---|---|---|
| 29a | Y1, the Drift | the post's last stages | the bloom against the post; the bear or not |
| 29b | the roofs' chip, SL37 | `clear_roofs` | write the rule, or climb by hand, or leave it |
| 29c | Y2 | a post stage | who walks the Ashwood (the cast reads it at B22) |
| 29d | Y3, O-first-run | | I'll take it, or someone else |
| 29e | B22, the tracker | `run_cart` (smoked) | the cart's share against the table's |
| 30a | Y4, the line's page | | the tracker on the line or on their old work |
| 30b | Y5, moths | `net_moths` | dust on the line against the carts' time |
| 30c | Y6, the combing | `comb_pelts` (pelt) | the hair against the book's pelts and the hides |
| 30d | Y7, A42 shown | | queue A42 |
| 31a | B23, the ward | `ward_gate` | the ward against the watch's share |
| 31b | Y8, the latch | the latch's stages (stakes at cap) | the latch against P5's coming stones |
| 31c | Y9, P5 | the hill's walks (post stores) | the walks against the carts |
| 31d | O-burners, SL40 | | the answer; their shares |
| 32a | Y10 | a P5 stage | P5 against the latch |
| 32b | SL41, a job | `hunt_bear` (bear sign) | the bear against P5 |
| 32c | Y11 | a P5 stage | the line's tracker back to stakes, or not |
| 32d-32e | Camp 20, finds | P5 stages | the post's store split |
| 33a | B24 ★ | | |
| 33b | Y12 | the hill's walks | Wayfinding against the line |
| 34a | Y13, A44 shown | | queue A44; the walks' share for its row |
| 34b-34c | jobs, finds | | the last job; the boar against the line |
| 35a | B25 | | |
| 35b | Y14 | | (the line's share for week six) |
| 35c | Y15 | | (the edge of week five's content: the exception stands) |

## Per absence

At most two moments. Night 28 → 29a: Y1 (its refills and the drain, one moment). 29a → 29b: SL37 and the roofs' chip
(two). 29c → 29d: Y3 with O-first-run (one). 29d → 29e: B22 (A41's finish) with the tracker (one). 30b → 30c: Y6 and SL39
(two). 30d → 31a: B23. 31c → 31d: O-burners and SL40 (two). Every other absence brings one. The jobs share absences
with at most one moment (each shows on the countdown after the last answer).

## Cap loss, per chapter end

Target, as weeks one to four: from each chapter's last decision on typical, an 8 h and a 24 h absence lose at most half of
each gathered store's making. A readout, never failed.

| Store | Day twenty-nine | Day thirty | Day thirty-one | Day thirty-three |
|---|---|---|---|---|
| charwood | the post's last stage | the upkeep line adds to it: P5 not yet shown (the expected failure) | P5 | P5 done: the expected failure at the week's edge |
| stakes | the post | the same | the latch | (the latch done: the expected failure) |
| stones | the post | the hill adds to it | P5 | the expected failure at the edge |
| post stores | | the walks, the upkeep line | P5, the walks | the walks, the upkeep line |
| smoked | the table, A41 | the carts | the same, the burners | the same |
| hair | | `ward_gate` | the same | the same |
| roots | (98% at day twenty-five's end, measured: no sink this week) | | | |

**Expected verdicts, by arithmetic only:** day thirty fails on charwood (the upkeep line's making has no taker until P5
shows at Y9); the lever is Y9's two walks, never a new sink. Day thirty-three fails on charwood, stakes and stones at the
week's edge, as every week's last chapter has.

## Odds targets (combat)

loss_bp = T / (T + P) (`engine/design/`, "FIGHTS").

| Fight | Prepared | Loss share | Notes |
|---|---|---|---|
| `raid_line` | none on the line | about 1 in 2 | the expected cost of not deciding |
| `raid_line` | the tracker's card at a typical share | about 1 in 5 | |
| `raid_line` | the tracker and `dust_line` | about 1 in 8 | |
| `raid_line` | after `r2_clock` ≥ 312 (+25%) | each about a fifth worse | R2's mourner step |
| `raid_hall` | the watch only | about 1 in 3 | the watch holds the gap, not the latch: only the latch moves this |
| `raid_hall` | the iron latch (`latch` +200%) | about 1 in 10 | |
| `pack` | with `ward_gate` running at a 10% share | measurably fewer losses than the watch alone | the preparation check |

The preparation check: a route that keeps the tracker on the line loses measurably fewer post stores from B22 to night
35 than one that leaves the line unheld; a route with the ward loses fewer pack fights than one without.

## The 2 AM test

Level across night 28 to night 35: the chips by rules the route writes at each chip's first showing (typical, sharp and
whenever; the babysitter the same instant); the cart and the hill's walks held in the mix; the latch and P5 by their order
cards; O-burners by the kind's rule; O-first-run, the jobs and the asks answered in the visit they show, one-offs queued
When ready; A41 to A44 queued When ready from the visit they show; the raids, the pack and the bear as flows; the moths
yielding at their end (D-125). The babysitter and the whenever player end week five with the same stores and tallies, or
the report names the visit.

## Placeholders the simulator sets

| Placeholder | Set to |
|---|---|
| the cart (2400 s, 4 → 4), the upkeep line (1 an hour) | post stores bind P5 on typical, never empty more than an hour |
| `mourner` base (10), the raids' rates (0.5, 0.25) | the odds targets above |
| the latch (4 stages: 3 scrap, 4 stakes, 1 cord) | done by 770 h on typical; stakes leave their cap |
| `walk_hill` (7200 s, 2 post stores, 2 stones), Y9's count (2) | Y9 within 12 h of B23 |
| P5 (8 × 6 charwood, 4 stones, 2 cord, 2 post stores) | typical's eighth stage in day 33 |
| Arcana L1 (15), Wayfinding L2 (12) | the level typical holds just before each beat's morning |
| O-burners' meals (380) | they come in day 31-32 |
| `ward_gate` (1200 s, 1 hair, gap +50%) | a route with the ward loses measurably fewer pack fights |
| the chips' costs (rest −15% as shipped; carts −33%) | unruled, B24 inside its band's top |
| Camp 20 at P5 stage 4, Camp 21 at 7 200 000 | typical's bar at 21's marker at the edge |
| Lucy's jobs' countdown (`ask_wait`) | each typical and sharp return with no other decision finds one |

## Verified

- **The flat check over the designed order.** A scratch copy of `content/beats.yaml` with week four's day-twenty-seven
  list as `week-four.md` designs it, this week's five lists as `week-five.md` designs them, the four spine entries'
  gates and `pays` as designed, and SL36 to SL41, run through `content/team/flatcheck.py`: this week raises only the
  expected flags D-219 names (near_untouched on 29a, 30a, 30b, 31b and 32c; th-town's open end moving to O-burners).
  The run also flags week four's I12 (three down from I10) because the designed day-twenty-seven list ties I11 and I12
  with B21 on day 27; that list is the chapter writer's, and the flag goes away once B21 is ordered first.
- Nothing is played through week five: the bands are targets for the simulator to measure.
