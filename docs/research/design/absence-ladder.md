# Absence ladder

Proposal 8 of `design-101.md` §3, measured. No change to the game. Beats by id only.

## Method

`python -m tests.dayone.report --absence` (`app/tests/dayone/absence.py`). The human-paced player plays day one on the
real engine; at the exit of each of its four visits the player is gone for 1 h, 8 h, 24 h, 3 days and 7 days and the
engine runs on with the mix as left. Each return is counted from served data: the unlock set, chips, skill levels
and the lines the step emitted, before and after. Lines are placed as the page places them (`awaylines.ts`, ported as `absence.place`): a chip's line never plays on
the band (an on-line, and a chip's last off-line while it is not shown, go to the Log; its other off-lines go nowhere),
and a repeat task's line goes to the Log. The port and the page are held to one table of cases
(`app/client/fixtures/arrival_cases.json`), run by `client/test/arrivalcases.test.ts` and `test_dayone_absence.py`,
along with the queue's schedule. No chip line landed in any of these windows, so the placement did not change a count.
The reveal time is
`ArrivalQueue.start`'s schedule without reduced motion; the pace, the cap and the reading time are read out of
`arrivals.ts` and `reading.ts` by `arrival_rules.py`, not copied. Kinds are the queue's (line, feature, chip, store,
skill, card) plus level-ups, which take a turn too.

One route (human-paced, seed 0). The build holds day one only, so V4 (after B3, the end) has no further content to bring.

## Results

Counts are arrivals on the return; "reveal" is seconds from the first turn to the last; "squeezed" is non-line
arrivals the cap makes share its last turn.

| Leave point | Away | Lines | Feature | Card | Level | Total | Reveal s | Squeezed |
|---|---|---|---|---|---|---|---|---|
| V1, +0.13 h, after H1 | 1 h | 8 | 1 | 0 | 3 | 12 | 28.8 | 0 |
| | 8 h | 16 | 1 | 0 | 3 | 20 | 63.4 | 0 |
| | 24 h | 20 | 1 | 0 | 3 | 24 | 81.2 | 0 |
| | 3 d | 23 | 1 | 0 | 3 | 27 | 93.9 | 0 |
| | 7 d | 23 | 1 | 0 | 3 | 27 | 93.9 | 0 |
| V2, +3.23 h, after H5 | 1 h | 1 | 0 | 0 | 0 | 1 | 3.0 | 0 |
| | 8 h | 10 | 1 | 2 | 3 | 16 | 44.5 | 0 |
| | 24 h | 15 | 1 | 2 | 4 | 22 | 65.2 | 0 |
| | 3 d | 18 | 1 | 2 | 4 | 25 | 77.5 | 0 |
| | 7 d | 18 | 1 | 2 | 4 | 25 | 77.5 | 0 |
| V3, +5.07 h, after H6 | 1 h | 2 | 1 | 1 | 0 | 4 | 7.1 | 0 |
| | 8 h | 5 | 1 | 1 | 3 | 10 | 22.3 | 0 |
| | 24 h | 10 | 1 | 1 | 4 | 16 | 43.2 | 0 |
| | 3 d | 13 | 1 | 1 | 4 | 19 | 55.5 | 0 |
| | 7 d | 13 | 1 | 1 | 4 | 19 | 55.5 | 0 |
| V4, +7.58 h, after B3 | 1 h | 1 | 0 | 0 | 0 | 1 | 3.4 | 0 |
| | 8 h | 4 | 0 | 0 | 3 | 7 | 16.1 | 0 |
| | 24 h | 9 | 0 | 0 | 4 | 13 | 37.7 | 0 |
| | 3 d | 11 | 0 | 0 | 4 | 15 | 45.9 | 0 |
| | 7 d | 11 | 0 | 0 | 4 | 15 | 45.9 | 0 |

Chip, store and skill arrivals are 0 in every row (the report prints them). A longer absence never holds fewer
arrivals than a shorter one from the same point (`test_a_longer_absence_never_holds_fewer_arrivals`).

## Verdict

**The ladder is not flat.** Story lines and level-ups climb through 24 h to 3 days (V1: 12, 20, 24, 27 arrivals; the
reveal from 29 s to 94 s), so a longer absence does hold a recognisably bigger moment. Two qualifications: the
milestone-class arrivals (feature, card) step once between 1 h and 8 h and are the same from 8 h to 7 days, and every
row from 3 days to 7 days is identical, which fits day one's content running out (not tested here).

**The cap does not flatten anything.** It binds from 12 non-line arrivals; the most any return holds is 7 (V2 at 24 h
and later, with its lines), so "squeezed" is 0 throughout. The reveal's length is the lines' reading times (a 3 s floor
each), not the pace, and is skippable by tap.

Proposal 8's "start a new marker partly filled" is not warranted by this ladder; it was conditional on a flat one.
