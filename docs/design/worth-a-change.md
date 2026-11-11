# Worth a change

This note designs the direction of 2026-11-07: players should want to come back to their rules and mixes at least
periodically, beyond clicking a button so something doesn't run out again. One real save set one early mix and never
touched it; Idle Awakening, where the mix system comes from, makes its players babysit. The aim sits between the two. Mechanics
only: no content, card or goal names.

## What it proposes

- **A change is worth making when goals compete, and when upkeep asks.** Idle Awakening's reasons to re-mix (a cap, a
  starved input) are answered here by rules the player writes, which the game teaches; only the dry store's handover is
  engine mechanics, since a store cannot go negative. On top of that sits wanting one thing sooner than another, so
  the design's job is a steady supply of moments where the best setup moves, and a way to see it move.
- **The plan becomes something the player writes: `run {mix} until {goal}`, queued.** The engine's queue entries
  already carry an `until` condition (`engine/orders.py`, `QueueEntry`). Goal stints in
  the queue turn "which goal first" into a standing plan that acts while the player is away.
- **Every editor shows the change in goal times, before and after.** The mix editor's before → after block and the
  condition editor's dry run gain rows for the open goals: when each lands as set, and when it lands with the edit.
  Numbers, never a verdict.
- **Give the player the tools, not a button.** After the guided first mix and first rule no offer builds
  anything: a quiet dot marks what a rule or mix could answer. The player gets the tools and decides, rather than a
  button that solves the problem every time.
- **"Periodically" is a readout, never a band.** The simulator reports, per visit, how much sooner the open goals all
  land under the best setup than under the kept one, the gap in days between visits where that is worth acting on,
  and how many changes are worth making per absence. A person judges the rhythm from it; no number holds it
  (`sim-invariants.md`).

## Fit pass

Nothing here is a new system.

| Part | Extends | How |
|---|---|---|
| Goal stints | Standing orders and the queue (`systems.md`) | A queue entry whose verb is a mix switch and whose `until` is a goal row's condition (`GoalRow.until`). Its mix runs over the player's while it controls, as an order's mix does (engine `DESIGN.txt`, "Queue mix"); the engine pops it when the goal lands, and the next entry, or the player's own mix, takes over |
| Goal conditions | The order vocabulary: `CardCount`, `SkillLevel`, `Unlocked`, `StoreValue` (`engine/conditions.py`) | The condition editor offers the subjects the engine already solves for. A card's count, a skill's level and an unlock only grow, so a stint on one cannot come back on |
| Goal times in editors | View.goals and the readout's rate measure, over the editors' dry run | One dry run per edit; the server reads each open goal's time and binding line off the engine's own rates as set (`api/goalrows.py`) |
| Lately for stints | Chronicle and unwrap, via `engine/rulelog.py` | A stint's entry records its start, its goal landing and what its mix made while it ran |
| Offers that step back | Offers and quests; the repeat offers (`opening-screen.md`, the hands strip); the lessons (`game/lessons.ts`) | The same detection, a quiet dot in place of the build, below |
| The moments | Cards, goals, prestige, seasons and chores, trips, offers: all content on existing systems | Content supplies them; the simulator counts them |
| The readout | Simulator, open-work item 1, "What a re-mix is worth" | This note specifies that item |

Patterns: **Command** (a stint is a queued verb) and **Specification** (a goal is a condition in the one vocabulary
Gates already use). Nystrom's *Command* chapter is the precedent: a queue of commands is a plan that runs unattended.

## The design

### The moments

A moment is a visit where the best setup differs from the kept one by enough to act on. Each comes from something the
game already does:

