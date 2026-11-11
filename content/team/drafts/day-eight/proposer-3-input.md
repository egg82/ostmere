# Proposer writer-3 input: day eight's lines (B8 to B9)

You are writing day eight's lines. This file is all you may see from the project's content; read nothing else.

## Your lens

what the animals already know

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

---

# Day eight's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `week-two.md`; the data is
`app/ashfall_app/opening/day_eight.toml`, where every key below reads "[day two: line to write]" (the marker's spelling is
the data file's; ignore it). The brief's design states are an expectation; the generated states below replace them.

## How the lines get written

Three blind proposers (Sonnet), one lens each (below), every key plus one alternate per key marked H; a critic scores the
drafts blind on `rubric.md` plus *true in every listed state?*; the lead picks line by line; code checks length, the
must-nots as a scan, and three-word echoes against content prose and every shipped line before them; a fresh agent's
voice pass reads every picked line and label in player order and writes the labels.

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases.

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase, plain. One or two short sentences. A turn the
  reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, per chapter; no line over 75.
- **True in every state.** Most of this plays on return. Never say when, in real time, anything happened, or how long it
  took.
- **People:** Lucy by name; him as `{n2}`; the pair as `{n3}` and `{n4}`; the family as "the woman", "her husband", "her
  brother" until l_join3_1 gives `{n5}`, `{n6}` and `{n7}`; the stranger only ever as "the man who came with them" or
  "him" where clear, **never named, never a slot**. What each does, in active voice. Lucy never grateful, never sweet,
  never says much. Light-tier people are ordinary: no backstory past what they carry.
- **Fights:** plain, one short line, won or lost, never gory, never dwelling on how a beast dies; hunting and skinning
  told as a way of life. The page writes a long absence's count line; write the pools below.
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
  - never count who the family lost or say who; never say they are missing anyone outright; never a child;
  - the cellar: no count matches anything; never "tally" as a Chequer word; the stool line obeys the stool's rules (one
    stool line in a day's unwrap, never in a dark moment's own line, never named as a pattern);
  - the burning: plain, no body described, no smell; the hand on the warm ground is someone's, unnamed, and means nothing
    a line says;
  - no line judges either answer to O-family or O-guard;
  - no proper noun but Lucy and the name slots.

## What the earlier passes taught (read before writing)

From day one's and day three's voice passes and the lead's picks. Each cost a line its place:

- **Do not lift the brief's fact phrases.** Every draft of day three copied the spec's words ("frost greys everything",
  "a stick at a time"); the facts are attributes, not wording. Say it your own way.
- **A line must be true in every state that fires it, and the state lists below are the typical route's.** Read the
  "fires with" column of the wiring table: lines that fire at the same moment cannot contradict each other (a fire "lit"
  in one line while the other fires before it is lit was false), and a line that fires on return cannot say "as the
  light goes" or "just now".
- **A failed-card line fails on whichever input is short.** The wiring table lists every input and requirement of the
  card; a line naming one store ("not enough wood") is false when another is short, and a card that fails on a night or a
  skill never fails on stuff. Say only what is true whichever is short; a card shared with another person's task gets
  no "you".
- **A stage line is one of a card's stages (1 of 3, ...): do not say "again", do not repeat the stage before, and do not
  open two stages the same way.** A stage that cannot be finished yet is not "finished": the last stage line is shown
  when its stage begins to dry or cure, not when it is done.
- **Do not repeat a word the neighbouring line uses at the same moment** ("keep", "quiet", "larder" back to back).
  Lines that fire in one visit sit next to each other on screen.
- **Do not carry a card's label or upside into its line.** You are not shown the labels; do not describe the effect
  ("a bigger batch", "faster", "more").
- **The two answers of a choice are mirrors.** Neither reads as right, neither is the one with the better line; give
  both the same frame and length.
