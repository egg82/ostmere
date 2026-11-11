# Day two's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `day-two.md` (the beats, the canon ids); the data is
`app/ashfall_app/opening/day_two.toml`, where every key below reads "[day two: line to write]". The states are generated:
`python -m tests.daytwo.report --lines` (from `app/`) on main at `1207182`, the ten routes at seed 0.

## How the lines get written

1. **Three proposers** (Sonnet), blind to each other, each with one lens drawn by code (below). Each writes every key in
   "The lines", plus one alternate for each key marked H. Output: a TOML file, `key = "line"` and `key_alt = "line"`,
   in the order below. A draft missing an alternate is sent back.
2. **A critic** scores the three drafts blind on `rubric.md`, plus one row: *true in every listed state?* (quote the
   state it breaks). Writers revise their own drafts once.
3. **The lead** picks line by line. Code then checks: length (below), the must-nots as a scan, and n-gram echoes against
   content prose and the shipped lines of the opening and day one (no run of three words shared with either).
4. **A voice pass** by a fresh agent reads every picked line and every label in `day_two.toml` in player order, after
   day one's last lines, and writes the labels.

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases: a word from an attribute may appear in a line, its phrasing should not.

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase, plain. One or two short sentences. A turn the
  reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** the lines show on the task card. Across all of day two's lines, the median is 45 characters or fewer and
  the 90th percentile 75 or fewer.
- **True in every state** on the line's list. Most of day two plays on return: a line must read right whether the
  player watched it happen or is reading it hours later. Never say when, in real time, anything happened, or how long
  anything took.
- **She:** her name is Lucy, given in l_name. Before l_name she has no name in any line. After it, "she" is the default
  and the name is for where "she" would be unclear. Her lines are what she does, in active voice; she is never grateful,
  never sweet, and never says much. She does not tire, get cold or go hungry in play: no line gives her a need the
  player could tend.
- **Must-nots (all lines):**
  - nothing about the ground being warm or glowing beyond what day one showed, nothing about the player's hands and
    heat;
  - never "again", or any hint of having been here or done this before;
  - never count her people, say how many she lost, or what happened to them;
  - the dark square on the ridge is never named before the offer (l_offer_1 is the first line that may say "cart"), and
    no line ever says it is gone from the ridge;
  - no wolves, and no animal at all, before B4's lines; the night's sound is a sound;
  - the you-said-yes line (l_yes) only after Go; no line judges either answer, and nothing on the other answer is
    about saying yes;
  - nothing comes back from the ridge: whoever walks brings only the news;
  - the stool only in l_stool_1, l_stool_2, l_name and l_morning_3;
  - no proper noun but Lucy; no Chequer, keels, holders, magic, faith, the burn.

## Voice exemplars (shipped)

Quoted as shipped, by key. Read them for voice; reuse no phrase from them. The opening:

| Key | Line |
|---|---|
| l_up_2 | knees under you this time. then not. |
| l_nail | under a fallen beam, a bent nail. you keep it. |
| l_strike_fail | you strike at the dry wood for a good while. it stays wood. |
| l_roast | roasted, they go soft enough to eat. you eat three. |
| l_stool | four legs, one of them short. you sit on it anyway. |
| l_retire | no more snapping dead wood by hand. the edge does it better, and it doesn't bleed. |
| l_dusk_2 | far off on the ridge, a light comes up that isn't yours. it doesn't move. it doesn't go out. |

Day one, which day two follows directly:

| Key | Line |
|---|---|
| l_night_1 | no sound from the ridge. the light stays low. |
| l_night_2 | one howl, a long way off. the air is so still you hear it end. |
| l_morning | morning. the ridge light is out. your fire lasted the night. |
| l_look_out_2 | where the light was, something dark and square. |
| l_snare_1 | the run you chose has a snare in it, rusted to flakes. |
| l_lean_to | birch poles, leaned. the open side faces the ridge. |
| l_lean_to_fail | the poles clack together and won't stand. |
| l_smoke_1 | no wind. the smoke stands straight up. you could steer by it. |
| l_prints_2 | three roots gone. smoked meat left, not yours. |
| l_b3_1 | you count the food twice. the count holds. you look up. |
| l_b3_2 | a figure comes out of the ash at the gap. alone. |
| l_b3_3 | she looks over the larder, then sits on your side of the fire. |
| l_b3_4 | she eats. you do sums for two. |
| l_camp_3 | seven fit on the wall. you know which seven. |
| l_tipped_birch | a birch has tipped over. stones came up in its roots. |
| l_lintel | you lever a lintel out of the rubble. the wall under it was holding nothing up. |

