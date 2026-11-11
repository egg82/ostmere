# Critic input (template): day eleven's lines (B10 to B11)

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

# Day eleven's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `week-two.md`; the data is
`app/ashfall_app/opening/day_eleven.toml`, where every key below reads "[day two: line to write]" (the marker's spelling is
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

### Changes to the section above (the data file wins)

- **l_posts** of this section is the data file's **l_leaning_posts** (SL19). Day nine has a shipped line of the same
  brief name; write only the SL19 one.
- **l_dig_open** has no key in this chapter: write nothing for it.
- **l_family_1, l_family_2** are written here (the family arrives with B10's moment and these two are shown with
  O-family, below).

### The family at the gate (O-family's lines)

**l_family_1, l_family_2** (on screen with the offer until it is answered). Facts: the woman does the talking; she asks
if there is room inside the wall; the man who came behind them sits down outside the gate and waits, apart from the
rest. Four figures are at the gate and the way they stand leaves room for a fifth; no line counts them, names a loss, or
says who is missing. One of the four is their child: there, plainly, close to the woman, never working, never named,
never in danger, never the one they are missing. They are "the woman", "her husband", "her brother", "their child" and
"the man who came with them": no slots before l_join3_1.

### Keys the brief spells differently or not at all

- **l_hut_fail**: the failed-card line of both hut cards (the player's `make_hut` and her lane's `n5_build_hut`): short
  of stakes, stones, or both. No "you", no "she": the card is shared.
- **l_arm_fail**: the failed-card line of the spear's making (a one-off on the player's hands; the same card for either
  guard): short of scrap, a stake, or both. Names neither {n2} nor {n7}.
- **l_n6_posts_fail**: the failed-card line of her husband's own posts card: short of stakes. **l_n6_posts_done**: the
  line on finishing: the three leaning posts set right with the stakes he asked for. No count, no "you".
- **l_vigil_fail**: the failed-card line of the vigil card when it is tapped and cannot start yet. It does not say why,
  does not name the night, and waits on nothing.
- **l_lane_watch_dry**: the failed-card line of the family's watch card (the three newcomers' lanes share it): short of
  dry wood. No "you", no name.
- **l_night_12**: the light going, on the night after the count: everyone at the fire, him covered. A plain record.

### The camp's asks (offers): this chapter's other writing job

Five offers: the family's, the guard's, and three small asks that come one a return while the hut waits on its stakes.
Each is a short text (the question, `o_*`) and two answers (`a_*`), each a button. Neither answer is judged, neither is
the right one, and declining costs nothing. **Write the offer text and both answer labels for every offer below**, after
the lines' keys in your output, in the order listed.

