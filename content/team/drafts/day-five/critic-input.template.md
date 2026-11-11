# Critic input (template): day five's lines (the stone and the pair)

Fill the three DRAFT blocks with the proposers' TOML, labelled A/B/C in shuffled order; do not say which lens wrote which.

You score the three drafts blind on the rubric below, plus one row: *true in every listed state?* (quote the state a line breaks). Check each line against the brief's rules and must-nots, and the 75-character limit. Score per key per draft; name the best of the three per key and why in a clause.

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

# Day five's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `days-four-to-seven.md`; the data is
`app/ashfall_app/opening/day_five.toml`, where every key below reads "[day two: line to write]" (the marker's spelling is
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
- **True in every state.** Most of this plays on return. Never say when, in real time, anything happened, or how long
  it took.
- **People:** Lucy by name where "she" would be unclear; him as `{n2}`; the pair as "she" and "the old man" until
  l_join2_2 gives `{n3}` and `{n4}`. What each does, in active voice. Lucy never grateful, never sweet, never says
  much; no line gives anyone a need the player could tend. Light-tier people are ordinary: no backstory past what they
  carry.
- **Fights** (B7 and day six): plain, one short line, won or lost, never gory, never dwelling on how a beast dies;
  hunting and skinning told as a way of life.
- **Must-nots (all lines):**
  - no "magic", "spell", "mage", "arcana", Chequer, keels, holders, faith, the burn, Drift or any season name;
  - after B6, the stone may do what the player's hand does with it (wood steams dry, stones come up hot); never why,
    never what it costs, never that it is alive, breathing or anyone's; the ash on the fingers is B6's alone;
  - never "again", or any hint of having been here before; never that the camp stone was cut or set;
  - no wolf at the edge of the firelight before B7's lines; L2 is a kill and prints, M2 is shapes at a distance;
  - never count who anyone lost or say what happened to them; never count her people or theirs;
  - no line judges either answer to O-pair or `o_pelt`; on either answer they stay, and the ground is the same;
  - nothing in any line may imply the old man is ill, failing or in danger, nor that he is safe: what he does, only;
  - G2's wind is weather felt, never a warning and never what comes next;
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
- **A person's name is a slot.** `{n2}` (the man who joined on day three), `{n3}` (the woman) and `{n4}` (the old man)
  are filled by the page with that person's name, lowercased inside a line. A line may say `{n2}`, `{n3}` or `{n4}` where
  the design below names that person, and only once that person has joined in every state the line shows in: `{n2}` from
  day four on, `{n3}` and `{n4}` only at or after l_join2_2 (the pair is "she" and "the old man" before it, and in any
  line that can show before the pair has joined). The wiring and states tables show when each line fires. Where a line is not sure to have the person joined, write "he", "the
  woman" or "the old man". Write the slot exactly (`{n2}`, no spaces, no other braces); never invent a name; Lucy stays
  the one name written out. The line-length limit counts a slot as the name it shows (about six letters), and a line
  holds no digit.
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

Day three, which day four follows directly (every shipped line of it):

| Key | Line |
|---|---|
| l_track_end_fail | you lose the track past the cairn. not yet. |
| l_edge_1 | scrub, thorn, thorn, a sunk track. the camp is easy to find. |
| l_edge_2 | the ash is thinnest where you started. you check twice. |
| l_track_fail | not enough laid by for a run. |
| l_track_first | a run: out on the laid wood to the cairn, and back. |
| l_stream | ash everywhere but the water. the clay on the bank is warm. |
| l_field_1 | you laid the track all this way for furrows. |
| l_field_2 | the track's whole yield: a rusted ploughshare. scrap. |
| l_floor_fail | you lay out a floor and run short. |
| l_larder_1 | a course of stone, so the roots stop sitting in wet. |
| l_larder_2 | a second course, flat enough to set a root on. |
| l_larder_3 | the last course is laid. level, give or take. |
| l_larder_done | lucy moves two roots, and looks at the rows. |
| l_roof_fail | the roof takes more wood than this. |
| l_roof_1 | poles go up over the drying wall. |
| l_roof_2 | thatch of anything at all. it shows. |
| l_roof_done | rain runs dark off the roof. what hangs under it stays pale. |
| l_hearth_fail | the next course won't go down yet. |
| l_cure_fail | there's no new course to dry. |
| l_hearth_1 | one course of clay. a mud ring, so far. |
| l_hearth_2 | more clay, pressed onto the dry course. |
| l_hearth_3 | a third course. everyone steps round it to the fire. |
| l_hearth_done | the fourth course goes on. a whole hearth, drying. |
| l_stew_fail | too little to fill the pot. |
| l_stew_first | the first pot of stew. lucy eats hers standing. |
| l_night_3a | two howls trade across the dark, closer in. |
| l_night_3b | lucy piles on wood without a word. nothing comes. |
| l_morning_4 | frost out to the thorn. the stone stays dark. |
| l_watch_1 | lucy lays stones at the gap. she brings more. |
| l_watch_2 | room inside for a fire, facing down the track. |
| l_watch_fail | the gap stays bare for now. |
| l_watch_lit | lucy keeps her fire, stick by stick, looking out. |
| l_watch_dry | no dry wood to feed her fire. |
| l_night_4 | nightfall. three bowls, and the pot scraped. |
| l_bank_hearth_fail | not yet. the hearth can wait. |
| l_b5_1 | you bank the new hearth. round it, the ash melts away. |
| l_b5_2 | the ground is warm. all three of you sit down. |
| l_b5_3 | faint red in the cracks. nobody gets up for more wood. |
| l_stay_1 | a man at the light's edge, nose toward the pot. |
| l_stay_2 | he's alone. his spear has no head. can he stay? |
| l_bay_go | you start a bay off the lean-to. |
| l_bay_his | he starts the bay himself. he doesn't ask where. |
| l_bay_help | he holds the poles steady while you tie them. |
| l_bay_fail | the bay needs more than you have. |
| l_join_1 | he sits. lucy looks at him once, then works on. |
| l_join_2 | he says his name. the stores go three ways now. |
| l_his_first | he's at work before anyone tells him. |
| l_scrap_ask | he picks through what's piled up. he raises his spear, lowers it. |
| l_bank_1 | she'd cover it in ash. he'd set stones round it. |
| l_bank_hers | ash over the coals, her way. he eyes the wood. |
| l_bank_his | a ring of stones, his way. she eyes the wood. |
| l_camp_9 | eleven go on the wall, if they don't lean. |
| l_camp_10 | twenty-seven in the smoke, and three to eat them. |
| l_clay_seam | a seam of clay in the bank, grey and deep. |
| l_lee_lichen | lichen in a cairn's lee, scraped off for the pot. |
| l_buckle | a buckle in the ash. no belt, but a good buckle. |
| l_thick_pot | a thick-walled pot, whole. it will take stew. |
| l_stack_fail | the stack won't go up yet. |
| l_stack_1 | stones in two rows, with room for wood across. |
| l_stack_2 | damp wood piled on the stones, bark side up. |
| l_stack_3 | the stack stands clear. the bottom logs stay dry. |
| l_shelf_fail | no shelf yet. the pots sit on the ground. |
| l_shelf_1 | a flat stone set, then another. |
| l_shelf_2 | boards of damp wood laid across the stones. |
| l_shelf_3 | the pots go up, out from underfoot. |

## Lenses

| Writer | Lens |
|---|---|
| writer-1 | what a stranger would get wrong |
| writer-2 | what it costs the people |
| writer-3 | what the hands are doing |

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, and anything special.
Keys named in the entries below that the data file spells differently are listed under "Brief names" at the end.

### Day five: the stone and the pair (X1-X5)

**l_stone_first** (`hand_on_stone`'s first completion). Facts: the player's hand on the stone, deliberately; the wet
wood steams and comes away dry. Special: the first time on purpose; no word for what it is.

**l_morning_6**. Facts: the fog thins to haze.

**l_ridge_1, l_ridge_2** (M2, H). Fields: down · dread · opens the near question. Canon C-beat-97. Facts: midday; on
the ridge where the cart stood, grey shapes sitting in a row facing the camp; when Lucy looks up they are gone. States:
day 6, on return mostly. Special: shapes; "grey" and "sitting" carry it; no "wolf".

**l_arcana_2** (SL9, a find). Facts: wood on the drying wall where the stone shows through the ash dries first.

**l_pair_1, l_pair_2** (O-pair, H). Canon C-beat-98. Facts: two at the fire's edge out of the haze; a woman with a sack
over her shoulder; an old man on her arm, his leg straight; she asks if the fire is theirs to share. States: stew just
reached 9; present or on return; sits on screen until answered. Special: neither answer may read as the right one.

**l_bay2_go, l_bay2_hers** (each answer's build starts). Facts: the player's hands start a second bay / she starts it
herself, the old man handing her stones.

**l_join2_1, l_join2_2** (M1, H). Fields: up · yes_but · warm · stores. Canon C-beat-99. Facts: they take their places;
the old man lowers himself onto the stool Lucy brings without looking at it; the woman gives both names (said by neither line: no name slot); five at the fire; the pot goes round twice and comes back light. Special: the yes_but is the pot,
said as a fact.

**l_seed** (SL10). Facts: the woman turns a strip of ground at the stone's edge with a flat stone, edges it, lays seed out on
a cloth in rows, and ties it up again unplanted. Special: no reason, no hope said.

**l_old_watch** (SL11). Facts: the old man settles at Lucy's watch fire with his leg out straight and feeds it; Lucy stands
there a while, then goes back to the roots.

**l_stones_1..3** (`hearth_stones` stages). Facts: stones lifted off the camp stone hot, set round the pot.

**l_night_6** (night 6's first item). Facts: five round the fire; the player banks it for the night. States: present
mostly (A29 follows).

### Arcana levels (this chapter's)

**l_arcana_5** (Arcana 5, a find: the hand on the stone dries a little wood, +dry wood; the brief's `l_find_dry_kindling`),
**l_arcana_6** (Arcana 6, the level's speed-up: the smoking catches more). One line each, by the mix, any visit; never
wolves at the camp's edge, never the stone's heat past what the player's hand does, nothing of week 2.

To check first: **o_pair** sits on screen across absences and neither answer may read as the right one.

## Where each key plays (read from the data file; "fires with" lines share one moment on screen)

| key | where it plays (from the data file) |
|---|---|
| l_stone_fail | failed-card line of card hand_on_stone (action; lane -); inputs damp_wood x6 |
| l_stone_first | trigger t_stone_first when card hand_on_stone done >= 1 |
| l_stones_fail | failed-card line of card hearth_stones (craft; lane -); inputs stones x12, clay x4 |
| l_stones_1 | stage line 1 of 3 of card hearth_stones (craft; inputs stones x12, clay x4) |
| l_stones_2 | stage line 2 of 3 of card hearth_stones (craft; inputs stones x12, clay x4) |
| l_stones_done | stage line 3 of 3 of card hearth_stones (craft; inputs stones x12, clay x4) |
| l_arcana_2 | trigger t_arcana_2 when skill_level arcana >= 2 |
| l_arcana_5 | trigger t_arcana_5 when skill_level arcana >= 5 |
| l_arcana_6 | trigger t_arcana_6 when skill_level arcana >= 6 |
| l_morning_6 | trigger t_day_6 when feature morning_6 unlocked |
| l_ridge_1 | trigger t_ridge when store day_6 >= 40; fires with l_ridge_2 |
| l_ridge_2 | trigger t_ridge when store day_6 >= 40; fires with l_ridge_1 |
| l_pair_1 | offer o_pair line (on screen until answered; fires with l_pair_2) |
| l_pair_2 | offer o_pair line (on screen until answered; fires with l_pair_1) |
| l_bay2_go | answer o_pair_room of offer o_pair: line when that answer is given |
| l_bay2_hers | answer o_pair_hers of offer o_pair: line when that answer is given |
| l_bay2_fail | failed-card line of card make_bay2 (craft; lane -); inputs damp_wood x18, stones x18 / failed-card line of card n3_build_bay (craft; lane n3); inputs damp_wood x18, stones x18 |
| l_n4_watch_dry | failed-card line of card n4_watch (action; lane n4); inputs dry_wood x1; requires store watch_done >= 2 |
| l_join2_1 | trigger t_pair_joins when store bay2 >= 1; fires with l_join2_2 |
| l_join2_2 | trigger t_pair_joins when store bay2 >= 1; fires with l_join2_1 |
| l_seed | trigger t_seed when store pair_3h >= 20 |
| l_dig_bed_fail | failed-card line of card n3_dig_bed (craft; lane n3); inputs stones x6 |
| l_dig_bed_1 | stage line 1 of 3 of card n3_dig_bed (craft; inputs stones x6) |
| l_dig_bed_2 | stage line 2 of 3 of card n3_dig_bed (craft; inputs stones x6) |
| l_dig_bed_done | stage line 3 of 3 of card n3_dig_bed (craft; inputs stones x6) |
| l_old_watch | trigger t_old_watch when store pair_3h >= 60 |
| l_night_6 | trigger t_night_6 when store night_6 >= 5 |

## Generated states (the simulator's `--lines` over the typical, sharp, babysitter and whenever routes; replaces the brief's expected states where they differ)

Visit numbers count from the first visit of the chapter's pass, per route (a find can fire in a later chapter's visits). 'present' = the player is there when it happens; 'on return' = reads it after an absence. A line must read right in every listed combination. The answers listed are everything answered so far in the whole week, not only this chapter's.

| key | where it showed (route, visit, present or on return) | state |
|---|---|---|
| l_stone_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_stone_first | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V2 on return; capped done 38-38; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_stones_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_stones_1 | sharp V12 on return | typical V6 on return; whenever V6 on return; capped done 41-43; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_stones_2 | sharp V13 on return | typical V7 on return; whenever V7 on return; capped done 43-44; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-1 |
| l_stones_done | sharp V14 on return | typical V8 on return; whenever V8 on return; capped done 44-45; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-1 |
| l_arcana_2 | babysitter V1 present | sharp V7 on return; typical V2 on return; whenever V2 on return; capped done 38-45; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-1 |
| l_arcana_5 | sharp V14 on return | typical V6 on return; whenever V5 on return; capped done 40-45; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-1 |
| l_arcana_6 | sharp V22 on return | typical V8 on return; whenever V6 on return; capped done 41-46; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_morning_6 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V2 on return; capped done 38-38; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_ridge_1 | babysitter V1 present | sharp V3 on return; typical V2 on return; whenever V2 on return; capped done 38-38; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_ridge_2 | babysitter V1 present | sharp V3 on return; typical V2 on return; whenever V2 on return; capped done 38-38; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_pair_1 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V2 on return; capped done 38-38; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_pair_2 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V2 on return; capped done 38-38; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_bay2_go | babysitter V1 present | sharp V2 present; typical V2 present; whenever V2 on return; capped done 38-38; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_bay2_hers | never shown on any simulated route (design expectation in the brief applies) | |
| l_bay2_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_n4_watch_dry | never shown on any simulated route (design expectation in the brief applies) | |
| l_join2_1 | babysitter V1 present | sharp V6 on return; typical V4 on return; whenever V4 on return; capped done 39-39; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_join2_2 | babysitter V1 present | sharp V6 on return; typical V4 on return; whenever V4 on return; capped done 39-39; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_seed | babysitter V1 present | sharp V6 on return; typical V4 on return; whenever V4 on return; capped done 39-39; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_bed_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_dig_bed_1 | babysitter V1 present | sharp V7 on return; typical V5 on return; whenever V5 on return; capped done 39-40; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_bed_2 | babysitter V1 present | sharp V8 on return; typical V5 on return; whenever V5 on return; capped done 39-40; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_bed_done | babysitter V1 present | sharp V8 on return; typical V5 on return; whenever V5 on return; capped done 40-40; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_old_watch | babysitter V1 present | sharp V7 on return; typical V5 on return; whenever V4 on return; capped done 39-40; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_night_6 | babysitter V1 present | sharp V8 on return; typical V5 on return; whenever V5 on return; capped done 40-40; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |

## Brief names

The design briefs name these keys differently; this file's keys are the data file's:

- `l_find_dry_kindling` is `l_arcana_5`
- `l_stones_3` is `l_stones_done`

## Keys the brief does not spell out

No beat facts: write from the wiring table. Failed-card lines (`*_fail`, `*_dry`): what the card shows when tapped with the cost short; the player's try (or the person's), short of the means; one short line; no number. Stage lines: the card's stages in order, same register as the shipped stage lines of day two and three.

Keys: l_stone_fail, l_stones_fail, l_bay2_fail, l_n4_watch_dry, l_dig_bed_fail, l_dig_bed_1, l_dig_bed_2, l_dig_bed_done

## Output

A TOML file, `key = "line"` per key below, in this order, lowercase, plain. Keys marked H also get `key_alt = "line"` right after. A draft missing an alternate is sent back. Every line within 75 characters; no digit; no name slot.

Keys (27, in order): l_stone_fail, l_stone_first, l_stones_fail, l_stones_1, l_stones_2, l_stones_done, l_arcana_2, l_arcana_5, l_arcana_6, l_morning_6, l_ridge_1, l_ridge_2, l_pair_1, l_pair_2, l_bay2_go, l_bay2_hers, l_bay2_fail, l_n4_watch_dry, l_join2_1, l_join2_2, l_seed, l_dig_bed_fail, l_dig_bed_1, l_dig_bed_2, l_dig_bed_done, l_old_watch, l_night_6

H keys (alt required): l_ridge_1, l_ridge_2, l_pair_1, l_pair_2, l_join2_1, l_join2_2

## Shipped lines of the chapter before (day-four)

{{PREVIOUS_PICKS}}

(The lead fills this with the previous chapter's shipped lines before the proposers start; reuse no phrase from them.)


## Drafts

### Draft A

{{DRAFT_A}}

### Draft B

{{DRAFT_B}}

### Draft C

{{DRAFT_C}}
