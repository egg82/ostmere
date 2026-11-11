# Week two: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `week-two.md` (beats, side layer, canon ids); the data will
be `day_eight.toml`, `day_nine.toml`, `day_eleven.toml` and `day_twelve.toml`, where every key below reads "[line to
write]". The states below are the design's expectation. **Before the writers start**, regenerate them with the
simulator's `--lines` (`docs/design/week-two-plan.md`, item 1) and replace this file's "States" notes with the
generated lists; a line written against the expectation alone is a draft.

## How the lines get written

As week 1's brief, unchanged: three blind proposers (Sonnet), one lens each (below), every key plus one alternate per
key marked H; a critic scores the drafts blind on `rubric.md` plus *true in every listed state?*; the lead picks line by
line; code checks length, the must-nots as a scan, and three-word echoes against content prose and every shipped line
before them; a fresh agent's voice pass reads every picked line and label in player order after day six's last lines,
and writes the labels. One batch per chapter, in chapter order. The journal's notes are a fifth batch with their own
rules (below), after day eight's lines, by the same pipeline.

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases.

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase, plain. One or two short sentences. A turn the
  reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, per chapter.
- **True in every state.** Most of this plays on return. Never say when, in real time, anything happened, or how long it
  took.
- **People:** Lucy by name; him as `{n2}`; the pair as `{n3}` and `{n4}`; the family as "the woman", "her husband", "her
  brother" until l_join3_1 gives `{n5}`, `{n6}` and `{n7}`, and their child as "the child" or "their child", never
  named; the stranger only ever as "the man who came with them" or
  "him" where clear, **never named, never a slot**. What each does, in active voice. Lucy never grateful, never sweet,
  never says much. Light-tier people are ordinary: no backstory past what they carry.
- **Fights:** plain, one short line, won or lost, never gory, never dwelling on how a beast dies; hunting and skinning
  told as a way of life. A long absence folds into one count line (pools, below).
- **Must-nots (all lines):**
  - no "magic", "spell", "mage", "arcana", Chequer, keels, holders, faith, the burn, Drift, Clear or any season name;
    the weather is described, never named;
  - never "again", or any hint of having been here before, including in the margin note and at the cellar; never that
    the camp stone was cut or set; the stone may do what the player's hand does with it, never why;
  - the crows say numbers; never what they count, in what tongue, or that it is people; Z3 says the count is one short,
    nothing more;
  - the sitting wolf (S3, S4) is never called anything but a wolf, never linked to the margin note, never said to be
    waiting for anything; the wind dropping at S4 is weather, never a warning or a promise;
  - nothing in any line may suggest the man who came with them could have been saved, by anyone, or that anything the
    player did or had matters to it; no line names his wound's cause;
  - never count who the family lost or say who; never say they are missing anyone outright;
  - their child (`decisions.md`, "Never"): there, plainly, never working, never a cost or counted among mouths or
    hands, never in danger in these lines, and never the one the family is missing;
  - the cellar: no count matches anything; never "tally" as a Chequer word; the stool line obeys the stool's rules (one
    stool line in a day's unwrap, never in a dark moment's own line, never named as a pattern);
  - the burning: plain, no body described, no smell; the hand on the warm ground is someone's, unnamed, and means nothing
    a line says;
  - no line judges either answer to O-family or O-guard;
  - no proper noun but Lucy and the name slots.

## Voice exemplars (shipped)

Read the exemplar tables in `day-two-lines-brief.md` and day six's shipped lines in `day_six.toml` (its G2 set
especially, which B8 follows). Reuse no phrase from them.

## Lenses

`python3 content/team/draw_lenses.py week-two-lines --writers 3`:

| Writer | Lens |
|---|---|
| writer-1 | the day after |
| writer-2 | what gets written down, and what doesn't |
| writer-3 | what the animals already know |

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, anything special.

### Week 1's last visit (G2's, in `day_eight.toml`)

