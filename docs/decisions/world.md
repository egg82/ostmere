# Living world and maps

What there is to watch, the maps, and the art.

## Something to watch, any time, for hours

The salon case (2026-10-10: hours in a chair, bored, needing to stay aware of the room, so no audiobooks). Opening it
any time gives something if you look long enough:
- **Something to watch:** habits' living world, townsfolk going about their day, chatter, visitors, small scenes
  that come and go (Johnny Castaway): a fish tank where staring is rewarded with small things to notice.
- **Something to read:** the chronicle, lore in items and places, people's lines.
- **Something to think about:** tuning mixes and orders, planning the next project; thinking never runs out.
- **Progress visibly ticks while you watch:** bars creep, counters roll, stores fill in real time, not only as a
  total on the next open (looking at progress is nice too).
- **Silent and glanceable:** sound optional, one-handed, interruptible any second with nothing lost.
- **Watching earns nothing extra:** three hours staring equals three hours in a pocket (the 2 AM test).

This is one reason for the art (below, "Art: a drawn, living town over bars"): bars can't be stared at for hours, a
living town can, with habits' people moving in it (so more of its spatial layer comes along) and bars for the mix
and numbers.

## A world map

A Tolkien front-of-the-book map: where you are and where things are relative to you (Melvor's geography, wanted
here). Two scales: the world map reveals as you expand and explore, names appearing as you reach them; the town map
fills in as you build. Built from engraved stamps (Widman, `docs/research/art-sourcing.md`) placed by code: stamps
never overlap and never repeat until the pool is used, and labels go in clear space beside their place with a dark
halo, never over another stamp.

## Art: a drawn, living town over bars

A drawn town on top with bars for the numbers below, plus a Tolkien map screen; bars alone can't be watched for
hours, a living town can. The tiles are the Time Fantasy packs (bought, not in the repo) that
habits doesn't use (Ashlands, Dark Dimension, Castle Catacomb, Caves and Mines, Farm and Fort, Monsters), graded
dark in code (cold desaturated palette, fog, real night with firelight, ash), with the chibi characters grimed in
code; so it shares habits' code but not its look. The night camp in the look test
(`docs/research/look-test/compose.py`) reads well after the recolor.

**Warm means yours**. What the player made or placed (wood they gathered, the rack, the stool, the
fire, later every building) carries a warm palette; the world they found (the ruin, its old beams, the ground) stays
cool and neutral, never muddy one-hue brown. So a glance tells what the player did, and as the town grows it reads
against the ruin. The fire is the warmest thing on screen. The interface keeps the rule with ember's two jobs: filled
is yours and moving (a running bar, the primary button), and an outline needs you now, on one thing at a time. Only
the scene has a frame; everything else sits on hairlines, and a control lifts onto a raised surface with a shadow.
No text sits inside a mix's split bar: its labels go in a legend beneath it (the Mixes list's small bars still carry each task's initial). The six mix hues are muted and none is ember, each
3:1 against the page, and neighbouring segments sit apart on a gap of the page.

Type: IM Fell English SC for the camp level and view titles only, Alegreya Sans for everything else in four sizes
(meta, body, story, display), Reenie Beanie (Google Fonts, OFL) for the journal's handwriting. It reads a little worse
than Caveat but looks like a real hand, and the journal's handwriting is flavour: its numbers sit in Alegreya Sans.

