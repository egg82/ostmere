# Motion, sound, hit-area and phone audit

The failure list asked for by proposal 7 in `design-101.md` (§3), before any rule is designed. Nothing here changes code
or `decisions.md`. Screenshots are kept outside the repo (names below are
relative to their folder). Controls are named by class, never by their words.

**Method.** The client's own fixture build (`node build.mjs --fixtures`, `app/client/fixtures/`) served statically and
driven by Playwright 1.56 Chromium in one `--cpus=2` container (`mcr.microsoft.com/playwright:v1.56.0-noble`), phone
390x844 with touch, `document.visibilityState === "visible"` asserted before every shot, 7 s settle per state (the
reveal queue holds the hands strip and ledger back for several seconds; 2.5 s shots missed them). States reached:
first screen, after Begin, first-mix offer, mid game (Tasks tab), the Mixes sheet, the mix editor, the Rules tab (both
a lone rule and three rules), the condition editor, the mix picker, a ledger line, the strip's rule link, the devices
and games sheets. Harness: `pw/` in the shots directory.

**Not a real build.** The server, database and art volume were not run: the scene is the fixture's placeholder
rectangles and the text is fixture text. Layout, CSS, hit boxes and client code are the real ones; art, real server
timing and real lesson sequencing are not.

## 1. Reduced motion (4 failures, 1 weak)

The `@media (prefers-reduced-motion)` block (`game.css:692-699`) zeroes CSS animation and transition inside `.game`
and keeps colour or still forms for the failed tap, the ladder ring, the burst and the fired rule. Confirmed by
computed style under emulation (`pw/rm.mjs`): `arrive`, `press`, `pop` become `none`; `landed`, `burst`, `fail-mark`
become their still forms. `Flight` (`ui/flight.ts:19`), the reveal queue (`ui/reveal.ts:83`) and the self-update fade
(`app/selfupdate.ts:128`) read the preference themselves. A tap under reduce changes only the card's progress and the
log line; nothing else says "your tap landed" (weak, not a failure: the state change is visible).

Failures:

1. **The scene's fades ignore the preference.** `scene/scene.ts` eases the grade and layer fades in JS (`GRADE_S`
   2.5 s, per-grade `ease_s`, `:161`); no `matchMedia` exists under `scene/`. Dusk and the fire's arrival
   still fade in over seconds. Not a motion-alone failure (the end state is the information), but the preference is
   not honoured.
2. **The front page's glimpse ignores it.** `ui/glimpse-scene.ts:56` cycles canned views with fades every `TURN_MS`;
   `ui/glimpse.ts:56` ticks the amount each second. Both run under reduce.
3. **The glimpse's `+N` cue has no still form.** `.g-pop` is `opacity: 0` with its animation as the only thing that
   shows it (`game.css:106`); the reduce block sets `animation: none` (`:693`) and does not replace it, so it never
   shows (computed: `animation none`, `opacity 0`). The cue relies on motion alone.
4. **Two fades sit outside `.game` and keep running:** `#begin`'s transitions (computed `0.25s, 0.15s` under reduce,
   `game.css:64`) and the `body.playing main` fade-out (`:115`).

Screenshots: `rm-front-reduce.png`, `rm-tap-reduce.png` (and `-no-preference` twins), every `a-*.png` is taken under
reduce. Not checked live: the failed-tap flash and ladder ring firing in a running session (read from CSS and
computed style only).

## 2. Hit areas under 44 CSS px (31 controls; 3 under 24)

Method: `button, a, [role], input, select, summary, [tabindex]` plus every element with `cursor: pointer` whose
ancestor is not already a target, visible and unoccluded, in 18 states (`audit.json`). WCAG 2.5.8 spacing test:
24 px circle on the box centre against every other target. Controls at or above 24 px pass 2.5.8 by size; the three
under 24 pass the spacing test (nothing within 12 px). Only the cards (`.card-tap`) reach 44.

Under 24 on the short side:

