# Proposer writer-2 input: day twelve's lines (B11 to night 14)

You are writing day twelve's lines. This file is all you may see from the project's content; read nothing else.

## Your lens

what gets written down, and what doesn't

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

---

# Day twelve's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `week-two.md`; the data is
`app/ashfall_app/opening/day_twelve.toml`, where every key below reads "[day two: line to write]" (the marker's spelling is
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
  brother" until l_join3_1 gives `{n5}`, `{n6}` and `{n7}`, and their child as "the child" or "their child", never
  named; the stranger only ever as "the man who came with them" or
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
  - never count who the family lost or say who; never say they are missing anyone outright;
  - their child (`decisions.md`, "Never"): there, plainly, never working, never a cost or counted among mouths or
    hands, never in danger in these lines, and never the one the family is missing;
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

### Changes to the section above (the data file wins)

- **No line counts people.** l_dig_open and S4 say "everyone", "all of them" or nothing, never a number of mouths or of
  people at the fire: their child is never counted among mouths, and the guard is at the gap.
- **l_sitter_1, l_sitter_2** land at the same hour on every route, which is not dusk: never say the time of day. The
  guard is "the guard" in every line of this chapter, never a name: either {n2} or {n7} may hold the spear.
- **l_b12_1 to l_b12_3**: the marks may be told as groups of five with the last group four, in words; never a total,
  never "one short", and the board is never tied to the town's own board by the fire, by any word. The stool is tied to
  the one at the fire, as the facts say; that is the day's one stool line.
- The asks' cost lines (`*_cost`) are the voice pass's, not the writers'.

### Keys the brief spells differently or not at all

- **l_dig_open** (the brief's day eleven entry; its key is this chapter's). Shown in B11's moment, after day eleven's
  shipped l_b11_3, with the dig's card. Facts: everyone to feed, the larder full, and nowhere to keep it. It never says
  where anything would be kept, never that anyone digs or will, never ground, under, below or a cellar: S1 is the dig's
  first word.
- **The dig's stage lines** (`dig_cellar`, four stages on the player's hands, each taking stakes and damp wood for props
  and shoring, run by its order card, so most land on return). **l_dig_stage_1** shows in S1's moment with l_dig_1 and
  l_dig_2; **l_dig_stage_3** in S2's with l_steps_1 and l_steps_2; neither repeats its beat, each is the stage's plain
  record (the props in, the shoring set). **l_dig_stage_2** shows alone. **l_dig_done**, the last stage: usually in
  B12's moment, but on a fast route it lands before B12 and shows alone, so it says nothing of what is below or that
  anything is open; the last props set.
- **l_dig_fail**: the dig's failed-card line: short of stakes, damp wood, or both.
- **l_hunt_bear_fail**: the hunt's failed-card line: short of smoked meat, or the bear's sign is spent (the hunts left
  are used up). True for either; it says neither which nor why.
- **l_fight_bear_won_1, l_fight_bear_won_2, l_fight_bear_lost_1, l_fight_bear_lost_2**: the bear hunt's pools, two
  lines each (the brief's eight are the data file's two). The player goes out after the bear, from the bloom's sign; the
  bear is never at the camp. Won: brought down; meat, a pelt and its fat carried home. Lost: the player comes back
  hurt; the line does not say so. A pool line is one fight, plain and short, never gory, never dwelling on how a beast
  dies; no count, no "again", no "another", no "this time", no real-time word, no name, no spear.
