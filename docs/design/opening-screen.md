# The opening's screen

The page the first fifteen minutes run on, under the every-card-mixable engine (engine `DESIGN.txt`, "CARDS"). Rules
it answers to: `decisions.md`, "Shown in the design, not claimed", "What can be tapped looks tappable", "Tapping never
moves the layout", "The screen arrives when it means something", "Taught by need", the mix section and "Warm means
yours". What the opening contains is in
`content/`; nothing here names it.

It fixes four things the testers found: the eyes split between chips, cards and a tiny log; type that stayed small on
a 4K monitor; a first card lost against the scene; and a front page that didn't say what kind of game this is.

## One column of attention

The eye works in one place: **the seam** between the artwork and the controls. Chips and the Camp bar sit on the
art's top, the aim just above it and the newest story line just under it; the hands strip and the cards start right
beside them. Nothing the player needs during play sits in a far corner.

- **The story strip, under the art.** The newest story line sits whole in a strip of its own, off the artwork, in the
  panel's colours: in the pinned stage between the art and the hands strip on a phone, along the art's foot on a
  desktop (between the art and the skills and ledger). It shows the newest lines that fit whole, oldest first, the
  older ones dimmer; a new line pushes out the oldest that no longer fits, so a quick run can still be read. A line
  shows when the arrival queue releases it, held back for the reading time of the one before (`decisions.md`, "A story
  line stays until it can be read"). The strip's height is the tallest story line in the content at the strip's width,
  so no line is ever cut and none arriving moves anything: every line the content can write (`Content.line_infos`) is
  laid out unseen in the strip's one cell, the shown lines sit over them, and as many of the newest as fit that height
  show (at least the newest, so one where the room holds only one). The full log is one tap away (the "Log" button
  with the chips, which looks like a button), dotted while a line it holds left the strip entirely before the player
  touched anything after it showed. A new line slides in once, about 200 ms (no slide under reduced motion). The strip and
  the Log are the record; a line the player's own tap wrote also shows on that card (Cards), where the eyes already
  are (`docs/research/story-to-the-eyes.md`).
- **The Log sheet** (`ui/logsheet.ts`) is the siblings' frame with a sticky `.panel-heading` (the word on the button). It is a
  diary of visits: one stretch per return after at least half an hour away (`game/loggroups.ts`), each from the game second
  the player left to the one they next left, titled "Away 54m" with how long ago the return was in the `ui.time.*` words.
  The page keeps each return in the save's presentation (`SavePresentation.visits`, written when the away reveal lands), so
  a reload keeps the stretches; lines before the first kept return are one stretch, "Earlier" (or "Now" when it is the only
  one). The newest stretch is open under an ember spine and square; older ones are folded to their counts ("Taps 4 · Finds 3").
  A line's kind (`Content.line_infos`, authored in each file's `[line_kinds]`; kinds in `opening/line_kinds.py`) sets it:
  story lines are the only full-size text, in the bright ink; tap, find, level, body and fight lines are small, in the dim
  ink, under the story line they follow and behind the stretch's counts, which open them. Lines the page words itself
  (fights, a skill's top) carry their kind where the page words them; a return's away lines enter by the same stamps.
- **The panel's foot:** a row of quiet text buttons after the last thing in the panel (the ledger and skills on a
  phone, the cards on a desktop): "Feedback" opens the tester's sheet (a field, what is sent along, Send, Not now).
  Nothing that must be seen sits with the chips for it.
- **The aim, just above the art** (`decisions.md`, "Every stretch of play has a stated aim"): one line in the story's
  voice, over the art's column on a desktop and between the Camp bar's row and the art in the pinned stage on a
  phone. Its room is there from the first screen, so it never moves anything later;
  a new aim takes its turn in the arrival queue, after the lines that came with it. It is plain text, not a control: no
  dot, no glow.
