## One column of attention

The eye works in one place: **the seam** between the artwork and the controls. Chips and the Camp bar sit on the
art's top, the aim just above it and the newest story line just under it; the hands strip and the cards start right
beside them. Nothing the player needs during play sits in a far corner.

- **The story strip, under the art.** The newest story line sits whole in a strip of its own, off the artwork, in the
  panel's colours: the pinned foot of the stage, just above the hands strip, on a phone, along the art's foot on a
  desktop (between the art and the ledger). It shows the newest lines that fit whole, oldest first, the
  older ones dimmer; a new line pushes out the oldest that no longer fits, so a quick run can still be read. A line
  shows when the arrival queue releases it, held back for the reading time of the one before (`decisions.md`, "A story
  line stays until it can be read"). On a desktop the strip's height is the tallest story line in the content at the
  strip's width, so no line is ever cut and none arriving moves anything: every story line the content can write (`Content.line_infos`,
  the kinds `game/book/chronicle.ts` routes to Story) is laid out unseen in the strip's one cell, the shown lines sit over
  them, and as many of the newest as fit that height show (at least the newest, so one where the room holds only one).
  On a phone the strip is three rows of the story's size (`--strip-rows`), so the pinned strip never grows for the
  longest line ever written: that is a content rule, every story line fitting three rows at a 360-wide phone's 328px
  (`tests/rules/checks/test_strip_rows.py`, its wrap checked against Chrome's), and three short lines fit with no gap between.
  The strip shows story lines only: a story beat's, a tap's, the body's. A find, a level, a rule's start or let-go and a
  fight go to the chronicle alone. The chronicle is one tap away (the tabs' Book, which opens on it: in the rail on a
  desktop, the bottom bar on a phone), dotted while a line it holds left the strip entirely before the player touched anything after it
  showed. A new line slides in once, about 200 ms (no slide under reduced motion).
- **The chronicle** (`ui/book/chroniclesheet.ts`; `decisions.md`, "The chronicle and unwrap, as built") is the Book's first
  page (The Book, below): a row of filters once two kinds have entries: Story,
  Finds, Levels, Rules, Fights, Town talk, each once it has one, and All. It opens on Story, at the top, newest first.
  It is a diary of visits: one stretch per return after at least half an hour away (`game/book/chronicle.ts`), each from the
  game second the player left to the one they next left, its lines oldest first. The newest return's stretch is the
  "Since you left" chapter (`ui/book/chapter.ts`): under an ember spine, never folded, titled with how long the player was
  away ("54m"), drawn under Story and All even with no line. Under Story its lines are followed by its figures as
  rows of a dim label and a value (`game/book/chronwords.ts`, `chapterRows`): stores ("+326 Dead wood · −26 Warmth"), levels
  ("Camp 1 → 2 · Foraging 2 → 4"), rules (one per line, "… came on ×2"), waiting ("1 ask", which closes the
  chronicle and brings the first ask into view); the levels and rules labels open their filters. When anyone came or
  went, a people section follows under a hairline: the dim word "people", then the lines telling a person's joining or
  leaving and each day's mention, set as story lines with their causes and taken out of the lines above. The counts of
  any other filter follow. With figures kept and nothing in them or the lines, it says "Nothing changed." Older
  stretches are titled "Away 54m" with how long ago the return was in the `ui.time.*` words. The page
  keeps each return in the save's presentation (`SavePresentation.visits`, written when the away reveal lands), so a
  reload keeps the stretches; lines before the first kept return are one stretch, "Earlier" (or "Now" when it is the
  only one). The stretches are the same under every filter, which picks their lines; one with none of them is not
  drawn. With no chapter drawn, the newest stretch drawn is open under a bright spine and square unless folded by hand;
  the others are folded to their counts by filter ("Story 4 · Finds 3"). Story lines are set as in the strip, italic in the bright ink; the others in
  the body size and ink. Under each line, in the dim meta ink, "↳" and its cause (`Content.line_infos`' cause, worded
  by `game/book/chronwords.ts`). Under Story, a stretch ends with its counts of the other filters, each a button that opens
  its filter. Lines the page words itself (fights, a skill's top) carry their kind and cause where the page words them;
  a return's away lines enter by the same stamps.
- **The panel's foot:** quiet text buttons at the rail's foot on a desktop, after the last thing in the panel elsewhere
  (`ui/partseat.ts`): "Feedback" opens the tester's sheet (a field, what is sent along, Send, Not now).
  Nothing that must be seen sits with the chips for it.
- **The aim, just above the art** (`decisions.md`, "Every stretch of play has a stated aim"): one line in the story's
  voice, over the art's column on a desktop and between the Camp bar's row and the art in the stage on a
  phone (scrolling away with the head). Its room is there from the first screen, so it never moves anything later;
  a new aim takes its turn in the arrival queue, after the lines that came with it. It is plain text, not a control: no
  dot, no glow.
- **Chips at the art's top,** in one row with the Camp bar, just above the art in its stage (above the
  pinned strip on a phone, scrolling away with the page), never on it: the head grows a row for each goal, and laid on the art it hid the camp's top. An
  icon plus the word (the word kept for screen
  readers and first sight), and under the word what the chip costs while it shows, two or three words from the
  content (`cost_key`, e.g. "hands slower"), in the meta ink. A chip is drawn once its cure is on screen (unlocked
  with it, or held back by its content's `offered_after` if it costs nothing), so the first status the player meets
  arrives with its answer. On a phone the chips stay in the head's one row while they fit, and the row keeps room for a chip and its
  cost line from the start, so one arriving never pushes the art down. When the Camp bar's line, the chips' cost lines
  and what the player carries do not fit one row (a long next-level line, two costed chips, a larger text size), what
  does not fit wraps onto a second row: nothing leaves the screen, and the art moves once when the row grows.
- **The Camp bar with the chips:** the bar first, the chips after it, so a chip coming or going
  never moves the bar's left edge. It arrives at its first level, with its burst, already pointing at the next; the
  first level is a surprise, every later one previewed. A warm bar (it is the player's), its level, and its next
  marker stating what that level pays (before → after, or "something new" for a story unlock and while what it pays
  names something the player has not met, so there is always a next mark to fill toward). Past the opening's last
  level it fills to that marker and holds there until the story lifts it. It is not tappable while it isn't
  interactive, so it doesn't look like a button.
- **What the player carries** (the book) sits after the chips the same way, icon and word, as plain text, no dot,
  until the journal's first entry moves it into the Book as its Journal page (The Book): from then on nothing of it is
  on the art, and Book is the one way to it.

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

