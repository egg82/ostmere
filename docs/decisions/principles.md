# Principles

Product-wide decisions: the words used, attention, progress on screen, choices, and what is never built.

## Words used here

- **Card:** one kind of work the player can do, shown with its bar and what it makes and takes; tapped or mixed alike
  (`docs/design/opening-screen/asks-and-cards.md`, "Cards"; below, "The mix").
- **Mix:** several cards run at once, each with a share of the hands' time (below, "The mix").
- **Hands strip:** the one row showing what the hands are doing, the mix's slim view
  (`docs/design/opening-screen/hands-strip.md`, "The hands strip").
- **Ledger:** the lines of per-hour rates for each store, with when it empties or fills; a falling line no rule covers
  is red (`docs/design/opening-screen/ledger-and-fights.md`, "Ledger and rules").
- **Rule / standing order:** a "when X, do Y" line that runs a mix while its condition holds; the docs call it a
  standing order here and in `docs/systems.md`, and a rule in the Rules tab (below, "The mix").
- **Camp bar:** the bar of the camp's level, filled by work done, with a next marker stating what the next level
  pays (`docs/design/opening-screen/attention.md`, "One column of attention").
- **Unwrap:** what happened since the last visit, shown in order on opening the app (`docs/systems.md`,
  "Chronicle and unwrap").

## Fun, but never vying for attention

The optimal way to play is whenever you feel like it. Attention earns no efficiency, so an optimizer has nothing to
chase on the clock.

**The 2 AM test, held by the simulation:** a babysitter who acts the moment every timer ends must end no further
ahead than a player who opens it at random times of their own choosing, given the same setup: the rules and mixes
the game has taught. Any gap is a bug. It guarantees that a player who uses the tools never needs to babysit; it does
not stop a player who skips them, or prefers tapping by hand, from doing so. Not knowing a tool is a teaching
problem (the lessons and hints answer it), and not wanting one is the player's choice, never something the game
removes by deciding for them. (What Idle Fantasy's players would most happily lose: 20+ push notifications a day,
feeling they must babysit it, staying up at 2 AM for a timer to set up the next task efficiently.)
- **No offline cap, full rate.** Time away earns exactly what time present earns. Any cap, bank limit or decay sets
  an optimal check-in schedule, and an optimizer will follow it.
- **Covering an absence is never an upgrade.** It is complete from day one. (Idle Fantasy grows queue length with
  progress, so early on a 3-hour queue pulls you back hourly.) Nor is automation held back as a reward: the player
  sets things up as needed, rather than sitting and waiting for an unlock condition. Every rule condition and kind is available once the thing it watches exists in the game (once
  tiredness exists, "when tired" can be written), and one about something the story introduces arrives with it.
- **Routine spends can be automated**, so compounding never rewards checking sooner. The queue's `When ready` and the
  player's rules make them once the player sets them up. The game makes no spend for the player: a spend happens when
  the player taps, queues or rules it, or picks an answer that names it.
- **No daily resets** (daily touches, daily hires, login rewards).
- **Nothing has to finish into idleness.** A finished task hands its share to the rest of the player's mix, and the
  queue and the player's rules take over from there, so a player who has set them up never comes back to idle hands.
  The game picks no next task: with nothing set, the hands wait and the strip says so. The one task the game sets is
  an arrival's first, since no rule could name a person before they came; it is an ordinary rule the player can change.
  A finished thing joins the unwrap. Idle Fantasy is the phone's top notifier because a worker holds one session and a
  crop waits when ripe.
- **No notifications unless the player asks.** Nothing ever waits on you, so there is nothing to tell, and nothing is
  on until the player turns it on. Three opt-ins may exist. A **reminder to play** after an absence the player picks,
  so the game never begs or bothers players who don't want it: one notification per absence,
  none after it until the player returns, an invitation that names no loss, no countdown and nothing from a save. One
  early mention points at the setting, shown once whether or not it is taken (`design/reminders.md`). A **hands-free
  notice**, for a player steering by hand: one notification when a long task the player gave the hands is done
  and nothing they planned follows (owner, 2026-11-16), never mentioned or offered, only found in Settings. And a
  digest of story moments. Never a daily one, a badge, or any other message that something is waiting.
- **Make what is already there tappable before adding words.** A way to reach more (a breakdown, the total a bonus
  feeds, what a job does) is the existing figure or line made tappable and marked tappable the way the screen's
  other tappable words are, not a new line or label beside it. Something new goes on screen only when nothing
  already there can carry it. The owner's rule, from play: subtractive over additive, so the screen does not fill up.
