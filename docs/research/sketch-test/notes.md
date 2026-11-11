# Can an LLM draw the field-journal sketches? Verdict: not at the bar

Neither sketch clears the bar for shipping in the game. Judged against the Journal 3 target (quick, nervous field sketches with searching lines, partial hatching, side studies, labels and a crossed-out attempt), both pages have all the ingredients. Neither has the drawing. A reader would spot that a machine drew them, mostly from the anatomy and the sameness of the pen, not from the page furniture.

## Redo: feathers, heads from the neck, seeded layouts, notes as data

All page text now lives in `notes/<subject>.json`. Each page's layout comes from a seed. Heads are built into the trunk silhouette, ears use `ear()`, and feathers use `feather_row`/`feather_blade`.

- **raven (2 more rounds):** feathered rather than furry. Sparse hatching runs along the feather direction, the wing has covert rows and layered primaries reaching toward the tail, the throat feathers are pointed tips, and the cross-hatched body reads dark. The giveaways are the covert rows, which are still a little regular, and the small figure (seeded scale 0.8).
- **boar (2 more rounds):** the head grows out of the neck into a long, low wedge and the ear rises from the skull, so both pasted-on faults are gone. The top half is still lightly inked for a dark animal.
- **creature2 (2 more rounds):** the head now hangs from a short thick neck inside the body silhouette, and the near arm crosses in front of the face. It no longer reads as a crocodile. The face is still small for what the notes describe.
- **creature (stilt thing), reproduced from process.md (3 rounds):** recognisably the same creature, with the neck and head now one form with the torso and a hunched multi-mass body. The face is still a sock shape with a seam, and a few vertebra ticks float just off the neck.
  - **Gaps in the doc that I had to supply, now written into process.md:**
    - How to measure an invented creature: use a previous page or real analogues.
    - A single egg torso reads as a bun: use several unequal masses.
    - The two layering rules conflict for a limb that rises above the back: decide by where its root is.
    - Detail coordinates must be placed relative to the masses rather than copied.

## The set of four (`journal.py` method; process in `process.md`)

**Method fixes, made before drawing the set:**
- Construction ellipses are hand-drawn: flattened, tilted, egg-shaped, unclosed or overshooting, sometimes double-passed. They no longer form a perfect circle.
- Contours are heavier at overlaps.
- Hatching direction is chosen per part, near-axial on limbs, and density follows tone. Dark subjects get a second, crossing layer.
- Limbs have knuckle masses at the joints and real paws or hooves.
- Page furniture is shared through helpers.

- **wolf3 (3 rounds):** the best wolf. Same lean, low-headed figure as wolf2, now with paws, a visible bushy tail, limb shading along the legs, and hand-drawn construction underneath. Still close to "nearing good enough": the forelegs are slim, near-parallel posts, the head is a little fox-like, and the marks are even.
- **raven (4 rounds):** the strongest new page. It reads as a corvid at a glance: hooked beak, shaggy throat, folded wing over a dark body, wedge tail, scaly feet. The giveaways are the scalloped covert rows, which look stamped, and an outline around the beak base that is too heavy.
- **boar (3 rounds):** reads as a wild boar, with weight in the front, a bristle crest and a wedge head. The top half of the body is under-inked for a dark-bristled animal, the tusks are faint, and the legs are a touch long.
- **creature2 (3 rounds):** weaker than the first creature. The concept works (a sack dragged on high-elbowed arms, six eyes, kin to the stilt thing), but the flat toothed head reads as a cartoon crocodile, more goofy than eldritch. The hand study is unclear. A head redesign would be the next round.

## Wolf, construction version (`wolf2.svg`, `wolf2.png`; 6 rounds, `rounds/wolf2_r*.png`)

The user suggested drawing it the way a human does: basic shapes first, then noise. `wolf2.py` follows that method:
1. A gesture line and ground plane.
2. Masses with proportions measured off the hound. Withers height H, body length about 1.15H, chest about 50% of H, head length about 0.37H. The masses are a ribcage egg, a pelvis, a cranium plus a muzzle wedge, and a loin mass; bones are lines with joint dots.
3. The contour is drawn over the masses. A morphological closing produces the tangent bridges (back line, belly tuck) instead of tracing an ellipse's edge.
4. The construction is left faint underneath at 42% opacity.
5. Noise on top: multi-pass searching contours, overshoots, varied weight, partial hatching plus some form-following strokes.

The page furniture is reused verbatim from `wolf.py`; only the arrow targets moved.