| Moment | Produced by | Why the best setup moves |
|---|---|---|
| A new card that does old work better | Cards; a tool or method unlocked | The editor's goal rows show it once the player opens one |
| A new goal in view | Goals ("Always something to build toward, several at once") | Its cost pulls on skills or stores the kept mix weights lightly |
| A goal lands | The same | The share that served it now serves nothing in view; a stint pops by itself |
| A skill reaches its top | Prestige phases (`design/prestige-phases.md`) | Past the carry window its share earns goods and no XP |
| A prestige pick | Prestige nodes, which act on other skills | The picked node raises another skill's rates |
| A season turns | Seasons: "seasonal options that make your mixes worth re-tuning" | New cards and raised rates for its length |
| A chore arrives | Seasons' chores | Upkeep: a problem with a cost and a hint dot; the rule is the player's |
| A trip or an ask | Expeditions; offers | Its supply or its price is a goal with a store in it |

Two kinds, kept apart. **Upkeep** (a chore, a store that falls, a cap) is answered by rules the player writes, guided
by a hint; ignoring it costs what it costs, shown in the ledger as a fact. **Opportunity** (everything else) is optional: ignoring it costs only the gain, and the gain is shown.

**How content keeps them coming through the back half.** The supply is the goals. Each chapter's goals are written so
that the open ones draw on different skills' makings: a mix that serves one well serves another poorly. A content
check on the loader states it structurally: at every chapter's start, the open goals' costs name stores made by at
least two different skills (the loader knows which card makes what, so this needs no field). Seasons and prestige add
moments on their own clocks. The readout below is what holds the supply, not the content check: a stretch the readout
finds flat is a content gap, as "The back half never slows" already treats one.

### What to add first, and why

1. **Goal stints in the queue.** Strongest fit (the engine already runs them), and it answers the one reason left to
   change a setup. It also gives planning skill its payoff without rewarding presence: a player who queues "Timber
   until the next build, then Study until the skill's next marker" before bed wakes ahead of one who did not, by
   decisions made, not by the hour of the visit. Written from the Next list's `+ Plan`, or from the mix editor's foot
   (`Run until…`), picking a mix and one goal from the goals in view. A stint is listed in Next as `{mix} until
   {goal}` with its forecast time.
2. **Goal rows in the editors.** Without them the player cannot see that a share drag moved anything that matters;
   per-minute rates do not say which goal comes first. They come with the stints because a stint is chosen by them.
3. **A skill's level as a stint goal**, defaulting to the next marker and the top. It is `SkillLevel`, already
   solved for, and covers the top-out moment without a new condition.
4. **Later, only if the readout asks for it:** `while {season}` as a rule condition (the Clock's discrete state), and
   `once {skill} stops gaining` (the end of the carry window, a time the engine knows). Neither is needed for the
   2 AM test: inside an ordinary absence the carry window loses nothing, and seasons only add.

Not added: conditions on a store's rate or on which card runs (Idle Awakening had both). Every case found reads
better as a store level or a goal.

### The payoff, shown before and after

Before, in the mix editor, under the per-minute block, one row per open goal the edit moves:

```
goals             now   →   after
next build        2d 4h →   1d 9h
Woodcutting 15    6h    →   9h 30m
```

- Only goals the edit moves. Each time is read off the rates as set at the edit's instant (a tap of the hands set
  aside), the readout's measure below: a fork bounded by the forecast's instant cap reaches too few goals. It leaves
  out what orders and dry inputs take later, so it is the time at today's rates, not a promise.
- Under each row, the line that binds it, as a fact the server reads off the runs: the dry store a card moving the
  goal waits on and what comes into it (`limited by rope, 0.5/min`), else the goal's own rate (research
  `fun-from-choice.md`, proposal 1).
- The condition editor shows the same rows for running the rule's mix, beside its existing `while … runs` fact.

After, in the Rules tab's `Lately`: a stint's entry reads `ran 2d 3h · goal landed 4h ago · made 140 dry wood`, a
rule's adds what its mix made while on. Facts the save recorded, never a claim about the road not taken (see
Rejected).

### Offers teach, then step back

Do it once or twice, then let the player do it from there: they have the capability, but they have to interact with
the systems. Settled narrower still: after the guided lessons, **no offer builds a mix or a rule.**

- **The first mix, a second mix and the first rule are the only guided builds**, on the real editor. The first rule always goes through its lesson: an offer that cannot be pointed at waits
  for one that can.
