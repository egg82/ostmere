# Desktop playthrough of day one (2026-10-24)

Where a newcomer at a desktop browser would likely drift in the first session, read off the screen at 1440×900. It
covers the queue item "a desktop playthrough in a browser, for what the model can't see". It is a model's read of
the screen, not tester data: what it predicts about people still needs `docs/tester-protocol.md`'s cold testers. The
phone pass left no written report, so the comparison below is against the phone layout in
`docs/design/opening-screen.md` and the phone fixes in the log.

Lines, beats and cards are named by key or card id (`c_gather_wood` → `gather_wood`), never by what a story line says.
Times are game time from the first tap. The player taps promptly, so a slower person reaches each point later.

## How it was played

origin/main at 416e873, run locally: its own server against a throwaway postgres:17, with the scene art copied from
the live site's `/assets/`. One headless Chromium at 1440×900 drove it, with `document.visibilityState` checked
`visible` at every shot. Game time was moved by hand: the server's clock read a file, and Playwright's fake clock
moved the page by the same second, so the first session played in about 25 wall minutes. It ran from the front page
through the opening's end (the "Until morning" card at 15:02) and about 9 minutes past it. Screenshots are
kept outside the repo (`d01`…`d12` are the ones cited), as is the harness.

The player acts as someone who does not play idle games: taps the glowing thing, then any new card that is ready,
then what its needs point at. It follows a lesson when one is on screen and answers offers with their raised button.

## Where a person would likely drift

### 1. The first mix's lesson stalls at its second step, and no later lesson runs (5:40 onward)

`d05-lesson-add-step.png`, `d06-lesson-back-to-step-one.png`, `d08-rule-editor-unguided.png`

The mix offer arrives at 5:40 with its glowing Show me. Show me opens the editor, and the note says to tap
`gather_wood`'s chip in the Add row. Tapping the chip adds the card, but then the note goes back to step one
("A mix works two tasks at once…") and the glow returns to Show me in the hands strip, which is still on screen
above the open editor. Tapping `scavenge` changes nothing, and Save starts the mix with the note just gone.

**Cause, verified in Chromium:** an Add-row chip joins the mix on `pointerup` (`app/client/src/ui/editordrag.ts`), and
`drawAdds` replaces the chip before the browser fires `click`. So no `click` reaches the document at all: a capture
listener logged none. The lesson runner ends a "touch" step only on `click` (`app/client/src/ui/lessons.ts`,
`touched`). Step two never counts, `stepOnShow` falls back to the only target still on show (step one's offer
button), and the lesson never ends. A keyboard press still works, because it takes the `click` path.

**What follows:** the run never ends, so it is never kept, and `Lessons.tick` starts no other lesson while one is
held. The rule lesson never starts. Its offers at 6:02 still say Show me, with no glow. Show me opens a blank
New rule editor (Do / When / Add rule) with no note at all, after a button that promised to show something. The
changing-the-mix lesson needs the first one kept, and it uses the same Add-row step, so it would stall the same
way. Every mouse player who doesn't press Skip hits this. Touch also joins on `pointerup`, so phones very likely do
too (not run here). The phone pass predates this lesson (2026-10-22).

### 2. The newest line sits at the window's bottom edge, far from the card (0:00–3:25)

`d01-first-screen.png`, `d02-strip-far-line-overflow.png`

On the first screen the art is centred in the left column with black bands above and below. The aim sits in the top
left corner, 16px italic, and the first card is at the top right. The story strip is the left column's foot: the first
line lands at y≈847, about 950px left of the card and 650px below it. While tapping, the eyes stay on the card, and the
tap's own line on the card is the only text read near it (`docs/research/story-to-the-eyes.md`, finding 1). Lines
written by time or by the mix land only in the strip, which is out of the way for these first minutes. At 3:25 the
skills band arrives, the art shrinks from 916px to 620px wide, and the strip jumps up to y≈467 (`d03`), so it moves
once, a long way. The strip-under-the-art layout landed today (30baf2f), so this is its first desktop look.

On the phone the strip sits just under the pinned art, a thumb's width from the cards, so this is desktop-only.

### 3. The fire lands everything at once, and on a desktop all of it is visible together (6:00–7:40)

`d07-fire-burst-two-show-me.png`

Within about 100 s of `strike_fire`: a new aim; the ledger with four lines, two of them red; two rule offers, each an
identical Show me; two chips with their costs; four new cards (`knap_edge`, `forage`, `roast_roots`, `rest`); and the
Camp bar's next mark. A phone shows this one scroll-screen at a time. At 1440×900 every piece is on screen at once,
spread across art, ledger, skills and panel. Nothing glows (issue 1), so nothing says which to take first. If the rule
lesson ran, one Show me would glow, but the second identical button would still compete.