Day two picks up from l_b3_4: she has just arrived, eaten, and sits on the player's side of the fire. The player knows
nothing else about her. The ridge holds something dark and square where a light burned the first night.

## Lenses

`lenses.txt`, one per line (16). **The draw:** `python3 content/team/draw_lenses.py <task id> --writers 3`, seeded
from the task id. Task id `day-two-lines`:

| Writer | Lens |
|---|---|
| writer-1 | the oldest thing in it |
| writer-2 | what the animals already know |
| writer-3 | what a stranger would get wrong |

A lens is a way into the line, not a topic: a line that cannot take it plainly ignores it. writer-2's lens does not
lift the must-not on animals before B4.

## The states

Each key's states below are condensed from the report: the visit (V1 is the session B3 lands in), present or on return,
the story's clock (afternoon, evening, night, day 3), what is built, the offer (none yet, open, or answered Go or
she-goes), and her task. "Never on the ten routes" means the routes don't reach it in day two: write it true for any
state its gate allows, since later play does.

## The lines

Each entry: the moment, the beat (where there is one), the facts as attributes, the states, and anything special. "H"
marks a beat line: write an alternate too.

### The afternoon (V1)

All of V1's lines play present, in the grey afternoon, the same session B3 lands in, on every route. Nothing is built
yet; her task is foraging (the default).

**l_her_row** (no beat). Her row first shows under the player's own work: she is already at work. Facts: she has
gone to forage without being asked; roots are what she came for; she works beside the player, not for them.
Special: straight after B3's last line ("she eats. you do sums for two."). No name.

**l_her_first** (no beat). Her first finished task, within a minute. Facts: she comes back with what she went for and
puts it with the stores; the player's task card goes on. Special: the player may have changed her task at once, so the
line names no store and no task.

**l_her_rule** (no beat). The player gives her her first rule: any rule on her work other than her standing task
(usually the offered one: when the damp wood falls under 5, she cuts wood until 11; but any rule the player writes for
her fires it). States: V1 present on 6 routes (on one of them already day 3), V2 present (day 3) on 2. Special: names no store and no task; she
takes the instruction plainly, the way she does everything.

**l_stool_1** (A15, J1, H). The player gives her the stool. Fields: up · wry. Facts: the stool from day one; four legs,
one short; the player made it and has been sitting on it. Special: the giving is the player's own act (a card they
tapped).

**l_stool_2** (J1, H). Facts: it rocks under her; she wedges the short leg with a chip of stone; she doesn't remark on
it. Special: wry; the wedge is her answer to the joke, not a fix.

**l_name** (J1, H). Fields: up · wry · opens the near question (what is up on the ridge?). Canon C-beat-81. Facts: she
gives her name, Lucy, plainly, in return for the stool; then she looks at the ridge a long time. Special: the first
time the name appears anywhere; the look is the hook, never explained. Nothing about who she is beyond the name.

### The evening, the second night, the morning (V1 → V2)

On 9 of 10 routes these four play together on return, in the morning of day 3, before anything else of V2; on one
they play present as the light goes. Nothing built; her task foraging.

**l_evening_2** (no beat). Dusk, a quarter hour after the stool. Facts: the grey goes; the two of them at the fire;
the floor's cracks glow as they did the first night (nothing new about them). Special: day one's dusk line said the
glow in full; this one doesn't describe it again, and doesn't say "again".

**l_night_2a** (J2, H). Fields: down · dread · advances the near question. Canon C-beat-82. Facts: the two at the
fire, she on the player's side; a sound carried down from the ridge on air with no wind in it: wood dragged on stone, a
long scrape. Special: a sound, nothing more: no animal, no cause, no cart.

**l_night_2b** (J2, H). Facts: then nothing; she heard it too and says nothing. Special: the turn is in her silence;
never say what she thinks.

**l_morning_3** (J3, H). Fields: up · wry · cost time. Canon C-beat-83. Facts: a grey morning; she was up before the
player; the fire has been fed; the stool's wedge is out and it rocks. Special: heads the unwrap of what two got done
in a night; true for a one-hour night and a day-long absence alike. No "again".

### Making room (V2)

**l_make_room_fail** (failed line). Make room tapped before first light. States: never on the ten routes; derived:
night 2, after J2's lines, nothing built. Special: nothing can be built in the dark; wry about trying.