- **Name a thing one way throughout** ("the walk" vs the card's "run the track" read as two things).
- **Hard limit: no line is over 75 characters** (`app/tests/opening/test_line_length.py`, applied to every `l_` line;
  a line over fails CI and goes back). The set's median should stay at 45 or under. Count characters before sending;
  most lines should be well under.
- **Voice notes (day one's pass):** a line that echoes its own level label or another line shown in the same instant is
  changed first; "again" is a must-not even as "half as much again"; the stomach is not the stores.

## Voice exemplars (shipped, verbatim)

Read them for voice; reuse no phrase from them.


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

## Lenses

| Writer | Lens |
|---|---|
| writer-1 | the day after |
| writer-2 | what gets written down, and what doesn't |
| writer-3 | what the animals already know |

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, and anything special.
Keys named in the entries below that the data file spells differently are listed under "Brief names" at the end.

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

### Fights and finds (this chapter's)

**The fight pools.** The pack at the gap has a pool of lines for one fight won and one lost; the page shows one line per
fight, the runner's lines drawn in a shuffled order (each once before any repeats), so any line may follow any other, the
same line may come twice in a day, and the number of fights before it is anyone's. Write **three lines per pool**, as `_1`,
`_2` and `_3`:
- **l_fight_pack_won_1..3**, **l_fight_pack_lost_1..3**: the pack at the gap, one plain line each; a lost one says only
  what is gone from the rack.

A pool line is one fight, plain and short, never gory, never dwelling on how a beast dies. It carries no count, no
"again", no "another", no "this time", no real-time word, and no name.

**l_find_shelf** (Foraging 13), **l_find_pole** (Woodcutting 23), **l_find_hoe** (Scavenging 23), **l_find_pot**
(Cooking 9), **l_find_fine_ash** (Arcana 11): one line each, by the mix, any visit. No find names a wolf sitting, the
stone's heat past what the hand does, the cellar before B12, or anything of week 3.

## Where each key plays (read from the data file; "fires with" lines share one moment on screen)

| key | where it plays (from the data file) |
|---|---|
| l_ring_scored | trigger t_ring_scored when feature still_end unlocked |
| l_palisade_fail | failed-card line of card palisade (craft; lane -); inputs stakes x24, cord x4, stones x6 |
| l_stage_1 | stage line 1 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_2 | stage line 2 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_3 | stage line 3 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_4 | stage line 4 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_5 | stage line 5 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_6 | stage line 6 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_7 | stage line 7 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_8 | stage line 8 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_9 | stage line 9 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_10 | stage line 10 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_11 | stage line 11 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_stage_12 | stage line 12 of 12 of card palisade (craft; inputs stakes x24, cord x4, stones x6) |
| l_cut_stakes_fail | failed-card line of card cut_stakes (action; lane -); inputs damp_wood x4 |
| l_lane_stakes_fail | failed-card line of card {lane}_stakes (action; lane ['n1', 'n2']); inputs damp_wood x4 |
| l_cord_fail | failed-card line of card twist_cord (action; lane -); inputs damp_wood x2 |
| l_n4_cord_fail | failed-card line of card n4_cord (action; lane n4); inputs damp_wood x2 |
| l_flaps_fail | failed-card line of card hide_flaps (craft; lane -); inputs pelt x2, damp_wood x4 |
| l_flaps_1 | stage line 1 of 4 of card hide_flaps (craft; inputs pelt x2, damp_wood x4) |
| l_flaps_2 | stage line 2 of 4 of card hide_flaps (craft; inputs pelt x2, damp_wood x4) |
| l_flaps_3 | stage line 3 of 4 of card hide_flaps (craft; inputs pelt x2, damp_wood x4) |
| l_flaps_done | stage line 4 of 4 of card hide_flaps (craft; inputs pelt x2, damp_wood x4) |
| l_b8_1 | trigger t_b8 when the clock reaches 168 h; fires with l_b8_2, l_b8_3 |
| l_b8_2 | trigger t_b8 when the clock reaches 168 h; fires with l_b8_1, l_b8_3 |
| l_b8_3 | trigger t_b8 when the clock reaches 168 h; fires with l_b8_1, l_b8_2 |
| l_pick_fail | failed-card line of card pick_fungus (action; lane -); inputs bloom x1 / failed-card line of card {lane}_pick (action; lane ['n3']); inputs bloom x1 |
| l_fungus_stew_fail | failed-card line of card fungus_stew (action; lane -); inputs fungus x6, dry_wood x1 |
| l_howls | trigger t_howls when store drift_clock >= 6 |
| l_caps_1 | trigger t_caps when card fungus_stew done >= 1; fires with l_caps_2 |
| l_caps_2 | trigger t_caps when card fungus_stew done >= 1; fires with l_caps_1 |
| l_ash_laden | chip ash_laden line when it shows |
| l_ash_cleared | chip ash_laden line when it clears (it heals by itself) |
| l_clear_fail | failed-card line of card clear_roofs (action; lane -); inputs roof_ash x16 / failed-card line of card n2_clear_roofs (action; lane n2); inputs roof_ash x16 |
| l_roofs_first | trigger t_roofs_first when store ash >= 4 |
| l_ash_ground | trigger t_ash_ground when store drift_clock >= 12; requires feature roofs_cleared unlocked |
| l_ash_ground_fail | failed-card line of card n3_ash_ground (action; lane n3); inputs ash x4 |
| l_cord | trigger t_cord when store drift_clock >= 14; requires feature cord_made unlocked |
| l_pack_1 | trigger t_pack when store drift_clock >= 12; requires feature pack_near unlocked; fires with l_pack_2 |
| l_pack_2 | trigger t_pack when store drift_clock >= 12; requires feature pack_near unlocked; fires with l_pack_1 |
| l_fight_pack_won_1 | pool of lines for one fight won, of pack (side gap against wolf_pack); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_fight_pack_won_2 | pool of lines for one fight won, of pack (side gap against wolf_pack); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_fight_pack_won_3 | pool of lines for one fight won, of pack (side gap against wolf_pack); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_fight_pack_lost_1 | pool of lines for one fight lost, of pack (side gap against wolf_pack); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_fight_pack_lost_2 | pool of lines for one fight lost, of pack (side gap against wolf_pack); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_fight_pack_lost_3 | pool of lines for one fight lost, of pack (side gap against wolf_pack); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_b9_1 | trigger t_b9 when entry e_wolf unlocked; requires entry e_ashrat unlocked; entry e_crow unlocked; feature wolves unlocked; fires with l_b9_2 |
| l_b9_2 | trigger t_b9 when entry e_wolf unlocked; requires entry e_ashrat unlocked; entry e_crow unlocked; feature wolves unlocked; fires with l_b9_1 |
| l_find_shelf | trigger t_find_for_13 when skill_level foraging >= 13; requires feature drift unlocked |
| l_find_pole | trigger t_find_wc_23 when skill_level woodcutting >= 23; requires feature drift unlocked |
| l_find_hoe | trigger t_find_scav_23 when skill_level scavenging >= 23; requires feature drift unlocked |
| l_find_pot | trigger t_find_cook_9 when skill_level cooking >= 9; requires feature drift unlocked |
| l_find_fine_ash | trigger t_find_arc_11 when skill_level arcana >= 11; requires feature drift unlocked |
| l_camp_13 | camp level at 1200000 items |

## Generated states (the simulator's `--lines` over the typical, sharp, babysitter and whenever routes; replaces the brief's expected states where they differ)

Visit numbers count from the first visit of the chapter's pass, per route (a find can fire in a later chapter's visits). 'present' = the player is there when it happens; 'on return' = reads it after an absence. A line must read right in every listed combination. The answers listed are everything answered so far in the whole week, not only this chapter's.

| key | where it showed (route, visit, present or on return) | state |
|---|---|---|
| l_ring_scored | babysitter V1 present | sharp V1 present; typical V1 present; whenever V1 present; capped done 45-47; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-2 |
| l_palisade_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_stage_1 | babysitter V1 present | sharp V3 on return; typical V5 on return; whenever V6 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_stage_2 | sharp V7 on return | typical V7 on return; whenever V8 on return; capped done 47-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_stage_3 | sharp V9 on return | whenever V10 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_stage_4 | whenever V11 on return | capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_stage_5 | never shown on any simulated route (design expectation in the brief applies) | |
| l_stage_6 | never shown on any simulated route (design expectation in the brief applies) | |
| l_stage_7 | never shown on any simulated route (design expectation in the brief applies) | |
| l_stage_8 | never shown on any simulated route (design expectation in the brief applies) | |
| l_stage_9 | never shown on any simulated route (design expectation in the brief applies) | |
| l_stage_10 | never shown on any simulated route (design expectation in the brief applies) | |
| l_stage_11 | never shown on any simulated route (design expectation in the brief applies) | |
| l_stage_12 | never shown on any simulated route (design expectation in the brief applies) | |
| l_cut_stakes_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_lane_stakes_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_cord_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_n4_cord_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_flaps_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_flaps_1 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V2 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_flaps_2 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V8 on return; capped done 47-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_flaps_3 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V8 on return; capped done 47-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_flaps_done | babysitter V1 present | sharp V2 on return; typical V3 on return; whenever V9 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_b8_1 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V3 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_b8_2 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V3 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_b8_3 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V3 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_pick_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_fungus_stew_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_howls | babysitter V1 present | sharp V4 on return; typical V3 on return; whenever V4 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_caps_1 | babysitter V1 present | sharp V3 on return; typical V3 on return; whenever V4 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_caps_2 | babysitter V1 present | sharp V3 on return; typical V3 on return; whenever V4 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_ash_laden | babysitter V1 present | sharp V5 on return; typical V3 on return; whenever V5 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_ash_cleared | babysitter V1 present | sharp V6 on return, V9 on return; typical V4 on return, V5 on return, V6 on return, V8 on return; whenever V6 on return, V8 on return, V9 on return, V11 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_clear_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_roofs_first | babysitter V1 present | sharp V6 on return; typical V4 on return; whenever V6 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_ash_ground | babysitter V1 present | sharp V7 on return; typical V4 on return; whenever V6 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_ash_ground_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_cord | sharp V8 on return | typical V4 on return; whenever V6 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_pack_1 | babysitter V1 present | sharp V9 on return; typical V7 on return; whenever V11 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_pack_2 | babysitter V1 present | sharp V9 on return; typical V7 on return; whenever V11 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_fight_pack_won_1 | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_pack_won_2 | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_pack_won_3 | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_pack_lost_1 | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_pack_lost_2 | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_pack_lost_3 | never shown on any simulated route (design expectation in the brief applies) | |
| l_b9_1 | babysitter V1 present | sharp V9 on return; typical V8 on return; whenever V11 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_b9_2 | babysitter V1 present | sharp V9 on return; typical V8 on return; whenever V11 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_find_shelf | never shown on any simulated route (design expectation in the brief applies) | |
| l_find_pole | never shown on any simulated route (design expectation in the brief applies) | |
| l_find_hoe | never shown on any simulated route (design expectation in the brief applies) | |
| l_find_pot | never shown on any simulated route (design expectation in the brief applies) | |
| l_find_fine_ash | never shown on any simulated route (design expectation in the brief applies) | |
| l_camp_13 | babysitter V1 present | sharp V7 on return; typical V5 on return; whenever V5 on return; capped done 46-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |

## Keys the brief does not spell out

No beat facts: write from the wiring table. Failed-card lines (`*_fail`, `*_dry`): what the card shows when tapped with the cost short; the player's try (or the person's), short of the means; one short line; no number. Stage lines: the card's stages in order, same register as the shipped stage lines of day two and three.