- **Chips at the art's top,** in one row with the Camp bar and the Log button, just above the art in its stage (pinned
  with it on a phone), never on it: the head grows a row for each goal, and laid on the art it hid the camp's top. An
  icon plus the word (the word kept for screen
  readers and first sight), and under the word what the chip costs while it shows, two or three words from the
  content (`cost_key`, e.g. "hands slower"), in the meta ink. A chip is drawn once its cure is on screen (unlocked
  with it, or held back by its content's `offered_after` if it costs nothing), so the first status the player meets
  arrives with its answer. On a phone the chips stay in the head's one row while they fit, and the row keeps room for a chip and its
  cost line from the start, so one arriving never pushes the art down. When the Camp bar's line, the chips' cost lines
  and the buttons do not fit one row (a long next-level line, two costed chips, a larger text size), what does not fit
  wraps onto a second row, the Journal and Log buttons last at the right: nothing leaves the screen, and the art moves
  once when the row grows.
- **The Camp bar with the chips:** the bar first, the chips after it against the Log button, so a chip coming or going
  never moves the bar's left edge. It arrives at its first level, with its burst, already pointing at the next; the
  first level is a surprise, every later one previewed. A warm bar (it is the player's), its level, and its next
  marker stating what that level pays (before → after, or "something new" for a story unlock and while what it pays
  names something the player has not met, so there is always a next mark to fill toward). Past the opening's last
  level it fills to that marker and holds there until the story lifts it. It is not tappable while it isn't
  interactive, so it doesn't look like a button.
- **What the player carries** (the book) sits after the chips the same way, icon and word, as plain text, no dot,
  until the journal's first entry turns the book into the Journal button in the same place (The journal).

**Rejected, and why** (the story strip). The lines sat on the art for a long time, in a band under the chips, and
each fix moved the collision rather than ending it: the band shared its box with a chip row whose height changes (a
chip, its cost line, the book), so a line's first row ended up under the chips or the fade.
- *Keeping the overlay, with a smarter fade or a seat measured for the head:* tried several times; any overlay that
  shares a box with a row of varying height cuts a line whenever the row grows.
- *A strip that grows with its line:* a two-row line arriving after a one-row one would push the hands strip and the
  cards down under the finger ("Tapping never moves the layout").
- *Keeping the band and moving the chips off the art:* the chips and the Camp bar belong at the art, and the
  band's lines would still cover the scene the player is meant to watch.

## One type scale

Everything is sized in rem off a root that scales with the viewport: `font-size: clamp(16px, 0.5vw + 10px, 30px)`
(about 16px on a phone, 20px at 1920 wide, 29px at 3840 wide). Story lines are 1.15rem and card titles 1rem, so a
story line is never smaller than card text. Chips and bar labels are 0.9rem, the smallest text on the page. The
layout's widths are in rem too (the page tops out at about 100rem), so a 4K screen gets a larger page, not a wider
one with tiny type. Checked by rendering at 3840×2160 and 390×844 before shipping: the first card's title, a story
line and a ledger line are measured in device pixels on both, and the story line must be at least the card title.

## Desktop (wider than about 64rem)

```
┌──────────────────────────────────────────────────┬──────────────────────────────┐
│                                                  │ HANDS ▸ [ Gather ▓▓▓|Scav ▓▓ ]│  hands strip (slim mix view)
│ the aim, one line                                │        runs on            Edit│
│ Camp 1 ▓▓▓░ next…   ❄ cold  ◐ hungry       Log   ├──────────────────────────────┤
│                                                  │ Tasks · Completed · Rules    │
│              SCENE (the artwork)                 │ ┌──────────┐ ┌──────────┐    │
│                                                  │ │ card     │ │ card     │    │
│                                                  │ └──────────┘ └──────────┘    │
├──────────────────────────────────────────────────┤ ┌──────────┐ ┌──────────┐    │
│ NEWEST LINE, whole (the strip: the tallest       │ │ card     │ │ card     │    │
│ line's height, kept)                             │ └──────────┘ └──────────┘    │
├──────────────────────────────────────────────────┤                              │
│ SKILLS · LEDGER (a tall window)                  │ LEDGER (a short window)      │
│                                                  │ dry wood 2  −6/h  empty 20m  │  red
│                                                  │  ┌ rule ───────────────────┐  │
│                                                  │  │ When low on dry wood →  │  │  inline, unprompted
│                                                  │  │ ■ Lay to dry [Add rule] │  │
│                                                  │  └─────────────────────────┘  │
└──────────────────────────────────────────────────┴──────────────────────────────┘
```

The art's column reads top to bottom: the aim, the art with the Camp bar, chips and Log in a dark row along its top
(off the art until it holds a chip, the Camp bar or a dotted Log), then the story strip at its foot, right where the column meets the panel's cards. The strip spans the art's width, so
the longest line takes fewer rows here than on a phone.

On a tall desktop window the skills and ledger sit in a block under the strip. Until one of them has something to
show (the ledger comes with the fire) the block is not drawn, but its room is kept: the art is sized from the
column's height less the aim, the strip and that room, as large as its width allows. So the art and the strip sit
where they will stay, with the empty room under the strip, and the block's arrival, like a line's or a tap's, moves
nothing (over a larger first screen that shrinks once).

Once the stool is built the figure does its jobs (knap, roast, read) sat on it, facing the fire; before, it kneels at
the fire's left. The scene manifest says so with an all-of condition (`running:read_by_fire&feature:stool`).

A trip is away from the scene like any job that takes the figure off the stool: its card id is listed in `tools/scene/trips.py`,
so the seated figure gives way while the hands tap it and for its share of each cycle while the mix runs it. Its completions go
to the Log and its finds play on the band, as an uncapped card's and a trigger's lines already do.

## Phone

```
┌────────────────────────────┐
│ Camp 1 ▓▓░ ❄ cold  ◐  Log │  chips + Camp, pinned above the art
│ the aim, one line          │
│ SCENE                      │
├────────────────────────────┤
│ NEWEST LINES, whole (the   │  the story strip: the tallest line's
│ strip keeps its height)    │  height, pinned under the art
├────────────────────────────┤
│ HANDS [Gather ▓▓|Scav ▓▓]  │  hands strip, sticky under the art
├────────────────────────────┤
│ Tasks · Completed · Rules  │
│ ┌──────────┐┌──────────┐   │
│ │ card     ││ card     │   │  scrolls
│ └──────────┘└──────────┘   │
│ LEDGER …                   │
└────────────────────────────┘
```

The art, the story strip and the hands strip stay pinned while the cards and ledger scroll under them, so the newest
lines are always on screen while the thumb is on a card. In landscape the phone uses the desktop arrangement.

## The hands strip (the mix's slim view)

One row that says what the hands are doing, the mix's home. It takes no room, so no empty band shows, until the first
mix's offer (or once a mix or rule exists); it then arrives like any other new part, in its turn in the arrival queue,
and the cards below make way once. Until then each card's own bar says what the hands do. Once drawn it stays, and
the rows below apply.

| State | Shows |
|---|---|
| Tapping | `HANDS · Stand up` and the card's name; the bar itself stays on the card |
| Idle | `HANDS · idle` in grey |
| Mix offered (first time) | the two cards' names side by side and one button, `Show me` while the mix's lesson may start (the glow, if nothing else has it), which opens a new mix on the real editor where the lesson walks it. After the lesson is done or skipped with no mix made, the same button reads `New mix` and opens the editor with nothing built |
| Mix running | the split bar, one segment per card, each labelled with name and share (a segment too narrow for both cuts the name, never the share); under it the mix's name as plain text (a long one truncates, but gives way after the status text and the queue's head: a covered status keeps its width unseen, so the name is never squeezed for it). The rest arrive when they first mean something and then stay: `Mixes ▾` before the name once a mix is saved, `runs on` or `runs 7h` (never broken mid-value) once the ledger is there, and `Edit` at the end once a mix greys or an action card the first mix does not hold is in play |
| Yielded to a tap | the bar dims and reads `paused while busy`, with `runs …` and the rule's `until …` hidden for the room; it comes back unchanged when the tap lands |
| A card of the mix stopped (its store dry) | under the bar the player set, which never changes on its own, `running now` and the split that runs: each card at its share plus what it gains, `+25% from {card}` naming each source, and the stopped card's slice greyed, `{card} waiting`; a spent card also puts `{store} is used up` in the status. It comes through the arrival queue the first time; after that its row keeps its room and shows nothing while the splits match, so nothing under a finger moves when a store runs dry or refills. The town's rows show the same under each person's split (`ui/runningnow.ts`) |
| Greyed | the bar in grey with the cards left, a retired or completed card's share divided among them in proportion (the editor still shows it struck, until removed); under it `stopped · {card} done`, naming the card that left, in plain ink, since the grey bar alone still reads as work under way; and `Edit` |
| Any saved mix | `Mixes ▾` is the button that opens the Mixes list (the mixes only), so the way in says what it is; tapping a mix there makes it the default |
| A rule's mix running | that mix's bar, `Mixes ▾` and its name, where the rule lets go (`until 8 dry wood`, `until under 10 stones`; a rule with no band: `while under 2 dry wood`) where `runs …` would be, as a button that opens the Rules tab (its row and `Lately`), and `Edit` (it edits that mix); `paused while busy` still wins while a tap holds the hands |
| A rule's task on the hands | `HANDS · {task}` and where the rule lets go, the same button, as above |
| No mix running, mixes or rules saved | `Mixes ▾` in the meta slot, opening the list (or `Rules ▾` with only rules, opening the Rules tab) |
| Hint: a card the mix could take (once per card) | a quiet dot on the card itself (the new-card dot, `markNew`), no row and no sentence: a hands card in play, doable again, not in the player's own mix (saved, not greyed), tapped `hand_taps` times within `hand_taps_within_s` while a mix without it ran (opening.toml's `[repeat_offers]`, counted by the server, Step.repeats). Touching the card clears it and it is kept in the save (`Keeps.mixOffered`). It opens nothing and highlights nothing: every card could join a mix or be its own rule, so the game does not choose, and the player uses what the lessons taught. Never during a lesson, nor while the mix's lesson may still start. The first such card, once the first rule's lesson is behind, also starts the second mix's lesson (Lessons). Fits into: the new-card dot (`game/marks.ts`, `ui/fresh.ts`), detection `game/hints.ts` |
| Hint: a mix switch or an order card (once per chip) | the same dot on the chip in the story strip: a switch of the player's own mix made `switches` times under it within `switches_within_s` (Step.repeats, kept in `Keeps.switchOffered`), or a chip whose order card has no rule yet (once a page session). On a red ledger line whose order card has no rule, the dot sits on the line (the red line stays the signal; once a page session). Only once the first rule's lesson is behind; nothing is built, opened or highlighted. Fits into: as the card's |
| Hint: the first full store (once) | the same dot on the store's ledger line, the first time a store the player's mix or tap makes reaches its cap while another hands task could use the time and no rule watches it reach a level, once the player has seen a rule of theirs come on and let go (`game/caphint.ts`). No cap rule is installed in a new save; the dot opens nothing, and the cap rule's lesson (Lessons) starts from the line. Done or skipped, it never comes back. A player who ignores it loses only the overflow, which the full line shows. Fits into: as the card's, and lessons (`game/lessons.ts`) |
| Hint: the first dry store (once) | the same dot on the store's ledger line, the first time a card of the running mix stops on a store that ran dry (its line starved), no rule covers that store, and a hands card in play that makes it is ready and outside the mix (`game/dryhint.ts`), once rules are taught. The dot opens nothing, and the dry store's lesson (Lessons) starts from the line. Done or skipped, it never comes back. A spent card (nothing in play can refill its store) is not marked: no card added would help. Fits into: as the first full store's |
| Offer (someone asks) | on the mix offer's row, after it: the offer's question and one button per answer (44 px, each a primary tap), its time under its label (`takes 12m 30s`, from the answer's cost text; none when the answer starts nothing). No `Dismiss`: it stays until answered, which sends the answer. It is someone speaking, so it is set apart from the routine rows above it: a panel with an ember edge and a larger question, for as long as it waits. On arrival it takes the glow, as a ring round the whole row, until a button is tapped; the glow is the single attention mark, so a lesson's step keeps or takes it first and the offer waits for it, as it does for any other control already holding it. The ring is still, so reduced motion changes nothing. It arrives through the arrival queue after the last of its own lines in that step, or at once when that step holds none of them (it was shown before the page's last view). An offer answered while the page was shut (a rule may answer it) draws no row; an answer the server refuses because it was answered since redraws the save as it is. Not a guided offer: no lesson starts on it, and it does not wait for one, since a lesson's note follows its control and the question is the story's. Fits into: the mix offer's row (`ui/offerrows.ts` beside `ui/mixoffer.ts`), the arrival queue for its turn, the session for the refused answer |
| First rule's entry (after the end) | on its own row under the mix row, only while the first rule's lesson may start: a chip's rule, `While {chip} → {task}`, and `Show me`, which opens a new rule on the real editor and the lesson walks it. It comes the first time the chip is on with no rule on its store, once the end lines have been read, and stays until a rule is set (not when the chip clears), so the strip moves once, on its arrival. Once the lesson is done or skipped no row is drawn: the chip carries the hint dot. No offer builds a mix or a rule |

**On a phone the rows under the mix row (the offers) sit under the pinned strip, not in it** (`Hands.rows`,
placed by the screen as the lane rows are): they scroll with the cards, so a prompt does not cost the cards their room, and
the strip keeps the mix's bar, name and `stopped · {card} done`. They still arrive through the arrival queue, and a row that
arrives out of sight shows at once. On a wider screen they stay in the strip.

The dividers on the strip are draggable for a quick change; the strip never shows a 0% divider (a card joins with a
real share, see the editor).

**A lane run by rules** (a townsperson who works: api `CONTRACT.txt`, "A lane run by rules") gets a row under the
strip in the strip's shape: the lane's label (a later label once its unlock is held), what it does (the task's name, or
`idle`), the task's bar, and `Change`. The rows sit under the pinned band, not in it, so on a phone they scroll with the
cards and the pinned stage stays the art, the line and the hands. A row
arrives through the arrival queue the first time its lane is in view, then stays. `Change` opens the Rules tab on the
lane's task editor: the rule editor's simple view with only `Do`, the lane's own tasks, the rule's sentence and Save. It
opens on the rule the lane runs now, else the lane's first always rule that is not passed over, else a new always rule;
Save changes that rule's task in place (its condition kept) or adds the always rule. The lane's tasks are never cards in
Tasks or Completed: the row and its editor are their only way in. Fits into: the hands strip (`ui/lanerows.ts`, owned by
`ui/hands.ts`), the Rules tab's editor (`ui/laneedit.ts`), `game/lanes.ts` for what Change opens.

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
  making it, no grant left) says so on its row (`flint 0/1, none left`). A tap still answers, at once and taking no time: the card glows red for a moment,
  what stopped it (that need, skill or step row, or the countdown when that is all it shows) flashes red and swells
  in place, and its failed line shows. A busy card can't be tapped and looks it (its bar running, the card's surface
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
- **Completed** is a tab beside `Tasks` with no count on it. A completed card there is dimmed, shows its cap reached,
  and can't be tapped.
- **A choice arrives as one thing:** its two cards appear together, side by side in adjacent slots, under one small
  heading. Each names its upside, and both show what they take.
- **A tap's line shows on the card that wrote it,** hung whole under the card over whatever follows, out of the card's
  flow so nothing moves; the timer hides meanwhile. The panel foot (Feedback, Another device, Games) keeps room above
  it for the tallest line a card can hang (`--line-room` in `game.css`, set for a 360px-wide phone's two-column card
  and for the desktop panel), so a line never covers the foot, however few cards there are. It stays for its reading time: 2.9 words a second
  (the research's 15 characters a second at the opening's 5.1 characters a word), at least 3 s. Only the player's
  taps: lines written by the mix, a rule, time or a chip, and the end's, are strip-only. A finished card showing a line
  keeps its slot, drawn done, until the card taking the slot arrives; a card that has left the screen gets no line.
- **Skill rows** show what the next level pays and, when the view's forecast has it land, the time to it (`a find ·
  12m`). Change the mix and the time changes: the row is where the player sees the setup at work. A row with nothing
  ahead in the content reads `no more yet`, its bar grey, so it never reads as progress toward something.
- **A completion's "+1" pops from the card**, a level's burst lights a skill row or the Camp bar: the rungs are in
  "The feedback ladder". None of it moves the layout.

## Ledger and rules

The ledger arrives with the fire (the `ledger` feature unlock); until then nothing of it is drawn. It arrives with only
the lines that ask something: red, starved, or carrying an offer. Any other line joins the first time it is falling
(not only from the hands' passing tap), full while something feeds it, or covered by a rule, taking its turn as it
arrives. Once drawn a line stays, remembered for the account, so each line moves the layout once; with nothing
remembered (another account), the lines that ask something still show.

Lines are store rates per hour, with when a store empties or fills; the "full in" time is the view's forecast
(api `CONTRACT.txt`, "Forecast"), so no time is drawn when a rule will take from the store, or stop it, first.
A **falling line with no rule covering it is red**, with its answer right beside it: an **inline rule offer** under
the line, the card's condition and task (`Under 2 dry wood, until 6 → Lay to dry`), pre-filled, and `Show me` beside
the sentence, while the first rule's lesson may start. After it, no row: the red line is the signal and carries the hint
dot (below), and the player writes the rule in the Rules tab. Nothing is ever built from the line. On a desktop the ledger is a grid and the offer spans the whole row under its line, the line's neighbour
keeping the cell beside it. It is shown unprompted: in the preview, no player found the order card it kept out of
sight, and every player who saw the inline offer set it. On the hands a rule always runs a mix, so the lesson's editor saves
a mix of that task alone (named by the task) with the rule; a task on another lane
(the rack) becomes a rule of its own. Once set, the line turns white and reads `covered`. A rule that is set while the
line is still red (found by its store and test, so a level the player changed still counts) shows that rule's
sentence and `Change`, which opens the Rules tab on that rule's editor. A falling line a rule covers says `covered`, a
small button to that rule in the Rules tab. Player text says rule and task, never order or card.

- **Starved** (the store is at 0 and something waits on it) reads as a problem too, covered or not.
- **Full** (`damp wood 12/12 · full`) is not an alarm: the ordinary line colour, `full` in
  the time's dim ink (never green, which would call a loss a gain; never an alarm hue or a pulse), no `Edit mix`. The rate beside it is what spills,
  and the numbers and the bar show the loss: a cap rule is the player's to write (the cap rule's lesson), and skipping it costs
  only that overflow.
- **A rising line's rule** (a card whose condition is `n or more` on a store a task takes, a side lane's or a build on
  the hands: `4 or more catch → Smoke`) is marked on the line (a hint dot) once it is full or rising, calm rather than red, and
  stays until a rule is set.
- **A rule re-tuned:** a later card on a store whose rule is already set at other levels (a new need asks more of it) changes nothing:
  the player edits the rule in the Rules tab, and its goal rows show what the levels buy.
- **Falling with no order card to answer it** (a drain the mix or the rack is causing) names what draws on it most,
  with `Edit mix` beside it. A tap of the hands draining a store for a moment gets neither: it ends by itself.
- While a mix share is being dragged, the lines that card feeds or draws on light up.

## Fights

Fight parts show once the `combat` feature is unlocked (api `CONTRACT.txt`, "FIGHTS"); every number is the engine's, served.

- **A fight card** draws under its tap, never inside it: the odds as the smallest exact "1 in 5 lost" (a percentage when
  no whole pair up to 20 is exact), the two strengths beside it (`yours 12, theirs 9`), and what one lost fight costs or
  adds. Each strength is a button of at least 28 px that opens its entries under it, the base first, then sums as
  signed percentages, then factors as multiples; a second tap, or the other strength, closes it. No hover.
- **A standing fight** (a threat that runs on its own) is a row in the ledger's threats group under the stores' lines,
  calm and never red: its name, the same odds and strengths, and `fought, lost` as served.
- **The arrival queue** writes each window of fights since the last view as lines in the strip and the Log: k entries
  of which exactly j read as lost, which ones picked by a shuffle-bag draw seeded by save, runner and the fought count
  the window starts at (`app/client/src/game/fights.ts`), so the same window reads the same on every device. Past three
  in one window, one summary line of the exact counts. The draw changes no number.
- A threat's strength is never worded as answering what the player built: it rises with the region's clock alone.

## The journal

The book the player carries, written in: one page per thing known, its notes in the hand and its learned numbers
under them (api `CONTRACT.txt`, "JOURNAL"; `decisions.md`, "What you learn is written in a journal" and, under Art,
the type and the sketches). Fits into: Unlocks (entries and notes), Knowledge (the numbers, read off `View.fights`),
Lessons (its first use), the page shell (a sheet). Not a system: one caller, nothing to swap. The page's code is two
files: `game/journal.ts` (pure: which pages and notes show, what is unread, the numbers rows, the seeded draws) and
`ui/journal.ts` (the button and the sheet).

```
phone, portrait                        desktop, and a phone in landscape
┌────────────────────────────┐         ┌───────────────────────────────────────────────┐
│ Journal                    │ heading │ Journal                                       │
│ ┌────────────────────────┐ │         │ ┌───────────────────┬───────────────────────┐ │
│ │ (a first note, if the  │ │         │ │                   ░ a note, in the hand   │ │
│ │  seed puts it on top)  │ │         │ │     SKETCH        ░   a later note,       │ │
│ │      SKETCH            │ │         │ │  (seeded size     ░   indented            │ │
│ │                        │ │         │ │   and place)      ░ a note  [its sketch]  │ │
│ │ a note, in the hand    │ │         │ │                   ░                       │ │
│ │   a later note         │ │         │ │                   ░ ───────────────────── │ │
│ │ ────────────────────── │ │         │ │                   ░ runner      1 in 5    │ │
│ │ runner         1 in 5  │ │         │ │                   ░ yours 12, theirs 9    │ │
│ │ yours 12, theirs 9     │ │ numbers │ │                   ░ fought 6, lost 1      │ │
│ │ fought 6, lost 1       │ │         │ └───────────────────┴───────────────────────┘ │
│ └────────────────────────┘ │         │                        Close   Prev   Next    │
│ Close        Prev   Next   │ actions └───────────────────────────────────────────────┘
└────────────────────────────┘
```

- **The button.** From the first entry on, the book is a button in its own place after the chips: its icon and its
  word (the book's label), styled as the Log button (`.log-open`'s rim, bevel and tap size). Nothing left of it
  moves, and the change takes its turn in the arrival queue as a feature does, after the step's lines. It carries the
  quiet dot (`.new-dot`, placed as on `.log-open`) while a note is unread and at no other time, so a new entry dots
  it through its notes. It glows only as its lesson's step.
- **The sheet** is the siblings' frame: `dialog.sheet.journal-sheet`, a sticky `.panel-heading` (`ui.journal.heading`)
  and sticky `.sheet-actions` holding Close (`ui.close`), then `Prev` and `Next` at the right end, under the thumb.
  All three are `.quiet` at 44 px (no step here is the obvious next one, so none is `.primary`); `Prev` is off on the
  first page and `Next` on the last, never hidden, so neither moves. A tap on the backdrop or Escape closes it, as on
  every sheet; ← and → turn pages while it is open. It opens on the first entry with an unread note, else the page
  last shown in this page session, else the first. Pages run by section (days, creatures, places) and in content order
  within one, one per entry written.
- **The bookmarks** are a row of the panel's tab buttons (`.tabs`, `.tab`, `.on`) under the heading, in a `nav`
  labelled by the heading: one per section that has a page written (`ui.journal.days`, `.creatures`, `.places`), none for
  a section with no page. Each is a button, so Tab and Enter reach it. A bookmark turns to its section's first page with
  an unread note, else its latest page; the open page's section's bookmark is marked `.on` and `aria-current`.
- **The page** is parchment, written in the hand's ink: three tokens added to `:root`, the only new ones, since no
  sibling draws ink on paper. Their values are the ones the sketch method draws with
  (`docs/research/sketch-test/process.md`): `--parchment: #e6dcc6`, `--hand-ink: #2b241c`, and `--hand-pencil:
  #645d52`, the ink lightened only as far as 4.5:1 on the parchment holds (`tests/test_client_contrast.py` checks
  all three). The frame round the page stays the sheet's `--panel`, rim and shadow.
  - **The sketch:** the entry's drawing (`/assets/journal/<sketch>.png`), `aria-hidden`, since its labels are art and
    the notes carry the page's words. One that fails to load leaves its room empty. A page with none (a days page) is
    text alone: the sketch's room is not drawn (on the desktop spread the notes page stands alone, without a gutter), and
    nothing is loaded or reported.
  - **The notes,** in the hand: Reenie Beanie at 1.35rem, line height 1.2, in `--hand-ink` or `--hand-pencil` by the
    note's hand. Reenie Beanie reads small beside Alegreya Sans at one size, so its size is set above the story
    line's 1.15rem. Each note is its own block, in content order; a note's sketch sits to its right when it fits in
    40% of the page's width, else under it, at most 8rem tall. Notes only append, so a later one never moves an
    earlier one. The font is served from `app/ashfall_app/static/fonts/` beside the others (OFL, from google/fonts).
  - **The numbers,** in Alegreya Sans in `--hand-ink`, under a 1px rule in `--hand-pencil`: per runner, its label
    (1rem, weight 500), then the odds and the two strengths on one line, then the tally, in the fight card's own words
    (Fights), so the journal and the card never disagree. A runner never fought reads as the card's unknown: no
    figure but the player's own strength.
