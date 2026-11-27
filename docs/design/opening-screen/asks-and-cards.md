## Asks

Every open offer (someone asks) lives in one list under the hands strip (`ui/asks.ts`), headed `ASKS`, and it takes
no room while nothing is open. The first open offer in content order is drawn in a slot of fixed height that the ask
fills, so when a season or a busy day brings several, nothing under it moves: the rest are only counted, as `2 more`,
which opens every open ask in a sheet. On a phone the slot is one row and opens that sheet ("Phone"). The chronicle's
waiting row points here: with one waiting on a wider screen it brings the ask into view and focuses its first answer;
with several, or on a phone, it opens the sheet.

An ask (`ui/asknode.ts`) reads top to bottom: who asks, a face (initial, ringed in the lane's hue) and name per person;
the question in the story's size; `↳` and what led to it, worded as a chronicle line's cause (an earlier answer by its
label); one button per answer (44 px) with its label, its cost text (`takes 12m 30s` from takes_s; an effect such as
`+10% rest` for an answer that installs a modifier), and each figure the answer moves, `Dead wood -2/min → -1.8/min`,
`Rest 5 s → 4 s`, read off a dry run of that answer (`ui/askruns.ts`), never computed by the page. Last, the offer's own
words for what differs from the usual: what waiting costs, when it goes, what the answer settles for good. Each piece
the content leaves out is not drawn, so a bare offer is its question and its buttons. No `Dismiss`: it stays until
answered.

The shown ask is the one ember outline on screen, on a warm ground; in the sheet the asks sit on hairlines. On arrival
it takes the glow (shown as its own outline), so a lesson's step keeps or takes the glow first and the ask waits. It
arrives through the arrival queue after the last of its own lines in that step, or at once when that step holds none
of them; one that joins behind the shown ask only moves the count. An offer answered while the page was shut (a rule
may answer it) is never drawn; an answer the server refuses because it was answered since redraws the save as it is.
Not a guided offer: no lesson starts on it. Rejected: one row per open ask (the scale check's first break: a season's
several asks pushed the cards off a phone); a pager stepping through asks in the slot (hides the count's meaning and
adds a control); a fixed "waiting costs nothing · never expires · permanent" line on every ask (only what differs gets
words, `design/redesign.md`, "Words"). Fits into: Offers (`systems.md`), the arrival queue, the session's dry run.

## Cards

```
┌─────────────────────────────┐      ┌─────────────────────────────┐
│ Scavenge                    │      │ Ring the spot      (muted)  │
│ stones +1 · Scavenging 2 ▸? │      │ stones 2/6 · Scavenge       │  short number marked, names its maker
│ ▓▓▓▓▓▓▓▓░░░░░░  4s          │      │ ░░░░░░░░░░░░░░░             │
│ in mix 50%                  │      │                             │
└─────────────────────────────┘      └─────────────────────────────┘
```

- **Anatomy:** title; what one completion makes and takes, as have/need (`stones 2/6`); the one bar, on the card,
  filled by a tap or by the mix share alike; the card's share when it is in the mix; a cap shown as `1/3` on capped
  cards. Cards carry no mix control: a card joins a mix from the editor's Add row, the strip's first `Both` offer, or the strip's mix offer, which leads to the Add row.
- **Unready looks unready:** muted, the missing need in the card's quiet tone with only the number it is short of
  marked (red is the ledger's alarm, never a need), never glowing. An input a find brings shows the find's gate in its
  place until it is met (`Scavenging level 1/2`, never `flint`, so the find stays a surprise), then the input as
  have/need. Tapping a short need's row lights the cards that make it, and the ledger lines they feed, with no words
  added (`smoked 2/6` lights both smoke tasks). An input nothing will bring again (a pool used up, nothing in play
  making it, no grant left) says so on its row (`flint 0/1, none left`). A wait on a part of the day reads as when it
  opens (`Opens after dark`) until it comes; a count the game keeps (arrivals) reads as have/need like a store. A tap still answers, at once and taking no time: the card glows red for a moment,
  what stopped it (that need, skill or step row, or the countdown when that is all it shows) flashes red and swells
  in place, and no text shows. A busy card can't be tapped and looks it (its bar running, the card's surface
  flat), except a glowing step not yet done while the queue or a rule holds the hands: it stays ready, takes its glow,
  and its tap cuts in (`decisions.md`, "A glowing step cuts in").
- **A working card draws no needs.** Its inputs are drawn as the work runs, so the live store would read short of the
  whole input a second after it started with all of it. A card whose run is `paused` (a store ran dry) draws them again.
- **The first card is larger:** stand-alone, double width and about 1.5× height, at the head of the card area, so
  at every size it is the most obvious thing to tap. Until its first tap it shows only its title, centred: its count,
  bar and time keep their room unseen, so the tap moves nothing.
- **Taps never move the layout; an arrival may, once.** A new card (it carries a dot) can push the groups under it down.
- **The desktop panel fades at its foot while more lies below**: it is its own
  scroller, so a fade over its last rem or so shows while its content runs past the bottom and it is not at the end. A still
  cue, kept under reduced motion. The phone's column scrolls with the page, so it has none.
- **A card that arrives out of sight dots the Tasks tab**. The panel stays
  on the tab the player left it, because the rule lesson's last step waits on Rules; the dot clears when Tasks opens.
- **Slots don't move.** A card that completes stays in its slot, showing its done state, until a new card needs a
  slot: the new card takes the slot of the card whose step opened it, so the next step lands under the finger. A
  done card nobody takes the slot of goes to Completed after a short hold (5 s, so the player sees it finish), never
  within 1.5 s of a press or while one is down. Nothing reflows during a tap.
- **Completed** cards are the Book's Done page (The Book), offered once one exists, with no count on it. A completed card
  there is dimmed, shows its cap reached, and can't be tapped.
- **A choice arrives as one thing:** its two cards appear together, side by side in adjacent slots, under one small
  heading. Each names its upside, and both show what they take.
- **A tap's line goes to the strip and the chronicle, never under the card.** It stays in the strip for its reading time: 2.9
  words a second (the research's 15 characters a second at the opening's 5.1 characters a word), at least 3 s. A refused
  tap has no line at all: the card goes red and the need it lacks is marked in its need line (`decisions/feedback.md`,
  "Rewarding at any moment"). Every tap outcome has exactly one home.
- **Skill rows** show what the next level pays and, when the view's forecast has it land, the time to it (`a find ·
  12m`). Change the mix and the time changes: the row is where the player sees the setup at work. A row with nothing
  ahead in the content reads `no more yet`, its bar grey, so it never reads as progress toward something.
- **A completion's "+1" pops from the card**, a level's burst lights a skill row or the Camp bar: the rungs are in
  "The feedback ladder". None of it moves the layout.