- **After them, a hint, not an offer:** the same detection as before (a card tapped by hand again and again, a switch
  repeated, a red line or chip whose order card has no rule) puts a quiet dot on the thing itself, once, until touched.
  It opens nothing and highlights nothing: every card could join a mix or be its own rule, so the game does not choose.
  The red ledger line stays the main signal.
- **Upkeep stays the player's:** a chip's cure or a store that falls gets the dot like anything else, never a rule
  installed for them. The 2 AM test holds for a player using the tools the game taught; a player who skips them, or
  prefers tapping by hand, may: babysitting is never *prevented* for a player who wants it.
- **Judged by a cold tester who doesn't play idle games**, as the galaxy work was: the dot must still get a newcomer
  to try a mix or a rule (the reviewer who hand-tapped 91 times is the case it must not repeat).

When the readout exists, it shows the result: a route that writes no rules reaching the goals more slowly than the
own-rules route. The same gap is the simulator's one check on players who skip the tools, held today for `by_hand`
and `lazy` on day one (`sim-invariants.md`, D31).

## What the simulator measures

Built in `app/tests/worth/` on the visits of a played route (the typical route through day fifteen), read at each
visit's exit, the setup left running for the absence.

- **The set:** the open goals that are a choice (a skill's next level whose fastest ready card alone lands it at least
  `CHOICE_S` out, as `tests/dayone/goals.py` counts a choice) on the skills the player's own mix trains now. The
  player's mix says what they are pursuing; the readout asks how well a setup pursues it, not what to pursue.
- **A setup's score:** the time until every goal of the set has landed. A setup that leaves a goal of the set
  unserved never lands it, and reads `never`.
- **The best setup:** the probe keeps the player's mix's cards that train no skill (upkeep) at their shares and splits
  the rest of the hands between the set's fastest cards in proportion to each card's time alone. Every goal then lands
  together, at the sum of the times alone: the time one card after another would take. The best is the least score
  among the probe and the routes' own mixes.
- **Rates, not a simulation:** a mix's XP rate into a skill is the engine's own rate formula (base, modifiers,
  share) over the mix's ready cards, a card that cannot run now giving its share to the rest as `SPENT` does. It leaves
  out what orders, taps and dry inputs take from the mix later, alike for every setup; the readout prints how much of
  the kept mix's promised XP each absence delivered, so a drift in that is seen.
- **Worth, per visit:** a setup's score less the best's, in hours and as a fraction of the setup's score.
- **Routes on the same saves.** *Keeper* is the route as played: its mix changes only where a chapter's moves make it,
  never for a goal (as a real save played). *Tuner* takes the best setup whenever its own mix's worth crosses the threshold;
  its moments show how often a change is worth making. Two controls: *fresh* takes the best at every visit, so its
  worth is how far the best moved since the visit before (re-mixing should be worth little); *once* takes the best at
  the first visit and never again (worth a lot, more as the game moves). The readout prints each route's worth by
  decile, so a measure that cannot tell them apart shows.
- **Moments:** a tuner visit where worth crosses the threshold, tagged with its causes: the table above's kinds, a
  goal of the last set landing, the player's mix edited, and the set gaining a skill.
- **Printed:** per day, keeper's worth and tuner's moments by cause; fresh's worth at visits with and without a cause;
  moments per visit by week beside the opening's; the longest stretch with none; every visit.
- **Not built:** own rules against offers only (goal arrival on a route that writes stints against one that only
  accepts offers) waits for goal stints.

**The worth threshold** says which visits count as moments: 25%, above where fresh's worth sits at visits with no
cause, so the best drifting as goals near is noise and a cause moving it is a moment. It sorts visits for the printout
and fails nothing. The readout is committed as an approval snapshot like the others (`sim-invariants.md`) and costs a
few CPU seconds on a play the week-two job already has. Flat near zero after week one means goals that pull on one
skill: content work, not a mechanic.

## What must stay true