| Control | Box | Where |
|---|---|---|
| `#privacy a` (front page) | 42 x 15 | `index.html:63-64` |
| `#have details summary.head` | 330 x 17.3 | `game.css:72` |
| `#have summary` | 352 x 22.4 | `game.css:72` |

24 to 43.9, grouped by size (short side in px, selector, line):

- 27.6 `.quiet.lesson-skip` (`game.css:707`); 28.8 wide, 44 tall `.rule-handle` (`:562`); 28.8 wide `.share-divider` (`:252`,
  height 43 to 61).
- 30.4 `.log-open` (`:183`); 32 `.line-covered` (`:373`).
- 35.2 `.tab` (`:260`), `.hands-rule` (`:233`), `.entry-remove` (`:415`).
- 38.4 (2.4rem, the house button size) `.feedback-open`, `.devices-open`, `.games-open` (`:190`), `.hands-name`, `.hands-edit`,
  `.quiet` / `.quiet.danger` / `.quiet.selector-new` in sheets and editors, `.primary` / `.primary.glow`,
  `.offer-both`, `.editor-close` (`:405`), `.rule-slot`, `.rule-cond` / `.chip-rule`, `.editor-name`.
- 41.6 `.add-card` (`:428`).
- `input.sr` 9 x 7 in the devices sheet is a visually hidden field, listed by the probe and not a real target.

In CSS only, not on screen in these states: `.card-ready` (`:306`, 2rem = 32) and `.line-edit` (`:372`, 2rem = 32).

Screenshots: `a-<state>.png`; per-state counts in `audit.json` (`under44`).

## 3. Greyscale (4 things that do not read)

