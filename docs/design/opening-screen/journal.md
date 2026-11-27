## The journal

The book the player carries, written in: one page per thing known, its notes in the hand and its learned numbers
under them (api `contract/journal.txt`, "JOURNAL"; `decisions.md`, "What you learn is written in a journal" and, under Art,
the type and the sketches). Fits into: Unlocks (entries and notes), Knowledge (the numbers, read off `View.fights`),
Lessons (its first use), the Book (a page of it). Not a system: one caller, nothing to swap. The page's code is
`game/book/journal.ts` (pure: which pages and notes show, what is unread, how a turn runs, the contents, the numbers rows, the
seeded draws), `ui/book/journal.ts` (the Book's Journal page) and `ui/book/journalnav.ts` (its controls for finding a page).

```
phone, portrait                        desktop, and a phone in landscape
┌────────────────────────────┐         ┌───────────────────────────────────────────────┐
│ Book  Chronicle Journal …  │ head    │ Book  Chronicle  Journal  Done  (the Book's)  │
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
│ └────────────────────────┘ │         │                      Prev   Next              │
│ Close        Prev   Next   │ actions └───────────────────────────────────────────────┘
└────────────────────────────┘
```

- **The way in.** From its first page on (a written day or an entry), the journal is the Book's Journal page (The
  Book), and the book leaves the chips. Its page button and the Book's tab carry the quiet dot (`.new-dot`) while
  something written is unread (a note, or a day after the save's newest day read) and at no other time, so a new
  entry dots them through its notes. The Book's tab glows only as its lesson's step.
- **The page's frame** is the Book's: its head, then the Book's actions row with `Contents`, `Prev`, the open page's
  place in its section ("3 / 9") and `Next` after the phone sheet's Close (`ui.close`) at the right end, under the thumb
  (on a desktop, centred under the spread, after it and never over it). The buttons are `.quiet` at 44 px (no step here
  is the obvious next one, so none is `.primary`); `Prev` is off on the first page and `Next` on the last, never
  hidden, so neither moves. ← and → turn pages while it is open. It opens on the first page holding something unread,
  else the page last shown in this page session, else the first. Pages run by section: the days pages (below), then
  creatures and places in content order, one per entry written.
- **Prev and Next stay in the section.** At a section's last page `Next` is worded by the next section's bookmark
  (`Creatures ›`), and at its first page `Prev` by the one before (`‹ Days`): the one way across, and it says where it
  goes. Nothing is skipped: the book still runs page by page from first to last.
- **The contents** (`ui.journal.contents`, the button after Close) swaps the page for the open section's pages as rows
  in the parchment, in book order: a number, a title and the quiet dot while the page holds something unread; the open
  page's row is marked and scrolled to. A days page is titled by the day it begins on (`ui.journal.day`), an entry's
  page by the words of its first note (the entries have no title of their own). A row turns to its page; the button
  turns back; a bookmark lists its section while the list is open. Listing reads nothing: only pages turned to count as
  read. The list scrolls inside its own box, so the head, the bookmarks and the actions stay put, and the bookmarks
  row scrolls sideways, the open section kept in view, if the sections outgrow the width.
- **The days pages** hold the written days (`docs/design/journal.md`, "What the page draws"): each day's notes under
  its heading (`ui.journal.day`, in the hand at the notes' size, in `--hand-pencil`), days running on down a page; a
  note that does not fit starts a new page, headed again by its day, so a day still being written runs on over the
  page instead of leaving it. Whether a note fits is counted in rows of the hand at the desktop page's width (`game/book/days.ts`: a page holds 22 rows of about 46 characters, a note's drawing
  five), never measured from the window, so the same days are the same pages on a phone and a desktop. The measure is
  a little under what the desktop page holds at 1440×900, so a full page fits it unscrolled; elsewhere the page
  scrolls as any long page does. A days page has no sketch and no numbers, and is seeded by its first day.
- **The bookmarks** are a row of the panel's tab buttons (`.tabs`, `.tab`, `.on`) under the Book's head, in a `nav`
  labelled `ui.journal.heading`: one per section that has a page written (`ui.journal.days`, `.creatures`, `.places`), none for
  a section with no page. Each is a button, so Tab and Enter reach it. A bookmark turns to its section's first page with
  an unread note, else its latest page; the open page's section's bookmark is marked `.on` and `aria-current`.
- **The page** is parchment, written in the hand's ink: three tokens added to `:root`, the only new ones, since no
  sibling draws ink on paper. Their values are the ones the sketch method draws with
  (`docs/research/sketch-test/process.md`): `--parchment: #e6dcc6`, `--hand-ink: #2b241c`, and `--hand-pencil:
  #645d52`, the ink lightened only as far as 4.5:1 on the parchment holds (`tests/client/test_client_contrast.py` checks
  all three). Round the page is the sheet's raised surface and shadow.
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
  (`100dvh`, under the safe area) while the Journal is open. Top to bottom: the sketch, the notes, the numbers. A long
  page scrolls between the Book's sticky head and actions, as a tall sheet does.
- **Desktop, and a phone in landscape** (the desktop query): an open spread, centred. The left page holds the sketch
  alone; the right page the notes, then the numbers at its foot (`decisions.md`: the sketch page on the left,
  numbers and lore on the right). The gutter between them is a shade of `--hand-ink` at 12% fading into each page.
  Both pages are the largest 600:780 boxes two of which fit in 94% of the window's height less 8.5rem of head and
  actions (and in 96% of its width), so the spread and its Prev and Next fit at 1280×720 and grow on a 4K screen with
  the rem-sized text. A right page whose notes run past its
  height scrolls inside itself, the numbers staying at its foot.
- **Seeded per entry.** The page's draws come from the seeded draw `game/ledger/fights.ts` uses, keyed by "journal", the
  entry id (a days page's first day) and the part, never the save, so a page looks the same in every game and on every device and differs from
  its neighbours. The seed sets the sketch's width (86–100% of its box) and its offset in the space left over (on the
  left page, its height too); on a phone, whether the first note sits above the sketch (35%, the method's "caption on
  top"); each note's tilt (−2° to +1°, half the method's range, since live text must stay easy to read) and indent
  (0–1.5rem), a note after the first indented further as one written later (the method's `later`). A note's draws are
  keyed by its index, so one written later leaves the earlier notes' draws alone. The seed never changes the text's
  size, the order or what shows.
- **Turning a page** is an answer to a touch, below the ladder: the new page slides 0.5rem in from the side turned
  toward and fades in over 150 ms; under reduced motion it is swapped at once.
- **Reading writes nothing.** Opening the sheet and turning pages send no request. The notes of every page the player
  turned to (the page it opened on counts) go as read in one presentation write when it closes (`contract/journal.txt`,
  "JOURNAL"), so the dot clears by the player's taps, never by time.
- **Its first use is its lesson** (Lessons): the button is the trigger and the first step.

