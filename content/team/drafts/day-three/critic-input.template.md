# Critic input (template): day three's lines

Fill the three DRAFT blocks with the proposers' TOML, labelled A/B/C in shuffled order; do not say which lens wrote which.

You score the three drafts blind on the rubric below, plus one row: *true in every listed state?* (quote the state a line breaks). Check each line against the brief's rules and must-nots. Score per key per draft; name the best of the three per key and why in a clause.

## Rubric (verbatim)

# Critic rubric

You score another writer's draft blind. Score each item (a line, a fact, a set piece) on every row below, 0–2,
with a one-line reason. Quote the words you mean. Do not rewrite anything.

| Row | 0 | 1 | 2 |
|---|---|---|---|
| **Turn** (curated items only; plain event-log records skip this row) | stated outright or absent | implied but the last step is easy | the reader completes it |
| **On the nose** | says the feeling or the moral | one word too many | leaves it hanging |
| **Repeats** | reuses a shape or phrase already in the bible or in this draft | a near echo | fresh |
| **Canon** | contradicts a canon id (name it) | strains one (name it) | consistent |
| **Rules** | breaks decisions.md (Never list, tone, tropes rule, spoiler rule) | bends one (name it) | clean |
| **Overwrought** | ornate, stacked images, arch phrasing | one flourish too many | plain and exact |

Then answer yes or no for each item, quoting the span that decides it:
- **Changed?** Does the situation end different from how it started?
- **Free win?** Is a clean success missing its cost?
- **Brighter than planned?** Is the ending tidier or brighter than the beat's declared `turn`?
- **Turn stated?** Is the turn stated rather than left to the reader?

Notes:
- Most tropes should resolve as promised; flag an item that turns a trope outside the four listed in world.md.
- Facts passed as finished phrases, and key names leaking into prose, count as Repeats.
- Close with the draft's three weakest items by id and the one strongest, each with a reason.


---

# The brief (verbatim)

# Day three's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `day-three.md` (the beats, the side layer, the canon ids);
the data will be `app/ashfall_app/opening/day_three.toml`, where every key below reads "[day three: line to write]". The
states below are the design's expectation. **Before the writers start**, regenerate them with the day-three report's
`--lines` (`docs/design/day-three-plan.md`, item 6) and replace this file's "States" notes with the generated lists;
a line written against the expectation alone is a draft.

## How the lines get written

As day two's brief, unchanged: three blind proposers (Sonnet), one lens each (below), every key plus one alternate per
key marked H; a critic scores the drafts blind on `rubric.md` plus *true in every listed state?*; the lead picks line by
line; code checks length, the must-nots as a scan, and three-word echoes against content prose and the shipped lines of
the opening, day one and day two; a fresh agent's voice pass reads every picked line and label in player order after
day two's last lines, and writes the labels.

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases.

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase, plain. One or two short sentences. A turn the
  reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, across all of day three's lines.
- **True in every state.** Most of day three plays on return. Never say when, in real time, anything happened, or how
  long it took.
- **Lucy:** "she", her name where "she" would be unclear. What she does, in active voice; never grateful, never sweet,
  never says much; no line gives her a need the player could tend.
- **Him:** "he" until l_join_2 gives his name; the name is a slot (`{n2}`), filled per save from the names pool, so no
  line leans on its sound. He is light tier and ordinary: what he does, in active voice; no backstory past what he
  carries.
- **Must-nots (all lines):**
  - never that the ground or the stone is warm, or glows, before the B5 lines (K1 is thin ash, K3 is frost absent: the
    fact, never a cause); nothing about the player's hands and heat;
  - no wolf seen: K3 is voices across the Hollow; no line has an animal at the edge of the firelight;
  - never "again", or any hint of having been here before;
  - never count who he lost or say what happened to them; never count her people;
  - no line judges either answer to O-stay or to `o_bank`; on either answer he stays;
  - the scrap and the shaft he carries are never put together in a line (SL4 shows him looking, nothing more);
  - no proper noun but Lucy and `{n2}`; no Chequer, keels, holders, magic, faith, the burn.

