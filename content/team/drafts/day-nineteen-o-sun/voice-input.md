# Voice pass: one ask in an idle survival game's story

You are a fresh reader. Read the lines below in the order a player meets them, then do two things.

1. For each PICKED line, give a verdict: kept, or changed (with your text and a one-line reason). Check: second person,
   present tense, lowercase, plain; no feeling named, no moral; true at any hour of day or night; no line judges either
   answer; nobody arrives in the light's line; nothing suggests the man who went over the ridge can be found or that a
   light or store is for him; no season named; never "again"; at most 75 characters.
2. Write the LABELS (UI register, not the story's voice), matching the shipped examples' shapes exactly:
   - `o_last_sun`: the offer's text, one or two sentences, sentence case, putting the choice outright (who asks, what);
   - `a_last_sun_light`, `a_last_sun_cellar`: the two answer labels, a few words each, sentence case, no full stop;
   - `a_last_sun_light_cost`, `a_last_sun_cellar_cost`: what each answer changes, with `{pct}` where the page puts the
     signed percentage (the light answer's is the table's meals, which draw travellers to stay; the cellar answer's is
     how much smoked meat the store holds). Name the thing changed plainly; no direction word, no number.

Output: a TSV with header `key	verdict	text	reason`, one row per key (3 lines, 5 labels). Nothing else.

## Shipped label examples
o_door_ice = "The hut door has frozen in its frame. {n6} looks it over."
a_door_ice_shave = "He shaves the frame each frost"
a_door_ice_shave_cost = "{pct} your work, {pct_b} from {n6}"
o_sun_rack = "{n3} says meat dries faster in sunlight than over the coals."
a_sun_rack_sun = "She moves the rack into the sun"
a_sun_rack_sun_cost = "{pct} smoked"
a_sun_rack_fire_cost = "{pct} stew"
o_choir = "Three women have come for the table. Where do they work first?"
a_choir_beds = "To the beds"
a_choir_beds_cost = "{pct} beds' growth, {pct_b} smoked at the table"
o_j_steps = "Lucy says somebody has to cut steps down the bank to the open water."

## The lines in player order (shipped, then PICKED)
l_b17_1 = "{n11} goes out alone at first light to start the last stretch."
l_b17_2 = "by dark he is not back."
l_b17_3 = "when the last stretch is laid, his axe is in its last stump."
l_b17_4 = "his prints go on down the far side, a wolf's either side of them, close."
l_b17_5 = "past the hill it is grey as far as you can see."
l_lamp_out_1 = "at dusk {n12} carries a lamp out to the end of the road."
l_lamp_out_2 = "she sits by it facing the far side, and is still there when the light goes."
PICKED l_last_sun = "a few days of pale sun left. lucy turns to you."
(the offer shows here: o_last_sun with its two answers)
PICKED l_last_sun_light = "a lamp hangs in the hall door now, lit every night."  (if the light answer)
PICKED l_last_sun_cellar = "smoked meat hangs in rows from the cellar beams."  (if the cellar answer)
l_night_21 = "the light goes. stars, and a lamp at the end of the road."
l_t13_1 = "you walk out along the road in the starlight and sit with her by the lamp."
