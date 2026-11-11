# Day two: applied numbers and measurements

Spoilers: under `content/`, never shown to the owner. Ids and numbers only, no lines. Measured with the day-two simulator
(`python -m tests.daytwo.report`, from `app/`; its routes are day one's ten, continued past B3) on `day_two.toml` with the
numbers below applied, seed 0, with the simulator as of `e12d73c` (a visit ends once nothing is left to act on and
nothing of the player's lands within the dead gap; the babysitter stays for the whole day). Targets are `day-two.md`'s. The B5/B6, W1 and
lane sections below were measured on the earlier numbers and are unchanged.

## Verdict

Before the numbers, day two played in two visits on every route but the babysitter's, because **every store a build takes
is full when the builds show**: nothing in day two waited on production, and a cost cannot exceed a cap. **Time is the
lever**, so three work times were raised. With them, typical lands B4 11.21 h after B3, inside its 10-30 h band, and
every route but the babysitter's plays in 3-5 visits. Lazy's B4 moved to 76.74 h after B3 (it was 50.28 h) under the new
leave rule.

## Applied numbers

| Id | Was | Now | Why |
|---|---|---|---|
| `build_shelter` work_s | 20 | 1800 | A half-hour build outlasts any visit, so the shelter finishes while the player is away and O-cart greets the next return |
| `build_woodstack` work_s | 20 | 1800 | Same length as the shelter, so the order costs the story the same half hour either way |
| `walk_ridge` work_s | 360 | 7200 | A walk that outlasts a visit makes B4 meet the player on the next return. The hands walk mostly tired, at half: about 3.8 h (13 790 s on typical) |
| `n1_walk_ridge` work_s | 360 | 17 280 | Equal real time (D-87): at the shelter's 1.2, 17 280 / 1.2 = 14 400 s, 4.0 h, as the hands' about 3.8. The nearest length that divides 1.2 x one item (4 320 000 units) exactly and walks whole seconds; 16 560 landed the walk 0.33% short of one, so B4 never fired |
| `t_rack_lean` (new trigger, first Take stock) / `t_rack_lean_off` (`day_four.toml`, B5's warm ground) | none | `smoke_catch`'s make x 6250 bp, undone by x 16 000 bp | The cap-loss measure (`tests/dayone/caploss.py`, exact) reads `smoked` at day two's end losing 66-67% of its making to its cap, 8 h and 24 h: the store sits full from day two on (the route fills it whatever its cap, a raised larder or camp cap only moves the full line), so a tap's 4 lands on a store with room for about a third. The yield, not the cap, is what a full store can absorb: x 0.625 makes a tap 2.5, and the loss 46% (seed 0; the three typical seeds read alike). Lifted at B5 because G2's smoked gate is paced by the rack's full rate (`days-four-to-seven-numbers.md`): leaving the trim in held sharp and evenings off G2 on seeds 0 and 2 |

## Measured (seed 0)

| Route | B3 (h after the end) | B4 (h after B3) | Day-two visits | Camp 7 / 8 (h after B3, as seen) |
|---|---|---|---|---|
| typical | 12.5 | 11.21 (in band) | 4 | 7.4 / 16.6 |
| sharp | 5.7 | 13.74 | 5 | 9.9 / - |
| lazy | 48.5 | 76.74 | 5 | 24.2 / 97.0 |
| by_hand | 16.7 | 16.3 | 4 | 12.4 / 16.6 |
| larder_first (woodstack first) | 12.5 | 11.38 | 4 | 7.4 / 16.6 |
| evenings | 25.4 | 27.81 | 5 | 24.0 / 48.0 |
| lunch | 25.4 | 27.99 | 5 | 24.0 / 48.0 |
| return_22h | 25.5 | 17.21 | 5 | 9.2 / 25.8 |
| babysitter | 3.9 | 7.0 | 1 | - / - |
| whenever (answer order) | 20.5 | 16.03 | 3 | 11.2 / 21.2 |

| Band | Target | Measured |
|---|---|---|
| B4, typical | 10-30 h | 11.21 h: **holds** |
| B4, babysitter | not before ~1.6 h | 7.0 h: **holds** |
| B4, every other route | babysitter's plus 3 of its day-two gaps (`b4_relative`) | holds on every route |
| Visits | four | typical, by_hand, larder_first 4; sharp, lazy, evenings, lunch, return_22h 5; whenever 3; babysitter 1 |
| Per absence | at most two unlocks | V1->V2 still opens **three** on nine routes: `t_dusk_2`, `t_night_2`, `t_morning_3`; whenever's V2->V3 opens four |
| Per visit | day one's bar, with its two exceptions (the visit B4 is seen in; a return during a long wait) | holds on typical, larder_first, evenings, lunch, return_22h, babysitter, whenever. Held: sharp V1 no decision; lazy V1 no decision, V3 0 bigger; by_hand V1 no decision, V4 2 bigger |
| 2 AM | the babysitter no further ahead | level |
| `day_gate_order` (flatcheck) | A18 lands after its gate J4 | holds on every route |

## Open for the lead

Nothing below is a number I decided:
- **V1->V2's third unlock is `t_dusk_2`'s feature** (`dusk_2`, the grade). No number fixes it.
- **Assumptions in `day-two.md` the routes don't bear out:** dry wood's cap at B3 is 18, not 12. Foraging stands at
  3-6 at B3, not 7. Woodcutting stands at 13-19.

## The Camp

The camp-lift fix has merged (`0843306`): Camp 8 is held at 150 000 and either walk (`walk_ridge`, `n1_walk_ridge`)
lifts it. Read from the report: Camp 7 (90 000) is seen at 7.4-24.2 h after B3 on every route but the babysitter's (one
visit, never seen). Camp 8 is seen on eight routes (typical 16.6, by_hand 16.6, larder_first 16.6, whenever 21.2, return_22h 25.8, evenings 48.0,
lunch 48.0, lazy 97.0 h); in the earlier run it coincided with B4 being seen, and I did not recheck that here. Two routes do not see Camp 8: the babysitter (one visit) and **sharp**,
which sees B4 at 13.7 h but Camp 8 never; I have not traced why. I read the coincidence with B4 as the lift working;
I did not trace the mechanism.

## B5 and B6: the day-three placeholders

A20 and A21 have no content, so the simulator projects only the levels. Each level's time is projected from B4 at day
two's average XP rate; on typical the projection matched a played-on run at +10 h and +30 h. A level lands "inside day
three" when it comes after B4 and within 30 h of it.

| Gate | Measured | Verdict |
|---|---|---|
| B5: foraging 10 | Foraging 3–6 at B4 and **no foraging XP in day two on any route**. Her default task keeps roots full, so the player's roots rule never fires | never lands |
| B6: scavenging 20 | Scavenging 11–17 at B4; level 20 projected 131–216 h after B4 | past day three on every route |

Projected levels at B4 / +10 h / +30 h:

| Route | Scavenging | Woodcutting |
|---|---|---|
| typical | 13 / 15 / 16 | 16 / 17 / 18 |
| sharp | 11 / 13 / 15 | 14 / 16 / 17 |
| babysitter | 11 / 13 / 15 | 13 / 15 / 17 |
| lazy | 17 / 17 / 18 | 19 / 20 / 20 |
| others | 14–15 / 15–16 / 16–17 | 16–17 / 17–18 / 18–19 |

Proposed: **B5 on woodcutting 18**, not foraging. Foraging only trains if day three makes the player forage again; if it
does, keep foraging and re-measure. **B6 on scavenging 16.** Both land inside day three on typical. Slower routes reach
them a few hours past +30 h. On lazy both are already met at B4, so the step alone gates there. These are measured on
today's B4 times; the proposal above moves B4 later, which raises the levels at B4 by about one. Re-run once day three
exists, since its content changes the XP rates.

## W1's `week_net_up` (+2), observed

On every route, all of day two's beats (B3, J1–J4, B4) land on day 2–4 of play (lazy is the latest: B4 on day 4). So
all of them sit in W1. B5–B7 aren't simulated and keep their target days 4–6. The net counts: the spine's seven, −1;
day one's H beats, +1; J1–J4, +2. Total +2 on every route, whatever its pace. Timing can't move it; only the beats' turns
can, which is a content decision.

## Her lane

At day one's levels her lane mostly fills stores that are already full. That is why changing her task at B3 gains
nothing (the 2 AM case above). Open 8 asked whether she would be negligible next to a levelled mix; the measured
answer is that she is **redundant while the caps hold**, not slow. Her default foraging also takes the player's own
foraging XP to zero (B5, above).