**l_ring_scored** (the palisade shown, keyed on `still_end`). Facts: Lucy scores a line in the ash round the bays with a
stick; she does not explain it. States (generated; visits count from the pass's first): V1 present on every route (the first visit of the pass). Special: the wall is
never named in the line; the card says what it is.

### Day eight (8a-8d)

**l_b8_1 to l_b8_3** (B8, H each). Fields: up · yes_but · dread · time. Canon C-beat-8. Facts: a warm wind out of one
quarter all at once; ash so thick the noon goes brown; the bays' roofs sagging under it; fungus up overnight in shelves
on every dead birch and stump; the larder full for the first time; on the roof's ridge the crows in a row, beaks moving,
saying numbers. States (generated; visits count from the pass's first): babysitter V1 present; sharp V2, typical V2 and whenever V3 on return. Special: the plenty and the
wrongness in one set; the crows last.

**l_howls** (U1, H). Fields: down · dread · opens the near question. Facts: howls from three places round the valley,
answering; by morning prints of many in the fresh ash between the bays, round the rack and away, none at the fire.
States (generated; visits count from the pass's first): babysitter V1 present; typical V3, sharp V4 and whenever V4 on return.

**l_caps_1, l_caps_2** (U2, H). Fields: up · yes · warm. Facts: `{n3}` tips the picked caps on a cloth and sorts them
without a word, half into the fire; the pot goes round and comes back with some left; everyone eats until they stop.
States (generated; visits count from the pass's first): babysitter V1 present; typical V3, sharp V3 and whenever V4 on return.

**l_roofs_first** (the first clear). Facts: ash shovelled off the bays' roofs in sheets. States (generated; visits count from the pass's first): babysitter V1 present; typical V4, sharp V6 and whenever V6 on return.

**l_ash_ground** (SL15). Facts: `{n3}` carries the first heap of roof ash to her turned ground in a sack and works it in
with her hands; unties the seed bag, counts seed out on the cloth in rows, ties it up again. States (generated; visits count from the pass's first): babysitter V1 present; typical V4, whenever V6 and sharp V7 on return. Special: never what for,
never when; her arc's last moment this week, quiet.

**l_cord** (SL16). Facts: `{n4}` sits outside the bay in the warm wind, stripping bark and twisting it into cord against
his good knee, fast. States (generated; visits count from the pass's first): typical V4, whenever V6 and sharp V8 on return; never shown on the babysitter route. Special: the speed is the turn; never who taught him.

**l_stage_1 .. l_stage_12** (the palisade's stages; one per stage, the last carried by B10). Facts: posts set, stamped
in, lashed; a stretch of ring at a time. States (generated; visits count from the pass's first): l_stage_1 babysitter V1 present, sharp V3, typical V5 and whenever V6 on return; l_stage_2 typical V7, sharp V7 and whenever V8 on return; l_stage_3 sharp V9 and whenever V10 on return; l_stage_4 whenever V11 on return; l_stage_5 to l_stage_12 never shown on these routes. Special: no
two share a verb; no wolf in them.

**l_pack_1, l_pack_2** (U3, H). Fields: down · yes_but · grim · stores · advances the near question. Facts: five or six
wolves at the gap between the bays and the woodshed in the warm dark; one comes as far as the rack and is driven back
with a brand; the rest wait outside the light and go before dawn with what hung lowest. States (generated; visits count from the pass's first): babysitter V1 present; typical V7, sharp V9 and whenever V11 on return.

**l_b9_1, l_b9_2** (B9, H). Fields: down · dread · pays the near question; canon C-beat-9, C-beat-106. Facts: the book
out by the fire for the first time; the player writes what is known (the rats, the crows, the wolves); on the wolf page,
before a word is written, a note in the margin in pencil, in the player's own hand, about wolves that sat facing the
fire. States (generated; visits count from the pass's first): babysitter V1 present; typical V8, sharp V9 and whenever V11 on return. Special: the line says the note is there and
whose hand; the note's words are the journal's (below), never quoted in the line.

**l_camp_13** (stakes hold 36). **l_journal_first** (the journal's lesson line, UI voice: the voice pass's).

### Day nine (9a-9g)

**l_ring_1, l_ring_2** (E1, H). Fields: up · warm · time · opens the near question. Facts: Lucy scores the line in the ash
all the way round the camp, bays, rack, woodshed and the stone inside it, and comes back to where she started; she looks
at the line, then at the stakes, and starts cutting. Special: the size of the job is the turn.

**l_gap_fire_1, l_gap_fire_2** (SL18, the gap fire's stages). Facts: a fire laid at the gap itself, stones round it.

**l_old_wire** (SL17). Facts: on a run in the scrub along the track, snare wire rusted to a stake, set with the knot the
player's hands tie without thinking; nobody in camp set it. Special: a clue, left at the knot; never "again", never
"your knot" said outright, never who.

**l_open_side_1, l_open_side_2** (E2, H). Fields: down · no · grim · stores. Facts: in the night the pack comes round the
side with no posts, quiet; the rack's low rows stripped; a pegged pelt dragged off into the scrub. States: on return
(nearly always).

**l_smoke_1, l_smoke_2** (E3, H). Fields: up · wonder · advances the near question. Facts: from the ridge, smoke on the
road beyond, more than one fire, low, moving slowly toward the valley over the day. Special: never who; the wonder is
that there is anyone.

**l_b10_1 to l_b10_3** (B10, H each). Fields: up · yes_but · warm · people · pays the near question; canon C-beat-10,
C-beat-110. Facts: the last post set and lashed; the ring closed with a gate of stakes; by evening, people at the gate,
a woman, two men and a child, and another man behind them who keeps apart. States: present or on return. Special: the week's big
moment; the "but" is the gap in how the family stands, shown, never said.

**l_family_1, l_family_2** (O-family's lines). Facts: the woman does the talking; she asks if there is room inside the
wall; the man behind them sits down outside the gate and waits.

**l_find_pole** (Woodcutting 23), **l_camp_14** (stew holds 30).

### Day eleven (11a-11e)

**l_hut_go / l_hut_theirs** (each answer). Facts: the hut going up by the player's hands / by theirs; the same hut.

**l_join3_1, l_join3_2** (Z1, H). Fields: down · grim · opens the near question. Facts: they take the hut; the woman
gives three names (`{n5}`, `{n6}`, `{n7}`; the child is not named); the man who came with them lies by the fire on the side away from them,
wrapped, and does not eat what is given him; asked his name, he looks at the fire. Special: l_join3_1 carries the names.

**l_guard_ask** (O-guard's line). Facts: Lucy looks at the gap, then at the spear on the wall; somebody has to stand
there at night now. Special: the line never prefers one of the two.

**l_guard_n2_1, l_guard_n2_2 / l_guard_n7_1, l_guard_n7_2** (Z2, H; two sets, one per answer, each fired by its arm
card's trigger). Fields: up · yes · warm. Facts: the spear's head beaten on the stone and bound on; the player hands it
over at the gap fire to `{n2}` / `{n7}`; he goes out to the gap and stands through the dark facing out. Special: the two
sets are written as one moment with two names, never one warmer than the other; no line says why that one.

**l_posts** (SL19). Facts: `{n6}` walks the ring with a hand on each post, stops at three that lean, asks for the stakes
left over.

**l_count** (Z3, H). Fields: down · dread · advances the near question. Facts: on the bays' ridge the crows count, as
they do every morning, and the count is one short of yesterday's; then Lucy goes over to wake him, and he is dead.
States: on return (nearly always). Special: the count first, the death second, in that order and no other.

**l_night_12**. Facts: the light going; everyone at the fire, him covered.

**l_b11_1 to l_b11_3** (B11, H each). Fields: down · yes_but · grim · people · pays the near question; canon C-beat-11,
C-beat-115. Facts: the town sits up with the body by the fire all night, the guard at the gap; at first light they burn
him at the scrub's edge, away from the stone; someone lays a hand flat on the warm ground while it burns; nobody knew
his name, so Lucy cuts his mark on a board by the fire with nothing beside it. States: A31 is a tap: present. Special:
the mark with nothing beside it is the last image.

**l_dig_open** (the dig shown with A31's finish). Facts: eight to feed and nowhere to keep it.

### Day twelve (12a-12h)

**l_morning_13**. Facts: grey light, the board by the fire with one mark.

**l_dig_1, l_dig_2** (S1, H). Fields: up · yes · wry · time · opens the near question. Facts: the player takes the spade
to the ruin's north wall and starts digging before anyone has asked where, and only then looks round to see if anyone
minds; nobody does. Special: the wry is at the player's own sure hands; never "you knew", never "again".

**l_bear_sign** (SL20). Facts: at the bloom on the dead birch, the shelves torn down and eaten; claw marks higher on the
trunk than a man can reach.

**l_steps_1, l_steps_2** (S2, H). Fields: up · yes_but · wonder. Facts: under a yard of ash the spade rings on cut stone:
steps going down, whole; dry, cold air coming up them.

**l_b12_1 to l_b12_3** (B12, H each). Fields: down · no · wry · time · pays the near question; canon C-beat-12,
C-beat-118. Facts: a square cellar, dry, dug for stores; no stores; on one wall a board scored with marks in groups of
five, the last group four; in the corner a stool, short on the same leg as the one at the fire. States: present or on
return. Special: reads as a joke; the stool line is this day's one; no line counts the marks or compares them to
anything.

**l_lamps** (SL21). Facts: tallow from the bear rendered in the stew pot, poured into split stakes; lamps on the gate
posts.

**l_sitter_1, l_sitter_2** (S3, H). Fields: down · dread · opens the near question. Facts: at dusk a wolf comes to the
edge of the light, grey, alone, and sits down facing the fire; it sits longer than a wolf sits; the guard doesn't move,
nor does it. States: on return or present. Special: never what it is, never why; no line touches the book.

**l_night_14**. Facts: the light going; the wolf still there.

**l_s4_1 to l_s4_3** (S4, H each). Fields: up · yes · warm · pays the near question. Facts: the wind that has blown all
week drops before dawn, all at once; the ash falls lighter; eight at the fire, the guard at the gap; when it is light
enough to see, the edge of the light is empty and there are no prints where it sat. States: night 14, present (A32 is
a tap). Special: the week's quiet close; the missing prints are the last fact, unremarked.

**l_camp_15** (fungus holds 36), **l_camp_16** (smoked holds 60).

**The asks** (`o_spoil`, `o_cradle`, `o_shaft`, `o_cold_air`, `o_lean_to`, `o_lye`, `o_wet`, `o_crows`, `o_sag`; their
`a_*` labels and costs): facts and answers in `week-two.md`, "The asks (day twelve)". As day nine's: who asks, in
their own active voice, and neither answer judged.

### Fights (pools)

From the line-state lists of item 1. Eight lines per writer per pool, any order, true for any count:

- **fight_pack_won**, **fight_pack_lost**: the pack at the gap; a lost one says only what is gone from the rack.
- **fight_bear_won**, **fight_bear_lost**: the bear hunt, plain.
- **fight_summary**: unchanged from week 1 (it takes the runner's name slot).
- **l_hurt**, **l_poultice**, **l_healed**: unchanged from week 1; a bear's hurt uses the same pool.

### Finds and levels

**l_find_shelf** (Foraging 13), **l_find_pole** (Woodcutting 23), **l_find_hoe** (Scavenging 23), **l_find_pot**
(Cooking 9), **l_find_gap_wolf** (Melee 7), **l_find_fine_ash** (Arcana 11): one line each, by the mix, any visit. No
find names a wolf sitting, the stone's heat past what the hand does, the cellar before B12, or anything of week 3.

## The journal's notes (a batch of their own)

The register is not the lines': `decisions.md`, "Art": lowercase fragments jotted at different times, a later line added
under an earlier one, never composed sentences; mostly mundane (sizes, times, counts, guesses); at most one ominous note
per page; numbers sit beside the notes in the UI font and are never written into them. Two hands: the player's own
charcoal (the current notes) and the old hand's pencil (the margin and the gutter), which reads like the player's but
older. Must-nots as the lines', and: no note says what the crows count; no note confirms or answers the margin.

| Note | Page | When | Facts |
|---|---|---|---|
| n_wolf_1 | wolf | the journal opens | lean; ribs; came as one, then as five or six; won't come into the light |
| n_wolf_margin | wolf | already there (B9) | old hand: wolves that came to the edge of the light and sat facing the fire, as if waiting to be asked in; no date, no count |
| n_rat_1 | ashrat | the journal opens | fat, grey, big front claws; in the roots; the stone floor helps |
| n_rat_2 | ashrat | the Drift's rat step | in the warm wind they come indoors |
| n_crow_1 | crow | the journal opens | on the ridge in a row; they say numbers |
| n_crow_2 | crow | after B10 | counted along with them once: their number is more than live in the camp (a later line under n_crow_1) |
| n_bear_1 | ash-bear | with SL20, the sign (its numbers fill in at the first hunt) | comes for the fungus; the sign higher than a man's reach; not seen yet |
| n_gutter_1 | the bear's, by the gutter (sketch `gutter_knot`) | with n_bear_1 | old hand: a small drawing of a knot near the gutter, no words |

## Labels: the voice pass's, not the writers'

- **Cards:** c_palisade, c_cut_stakes, c_n1_stakes (the town card's label), c_twist_cord, c_hide_flaps, c_pick_fungus,
  c_n3_pick, c_fungus_stew, c_clear_roofs, c_n2_clear_roofs, c_n3_ash_ground, c_gap_fire, c_set_snare_4, c_make_hut,
  c_n5_build_hut, c_arm_n2 / c_arm_n7, c_n2_guard / c_n7_guard, c_n6_posts, c_keep_vigil ("Keep the vigil" or the pass's
  shorter), c_dig_cellar, c_hunt_bear, c_tallow_lamps, c_sit_last_night
- **Upsides** (UI register, numbers): up_palisade ("Gap +50%"), up_gap_fire ("Watch +50%"), up_hide_flaps ("Rest
  +10%"), up_n6_posts ("Gap +50%"), up_tallow_lamps ("Gap +100%"), up_dig_cellar ("Roots hold +50%" and its two
  others), the guard card's ("Gap +150% while on guard"), Arcana 9 and 12's pays
- **Chips:** chip_ash_laden ("rest slower")
- **Offers:** o_family, a_family_room, a_family_theirs, their cost lines; o_guard, its two answers by name slot
- **Order cards:** the stakes ("build when stakes reach 24"), the lanes' stakes and picking ("under 20"), the roofs'
  ("when ash-laden"), the dig's ("dig when stakes reach 12")
- **Fights:** side_gap, threat_wolf_pack, threat_ash_bear (and week 1's side and threat labels, drawn now: plan item 9)
- **Rows and stores:** store_stakes, store_cord, store_bloom ("fungus in the scrub" or the pass's), store_fungus,
  store_ash, store_ashed_ground, store_tallow, store_bear_sign, store_wire; lane_n5..n7 before their names
- **Journal:** the sheet's button, its lesson line, the entry titles (wolf, ashrat, crow, ash-bear), "unknown until
  fought" if the page shows a never-fought runner
- **Aims:** aim_wall, aim_room, aim_gap, aim_store, aim_wind
- **End cards:** dayend14_* (the edge of week 2's content); week 1's dayend6_2 rewritten now it is no longer the edge
- **Never drawn:** store_drift_left, store_drift_clock, store_roof_ash, store_stranger_clock, store_night_12,
  store_night_14, store_entries, the tallies, store_hurt

Two to check first: **o_guard** names two people and neither may read as the right one; **l_count** must work as a
crow line before it works as a death line.
