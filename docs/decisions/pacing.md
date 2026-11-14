# Pacing curve

Caps, the opening's pace, each skill's pace, and prestige.

## Finite, and the walls are the world

- Everything has a cap, and maxing it is an event that ends its own little story, never a bar that greys out. No
  infinite point dumps.
- Costs read as the world ("the bridge needs 200 planks because the river is wide"), not as `base × rate^n`.
- **Each new layer reworks the old ones.** An unlock chains into a few more and improves upgrades already owned, so
  old systems never go stale (Orb of Creation, the pacing benchmark here). Reveal as a steady drip; never dump the
  choices early (its 1.0 did, and early players missed the drip). Each new system arrives alone with a small first
use that teaches it, and every number can show where it comes from (some of Orb's mechanics confuse at first).
- **The opening is fun first; the weakness is felt inside it, never instead of it** (the
  preview was good but not yet as fun as Idle Fantasy; Progress Knight was addictive from its first minute while
  starting weak). The hooks, in order:
  - **Levels mean something:** something new every few levels, and the player can see what level each thing needs
    and what the next level opens (near-perfect knowledge; a story unlock shows that something is there without
    saying what).
  - **Skills feed each other,** visibly: what one skill makes is what the next needs.
  - **A bar to work toward before it can be used** (as in Idle Awakening): an overall progress bar, filling from
    everything the player does and paying out bonuses, is on screen from early on but not interactive for a while, so
    every action, even a slow one, visibly earns toward something coming.
  - **Time to the next thing is measured in effort, not hours**: seeing a whole system coming feels great when
    it is near. While play is manual, a new system arrives within a few minutes of effort; once mixes and orders carry
    the player through hours, a new system may take days, since waiting no longer costs attention. **The effort per new
    thing stays roughly constant** while the clock time between them stretches, which is what keeps the reward
    coming. The pacing simulator measures active effort (taps and decisions) to each new thing, alongside elapsed
    time, and flags a stretch where that effort climbs.
  - **Progress made while away**, never a daily reward.
  - **The story is told where the eyes are,** so the slowness means something.
  - **Fewer upkeep taps, more real decisions** with visible consequences.
  - **No gate counts taps** (the preview's tap, wait, tap, wait was the counter-example: 12 gathers to open the ruin, 10 scavenges
    for the fire). Repeating a card can pay out (a level, a find), but what opens the next thing is a different step
    the player takes, never the Nth repeat of the same one.
  - Surprise (a lucky find) is a minor extra, not a pillar.
  - **From Idle Awakening's pacing** (studied 2026-10-15, from own-play notes kept outside the repo):
    something new every 2–5 minutes early, the main level about every 10, judged on real players' runs; a cheap, visible
    first win that opens several things at once; a system arriving with the problem it cures (mixes when juggling by
    hand starts to hurt); costs as have/need and effects as before → after; empty states that preview what is coming; a
    quiet dot only on a new control, cleared once the player interacts with it or puts it to work, never a count. Not
    taken: hiding unavailable cards (ours stay visible and muted), and its banked offline time with a speed-up (time
    away is never a currency).
  The rule below on slowness stands, but shorter and lighter than the preview's first cut.
- **The first minutes are slow, made by hand, and told**. Roughly the first ten minutes are
  narrative-heavy and painstaking for the character, so the player feels their weakness through the screen before any
  power (A Dark Room's hook). They run on **one-off narrative actions**: standing up, looking around, gathering dead
  wood by hand. Each runs once, says something and opens the next; they are front-loaded, then sparse later, used where
  the story needs a step. **A finished one-off moves to the Book's Done page**, as every finished card does (upgrades,
  research, built projects), as idle games usually do: a story step is a card with a cap, with no special case. Its
  record is also the log line it wrote (the journal, once it exists), and what it built shows in the scene. **Tools come before
  skills:** bare hands gather; a skill like Woodcutting opens once something has been made to cut with. Learning stays
  by necessity, but each complex system (the mix, orders) is made obvious in the UI when it arrives.
- **The opening is 15–30 minutes of near-constant interaction**. The first leave-it-running moment (a standing
  order, or bars that keep going) comes within about 15 minutes, so a lunch-break player reaches it in one sitting and
  never feels leaving is inefficient; the rest of the opening is there for whoever keeps playing. Leaving even earlier
  strands nothing: whatever is mid-bar finishes while you're away. The struggle is felt in how many steps things take,
  never in waiting: bars are seconds, and no wait blocks the current goal for more than about a minute unless it is
  filled with steps toward that goal. **The steps are different steps, never one tap repeated into a chore** (feeling the character's struggle is good; wondering when
  the grind will end is not): work the
  player would otherwise tap over and over becomes mixable soon after it appears, and the preview's logs count runs of
  one card tapped in a row to check it. Every judgment on the first hour's pacing and story concentrates here; it is
  where a player stays or leaves. The simulator reports it (time to the first leave-it-running, longest stretch with
  nothing to do). **It is paced for someone who has never seen the game** (what takes the developers 40 s takes a newcomer 5
  minutes). A scripted player that knows the next step is a lower bound, not the pace: at the preview's launch it
  reached the first mix at 35 s and real players near 288 s. Timings are judged on real players' runs
  (`app/tools/play_report.py`) whenever they exist.
- **Idle time pays out mostly in the old**. Coming back after a while with a mix and orders running brings full
  stores and finished work, plus one new possibility, maybe two, as a reason to come back: never a flood of new
  cards, systems or story. The rest of what is new is gated on steps the player takes while present. Anything that
  unlocks while away is revealed one at a time after the player returns. In the opening, a content test runs a save a
  day forward with no player and asserts at most two new unlocks. One, maybe two is a guideline, not a limit: three, occasionally, in an edge case, is fine. The checks allow three in an absence the season's turn
  lands in, since the turn is on the calendar and an ask can open beside it.
- **What the hands make while away has somewhere to go from the first leave**. Day one offers a sink from the opening's end: an uncapped card in the mix that
  takes damp wood, feeding a staged comfort that its order card builds a stage at a time while the player is away,
  shown unready from the end. So a return shows what the mix built, more for a better mix and more for a day away
  than a night away. The cap-loss check still reads chapter ends only: day one's leave points are a readout.
- **A mix keeps going without a dry store** (consistency is the priority: no card may look the same
  as every other card and yet be treated differently, say because it is seasonal). A card that behaves differently must look different; no rule may single out a card for a property
  the page doesn't show. A card whose store runs
  dry hands its share to the rest of its mix until the store is built back up. That holds whether nothing can refill
  the store before the season turns or a running maker refills it; in the second case the share comes back at the
  hourly resume step, so the split changes at most hourly. The bar the player sets never changes on its own. Under a
  mix whose actual split differs from the set one, a "running now" strip pops out showing the actual split, the
  waiting card's slice greyed; it disappears once they match again.
- **One at a time counts decisions, not cards**. A choice between two cards (the stool or the fireback)
  arrives as one thing, both in view, or it stops being a choice; and a card that can be tried too early (ringing a
  spot not yet cleared) stays there, because trying it too early costs nothing and the red card answers it. Pacing spaces out systems and decisions,
  never by chaining the options of one choice or hiding what a player could try too soon.
- **The screen arrives when it means something** (2026-10-17, after a non-gamer's cold play found the first minutes
  too busy). Each part of the screen is drawn from the moment it first means something to the player, not when the
  engine first has it: a status once its cure is on screen, a ledger line once it asks something or moves, a control
  once there is something to do with it, a bar once it has something to show. A part takes no room
  until it arrives (an empty band reads as broken), except where its arrival would move what is under a finger, where
  its room is kept from the start; once drawn, a part stays. In the first five minutes at most one
  Ashfall-specific mechanic is on screen (the mix); the others follow, spaced out. The engine's timeline is not moved
  for it: what the page draws is the lever. Held by `tests/dayone/test_dayone_reveal.py`.
- **Taught by need, and needed again.** A system is introduced when the world gives you a reason to use it (the candles
  run low, so you meet the ledger line; wolves come, so you meet orders), never by a tutorial screen, as habits does.
  Not even a spotlight tour that forces the real click, as Idle Awakening has: if a point ever proves
  to need one, it is optional. The common failure of games that do this well is a system used once and never again,
  so the teaching moment is the first of a need that recurs: new unlocks, seasons and regions keep sending you
  back to mixes, orders, the map and the journal. A system with no second reason to open it is cut or folded into one
  that has.
- **A note about a mechanic appears in the same moment as the thing on screen that proves it** (after
  the dusk card told the player morning was a wait away minutes before any countdown showed it, so they wondered why
  they would wait with the camp to run). The timer, the new control or the changed number is what the note points at,
  as a lesson step on that very element, and it starts when that element first shows; a card or line that arrives
  before its proof is moved to the proof's moment, not shortened. A note whose proof never shows is cut.
- Every skill is paced to one shared target, which the simulator reports per skill (`tests/dayone/growth.py`,
  `climb_hours`): woodcutting's 900 XP an hour at a full share, under the prestige floor (`opening/prestige.py`,
  `check_phase_spans`), so how fast a skill climbs on a route is the share of the hands the player gives it, not which
  skill it is. The slow skills' methods sit below it where raising them turns an invariant red; each skill's reason,
  measured on the push routes:
  - scavenging, 360: none needed. Its track card holds about a quarter of the hands all story, so at 360 it climbs
    with woodcutting, and at 900 the typical route crosses two of its phases by game day 14;
  - foraging, 300: at 900 the typical route's day two ends losing damp wood to its cap (the cap-loss check), and its
    foraging reaches level 16 by day three's end;
  - arcana (60, 10, 300): at 900 story gates are met before the page states them (the check that every gate met was
    stated), one of them by a level find that lands the moment its own gate opens;
  - melee (the hunts 2, spar 300): its levels speed the hunt, and at 900 the hunts leave day six's end, and spar with
    the day-fifteen hunt leave day fifteen's, losing pelt to its cap (the cap-loss check);
  - cooking (stew 36, fungus_stew 18, catch_broth 300): at 900 stew leaves the babysitter with no dry wood on day five,
    the cold chip shown and no cure on offer (the week's cures check), and fungus_stew leaves days nine, eleven and
    twelve losing smoked to its cap; day fifteen's barley_stew is at 900;
  - the smoke lane's cards, 18: a lane of its own costs the hands nothing.

  So the slow skills reach the target only through content: sinks for what their levels speed up, and gates their
  finds cannot meet (issue #40).

  Late levels open a new method or place, not just a longer bar. Nothing important waits behind the slowest grind.
  (Idle Fantasy uses RuneScape's XP table, where 92 is about half of 99; Prayer is bone-burying for many hours, and its
  per-skill prestige opens only at 99.)
- Systems interlock from day one (the OSRS/Melvor skill web); nothing bolted on later. **Expansions are where it
  drifts** (Melvor, The Perfect Tower II, and now Idle Fantasy started integrated and grew disjointed systems), so a
  new system must name the existing one it extends and change the old ones in turn, or it doesn't ship.

## Prestige is per skill, and finite

A skill resets on its own for permanent bonuses; nothing else is touched, and its prestige track can be maxed
(Idle Fantasy's shape). Nothing resets the whole game: a global prestige after many hours is where
Gnorp Apologue loses players. It opens at a point the simulation reaches on the shared pacing target, not
behind the worst grind. Its timing has a flat optimum, so there is no right moment to watch for. Each skill's
prestige rewards reach the web beyond that skill, so no track is skippable for its bonus. True prestige is for your
skills only.

**Prestige is the player's click, and a week away loses nothing** (the design is issue #37). A
skill that reaches its top is never reset behind the player's back, since a skill found at level 1 after a week away
is the "won't know what's happening" return. Prestige is a click plus a choice of bonus, and it lifts the skill's
top, the way the camp's levels go: the skill's level never falls, and the player sees one level counted up across the
phases, with no phase named. The control is "Push past", since it says what the skill does and promises no reset. A skill at its top waits there for the click. Some time lost
after an absence that was simply too long is a fair hit (a week away is shorthand for that, not a number
to design to); what must not happen is a loss inside an ordinary absence, which would set a check-in
schedule. An ordinary absence is roughly a day or two: a guideline like "one, maybe two" new things per
return, which an edge case may bend a little. A prestige bonus is a node with a few ranks that the player completes
(completing a node beats a bonus that repeats without end); the finite track bounds the total. The click is only by hand, never queued (a queued click is an auto-prestige
with an extra step). XP past the top carries into the next phase for about two days and never past that phase's top,
so an ordinary absence loses nothing and a long one leaves one click waiting, never a stack. No
interruption ever stops work to keep a player from idling one skill (OSRS's random events, rejected as an offline cap
in disguise). Breadth comes from the web: a skill's later methods need what other skills make, so a one-track mix
runs into the web, and the dry-store rule moves its share on; seasons' chores and options do the rest.

**A building's prestige is its fall and rebuilding** (Legends & Lattes: rebuilding after destruction as natural
progression, not a setback). A building that has maxed out becomes eligible to be destroyed, and its fall arrives as a
story beat (a raid, a fire, something stranger); the rebuild opens its next, better form, with salvage. Failed
defences damage a building (a repair cost, a slowed building) and never destroy it, so walls and guards have a stake.
The fall stays the story's to give, or letting the walls fall would become a way to farm upgrades; a fall is never
the player's fault.

**No bonus depends on remembering to do something by hand.** It is passive, or it is something a standing order can do.
(Idle Fantasy's race gate can leave one farming prestige option, crop rotation: +5% for planting a different crop
than last time, which is easy to forget, so not worth a reset.)

## Stores, caps, the pacing curve and the forecast, as built

How these engine parts behave today, moved from their rows in `systems.md`.

Stores and caps: finite everywhere. Past a cap, production is lost on purpose; where it should go instead is sinks,
work that takes stores (trips, comforts, arrivals: Cards and Offers), sized so a day's absence loses at most half
(`docs/design/banked-time-plan.md`; engine `DESIGN.txt`, "BANKED TIME").

Pacing curve: an A/B target, the simulator running two curves side by side. One curve for every skill, its steps never
shrinking past the shipped ones; a level's pay speeds its skill's work (more made, the same XP), so time per level
grows with the curve and the loop stays tame (`app/tests/dayone/growth.py`).

Forecast: `app/ashfall_app/engine/forecast.py`, sent when the page asks (a new or opened save, an advance after its plan
changed) and kept across plain advances, so the page draws only times that come true (CONTRACT.txt, "Forecast").
