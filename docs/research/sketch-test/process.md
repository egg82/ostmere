# Field-journal sketches: the method

This is how to produce a new journal entry (pen-and-ink field sketch on parchment, Journal 3 register) in the same hand as `wolf3`, `raven`, `boar`, `creature` and `creature2`. It is code-drawn: you write coordinates, render, look, and revise. At its best it gets to "nearing good enough". See *Limits*.

## Files

| File | What it is |
|---|---|
| `ink.py` | Tapered variable-width strokes as filled polygons; pseudo-3D shading from part masks |
| `sketch.py` | Searching multi-pass contours with overlap accents; partial hatching; arrows, scribble-outs; handwriting as glyph paths |
| `journal.py` | The construction method: hand-drawn ellipses, bones, masses → silhouettes, paws and hooves, `ear`, `feather_blade`/`feather_row`, `ink_figure`, and `Layout` (seeded page layout) |
| `notes/<subject>.json` | Every word on the page: caption, crossed-out note, study captions, labels with anchor points. A line is a string or `{"t", "struck", "later"}`: `struck` puts one pen line through it, `later` indents it at a different angle as if added afterwards. `"required": true` on a study or crossed entry makes it always appear. The drawing code authors no text |
| `wolf3.py` (saves `wolf.*`), `raven.py`, `boar.py`, `creature.py`, `creature2.py` | One script per subject, all on the full pipeline (`Layout` plus a notes file); copy the nearest one to start a new subject |
| `entry_<sketch>.py` | The game's journal entries, one per sketch id. `notes/entry_<sketch>.json` holds only words that point into the drawing (study and part labels; a crossed-out try with empty text): the entry's notes are game text. Its `entry_<sketch>_ink.png` is seeded onto the assets volume as `journal/<sketch>.png` by the cluster repo's `seed-assets-job.yaml` |
| `note_<sketch>.py` | A sketch on one of the game's journal notes (a note's `sketch`): small, no layout furniture and no words, its weights twice an entry's because the game shows it at under half an entry's size, recoloured to the note's hand (pencil `#645d52`). Its `note_<sketch>_ink.png` is seeded as `journal/<sketch>.png`, as an entry's is |
| `render.sh` | `bash render.sh <script> [round]` → `<out>.svg`, `<out>.png` (600px on parchment #e6dcc6), `<out>_ink.png` (1200px ink on transparent, for the game screen), and a copy under `rounds/`. `<out>` is `$OUT` if set (`OUT=wolf bash render.sh wolf3`), else the script name |

**Setup:** `pip install --target lib fonttools`. `fonts/ReenieBeanie.ttf` is OFL and comes from google/fonts.

`wolf3.py` pulls its page furniture from `wolf.py`, so keep that file alongside it.

## Steps, in order

1. **Measure a reference** before placing anything. Use a real drawing or photo (the Gessner woodcuts in `engravings/ref/`). Overlay a grid with PIL and read the ratios off it:
   - withers or shoulder height H;
   - body length (wolf about 1.15H);
   - chest depth (wolf about 0.5H, greyhound 0.43H);
   - head length (about 0.37H);
   - leg length below the chest;
   - which joints bend which way.

   Write the ratios as a comment at the top of the script. Every attempt drawn from memory read as a cartoon until it was checked against a reference.

   **Invented creatures** have no reference, so measure a previous page of the same creature if one exists. Otherwise borrow real analogues per body part (harvestman legs, a heron's hanging neck, a sow's sag) and write the ratios down the same way.
2. **Gesture first.** A line of action through nose, spine and tail, plus a ground line. Decide the pose (head low, weight forward) on this line, not later.
3. **Masses on the gesture**, drawn with `hand_ellipse` inside `pen.construction()`. Each one is flattened, tilted, egg-shaped, not quite closed or overshooting, and sometimes double-passed. Typical masses:
   - eggs for the ribcage or chest, and a smaller one for the pelvis or ham;
   - a box or wedge for the head and muzzle;
   - for limbs, a bone chain (`bones`) with joint dots.

   These stay faint (42% opacity) on the final page. That is what makes it read as a sketchbook.
4. **Silhouettes from the masses**, built with `mk(name, polys, close_r, z, …)`:
   - Pass ellipses, tubes, `limb(chain, widths, knuckles=…)`, and `paw(...)` or `hoof(...)`.
   - The morphological closing radius `close_r` makes the tangent bridges a draughtsman draws, such as the back line and belly tuck. Use about 16–22 for a trunk and 3–6 for limbs and heads.
   - **Add a connecting mass** (a loin tube) when two masses are too far apart to bridge.
   - **Never let one egg be a whole body.** A single ellipse reads as a bun. Use two or three overlapping, unequal masses (shoulders bigger than rear, a sag, a spine-ridge tube).
   - **Build the head from the neck.** Neck tube, skull ellipse and muzzle or jaw tubes go in the *same* `mk` as the trunk, so the contour flows from neck into head. A separate head part reads as a box pasted on top.
   - **Ears grow from the skull:** `ear(pen, base_a, base_b, tip)` with both base points inside the skull outline. It draws no base line.
5. **Layering (z):**
   - Far legs go lowest and get `tone` 0.3, so they print darker and with a lighter line.
   - **Near legs whose tops would show go *behind* the trunk** (z just under it). The belly line then overlaps them, the way an elbow does. A leg in front shows its top edge as a plank.
   - A thigh or wing that overlaps the body goes in front.
   - A near limb may cross in front of the head (higher z). The head must never cover a limb that sits nearer the viewer.
   - When these rules conflict, decide by where the limb's root is. A limb whose root (hip or shoulder) lies inside the trunk outline goes behind the trunk, even if it rises above the back like the stilt thing's legs. A limb whose root is outside the trunk, like an arm reaching past the face, goes in front.
   - Place details (ribs, seams, eyes) relative to the mass centres you defined, not copied coordinates; check they land on the form after the first render.
6. **Ink:** `ink_figure(pen, parts, seed, hatch_t, form_parts, part_t, cross)`.
   - **Contours:** three passes (searching, searching, final). Weight comes from pressure, heavier on the side away from the light and at overlaps. Lit edges are sometimes left out entirely.
   - **Hatching:** partial, with a low-frequency "attention" field deciding where the hand bothered.
     - Elongated parts get near-axial strokes; round ones get a diagonal.
     - `form_parts` adds short strokes that follow the form, for a torso or tail.
     - `part_t` sets a per-part threshold: lower means more ink.
     - `cross` adds a second layer, which a dark subject (raven, boar) needs or it reads grey.
   - **Texture matches the covering:**
     - **Fur** is `fur=[(box, flow, strength)]` on `mk`. It turns contour runs inside the box into tufts flowing along `flow`.
     - **Feathers get no fur at all.** Use sparse hatching along the feather direction (`hatch_angle`, `hatch_spacing` about 4.4), `form_parts` for smooth form shading, layered edges with `feather_row` (coverts) and `feather_blade` (primaries and tail, open at the base, tips staggered), and lanceolate throat tips.
     - **Bare skin** (creatures) gets form hatching only, plus a few folds.
7. **Details by hand:** eye, nose, mouth, claws (`paw_details`), crest or bristles (`tufts`), ribs.
8. **Page, from data and a seed.** Wrap all figure drawing in `with L.figure(pen, native_center):`, where `L = Layout(LAYOUT_SEED, subject)`. Then call `L.page(pen, studies, crossed_draw)`:
   - `studies` is `{id: (draw_fn, native_bbox)}`. Each study is drawn at any native coordinates; the layout fits it into a free corner.
   - The seed picks the figure's scale and position, whether there is a crossed-out first try, how many studies (0–3) and which, where the caption sits, and the tilt of all writing.
   - Labels are placed off the figure using an occupancy grid, with an arrow to their anchor.
   - All text lives in `notes/<subject>.json` as entries `{kind: caption|crossed|study|label, text: [lines], id?, anchor?}`. Anchors are in the figure's native coordinates.
   - **Page size is a parameter:** `Layout(seed, subject, W, H, text_scale, fig_scale)` and `save(pen, name, W, H)`. Slots, figure centre, bounds, caption position and the occupancy grid all derive from W×H; 600×600 is the default and renders exactly as before.
     - **Choosing the size:** for the game, render the default 600×600 with no caption and no free notes: the game lays the entry's notes and numbers around the drawing itself, on a phone's portrait page and on a desktop spread's right page (api `CONTRACT.txt`, "JOURNAL"; `docs/design/opening-screen.md`, "The journal"). Its `_ink.png` is the image the game shows. The portrait sizes below are for a stand-alone preview page.
     - **Spending extra height:** use it on legibility, not emptiness. The portrait wolf uses `text_scale` 1.3 and `fig_scale` 1.15.
     - **Running it:** `PAGE_W=600 PAGE_H=780 TEXT_SCALE=1.3 FIG_SCALE=1.15 OUT=wolf_portrait bash render.sh wolf3` writes `wolf_portrait.png` (600 wide, parchment) and `wolf_portrait_ink.png` (1200 wide, transparent).
   - Write the notes as plain field observations: mostly mundane, with measurements, uncertainty and abbreviations, and at most one ominous line per page. No punchy literary lines.
9. **Render and look, 3–4 rounds.** Critique the PNG like an illustrator would: silhouette and proportion first, then joins, then marks. Fix one class of problem per round.

## Parameters that matter

| Parameter | Value |
|---|---|
| Contour weight | `contour_w` about 1.9; passes (0.35, 0.5, 1.0) |
| Construction weight | 0.4–0.5 |
| Hatch weight | 0.6 |
| Overlap accent | ×(1 + 0.45·overlap) (in `sketch.py`) |
| Hatch threshold `hatch_t` | 0.5–0.6 for light subjects; `part_t` down to 0.3–0.36 for dark ones |
| Hatch spacing | about 3.0–3.4 px, tightened automatically in darker parts |
| Stroke noise | `wobble` 0.3–0.9, `wvar` 0.25–0.4, overshoot 4–10 px |
| Feather hatching | spacing 4.0–4.6 along the feather direction; `cross` only above darkness 0.95 |
| `Layout` | figure scale 0.74–1.0, writing tilt −4° to +2°, crossed-out try p = 0.55, studies 0–3, caption on top p = 0.35 |
| `hand_ellipse` | flatten 0.86–1.0, tilt ±5°, sweep 0.82–1.12 turns, 45% chance of a second pass |
| Handwriting | Reenie Beanie at 15–19 px, per-letter rotation σ 2.5°, scale σ 5% |

## Failure modes seen, and their fixes

| Looks like | Cause | Fix |
|---|---|---|
| "Made of circles and ovals" | Contour traced the construction ellipses, or ellipses perfectly round | Contour over the masses via closing; hand-drawn ellipses kept faint |
| Body is two blobs | Masses too far apart for the closing | Add a loin or connecting tube |
| Plank or board edges on legs and shoulders | A near limb drawn in front of the trunk shows its top | Put it behind the trunk, merge the upper arm into the trunk masses |
| Pipes or bandaged legs | Cross-contour ring hatching on limbs | Near-axial hatching on elongated parts |
| Clogs for paws | Overlap accent fired on the ground shadow | Shadow excluded from overlap |
| A black bird reads grey | One thin hatch layer, with the wing covering the body | `cross` second layer and lower `part_t` |
| A head that is "a box pasted over everything" | Head built as its own part on top, sometimes covering a limb that should be in front | Neck, skull and muzzle masses in the trunk's `mk`; the near limb at higher z crosses the face; fur over any remaining seam |
| Ear pasted on | Ear drawn as a closed shape, base line included | `ear()`: two edges rising from inside the skull, no base line |
| A bird that "has fur" | Fur tufts and dense hatching on feathers | No fur; sparse hatching along the feather direction; layered `feather_row`/`feather_blade` edges |
| Every page looks the same | Furniture hard-coded in the same places | `Layout`: seeded figure scale and position, optional crossed-out try, 0–3 studies, moving caption, tilted writing |
| Writing that "sounds like Claude" | Notes authored in drawing code, punchy and literary | Text only in `notes/*.json`; plain observations, measurements, doubt, abbreviations, at most one ominous line |
| Goofy or childlike | Proportions guessed; legs uniform tubes; stiff verticals | Measure the reference; taper widths; knuckles at wrist and hock; slope the pasterns |
| Scarf-like neck | Separate neck or hackle part | Merge into the body silhouette; hackles as fur on its contour |

## Limits

- **It stays "nearing good enough" at best.** Proportion and silhouette can be fixed by measuring and iterating. Mark-making cannot: every stroke comes from one noise model, so the hatching is the same texture everywhere apart from where a mask cuts it, and there are no real speed changes or blots.
- **Heads are the weakest part.** Wedges and ellipses read as cartoon (rat, croc, duck bill) unless specifically checked against a reference head.
- **Invented creatures hide the weakness** because there is no anatomy to violate. Spindly, angular designs suit the method; soft, fleshy ones go goofy.
- **The handwriting is a real person's font**, not drawing.
- **Each page takes 3–6 render rounds** of human-style critique. The tooling does not judge the result; you do, by looking.
