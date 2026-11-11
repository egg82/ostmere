# Proposer writer-3 input: day nine's lines (B9 to B10)

You are writing day nine's lines. This file is all you may see from the project's content; read nothing else.

## Your lens

what the animals already know

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

---

# Day nine's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `week-two.md`; the data is
`app/ashfall_app/opening/day_nine.toml`, where every key below reads "[day two: line to write]" (the marker's spelling is
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
a woman, two men, and another man behind them who keeps apart. States: present or on return. Special: the week's big
moment; the "but" is the gap in how the family stands, shown, never said.

**l_family_1, l_family_2** (O-family's lines). Facts: the woman does the talking; she asks if there is room inside the
wall; the man behind them sits down outside the gate and waits.

**l_find_pole** (Woodcutting 23), **l_camp_14** (stew holds 30).

### Changes to the section above (the data file wins)

- **l_family_1, l_family_2** and O-family are not in this chapter; **l_find_pole** shipped with day eight. Write neither.
- **l_road_smoke_1, l_road_smoke_2** are the brief's l_smoke_1, l_smoke_2 (E3). "smoke" also names the camp's own
  smoking rack and smoked meat; the road's smoke must not read as the rack's.
- B10's people: the woman, her husband, her brother, and the man who came with them. No names, no slots, no count of
  who they lost.

### The gap fire (SL18): this chapter's

The camp has kept a small watch fire at the gap since day three (shipped: "lucy lays stones at the gap. she brings
more." / "room inside for a fire, facing down the track." / "{n2} sits at the gap, the shaft on his knees."). SL18 builds
it up: a fire laid out in the gap itself, ringed with stones, so whoever sits the watch sits where the wolves come. Name
it so it does not read as a second, separate fire, and never as the camp's hearth.
- **l_gap_fire_1**: the moment it is shown (a trigger, with the card).
- **l_gap_fire_2**, **l_gap_fire_done**: stage lines 1 and 2 of 2 (dry wood and stones each stage). Plain records.
- **l_gap_fire_fail**: the failed-card line; short of dry wood, stones, or both.

### The fourth snare (SL17's spend)

- **l_snare_4**: the line when the fourth snare is set, from the old wire (two lengths of it) and dry wood. It never
  says whose wire, and never "your knot" or "again".
- **l_snare_4_fail**: the failed-card line; short of wire, dry wood, or both.

### The wind at the hides (the season's second chore)

The warm wind blows all through the season. It works the hide flaps over the bays' openings loose (day eight's flaps,
shipped: "the flaps hang over the openings, stiffening."). Pegging them again takes pelts and stones to weigh the hems,
done by the player or by Lucy on her lane.
- **l_wind**: when the chore is shown: the wind has torn the flaps loose. Shows the same hour on every route.
- **l_draughty**: the chip shows: the bays are draughty (rest is slower; the chip says so, the line does not).
- **l_draughty_off**: the chip clears, because the flaps were pegged down (by the player or by Lucy). It never says who.
- **l_peg_fail**: the failed-card line of both pegging cards (the player's and Lucy's): short of torn flaps to fix,
  pelts or stones. No "you", no "she": the card is shared.

### The Camp

**l_camp_14** (the stew holds more, lifted by the palisade's last stage). A plain record, no number.

### The camp's asks (offers): this chapter's main writing job after B10

While the ring goes up the camp puts small questions to the player, one at a time, one per return. Each is an offer:
a short text (the question, `o_*`) and two answers (`a_*`), each a button. Neither answer is judged, neither is the
right one, and declining costs nothing. **Write the offer text and both answer labels for every offer below**, after the
lines' keys in your output, as `o_rack = "..."`, `a_rack_high = "..."`, `a_rack_down = "..."`, and so on, in the order
listed.

Register: these are game UI with a person behind them, so sentence case with a capital first letter (unlike the lines),
plain, one sentence, at most about 60 characters for the text and about 22 for an answer, no digit. A name is a slot,
written exactly: `{n2}` (him), `{n3}` (the woman), `{n4}` (the old man); Lucy by name. Shipped offers, for the register
only: "Who goes to the ridge for her cart?" (answers "You go" / "She goes"); "Bank the fire her way or his?" ("Her way" /
"His way"); "Cover {n3}'s ground with a pelt or sacking?" ("Pelt" / "Sacking").

**Read in a row they must not feel like a quiz or a form.** Ten of them come one after another across the chapter. So:
- each has a different stake (what it costs, who it is for, what it risks), and the text makes that stake plain;
- vary the shape of the sentence: not ten "X or Y?" questions. Some are someone asking ("{n3} asks if..."), some say
  what someone wants or is doing and end on the choice, some are the choice alone; vary where the person's name sits;
- vary who asks and why (the asker is given; keep it);
- answers are short and active: a person doing a thing, in active voice ("You go", "She goes", "He sinks them"),
  never a bare noun pair every time; the two answers of one offer mirror each other in frame and length.

| Offer | Shows | Who asks, and the facts | Answer 1 (key, what happens) | Answer 2 (key, what happens) |
|---|---|---|---|---|
| o_posts | the palisade's second stage (late day eight), with its line l_posts | {n4} lashed the first stretch himself; the cord he twisted wet holds best of anyone's | a_posts_cord: he keeps twisting cord (his cord comes faster) | a_posts_fire: he goes back to sit the watch at the gap (the gap holds better) |
| o_margin | B9's moment: the book has just shown a note in the margin of the wolf page, in the player's own hand | no one asks; the player, reading the margin, which marks where the wolves come to | a_margin_gap: the watch is set where the margin says (the gap holds better) | a_margin_fire: the watch stays by the fire (everyone rests better) |
| o_rack | with E2, the morning after the pack stripped the rack's low rows | {n3}: what the pack left on the rack | a_rack_high: hang it high, inside the posts that stand (the rack holds more from now on) | a_rack_down: she smokes it down hard now (some smoked meat at once) |
| o_deep | the next return | {n2}: the ground on the low side is soft | a_deep_sink: he sinks the posts a hand deeper there (the gap holds better; his stakes come slower) | a_deep_pace: he keeps the pace (nothing changes) |
| o_bark | the next return | Lucy: the bark stripped off the poles is piling up | a_bark_tinder: dried for tinder (the fire burns less dry wood) | a_bark_cord: twisted into cord (some cord at once) |
| o_footing | the next return | {n4}: stones turned up digging the post footings | a_footing_hearth: a ring of them round a hearth in the bays (better rest) | a_footing_keep: onto the stone pile (some stones at once) |
| o_fed | the next return | {n3}: whoever sits the watch eats cold, out at the gap | a_fed_watch: a share of the pot carried out each night (the gap holds better; the stew comes slower) | a_fed_pot: the pot stays in the bays (nothing changes) |
| o_lookout | the next return | {n2}: he wants someone up on the stacked stakes, watching the road beyond the ridge | a_lookout_up: one up there (the gap holds better; his stakes come slower) | a_lookout_wall: everyone stays on the wall (nothing changes) |
| o_gate | the next return | Lucy: where the gate in the ring goes | a_gate_road: facing the road (a line follows: l_gate_road) | a_gate_track: facing the track (the track's run costs fewer roots) |
| o_skin | the next return, the last before the ring closes | {n2}: a wolf the watch killed; its skin | a_skin_post: nailed up on the posts by the gap (the gap holds better) | a_skin_flaps: on the flaps over the bays (one pelt at once) |

Must-nots for the asks: never "again"; no wolf sitting or waiting; o_margin never quotes the note, never says whose hand
(the player has just read that), never "remember"; o_skin is plain about a dead wolf's skin, nothing about how it died;
o_lookout and o_gate never say who is on the road, or that anyone is (the smoke on the road may not have been seen yet).

**l_posts** (o_posts' line, shown with it): {n4} at the first stretch, lashing it himself with his own cord. One line.
**l_gate_road** (when a_gate_road is given): the gate's place marked facing the road. One line; it never says who
will come by it.

Answer cost lines (`*_cost`), labels and the rest are the voice pass's, not the writers'.

## Where each key plays (read from the data file; "fires with" lines share one moment on screen)

| key | where it plays (from the data file) |
|---|---|
| l_ring_1 | trigger t_ring when store b9_clock >= 2; fires with l_ring_2 |
| l_ring_2 | trigger t_ring when store b9_clock >= 2; fires with l_ring_1 |
| l_gap_fire_1 | trigger t_gap_fire when store b9_clock >= 5 |
| l_gap_fire_fail | failed-card line of card gap_fire (craft; lane -); inputs dry_wood x6, stones x8 |
| l_gap_fire_2 | stage line 1 of 2 of card gap_fire (craft; inputs dry_wood x6, stones x8) |
| l_gap_fire_done | stage line 2 of 2 of card gap_fire (craft; inputs dry_wood x6, stones x8) |
| l_old_wire | trigger t_old_wire when card field_track done >= 6750; requires card gap_fire unlocked |
| l_snare_4_fail | failed-card line of card set_snare_4 (narrative; lane -); inputs wire x2, dry_wood x2 |
| l_snare_4 | line on finishing of card set_snare_4 |
| l_open_side_1 | trigger t_open_side when card palisade done >= 6; requires action e2_clock unlocked; fires with l_open_side_2 |
| l_open_side_2 | trigger t_open_side when card palisade done >= 6; requires action e2_clock unlocked; fires with l_open_side_1 |
| l_road_smoke_1 | trigger t_smoke when card palisade done >= 9; fires with l_road_smoke_2 |
| l_road_smoke_2 | trigger t_smoke when card palisade done >= 9; fires with l_road_smoke_1 |
| l_b10_1 | trigger t_b10 when card palisade done >= 12; requires action b10_floor unlocked; fires with l_b10_2, l_b10_3 |
| l_b10_2 | trigger t_b10 when card palisade done >= 12; requires action b10_floor unlocked; fires with l_b10_1, l_b10_3 |
| l_b10_3 | trigger t_b10 when card palisade done >= 12; requires action b10_floor unlocked; fires with l_b10_1, l_b10_2 |
| l_wind | trigger t_wind when store drift_clock >= 23 |
| l_draughty | chip draughty line when it shows |
| l_draughty_off | chip draughty line when it clears (by a cure, or by itself where it has none) |
| l_peg_fail | failed-card line of card peg_flaps (action; lane -); inputs wind_torn x12, pelt x3, stones x4 / failed-card line of card n1_peg_flaps (action; lane n1); inputs wind_torn x12, pelt x3, stones x4 |
| l_camp_14 | camp level at 1600000 items |
| l_posts | offer o_posts line (on screen until answered; fires with nothing) |
| l_gate_road | answer o_gate_road of offer o_gate: line when that answer is given |

## Generated states (the simulator's `--lines` over the typical, sharp, babysitter and whenever routes; replaces the brief's expected states where they differ)

Visit numbers count from the first visit of the chapter's pass, per route (a find can fire in a later chapter's visits). 'present' = the player is there when it happens; 'on return' = reads it after an absence. A line must read right in every listed combination. The answers listed are everything answered so far in the whole week, not only this chapter's.

| key | where it showed (route, visit, present or on return) | state |
|---|---|---|
| l_ring_1 | babysitter V1 present | sharp V1 on return; typical V1 on return; whenever V2 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_ring_2 | babysitter V1 present | sharp V1 on return; typical V1 on return; whenever V2 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_gap_fire_1 | babysitter V1 present | sharp V3 on return; typical V2 on return; whenever V2 on return; capped done 48-48; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_gap_fire_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_gap_fire_2 | babysitter V1 present | sharp V4 on return; typical V3 on return; whenever V3 on return; capped done 48-49; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_gap_fire_done | babysitter V1 present | sharp V4 on return; typical V3 on return; whenever V3 on return; capped done 49-49; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_old_wire | babysitter V1 present | typical V3 on return; whenever V4 on return; capped done 49-49; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_stay_room']; trip held; queue 0-0 |
| l_snare_4_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_snare_4 | babysitter V1 present | typical V4 on return; whenever V5 on return; capped done 50-50; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_stay_room']; trip held; queue 0-0 |
| l_open_side_1 | babysitter V1 present | sharp V4 on return; typical V3 on return; whenever V3 on return; capped done 49-50; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_open_side_2 | babysitter V1 present | sharp V4 on return; typical V3 on return; whenever V3 on return; capped done 49-50; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_cart_she_goes', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_road_smoke_1 | babysitter V1 present | sharp V6 on return; typical V7 on return; whenever V3 present; capped done 49-50; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_road_smoke_2 | babysitter V1 present | sharp V6 on return; typical V7 on return; whenever V3 present; capped done 49-50; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_b10_1 | babysitter V1 present | sharp V9 on return; typical V11 on return; whenever V8 on return; capped done 50-51; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_b10_2 | babysitter V1 present | sharp V9 on return; typical V11 on return; whenever V8 on return; capped done 50-51; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_b10_3 | babysitter V1 present | sharp V9 on return; typical V11 on return; whenever V8 on return; capped done 50-51; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_wind | babysitter V1 present | sharp V2 on return; capped done 48-49; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_draughty | babysitter V1 present | sharp V2 on return; capped done 48-49; answers so far, any of ['o_bank_hers', 'o_cart_go', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_stay_room']; trip held; queue 0-0 |
| l_draughty_off | babysitter V1 present | sharp V3 on return, V6 on return, V9 on return; typical V1 on return, V3 on return, V5 on return, V8 on return, V10 on return, V11 on return; whenever V2 on return, V7 on return; capped done 48-51; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_peg_fail | never shown on any simulated route (design expectation in the brief applies) | |
| l_camp_14 | babysitter V1 present | sharp V9 on return; typical V11 on return; whenever V8 on return; capped done 50-51; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_cart_she_goes', 'o_deep_pace', 'o_fed_pot', 'o_footing_hearth', 'o_gate_road', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_skin_flaps', 'o_stay_room']; trip held; queue 0-0 |
| l_posts | never shown on any simulated route (design expectation in the brief applies) | |
| l_gate_road | babysitter V1 present | typical V9 present; capped done 50-50; answers so far, any of ['o_bank_hers', 'o_bark_tinder', 'o_cart_go', 'o_deep_pace', 'o_fed_pot', 'o_footing_hearth', 'o_lookout_wall', 'o_margin_gap', 'o_pair_room', 'o_pelt_give', 'o_posts_cord', 'o_rack_high', 'o_stay_room']; trip held; queue 0-0 |

## Brief names

The design briefs name these keys differently; this file's keys are the data file's:

- `l_smoke_1` is `l_road_smoke_1`
- `l_smoke_2` is `l_road_smoke_2`

## Output

A TOML file, `key = "line"` per key below, in this order, lowercase, plain. Keys marked H also get `key_alt = "line"` right after. A draft missing an alternate is sent back. Every line within 75 characters; no digit; a name slot only as the rule above allows.

Keys (23, in order): l_ring_1, l_ring_2, l_gap_fire_1, l_gap_fire_fail, l_gap_fire_2, l_gap_fire_done, l_old_wire, l_snare_4_fail, l_snare_4, l_open_side_1, l_open_side_2, l_road_smoke_1, l_road_smoke_2, l_b10_1, l_b10_2, l_b10_3, l_wind, l_draughty, l_draughty_off, l_peg_fail, l_camp_14, l_posts, l_gate_road

H keys (alt required): l_ring_1, l_ring_2, l_open_side_1, l_open_side_2, l_road_smoke_1, l_road_smoke_2, l_b10_1, l_b10_2, l_b10_3

Then the offers, after l_gate_road, in this order (sentence case, a capital first letter, no digit; each offer text also gets one alternate, `o_*_alt`, of a different sentence shape):

Offer keys (40): o_posts, o_posts_alt, a_posts_cord, a_posts_fire, o_margin, o_margin_alt, a_margin_gap, a_margin_fire, o_rack, o_rack_alt, a_rack_high, a_rack_down, o_deep, o_deep_alt, a_deep_sink, a_deep_pace, o_bark, o_bark_alt, a_bark_tinder, a_bark_cord, o_footing, o_footing_alt, a_footing_hearth, a_footing_keep, o_fed, o_fed_alt, a_fed_watch, a_fed_pot, o_lookout, o_lookout_alt, a_lookout_up, a_lookout_wall, o_gate, o_gate_alt, a_gate_road, a_gate_track, o_skin, o_skin_alt, a_skin_post, a_skin_flaps


## Shipped lines of the chapter before (day-eight)

Day eight's shipped lines (the chapter just before this one):

```toml
l_ring_scored = "lucy drags a stick through the ash in a wide circle. no word."
l_palisade_fail = "you sort the pile. not enough for a stretch."
l_stage_1 = "the first posts go in along the scored line."
l_stage_2 = "stones wedged round the foot of each post."
l_stage_3 = "cord bound round the heads. the stretch stands."
l_stage_4 = "you walk the new posts from first to last."
l_stage_5 = "a post leans. you prop it with a stone."
l_stage_6 = "you haul stakes to the next stretch."
l_stage_7 = "{n2} puts his weight on a post. it doesn"t give."
l_stage_8 = "you shave the tops to points."
l_stage_9 = "the loose posts are dug up and reset."
l_stage_10 = "a slanted pole braces the weak stretch."
l_stage_11 = "you trim the cord ends close."
l_stage_12 = "the ring closes on itself."
l_cut_stakes_fail = "not enough wood to split into stakes."
l_lane_stakes_fail = "the wood runs out before the points do."
l_cord_fail = "there isn"t enough to twist a cord from."
l_n4_cord_fail = "{n4} sorts through the sticks and sets them down."
l_flaps_fail = "held to the opening, it doesn"t cover."
l_flaps_1 = "poles bent into a frame to fit the opening."
l_flaps_2 = "a pelt stretched on the frame, hair side out."
l_flaps_3 = "tied down at the corners with thongs."
l_flaps_done = "the flaps hang over the openings, stiffening."
l_b8_1 = "the wind turns warm, all from one side. ash browns the noon."
l_b8_2 = "the larder won"t hold more. the rafters creak."
l_b8_3 = "fungus juts from the stumps. up on the roof, crows call numbers."
l_pick_fail = "every stump is picked bare."
l_fungus_stew_fail = "the pot stays on its hook. something is short."
l_howls = "howls, answering each other. prints circle the rack, not the fire."
l_caps_1 = "{n3} sorts the caps. half go in the fire."
l_caps_2 = "the pot passes hand to hand, still not empty."
l_ash_laden = "the roof hangs low over where you sleep."
l_ash_cleared = "the roof poles stop creaking."
l_clear_fail = "too little ash overhead to shovel."
l_roofs_first = "the roofs shed their ash in slabs under the shovel."
l_ash_ground = "{n3} works ash in by hand, counts seed, and ties the bag shut."
l_ash_ground_fail = "{n3} looks in the sack. not enough ash in it."
l_cord = "{n4} rolls bark into cord over one knee. fast."
l_pack_1 = "a handful of wolves gather near the gap. a brand turns the first."
l_pack_2 = "the others wait out of reach. the low strips go with them."
l_fight_pack_won_1 = "a brand swung low and the pack backs off."
l_fight_pack_won_2 = "the wolves give the gap up and trot off."
l_fight_pack_won_3 = "the pack noses up and finds you waiting."
l_fight_pack_lost_1 = "the lowest strips on the rack are gone."
l_fight_pack_lost_2 = "the bottom pegs are empty."
l_fight_pack_lost_3 = "the lower poles are picked clean."
l_b9_1 = "the book lies open in the firelight. rats first, then crows."
l_b9_2 = "the wolves" page is empty. at its edge, a pencil note. your hand."
l_find_shelf = "a fungus shelf on a birch, still firm."
l_find_pole = "a straight birch pole, barked and dry."
l_find_hoe = "the head of a hoe, rust-pitted but whole."
l_find_pot = "a small pot with a dent. it holds water."
l_find_fine_ash = "fine pale ash, sifted by wind into a hollow."
l_camp_13 = "stakes stacked by the shed, points all one way."
```

(The lead fills this with the previous chapter's shipped lines before the proposers start; reuse no phrase from them.)