Register: game UI with a person behind it, so sentence case with a capital first letter (unlike the lines), plain, one
sentence, at most about 60 characters for the text and about 22 for an answer, no digit. A name is a slot, written
exactly: `{n2}` (him), `{n3}` (the woman), `{n4}` (the old man); Lucy by name. `{n7}` (the family's young man) may be
written in o_guard and its answer only, which show once the family has its names. Shipped offers, for the register only:
"Who goes to the ridge for her cart?" (answers "You go" / "She goes"); "Bank the fire her way or his?" ("Her way" / "His
way"); "Cover {n3}'s ground with a pelt or sacking?" ("Pelt" / "Sacking").

**Read in a row they must not feel like a quiz or a form.** Five of them come across the chapter, after day nine's ten.
So:
- each has a different stake (what it costs, who it is for, what it risks), and the text makes that stake plain;
- vary the shape of the sentence: not five "X or Y?" questions. Some are someone asking, some say what someone wants or
  is doing and end on the choice, some are the choice alone; vary where the person's name sits;
- vary who asks and why (the asker is given; keep it);
- answers are short and active: a person doing a thing, in active voice, never a bare noun pair every time; the two
  answers of one offer mirror each other in frame and length.

| Offer | Shows | Who asks, and the facts | Answer 1 (key, what happens) | Answer 2 (key, what happens) |
|---|---|---|---|---|
| o_family | B10's moment, at the gate, with l_family_1 and l_family_2 | the family's woman, for all of them: room inside the wall; the hut costs the same stakes and stones either way and takes the same time | a_family_room: you build the hut with your own hands | a_family_theirs: they build it themselves, on her lane |
| o_guard | with Z1, once the family has the hut and its names | Lucy, at the gap: a spear on the wall and nobody to stand the gap at night; it is made at the stone before it is handed over | a_guard_n2: {n2} takes it (he carried the shaft the first spear was made from) | a_guard_n7: {n7} takes it (the young man who wanted it) |
| o_door | the next return after B10, while the hut goes up | {n2}: the hut's door, which way it faces | a_door_fire: facing the fire (everyone rests better) | a_door_gate: facing the gate (the gap holds better) |
| o_pot | the next return | the woman: they carried a pot of their own | a_pot_hang: hung by the camp's pot (the stew comes faster) | a_pot_trade: traded for what {n2} can use (some scrap at once) |
| o_ditch | the next return | Lucy: ash heaped against the posts inside the ring | a_ditch_dig: dug out to a ditch outside the ring (the gap holds better) | a_ditch_bank: banked up, taking the stones from under it (some stones at once) |

Must-nots for the asks: never "again"; o_family says nothing of who the man behind them is or why he waits, and never
counts or names a loss; o_family and o_guard never prefer an answer; o_guard names two people and neither may read as
the right one, and it never says why that one; o_door, o_pot and o_ditch are about the hut, the pot and the ash only.

Answer cost lines (`*_cost`), labels and the rest are the voice pass's, not the writers'.

## Where each key plays (read from the data file; "fires with" lines share one moment on screen)

| key | where it plays (from the data file) |
|---|---|
| l_family_1 | offer o_family line (on screen until answered; fires with l_family_2) |
| l_family_2 | offer o_family line (on screen until answered; fires with l_family_1) |
| l_hut_go | answer o_family_room of offer o_family: line when that answer is given |
| l_hut_theirs | answer o_family_theirs of offer o_family: line when that answer is given |
| l_hut_fail | failed-card line of card make_hut (craft; lane -); inputs stakes x16, stones x12 / failed-card line of card n5_build_hut (craft; lane n5); inputs stakes x16, stones x12 |
| l_join3_1 | trigger t_family_joins when store hut >= 1; fires with l_join3_2 |
| l_join3_2 | trigger t_family_joins when store hut >= 1; fires with l_join3_1 |
| l_guard_ask | offer o_guard line (on screen until answered; fires with nothing) |
| l_arm_fail | failed-card line of card arm_n2 (narrative; lane -); inputs scrap x6, stakes x1 / failed-card line of card arm_n7 (narrative; lane -); inputs scrap x6, stakes x1 |
| l_guard_n2_1 | trigger t_guard_n2 when card arm_n2 done >= 1; fires with l_guard_n2_2 |
| l_guard_n2_2 | trigger t_guard_n2 when card arm_n2 done >= 1; fires with l_guard_n2_1 |
| l_guard_n7_1 | trigger t_guard_n7 when card arm_n7 done >= 1; fires with l_guard_n7_2 |
| l_guard_n7_2 | trigger t_guard_n7 when card arm_n7 done >= 1; fires with l_guard_n7_1 |
| l_leaning_posts | trigger t_posts when store z1_clock >= 80; requires answered o_guard unlocked |
| l_n6_posts_fail | failed-card line of card n6_posts (craft; lane n6); inputs stakes x12 |
| l_n6_posts_done | stage line 1 of 1 of card n6_posts (craft; inputs stakes x12) |
| l_count | trigger t_count when store stranger_clock >= 400; requires feature family_joined unlocked |
| l_night_12 | trigger t_night_12 when store stranger_clock >= 440; requires card keep_vigil unlocked |
| l_vigil_fail | failed-card line of card keep_vigil (narrative; lane -); inputs none; requires store stranger_clock >= 445; action guard_made unlocked |
| l_b11_1 | trigger t_b11 when card keep_vigil done >= 1; fires with l_b11_2, l_b11_3 |
| l_b11_2 | trigger t_b11 when card keep_vigil done >= 1; fires with l_b11_1, l_b11_3 |
| l_b11_3 | trigger t_b11 when card keep_vigil done >= 1; fires with l_b11_1, l_b11_2 |
| l_lane_watch_dry | failed-card line of card {lane}_watch (action; lane ['n5', 'n6', 'n7']); inputs dry_wood x1 |

## Generated states (the simulator's `--lines` over the typical, sharp, babysitter and whenever routes; replaces the brief's expected states where they differ)

Visit numbers count from the first visit of the chapter's pass, per route (a find can fire in a later chapter's visits). 'present' = the player is there when it happens; 'on return' = reads it after an absence. A line must read right in every listed combination. The answers listed are everything answered so far in the whole week, not only this chapter's.

| key | where it showed (route, visit, present or on return) | state |
|---|---|---|
| l_family_1 | sharp V1 on return | typical V1 on return; whenever V1 on return; capped done 50-51; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-1 |
| l_family_2 | sharp V1 on return | typical V1 on return; whenever V1 on return; capped done 50-51; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-1 |
| l_hut_go | sharp V1 present | typical V1 present; whenever V1 on return; capped done 50-51; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-1 |
| l_hut_theirs | never shown on any simulated route (design expectation in the brief applies) | |
| l_hut_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_join3_1 | sharp V5 on return | typical V3 on return; whenever V3 on return; capped done 51-52; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_join3_2 | sharp V5 on return | typical V3 on return; whenever V3 on return; capped done 51-52; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_guard_ask | sharp V5 on return | typical V3 on return; whenever V3 on return; capped done 51-52; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_arm_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_guard_n2_1 | never shown on any simulated route (design expectation in the brief applies) | |
| l_guard_n2_2 | never shown on any simulated route (design expectation in the brief applies) | |
| l_guard_n7_1 | sharp V6 on return | typical V4 on return; whenever V4 on return; capped done 52-53; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_guard_n7_2 | sharp V6 on return | typical V4 on return; whenever V4 on return; capped done 52-53; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_leaning_posts | sharp V7 on return | typical V4 on return; whenever V4 on return; capped done 52-53; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_n6_posts_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_n6_posts_done | sharp V8 on return | typical V5 on return; whenever V5 on return; capped done 53-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_count | sharp V9 on return | typical V4 on return; whenever V5 on return; capped done 53-54; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_night_12 | sharp V10 on return | typical V5 on return; whenever V5 on return; capped done 54-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_vigil_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_b11_1 | sharp V10 on return | typical V5 on return; whenever V5 present; capped done 54-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_b11_2 | sharp V10 on return | typical V5 on return; whenever V5 present; capped done 54-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_b11_3 | sharp V10 on return | typical V5 on return; whenever V5 present; capped done 54-55; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_ditch_dig', 'o_door_gate', 'o_family_room', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_guard_n7', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_pot_hang', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_lane_watch_dry | never shown on any simulated route (design expectation in the brief applies) | |

## Brief names

The design briefs name these keys differently; this file's keys are the data file's:

- `l_posts` is `l_leaning_posts`

## Output

A TOML file, `key = "line"` per key below, in this order, lowercase, plain. Keys marked H also get `key_alt = "line"` right after. A draft missing an alternate is sent back. Every line within 75 characters; no digit; a name slot only as the rule above allows.

Keys (23, in order): l_family_1, l_family_2, l_hut_go, l_hut_theirs, l_hut_fail, l_join3_1, l_join3_2, l_guard_ask, l_arm_fail, l_guard_n2_1, l_guard_n2_2, l_guard_n7_1, l_guard_n7_2, l_leaning_posts, l_n6_posts_fail, l_n6_posts_done, l_count, l_night_12, l_vigil_fail, l_b11_1, l_b11_2, l_b11_3, l_lane_watch_dry

H keys (alt required): l_join3_1, l_join3_2, l_guard_n2_1, l_guard_n2_2, l_guard_n7_1, l_guard_n7_2, l_count, l_b11_1, l_b11_2, l_b11_3

## Shipped lines of the chapter before (day-nine)

{{PREVIOUS_PICKS}}

(The lead fills this with the previous chapter's shipped lines before the proposers start; reuse no phrase from them.)


## Drafts

### Draft A

{{DRAFT_A}}

### Draft B

{{DRAFT_B}}

### Draft C

{{DRAFT_C}}