**l_room_1** (A16, J4, H). Fields: up · yes_but · warm · cost option. Canon C-beat-84. Facts: one cover, two people:
she slept by the fire in the open; the player's lean-to is the only shelter. States: V2 present, day 3, nothing built
(V1 present on one route). Special: the player notices; no one says it.

**l_room_2** (J4, H). Facts: two things to build, one at a time: a shelter for her, and a woodstack. Special: the order
is the choice; name neither upside, and don't say which comes first.

**l_shelter** (A17, H). Facts: a shelter of green birch poles and two stones; small, lower than the lean-to, beside it,
its back to the wall; she has a roof of her own. States: on return on 9 routes, present on one; the woodstack built (7)
or not (3). Special: the offer's lines follow at once on every route, so this line leads into her asking without
asking for her.

**l_woodstack** (A18). Facts: a woodstack on a stone footing by the wall; room to keep twice the dry wood. States: on
return on 7 routes, present on one; the shelter is already built on every route that reached it (but a player may
build it first: true either way).

**l_shelter_fail**, **l_woodstack_fail** (failed lines). Tapped unready: the shelter short of damp wood (needs 12) or
stones (2); the woodstack short of stones (10) or dry wood (4). States: never on the ten routes; derived: day 3, the
other build done or not. Special: true whichever input is short.

### The offer and the walk (V2–V4)

**l_offer_1** (O-cart, H). Canon C-beat-85. Facts: with a roof of her own she means to stay; she says so by asking
something. States: straight after l_shelter, on return on 9 routes (present on one); the woodstack built or not.