- **The 2 AM test.** A stint pops at the instant its goal lands, so a babysitter switching by hand gains nothing on
  the queue. Every new condition is one the engine solves for. No moment rewards the time of the visit, only the plan.
- **Ignoring upkeep costs what it costs.** The queue starts empty and nothing is installed for the player: the player's
  own mix and the dry-store handover run, and a full store costs its overflow, shown in the ledger. Keeper is reported
  with `by_hand` and `lazy`, never held to a floor; its gap to tuner may include beats.
- **Nothing is taken back.** No moment lowers a rate; a season adds; a stint popping returns to the player's own mix.
  A saved mix's rates dropping with no change by the player is a shown number not coming true, so that one check fails.
- **No attention-efficiency.** The worth figure is about setup only: tuner and keeper visit on the same schedule.
- **Facts, never verdicts.** No row, mark or line says better, best or efficient; it says when a goal lands.

## Decisions this changes

- **The mix, "A re-tune is only ever set off by something the player chose":** reworded (settled below): a re-tune is
  never necessary, and a season or an ask may make one worth making. The old line conflicted with the seasons section.
- **Open-work item 1, "What a re-mix is worth":** is specified by the section above.
- **The better-option mark and the one-change-per-absence ceiling are dropped** (`choice-not-protection.md`); the
  editors' goal rows carry the information when the player looks.
- **The Rules tab's Next:** holds goal stints as well as `When ready` taps.

## Rejected, and why

- **An "optimise" button or a suggested best mix:** it makes the decision for the player, and it is the verdict the
  game never gives. Idle Awakening's opaque Auto effort was the clumsy part of its editor.
- **A better-option mark on a saved mix:** the game computes the best mix and points at it, which is the optimise
  button above. The goal rows show what a change does once the player opens one.
- **Authored offers for goal rules:** the offer would encode the game's guess at what the player wants, and accepting
  it is clicking the button again.
- **Drift, decay or fatigue on a long-running mix:** upkeep the game imposes, and it sets a check-in schedule.
- **"Earned N hours sooner than without it" in `Lately`:** a claim about a road not taken, which needs the save as it
  stood when the rule started, and reads as praise. What the mix made while on is a recorded fact.
- **A re-mix bonus, or a reward per change:** it pays for the act, not the result, and attention would earn it.
- **Goal stints as rules with a negated condition:** rules are priority among things that recur; a goal lands once.
  The queue is already "the plan" in the engine, and it pops.
- **Worth at the nearest single goal** (the readout's first build): one card at a full share always wins it, so any
  mix split across several cards reads far behind whatever the player does; keeper's worth measured the split, not
  the play.
- **A sum or mean of the set's landing times:** one pair of hands lands goals soonest on average one at a time,
  soonest first, so a sum favours putting the hands on the nearest goal, the first build's bias again, milder. The
  time until all land is the same for a mix in proportion and for a queue of stints, so it stays true once stints
  ship.
- **Every open goal as the set:** a goal on a skill the player's mix never trains would read `never` at every visit,
  which says what the player chose, not how well the mix serves it.
- **Landing times from the engine's forecast or by advancing each probe:** from the first days the set's slowest goal
  is tens of hours out on its card alone, past the forecast's instant cap (which reaches about 2 hours by day nine), and advancing each
  probe to its goals cost the first build about 400 CPU seconds per push. The rate formula is the engine's own and costs
  milliseconds.
- **The view's next-level time under a probe:** it reads nothing while the hands run a tap, which most visit exits do.

## Settled

- **Periodically means "more than basically never".** Changes worth making per absence are reported, with no floor
  and no ceiling (`choice-not-protection.md`; `sim-invariants.md`).
- **A season or an ask may make a change worth making, never necessary** (`decisions.md`, "The mix", reworded).
- **Plan steps are never offered.** Adding mixes and rules is already automated to the point of a player not needing
  to interact with them at all. A plan written for the player is the engagement removed.

- **Offers teach, then step back** (above): after the guided lessons, hints only.