Keys: l_palisade_fail, l_stage_6, l_stage_7, l_stage_8, l_stage_9, l_stage_10, l_stage_11, l_cut_stakes_fail, l_lane_stakes_fail, l_cord_fail, l_n4_cord_fail, l_flaps_fail, l_flaps_1, l_flaps_2, l_flaps_3, l_flaps_done, l_pick_fail, l_fungus_stew_fail, l_ash_laden, l_ash_cleared, l_clear_fail, l_ash_ground_fail

## Output

A TOML file, `key = "line"` per key below, in this order, lowercase, plain. Keys marked H also get `key_alt = "line"` right after. A draft missing an alternate is sent back. Every line within 75 characters; no digit; a name slot only as the rule above allows.

Keys (54, in order): l_ring_scored, l_palisade_fail, l_stage_1, l_stage_2, l_stage_3, l_stage_4, l_stage_5, l_stage_6, l_stage_7, l_stage_8, l_stage_9, l_stage_10, l_stage_11, l_stage_12, l_cut_stakes_fail, l_lane_stakes_fail, l_cord_fail, l_n4_cord_fail, l_flaps_fail, l_flaps_1, l_flaps_2, l_flaps_3, l_flaps_done, l_b8_1, l_b8_2, l_b8_3, l_pick_fail, l_fungus_stew_fail, l_howls, l_caps_1, l_caps_2, l_ash_laden, l_ash_cleared, l_clear_fail, l_roofs_first, l_ash_ground, l_ash_ground_fail, l_cord, l_pack_1, l_pack_2, l_fight_pack_won_1, l_fight_pack_won_2, l_fight_pack_won_3, l_fight_pack_lost_1, l_fight_pack_lost_2, l_fight_pack_lost_3, l_b9_1, l_b9_2, l_find_shelf, l_find_pole, l_find_hoe, l_find_pot, l_find_fine_ash, l_camp_13

H keys (alt required): l_b8_1, l_b8_2, l_b8_3, l_howls, l_caps_1, l_caps_2, l_pack_1, l_pack_2, l_b9_1, l_b9_2

## Shipped lines of the chapter before (day-six)

{{PREVIOUS_PICKS}}

(The lead fills this with the previous chapter's shipped lines before the proposers start; reuse no phrase from them.)
