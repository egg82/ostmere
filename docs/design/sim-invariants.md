# Simulator: invariants fail, taste reports

Every check the pacing simulator makes, sorted by the rule of 2026-11-07, and what each now is. Ids, files and
mechanics only: no content.

**The rule.** A pacing check may fail CI only on an invariant:

- **softlock**: a route cannot reach the next thing, or a state shows no way out;
- **spiral**: something compounds past recovery, or being away loses what was already made;
- **babysit**: a player who uses the taught tools ends behind one who watches;
- **shown**: a number or state the page shows does not come true.

Everything else about the rhythm of play is **taste**. Taste never fails on a threshold. It is printed as a readout,
and the readout's text is committed beside it: when it changes, CI reports the diff and never fails; a person reads
it and commits the new text by writing it again. No band or target is set for a rhythm. Scripted players who skip the tools are
reported, never held to a floor; the one check on them is that they land measurably behind.

Two more classes:

- **correct**: content, engine and plumbing doing what they say (lines never repeat, saves load, an authoring rule
  `decisions.md` states, the chain of saved ends matching today's play). The four invariants are about pacing;
  correctness was never in question. These keep failing.
- **control**: a planted fault proving an instrument can fail. A control of a counter asserts the count on its planted
  fixture; the controls of the bands went with the bands.

## Where each check went

Paths are under `app/tests/`. Where a test's name names content, the row gives its file alone.

### The opening (job `playthrough`; readout `opening/report.py`)

| # | Where | What | Class | Now |
|---|---|---|---|---|
| O1 | `opening/test_opening_pacing.py`: `test_no_gate_counts_taps_of_one_card` | no story gate counts taps of one card | correct (`decisions.md`, "No gate counts taps") | fails |
| O2 | the typical route's timeline | taps and decisions between new things | taste | readout |
| O3 | each push route | the longest run of taps of one card | taste | readout |
| O4 | a day away from the first order | what it opens | taste | readout |
| O5 | the crafts at first show | shown together, each blocked or ready | taste | readout |
| O6 | `opening/test_opening_pacing.py`: `test_either_craft_first_reaches_the_end` | either order reaches the end moment | softlock | fails |
| O7 | same: `test_tapping_extra_early_cannot_reach_the_end_before_its_steps` | extra taps never reach the end sooner | babysit | fails |
| O8 | `opening/test_opening_length.py`: `test_a_newcomerish_player_reaches_the_end` | the route reaches the end, with no clock; when is the readout's | softlock + taste | fails; the minutes are a readout |
| O9 | `opening/test_level_pays.py`: `test_every_marker_pays_when_its_level_lands` | a level's marker pays when the level lands | shown | fails |
| O10 | same: `test_a_level_never_comes_sooner_than_the_one_before` (`dayone/growth.py`, `runaway`) | no level's pay outruns its curve step | spiral | fails |
| O11 | `dayone/growth.py`, `climb_hours` | each skill's climb against the fastest; the 3x band is gone | taste | readout |
| O12 | `opening/test_second_skill.py`: `test_the_skill_checks_cover_the_new_row_and_pass` | markers paid, no blank level, no runaway | shown + spiral | fails |
| O13 | `opening/test_phase_pays.py`: work pays are adds | later phases' work pays never multiply | spiral | fails |
| O14 | same: `test_every_level_of_every_phase_a_track_reaches_pays` | every level a track reaches pays | correct (`decisions.md`, "A level is a thing, not only a number") | fails |
| O15 | same: no three speed-only levels running, and the loader's refusal | at least every third level brings something named | correct (the same rule, stated for authoring) | fails |
| O16 | `opening/test_after_end.py`: `test_the_rest_offer_never_shows_before_the_end_lines_are_read` | the content's `after_end` gate holds the offer | correct | fails |
| O17 | `opening/test_first_rule_offer.py` | every route meets a rule offer before the end | babysit (the tool is taught) | fails |
| O18 | the by_hand player past the end | actions between the offer and the door's glow | taste | readout |

### Day one (job `playthrough`; `dayone/verdicts.py`; readouts `dayone/report.py`)

| # | Where | What | Class | Now |
|---|---|---|---|---|
| D1-D4 | each visit's counters (`dayone/checks.py`, `figures`) and the opening's own row | new and bigger things, the first one's second, decisions, actions, idle, runs, effort | taste | readout |
| D5 | `checks.absences` | what a day away from each visit opens | taste | readout |
| D6 | `CHECKS["story_order"]` | day one's beats all land, in authored order | softlock + correct | fails |
| D7 | `checks.near_promise` | returns showing no beat on the near promise | taste | readout |
| D8 | `dayone/story.py`, `flatcheck` | the content team's story-shape flags on the route | taste | readout |
| D9 | B3's hours after the end | the typical band and the babysitter's floor are gone | taste | readout |
| D10 | `CHECKS["b3_relative"]` (`dayone/bands.py`) | a tool user's B3 lags the babysitter's by its own gaps | babysit | fails, on `TOOL_USERS` |
| D11 | `CHECKS["queueable"]` | every rate-raising step queueable before it is ready | babysit | fails, on `TOOL_USERS` |
| D12 | `dayone/goals.py`, `goal_summary` | samples with no driven goal; samples where weighting decides | taste | readout |
| D13 | `CHECKS["promises"]` | every time the page draws comes true | shown | fails |
| D14 | `dayone/test_dayone_routes.py`: `test_what_lands_away_is_seen_on_return` | a beat is seen no sooner than it lands | correct | fails |
| D15 | `dayone/test_dayone_two_am.py` | the babysitter given the whenever player's reveals ends level | babysit | fails |
| D16 | `dayone/test_dayone_cures.py` | every chip shown has a cure on offer | softlock | fails |
| D17 | `dayone/test_dayone_forecast.py` | the forecast is what advance does | shown | fails |
| D18 | same: `test_a_forecast_stays_inside_its_budget` | the forecast's cost | correct | fails |
| D19 | `dayone/test_dayone_invariants.py` | a card showing every need met starts when tapped | shown | fails |
| D20 | `dayone/test_dayone_aims.py`: `test_every_aim_is_stated_at_some_view` (`dayone/screen.py`) | every declared aim is stated; views with no aim are the readout's | correct + taste | fails; the count is a readout |
| D21 | `dayone/screen.py`, `early` | mechanics drawn in the first five minutes | taste | readout |
| D22 | `dayone/test_dayone_level_pays.py`: `test_no_skill_pays_speed_alone_three_levels_running` | O15's rule on the levels day one reaches | correct | fails |
| D23 | `dayone/levelpays.py`, `speed_only_leaves` | leave points naming only a speed level | taste | readout |
| D24 | `dayone/test_dayone_prestige.py` | a visit clicker ends level with an instant one inside the carry window | babysit | fails |
| D25 | `dayone/test_dayone_absence.py`: `test_a_longer_absence_never_holds_fewer_arrivals` | a property of the page's arrival queue | correct | fails |
| D26 | the absence ladder (`dayone/absence.py`) | what a return holds after 1, 8 and 24 h, and each gathered store's cap loss from day one's leave points as D30 reads it (day one's leave points come before the cap rule is taught, so they are read, never checked) | taste | readout |
| D27 | `dayone/test_dayone_rebase.py`: `test_the_rebased_story_lands_in_order` | a golden ended save's story lands in order; what its load opens is the readout's | correct + taste | fails; the counts are a readout |
| D28-D29 | the rebase's lines; `dayone/test_dayone_lines.py` | lines are text keys; none repeats | correct | fails |
| D30 | `dayone/capcheck.py` | from a chapter's end, 8 h and 24 h away lose at most `LIMIT` of each gathered store's making | babysit | fails (H4's and two of W7's strict xfails: held below) |
| D31 | `dayone/test_dayone_human.py`: `test_the_players_who_skip_the_tools_land_behind_the_typical_route` | `by_hand` and `lazy` each land some unlock later than typical by more than `unlock_margin_s` | the check on players who skip the tools | fails |
| D32 | the human-paced player's day (`dayone/human_flags.py`) | sessions, dead gaps, bored leaves, earned and fixed-time unlocks | taste | readout |

### Day two (job `playthrough-day-two`; `daytwo/verdicts.py`; readouts `daytwo/report.py`)

| # | Where | What | Class | Now |
|---|---|---|---|---|
| T1 | each visit, with `daytwo/checks.py`, `marks` | day one's counters; the edge of written content and returns during a long wait marked | taste | readout |
| T2 | `checks.absences` | what each absence between visits opens | taste | readout |
| T3 | `CHECKS["story_order"]` | day two's beats all land, in order | softlock + correct | fails |
| T4 | `daytwo/story.py`, `flatcheck2` | story-shape flags on the route | taste | readout |
| T5-T6 | B4's hours after B3 | the typical band and the babysitter's floor are gone | taste | readout |
| T7 | `CHECKS["b4_relative"]` | a tool user's B4 lags the babysitter's by its gaps | babysit | fails, on `TOOL_USERS` |
| T8 | `CHECKS["cap_loss"]` | typical's day-two end, as D30 | babysit | fails |
| T9 | `daytwo/abs_band.py`, `summary` | each beat from B5 on, its day beside its `target_day` | taste | readout |
| T10 | `daytwo/test_daytwo_two_am.py` | 2 AM across day two | babysit | fails (a strict xfail: held below) |
| T11-T13 | `daytwo/test_daytwo_routes.py`, `daytwo/test_daytwo_repeat.py` | beats seen after landing, no repeats, the answered branch's lines, the player model's leave rule, the repeating lane | correct | fails |
| T14 | `daytwo/caps.py`, `lines_of` | each store's share lost to caps as played and away | taste | readout |

### Day three (job `playthrough`; `daythree/verdicts.py`; readouts `daythree/report.py`)

| # | Where | What | Class | Now |
|---|---|---|---|---|
| H1 | `daythree/test_daythree_routes.py`: `test_the_route_plays_day_three_to_b5` | each push route reaches B5 | softlock | fails |
| H2 | B5's day | beside its target day, on typical and sharp | taste | readout |
| H3 | `daythree/counters.py` | spend and decide per visit, marked as T1 | taste | readout |
| H4 | cap loss from day three's end, as D30 | | babysit | fails (a strict xfail: held below) |
| H5 | `daythree/plumbing.py` | a card shown ready starts; a tapped trip lands when drawn; a dry trip's maker is in reach | shown + softlock | fails |
| H6 | 2 AM across day three | | babysit | fails (a strict xfail) |
| H7 | `daythree/test_daythree_town.py` | keeping the join's split ends level with re-splitting by hand | babysit | fails |

### Week one (job `playthrough-week-one`; `weekone/verdicts.py`; readouts `weekone/report.py`)

| # | Where | What | Class | Now |
|---|---|---|---|---|
| W1 | `weekone/test_weekone_routes.py`: `test_the_route_plays_days_four_to_six_to_g2` | each push route reaches G2 | softlock | fails |
| W2 | `weekone/test_weekone_routes.py` (G1's fight) | the page reads G1's fight as won | shown | fails |
| W3 | B6 and B7's days | beside their target days; the sharp floor tests went with the band | taste | readout |
| W4 | `test_night_seven_falls_before_the_seasons_turn` | the story against the calendar | correct | fails |
| W5 | `dayone/daily.py` | each calendar day's arrivals by kind, on typical, sharp and whenever | taste | readout |
| W6 | each chapter's visits | spend and decide, marked as T1 | taste | readout |
| W7-W8 | cap loss, as D30; the checks past the sinks, as H5 | | babysit; shown + softlock | fails (W7 on days four and six strict xfails: held below) |
| W9 | 2 AM across the week, fights running | | babysit | fails (a strict xfail) |
| W10 | `weekone/test_weekone_fights.py`: the same decisions at any visit times end the same | | babysit | fails |
| W11 | same: building the gear wins more fights | the gear's stated strength comes true | shown | fails |
| W12-W14 | a store a threat emptied has a card to refill it; fight landings; every chip has a cure | | softlock; shown | fails |
| W15-W16 | long absence instants; journal notes and line keys | | correct | fails |

### Week two (job `playthrough-week-two`; `weektwo/verdicts.py`; readouts `weektwo/report.py`)

One row stands for its siblings in `weektwo/test_weektwo_routes.py` (day eight), `test_weektwo_nine.py`,
`test_weektwo_eleven.py` and `test_weektwo_twelve.py`.

| # | Where | What | Class | Now |
|---|---|---|---|---|
| K1 | each chapter's "the route plays" test | each push route reaches the chapter's stop beat | softlock | fails |
| K2-K3 | each chapter's beats and absences | beats beside their target days; what each absence opens | taste | readout |
| K4 | `weektwo/verdicts.py`, `calendar_days` | each calendar day's arrivals after week one's | taste | readout |
| K5 | `weektwo/counters.py` | spend and decide per visit, a queued stage refused, marked as T1 | taste | readout |
| K6-K7 | cap loss, as D30; 2 AM per chapter | | babysit | fails (cap loss on days eight to fifteen and day eight's 2 AM strict xfails: held below) |
| K8-K9 | a save from the chapter before loads and plays on; every chip has a cure | | softlock | fails |
| K10 | typical's late store at the ends of days eleven and twelve | | taste | readout |
| K11-K12 | calendar, a fight pool ending its card, a join's tally, notes, line keys | | correct | fails |

### Chains, ladder and fixtures

| # | Where | What | Class | Now |
|---|---|---|---|---|
| C1 | `weekone_saved/`, `weektwo/test_weektwo_saved.py`, `weekone/test_weekone_export.py` | the saved ends are today's play, link by link | correct | fails |
| C2 | `ladder/readout.py` | each skill's ladder, each card's share by day, each skill's XP by source per band of days, and whether one saved mix shape always wins (`ladder/dominance.py`; its control sets in `ladder/test_dominance.py`) | taste | readout, compared in `weektwo/test_ladder_readouts.py` |
| C3-C6 | `ladder/test_*.py`, `banked/` | the ladder's arithmetic; 2 AM, the checks past the sinks and the sink policies on a fixture chapter | control; babysit | fails |
| C7 | `worth/readout.py` | what a re-mix is worth per visit on keeper, tuner's moments by cause, the two control routes, moments per visit by week beside the opening's (`worth-a-change.md`) | taste | readout, compared in `weektwo/test_worth_readouts.py` |
| C8 | `worth/test_measure.py`, `worth/test_summary.py` | the worth measure on a fixture world (a split in proportion worth nothing, a starved goal worth a lot, the first build's measure beside it) and the readout's arithmetic | control; correct | fails |

The opening's loader, lock, content-contract and cost tests (`opening/test_released.py`, `opening/test_chapters.py`
and the like) are content structure, not pacing, and are untouched.

## The one hand-picked line on an invariant

Cap loss (D30, T8, H4, W7, K6) is babysit: a tool user who must come back to spend a full store is babysitting. Its
limit, `LIMIT` in `dayone/capcheck.py` (half of each gathered store's making over 8 h and 24 h away), was picked, not
derived. Every other failing check is exact: a route reaches a beat or not, a drawn time comes true or not, a
babysitter ends level or ahead. With the default cap orders gone (`open-work.md`, item 15 (b)), typical writes its own
cap rule, which is the point.

## Held today

The strict xfails (T10, H6, W9, day eight's K7; and cap loss: H4, W7 on days four and six, K6 on days eight, nine,
eleven, twelve and fifteen) are babysit invariants failing on today's content, each for the reason its xfail names.
The cap-loss ones are content gaps, each a store a card fills with no sink behind it, or `field_track`'s input ratio
(`open-work.md`, items 16 and 24). The taste entries of day one's and day two's `HELD` ledgers went with the taste checks, the
`by_hand` and `lazy` per-visit entries among them, and with them the ledger machinery in both packages.

## Which players are held

| Player | Uses the tools | Held to |
|---|---|---|
| typical, whenever, sharp, evenings, lunch, return_22h, larder_first (`dayone/routes.py`, `TOOL_USERS`) | yes | every invariant |
| `by_hand`, `lazy` | no rules or queue; once a day | softlock, spiral, shown and correct; and landing behind typical (D31) |
| babysitter | no queue or rules, never away | the measure the babysit checks compare against |
| keeper | typical as played: its mix changes only where a chapter's moves make it, never for a goal | the worth readout (C7), beside tuner on the same saves |

Taste readouts print every route a package plays on a push.

## The readout report

- **Stored** one file per readout under `app/tests/readouts/`, named for its package (`dayone-typical.txt`,
  `weektwo-twelve.txt`, `ladder-sharp.txt`). Generated, so in a directory of its own (`engineering.md`, "Structural
  gates"); one file per readout, so a diff names the rhythm that moved.
- **Rendered** by each package's `report.py` (`ladder/readout.py` for the ladder, `worth/readout.py` for the worth readout): `NAMES` and `readouts()`, from the
  push routes at seed 0, with ids, counts and game times only, never CPU or wall time.
- **Compared** by `app/tests/readout_snapshot.py`, `check`, in each package's `test_<package>_readouts.py`, in the job
  that already plays the routes: `playthrough`, `playthrough-day-two`, `playthrough-week-one`, `playthrough-week-two`.
  Week one's chapter readouts are compared in `weekone/test_weekone_routes.py` and day one's rebase readout last in
  `dayone/test_dayone_rebase.py`, after the setups whose readings they reuse. A difference is reported, never failed: a
  `ReadoutChanged` warning carries the diff's first lines (pytest's warnings summary, in the job's log) and, when
  `READOUTS_OUT` is set, the new text is written there and kept as the job's artifact. A package's committed files must
  be exactly the readouts it writes, and an empty readout fails (a broken play, not taste).
- **Committed** with one command from `app/`: `python -m tests.readout_snapshot --write` writes every package's
  readouts and removes files nothing writes; `--write dayone daytwo` writes only those. Because chapters play on from
  earlier ones, a change early in the game moves every later readout, so committing the new text writes them all.
- **Merges**: two branches that each move a readout conflict on its file. Write it again on the merged tree, never take
  a side.
- The deep nightly run plays more routes and seeds; their figures are printed by the reports, never compared.

What stops slow drift across many committed changes is the drift judge (`drift-judge.md`), which a session runs after landing a readout change.
