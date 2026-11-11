# Art to commission

Spoilers: under `content/`, never shown to the owner. Scene pieces the code-drawn pass could not make read; each is a
layer in `tools/scene` (or a dropped one) that a commissioned sprite replaces without touching the page.

**Shared spec for every piece.** Time Fantasy style at its 1x grain (16 px tiles; the scene is 240×144 art pixels,
drawn at 2x as 480×288 and scaled up with nearest-neighbour), outlined like the pack's props, transparent PNG.
Palette rule (`docs/decisions.md`, "Art"): what the player made is warm (the Farm and Fort wood tones, e.g.
#C7995C / #B87E50 / #9D5F3E / #7D5643, outline #6C3C4A); the found world is cool, neutral grey. The scene is seen at
phone width (390 CSS px for the 480 px scene, about 1.6 screen px per art pixel) and on 4K (the 480 px scene at 7x): a piece must
read as what it is at both.

## Hung catch (dropped: `catch_hanging`)

- **What:** two ashrats (`content/creatures.md`, C-creature-4; R1's only small prey) hung head down by their tails
  from cords.
- **When it shows:** `store:catch` (the snares' catch, before it is smoked).
- **Where:** hung under the drying rail's left half, between its legs, around scene px (114–154, 134–168) at 2x;
  clear of the smoke column at x ≈ 163.
- **Size:** each rat about 6×12 art px including tail; two of them, slightly different heights.
- **Style:** grey-brown fur, cool (the creature is the world's); cords warm. It must read as small dead animals at 2x
  (body, tail, ear, snout, legs hanging) and at least as "something hung up" on a phone. The code-drawn try read as
  seed pods.

## Snares (`snare_1` to `snare_3`): borderline

- **Status:** commission if they must read as snares on a phone. Today: a stake and a cord loop laid on the ground;
  at phone width they read as three small pale loops by stakes.
- **When:** `pushes:set_snare@1`, `@2`, `@3`, one each.
- **Where:** at the birch edge past the stump, scene px about (427, 222), (452, 243), (434, 264) at 2x, near the
  scene's right edge; a crouched figure (`figure_snaring`) sits just left of the first.
- **Size:** at most about 14×11 art px each.
- **Style:** a snare set on an animal run (a stake or bent sapling, a cord or wire noose), warm wood and a pale cord
  or wire with a highlight; a little ground shadow. Not a hanging noose (it read as a gallows).

## Her shelter (`n1_shelter`): weakest pick of day two

- **Status:** commission before day two ships if it still reads as a rack. Today: the Farm and Fort hide-on-pole frame
  (`tileB_fortA`) with a bedroll under it; every tent in the packs is about 100 px tall against the lean-to's 50.
- **When:** `project:build_shelter` (its `_ghost` while it is built), then for good.
- **Where:** beside the lean-to, scene stage `22_offer`.
- **Size:** about 40×36 px at 2x.
- **Style:** one low lean-to of poles and brush matching the scene's own lean-to: warm wood, dark brush, a little
  ground shadow.
