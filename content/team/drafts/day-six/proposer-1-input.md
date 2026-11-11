# Proposer writer-1 input: day six's lines (keeping it, G2)

You are writing day six's lines. This file is all you may see from the project's content; read nothing else.

## Your lens

what a stranger would get wrong

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

---

# Day six's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `days-four-to-seven.md`; the data is
`app/ashfall_app/opening/day_six.toml`, where every key below reads "[day two: line to write]" (the marker's spelling is
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
  hunting and skinning told as a way of life. The page writes a long absence's count line; write the pools below.
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

### Day six: keeping it (Y1-Y6)

**l_morning_7**. Facts: the rack bare in daylight; everyone counting what's left.

**l_spear** (SL12, the spear done). Facts: `{n2}` hands over the shaft he carried since he came; the ploughshare's iron,
beaten flat on the stone and bound on, is its head; he holds it once and gives it back. Special: the first line
allowed to put the shaft and the scrap together.

**l_hunt_1, l_hunt_2** (G1, H). Fields: down · yes_but · grim · time · opens the near question. Canon C-beat-101.
Facts: the first wolf the hunt brings back: alone, starving, ribs like a rack of its own, teeth worn; it comes back as
meat and a pelt. States: the first whole won hunt, by the mix or a tap, any visit of day six. Special: the grim is that
it was as hungry as the camp; plain about the meat.

**l_rats_first, l_crows_first** (each standing fight's first unit). Facts: a fat grey rat at the roots / crows on the
roof's ridge (or in the hang, without the roof).

**l_bedding_1..3** (`pelt_bedding` stages), **l_bedding_done** (SL14). Facts: pelts on the floors of the bays; the old
man sleeps through the night for the first time.

**l_pelt_ask** (SL13, the offer's line), **l_pelt_given**, **l_pelt_kept** (each answer). Facts: `{n3}` asks for a pelt to
lay over the turned ground at night / she lays it over and weights its corners with stones / she covers it with sacking
instead. Special: neither answer judged; the ground's future never hinted.

**l_night_7** (night 7's first item). Facts: the light going; the rack hung.

**l_g2_1 to l_g2_3** (G2, H each). Fields: up · yes · warm · pays the near question. Canon C-beat-102. Facts: the rack
hung again, fuller than before; five at the fire, Lucy still on the far side; nothing at the edge of the light tonight;
for the first time in a week a little wind. States: night 7, smoked ≥ 18; present or on return. Special: the week's
quiet close; the wind is felt, never explained or foreboding.

### The Camp (this chapter's)

**l_camp_12** (the 900 000-item camp level, lifted by G2: smoked holds 36, was 27).

To check first: **o_pelt** is a small thing asked by someone new, and "keep it" must read as an ordinary answer, not a refusal.

The spear line (`l_spear`) is the one place a line may put the shaft and the scrap together.

## Where each key plays (read from the data file; "fires with" lines share one moment on screen)

| key | where it plays (from the data file) |
|---|---|
| l_morning_7 | trigger t_morning_7 when store dawn_7 >= 20 |
| l_spear | trigger t_spear_made when card make_spear done >= 1 |
| l_rats_first | trigger t_rats_first when store rats_fought >= 1 |
| l_crows_first | trigger t_crows_first when store crows_fought >= 1 |
| l_hunt_1 | trigger t_first_pelt when store pelt >= 1; fires with l_hunt_2 |
| l_hunt_2 | trigger t_first_pelt when store pelt >= 1; fires with l_hunt_1 |
| l_bedding_fail | failed-card line of card pelt_bedding (craft; lane -); inputs pelt x2, damp_wood x6 |
| l_bedding_1 | stage line 1 of 3 of card pelt_bedding (craft; inputs pelt x2, damp_wood x6) |
| l_bedding_2 | stage line 2 of 3 of card pelt_bedding (craft; inputs pelt x2, damp_wood x6) |
| l_bedding_done | stage line 3 of 3 of card pelt_bedding (craft; inputs pelt x2, damp_wood x6) |
| l_pelt_ask | offer o_pelt line (on screen until answered; fires with nothing) |
| l_pelt_kept | answer o_pelt_keep of offer o_pelt: line when that answer is given |
| l_give_pelt_fail | failed-card line of card give_pelt (narrative; lane -); inputs pelt x1 |
| l_pelt_given | stage line 1 of 1 of card give_pelt (narrative; inputs pelt x1) |
| l_night_7 | trigger t_night_7 when store night_7 >= 5 |
| l_sit_fire_7_fail | failed-card line of card sit_fire_7 (narrative; lane -); inputs none; requires store night_7 >= 5; store smoked >= 18 |
| l_g2_1 | line on finishing of card sit_fire_7 |
| l_g2_2 | line on finishing of card sit_fire_7 |
| l_g2_3 | line on finishing of card sit_fire_7 |
| l_camp_12 | camp level at 900000 items |

## Generated states (the simulator's `--lines` over the typical, sharp, babysitter and whenever routes; replaces the brief's expected states where they differ)

Visit numbers count from the first visit of the chapter's pass, per route (a find can fire in a later chapter's visits). 'present' = the player is there when it happens; 'on return' = reads it after an absence. A line must read right in every listed combination. The answers listed are everything answered so far in the whole week, not only this chapter's.

| key | where it showed (route, visit, present or on return) | state |
|---|---|---|
| l_morning_7 | babysitter V1 present | sharp V2 on return; typical V3 on return; whenever V3 on return; capped done 43-43; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_spear | babysitter V1 present | sharp V2 on return; typical V3 on return; whenever V3 on return; capped done 43-43; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_rats_first | babysitter V1 present | sharp V2 on return; typical V3 on return; whenever V3 on return; capped done 43-43; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_crows_first | babysitter V1 present | sharp V3 on return; typical V3 on return; whenever V3 on return; capped done 43-43; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_hunt_1 | babysitter V1 present | sharp V4 on return; typical V4 on return; whenever V4 on return; capped done 43-44; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_hunt_2 | babysitter V1 present | sharp V4 on return; typical V4 on return; whenever V4 on return; capped done 43-44; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-0 |
| l_bedding_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_bedding_1 | babysitter V1 present | sharp V8 on return; typical V5 on return; whenever V5 on return; capped done 44-45; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_bedding_2 | babysitter V1 present | sharp V9 on return; typical V6 on return; capped done 44-45; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_bedding_done | babysitter V1 present | sharp V10 on return; typical V7 on return; capped done 45-46; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_pelt_ask | babysitter V1 present | sharp V5 on return; typical V4 on return; whenever V4 on return; capped done 43-44; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_stay_room']; trip held; queue 0-1 |
| l_pelt_kept | never shown on any simulated route (design expectation in the brief applies) | |
| l_give_pelt_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_pelt_given | babysitter V1 present | sharp V5 present; typical V4 present; whenever V4 present; capped done 44-45; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-2 |
| l_night_7 | babysitter V1 present | sharp V21 on return; typical V8 on return; whenever V5 on return; capped done 45-46; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_sit_fire_7_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_g2_1 | babysitter V1 present | sharp V21 present; typical V8 present; whenever V5 present; capped done 46-47; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_g2_2 | babysitter V1 present | sharp V21 present; typical V8 present; whenever V5 present; capped done 46-47; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_g2_3 | babysitter V1 present | sharp V21 present; typical V8 present; whenever V5 present; capped done 46-47; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |
| l_camp_12 | babysitter V1 present | sharp V21 present; typical V8 present; whenever V5 present; capped done 46-47; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_pair_room', 'o_pelt_give', 'o_stay_room']; trip held; queue 0-0 |

## Brief names

The design briefs name these keys differently; this file's keys are the data file's:

- `l_bedding_3` is `l_bedding_done`

## Keys the brief does not spell out

No beat facts: write from the wiring table. Failed-card lines (`*_fail`, `*_dry`): what the card shows when tapped with the cost short; the player's try (or the person's), short of the means; one short line; no number. Stage lines: the card's stages in order, same register as the shipped stage lines of day two and three.

Keys: l_bedding_fail, l_give_pelt_fail, l_sit_fire_7_fail

## Output

A TOML file, `key = "line"` per key below, in this order, lowercase, plain. Keys marked H also get `key_alt = "line"` right after. A draft missing an alternate is sent back. Every line within 75 characters; no digit; a name slot only as the rule above allows.

Keys (20, in order): l_morning_7, l_spear, l_rats_first, l_crows_first, l_hunt_1, l_hunt_2, l_bedding_fail, l_bedding_1, l_bedding_2, l_bedding_done, l_pelt_ask, l_pelt_kept, l_give_pelt_fail, l_pelt_given, l_night_7, l_sit_fire_7_fail, l_g2_1, l_g2_2, l_g2_3, l_camp_12

H keys (alt required): l_hunt_1, l_hunt_2, l_g2_1, l_g2_2, l_g2_3

## Shipped lines of the chapter before (b7)

{{PREVIOUS_PICKS}}

(The lead fills this with the previous chapter's shipped lines before the proposers start; reuse no phrase from them.)