- **Phone** (the phone query, as the mix editor's): one portrait page across the sheet's width, the sheet full height
  (`100dvh`, under the safe area). Top to bottom: the sketch, the notes, the numbers. A long page scrolls between the
  sticky heading and actions, as a tall sheet does.
- **Desktop, and a phone in landscape** (the desktop query): an open spread, centred. The left page holds the sketch
  alone; the right page the notes, then the numbers at its foot (`decisions.md`: the sketch page on the left,
  numbers and lore on the right). The gutter between them is a shade of `--hand-ink` at 12% fading into each page.
  Both pages are the largest 600:780 boxes two of which fit inside the sheet, less its heading and actions, so the
  spread fits at 1280×800 and grows on a 4K screen with the rem-sized text. A right page whose notes run past its
  height scrolls inside itself, the numbers staying at its foot.
- **Seeded per entry.** The page's draws come from the seeded draw `game/fights.ts` uses, keyed by "journal", the
  entry id and the part, never the save, so a page looks the same in every game and on every device and differs from
  its neighbours. The seed sets the sketch's width (86–100% of its box) and its offset in the space left over (on the
  left page, its height too); on a phone, whether the first note sits above the sketch (35%, the method's "caption on
  top"); each note's tilt (−2° to +1°, half the method's range, since live text must stay easy to read) and indent
  (0–1.5rem), a note after the first indented further as one written later (the method's `later`). A note's draws are
  keyed by its index, so one written later leaves the earlier notes' draws alone. The seed never changes the text's
  size, the order or what shows.
- **Turning a page** is an answer to a touch, below the ladder: the new page slides 0.5rem in from the side turned
  toward and fades in over 150 ms; under reduced motion it is swapped at once.
- **Reading writes nothing.** Opening the sheet and turning pages send no request. The notes of every page the player
  turned to (the page it opened on counts) go as read in one presentation write when it closes (`CONTRACT.txt`,
  "JOURNAL"), so the dot clears by the player's taps, never by time.
- **Its first use is its lesson** (Lessons): the button is the trigger and the first step.

## The end

No card and nothing over the screen: the end lines land in the story strip like any other lines, the scene goes to
dusk, and play goes on into day one. What waits on the end (the rule offer) comes once those lines have had twenty
seconds to be read.

The end is a fact the save records (`view.ended_at`), so it survives a reload: the dusk stays even if a line goes red
afterwards. Coming back to an end the page had already shown replays its lines only if it happened under thirty
seconds ago; later than that, the dusk alone. An end that came while the page was shut was never shown, so the return
plays its lines in full.

## A feature's card

The last shipped chapter's last beat carries the content's one end card (the loader attaches it to the chapter's `end_feature`): docked at
the panel's foot on a desktop and along the bottom edge on a phone, nothing dimming the scene, with one button that
puts it away while the camp runs on. It comes once, after what arrived with its beat has been revealed; a page that
opens on a save already past it never shows it.

The dusk has no card: the night's real-time wait is taught by the clock lesson (Lessons), on the countdown, when it first shows.

## The mix editor

Opened from the strip's `Edit` (or from a greyed strip), or from `New mix` in the Mixes list or a rule slot's picker.
On desktop it replaces the card area beside the art, which stays visible; on a phone it is a full-height sheet
whose top shows the strip.

```
┌──────────────────────────────────────────────┐
│ Name [ Main                    ]   Save  ✕   │
│                                              │
│ [ Woodcutting 60% ▓▓▓▓▓▓|Scavenge 40% ▓▓▓▓ ] │  drag dividers; drag a segment off, or tap ✕ on its row
│                                              │
│ per minute        now   →   after            │  live, before Save; and the goal rows, right under the
│ damp wood        +6.0   →   +9.0             │  bar so a drag shows its effect without scrolling
│ stones           +5.0   →   +4.0             │
│ Run until…                                   │
│                                              │
│ Woodcutting   60%   damp wood +9/min     ✕   │  each entry shows what it does at its share
│ Scavenge      40%   stones +4/min        ✕   │
│ Gather (retired) ~~struck~~                ✕ │  a retired card, shown until removed
│                                              │
│ + Add                                        │  one control: opens the cards that can join, in place
│ ┌────────┐ ┌────────┐ ┌────────┐             │  tap or drag in; joins with a real share
│ │Forage •│ │ Rest   │ │Woodcut•│             │
│ └────────┘ └────────┘ └────────┘             │
│                                   Delete mix │
└──────────────────────────────────────────────┘
```


- The **before → after** totals update while a divider moves, before anything is committed. They list only the stores
  the edit changes, and are not drawn until it changes something; for a mix that Save will not run, the second column
  reads `if run`. `Save` commits; `✕` leaves without a change.
- **`+ Add` is folded** so the editor does not grow with every unlocked card. A tap opens the cards that can join in
  place and a second tap closes it; picking a card leaves it open, so several can join in a row. It opens by itself
  when a lesson's step points at a card inside it, and a new card's dot shows on `+ Add` while it is closed.
- **Saving never changes which mix runs** (`decisions.md`, "The mix"). Editing the mix that runs changes what runs;
  saving a new or another mix only saves it, and the Mixes list runs it. A rule slot's `New mix` points that rule at the
  new mix.
- A card joining takes an equal slice from the others (two at 50% plus one becomes three at a third). A card never
  joins at 0%.
- The name field is there from the first edit, pre-filled; the player may leave it. The header is one row, Name then
  `Save` and `✕` as a group; the name field shrinks first, and on a phone the group wraps as one. `Save as new` sits at
  the foot, left of `Delete mix`, when editing a saved mix; it keeps the original and is off while the name is empty or
  already a saved mix's.
- `New mix` opens the editor with no cards and a pre-filled name no saved mix has. `Save` stays off until a card has
  been added and the name is free; saving creates the mix.
- `Delete mix` asks once, in place (`Delete? Yes · No`). A mix named by a rule (`a rule uses it`; in the Mixes list
  `used by 2 rules`), or nested in another, says so instead of deleting.
- Renaming a mix that rules run points those rules at the new name; renaming the player's own keeps it the player's
  own.
- Rates are facts: `runs on` or `runs 7h`, `empty in 20m`. Nothing in the editor says balanced, efficient or better.

## The Mixes list

From the strip's name ▾ (or its `Mixes ▾`): the saved mixes and nothing else, the player's own first. A centred sheet
on a desktop, a full-width bottom sheet on a phone (at most 85% of the height, scrolling).

- **Tapping a mix makes it the default,** what runs when no rule's mix does; while a rule's mix runs, it sets what
  comes back, not what runs now. Each mix it can run says `Run`; ● and `running` (or, for the player's own, how long it
  runs) mark the mix running now.
- A mix rules run says how many (`used by 2 rules`, `used by a rule`) where `Delete mix` would be; one nested in
  another says so. A greyed mix (it holds a retired or completed card) can't be run, only edited or deleted, so a
  saved mix never quietly does something else.
- `Edit` on every row; `New mix` last.

## The Rules tab

A tab beside Tasks and Completed, there once this game has a rule or a queued tap, or, once writing rules is open in
this game (a rule seen on and then off in it, by the page or in the save's record of what its rules did) and the ledger
is in: then the tab stays with no rule left, its list empty but for `+ New rule`. A new game's first screen stays
without it. Kept for the page session if every rule is removed. A mix is what the hands do and a rule is what waits on something happening, so they
live apart: mixes in the Mixes list, rules here, one line each.

```
Tasks · Completed · Rules
≡   (Under 3 dry wood, until 8 ✎)    →  [Scavenge ▾]   top priority first
    needs under 3 dry wood · now 5                     why a rule is off, quiet, under its line
≡ ● (While tired ✎)                  →  [Rest ▾]       ● the rule on now
    Otherwise                        →  [Main ▾]       the player's own mix, the default
+ New rule                                             once writing rules is open
Rack                                                   each side lane's task rules, under its label
● (Under 2 dry wood, until 6 ✎)  →  ■ Lay to dry   Remove
```

- **Rules run mixes, in priority order.** The first hands rule whose condition holds runs its mix over the player's;
  when it lets go, the player's own comes back. A mix can have several rules (each its own line: X or Y).
- **The condition is a button** in the house button colours with an edit mark: it opens the condition editor in the
  tab. Changing a rule that exists is never gated.
- **The mix slot**, tapped, opens a picker: the rule's condition as heading, every saved mix (a greyed one off, the current one
  marked) and `New mix`, whose save points the rule at it. On `Otherwise` the same sets the default.
- **`≡` reorders the hands rules:** drag it (mouse, pen or touch; a press that moves a few pixels is a drag), tap it
  for `Move up · Move down · Remove`, or focus it and use the arrow keys. A side lane's rules keep their places. Every
  change sends the whole list in its new order (`set_orders`).
- A rule on another lane's task does that task while its condition holds, beside whatever the hands run: no slot, and
  `Remove` at its end.
- **A lane run by rules** has its section under its label like any side lane, every rule that taps one of its tasks in
  list order. Its always rule reads `{task}, always` (the task is in the words, so no `→`), a button that opens the
  lane's task editor; its ● marks the rule the lane runs now. A one-off whose task is done stays listed, `passed over`,
  until removed. A new rule on that lane (written, or an offer's `Add rule`) goes just before the lane's first always
  rule, so it can act. `outranked by …` names the rule the lane runs now: its condition, or its always words.
- A rule or a queue entry that answers an offer (set by an answer, never by this page) reads `Answer: {answer}`; such
  rules sit last, under `Answers`. An always answer rule (the answer
  order, set ahead) is listed there too, in list order, in its own words with no arrow; an offer whose answers start
  nothing shows each answer's effect where a time would be.
- A rule whose mix is greyed is passed over; while the player's own is greyed, the hands fall through to the rules or
  the queue.
- **A rule whose condition is exactly a chip's is the chip:** `While tired → Rest` here, `while tired` on the strip,
  and its editor offers only its mix and `Remove`. The player never sees that store as a number.
- Rules on a store's amount, a task's count and a skill's or the Camp's level are drawn, the kinds the editor writes.
  None is written or drawn on time, an unlock (unlocks only grow, so one the save holds is always true) or a task
  running (`set_orders` refuses it: an order on what its own mix stops would flip at every instant).
- **Shortcuts:** the ledger offer's `Change` and a line's `covered` open the tab on that rule's editor; the strip's
  `until …` or `while …` opens the tab itself, where `Lately` says what the rules did.
- On a phone, tapping is the primary path (the picker, ≡'s menu); dragging ≡ works with touch too.
- **A rule that is off says why** in a quiet line under it, in the ledger's grammar, from the engine's own
  reading of where each rule stands (`View.order_states`), never from the page's: `needs under 3 dry wood · now 5`
  (`needs 12 or more dry wood · now 5`) while its condition does not hold, the store's amount live; `outranked by
  {rule}`, the condition of the earlier rule whose mix has the hands, while its condition holds; `passed over · a task
  it runs is done` while its mix is greyed or its task completed, whatever its condition. A rule that is on has no
  line, and nor has a chip's rule that is waiting (its store is never a number). A side lane's task rule counts as on
  while its condition holds, as its ● does, even while its task waits to be ready.
- **Next**, the queue, sits between the hands rules and `Otherwise`, the order the engine gives the hands: a rule that
  is on, then the queue's head once it is ready, else the player's own mix. One line per entry, `Remove` at its end.
  The tab shows once the queue holds something.

### Lately

What the rules did, so a returning player can see why this mix is running (`research/design-101.md` §3, proposal 5). The tab's last block, under the side lanes, headed
`Lately`, there once any rule has come on. One entry per rule, the most recent change first:

```
Lately
Under 3 dry wood, until 8 → Scavenge
    ran 4 times · came on at 2 dry wood, 3h ago · let go at 8 dry wood, 2h ago
While tired → Rest
    ran once · came on 20m 5s ago                     a chip's rule: no levels; still on: no let-go
```

- **Facts only, in the ledger's grammar:** how many times the rule came on, then its last start and, once it has let
  go since, its last let-go, each with the store's level at that moment (never for a chip's rule) and how long ago.
- **The record is the server's,** since a rule can come on and let go while the page is closed (Step.rule_runs,
  CONTRACT.txt). It is a chronicle record, not a new system: the engine reports each order's latch turning true or
  false (`engine/rulelog.py`), and the save keeps one entry per rule, the most recent few, pruned as it is written.
- **A rule is known by what it says,** its condition and what it runs, since rules have no id. A reorder keeps its
  entry. An edit makes it a new rule, so the old entry goes and the edited one starts its own the next time it comes
  on; a removed rule's entry goes with it.

### When ready

After the end, a step (not work done again and again, which is the mix's) that is unready but will be ready by itself
(its blocker has a ready time, drawn as the card's countdown) carries a small `When ready` button over the free right
end of its foot, beside the tap target. A ready time is a promise, so it is drawn only while the page can see it kept:
a rule on the store the card waits on that is on and lets go below the need stops the store short, and then the card
shows its need and maker with no countdown and no `When ready`. A step waiting on a store the player has never been
shown (the night) is a clock, not something to plan around: it draws its countdown alone, with no need line and no
`When ready`, since what it opens must open in front of the player (queued, the morning's step would open the snares
unseen, and the 2 AM test fails). It queues one tap of the card, held until that tap
completes, and the card flies to the Rules tab. Queued, it stays as a quiet `in Next` mark, so the card keeps its size;
the strip notes `next: {task}` (the first thing to give way on a phone). The first time it is on show it takes the one
glow.

### The condition editor

Writing a new rule is its own taught step (`decisions.md`, "The mix"): `+ New rule` shows once the page has seen one of
the player's rules come on and then let go, remembered in the browser. Until then rules come only from the offers.
Changing a rule's levels is open from the first rule on.

The editor takes the Rules tab's place until it is closed. A new rule opens **simple**:

```
New rule                                          ✕
Do    [Forage] [Cook roots] [Rest] [Smoke roots]     the tasks a rule can do, hands and other lanes
When  [hungry]                                       once a task is chosen: what it answers
[More options]
────────────────────────────────────────────────
While hungry → Cook roots                            the foot, pinned to the bottom of the screen while it scrolls
                                         [Add rule]
```

`More options` opens the **full** editor in place, and a rule being changed opens on it:

```
Run Evening when…                                 ✕
Do    [Forage] [Cook roots] [Rest] [Main] [Evening]  the tasks, then the saved mixes
When  [hungry] [tired] [dry wood 3 / 12] [stones 5 / 12] …     every chip shown so far, every store
Levels  [Camp level 1] [Foraging level 2] …         the Camp and each skill, at the level each stands at
Tasks   [Forage] [Cook roots] …                     each task in play, by its count of times done
[ When 3  Until 8                       ▾ ]         the levels, folded on a new rule; open when changing one
  [ falls below | reaches ]
  When  [−] 3 [+]      Until  [−] 8 [+]             stacked on a phone; 44 px targets
  ░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░                      the band n..m over 0..cap, a tick for now: drawn, not a control
while Evening runs: dry wood +0.80/min              a fact from one dry run, never a verdict
────────────────────────────────────────────────
Under 3 dry wood, until 8 → Evening
Remove                                   [Add rule] Remove only when editing; Save in place of Add rule
```

- **The common rule is two taps:** what it does, then the chip or store it waits on. A new rule starts with nothing
  chosen and `Add rule` off. In the simple view, `When` appears once a task is chosen and offers only what that task
  answers: the chips whose store it makes, and the stores with a ledger line it makes; a store rule takes the default
  levels below, stated in the sentence. Choosing another task clears a condition it does not answer. The rule as a
  sentence and Save stay pinned at the screen's foot, under the thumb, whatever is scrolled.
- **The full editor keeps every choice** (`decisions.md`, "The mix"): the saved mixes beside the tasks, every chip,
  store, level and task count a rule may watch, the levels (folded behind one row stating them, which opens them in place; a rule being
  changed opens with them shown) and the rate fact. `More options` goes once it is open.
- **A saved mix of one task alone is that task:** `Do` offers the task once, and choosing it runs that mix. A hands task
  with no such mix gets one when the rule is added (named by the task), as the offers do.
- A chip chosen is the chip's own condition, worded `While hungry`, with no levels: the player never sees that store as
  a number. The full editor offers every chip from its first showing on (`View.chips_seen`), whether it shows now and
  whatever task the rule then does: a player who meets a need and goes to write its rule finds it there, even before
  the task that answers it is open or after the chip has cleared. The simple view's narrowing stays: there a chip
  appears under a task that makes its store.
  Only stores of two items or more are offered (a smaller one has no room for a band).
- **A rule runs a mix or a task.** `Do` lists the unlocked tasks that can be done again, by their card labels; a
  one-off, a card at its cap and a retired one are not offered. A task on another lane saves the same order an offered
  card does (`tap_card`). A task on another lane has no rate to state, so it shows no `while … runs` fact.
- `falls below` comes on below `When` and lets go once the store reaches `Until`; `reaches` comes on at `When` and
  lets go below `Until`. The band is at least one item and inside the store's cap, so a rule never flips at one
  level and is never always true (the numbers' conventions: `api/CONTRACT.txt`). A store under two items is off.
- The words put the number before the store and use no verb (`Under 3 stones, until 8`, `12 or more dry wood, until
  under 6`), so they read right whatever the store's name.
- A new store rule starts below a quarter of the cap, until halfway to full (`reaches`: at full, until below half),
  and is added as the lowest priority. Editing keeps the rule's place; a rule written before bands (an offer with no release) opens with `Until`
  already filled in, visible in the sentence before Save.
- **A level or a task's count takes one stepper** in the store levels' place: `Level [−] 3 [+]` reads `Once Foraging
  reaches level 3`, `Times [−] 4 [+]` reads `Once Forage is done 4 times` (`Once Forage is done` at one). Each starts
  one past where it stands now, so a new rule is not already true, and reaches 1 at the bottom; a capped task stops at
  its cap. Counts and levels only go up, so there is no `Until`. The Camp stops below its first held level not yet
  lifted: the store passes that level's mark before the bar counts it, so a rule on it would come on while the bar
  still read the level below. Only what the save holds is offered, so the list grows with the story; a done task's
  count no longer moves and is not offered.
- **A pick that shows a control brings it into view,** centred in the editor's scroll (at once under reduced motion),
  so the store levels or a stepper never open under the pinned foot.
- Save is off, with `a rule already does this`, for a rule identical to another.
- Changing a chip's rule shows its chip as the heading, its `Do` row, the sentence and `Remove`: no stores, test,
  levels, band or fact.

Known limit: the ledger's `covered` ignores a rule's condition (a rule that would never come on still
covers its line). The rule's own line in the Rules tab says it is waiting and on what.

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
| A stopped mix | the first running mix to grey over a done card; its `Edit` is the trigger, and the mix has another card left to run or the content names a card that takes the done one's place (`replaced_by` on the retired unlock, in play and not yet in the mix). No `Show me`: the editor is the player's own | `Edit`: `{card} is done, so this mix stopped.` then `Open Edit.`, or `{card} is done, so this mix stopped. {task} takes its place. Open Edit.` with a replacement · with one, its add button: `Tap + {task} to add it.` · the editor's ✕ on the done card: `Tap ✕ to take {card} out.` · `Save`: `Save, and the mix runs again.` |
| Switching mixes | after the end, a hands build waits on a store nothing at work makes, and a saved mix that is neither the running one nor the player's own makes it, or else the running mix could take a card in play that does (`game/teach.ts` `switchCue`); the strip's `Mixes ▾` (the mix's name, with a mix running), or `Edit` in the second case, is the trigger. No `Show me`: it points at the player's own controls | `Mixes ▾`: `{build} needs {store}. Your {mix} mix makes it. Open Mixes.` · that mix's `Run` in the list: `Tap {mix} to run it.` — or, when only the running mix could take the card, `Edit`: `{build} needs {store}. {task} makes it. Open Edit to add it to this mix.` · its add button: `Tap + {task} to add it.` · `Save`: `Save, and the mix makes {store}.` |
| The clock | the night's countdown (the foot of a card waiting on a store the player was never shown) is on show, a few minutes into the night | the countdown (read): `A real-time wait: morning comes when it runs out. The camp keeps going meanwhile.` |
| The journal | the Journal button is on show and no other lesson runs; no `Show me`, since the button is its own control | the Journal button: `What you learn gets written in here.` · the open page's last note (read): `A dot on the button means a new note.` |
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

The journal's lesson runs inside its sheet after the first step: while a sheet is open the note is drawn inside the
sheet's own layer, so the modal sheet never covers it. The numbers are a lesson of their own, so a page with none (a
days page) never leaves a step waiting: the journal's lesson ends after its notes, and the numbers' starts the first time
a page with numbers is open (at once, when the sheet opened on one).

The Journal button can show just before a guided rule offer (the book and the ledger open at the same beat). The
journal's lesson yields: until its button is tapped it holds no offer back, and gives way to the rule's lesson when
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

## Dots and the one glow

- **A dot** is small and quiet (no number, no pulse). It marks only a control the player can act on and has not yet: a
  new task card, a new Add entry in the mix editor, the Journal button while a note is unread (cleared note by note
  as the player turns to its page). Plain text never gets one: story lines, the book while it is text, chips,
  ledger lines, skill rows, needs, labels, headings, mix segments. It clears when the player interacts with the thing
  (a tap, a drag, a key) and when the thing is put to work: joined to a mix (in the editor or by Both), running, held
  by any saved mix, or named by a rule. A task already at work never shows a dot. Never cleared by being seen or by
  time, and it never counts anything. The Log button takes one too, while a line it holds left the strip before the player touched
  anything after it showed; it clears when the Log is touched.
- **The glow** points at the one obvious next step, only when there truly is one, and only one at a time. In the
  opening: the first card; the first mix offer (`Both`); the first strike when everything it needs is in. Whenever
  the running mix greys (a task in it retired or completed): the strip's `Edit`, until the editor is opened. After
  the end: the strip's first-rule entry (`Show me`, the first time it is on show, after a return's reveal has shown it);
  the first `When ready`; and a someone-asks offer's row, on arrival. Switching mixes when a build waits on a store nothing at
  work makes is a lesson ("Lessons", below), not a glow.
  A player who has touched nothing for a while (`NUDGE_IDLE_S`) while no mix runs is pointed at the first ready card they
  have never completed, with the same glow, when nothing else has it. When no card is ready at all and the next thing is a timer card more than 10 minutes out (the opening's
  end), the same nudge goes to that card, so the eye lands on its countdown.
  The Rules tab's label, once the page has seen a rule come on and let go (when `+ New rule` opens), until the tab is
  first opened (remembered in the browser, across new games); before that the label is there without it. A rule just
  added from an offer flies to that label. A glow that is due while another control holds it, or while the
  reveal holds its control back, waits. Nothing else glows, and nothing pulses for urgency.

## The feedback ladder

Fits into: Feedback (`systems.md`).

Each kind of event has one fixed effect, sized by how much it matters (`decisions.md`, "Juice has a ceiling, written
as a ladder"). Nothing grows when its event repeats: a card's tenth completion looks like its first. The rungs are data
in `app/client/src/ui/ladder.ts`, their sizes keyframes in `app/client/src/game.css`. Lowest first:

| Rung | When | Effect | Under reduced motion |
|---|---|---|---|
| Background | A card completes by the mix or a rule | "+1" rising off the card | "+1" held still on the card, then gone |
| Tap | A card completes from the player's tap, a queued one (Next) included | "+1" and a ring spreading from the card | "+1" held still and a still ring, fading |
| First | Something new arrives: a card, chip, skill row, ledger line, feature | The arrive pulse, and a dot if it can be acted on | Shown at once, with its dot |
| Level | A skill or the Camp reaches a level | The burst: a wider, longer ring, the row lit | A still ring, the row lit, fading |
| Big | The end; a feature's card | Its lines in the strip, the scene to dusk; the card docks ("The end", "A feature's card") | The same: neither moves |

- **A rule's completion sits with the mix's**, one rung below the same completion from a tap, so a tap stays special
  and a mix or rule running alone still shows what it did. A rule's run is a tap the page did not send, started by a
  standing order (`app/client/src/ui/fires.ts`, the card's by-order dot).
- **Below the ladder, answers to a touch or a change of state**, each no bigger than the background rung: a pressed
  control dips; a failed tap pulses red on its card and blocker (colour, kept under reduced motion); a share divider or
  a ledger line coming back from red settles; a rule row that just started a card lights (colour, kept under reduced
  motion); an accepted rule offer flies to the Rules tab (under reduced motion the tab only takes its dot); a journal
  page turned slides in (The journal; swapped at once under reduced motion).
- **No sound yet.** When sounds come, each rung gets one, fixed like its effect, and none carries information alone.

## One thing at a time

A live step's story lines come first, each alone: the arrival queue (`app/client/src/game/arrivals.ts`) shows a line (strip and card
together), then holds the next turn for the line's reading time, and only then the card, chip, skill row or ledger
line that came with it (at the usual 400–700 ms pace). A ledger line is read before the cards: the ledger's new lines
keep the pace among themselves, then hold the next kind (skills, cards) for the longest one's reading time, its rule
offer's sentence counted, so the fire's ledger is seen before the cards that came with it. The one-off changes take turns too: a completion's ring and
"+1" (except on the card showing the line, where they come with it), a level's burst, a ledger line settling,
the glow (the Rules tab's label too), a rule row's fired pulse and the Rules tab's pulse when a
flown rule lands (the flight itself answers the tap, so it goes at once); a finished card waits to leave for Completed,
and a self-update's reload waits until nothing does. A tap or key moves on to the next line while lines wait, or shows
everything still waiting when none do (Escape and a tap on the story strip show everything), and the tap goes
through: input is never held. Something drawn while the queue still waits takes the next turn. Under reduced motion
the lines still lead and the ledger's hold stays (a wait is not motion); what follows them comes together. The end's lines take their turns the
same way.

## Coming back

What arrived while the player was away (the page reloaded, or hidden and shown again) is shown in turn, so a return
reads as what changed rather than everything at once (`decisions.md`, "Idle time pays out mostly in the old").

- **What counts:** everything new between the last view the page showed and the first one after the return. A reload
  first re-reads the kept game at its own time, so it is a return like any other.
- **Drawn at once, shown in turn.** Everything new takes its place together, so the layout moves once; each new thing
  stays invisible in its place until its turn, then shows with the usual arrive pulse. Dots follow their own rule
  (only on a control not at work). A new lane group's heading comes with its first card, a ledger line with its rule
  offer.
- **Order:** by when each happened, where the view says; otherwise by kind: feature, chip, ledger line, skill, card
  (the cards last, nearest the finger). The return's story lines lead, as a live step's do: each alone in the strip, held
  for its reading time before what came with it, so a planned moment that landed while the player was away plays in
  full: every story line plays, in order, however many, and the newest stays in the strip
  afterwards. Lines that come again and again are not story lines: a chip's on-line
  (which plays only the first time the chip shows in a save) goes to the Log only; its off-lines (which can come every
  cycle while away) collapse to the chip's last change, and that one and a repeat task's lines (an uncapped card's) go
  to the Log only. Which line is which comes from the content (a chip's line keys) and the
  view (the writing card's cap), never the text.
- **Pace:** the first at once, then 400–700 ms apart, the whole at most 4 s beside the lines' and the ledger's reading
  holds; past that, the rest together. Anything
  out of sight (below the fold on a phone) shows at once and takes no turn.
- **Never in the way:** taps and keys work throughout. While story lines are waiting their turn, a tap or key moves on
  to the next one at once; Escape, or a tap on the story strip, shows everything still waiting; with no line waiting,
  the first tap or key shows everything. A tap does this at its release, once it has landed on what it pressed:
  shown at the press, a line moved the controls under the finger and the tap was lost. Under reduced motion
  everything shows at once, with its dots.

## The front page

A stranger has to see within a few seconds that this is an idle game: shown more than told.

```
┌────────────────────────────────────────────────────────┐
│                      ASHFALL                           │
│                                                        │
│  ┌──────────────────────────┐  ┌────────────────────┐  │
│  │ the scene, at dusk,      │  │ HANDS [▓▓▓▓|▓▓▓]   │  │  a live, looping glimpse:
│  │ fire lit                 │  │ ┌──────┐ ┌──────┐  │  │  bars filling, a +1, a ledger
│  │                          │  │ │card ▓│ │card ▓│  │  │  line ticking (no story text)
│  └──────────────────────────┘  │ ledger  +9/min     │  │
│                                └────────────────────┘  │
│  An idle game. Your camp keeps working while you're    │
│  away: come back whenever.                             │
│  Single-player · plays in the browser · saves itself   │
│  · in heavy development                                │
│                                                        │
│                     [ Begin ]                          │
└────────────────────────────────────────────────────────┘
```

The glimpse is drawn by the page from canned numbers. It is a picture of the screen, so it shows no story line.
**The text lines under it are provisional**: build and render the glimpse first, and add a genre line only if
the visuals don't make it plain that this is an idle game; any that stays is game UI and goes through the voice
pass. Begin is there at once, without a fade. A returning player
never sees this page: a reload goes straight back into the game.

## Open questions for the owner (spoiler-free)

1. **The first mix comes earlier and pairs two jobs done by hand** (at about minute 3.5, when two needs pull at
   once). The first tool upgrade then retires one of them, which greys the mix and teaches the editor through a
   choice the player made. This replaces "the first mix pairs the two jobs the edge opens". Agreed?
2. **The bar to work toward is a Camp bar**, filled by work done (tapped or mixed, by bar time, never by tap count).
   Each level pays a stated bonus to something the player already has, and it becomes a choice of two per level once
   the town exists. Is the camp the right thing to level, and is "Camp" the right word?
3. **The story's pull:** the opening now carries a few hints the earlier version saved for later days, and it ends
   on an open question, not a settled moment. Each hint still reads as atmosphere. Is that within "a little more"? A
   spoiler is behind the specifics if you want to look.
4. **The camp can run itself from about minute 6** (the first order), well before the end at about 14:30.
   Fine to have the first leave-it-running moment that early?
5. **Where the list of what the rules did lately lives:** decided.
   At the foot of the Rules tab, one entry per rule (The Rules tab, "Lately").
