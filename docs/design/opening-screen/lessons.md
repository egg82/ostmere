## Lessons

A system is taught on its real controls the moment it first matters, and only then: the mix at the first-mix offer,
rules at the first rule offer, a second mix at the first card tapped by hand again and again, the cap rule at the first full store, adding a maker at the first dry store (these are all the page walks; no offer builds a mix or a rule), never two at once and the mix first (a rule switches the hands to a task or a mix, so
it is taught in terms of the mix). While a lesson may start, its offer's button reads `Show me`; tapping it
opens the real editor and the lesson walks it, one step at a time: the control to touch next takes the glow, with one
short line in a small note beside it (under it; else on its left or right; else above it; never over a sibling of the control, the card it sits in (above or below that card then), the panel's tabs or the next step's control when it is already on show. Orchestrator, 2026-10-24), fixed to the viewport
so nothing in the layout moves; its box, padding and border included, never passes 16px from the window's edge, at any width or text size. A step can name more the note keeps off (`clear`: the cap rule's
`reaches` keeps the When and Until rows in view). A step whose control (or what it keeps clear) is out of sight when it starts (off the window, under the pinned scene
and hands strip on a phone, past a scrolling sheet's edge) scrolls it to the middle of what is left, once, at once
under reduced motion. A step ends when its control is touched, or, for a line to read, when the player taps the note (it
shows a `Got it`, and the whole note takes the tap), never on a timer, since a player may look away for a while; a step whose control is not on show waits, and no step is skipped because a later control is also in view. A
read step never holds a tap back: a tap on a later step's control, with only read steps between, ends them all.
`Skip` sits in the note at every step. Done or skipped, a lesson is kept in the save and never returns in it, and its
offer is today's one tap again. Nothing is modal: every control stays live under the note. A step can name a lesson
it repeats (`unlessDone` in `game/lessons.ts`): it is left out for a player who finished that lesson rather than
skipped it, so the rule's lesson drops its Rules-tab step after a finished mix lesson.

One lesson at a time holds for the offers too: while one runs, another lesson's guided offer (a rule offer's or the
mix offer's `Show me`) waits off screen and comes back when it ends, so a `Show me` always opens its editor with its
lesson. Two rule offers never show as twins: while the rule's lesson runs on one, another rule offer that would read
`Show me` waits off screen until that one is answered. Once the lesson ends (done or skipped) it comes back as its one
tap; if the first offer goes without a rule (its line turned white), the waiting one is the `Show me` and the lesson
starts on it. And a lesson the player has left never holds the next one back for good: once nothing of it has been on show
for 30 seconds (its trigger gone, and neither the control of the step it last finished nor its next step's: the editor
closed, or the Rules tab left before a rule came on), it is abandoned: nothing is kept, so it starts over the next time it may.
Only `Skip` and finishing keep a lesson. A player still on the Rules row
waits for the hand-back as long as the rule takes.

| Lesson | Starts | Steps (the control, then its line) |
|---|---|---|
| The mix | the first-mix offer is on show and no mix exists | `Show me`: `A mix works two tasks at once, with no tapping.` · the first card in the editor's Add row: `Tap {card} to add it.` · the second: `Now {card}.` · the bar (read): `The bar splits your time between them. Drag the line to change the split.` · `Save`: `Save, and the mix starts.` · the strip's mix row (read): `The mix keeps going while you're away. Tapping a card pauses it.` |
| The first rule | a rule offer (a ledger line's or the strip's) is on show, no rule exists, and the mix's lesson is kept or a mix exists | `Show me` (opens a new rule): `A rule switches your hands to a task when something happens, then back to your mix.` (a hands task) or `A rule starts a task when something happens. Your mix keeps going.` (a side lane's) · the offer's task on `Do`: `Pick {task}: what the rule does.` · its store or chip on `When`: `Pick {when}: what it waits for.` · `Add rule`: `Add it to your rules.` · the rule's row in the Rules tab (read): `Your rules live here. This one runs by itself.` (left out after a finished mix lesson) · the strip's `until …`/`while …`, or the rule's row while it is on (read): `Your rule is on: {task}. When it lets go, your mix comes back.` |
| The second mix | a card the player keeps tapping by hand that their running mix could take (the card hint's detection, `game/hints.ts` `secondMixCard`), once the first rule's lesson is kept and a new mix can be saved; the card is the trigger. A dot already touched still counts. No `Show me`: nothing is opened or filled in | the card (read): `You keep tapping {card} by hand. A second mix could run it for you.` · the strip's Mixes: `Open your mixes.` · the list's `New mix`: `Start a new mix.` · the whole Add row, since the tasks are the player's pick: `Tap the tasks you want in it.` · the bar (read): `Add as many as you like, then drag the lines on the bar to split your time.` · the name (read): `Give it a name.` · `Save`: `Save it. Your first mix keeps running until you switch.` · the strip's Mixes (read): `To switch, open your mixes and tap Run on the one you want.` |
| The cap rule | a store the hands make is full while another hands task could take the time, no rule watches it reach a level, a rule can still be added, the save has no rule watching any store reach a level, and a rule of the save has come on and let go (`game/caphint.ts`); its line carries the quiet dot and is the trigger. No `Show me`: nothing is opened for the player, and the new rule starts empty | the full line (read): `{store} is full. What your hands make past the top is lost.` · the Rules tab: `A rule can switch your hands to something else when it fills. Open Rules.` · `+ New rule`: `Start a new rule.` · `More options`: `More options lists every store.` · the store on `When`: `Pick {store}: what it waits for.` · the levels' fold: `Set when the rule comes on and when it lets go.` · `reaches`: `Pick reaches. The rule comes on once {store} is full.` · the whole `Do` row, since what the hands do instead is the player's pick: `Pick what your hands do instead.` · `Add rule`: `Add it to your rules.` |
| The dry store | a card of the running mix is stopped on a dry store a card in play could refill (`game/dryhint.ts`), once the first rule's lesson is kept or a hands rule exists, and no saved mix already holds a card with a maker of one of its needs; its line carries the quiet dot and is the trigger. No `Show me`: the mix is the player's own, and only they add to it | the dry line (read): `{store} ran dry, so {card} stopped. Nothing in this mix makes more.` · the strip's `Edit`: `{task} makes {store}. Open Edit to add it to this mix.` · its add button: `Tap + {task} to add it.` · `Save`: `Save. While {card} waits, its time goes to the rest of the mix, and {task} makes more {store}.` · the strip's mix row (read): `A rule can also switch to another mix when something runs dry.` |
| A side-holder | a fight of a side is served (`combat` on), a card in play holds that side while it runs (`CardInfo.kept`), a card in play makes the fight, and no saved mix holds both (`game/sidelesson.ts` `sideCue`), once a mix is saved and a new one can be. The holder's face is the trigger. No `Show me`: the lesson points, and the player makes the mix with what the mix lesson taught | the holder's face (read): `{card} adds to your strength while it runs. A mix runs it beside {task}, so both work at once.` · the strip's Mixes (touch): `Put both in one mix and they run together, {card} paying at its share of your time.` The face words a held figure at the card's share of the mix (`Card.share_bp`), the full figure while it has none |
| A stopped mix | the first running mix to grey over a done card; its `Edit` is the trigger, and the mix has another card left to run or the content names a card that takes the done one's place (`replaced_by` on the retired unlock, in play and not yet in the mix). No `Show me`: the editor is the player's own | `Edit`: `{card} is done, so this mix stopped.` then `Open Edit.`, or `{card} is done, so this mix stopped. {task} takes its place. Open Edit.` with a replacement · with one, its add button: `Tap + {task} to add it.` · the editor's ✕ on the done card: `Tap ✕ to take {card} out.` · `Save`: `Save, and the mix runs again.` |
| Switching mixes | after the end, a hands build waits on a store nothing at work makes, and a saved mix that is neither the running one nor the player's own makes it, or else the running mix could take a card in play that does (`game/teach.ts` `switchCue`); the strip's `Mixes ▾` (the mix's name, with a mix running), or `Edit` in the second case, is the trigger. No `Show me`: it points at the player's own controls | `Mixes ▾`: `{build} needs {store}. Your {mix} mix makes it. Open Mixes.` · that mix's `Run` in the list: `Tap {mix} to run it.` — or, when only the running mix could take the card, `Edit`: `{build} needs {store}. {task} makes it. Open Edit to add it to this mix.` · its add button: `Tap + {task} to add it.` · `Save`: `Save, and the mix makes {store}.` |
| The clock | the night's countdown (the foot of a card waiting on a store the player was never shown) is on show, a few minutes into the night | the countdown (read): `A real-time wait: morning comes when it runs out. The camp keeps going meanwhile.` |
| The journal | the journal is in the Book and no other lesson runs; no `Show me`, since Book is its own control | Book's tab: `What you learn gets written in here.` · the Journal's button in the Book: `A dot here means a new note.` |
| The journal's numbers | the journal's lesson is kept and a page that shows numbers is open | the page's numbers (read): `Exact numbers once you've fought it. Unknown until then.` |

**Lessons are kept per save** (a game started over teaches as a first one does): the record is the
save's (SavePresentation: `lessons`, `lesson_ends`, `rule_seen`,
`mix_offered`, everything that gates a lesson or a lesson's hint), so every new game teaches everything again from
each lesson's own moment, whatever another game of the account kept. **The order a new game meets the build lessons
in:** the mix, then the first rule (it waits on a kept mix lesson or a mix), then the second mix and the cap rule,
whichever moment comes first (each waits on the first rule: the second mix on its lesson being kept, the cap rule on a
rule of this game having come on and let go). The clock, the journal and the town come with the story, between them.
A game kept nothing about its teaching before then, so it starts with none kept; each lesson's own condition keeps a
game past it from being taught it again: no mix (the mix's), no hands rule (the first rule's), the first rule's lesson
kept (the second mix's), no rule watching any store reach a level (the cap rule's), no saved mix holding a card and a maker of its needs (the dry
store's), no skill pushed past (Push past's),
and for the story's three, what the game carries of the moment: no night beyond the first begun (the clock's), no
second journal page written (the journal's), the town's mix still each person's whole time on one card as the game made
it (the town's) (`test/persave.test.ts`).

**Lessons on or off.** The Games sheet holds the account's setting as a checkbox under the front-page one: `Skip
lessons in every game`, unticked on a new account (AccountSettings.lessons). Ticked, no lesson starts in any game of the
account and no hint that only a lesson gives shows (the full line's cap dot, the card a second mix's lesson starts
from); every guided offer is today's one tap, and the ordinary dots no longer wait on a lesson that will not run. A
lesson under way when it is ticked ends unkept. Unticked again, each game's lessons go on from what it keeps.

The journal's lesson's second step is inside the Book: on a phone, inside its sheet, where the note is drawn in the
sheet's own layer, so the modal sheet never covers it. The numbers are a lesson of their own, so a page with none (a
days page) never leaves a step waiting: the journal's lesson ends at the Journal's button, and the numbers' starts the
first time a page with numbers is open (at once, when the Journal opened on one).

The journal can join the Book just before a guided rule offer (the book and the ledger open at the same beat). The
journal's lesson yields: until Book is tapped it holds no offer back, and gives way to the rule's lesson when
that one's `Show me` is on show (the journal's comes back after).

The editor asks what a rule does before what it waits for, so the rule's lesson does too. A rule built this way takes
the editor's default levels for its store, not the offer's. The lesson's rule flies to the Rules tab and,
unless that tab is open, leaves a quiet dot on its label until the tab is next touched.

A player who put rest in their own mix is never tired, so never meets the strip's rest entry, and that costs no lesson:
looked at, and fine. On every scripted route the ledger's dry-wood offer shows about two minutes after the first mix,
before any rule and minutes before the end, so the rule's lesson starts there (`tests/opening/test_first_rule_offer.py`
holds it); the rest entry is the rule lesson's second door, for a player who rests by hand. Further mixes and rules are the player's to write; a quiet dot marks the card, chip or line one could answer.

Fits into: the offers it replaces for one first time (the first-mix offer, `ui/chipoffer.ts`, the ledger's inline
entry), the one glow (`ui/fresh.ts`) as its highlight, and the save's presentation (`Keeps`) as its record. A
lesson is data in `game/lessons.ts` (an id, when it may start, its trigger, its steps); the runner is `ui/lessons.ts`.
The mix tutorials end with these: building a mix, changing one and finding the list, and the rule
lesson's hand-back to the mix. A second mix gets its own lesson; after that and the cap rule's, further mixes and the default mix are the player's to make,
with the quiet dot as the only hint. A later system gets its own lesson, one entry there plus the
guided button on its trigger.

How each lesson ended is recorded too, so a round of testers shows which step a skip clusters on: the lesson, done or
skipped, the index of the step it ended on, and the longest wait on one step in seconds. The index counts in the
lesson's full list, left-out steps included, so a thinned run and a full one are comparable. Fits into: the save's
presentation, which already carries the lesson's end (`lesson_ends` beside `lessons`), written by the `Keeps` that
keeps it and logged by the server as one `lesson.end` line with the save's id (Logs, job runs, retention). Not the decision log: its rows
are engine decisions a save is replayed from, and a lesson is not game state.

