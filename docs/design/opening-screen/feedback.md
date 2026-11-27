## Dots and the one glow

- **A dot** is small and quiet (no number, no pulse). It marks only a control the player can act on and has not yet: a
  new task card, a new Add entry in the mix editor, the Journal's page button and Book while a note is unread (cleared
  note by note as the player turns to its page). Plain text never gets one: story lines, the book while it is text, chips,
  ledger lines, skill rows, needs, labels, headings, mix segments. It clears when the player interacts with the thing
  (a tap, a drag, a key) and when the thing is put to work: joined to a mix (in the editor or by Both), running, held
  by any saved mix, or named by a rule. A task already at work never shows a dot. Never cleared by being seen or by
  time, and it never counts anything. Book takes one too, while a line it holds left the strip before the player touched
  anything after it showed; it clears when Book is touched. So does Town, when a person or a lane arrives while
  another tab is open.
- **The glow** points at the one obvious next step, only when there truly is one, and only one at a time. In the
  opening: the first card; the first mix offer (`Both`); the first strike when everything it needs is in. Whenever
  the running mix greys (a task in it retired or completed): the strip's `Edit`, until the editor is opened. After
  the end: the strip's first-rule entry (`Show me`, the first time it is on show, after a return's reveal has shown it);
  the first `When ready`; and the shown ask, on arrival. Switching mixes when a build waits on a store nothing at
  work makes is a lesson ("Lessons", below), not a glow.
  A player who has touched nothing for a while (`NUDGE_IDLE_S`) while no mix runs is pointed at the first ready card they
  have never completed, with the same glow, when nothing else has it. When no card is ready at all and the next thing is a timer card more than 10 minutes out (the opening's
  end), the same nudge goes to that card, so the eye lands on its countdown.
  The Rules tab's label, once the page has seen a rule come on and let go (when `+ New rule` opens), until the tab is
  first opened (remembered in the browser, across new games); before that the label is there without it. A rule just
  added from an offer flies to that label. A glow that is due while another control holds it, or while the
  reveal holds its control back, waits, with one exception: a story step the content marks (`glows`) takes the glow
  from the shown ask, which keeps its outline, so an ask left unanswered for days never keeps the step that moves the
  story on from glowing. Nothing else glows, and nothing pulses for urgency.

## The feedback ladder

Fits into: Feedback (`systems.md`).

Each kind of event has one fixed effect, sized by how much it matters (`decisions.md`, "Juice has a ceiling, written
as a ladder"). Nothing grows when its event repeats: a card's tenth completion looks like its first. The rungs are data
in `app/client/src/ui/feedback/ladder.ts`, their sizes keyframes in `app/client/src/game.css`. Lowest first:

| Rung | When | Effect | Under reduced motion |
|---|---|---|---|
| Background | A card completes by the mix or a rule | "+1" rising off the card | "+1" held still on the card, then gone |
| Tap | A card completes from the player's tap, a queued one (Next) included | "+1" and a ring spreading from the card | "+1" held still and a still ring, fading |
| First | Something new arrives: a card, chip, skill row, ledger line, feature | The arrive pulse, and a dot if it can be acted on | Shown at once, with its dot |
| Level | A skill or the Camp reaches a level | The burst: a wider, longer ring, the row lit; each card the level speeds up reads its old → new time for 2 s on an ember wash | A still ring, the row lit, fading; the card's line the same |
| Big | The end; a feature's card | Its lines in the strip, the scene to dusk; the card docks ("The end", "A feature's card") | The same: neither moves |

- **A rule's completion sits with the mix's**, one rung below the same completion from a tap, so a tap stays special
  and a mix or rule running alone still shows what it did. A rule's run is a tap the page did not send, started by a
  standing order (`app/client/src/ui/cards/fires.ts`, the card's by-order dot).
- **The level on its card:** the cards a level makes faster are LevelPays.speeds, and only one whose speed rose shows
  it. Its foot reads the skill, the level and one whole completion's time at the old and the new speed
  (`ui.card.levelled`); under a minute the times keep the decimals that tell them apart (5 s → 4.5 s). Each time is
  unbroken, and two lines fit the foot, so the card never grows.
- **Below the ladder, answers to a touch or a change of state**, each no bigger than the background rung: a pressed
  card sinks 2px onto its shadow, a step lighter, in 60 ms, and settles in 160 ms with a slight overshoot when the
  pointer lets go (a refused card too; one that cannot be tapped stays put; under reduced motion it only lightens); a
  failed tap pulses red on its card and blocker (colour, kept under reduced motion); a share divider or a ledger line
  coming back from red settles; a rule row that just started a card lights (colour, kept under reduced motion); an
  accepted rule offer flies to the Rules tab (under reduced motion the tab only takes its dot); a journal page turned
  slides in (The journal; swapped at once under reduced motion).
- **No sound yet.** When sounds come, each rung gets one, fixed like its effect, and none carries information alone.