- **Shown in the design, not claimed** (a cold tester joked about waiting for notifications to log back in and gather rewards). The calm has to be visible in the visual language, so a stranger reads it without being
  told: no badges, counters or "!" calling for attention; no shop-shaped elements (gem icons, gold "claim" buttons,
  timers to skip); nothing pulses for urgency; a new control (a task card, a mix-editor Add entry) carries a small quiet
  dot until the player interacts with it or puts it to work, and a dot once cleared stays cleared, across views and reloads (and the tabs' Book, while a line it holds left the story strip
  unread; Town, while a person or lane it holds arrived unseen), never plain text (not merely when it is seen; a dot on everything new, plain text included, was the
  defect), never a glow (a glow says click me now, a dot says this is one of the new things); a glow has its own
  job: pointing at the one obvious next step when there truly is just one (the very first card; a first-of-its-kind
  moment), one at a time, gone once the card is used by any route (a tap, a mix, a rule, the queue) and kept gone across a reload; a red line is information with its answer beside it, never an alarm that nags; time away is
  shown as what got done, never as what was missed. A line up front saying so is fine, but the screen has to prove it.
- **The opening's end is a moment, and the card that follows it is a feature card, not a screen.** The end's lines land
  in the story like any other and play goes on. The real-time wait is taught by a lesson (the clock's) at the moment its
  countdown first shows, a few minutes into the night: it points at the countdown and says, in plain words and out of
  the fiction, that this is a wait in real time and the camp runs on meanwhile. Nothing covers the scene, and the
  lesson is kept once, skippable; its line is UI voice ("The UI speaks plainly, in numbers", below), and its note never covers the card the countdown is on. The edge of the written content has one end card (`end_card` in `opening.toml`), which the loader puts on the last shipped chapter's `end_feature`. The dusk card
  that said this at the end, minutes before any countdown, is retired: the player had nothing on screen to tie it to.
  Why: a reviewer took the wait after dusk for the end of the game and left
  (`docs/research/design/galaxy-review.md`).
- **The quiet stretch before the end shows the light going** (2026-10-18, after a cold tester left 13 s into it, 25 s
  before the end). The last step's lines keep the evening to themselves, since end lines that follow at once read as
  rushed; but the stretch is never a still screen: the scene moves into its dusk grade over the evening, so a player
  sees something coming and the end lands in light already going. Not taken: shortening it, since she left
  inside any stretch that still gives those lines their reading time.
- **Optimization is the route, not the clock.** You plan ahead (a queue, standing orders), and skill shows as real days
  to each story beat, not as minutes of attention. A story twist the plan couldn't foresee pauses only its own branch.

## Cascades are the peak

The best moment is a good build setting off a chain reaction inside the system: rare, earned, deterministic from the
build (Nodebuster: "chef's kiss"; Orb of Creation's spell combos). Design for systems that can feed each other in
bursts, and let an optimizer chase them. The emblem: chain lightning done well, one cast jumping from target to target.
Replaying the identical game wore out in an hour (Nodebuster), so a replay here is never identical.

## Progress is stated, never hinted

**Where progress is, and what reaching it means, is always on screen in plain words**: the player needs a clear sign
of where progress is and what it means, and can work out the route on their own. Story may hint; a gate on progress may not hide. Any condition that unlocks something (the opening's
end, a find at a skill level, a held camp level) shows as a goal the player can read before they meet it, and says
what meeting it means, never naming a find it brings (a card needing one shows the find's gate in its place until it
is met); the route to it stays the player's to work out. A gate the player can only meet by accident is a
defect. **The next step is always on screen, with how far along it is** (no player left wondering for hours or
days when the next bit of story comes, while a store sits half empty): whatever the next beat waits on (a
store's amount, a level, a count) shows as the goal with its current value, so a store that holds the story up reads
as what is next, not as a store like any other. A wait on a card fight's lost tally shows on the wait line as the
fight's card and the count so far, and the card carries the story mark; the tally is never drawn as a store. A wait on the clock alone shows its countdown. A wait on a store the content marks `stated` shows its count beside the countdown on the wait line. A card shows every
requirement that can refuse its tap before the tap: a store as have/need, a level or a step as its row, a night or
other part of the day as when it opens ("Opens after dark"), any other clock as its countdown; a card the content
can show with a requirement its face cannot draw fails the build (`app/tests/rules/cards/test_requires_shown.py`, whose
held list only shrinks). The same holds for rules: a subject the player can see is one a rule can watch, in a form
that works for it (a task that repeats by its running, not by a count it soon passes for good).
**Progress uses mechanics native to the genre and fits the game's type and story**: a milestone is a build,
a level or a count, never a state of the screen; the opening's end is its last steps done, not every ledger line white,
since getting by is good enough in this story.

## Every option offered works as worded

**The game never sets the player up to fail with a choice it offers** (owner, 2026-11-17: "we don't want to set players
up for failure with poor wording or duplicate cards or choices"). Every option in a picker, editor or list:

- does what its words say, in the situation it is offered in: no rule that reads as waiting for an end the task never
  reaches, no choice that can never come true or is already true for good;
- appears once: the same card, task or choice is not offered twice in one list, under two names or two headings;
- is found where the player looks: a list long enough to scan is ordered the way the rest of the game orders it
  (by section under its heading, by name inside each).

An option that fails one of these is left out, or reworded until it holds; leaving it in with a caveat beside it is
not a fix.

## Tools early, choices kept

**Quality-of-life tools and near-perfect information arrive with the thing they serve** (owner, 2026-11-24): in a
months-long story-driven idle game the player expects them almost at once, so a rule, queue option or info row is
never held back until the chore was done by hand; that reads as a chore, not a reward. The fun is guarded by
keeping the decision with the player, never by delaying the tool: a rule the player writes is their decision, the
game picking for them is not, so automation never chooses or switches on its own. Anything locked anyway ships with
a lead-in (a hint or a lesson) at the moment it opens, or the player misses it.

## No blind permanent choices

**No option is perfect; every choice is a tradeoff**, down to which of two small things you build
first: each has a consequence and a cost. For minor choices the card names only the upside (what it
takes to make is always shown, as on every card: the hidden part is the tradeoff, never the price) and lets the player
work out the cost themselves ("oh, right, that makes sense"); afterwards the facts show it, never a verdict: the other
option's card shows its time as it now stands, and the ledger's numbers show what the order did. Weighty choices still
show their weight up front (below).

**A one-off never stands against a lasting bonus.** A mix refills any store, so items now lose to a percentage
forever every time (owner: "even if my stores ran dry I can probably just adjust a mix and get it back. Why trade a
permanent bonus for a one-off?"). Lasting goes against lasting: a rate on one store against a rate on another, a
person's time, or a door the other answer opens. A one-off answer appears only where no answer lasts. **An answer that changes a percentage shows the one it changes**, as now → after ("Stew
+15% → +20%"), so the player can see what they are adding to or giving up.

**Every answer keeps a consequence** (owner, 2026-11-25: answering an arrival offer yourself changed nothing).
Each answer to an offer leaves something the player can see and come back to: a lasting number (a modifier whose
source names the answer), a door (a card, line set or feature that a later gate, trigger or line actually reads), or
a count that a pattern of answers reads. Answers of one role are counted, so a habit is a fact too ("they expected
you to do it and had the tools ready"); a rule's answers count as the player's own, and the game never answers for
them. Good, bad, mixed and conditional are all allowed; no effect is not, and a decline gets a small named echo. The
consequence lands a little later, a few game hours to a day, as a line that refers back and a number that moves: a
consequence the player can't trace to its choice is wasted (the Witcher 3's Baron turns on an unmarked earlier
choice that players found only on a wiki).

**A promise is broken only by a choice, never by a clock** (owner, 2026-11-25: "it's expected and normal to come
back to this after a night or even a couple days"). A promise is a thing the player can see from the moment it is
made, named in the journal and still open there, as Ironsworn writes a vow down. It is tested by a later offer or
beat that sets it against something else the player values (food, a person, another promise), and the player picks
what to give up; "no good option" is allowed, as in the Witcher's quests. Breaking it is a legal choice whose price
is shown and is higher than declining would have been. The dilemma waits for the player and resolves while they are
there. How a dilemma reads a promise: the offer names it in `tests`, its answers that give it up name it in `breaks`
and retire the card it queued, and it is shown while that card runs, so the player is there for it. Both answers carry
a sourced modifier, so the price of each is on screen.

**The game doesn't pull its punches, and never cheats** (owner: "not pull our punches. If there's no reason to").
The reaction to aim for, in the owner's words: "oh, fuck, damnit, now what?" rather than "well that doesn't seem
fair" (2026-11-25). A choice can cost a life, never a notable's, and the player lives with the bed they made, as in
Frostpunk. What keeps it fair: the bind follows from what the player chose; the dilemma shows what each option costs,
and every option is one a player could defend taking ("there cannot be an optimal play-through", The Walking Dead);
when a choice's fit decides who lives (who goes on a dangerous job), the fit is shown, since the deaths players call
unfair in Mass Effect 2 came from a fit it never signalled; and a loss is warned before it lands, with time to act
while the player is there (Banished's starvation spirals, with no warning, are the counter-example). Stakes up to a
life come only from such a choice, never from time away (`people.md`: nobody dies from inattention).

**A dilemma left unanswered is allowed and is not a third, free option**: it holds back only its own thread, as any
unmade progress does, and the people waiting on it are shown waiting; nothing else stalls and nothing decays while
it waits.

A choice whose weight can't be seen when it is made is free to change later, or every option stays viable. (Idle Fantasy
let players pick a race when race was cosmetic; an update gave races weight in a combat-led game, and the elf lost out.)

## Built on habits

The living world comes from habits' modules when the town's content needs it (issue #28). The app
shell and accounts were built here instead, once the account became the browser. The engine and the pacing simulator are new code with nothing to take from habits, so they
start now.

## Never

- Real money, or any mechanic shaped by a store even without one: skippable timers, premium currency, ad boosts,
  sellable cap extensions, progress helpers.
- Physics-heavy generic 3D.
- Card mechanics or card framing (decks, draws, piles); a system named religion. A standing aversion, no reason needed.
  Faith itself belongs in the world (people need it to survive, as worldbuilding and in townsfolk's lives); it is
  never a currency or mechanic.
- In the story:
  - sexual violence, on screen or as a plot device: the world is brutal without it, and friends play;
  - the young (a child, a baby, a puppy) harmed or dying on screen. Such a loss may happen off screen or in the past,
    very rarely and to be sad, never for shock (a dead child's toy is the register); for Claude-written lines, how
    often is decided in code. Children do live in the town (a camp of adults only reads as an
    escape hatch). They are never workers and never a cost or a fight outcome. Like companions and notables, they may
    be in danger and escape narrowly, but the text never signals early that the escape is coming. Narrow escapes are
    rare across the whole game, counting children, companions and notables together, because a pattern of them kills
    the thrill. Canon records each one used;
  - cruelty to animals on screen, firmly if not absolutely. Hunting a deer or skinning a wolf is a way of life, told
    plainly; fights with beasts resolve without dwelling on how; companion animals never die, though like notables
    they may survive by the skin of their teeth; the
    broken world's wrong or made creatures sit on the monster side of the line;
  - "none of it mattered" twists (a dream, a loop, a simulation, all predetermined): they erase every choice, and the
    theme is significance earned by choice;
  - a karma meter deciding the ending: judging by numbers is still judging;
  - a true ending only on a second run: one run sees the real ending, and replays vary rather than gate;
  - a notable betraying you: it takes heavy investment by another door; betrayal stays on the light tier.

## Open

- Art, still to test before building on it: movement, a daylight grade, eerie tiles, monsters. Packs to buy if
  those fall short (research 2026-10-11): Ruined Dungeons ($5, finalbossblues), Inside the Monster's Belly ($5,
  eldritch), Lich Crusades (Patreon-only, dark characters).
- Names: the app is **The Breaking of Ostmere** (short form Ostmere; `ostmere.yggdrasil.pub`). Ashfall was
  the name until 2026-10-21 (chosen 2026-10-11 over Afterlight as grimmer; galaxy.click's reviewer read it as a stock
  title). The repo, package and cluster still say ashfall. No subtitle
  by default; "Somebody Has To" was dropped as not grimy. The world's name is in `content/`.
- Tower defense for the town's walls: candidate, not decided.

## Why the engine's contract reads as it does

The reasons behind the rules in `systems.md`, "The engine", moved out so the contract scans.

- Event to event: an hour away and an hour watched take the same steps.
- A tap is a decision, and a tap bonus linear in time since the last tap makes tapping often and tapping once come out
  the same.
- Every verb has an order: anything the player can do (switch a mix, tap a card, pick the next building, send an
  expedition, buy, accept an offer of a kind) can be queued or written as a standing order. Prestige's carry window
  means clicking at 03:00 gains nothing on clicking at breakfast. This is what holds the 2 AM test; the engine only
  guarantees that looking changes nothing.
- Solvable conditions with hysteresis mean two orders can't flip each other forever.
- Chance never touching the engine keeps "a prepared town fares the same whatever the timing" true, and the odds shown
  exact.
- A what-if fork keeps unknown unknown and never spoils a beat. The editors' goal rows read rates as set because most
  goals lie past what a bounded fork reaches.
- Claude's output (a soul, a quest's text) is replayed from the log, so nothing Claude writes changes a number.
- The client samples as habits' page samples a served day.
