## Desktop (wider than about 64rem)

```
┌────────────┬──────────────────────────────────────┬──────────────────────────────┐
│ Tasks      │ Camp 1 ▓▓▓░ next…   ❄ cold  ◐ hungry │ HANDS [ Gather ▓▓▓|Scav ▓▓ ] │  hands strip
│ Town       │ the aim, one line                    │ Mixes ▾ Main  runs on   Edit │
│ Rules      │ ┌──────────────────────────────────┐ ├──────────────────────────────┤
│ Book       │ │        SCENE (the artwork)       │ │ the shown ask                │
│            │ └──────────────────────────────────┘ │ ┌──────────┐ ┌──────────┐    │
│ Foraging 2 │ NEWEST LINE, whole (the strip)       │ │ card     │ │ card     │    │  the open tab's panel:
│ ▓▓▓░░░     ├──────────────────────────────────────┤ └──────────┘ └──────────┘    │  Tasks, or Rules
│ Firecraft 1│ LEDGER (a tall window)               │                              │
│            │ dry wood 2  −6/h  empty 20m          │ LEDGER (a short window)      │
│ Feedback   │                                      │                              │
└────────────┴──────────────────────────────────────┴──────────────────────────────┘
```

Three columns (`docs/design/redesign.md`, "Desktop frame"). **The left rail** holds the panel's tabs, Tasks, the town
(named by `ui.town.title`, as its heading is), Rules and Book (`ui/tabs.ts`: the same row the phone shows as its bottom bar), then the skills, and the panel's quiet text
buttons at its foot (`ui/partseat.ts` seats each by frame). Town and Rules keep their slots unseen until they arrive, as
on the phone, so nothing in the rail moves. The rail never lists a person's jobs. Book is a view like Town (The Book).

The middle reads top to bottom: the aim, the art with the Camp bar and chips in a dark row along its top (off the art
until it holds a chip or the Camp bar), then the story strip at its foot, right where the column meets the panel's
cards. The strip spans the art's width, so the longest line takes fewer rows here than on a phone. Only this scene keeps
a frame.

On a tall desktop window the ledger sits in a block under the strip. Until it has something to show (it comes with the
fire) the block is not drawn, but its room is kept: the art is sized from the column's height less the aim, the strip
and that room, as large as its width allows. So the art and the strip sit where they will stay, with the empty room
under the strip, and the block's arrival, like a line's or a tap's, moves nothing (over a larger first screen that
shrinks once). On a short window the ledger sits at the panel's foot.

The right column is the hands' own: the hands strip, the shown ask, and the open tab's panel (Tasks or Rules); the mix
editor takes the panel's place. Town is a view of its own (below): it takes the middle and the right.

Once the stool is built the figure does its jobs (knap, roast, read) sat on it, facing the fire; before, it kneels at
the fire's left. The scene manifest says so with an all-of condition (`running:read_by_fire&feature:stool`).

A trip is away from the scene like any job that takes the figure off the stool: its card id is listed in `tools/scene/trips.py`,
so the seated figure gives way while the hands tap it and for its share of each cycle while the mix runs it. Its completions go
to the chronicle alone and its finds to the chronicle's Finds, as an uncapped card's and a trigger's lines already do.

## Phone

```
┌────────────────────────────┐
│ Camp 1 ▓▓░        ❄ cold   │  the head: Camp bar, goals, chips
│ the aim, one line          │  (scroll away with the page)
│SCENE, edge to edge         │  the art: on Town only
├────────────────────────────┤
│ newest lines, three rows   │  the strip
├────────────────────────────┤
│ [Gather ▓▓▓|Scav ▓▓] Main ▾│  the mix's bar and name
│ ■ Gather 60% ■ Scav 40%    │  and its legend
├────────────────────────────┤  ── pinned above, scrolls below
│ runs on  while …      Edit │  the mix's controls
│ Wood  +2/min  18/18 full   │  the red and full lines it feeds
│ [L][M] Bank the fire… 1 ›  │  the shown ask, one 56px row
│ ┌──────────┐┌──────────┐   │
│ │ card     ││ card     │   │  the open tab's panel
│ └──────────┘└──────────┘   │
├────────────────────────────┤
│ Tasks  Town  Rules  Book   │  the bottom bar
└────────────────────────────┘
```

Read in the top half, touch in the bottom. Only the strip and the mix's bar stay pinned while the panel scrolls under
them, so the newest lines and what the hands run stay on screen while the thumb is on a card. The head and the aim sit
above the strip in the stage and scroll away with the page, back at its top (`ui/story/headseat.ts` measures the stage and the
strip, `--scene-vh` and `--stage-pin`; the stage is sticky at the strip's height less its own). The art is the Town tab's:
on Tasks the cards get its room. It covers a room of `--scene-h` edge to edge, cut top and bottom around what the view
shows (`scene/crop.ts`, the front page's placement at a cover scale); the strip is three rows (above), and the head keeps
room for a chip and its cost line. Of the hands strip only the bar, its legend and the mix's name stay pinned; the name
is the way to the Mixes list (`Main ▾`). The rest of its controls (runs, the rule's link, Edit) sit right under the pin
and arrive with the strip, and under them the ledger's red and full lines, beside the mix that feeds them; the lessons
that point at the controls find them there. At 390 wide the pinned part is about 145px once scrolled, a little more when
a legend takes two rows. Rejected: the head, art and strip all pinned (at day 17 the head's goals, chip and Bonuses held
it at about 540px of an 844px screen, and nothing capped it as content grew).

The panel's tabs are the bottom bar (`ui/tabs.ts`): **Tasks**, **Town** (the town's people and lanes, then the ledger
and skills), **Rules** and **Book**. Town and Rules keep their slots unseen until they arrive, so nothing moves; a tab
chosen while the panel is scrolled starts at its top under the stage. Book opens the Book as a sheet (The Book).
Anything opened only sometimes (an ask, the Mixes list, the Book, a prestige) rises from the bottom as a sheet across
the screen's width; the Book's sheet takes the full height while its Journal page is open. The mix and rule editors fill
the room under the strip, over the mix's bar (the mix editor draws its own), and the head steps aside with the art while
an editor or the Rules tab has the screen. The mix editor's store rows carry what each store holds of its cap beside
its rate now → after and where it heads, the ledger's figures a desktop shows beside the editor.

The shown ask is one row of fixed height (56px): who asks by face, the question cut to one line, and how many wait
(`1 ›`). A tap anywhere on it opens the sheet of every open ask, whole, so a season's several asks never move the
cards. Rejected: keeping the whole ask in the slot (it pushed the cards below the thumb's half); the hands strip's whole
controls row pinned (it held the stage at about 420px for controls used now and then); a grab handle on the sheets (it
promises a swipe that does nothing). In landscape the phone uses the desktop's two columns with the tabs as a row over
the cards, and no rail.