Map stamps, journal sketches and icons are sourced art, never drawn by Claude: the hand-drawn placeholders in the
design canvas "you can definitely tell". Candidates: `docs/research/art-sourcing.md`. **The journal sketches
are make-or-break**: dozens of entries in one hand and one pen, invented creatures included, found or
commissioned and drawn very well; a mixed or mediocre set sinks the journal. The style is a field sketch, not a
finished plate (an engraving reads "too pristine and careful"; Gravity Falls' Journal 3 got it right): quick,
loose, uneven lines, side studies, arrows and scribbled labels, a crossed-out first try. Its words are field notes
to match: lowercase fragments jotted at different times, a later line added under an earlier one ("took the goat
first" / "haven't come back for goat since"), never composed sentences. Mostly mundane observation (sizes,
times, counts, guesses); at most one ominous note per page. Every page differs in layout (where the drawing, side
studies, crossed-out tries and notes sit, and how many), seeded per entry. The page is laid out for the screen it
is shown on: a portrait page filling the phone screen with the learned numbers below; on desktop an open journal,
the sketch page on the left, numbers and lore on the right. The page around the drawing (notes, arrows,
a crossed-out first guess, measurements, the learned numbers) is laid out by code in the Reenie Beanie hand and grows as
you learn; a code-drawn test page got this part right. The creature drawings are code-drawn for now,
by the method in `docs/research/sketch-test/process.md` (construction drawing, hand-wobbled shapes, notes as data,
seeded layouts), judged good enough on 2026-10-11. Each new entry is looked at before it ships;
commissioned art replaces whatever keeps slipping (chunky bodies and comic shapes did), and swaps in without
touching the page around it.

## The chronicle and unwrap, as built

How the chronicle stands today, moved from its row in `systems.md`. The unwrap cursor lives in the presentation store.

- **One record, one home per kind.** Every line the game writes, each rule's start and let-go and each fight goes to
  the chronicle, a sheet opened from the button beside the chips (`app/client/src/ui/chroniclesheet.ts`). Each kind
  has one filter (`app/client/src/game/chronicle.ts`, `ROUTES`): story, taps and the body's lines
  under Story; finds, levels, rules and fights each under their own; town talk under its own, ready for the living
  world. The story strip on the main screen holds the Story filter's kinds and nothing else, so a find, a level, a
  rule or a fight never lands there, and town talk never will. A filter is offered once it has an entry, Story first
  and All last; under Story a stretch ends with its counts of the other filters, each opening its filter. Each filter
  keeps its own newest 200, so a busy kind never pushes out a quiet one's.
- **Coming back opens a chapter.** The chronicle runs newest first, and the newest return's stretch is "Since you
  left" (`app/client/src/ui/chapter.ts`): never folded, its lines with their causes, then under Story its figures as
  rows, each only when it has something: stores gained and lost, levels old → new (the Camp's first), the rules that
  ran, and how many asks wait now, linked to them. Figures, not sentences: a death or a fall stays a story line in the
  chapter, never a count in a row. The figures are taken once, as the return lands (`app/client/src/game/chapter.ts`),
  against the view the player left, and kept with the visit (`SavePresentation.chapter`), so a reload keeps them; a
  return from before they were kept shows its lines and claims no figures. Later systems add rows (people, seasons,
  fights) the same way. Rejected: a figures entry on every visit, which would put a few hundred bytes per return into
  every presentation write; and opening the chronicle by itself on a return, which would cover the strip's replay.
- **Every line says what caused it**, as "↳" and a few words under it: the card or fight that wrote it, the store,
  level or count a beat waited on, the Camp level, the player's answer. The cause is served beside the line's kind
  (`app/ashfall_app/api/line_causes.py`; `app/ashfall_app/api/CONTRACT.txt`, "Line causes"), read from where the
  content authors the key, and never parsed from the line. A key is written in one place, or by several levels of one
  skill (a phase's pool), whose cause is the skill alone since the key cannot say which level; any other sharing
  fails the content's load. A rule's entry takes the store's level when it came on or let go; a fight's line from a
  runner's pool takes the runner, while ui.fight.* lines already name it. Rejected: putting the trigger's id on each
  engine line, which would say exactly which level wrote a pool line but needs a new column on stored lines for a
  history's sake.
- The page's arrival queue (`app/client/src/game/arrivals.ts`) reveals what a return brings in turn and, live, each
  story line before what it announces.
- What the rules did lately: the engine's rule changes (`app/ashfall_app/engine/rulelog.py`) kept per rule on the
  save's row (`app/ashfall_app/saves/ruleruns.py`), a goal stint's start and landing among them, with what the save
  gained in its mix's stores between the two, drawn at the foot of the Rules tab (`app/client/src/ui/rulelately.ts`)
  and as the chronicle's Rules entries (`app/client/src/game/rulerows.ts`). The record is a summary, so a start a later
  start replaced before any page saw it is not an entry.
- Fights since the last view, exactly as many lost as the engine's count, which ones picked by a shuffle-bag draw keyed
  by save, fight and window, each worded from its runner's pool of lines when the content gives one
  (`app/client/src/game/fights.ts`; `app/ashfall_app/api/CONTRACT.txt`, "FIGHTS").
- The visits record: each return after a long time away kept in the save's presentation, newest last and the oldest
  dropped past a limit (`app/client/src/game/keeps.ts`, `app/ashfall_app/accounts/presentation.py`), which the
  chronicle splits its stretches at, whatever the filter; beside it the newest return's figures, replaced only by a
  later return's.
