# Banked time: what engineering builds

Open-work item 8: hours away should have somewhere to go. By day two's end every gathered store sits at its cap, so
what the hands and the townsfolk make past it is lost. This plan gives that production sinks: work that takes stores.
Their content is in `content/` (`team/banked-time-open.md`, questions BT1–BT6, never shown to the owner); this file holds
only what the code needs. Beats are named by id. Sizes: **S** under a day of agent work, **M** a few days, **L** a
week or more.

Interface: engine `DESIGN.txt`, "BANKED TIME", and `api/CONTRACT.txt`, "BANKED TIME". An implementer gets one item,
those two sections and this file.

## Measured

Day two's routes at `5f2b4c1`, seed 0, each store sampled every 15 game minutes; lost is the ledger's net while the
store is at its cap. XP still trains at a cap, so this counts materials only.

| Span | Share of each gathered store's making lost to its cap |
|---|---|
| Day two as played (B3 to the last decision) | 82–100% on every route |
| Away 8 h, 24 h or 72 h from day two's end, nobody deciding | 96–100% on every route |

The camp store loses 14–86% during day two by route, and all of it after B4, because its last level is reached.

This is not an attention bug: the 2 AM test is level on day two, because a babysitter has nothing to spend on either.
It is a value problem. A return after 8 h shows what a return after 2 h shows. So the fix is a number the content is
sized to (item 2), not a new engine guarantee.