`filter: grayscale(1)` shots: `g-<state>.png`. Survives: the dot beside the running rule (`g-rulestab.png`, a grey disc
against the glow's ring: different shapes, still tell apart), the glow ring on the next-step control (`g-firstmix.png`),
the dashed mix slot versus solid rule chips, every label.

Does not read:

1. **The red ledger line.** In `g-mid-rules.png` the draining line's tint and red name become the same dim grey as any
   other text; what remains is the bold rate figure and the time-left bar. Only one ledger line exists in the fixture
   state, so no calm line was shot beside it for comparison; the claim is that nothing but colour marks it urgent.
2. **Mix hues.** The two task hues (blue-grey and mauve) on the strip chips and share bar render as the same grey
   (`g-firstmix.png`, `g-mix-editor.png`); the segment text tells them apart, the hue-to-card link is lost.
3. **Warm ownership on cards.** Running (warm brown) versus unmet (cool) cards differ by a few grey levels
   (`g-mid.png`); the left stripe is the same light grey on both. The dimmer title and need line still separate them.
4. **Warm rule chips.** The ember border on rule chips versus the plain border on the mix slot is a hue difference
   that reduces to brightness (`g-rulestab.png`); the dashed outline on the slot still separates them.

## 4. Hover-only (0 strict; 1 weak; 2 affordances)

Grep of `src/` and `game.css`: one `title=` (`ui/hands.ts:158`, the running mix's full name), no `mouseenter`,
`mouseover`, `pointerenter` or tooltip code, 14 `:hover` rule lines in `game.css`, all cosmetic.

- Weak: `.hands-mix-name` truncates with an ellipsis (`game.css:223`) and `title` carries the full name; on touch the
  full name is one tap away in the Mixes sheet (`mid-mixes-sheet`). `.rule-slot` truncates the same way with no `title`
  at all (`rulestab` shows it clipped).
- Affordance revealed by hover: `.feedback-open`, `.devices-open`, `.games-open` are borderless text until hovered
  (`game.css:190`, its own comment: "words only until it is hovered"); on touch they read as plain text, not buttons.
  `.share-divider::before` brightens on hover or focus only (`:254`).

## 5. Sound alone (0)

No audio exists in the client: no `AudioContext`, `new Audio`, `<audio>` or `.play(`. The only non-visual channel is
haptic, `navigator.vibrate(8)` in `tapFeedback()` (`ui/dom.ts:58`, called from `ui/editor.ts:138`, `ui/chipoffer.ts:60`),
and it carries no information. Chromium logs a blocked-vibrate error when it fires before the first user tap (seen in
the first-mix state). The "sound never carries information alone" rule is vacuous today.

## 6. Pinned stage (3 failures, 1 overlap)

The stage is 382 px tall at 390 wide (set from the art's aspect by `ui/headseat.ts:19`, not from the viewport) and the
hands strip pins under it at 96 px: **478 px pinned at every height**, 57% of 844. Measured (`stage.json`):

| Viewport height | Scrolling room under the pin | Condition editor choice area |
|---|---|---|
| 844 | 366 | 259 (`v-condeditor-844.png`) |
| 750 (address bar shown) | 272 | 165, foot visible (`v-condeditor-750.png`) |
| 520 | 42 | 29, foot below the fold (`v-condeditor-520.png`) |
| 420 | none: the pin (478) is taller than the viewport | 0 |

Nothing important leaves the screen between 844 and 750 in any state tried (`v-*-844.png`, `v-*-750.png`).

Failures when the layout viewport shrinks (a keyboard that resizes the layout, or a short window):

1. **Condition editor:** its remove and save buttons (`.cond-foot`, `game.css:550`) sit at y 520-614 on a 520 viewport,
   off screen, and the choice list is 29 px. From the rects the foot is fully visible only at about 585 or taller.
2. **Mix editor:** at 520 the name field and its save button are cut by the bottom edge (`v-mixeditor-520.png`);
   at 420 the editor is 37 px tall.
3. **Hands strip** is cut by the bottom edge at 420 (its bottom is at 478; `v-mixeditor-420.png`).

Corrections to the proposal's premise: the condition editor has **no text input** (only buttons), so it never raises a
keyboard. Keyboard cases in this client are the mix editor's name field (`ui/editor.ts:27`), the feedback textarea
(`ui/feedback.ts:15`) and the device code fields. The viewport meta (`index.html:5`) has no `interactive-widget`, so
Chromium on Android resizes only the visual viewport and the layout above would not shrink; iOS likewise. The shrink
test is the worst case for browsers that do resize the layout, not what Chrome or Safari do by default.

Overlap: with the mix editor open at 844 a lesson note (`.lesson-note`, fixed, `game.css:704`) sits over the editor's
second task row and its remove button (`g-mix-editor.png`, `v-mixeditor-844.png`). The fixture's lesson step points
at a control the editor has hidden, so whether the real lesson reaches this state is unchecked.

## 7. Flashes (0)

No animation above 3 Hz. Infinite animations exist only in the glimpse (`.g-fill`, `.g-pop`, periods 8 s and 12 s,
`ui/glimpse.ts:15`), one brief fade-in per period, small area. Everything else is one-shot: the failed-tap glow and
mark flash (`--fail-ms` 400 ms), `fired` 1.2 s, `landed` 0.7 s, `burst` 0.9 s. A failed tap restarts its 400 ms
flash on each tap, so repeated taps above 3 per second would repeat it, but the lit area is a single card's glow, far
under the general-flash area threshold. `document.getAnimations()` was empty at idle under reduce in every state.

## Could not check

- **A real build** (see Method): real art, the real fire, server-driven timing and the real lesson order.
- **A real virtual keyboard or address-bar collapse.** Playwright resizes the layout viewport; it does not reproduce
  `visualViewport` panning, the iOS keyboard, or browser chrome. Both were approximated by window height.
- **Safari/WebKit and Firefox.** Chromium only; the `100dvh` sheets and `env(safe-area-inset-bottom)` were not
  exercised on a device with a notch.
- **Screen-reader behaviour and focus order.** Out of scope for the seven checks.
- **The failed-tap and ladder effects firing live** under reduce; the end screen's card and the end dock (not reached by a
  fixture phase I ran).
- **Landscape and the wide layout.** Phone portrait only.