- **The lamps** (SL21, `tallow_lamps`, three stages run by its order card, each taking tallow and stakes):
  **l_lamps** is the moment the card shows (the bear's tallow rendered in the stew pot and poured into split stakes);
  **l_lamps_1**, **l_lamps_2** are stage records; **l_lamps_done**, the last: lamps lit on the gate posts.
  l_lamps can share a moment with a won bear hunt's pool line. **l_lamps_fail**: short of tallow, stakes, or both.
- **l_sit_last_night_fail**: the failed-card line of the last night's card (A32), tapped before it is ready. It does
  not say why, names no night and no wolf, waits on nothing, and is not day eleven's l_vigil_fail reworded.
- **l_find_gap_wolf** (Melee 7, a find: a wolf dead at the gap, older than the pack's, a pelt off it). It can share
  B11's moment. Week 1 shipped the nearest find, "a wolf lies stiff under the thorn. you take the pelt."; reuse no
  phrase from it. Never a wolf sitting, never the guard's doing.
- **l_camp_15** (fungus holds more, lifted by the dig's last stage: it can show before B12, so never the cellar or
  what is below), **l_camp_16** (smoked meat holds more, lifted by the last night: it can follow l_s4_3 in S4's moment,
  so nothing of the wolf, the wind or the night). Plain records, no number.
- The journal's notes (n_bear_1, n_gutter_1, n_day_b12) are their own batch: write none.

### The camp's asks (offers): this chapter's other writing job

Nine offers, one a return, from B11's moment (the first can share it) to S4. Each is a short text (`o_*`) and two
answers (`a_*`), each a button. Neither answer is judged, neither is the right one, and declining costs nothing.
**Write the offer text and both answer labels for every offer below**, after the lines' keys in your output, in the
order listed.

Register: game UI with a person behind it, so sentence case with a capital first letter (unlike the lines), plain, one
sentence, at most about 60 characters for the text and about 22 for an answer, no digit. A name is a slot, written
exactly: `{n2}` (him), `{n4}` (the old man), `{n5}` (the woman), `{n6}` (her husband), `{n7}` (her brother); Lucy by
name; their child as "their child" or "the child", never named. Shipped offers of day eleven, for the register only:
"{n2} pegs a door together for the new hut." (answers "He hangs it fire side" / "He hangs it gate side"); "Among their
things, the woman has a pot." ("She hangs it by ours" / "She trades it to {n2}"); "Ash lies thick against the posts
inside the ring." ("Lucy digs it out" / "Lucy banks it up").

**Read in a row they must not feel like a quiz or a form.** Nine come one after another, after day eleven's five. So:
- each has a different stake (what it costs, who it is for, what it risks), and the text makes that stake plain;
- vary the shape of the sentence: not nine "X or Y?" questions. Some are someone asking, some say what someone wants or
  is doing and end on the choice, some are the choice alone; vary where the person's name sits;
- vary who asks and why (the asker is given; keep it). o_cradle and o_lye share an asker and change the same two things:
  their texts must differ most of any pair, in shape and in stake (the child's sleep; the work of scrubbing);
- answers are short and active: a person doing a thing, in active voice, never a bare noun pair every time; the two
  answers of one offer mirror each other in frame and length.

| Offer | Who asks, and the facts | Answer 1 (key, what happens) | Answer 2 (key, what happens) |
|---|---|---|---|
| o_spoil | {n6}: the spoil the dig throws up, ash and earth | a_spoil_ring: banked against the ring, outside (the gap holds better) | a_spoil_stones: sieved for the stones in it (some stones at once) |
| o_cradle | {n5}: their child won't sleep in the hut | a_cradle_fire: a place made for the child by the fire (everyone rests better) | a_cradle_hut: the pot moved into the hut, for the warmth (the stew comes faster) |
| o_shaft | {n7}: the spear's shaft has split at the binding; he has pulled iron out of the scrap to mend it | a_shaft_bind: bound tighter, with an iron collar (the hands fight better) | a_shaft_plain: a plain new shaft cut from a stake, the head moved onto it, and the iron back on the scrap (some scrap at once) |
| o_cold_air | Lucy: the dig keeps cold at the bottom | a_cold_air_meat: the meat hung down in the dig, in the cold (the larder keeps better) | a_cold_air_rack: the meat kept on the rack, where she can see it (the rack holds better) |
| o_lean_to | {n2}: a lean-to on the hut's side | a_lean_to_wood: for the wood (dry wood holds more) | a_lean_to_hides: for the hides (pelts hold more) |
| o_lye | {n5}: lye leached from the roof ash | a_lye_bedding: the bedding scrubbed with it (everyone rests better) | a_lye_pot: the pot scrubbed with it (the stew comes faster) |
| o_wet | {n2}: the hut's floor is wet at one corner, where the ash-water runs in | a_wet_drain: drained to the ditch (everyone rests better) | a_wet_pave: the wet corner dug out, the stones it turns up to the pile (some stones at once) |
| o_crows | {n4}: the crows have come down off the ridge to the rack | a_crows_off: driven off (the rack holds better) | a_crows_be: let be, since they cry at whatever comes near in the dark (the gap holds better) |
| o_sag | {n6}: the hut's roof sags under the ash | a_sag_prop: propped with a pole (everyone rests better) | a_sag_down: the sagging poles taken down and burned, the roof laid lower (some dry wood at once) |

Must-nots for the asks: never "again"; nothing of the man who came with them, the burning, the board or his mark;
their child never working, never a cost, never in danger, and o_cradle never says why the child won't sleep; o_spoil
can show before the dig's first stage, so it never says where the dig is, what it is for, or that it has begun; no ask
names the cellar or anything in it; o_cold_air can show before S2 (the steps), so it never names steps, stone or
air coming up, only the cold at the dig's bottom; o_crows never says the crows
count, or what; no ask touches a wolf, the light's edge, the book or the margin; o_shaft holds whoever has the spear
and names neither; o_sag never has the roof fall, or anyone under it.

## Where each key plays (read from the data file; "fires with" lines share one moment on screen)

| key | where it plays (from the data file) |
|---|---|
| l_dig_open | trigger t_dig when card keep_vigil done >= 1 |
| l_dig_fail | failed-card line of card dig_cellar (craft; lane -); inputs stakes x16, damp_wood x6 |
| l_dig_stage_1 | stage line 1 of 4 of card dig_cellar (craft; inputs stakes x16, damp_wood x6) |
| l_dig_stage_2 | stage line 2 of 4 of card dig_cellar (craft; inputs stakes x16, damp_wood x6) |
| l_dig_stage_3 | stage line 3 of 4 of card dig_cellar (craft; inputs stakes x16, damp_wood x6) |
| l_dig_done | stage line 4 of 4 of card dig_cellar (craft; inputs stakes x16, damp_wood x6) |
| l_morning_13 | trigger t_morning_13 when store dig_clock >= 1 |
| l_dig_1 | trigger t_s1 when card dig_cellar done >= 1; fires with l_dig_2 |
| l_dig_2 | trigger t_s1 when card dig_cellar done >= 1; fires with l_dig_1 |
| l_steps_1 | trigger t_s2 when card dig_cellar done >= 3; fires with l_steps_2 |
| l_steps_2 | trigger t_s2 when card dig_cellar done >= 3; fires with l_steps_1 |
| l_b12_1 | trigger t_b12 when card dig_cellar done >= 4; requires action b12_floor unlocked; feature b9 unlocked; fires with l_b12_2, l_b12_3 |
| l_b12_2 | trigger t_b12 when card dig_cellar done >= 4; requires action b12_floor unlocked; feature b9 unlocked; fires with l_b12_1, l_b12_3 |
| l_b12_3 | trigger t_b12 when card dig_cellar done >= 4; requires action b12_floor unlocked; feature b9 unlocked; fires with l_b12_1, l_b12_2 |
| l_bear_sign | trigger t_bear_sign when store dig_clock >= 5; requires action bear_season unlocked |
| l_hunt_bear_fail | failed-card line of card hunt_bear (action; lane -); inputs smoked x2, bear_sign x1 |
| l_fight_bear_won_1 | pool of lines for one fight won, of hunt_bear (side hands against ash_bear); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_fight_bear_won_2 | pool of lines for one fight won, of hunt_bear (side hands against ash_bear); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_fight_bear_lost_1 | pool of lines for one fight lost, of hunt_bear (side hands against ash_bear); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_fight_bear_lost_2 | pool of lines for one fight lost, of hunt_bear (side hands against ash_bear); one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before |
| l_lamps | trigger t_lamps when store tallow >= 2 |
| l_lamps_fail | failed-card line of card tallow_lamps (craft; lane -); inputs tallow x2, stakes x2 |
| l_lamps_1 | stage line 1 of 3 of card tallow_lamps (craft; inputs tallow x2, stakes x2) |
| l_lamps_2 | stage line 2 of 3 of card tallow_lamps (craft; inputs tallow x2, stakes x2) |
| l_lamps_done | stage line 3 of 3 of card tallow_lamps (craft; inputs tallow x2, stakes x2) |
| l_sitter_1 | trigger t_sitter when store drift_clock >= 150; fires with l_sitter_2 |
| l_sitter_2 | trigger t_sitter when store drift_clock >= 150; fires with l_sitter_1 |
| l_night_14 | trigger t_night_14 when the clock reaches 330 h |
| l_sit_last_night_fail | failed-card line of card sit_last_night (narrative; lane -); inputs none; requires store drift_clock >= 163; feature sitter unlocked |
| l_s4_1 | trigger t_s4 when card sit_last_night done >= 1; fires with l_s4_2, l_s4_3 |
| l_s4_2 | trigger t_s4 when card sit_last_night done >= 1; fires with l_s4_1, l_s4_3 |
| l_s4_3 | trigger t_s4 when card sit_last_night done >= 1; fires with l_s4_1, l_s4_2 |
| l_find_gap_wolf | trigger t_find_melee_7 when skill_level melee >= 7; requires feature dig unlocked |
| l_camp_15 | camp level at 2100000 items |
| l_camp_16 | camp level at 2700000 items |

## Generated states (the simulator's `--lines` over the typical, sharp, babysitter and whenever routes; replaces the brief's expected states where they differ)

Visit numbers count from the first visit of the chapter's pass, per route (a find can fire in a later chapter's visits). 'present' = the player is there when it happens; 'on return' = reads it after an absence. A line must read right in every listed combination. The answers listed are everything answered so far in the whole week, not only this chapter's.

| key | where it showed (route, visit, present or on return) | state |
|---|---|---|
| l_dig_open | babysitter V1 present | sharp V1 on return; typical V1 on return; whenever V1 present; capped done 55-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_dig_stage_1 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V2 on return; capped done 55-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_stage_2 | babysitter V1 present | sharp V3 on return; typical V3 on return; whenever V2 on return; capped done 55-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cradle_fire', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_stage_3 | babysitter V1 present | sharp V5 on return; typical V3 on return; whenever V2 on return; capped done 55-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_done | babysitter V1 present | sharp V5 on return; typical V4 on return; whenever V3 on return; capped done 56-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_morning_13 | babysitter V1 present | sharp V1 on return; typical V1 on return; whenever V2 on return; capped done 55-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_1 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V2 on return; capped done 55-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room']; trip held; queue 0-0 |
| l_dig_2 | babysitter V1 present | sharp V2 on return; typical V2 on return; whenever V2 on return; capped done 55-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room']; trip held; queue 0-0 |
| l_steps_1 | babysitter V1 present | sharp V5 on return; typical V3 on return; whenever V2 on return; capped done 55-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room']; trip held; queue 0-0 |
| l_steps_2 | babysitter V1 present | sharp V5 on return; typical V3 on return; whenever V2 on return; capped done 55-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room']; trip held; queue 0-0 |
| l_b12_1 | babysitter V1 present | sharp V6 on return; typical V4 on return; whenever V3 on return; capped done 56-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_b12_2 | babysitter V1 present | sharp V6 on return; typical V4 on return; whenever V3 on return; capped done 56-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_b12_3 | babysitter V1 present | sharp V6 on return; typical V4 on return; whenever V3 on return; capped done 56-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_bear_sign | babysitter V1 present | sharp V12 on return; typical V2 on return; whenever V2 on return; capped done 55-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_hunt_bear_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_bear_won_1 | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_bear_won_2 | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_bear_lost_1 | never shown on any simulated route (design expectation in the brief applies) | |
| l_fight_bear_lost_2 | never shown on any simulated route (design expectation in the brief applies) | |
| l_lamps | babysitter V1 present | sharp V17 on return; typical V3 on return; whenever V4 on return; capped done 55-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_lamps_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_lamps_1 | babysitter V1 present | sharp V18 on return; typical V4 on return; whenever V5 on return; capped done 56-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_lamps_2 | babysitter V1 present | sharp V19 on return; typical V6 on return; whenever V5 on return; capped done 56-57; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_lamps_done | babysitter V1 present | sharp V22 on return; typical V6 on return; whenever V6 on return; capped done 57-57; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_sitter_1 | babysitter V1 present | sharp V33 on return; typical V8 on return; whenever V6 on return; capped done 57-57; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_sitter_2 | babysitter V1 present | sharp V33 on return; typical V8 on return; whenever V6 on return; capped done 57-57; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_night_14 | babysitter V1 present | sharp V36 on return; typical V10 on return; whenever V7 on return; capped done 57-58; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-1 |
| l_sit_last_night_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_s4_1 | babysitter V1 present | sharp V36 on return; typical V10 on return; whenever V8 on return; capped done 58-58; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_s4_2 | babysitter V1 present | sharp V36 on return; typical V10 on return; whenever V8 on return; capped done 58-58; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_s4_3 | babysitter V1 present | sharp V36 on return; typical V10 on return; whenever V8 on return; capped done 58-58; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_find_gap_wolf | never shown on any simulated route (design expectation in the brief applies) | |
| l_camp_15 | babysitter V1 present | sharp V5 on return; typical V4 on return; whenever V3 on return; capped done 56-56; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |
| l_camp_16 | babysitter V1 present | sharp V36 on return; typical V10 on return; whenever V8 on return; capped done 58-58; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_cold_air_meat', 'o_cradle_fire', 'o_crows_be', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lean_to_wood', 'o_lookout_wall', 'o_lye_bedding', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_sag_prop', 'o_shaft_bind', 'o_skin_flaps', 'o_spoil_ring', 'o_stay_room', 'o_wet_drain']; trip held; queue 0-0 |

## Output

A TOML file, `key = "line"` per key below, in this order, lowercase, plain. Keys marked H also get `key_alt = "line"` right after. A draft missing an alternate is sent back. Every line within 75 characters; no digit; a name slot only as the rule above allows.

Keys (35, in order): l_dig_open, l_dig_fail, l_dig_stage_1, l_dig_stage_2, l_dig_stage_3, l_dig_done, l_morning_13, l_dig_1, l_dig_2, l_steps_1, l_steps_2, l_b12_1, l_b12_2, l_b12_3, l_bear_sign, l_hunt_bear_fail, l_fight_bear_won_1, l_fight_bear_won_2, l_fight_bear_lost_1, l_fight_bear_lost_2, l_lamps, l_lamps_fail, l_lamps_1, l_lamps_2, l_lamps_done, l_sitter_1, l_sitter_2, l_night_14, l_sit_last_night_fail, l_s4_1, l_s4_2, l_s4_3, l_find_gap_wolf, l_camp_15, l_camp_16

H keys (alt required): l_dig_1, l_dig_2, l_steps_1, l_steps_2, l_b12_1, l_b12_2, l_b12_3, l_sitter_1, l_sitter_2, l_s4_1, l_s4_2, l_s4_3

## Shipped lines of the chapter before (day-eleven)

{{PREVIOUS_PICKS}}

(The lead fills this with the previous chapter's shipped lines before the proposers start; reuse no phrase from them.)
