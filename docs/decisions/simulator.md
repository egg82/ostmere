# Simulator

How long the game runs, what it must hold over that length, and what a check may fail on.

## Length: about 3 months, set by play, not playtime

The base game targets about 3 months for a typical route, one that uses the tools the game teaches. Minutes spent never
change it; decisions do: a sharp route is faster (about 10 weeks), and a route that skips the tools is slower by what
it skips. No rubber-banding: an optimizer who notices it feels taxed. Simulation reports weeks to each story beat on
every route beside the beat's target day before anything ships, and the story clock's floors (a night, a season) hold
on every route by construction. The routes that write no rules (`by_hand`, `lazy`, `keeper`) are reported, never held to a floor, with one
check that they land measurably behind: what bounds neglect is that nothing blocks and nothing spirals.

**Progress freezes at the end of the main story**. Expansions take a while to make, so a player who
reaches the end isn't left banking progress that the next content would arrive already outrun by. How it freezes is
designed when the end is built.

**The back half never slows.** New things per week stay roughly flat from day 1 to the ending; late reveals may be
bigger, never further apart, and the simulation reads the last month as closely as the first week. Back-half slowdown
is what ends idle games like Cookie Clicker, A Dark Room, Orb of Creation and Idle Awakening; the other common reason
players stop, active time a career doesn't leave, is the attention rules' job.

**The opening is the bar for the whole game**: a game that kept the v2 opening's energy throughout would be fun. Every later stretch
is held to the opening's feel: something new to understand or decide on each visit, a system taught by need, the story
landing where the eyes are. The pacing simulator prints the opening's rate of new things per visit beside each later
week's, scaled to visits rather than minutes, for a person to judge.

**Always something to build toward, several at once.** At every moment a few goals of different kinds are in view
with their progress, and the player's setup decides how fast each comes, so tweaking a mix or adding a rule trades one
against another (Idle Fantasy keeps players coming back by having them build toward four at once: two skill prestiges, a
50m-gold building, gear for a boss). Days or weeks per goal is fine; every open is visibly a step
toward them. Early on, one or two goals is enough; the count grows as systems arrive. A timed arrival may stand beside
them, never instead of them: a wait nothing speeds feels like nothing you do matters. A goal shows its cost and
progress, not what it opens. Several goals make a choice, which goal to build toward first, and the choice is part of
the hook even when it is a tradeoff, since it is the player choosing what to build toward; the story
answers the order chosen with a line (funny or gut-punch), as the opening's first two builds do. Two things make the
choice: goals that share a resource, and capacity. Idle Fantasy's work queue does N things at once; here the mix
moves everything at once and the choice is its weighting (shares and rules), so a goal counts as chosen when moving the
mix changes which goal arrives first.

**Every stretch of play has a stated aim** (after players from the public share, playing cold, knew
the next step but not why, and one asked "so I just click buttons?"). One line just above the art says what the
current stretch is for, in the story's voice: a goal the player feels, never the task that gets there, and it changes
when the story moves on, so the next step reads as progress toward something. It is there from the first screen and
never empty. Each aim is content keyed to the unlock that starts it, and the next aim's start ends it;
nothing reads it from the prose. A plain objective line is genre-standard, so it is not one of the first five minutes'
Ashfall-specific mechanics ("The screen arrives when it means something"). Held by
`tests/dayone/test_dayone_aims.py` and the content check in `app/ashfall_app/opening/aims.py`.

**Unlocks mostly come from play.** A story moment on a clock may open a task, and that keeps the pace known, but
only interspersed with unlocks the player's own loops earn toward a goal they can see; lean on clocks too much and
nothing you do matters. The simulator reports per day which unlocks and build stages a better setup brings sooner and which
land at a fixed time, and flags a stretch where only fixed-time ones land.

**A level is a thing, not only a number.** Each level makes its skill's own work faster (levels speed the work, never
the levelling, so time per level never shrinks), but a plain speed-up is the floor, and it goes samey; unlocks and story
break it up. A skill goes at most two levels in a row paying
only speed; at least every third brings something named: a find, an unlock, a story moment.

This and the 3-month band hold together because they measure different things. The band bounds the story's beats; the
setup moves the goals between beats, and how much the camp has when a beat lands. A sharp setup gets each goal sooner
and arrives with more, and may lead the story's usual pace by up to a few days per week of play;
a beat held by the calendar or a night stays where it is. The simulator reports both: each beat's day beside its
target day, and at every sampled moment whether a visible goal is one a good setup reaches measurably sooner than a
poor one. Short windows where the mix doesn't change what comes next (one goal minutes away, the others nearly done)
follow from tasks, goals and choices lining up, so the count takes goals far enough out to be a choice.

**Leaving and coming back always pays.** Whenever the screen says time away brings something (a bar filling, a next
item, a timed arrival), a return after that time delivers it. One broken promise and players stop trusting the wait.
Every countdown, "full in", next-level time and next marker the page draws comes true by itself if the player changes
nothing, and a marker that would pay nothing is not drawn; the simulator checks each against a return.

**Every bad state has a cure in reach.** A chip like hungry, cold or tired only shows when the player has something
to do about it (a card they can afford, or a rule that will run it), unless the state is marked as having no cure on
purpose. The day-one tests check every sampled moment.

