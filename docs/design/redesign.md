# The redesign

Open-work item 25. Every in-game screen gets a new look and a new feedback language. The front page stays as it
is, restyled only to match. The design is `redesign/merge.html` in this directory; open it in a browser. It was
chosen from six competing designs (comparison: https://claude.ai/artifact/3zBFvQDBec1J6UWPqCuc6s). This note is what
the build follows where the page and this note differ. Mechanics only: no content, card or beat specifics.

## Why

The owner, playing at camp level 9: everything is "fine enough" but "off", "too big", "too crowded" and "doesn't
feel good". Underneath that there are three defects:

- **Evenly loud.** Every panel is a bevelled box with an ember rim, and type comes in many sizes, so nothing gets
  read first.
- **Every message in two places.** A tap's result shows under the card and in the log at once ("weird", "gets in
  the way").
- **No causes.** An offer or an arrival appears with nothing saying what led to it ("nothing in the app anywhere
  tells me what happened or what I missed").

And the part that was missing: it should be *fun to interact with*, grimdark or not.

## The design

Each part is tagged on the page with the competing design it came from.

- **Look.** Only the scene keeps a frame. Every other group sits on hairlines as aligned rows, in four type sizes,
  with IM Fell English SC for the camp level and view titles only and Alegreya Sans for everything else. Ember has
  two jobs: filled means yours and moving; an outline means it needs you now, and only one thing on screen has
  it.
- **One record.** A chronicle replaces the story strip's history, the Log and the line under a card. It can be
  filtered by kind (story, finds, levels, rules, town talk). Each line carries "↳" and what caused it, and
  coming back opens a "Since you left" chapter. The main screen's strip shows story lines only; town talk never
  enters it.
- **Desktop frame.** A left rail holds Tasks, Town, Rules and Book, then the skills. The scene and strip sit in
  the middle and the cards on the right. The rail never lists a person's jobs, and the town has a view of its own:
  Town takes the middle and the right, the town's people and lanes in one home.
- **Phone frame.** The pinned stage is about 380px: the camp bar, the scene edge to edge, a strip three lines tall,
  and the mix bar with its legend beneath it (no text inside a bar, ever) and the mix's name beside it (`Main ▾`);
  the mix's other controls scroll just under it. Cards sit in the thumb's half, a bottom bar holds Tasks, Town,
  Rules and Book, and anything set up only sometimes opens as a sheet from the bottom. Under Town sit the town's
  people and lanes, then the ledger and skills.
- **Book.** It holds the Chronicle, the Journal, Done (the finished cards) and, later, the Map. **The journal
  pages are kept exactly as they are:** the parchment, the handwriting, the drawings. They are the lore and story
  layer and the one deliberate exception to the quiet look (the only light surface, like a book opened by the
  fire). The page never draws one; the build keeps `ui/journal.ts`'s rendering.
- **Asks.** A list, one shown at a fixed height, with a count of the rest. Each ask shows who asks, "↳" what led
  to it, and each answer as before → after figures.
- **Ledger.** Grouped into yours, town, outposts and threats, each group appearing when its first row does. A row
  turns red only when its store is falling with nothing covering it.
- **Feel.** On pointer-down a card sinks 2px onto its shadow, and it settles in 160ms on release. A level shows its
  bonus on the card it speeds up (old → new). A chain sets off its links one by one, about 90ms apart, so the eye
  can follow the cascade. Reduced motion keeps every state and drops the movement.

## Routing: one home per message

- **A refused tap:** the card goes red, and what's missing is highlighted in its need line (flint 2/4). No text,
  ever. The refusal lines in the content retire.
- **A successful tap:** a story line in the strip and the chronicle, never under the card.
- **Humour** lands on choices: answering an ask, or picking one thing before another (the day-one order of builds
  keeps its dry line). It never lands on a refusal.
- **Later event kinds** have rows from the start: someone arriving or leaving, a season turning, a building
  falling, a fight resolving, a prestige, town talk (chronicle only, under its own filter). The page's routing
  table lists them.

## Words

- **Only what breaks an expectation gets words**, whether the game or the genre set that expectation. An ask
  says nothing about waiting, expiry or permanence unless this ask differs from the usual. Those three facts are
  fields on the offer's content, read by the page, and never a fixed line in the UI.
- **That rule cuts words, never knowledge** (`decisions.md`, "What the mods added is built in"). What you get and
  spend stays readable at a glance as figures: rates, percents, counts, times. Prefer a figure to a sentence,
  and never drop a figure to save space.
- The page's copy is placeholder. Every player-facing string in the build goes through the `writing-craft`
  skill, and a line that repeats what the visuals or the story already say is cut.

## Fit

Nothing here is a new system. The look is game.css's tokens and type, cut down. The record is Chronicle and
unwrap (`systems.md`), widened to replace the Log and filtered by kind. The causes are a field on what the
chronicle already records. Routing is the feedback ladder (`decisions.md`, "Rewarding at any moment") with one
home per rung. The asks are Offers with three new optional content fields. The rail, the bottom bar and the
landscape row are three forms of `ui/tabs.ts`'s one row of tabs, and the Town view is that row's Town panel, holding
the town strip and lane rows moved off the main screen. Decisions get rewritten as each part ships, in the same PR, because they say how
the game works now.

## Build order

One surface per PR, smallest first. Each step is playable on its own:

1. Routing: refused taps go red and highlight the missing need with no text; success goes to the strip only. Retire
   the refusal lines. Start by finding every place a tap's outcome is drawn today (the card's note line, the log,
   toasts), so each outcome ends with exactly one home.
2. The look: tokens, type scale, hairlines in place of rims and bevels, ember's two jobs. No layout change yet.
3. The mix bar's legend, and the ledger as grouped rows.
4. The chronicle replaces the Log, with causes and the kind filter. Then "Since you left".
5. Asks as a list, with the three content fields.
6. The phone frame: pinned stage, bottom bar, sheets.
7. The desktop rail, and the Town view.
8. Book, with its journal pages untouched, Done and a slot for the Map.
9. Feel: press, settle, level-on-card, cascade.

Before each step, check the layout against the later systems (`decisions.md`; the scale check behind this note
found the right column and a single ask slot were what broke first), not against week one alone.