**What works**
- This is the first version that reads as a wolf rather than a dog-shaped object: lean, deep-chested, head carried low.
- The visible construction underneath does a lot of the "real sketchbook" work. Masses and joint dots showing through make the contour look searched-for rather than generated.
- Getting there took rounds of the kind a human makes: the body was two blobs until a loin mass was added. The chest needed deepening to wolf proportion, the foreleg went behind the chest so its top edge stops reading as a plank, and the pasterns now slope.

**What still gives it away**
- The legs are still thin and fairly uniform, with little muscle or knuckle at the wrist and hock, and the paws are minimal.
- The near hind leg is a busy bundle of overlapping contours.
- The tail hides behind the thigh.
- Hatching is still the same texture everywhere, apart from where a mask cuts it.
- The pen is uniform: one noise model for every mark, no speed changes or blots.
- The head joins the neck a little stiffly, even with ruff tufts over the seam.

**Verdict:** this is a clear step up from `wolf.png` and the best figure I produced. It is close to passable as a quick journal study, and on a busy page with the annotations it may well pass a casual glance. A careful look still shows it is procedural, mostly in the legs and the evenness of the marks. More rounds could plausibly fix the legs and paws, since that is anatomy and can be iterated. The evenness of the marks is the method's ceiling.

## Wolf, first version (`wolf.svg`, `wolf.png`; 6 rounds, `rounds/wolf_r*.png`)

**What works**
- The page reads as a notebook page: crossed-out first attempt, eye and paw studies, arrows, scrawled notes.
- Contours are multi-pass, overshoot their ends, and are heavier on the shadow side.
- The silhouette from round 4 on is traced from the Gessner hound (`trace_hound.py`, gridded reference with points snapped to real ink pixels). This got rid of the "made of circles and ovals" look the user flagged in rounds 1–3. It is the single biggest improvement.

**What gives it away**
- **Anatomy and gesture.** The forelegs are rubbery and too even in width, and the paws are blobs. The muzzle is rat-like, and the head is lowered but not menacing. The user's "a five-year-old drew it" still fits round 6.
- **Hatching** is a statistical texture (diagonal strokes thresholded on a fake 3D shading), so it is the same everywhere. A person hatches where they are looking and leaves the rest. The "attention" noise field does not fake that.
- **One pen.** Every mark comes from one weight and noise model. Real nervous sketching has speed changes, hard stops, blots and a few confident strokes among the searching ones.
- **Studies are generic.** The eye is close to a human almond, and the print is four ovals plus a pad.

**Could more iteration fix it?** Not with this approach, in my judgement. Each round fixed the failure it was aimed at (proportion, head height, silhouette), and the next look found a new one of the same kind. The ceiling is that I place coordinates and judge a 600px render by eye; I can't feel a gesture line. Tracing real reference was the only step change. Going further down that road would mean tracing a real wolf photo or drawing for every pose, at which point it is a stylisation filter over reference rather than drawing. That could be a workable pipeline, but it is a different claim.

## Creature (`creature.svg`, `creature.png`; 4 rounds, `rounds/creature_r*.png`)

The design is a "stilt thing": four reverse-jointed legs with knees above the back, a sagging rib-bag body, an eyeless head on a hanging neck, and a face that splits vertically.

**What works**
- The silhouette is genuinely odd and reads as wrong in a good way.
- The angular, knobby legs (straight segments, round 4) suit the method better than fleshy forms. An invented anatomy also has no "that's not how a wolf stands" test to fail.
- The labels carry the story ("clicked when it moved", "no eyes – but it turned to the lamp").

**What gives it away**
- The torso is still a bean with hatching on its underside.
- The head and neck read as a dangling sock.
- The fang study looks like a chili pepper, and the split-face study is still essentially an oval with teeth.
- The composition is symmetric and centred: legs splayed like a table, with no ground contact weight or overlap.
- Same uniform-pen problem as the wolf.

**Could more iteration fix it?** Partly. This is the stronger of the two, because invented spindly anatomy hides the drawing weakness. A few more rounds could fix the head, torso and studies. It would still look procedurally even.

## Technical notes

- **Pipeline:**
  - `ink.py`: tapered variable-width strokes as filled polygons, inflated-mask Lambert shading, form hatching.
  - `sketch.py`: searching contours, partial overshooting hatching, arrows, scribble-outs, handwriting.
  - `wolf.py`, `creature.py`: the pages.
  - `trace_hound.py`: automatic silhouette extraction. It failed because flood fill leaks through gaps in the woodcut outline. The gridded manual trace with ink snapping is in `wolf.py`.
- **Handwriting** is the OFL font Reenie Beanie (`fonts/`), converted to glyph paths with per-letter jitter via fontTools in `lib/`. No font dependency is left in the SVG. It is the most convincing element on the page, and it is a human's handwriting, not mine.
- **Re-rendering:** `bash render.sh wolf|creature [round]`.