**A bad state costs something small and says what**. Every chip changes something while it shows, a cost the
player feels but is not punished by, and draws that cost under its word in two or three plain words ("hands slower").
A chip that costs nothing teaches players to ignore it. The cost runs exactly while the chip is drawn, so a chip whose
store crosses before its cure is on screen is unlocked with its cure rather than held back by `offered_after`; the
content check refuses a chip with effects and no cost words, cost words and no effects, or effects and an
`offered_after`.
A task on the hands runs at the speed it had when it started: a chip that shows or clears during it changes nothing
until it ends, so a task started tired shows its slower time up front, with the cure still in reach, and one started
rested is never slowed partway; a queued task waits while a rule's cure runs.
**A glowing step cuts in on the player's plan**. While the queue or a rule
holds the hands, a glowing step not yet done stays tappable and keeps its glow; the tap pauses that task where it stands,
and the queue or rule takes it up again once the step lands. A visit is often seconds long, so a step that has to wait
for free hands waits a whole absence. The queue never holds back for a step, so a player away keeps their plan running.
A glowing step never cuts into a task the player tapped by hand.
**A cure cuts in**. While a chip shows, a card that cures it takes the
hands from whatever task they run when the player taps it, unless that task is a cure too. The task keeps its work and
is taken up again once the cure lands, by the queue if no rule or entry of theirs would. A stage can run half an hour
or three hours, and a chip that showed during one had no cure in reach until it ended. A rule on the cure still waits
for the task to land, so every drawn landing comes true while the player is away; a player present can cure sooner
than their rule, a small edge for attention (engine `DESIGN.txt`, "CURE CUT-IN", known gap). Shorter stages (more taps,
and moved story counts) and builds off the hands (building no longer costs the player's time) were the alternatives.

**A card that shows every need met does the thing**. A card is not shown until the story beats it waits on
have happened, so every require it has is one its needs list can show; a content check refuses any other, and the
day-one tests check at every sampled moment that a card with every shown need met and a free lane starts for real.

## Tuned means checked

A check fails only on an invariant (rhythm comes from the design, not from knobs): a softlock, a
runaway spiral, a player who uses the taught tools being forced to babysit, or a number the page shows that doesn't
come true. Everything else about the rhythm of play is taste, which the simulator prints and never judges
(`docs/design/sim-invariants.md`). In three parts:
- **Pace:** the 2 AM test and its instruments hold on the players who use the tools (typical, whenever, sharp and the
  other schedules), and a player who skips the tools lands behind them. The rhythm (new things and decisions per visit,
  effort between bigger things, what an absence opens, when each beat lands, each calendar day's arrivals, the
  human-paced model's dead gaps) is a readout whose committed text CI compares and reports, never
  failing on it. No band or target is set for it. The last month is read as closely as the first week (above).
  A visit in the human-paced model ends once nothing is left to act on and nothing of the player's lands within the dead
  gap, so a long job started in a visit is not idle time. The readout marks the visit that reaches
  the edge of written content and each return during a long wait the player chose.
- **Shape:** every figure comes from the rules, never from text, and rounds the way its kind does: amounts down, costs
  up, durations up, rates toward zero (`CONTRACT.txt`, "Text and numbers").
- **Display:** a figure shows the fewest digits that tell it apart (a rate of 2 reads `2/min`, never `2.00/min`, and a
  rate that is not zero never reads as zero); a store's name is capitalised where it leads a row and lowercase inside
  a sentence; one formatter (`game/format.ts`) and one label lookup (`game/catalog.ts`) produce them, each with a client test.

**The UI speaks plainly, in numbers; the story keeps its voice**: story voice in the UI reads strangely, even in this
style of game. UI text is the `ui.*` entries and
every non-story string that says what the game does: level pays, camp levels, upsides, chip costs, rates, costs, buttons,
the ledger, the rule editor. It is matter-of-fact, the general style of an idle-game UI, and gives an amount or effect as
a number ("+10% woodcutting speed", "holds 18, was 12"), never as a word ("a tenth faster", "half again", "twice").
Not every line leads with a number, and names (skills, stores, cards) stay as they are. Flavour words in a UI string go
too. Story lines, card lines and aims keep their voice, and phrasing like "half" belongs there. The number is a slot fed
by a served value (`CONTRACT.txt`, `{pct}`), so it is stated once.

## The simulator, as built

How it stands today, moved from its row in `systems.md`. The queue item is `docs/open-work.md`, "Pacing simulator past
the opening"; it names beats by number only.

It fails only on an invariant (softlock, spiral, a tool user forced to babysit, a shown number not coming true;
`docs/design/sim-invariants.md`): the 2 AM test as a replay, the lag bound on tool users
(`app/tests/dayone/routes.py`, `TOOL_USERS`), drawn times coming true, cap loss on typical, and players who skip the
tools landing behind (`app/tests/dayone/human_flags.py`, `lands_behind`). The rhythm (per-visit and per-absence
counters, beats beside their target days, calendar days, the human-paced model, each skill's ladder, what a re-mix is
worth) is printed by each package's `report.py` and committed under `app/tests/readouts/`;
`app/tests/readout_snapshot.py` reports a readout whose text changed, and
`python -m tests.readout_snapshot --write` commits every package's at once. Week two plays on from week one's plays at
G2 (`app/tests/weektwo/routes.py`), its decide counter refusing a queued stage (`app/tests/weektwo/counters.py`).
Production lost to caps per store over a route and an absence: `app/tests/dayone/caploss.py`.