### 4. The panel scrolls on its own, with no sign it does (8:13)

`d10-drying-below-fold.png`

When the two craft cards arrive, the arrival queue holds their room. That pushes the Drying group (`lay_to_dry`)
below the panel's bottom edge at y≈880. The panel is its own scroller (`overflow-y: auto`, content about 1100px in
900), with no fade or other edge cue. The rack card a newcomer had been tapping goes out of sight just as the mix
stops, the Swap-in offer appears, the Camp bar levels and a new aim arrives (`d10`). On a phone the whole column
scrolls with the thumb, so this is desktop-only.

### 5. After a rule is added the panel stays on Rules (7:50)

`d09-panel-left-on-rules.png`

Add rule leaves the Rules tab open, and the cards are hidden behind the Tasks tab. In this run cards kept arriving
(`woodcutting`, the crafts) within the next minute. A newcomer who doesn't think of the tab row as navigation is
looking at a rules list that no longer asks anything. This run didn't check whether the Tasks tab marks a card that
arrived out of sight.

### 6. The first done card's line spills onto the panel foot (0:20)

`d02-strip-far-line-overflow.png`

When `stand_up` finishes, the card shrinks from the first card's double size to a single slot (210×96). Its long last
line then overflows below the card and covers the Feedback button until the next card takes the slot. It is short and
early, but it is the first thing the player sees the game "do" after their own taps.

### 7. Lesson notes cover a neighbour

`d04-mix-offer.png`, `d05-lesson-add-step.png`

The mix offer's note sits over the Tasks / Completed tabs (`d04`). Step two's note covers the Add row's third chip,
`strike_fire`, which shows only as "+ S" (`d05`). `strike_fire` is the card the aim has been asking for since 0:00, and
its needs had just been met.

### 8. After the end, nothing new for seven minutes (17:54–24:43)

`d11-until-morning.png`, `d12-after-the-end.png`

The Until morning card ("Morning is 1h away, in real time") comes at 15:02. Back to the camp brings a few new cards, one
of them waiting on the night with a 53-minute countdown. After 17:54 no new card arrives through 24:43, stores sit full, and
the only motion is bars. This is the queue item "The night visits go quiet". It isn't desktop-specific; it's
recorded here because a person at a desk is likely to leave at this point.

## Desktop against the phone

- **Desktop only:** the strip's distance from the cards and its one big jump (2), everything of the fire's burst on
  screen at once (3), the panel's own unmarked scroll (4), the aim in the far corner (2).
- **Both, very likely:** the stalled lesson (1). Touch joins on `pointerup` too, and the phone pass ran before the
  lesson existed. The Rules tab left open (5), and the quiet after the end (8).
- **What was fine:** at 1440×900 the first card is the obvious thing (`d01`), the front page's Begin sits above the
  fold, the hands strip and its offers sit at the panel's top where the eyes start, and the ledger's inline offers sit
  beside their red lines.

## Fixes, ranked

1. Make an Add-row chip's `pointerup` join count as the lesson step's touch (the editor tells the runner, or the runner
   listens for `pointerup`), and drive it in a client test with a real pointer sequence, not a synthetic `click`.
   Fits into: the lesson runner (`app/client/src/ui/lessons.ts`). Covers the first-mix and changing-the-mix lessons.
2. Let a held lesson end when its trigger has gone and none of its remaining steps can show, so one stuck lesson
   never blocks the rule lesson for the rest of the page's life. Fits into: `Lessons.tick`.
3. On a desktop, put the story strip directly under the art from the first screen (art top-aligned, spare height below
   the strip), so the newest line starts near the cards and doesn't jump about 380px when the skills band arrives.
4. Stagger the fire's arrivals: the second rule offer waits until the first is answered, and the four new cards come
   behind the ledger rather than with it, so the 6:00–7:40 stretch asks one thing at a time.
5. Give the desktop panel a visible cue when its content runs past the bottom (a fade at the foot while
   `scrollHeight > clientHeight`), so the Drying group and anything else below the fold reads as there.
6. After Add rule (and after the ledger's one-tap Add rule), return the panel to Tasks, or mark the Tasks tab when a
   card arrives while another tab is open.
7. Keep a tap's line inside its card: either the finished first card keeps its size until its slot is taken, or a long
   line is clipped to the card, never drawn over the panel foot.
8. Have the lesson note avoid covering other controls: below its target, then beside it, then above it, never over a
   sibling chip or the panel's tabs.