**The target:** over an 8 h and a 24 h absence from each chapter's end, on the typical route, at most half of what
each gathered store makes is lost to its cap. 72 h is reported, not checked: every sink is finite ("Everything has a
cap"), so a long enough absence runs them all, and the babysitter runs them the same.

## The new kinds of things, and what they fit into

| New kind | Fits into (`docs/systems.md`) | Why not something new |
|---|---|---|
| A trip (an expedition's first slice) | Cards: an uncapped card with inputs, run in the mix and held against its supply store | The hold already runs a consumer at exactly the fraction that keeps a store at its level, so production past it goes on trips with no order chasing a cap. Uncapped, because a capped card completing greys the mix and would stop the hands at 03:00 |
| A trip's discrete returns (finds, clues, map) | Triggers on the trip's completion count | A solved subject, so each lands at the exact second, whatever the share |
| A trip that fights | Combat: a FightDef on the trip's card, the hands' side | The seam combat named: "a side made of who goes" is the player alone until backup |
| A comfort (the camp made less miserable) | Cards: a capped craft with a big cost, built by the queue | A build is already how the camp gets better; "When ready" queues it across absences |
| An arrival ("surplus that lets people stay") | Offers (an offer on a food store's level), the queued one-off its answer starts, Triggers (lane and default rule on its completion) | Day two's offer, queued one-off and installed rule, in that order |
| "Lost to caps" | Simulator only | Never served: time away is shown as what got done, never as what was missed |

Nothing new in the engine: no type, field, verb, event kind, Save field or system. Rejected shapes are in
`DESIGN.txt`, "REJECTED, AND WHY (banked time)": a bank of idle hours, speed bought with time, overflow spilling
into another store, a separate expedition runner, a hands tap rule to re-send trips, and capped trips.

## Work, by system

Each item merges on its own, in this order. Items 1–4 must land before day three's content is sized; item 5 is day
three's content; items 6–9 can follow it.

1. **Lost to caps in the simulator** (**S**, tests). A shared module (`app/tests/dayone/caploss.py`) that, from a
   save and its rules, reads each unlocked store's ledger line event to event over a span with nobody
   deciding and over a played route's history between decisions, and sums made (the positive contributions) and
   lost (the net while at the cap), per store. `python -m tests.dayone.report --absence` and the day-two report gain
   the column for 8, 24 and 72 h. Store ids only. Accept: a fixture with a maker into a full store reports lost equal
   to its rate times the span, a store below its cap reports 0, and the module asserts it sampled a non-empty set
   of stores; day two's typical reproduces the table above within a point.
2. **The cap-loss check** (**S**, tests). A verdict `cap_loss` on the typical route: from each chapter's last
   decision, 8 h and 24 h absences lose at most half of each gathered store's making. Gathered: a store some card
   on a lane makes; not a tally store, and not the camp store (its levels pace the story by design). A chapter's end
   is read as a player has it, with the chapters after it merged: day two's from the visit B4 is seen in, where day
   three's track is offered (`tests/daytwo/caps.py`, `shipped_end`); on day two's rules alone every gathered store
   fails, which is the check's control. Accept: a planted fixture with a held trip passes, the same without the trip
   fails.
3. **The trip shape on the engine** (**S**, tests, blind). Engine-contract tests for invariants 87–89
   (`DESIGN.txt`, "BANKED TIME") on fixture rules, written from the interface by an agent that has not read the
   engine. No engine code should change; if a test goes red, that is an engine bug and lands findings-first (strict
   xfail, then the fix). Accept: each test has a planted control (a hold that leaks one unit past its level; a
   find's trigger read off the visit time; a trip that pays while paused) that turns it red.
4. **Sink policies and the 2 AM test** (**M**, tests). Route policies: sharp and typical set a trip held against
   its supply store at the visit it opens and queue each comfort with "When ready" when it shows; lazy does neither;
   whenever answers arrival offers by the answer order (day-two plan, item 4, which this item needs). The 2 AM test
   replays with a trip held and a comfort queued across the babysitter's and the whenever player's visits. Built on
   a fixture chapter until day three exists. Accept: level on the fixture; a planted comfort first unlocked while
   the player is away (a trigger in the night) turns the 2 AM test red, which is why content must show every sink
   unready before it can be afforded.
5. **Day three's sinks** (**M**, content, after BT1–BT4). The trips, comforts and arrivals BT1–BT4 settle, in day
   three's chapter file, with their lines; finds as triggers on completion counts; arrival offers with their
   make-room one-offs and installed rules. Accept: the loader passes, item 2's check passes at day three's end on
   typical without a held entry, item 4's 2 AM test is level, and B7's arrivals gate lands inside its band.
6. **The page's trips** (**S**, client; before day three if BT1 puts a trip in it). The figure away from the scene
   while a trip runs on a tap, and for the trip's share of a cycle while it runs mixed, picked by card id as poses
   are; a trip's completions in the log and its finds in the band, as the arrival queue already places them. Accept:
   a render at phone width and in dark mode, looked at (`headless-render`); a client test that nothing on the page
   totals what a cap lost.
7. **The day-one tests past the sinks** (**S**, tests). "Leaving and coming back always pays" covers a trip tapped
   (its drawn landing comes true); the cures check covers a trip paused dry (its supply's maker is in reach); "a card
   that shows every need met does the thing" covers a trip and a comfort. Accept: each extended check goes red on a
   planted fixture, and the held ledger of today's failures does not rise.
8. **Art** (**M**, after BT3). The comforts' scene states and the away pose, picked from the packs first
   (`sprite-catalog`).
9. **A trip that fights** (**S**, tests, after combat-plan items 2 and 8). An engine-contract test on a fixture trip
   with a FightDef on the hands' side: its supplies are taken whole whatever the odds, its makes scale by the share
   won, and its finds count trips made, won or lost. Accept: planted mutants (odds applied to inputs; finds read off
   the lost tally) turn it red.

## What this leaves for later, and where it plugs in

Each is a KNOWN GAP in engine `DESIGN.txt`, "BANKED TIME". Backup on a trip is a support card on each member's ruled
lane while the trip runs, adding to the trip's side strength; it needs a stack entry conditional on another card
running, decided by the first expedition with backup. Stance moves to that same decider. Wide expeditions are a share
of the town's mix, once the town has one. Study that takes materials (BT6) is the trip's shape and needs nothing new.
