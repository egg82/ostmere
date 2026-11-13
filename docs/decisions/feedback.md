# Feedback

How the game answers the player: juice and its ceiling.

## Rewarding at any moment

The juice is per visit; the progress is per hour.
- Opening the app unwraps what happened since the last visit.
- Lots of juice whatever the art style (Idle Fantasy has none): bars that fill with sparkle, level-ups that burst,
  collections that pour in, sound on every reward, a rare golden flourish, ceremonies for big moments. habits'
  tap ladder and reward sounds are a head start.
- **Juice is everywhere, not only in rewards:** every interaction feels good to touch. Dragging a share, a ledger
  line snapping to its target, saving a block, handing a guard their spear, turning a journal page each get a small
  tactile response (a click, a settle, a bounce); big moments get more, nothing touched feels dead.
- **Juice has a ceiling, written as a ladder** (from `research/design-101.md`): each kind of event
  has one fixed effect sized by how much it matters, and an effect never grows on repeats. A completion by the mix or a
  rule sits one step below the same completion from a tap, so a tap stays special and a mix running alone still shows
  what it did. The evidence: medium juice beat none and extreme, and making the same feedback bigger lowered players'
  sense of competence, while feedback that said whether their action worked raised it.
- **Motion, flash, sound and reach rule** (from `research/a11y-audit.md`):
  motion honours the OS reduced-motion preference everywhere, and every effect has a still form that says the same
  thing (the OS preference is the switch; the game has no motion toggle of its own). Nothing flashes more than 3 times
  a second. Sound never carries information alone (the game has no sound today). No meaning is reachable only by hover.
  Every control's hit area is at least 24 CSS px, or passes WCAG 2.5.8's spacing test, and the primary taps (cards,
  Show me, Save) are 44 px. Colour is never the only cue: a state shown by hue also differs in weight, mark or lightness.
- Juice reference: Leaf Blower Revolution ("holy crap satisfying"), many small things reacting to you at once,
  scattered and collected.
- Taps play out content that idle time produced (an encounter, a dig, a mini-story beat), never raw per-tap
  currency, so tapping more never becomes optimal. A tap bonus, if any, scales with time away.
- Something is ready at every timescale: cheap buys in seconds to minutes, choices in hours, unlocks and big steps in
  days.

## Feedback and lessons, as built

How these stand today, moved from their rows in `systems.md`.

Feedback: null is silent. The ladder (`docs/design/opening-screen.md`, "The feedback ladder") is data in
`app/client/src/ui/ladder.ts`: event kind to rung to effect. A failed tap (`api.models.Step`, its failed_tap) pulses its
card red and the need that stopped it (`app/client/src/ui/cards.ts`); the effect's numbers are tokens in
`app/client/src/game.css`. **A refused tap never has text**: the engine emits no line for it and the content has no
refusal lines. A tap that lands puts its line in the strip and the chronicle, never under the card, so each tap outcome
has one home.

Lessons: lessons as data (id, when it may start, trigger, steps naming a control and a line) and one runner, the glow
as its highlight (`app/client/src/game/lessons.ts`, `app/client/src/ui/lessons.ts`). Done or skipped is kept in the
save (SavePresentation); the account's setting turns lessons off (AccountSettings). Not a system: one caller, nothing
to swap.
