# Days four to seven: landing bands, targets and the arithmetic behind them

Spoilers: under `content/`, never shown to the owner. Ids and numbers only, no lines. The spec is `days-four-to-seven.md`.
**Nothing here is measured.** No simulator runs past B4 yet (day three's routes are `docs/design/day-three-plan.md`,
item 6), so every figure below is a target or an estimate built on `day-three-numbers.md`'s targets, and the
simulator replaces each one (`docs/design/days-four-to-seven-plan.md`, item 1). Where an estimate rests on another
estimate, it says so.

## Landing bands

From `day-three-numbers.md` (D-93; `pace_scale` 1.0), hours from the save's start:

| Beat | Target day | Typical band | Sharp floor | Estimate, typical | Estimate, sharp |
|---|---|---|---|---|---|
| B5 | 4 | 72-96 | 70 | 84 (day three's middle) | 70-72 |
| B6 | 5 | 96-120 | 90 | 101-110 | 90-91 |
| B7 | 6 | 120-144 | 110 | 122-131 | 110-112 |
| B8 (clock) | 8 | season's turn at 168 | the same | 168 | 168 |

Week 1's end (G2, night 7) is not a spine beat and is not banded; its dusk is held to the calendar (below).

## The chain that holds each floor

Day three's floor is four hearth courses on a cure lane. Days four and five use a day length with a floor in save
time instead (`after_time`, which the loader already reads), so a sharp setup lands earlier only by what its play
gates move (B6's Scavenging level, B7's arrivals), never by watching:

| Clock | Gate | Starting value | Sharp | Typical |
|---|---|---|---|---|
| morning 5 | A20 + 1 h (as day three's mornings) | | 71-73 | 85 |
| dusk 5 (`t_dusk_5`) | morning 5 + L5 **and** save time ≥ 90 h | L5 = 16 h | 90 (the floor binds) | 101 |
| B6 | A21 tapped in night 5 + Scavenging N | | 90-91 | 101-110 (visit gap) |
| morning 6 | A21 + 1 h | | 91-92 | 102-111 |
| dusk 6 (`t_dusk_6`) | morning 6 + L6 **and** save time ≥ 110 h | L6 = 16 h | 110 (the floor binds) | 118-127 |
| B7 | A29 tapped in night 6 + arrivals 3 + B6 | | 110-112 | 122-131 |
| morning 7 | A27 + 1 h | | 111-113 | 123-132 |
| dusk 7 (`t_dusk_7`) | save time ≥ 162 h **and** morning 7 + 6 h; past 165 h, morning 7 alone | | 162 | 162 |

**The levers:** L5 and L6, then the floors. Typical lands mid-band if B5 lands at 84; if the day-three simulator puts
typical's B5 at 90 or later, lower L5 (a late B5 pushes B6 past 120 at L5 = 16 plus a 9 h gap). If sharp lands under
a floor, the floor is wrong, not the play: raise the floor's hours. Never lengthen a hands bar to move a band (the mix
stops). The arrivals step for B7 (O-pair at morning 6, then 21 600 s) is about 6-14 h after morning 6,
inside L6, so it rarely binds.

**B6's Scavenging level** (placeholder 20): the held track trains Scavenging all week. Day three expects 15-17 at B5;
20 by about 100 h needs roughly three levels in 16 h, plausible only with the track held at a high share. Set it to
what typical reaches about twelve hours after B5.

## Per visit (density), every chapter

The same targets as day three (`day-three-numbers.md`, "Targets: per visit"), held on typical from the visit B5 is seen
in to the visit G2 is seen in. Day two's typical measured a mean of 8 new things a visit; day three targets a mean of
at least 6.

| Check | Target |
|---|---|
| New things per visit | mean ≥ 6 over each chapter's visits; none under 3 |
| Bigger things | ≥ 1 per visit (a chapter beat, a side beat, an arrival, a new system or card kind) |
| First new thing | within 60 s of opening |
| Something to spend | ≥ 1 per return: a card the player can afford whose takes include a store at ≥ 80% of its cap |
| Something to decide | ≥ 1 per visit: an answer, a choice of two builds, or a mix or queue change that moves which of two goals lands first |
| Idle | no stretch over 90 s inside the activity window |
| Runs | no run of one card over 3 |
| Effort between bigger things | at most 10 |
| Visits, typical | day four 4-5; day five 4-6; day six 5-7 (to night 7) |
| Visits, sharp | day six 7-9 (its day is about 50 h) |

**The bigger thing in each typical visit** (the design's expectation; the simulator's report replaces it):

| Visit | Bigger thing | Spend (store near cap) | Decide |
|---|---|---|---|
| W1 | L1, the woodshed | woodshed stage (damp wood, stones) | roof or woodshed first; the track's hold against the woodshed |
| W2 | L2, SL8 | woodshed stage | his share at the watch against wood |
| W3 | L3, Camp 11 | woodshed stage 3 | the hold against the stone-less rack under fog |
| W4 | SL7, B6 | the bigger dry wood line's re-tune | A21 (the step), the rack against the fire's draw |
| X1 | Arcana, `hand_on_stone` | `hand_on_stone` on full damp wood | the stone card's share against the track's |
| X2 | M2, SL9 | `hand_on_stone`, any day-four stage left | the rack against the stone |
| X3 | O-pair | the second bay (damp wood, stones) | the answer; the bay against the hearth stones |
| X4 | M1, SL10, SL11 | `hearth_stones` (stones, clay) | four shares to split; her bed against roots; Lucy off the watch |
| X5 | B7 | (the presence step) | A29 |
| Y1 | combat | `make_spear` (scrap from the track's finds only: 6 by day three's end, the rest from these chapters' finds) | spear first or a bare hunt |
| Y2 | SL12, the pests' first counts | the hunt in the mix (smoked) | the hunt's share against the stone and the track |
| Y3 | G1, `pelt_bedding` | bedding stage (pelts, damp wood) | bedding or a pelt held |
| Y4 | SL13 | bedding stage | `o_pelt` |
| Y5 | SL14 | the rack re-hang (catch from the hunt) | the hunt's share against the rack's |
| Y6 | G2, Camp 12 | | (the edge of week 1's content: the exception stands) |

Sharp's extra day-six visits get their bigger thing from Melee 3's find, Arcana 5 and 6, Scavenging 21 and Camp 12's
marker; if the simulator finds a sharp visit with none, add a find at the level it reaches there, never a wait.

## Per absence

At most two unlocks. Night 4 → W1: morning 5 with L1 (one moment) and the woodshed riding it. Night 5 → X2: morning 6
and M2 (two hours apart). Night 6 → Y2: morning 7, and SL12 if the spear was paid in Y1. A return that reveals O-pair
and M1 together (the whenever player, answer order set) counts two.

## Cap loss, per chapter end

Target, as day three: from each chapter's last decision on typical, an 8 h and a 24 h absence lose at most half of
each gathered store's making (banked-time plan item 2). What drinks each overflowing store, by chapter:

| Store | Day four | Day five | Day six |
|---|---|---|---|
| damp wood (about 2 200/h made) | the track (180/h at 50%); woodshed stages | `hand_on_stone`, 18 per 20 s for 1 dry wood, held, so it drinks only what passes the hold; the second bay | the same; `pelt_bedding` |
| stones (about 400/h) | the track (90/h at 50%); woodshed stages | `n3_dig_bed`, `hearth_stones`, the second bay | the same |
| roots (about 800/h) | the track (90/h at 50%); stew | the same; four mouths (`n2_eating`, and the pair's eating at the same rate each) | `rats` (2 per lost fight), `poultice` |
| dry wood (the rack's making, plus the stone's) | fire, the watch fires | the stone adds 2 per 20 s; `hearth_stones` none | `make_spear`; the watch fires |
| smoked | (day three's) | | `hunt_wolf` (1 per hunt), `crows`; the strip empties it at B7 |
| catch | | | the hunt makes 3 per won fight; `smoke_catch` takes it |

**Expected verdicts, by arithmetic only:** damp wood passes from day five on if the stone card runs at 50% or more
(540 + 180 against about 2 200, with the gatherers' making falling as the shares rise; day three's argument). Stones
and roots are likely to fail on the 24 h absence, as day three's are likely to; day three's numbers file names the
lever (shorten the track's bar) and the same lever serves here. Dry wood is new risk: the stone turns damp overflow into
dry wood, so dry wood may now cap. The fix order is in `days-four-to-seven.md`, Open 3 (raise the stone's input
before adding a sink).

**Measured (typical, seed 0):** the track's bar was already at its floor, so its takes follow the camp's making instead:
its roots take doubles at B6 (the stone takes the damp wood hold and the track's moves to stones) and rises half again at
M1 (a third forager), `t_track_roots` and `t_track_roots_2`. The stone runs 18 damp wood to 1 dry wood. Roots then lose
15-27% and dry wood under a third at each chapter's end; pelt needs a cap of 12 after the bedding.

The four new mouths draw stew and roots (each townsperson eats as `n2_eating`: stew −1 and roots −1 an hour). Food
drives growth, not survival: if stew empties, the eating pauses, no chip shows, nothing compounds.

## Odds targets (combat, from `days-four-to-seven.md`, "B7")

loss_bp = T / (T + P) (engine `DESIGN.txt`, "FIGHTS"):

| Fight | Prepared | P : T | Loss share | Expected losses in 24 h at the starting rates |
|---|---|---|---|---|
| `hunt_wolf` | no spear | 8 : 4 | 1 in 3 | at 50% share, 1.5 hunts an hour: 12 lost, a hurt every 2 h |
| `hunt_wolf` | spear | 20 : 4 | 1 in 6 | 6 lost, a hurt every 4 h |
| `rats` | no floor | 4 : 4 | 1 in 2 | 12 lost, 24 roots |
| `rats` | floor | 16 : 4 | 1 in 5 | about 5 lost, 10 roots |
| `crows` | no roof / roof | as `rats` | | 12 / about 5 smoked |

**Why the hunt's bar is long (1200 s).** At a gathering card's bar (under a minute) a hunt in the mix loses several
fights an hour, `hurt` sits at its cap and the chip never clears, which makes the chip noise. The target: in the mix at
a typical share, a hurt every one to two game hours unprepared and every three to five with the spear, against `heal`'s
one per four hours, so the chip comes and goes and the poultice has a reason. Tune by the bar (900-1800 s, the trip's
register) and `heal`'s rate, never by the odds formula. The hunt's makes (3 catch, 1 pelt a won hunt) are then sized
so the rack re-hangs to 18 smoked by about 30 h after B7 on typical (G2's gate): at 1.5 hunts an hour and five in six
won, about 90 catch a day before `smoke_catch`'s rate binds, so the rate that binds is the rack's, as it should be. The day-two trim of that rate (`t_rack_lean`) ends at B5 (`t_rack_lean_off`), so the rack binds at its full rate here.

The preparation check (combat-plan item 9): a route that pays the spear loses measurably fewer hunts over day six
than one that never does; the two cures likewise against the pests.

## The 2 AM test

Level across day four to night 7: the woodshed, the bays, `hearth_stones` and `pelt_bedding` queued When ready; the
stone card and the track held; O-pair and `o_pelt` answered by order; the hunt in the mix; `poultice` by a rule on
`hurt`. The fights are flows (invariant 81), so the babysitter and the whenever player end week 1 with the same stores
and tallies.

## Placeholders the simulator sets

| Placeholder | Set to |
|---|---|
| L5, L6 | so typical lands B6 and B7 mid-band (start at 16 h each) |
| the save-time floors (90 h, 110 h, 162 h) | the first two at the sharp floors; the third so night 7 falls before 168 h on every route |
| B6's Scavenging level | what typical reaches about 12 h after B5 |
| Arcana's XP per `hand_on_stone` | so typical reaches Arcana 4 by about M1 and 6-9 by night 7 |
| `hunt_wolf` bar, makes; `heal` rate | the hurt and re-hang targets above |
| sides' and threats' bases | the odds targets above |
| Camp 11, 12 at | typical reaching 11 in day four and 12's marker in day six |
| `pelt_bedding` and `hearth_stones` bars | a stage per typical visit at most |