## Voice exemplars (shipped)

Read the opening's, day one's and day two's tables in `day-two-lines-brief.md`, "Voice exemplars", and day two's
shipped lines in `day_two.toml` (B4's set especially, which day three follows directly). Reuse no phrase from them.

## Lenses

`python3 content/team/draw_lenses.py day-three-lines --writers 3`:

| Writer | Lens |
|---|---|
| writer-1 | the joke nobody laughs at |
| writer-2 | what it costs the people |
| writer-3 | what is eaten, and who goes without |

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, and anything special.

### The edge and the track (V1)

**l_edge_1, l_edge_2** (A22, K1, H). Fields: down · grim · opens the near question. Canon C-beat-87. Facts: the player
walks the edge of the firelight; the camp in plain view of the ridge; scrub and thorn on three sides; one way out, a
half-sunk track over old fields; coming back, the ash thinner on the camp's stone than anywhere on the walk. States:
day 3, straight after B4's lines on either answer, so no line says who walked to the ridge. Special: the thin ash is
the hook, stated as a sight, never explained.

**l_track_first** (no beat). The track's first run starts: wood laid over the wet ground, a cairn where the fog closes.
Special: the first trip; the line says what a run is, not how long.

**l_stream** (K2, H). Fields: up · wonder · advances the near question. Canon C-beat-88. Facts: a stream that steams a
little in the cold; no ash lies on the water; soft grey clay on the bank, warm in the hand. Special: the warm clay is
the one warm thing a line may say before B5, because it is the clay, not the ground.

**l_larder_1..3, l_roof_1..2** (each comfort stage). Facts: stone laid course by course for a floor off the wet ground;
a roof over the drying wall, poles and then thatch of what's to hand. States: in either order, present or by the queue.

### The third night (V1 → V2)

**l_night_3a, l_night_3b** (K3, H). Fields: down · dread. Canon C-beat-89. Facts: howls answering each other across the
Hollow, two voices, nearer than the first night's; Lucy banks the fire higher, says nothing; nothing comes. States: at
night, on return on most routes; the track has run at least once. Special: voices, not animals seen.

**l_morning_4** (no beat; K3's last fact). Frost greys everything past the firelight; none on the stone. Special: the
fact only.

### Clay, the hearth, the watch fire (V2-V4)

**l_clay_first**, **l_hearth_1..4** (one per course), **l_cure** (a course dry; one key, used for each), **l_stew_first**.
Facts: clay dug at the stream bank; a hearth laid on the camp's stone a course at a time, each left to dry before the
next; the first pot of stew. States: day 4; the courses often by the queue while away.

**l_watch_1, l_watch_2** (SL1). Facts: Lucy has begun a ring of stones at the gap, facing the track, a fire of her own
between the camp and the dark. States: morning 4, on return mostly. Special: what she does; no reason given.

**l_watch_lit** (SL3). Facts: she sits at it through the day with her back to the camp, a stick at a time. States: built
by her or by the hands.

**l_larder_done** (SL2), **l_roof_done** (SL5). Facts: roots in rows on a stone floor, Lucy rearranging them; rain-dark
ash running off the new roof, the hang under it staying pale. States: by the queue, either order.

### The old field (V3-V4)

**l_field_1, l_field_2** (K4, H). Fields: down · no · wry. Canon C-beat-90. Facts: the track reaches the old field;
furrows under the ash; nothing growing, nothing that will; a ploughshare rusted to a lump in the last furrow, carried
back as scrap. States: any visit from V2, before or after O-stay and K5. Special: wry about the walk having been for
this, never about the dead ground.

### The stranger (V5-V6)

**l_stay_1, l_stay_2** (O-stay, H). Canon C-beat-91. Facts: a man at the edge of the firelight, drawn by the stew's
smell; alone; a spear's shaft with no head; he asks to stay. States: stew just reached 6; present or on return; any
comfort built or not. Special: sits on screen until answered; neither answer may read as the right one.

**l_bay_go, l_bay_his** (each answer's build starts). Facts: the player's hands start a bay against the lean-to / he
starts it himself.

**l_join_1, l_join_2** (K5, H). Fields: up · yes_but · warm. Canon C-beat-92. Facts: he takes his place at the fire;
Lucy looks him over once and goes back to work; he gives his name (`{n2}` in l_join_2); three at the fire, the stores
for three now. States: the bay done, either answer. Special: the yes_but is the stores, said as a sum, never a worry.

**l_his_first** (his first finished task in the town's mix). Names no store and no task.

**l_scrap_ask** (SL4). Facts: he turns the scrap pile over with his foot, holds up the shaft he carries, puts it down
again. States: his first day; any scrap count, so no number.

### Banking the fire (V7-V8)

**l_bank_1** (SL6, the offer's line), **l_bank_hers**, **l_bank_his** (each answer). Facts: she buries the fire in ash;
he rings it with stones; each thinks the other's way wastes wood. States: the hearth's third course laid; three at the
fire. Special: neither answer judged; the two answers' lines are what each of them does when the camp goes their way.

### Night 4 and B5 (V9)

**l_hearth_done** (the fourth course cured), **l_night_4** (night 4's first item). Facts: the hearth whole on the stone;
three at the fire as the light goes.

**l_b5_1 to l_b5_3** (A20, B5, H each). Fields: up · yes · wonder · pays the near question, opens the deep one. Canon
C-beat-5, C-beat-93. Facts: the player banks the new hearth for the first time; the ground under the camp is warm; the
ash melts there first; the cracks round the hearth glow faintly red. States: night 4, present (A20 is a tap). Special:
wonder, not dread; no cause, no magic, no name for it.

### The Camp

**l_camp_9** (the drying wall takes 11), **l_camp_10** (lifted by B5: smoked holds 27).

### Finds (levels) and day two's sink

**l_find_clay_seam** (Foraging 6), **l_find_lichen_cairn** (Foraging 8), **l_find_buckle** (Scavenging 16),
**l_find_thick_pot** (Cooking 4): one line each, by the mix, any visit; never naming warmth, wolves or B5's or B7's
facts. **l_bed_1..3** (day two's `raised_bed`, one per stage): a bed off the wet ground, poles, a stone footing, then
lying off the damp; day 3, before or after the builds and B4.

## Labels: the voice pass's, not the writers'

- **Cards:** c_walk_edge, c_field_track, c_larder_floor, c_rack_roof, c_clay_hearth, c_dig_clay, c_stew, c_make_bay,
  c_n2_build_bay, c_bank_hearth, c_watch_fire, c_n1_build_watch, c_n1_watch, c_raised_bed, his task cards (c_n2_*)
- **Upsides** (UI register, numbers): up_larder_floor ("Roots hold 54, was 36"), up_rack_roof ("Rack +25%"),
  up_clay_hearth ("Stew 3 a pot, was 2"), up_raised_bed ("Rest +30%"), up_bank_hers ("Fire −10% dry wood"),
  up_bank_his ("Rest +10%")
- **Offers:** o_stay, a_make_room, a_let_him_build, a_make_room_cost, a_let_him_build_cost (`{d}`); o_bank, a_bank_hers,
  a_bank_his
- **Rows and stores:** lane_n2 (before his name), lane_n2_named; the town's mix's header; store_clay, store_scrap,
  store_stew; the mix offer on the damp wood line ("add the track, held at 12")
- **Aims:** aim_field, aim_stay, aim_three, aim_warm (the arc's first)
- **The end card:** dayend3_*, day two's pattern; day two's end card drops its "as far as it goes" line at release
- **Never drawn:** store_arrivals, store_night_3, store_night_4, store_cure_done, store_watch_done, action_night_3,
  action_night_4; plain labels that spoil nothing

Two to check first: **o_stay** sits on screen across absences and neither answer may read as the right one; **o_bank**
is a small choice between two people's habits, and its labels must read as habits, not as a correct way.


---

## Generated states (the typical route's simulator pass; replaces the brief's expected states where they differ)

Visit numbers count from the first visit of day three's pass. 'present' = the player is there when it happens; 'on return' = reads it after an absence. A line must read right in every listed combination.

| key | states |
|---|---|
| l_edge_1 | visits V1-V1 (1 states); present; capped done 25-25; answers seen so far, any of ['o_cart_go']; no trip held; queue 1-1 |
| l_edge_2 | visits V1-V1 (1 states); present; capped done 25-25; answers seen so far, any of ['o_cart_go']; no trip held; queue 1-1 |
| l_track_fail | never shown on the typical route (design expectation in the brief applies) |
| l_track_first | visits V2-V2 (1 states); on return; capped done 25-25; answers seen so far, any of ['o_cart_go']; trip held; queue 0-0 |
| l_stream | visits V2-V2 (1 states); on return; capped done 25-25; answers seen so far, any of ['o_cart_go']; trip held; queue 0-0 |
| l_field_1 | visits V4-V4 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_field_2 | visits V4-V4 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_floor_fail | never shown on the typical route (design expectation in the brief applies) |
| l_larder_1 | visits V6-V6 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_larder_2 | visits V7-V7 (1 states); on return; capped done 28-28; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_larder_3 | visits V8-V8 (1 states); on return; capped done 29-29; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_larder_done | visits V8-V8 (1 states); on return; capped done 29-29; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_roof_fail | never shown on the typical route (design expectation in the brief applies) |
| l_roof_1 | never shown on the typical route (design expectation in the brief applies) |
| l_roof_2 | never shown on the typical route (design expectation in the brief applies) |
| l_roof_done | never shown on the typical route (design expectation in the brief applies) |
| l_hearth_fail | never shown on the typical route (design expectation in the brief applies) |
| l_cure_fail | never shown on the typical route (design expectation in the brief applies) |
| l_hearth_1 | visits V3-V3 (1 states); on return; capped done 26-26; answers seen so far, any of ['o_cart_go']; trip held; queue 0-0 |
| l_hearth_2 | visits V5-V5 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_hearth_3 | visits V7-V7 (1 states); on return; capped done 28-28; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_hearth_done | visits V9-V9 (1 states); on return; capped done 30-30; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_stew_fail | never shown on the typical route (design expectation in the brief applies) |
| l_stew_first | visits V3-V3 (1 states); present; capped done 26-26; answers seen so far, any of ['o_cart_go']; trip held; queue 1-1 |
| l_night_3a | visits V2-V2 (1 states); on return; capped done 25-25; answers seen so far, any of ['o_cart_go']; trip held; queue 0-0 |
| l_night_3b | visits V2-V2 (1 states); on return; capped done 25-25; answers seen so far, any of ['o_cart_go']; trip held; queue 0-0 |
| l_morning_4 | visits V2-V2 (1 states); on return; capped done 25-25; answers seen so far, any of ['o_cart_go']; trip held; queue 0-0 |
| l_watch_1 | visits V2-V2 (1 states); on return; capped done 25-25; answers seen so far, any of ['o_cart_go']; trip held; queue 0-0 |
| l_watch_2 | visits V2-V2 (1 states); on return; capped done 25-25; answers seen so far, any of ['o_cart_go']; trip held; queue 0-0 |
| l_watch_fail | never shown on the typical route (design expectation in the brief applies) |
| l_watch_lit | visits V7-V7 (1 states); on return; capped done 28-28; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_watch_dry | never shown on the typical route (design expectation in the brief applies) |
| l_night_4 | visits V11-V11 (1 states); on return; capped done 31-31; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_bank_hearth_fail | never shown on the typical route (design expectation in the brief applies) |
| l_b5_1 | visits V12-V12 (1 states); present; capped done 33-33; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_b5_2 | visits V12-V12 (1 states); present; capped done 33-33; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_b5_3 | visits V12-V12 (1 states); present; capped done 33-33; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_stay_1 | visits V3-V3 (1 states); present; capped done 26-26; answers seen so far, any of ['o_cart_go']; trip held; queue 1-1 |
| l_stay_2 | visits V3-V3 (1 states); present; capped done 26-26; answers seen so far, any of ['o_cart_go']; trip held; queue 1-1 |
| l_bay_go | visits V3-V3 (1 states); present; capped done 26-26; answers seen so far, any of ['o_cart_go']; trip held; queue 1-1 |
| l_bay_his | never shown on the typical route (design expectation in the brief applies) |
| l_bay_fail | never shown on the typical route (design expectation in the brief applies) |
| l_join_1 | visits V4-V4 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_join_2 | visits V4-V4 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_his_first | visits V4-V4 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_scrap_ask | visits V4-V4 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_bank_1 | visits V7-V7 (1 states); on return; capped done 28-28; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_bank_hers | visits V7-V7 (1 states); present; capped done 28-28; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_bank_his | never shown on the typical route (design expectation in the brief applies) |
| l_camp_9 | visits V4-V4 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_camp_10 | visits V12-V12 (1 states); present; capped done 33-33; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_clay_seam | never shown on the typical route (design expectation in the brief applies) |
| l_lee_lichen | never shown on the typical route (design expectation in the brief applies) |
| l_buckle | visits V4-V4 (1 states); on return; capped done 27-27; answers seen so far, any of ['o_cart_go', 'o_stay_room']; trip held; queue 1-1 |
| l_thick_pot | visits V10-V10 (1 states); on return; capped done 30-30; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_stack_fail | never shown on the typical route (design expectation in the brief applies) |
| l_stack_1 | visits V9-V9 (1 states); on return; capped done 30-30; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_stack_2 | visits V10-V10 (1 states); on return; capped done 30-30; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_stack_3 | visits V11-V11 (1 states); on return; capped done 31-31; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_shelf_fail | never shown on the typical route (design expectation in the brief applies) |
| l_shelf_1 | visits V10-V10 (1 states); on return; capped done 30-30; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_shelf_2 | visits V11-V11 (1 states); on return; capped done 31-31; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |
| l_shelf_3 | visits V12-V12 (1 states); on return; capped done 32-32; answers seen so far, any of ['o_bank_hers', 'o_cart_go', 'o_stay_room']; trip held; queue 0-0 |

## Keys the brief does not spell out (ranges like l_larder_1..3 included; the rest have no beat facts, write from the card)

Failed-card lines (`*_fail`, `l_watch_dry`): what the card shows when tapped with the cost short; the player's try, short of the means; one short line; no number.
`l_stack_1..3` (card wood_stack) and `l_shelf_1..3` (card pot_shelf): three build stages each; a stack for dry wood raised on stones, and a shelf for pots; stone and damp wood go in. Same register as day two's `l_woodstack`/`l_bed` stage lines.
Keys: l_track_fail, l_floor_fail, l_larder_2, l_larder_3, l_roof_fail, l_roof_2, l_hearth_fail, l_cure_fail, l_hearth_2, l_hearth_3, l_stew_fail, l_watch_fail, l_watch_dry, l_bank_hearth_fail, l_b5_2, l_bay_fail, l_clay_seam, l_lee_lichen, l_buckle, l_thick_pot, l_stack_fail, l_stack_1, l_stack_2, l_stack_3, l_shelf_fail, l_shelf_1, l_shelf_2, l_shelf_3

The brief's `l_find_*` and `l_bed_*` names map to this file's keys: l_clay_seam, l_lee_lichen, l_buckle, l_thick_pot (finds) and l_stack_*/l_shelf_* (stage lines).


## Drafts

### Draft A

{{DRAFT_A}}

### Draft B

{{DRAFT_B}}

### Draft C

{{DRAFT_C}}