**l_offer_2** (O-cart, H). Facts: she asks the player to fetch her people's cart from the ridge; either answer is fine
to her. Special: the first line that may say "cart" or connect the ridge's dark square to her. The cart is hers to
believe in: the narration never says it is still up there (the night's sound was it going), only that she asks. Never count her people,
never say what became of them. The row below carries the two answers (go, or she goes); the line doesn't list them.

**l_yes** (H). Answered Go. The first you-said-yes line (C-promise-7, C-motif-4): every job is an offer the player picks,
declining costs nothing, and these lines land only after the player's yes. Facts: she is looking at the player. States:
present, day 3, on 6 routes; the woodstack built or not. Special: dry, about the player's own choice; not a judgment of
either answer; never "you said yes. of course you did." or anything close to it.

**l_walk_go** (A19, Go). Straight after l_yes. Facts: the player at the gap facing out; the ridge ahead. Special: the walk
is queued, so it may start now or after what the hands are doing: the line is the setting out, not the walking.

**l_she_goes** (A19, she goes). Facts: she leaves through the gap toward the ridge; her own work waits. States: present
on 3 routes, on return on 1 (answered by a standing answer while the player was away). Special: no judgment of the
choice; she goes the way she does everything.

**l_walk_out**, and **l_walk_out_2** to **l_walk_out_4** an hour apart after it (D-104), under the same rules (no beat). Part-way through the walk, on either answer. States: on return on 9 routes (Go 5, she goes
4), present on one (Go). Facts: the walk is hours long; whoever walks is well on the way, out of sight of the camp;
nothing yet known. Special: **one line true on both answers**: on Go the player is the one walking, on the other the
player is at the fire. So no "you" walking and no "she" walking; the camp, the gap, the ridge or the waiting are fair.

### B4 (V3–V5)

B4 lands when the walk is done. On every route that reaches it, it plays on return (one route present). The camp
behind: both builds done (most) or the woodstack still to build. One set or the other plays, by the answer.

**l_b4_1** to **l_b4_4** (B4, went, H each). Fields: down · no_and · grim · cost time · pays the near question.
Canon C-beat-4, C-beat-85. Facts, in order across the four: the place on the ridge where the cart stood; drag marks off
over the edge; wolf prints all round it; back at the fire, she takes the news without a word. Special: the first
wolves in day two, as prints only; nothing comes back; l_b4_4 ends the day: no hook sentence, no question.

**l_b4_h1** to **l_b4_h3** (B4, she went, H each). Fields as above. Facts: she walks back in through the gap with
nothing; she sits; she says nothing, and the player reads it off her. Special: the player didn't see the ridge, so no
line describes it, the prints or the wolves; what she does carries it all. l_b4_h3 ends the day, as l_b4_4.

### The Camp

**l_camp_7** (level). The wall takes nine to dry where it took seven. States: on return, V2 (3 routes, nothing built) or
V3 (6 routes, the shelter built). Special: like day one's camp lines (the camp getting known, not grand); the camp is
two now.

**l_camp_8** (level, lifted by B4). The catch holds half as much more. States: with B4 or on the return after it, on
either answer. Special: plain; may follow B4's last line, so nothing that answers or softens it.

### Finds (levels)

Each is a find by the player's own work at a skill level, paid as stores. States: by the mix, any visit after B3, in
day two or later; the routes reach only two in day two (l_flagged_floor V3 on return, l_straight_poles V5 on return).
Special: never the ridge, the cart, wheels or anything a cart carries; no warm ground; plain, like day one's finds
(l_tipped_birch, l_lintel above).

| Key | Skill, level | Facts | Pays |
|---|---|---|---|
| l_seed_stand | Foraging 9 | a stand of roots gone to seed, by an old field wall | roots |
| l_lichen | Foraging 12 | lichen thick on a north-facing stone; it goes into the roast | roots |
| l_clay_bank | Foraging 15 | a bank of soft clay by the warm stream; roots in it | roots |
| l_old_bed | Foraging 18 | an old bed of roots, gone wild | roots |
| l_wet_hollow | Foraging 21 | a wet hollow, roots thick in it | roots |
| l_root_mat | Foraging 24 | a mat of roots so dense it lifts in one piece | roots |
| l_flagged_floor | Scavenging 18 | a flagged floor under the ash | stones |
| l_fallen_gable | Scavenging 21 | a fallen gable, its timbers whole | damp wood |
| l_dressed_kerb | Scavenging 24 | a kerb of dressed stone | stones |
| l_straight_poles | Woodcutting 21 | a stand of straight young birch, good for poles | damp wood |
| l_root_plate | Woodcutting 24 | a birch root plate torn up whole, stones in its grip | stones |
| l_tighter_rack | Cooking 8 | the knack of packing the smoking rack tighter: one more strip a batch | a faster rack |

l_clay_bank: the clay is only where the roots are; nothing is made of it. l_tighter_rack: day one's l_cooking_2 ("you
get the knack of packing the rack. more fits.") already said packing; find another way in.

## Labels: the voice pass's, not the writers'

These keys are UI, written in the voice pass with the opening's and day one's labels beside them (card names are
imperatives, upsides short phrases naming the effect, stores and skills plain nouns, level pays short noun phrases):

- **Her row:** lane_n1 (before her name: no name), lane_n1_named (after l_name)
- **Cards:** c_give_stool, c_make_room, c_build_shelter, c_build_woodstack, c_walk_ridge (the player's walk),
  c_n1_walk_ridge (hers)
- **Upsides:** up_shelter (she works a fifth faster), up_woodstack (room for twice the dry wood)
- **The offer row:** o_cart (the question on the row, under her lines), a_go, a_she_goes (the answers), a_go_cost,
  a_she_goes_cost (each answer's time; `{d}` is filled with the walk's duration, as `ui.ledger.fills` does)
- **Aims:** aim_night_2 (get the two of you through the night), aim_room (give her a place of her own here), aim_cart
  (bring back what she left up there), aim_after (keep the camp worth keeping, now that something knows where it is).
  Day one's are in `day_one.toml` (`aim_two`: "lay in enough for both of you.").
- **The end card:** dayend2_title, dayend2_1, dayend2_2: out of fiction, "this is as far as it goes for now", on day
  one's end card's pattern (`dayend_*`). dayend2_2 replaces day one's "still being written" line, which is dropped at
  release.
- **Level pays:** pays_seed_stand, pays_lichen, pays_clay_bank, pays_old_bed, pays_wet_hollow, pays_root_mat,
  pays_flagged_floor, pays_fallen_gable, pays_dressed_kerb, pays_straight_poles, pays_root_plate, pays_tighter_rack
- **Never drawn:** store_evening_2, store_night_2, store_walk, store_walk_out, store_n1_worked, action_evening_2,
  action_night_2, action_walk_out. No route shows them. Confirm each stays hidden; the labels still ship in the content
  payload, so each gets a plain label that spoils nothing (as day one's `store_h7_clock`).

Two to check before anything else:
- **o_cart and the answers** sit on screen until answered, often across a whole absence. Neither answer may read as the
  right one; the costs are the same time.
- **lane_n1** is on screen through all of V1 before l_name; it names her role or her work, never her.
