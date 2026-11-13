# Day one: from the opening's end to the first arrival

Spoilers: this file is under `content/` and never shown to the owner. It picks up where `opening-v2.md` ends (story dusk,
day 1) and runs through the night and story day 2 to B3. Its data twin is `beats.yaml`'s `day_one:` list (ids, gates,
shape fields, checked by `team/flatcheck.py`); its canon is C-promise-16 and C-beat-68 to C-beat-78 in `canon.jsonl`;
its decisions are D-57 to D-63. **Every number below is provisional**: the simulator's routes set them, and the line
state lists are generated from those routes, not written by hand. Schema, engine and page work come in later steps;
this file only says what they must carry.

Binding: day and night run on the story's clock, not the real one; a planned moment that lands while
the player is away plays in full on return; the daylight grade is look-tested with the owner before it is used.

## The shape

Four visits. V1 is the session the opening ends in; V2–V4 are the next sessions a typical player has, 1–12 hours
apart. "Visit" is a stage of the content as a typical player meets it: a lazy player who returns once a day meets two
or three in one sitting, a babysitter meets them back to back.

The day is one causal chain the player builds themselves: **you make smoke, she comes to look, a fair trade, food to
spare, she sits down.** Every link is something the player chose to build; the story only says what it looks like
from outside.

- **The near question** (C-promise-16, *who is out there?*) is the light on the ridge at the opening's dusk. It is
  advanced on every visit and answered at the last, by B3 (D-60, a deliberate change from `opening-v2.md`, which
  answered it "in the next session").
- **The deep pull** gets one beat, H4 (an old snare where you set yours). Not B5, not B6: the warm ground and the
  hand on the stone stay theirs.
- **Story clock.** The opening ends at dusk. The night is about one game hour (the `night` store, the evening's
  pattern). Story day 2 then lasts until B3, however long that takes: one long grey day, the `day` grade. Still the
  Still: no wind, fog in the low ground, sound carries.

## The pull, visit by visit

| Visit | Gap before | What moves the near question | Beat |
|---|---|---|---|
| V1 | 0 | the light is still there at night, kept low, never moving; one howl, far off | H1 (opens) |
| V2 | 1–12 h | morning, the light is out; by day, on the ridge where it was, something dark and square; the lean-to's open side faces the gap and the ridge | H3, H5 |
| V3 | 1–10 h | the smoke stands straight up, visible for miles: the player has told the valley they have meat | H6 |
| V4 | 1–12 h | one set of prints to the larder; three roots gone, a strip of someone else's smoked meat left; she walks out of the ash | H7, B3 (pays) |

## Timeline

T, D and effort are per visit. Minutes inside a visit are active minutes. **Bold** marks the bigger new things.

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| V1 (12–18 min, continues the opening's session) | reads the end lines; takes the shipped **rest-rule offer**; the Rules tab glows as the door to Mixes; optionally sits up with the fire (A11) | night starts at the end (t_night on keeps_going); H1's lines a few minutes into the night; Camp 3 lands (un-held); the finds behind the opening's "?" markers land as their levels come: Scavenging 4 the wire, Foraging 2 the tinder fungus, Woodcutting 3 "the builds" | night grade: crack glow, ridge light, firelight | l_night_1, l_night_2 (H1), l_sit_up (A11), l_wire_1, l_tinder, l_wc_3, l_camp_3 |
| V2 (5–8 min) | looks out past the gap (A12); **sets three snares** (A13 and its two later pushes: Scavenging 4–6's wire is all in hand by morning); walks back and **looks over the camp by daylight** (A14); **chooses** which of two builds first; **switches mixes**, since the lean-to pulls on dry wood and the larder on stones; builds the first and queues the second with **When ready**, meeting the **Next** list; builds the rack; takes the **rising-line rule** "4 or more catch → Smoke" on the rising catch line | morning (t_morning, ~1 h after the end): H2 on return; A12 opened by morning; set_snare opened by A12; the snares' ledger line "catch +3/h · full in 2h"; look_over_camp opened by the first snare; lean-to, larder and the rack in view together at look_over_camp (H5), unready on wood and stones; the rack opens the Smoke lane, smoke_catch, the **Cooking** row and the catch rule's order card | day grade (look-tested first); ridge shape with a faint square silhouette in the haze; steam over the fog in the valley bottom; the figure crouched at the birch; the camp by day; lean_to or larder | l_morning (H2), l_look_out_1, l_look_out_2 (H3), l_snare_1 (H4), l_snare_fail, l_snare_3, l_camp_daylight (A14), l_rack_shown, l_lean_to, l_larder (H5, each with order variants), l_lean_to_fail, l_larder_fail, l_rack, l_rack_fail, l_cooking_open |
| V3 (5–8 min) | with the catch rule set: reads H6 and H7 (both landed while away) and taps **Take stock** (B3), or queues it when its roots are short, **taking the roots rule "until 15"** offered under the roots line, and/or **choosing what to smoke**; without the rule: runs the first **Smoke** by hand and meets H6 here, and H7 and B3 wait for V4 | the first catch (t_first_catch, ~20 min after the snares); H6 on the first Smoke completion, by the catch rule while away, opening smoke_roots; H7 ~90 game min after it, opening Take stock; Camp 4 and 5 by now | smoke_rack, meat_on_rack and smoke_plume while smoke runs; catch_hanging; prints | l_first_catch, l_smoke_1 (H6), l_smoke_fail, l_smoke_roots, l_prints_1, l_prints_2 (H7), l_camp_4, l_camp_5 |
| V4, or V3 for the rule user (B3) | **re-tunes the ledger and rules for two** | Cooking 2; Take stock done by tap or the queue once larder, rack, H7, smoked ≥ 6 and roots ≥ 12 all hold; B3; n1_eating turns the smoked and roots lines red with their answers; the Camp's held "?" lifts and the next marker reads as a choice | N1 walking in at the gap, then sitting at the fire on the player's side | l_cooking_2, l_take_stock_fail, l_b3_1 to l_b3_4 (B3), l_camp_6 |

**Per visit** (the simulator's checks, for any visit after a gap of an hour or more): at least one bigger and three new things, the first
within 60 s; at least one decision; no idle stretch over 90 s inside the visit's activity window (up to the player's
last act and that step's own landings); no run of one card over 3; effort between bigger things at most 10. Active
minutes are reported, never a bar: a two-minute return with a real decision is a good visit.

**What fills each visit** (D-63, D-64): V2 is the morning's work, the snares and then the camp by daylight, which
brings the two builds and the rack into view while the player is there, so the choice, the mix switch, When ready and
the rack all happen in V2. From there the chain runs on the player's setup (D-64): with the catch rule set, the smoke,
H6 and H7 come while they are away, as soon as the catch allows, and B3 waits only for their return; without it, the
first smoke waits for V3 and H7 and B3 for V4. So a better setup brings H6, H7 and B3 hours sooner (the human-paced
report's earned unlocks), while H1 and H2 stay on the story's clock. **The visit B3 is seen in** plays H7's and B3's
lines and the re-tune for two; the rest of its play is day two's, which is not built yet.
**Per absence:** at most two unlocks (the V2–V3 absence opens H6 and H7; Take stock opens with H7, on its condition,
so the two are one moment). Nothing opens on a tap count; no level opens anything (levels pay finds).

B3 landing, game hours after the end: on every route that uses the queue and the rules, no later than the
babysitter's plus one of the route's visit gaps for each step in B3's chain that waits for the player (read off the
content: bands.presence_steps); the typical route within 10–28 h (story day one plus slack); the babysitter not before
3 h. Measured with D-64: babysitter 3.9, sharp 5.7, typical 12.5, by_hand 16.7, lazy 48.5.

## Cards, stores, lanes, standing actions

All provisional. Same schema as `opening.toml`; everything is additive (new ids, appended levels, raised caps, new
triggers), so it passes the content lock.

### Stores

| Store | Cap | Notes |
|---|---|---|
| wire | 3 | each find adds 1, each snare takes 1; holds all three, since Scavenging 4–6 land in the night |
| tinder_fungus | 1 | Foraging 2's find; the rack takes it |
| catch | 6 (9 at Camp 4) | from the snares; ashrats, R1's only small prey (C-creature-4) |
| smoked | 4 (12 with the larder) | the rack's make; smoked ≥ 6 therefore needs the larder |
| roots | 12 from Camp 2 (24 with the larder) | existing store |
| night | 1 | never unlocked; filled by `night`, ~60 game min |
| h7_clock | 3 | never unlocked; filled at 2/h from H6, so ~90 game min |

### Standing actions

| Id | Unlocked by | Makes / costs (per hour) |
|---|---|---|
| night | t_night (on keeps_going; a new trigger, t_evening untouched) | night +1 |
| snare_1, snare_2, snare_3 | each set_snare push (t_snare_1..3 on its card_count) | catch +1 each |
| h7_clock | H6's trigger | h7_clock +2 |
| n1_eating | B3 | smoked −1, roots −1 |

### Cards

| Card | Story id | Lane | Cap | Bar (s) | Takes / requires | Makes / effect | Opened by |
|---|---|---|---|---|---|---|---|
| sit_up | A11 | hands | 1 | 20 | | line only | t_night; retires at morning (open question 1) |
| look_out | A12 | hands | 1 | 5 | requires night ≥ 20 (first light) | H3; opens set_snare | t_first_light_shown (night ≥ 1, H1's moment), so its countdown to first light is on the cards through the night; no When ready (the page's rule for a store never shown) |
| set_snare | A13 (first push) | hands | 3 | 8 | 1 wire per push | snare_1, 2, 3 | look_out |
| look_over_camp | A14 | hands | 1 | 5 | | H5: the two builds in view | set_snare's first push |
| build_lean_to | P0.1 | hands (craft) | 1 | 20 | 10 dry wood, 2 stones; Woodcutting 3 | upside "Rest under cover": weariness cost ×0.75 | look_over_camp, with the larder |
| build_larder | P0.2 | hands (craft) | 1 | 20 | 4 dry wood, 12 stones; Woodcutting 3 | upside "Food keeps": roots cap ×2, smoked cap ×3 | look_over_camp |
| build_smoke_rack | P0.3 | hands (craft) | 1 | 30 | 10 damp wood (green poles), 1 tinder fungus; requires A14 done | the Smoke lane, smoke_catch, Cooking, the catch rule's order card | look_over_camp, with the builds (t_rack, at the first catch, opens it for a player who left before A14) |
| smoke_catch | | smoke | none | 80 | 4 catch, 2 damp wood | 2 smoked (3 at Cooking 2); Cooking XP | the rack |
| smoke_roots | | smoke | none | 80 | 3 roots (the shipped roots rule's floor, so a return while the visitor takes roots can smoke some), 2 damp wood | 2 smoked; Cooking XP | the first smoke_catch completion (t_smoke_roots, H6's condition) |
| take_stock | P0.4 | hands | 1 | 10 | requires: larder built, rack built, smoked ≥ 6, roots ≥ 12; spends nothing | B3 | t_stock_shown, on H7's condition (h7_clock empty) |
| cook_roots | | hands | none | 4 | 3 roots; requires strike_fire done | fullness +7; the roast's label and failed line | t_cook, as roast_roots is done (its count ≥ 1); eating's roots drain stays, as the roots rule's Foraging rests on it |

The two builds and the rack open in front of the player (A14), so nothing opens or builds unseen: the second build
completes while away only if the player queued it. They pull on different stores, the lean-to on dry wood (ten is more than the wall's rule
keeps, so some is laid by hand or the rule's bound raised) and the larder on stones (it is stacked stone, off the warm
ground), so the need is a mix switch rather than one card laid four times running. The rack is green poles, so it
takes damp wood (dry wood is for burning), and it is never ready unseen: it shows while the player is there, and A14,
which it requires, is a tap. Its line (l_rack_shown) comes at A14, right after the soft roots: what the warm ground does to food is
why the meat the snares will bring wants smoke.

Damp wood's first second use is the smoke lane (the wood is meant to smoke). The stool/fireback shape returns in the
two builds: each card names only its upside, the cost is what the other card's time then reads. Lean-to first leaves
roots and smoked capped low; larder first leaves weariness at its full rate.

### Order cards

- Under the catch line, when catch is full and the rack idle: "4 or more catch → Smoke" (`when` at_least 4, release
  under 4; order cards today take only at_most, so the schema gains at_least; the engine already solves it). It is the first rule on a rising line.
- Under the roots line, once Take stock shows its roots need: "under 13 roots → Forage, until 15" (`when` at_most 12,
  release 15; Take stock needs the rule's lower level, never its release, since the roots drain and reach the release
  only as the rule lets go: the loader refuses a need at or past it; offered once Take stock is unlocked and the larder built, since the release must stay under the roots
  cap, 12 without the larder and 24 with it; the loader checks it against the 16 the larder alone makes certain). The shipped roots rule stops at 6, so Take stock's need is the
  reason to change a rule's bound: the first rule re-tuned rather than added. Fits into: order cards, an existing
  card on an existing store with new bounds.
- After B3: the existing roots rule is offered again under the red roots line, since n1_eating re-tunes it.
- In the hands strip while hungry, once the end card is put away and cook_roots is open (as the tired chip's rest rule
  is): "While hungry → cook_roots", `when` the chip's own. The card opens as the roast is done, the same label staying
  on the panel, so it is there before hunger comes back 40 to 70 min later. Hunger comes back every ~70 min after a cook;
  with the rule set, time away never leaves the chip on. Fits into: chip order cards (the tired one's shape).

### The weave and the screen (the day's sink)

From the end the hands make far more damp wood than its cap holds, so without a sink a day away brings what a night
away brings. Both cards are on offer from the end (t_screen_open, on keeps_going), while the player is there.

| Card | Lane | Cap | Bar (s) | Takes | Makes / effect |
|---|---|---|---|---|---|
| weave_wattle | hands, in the mix | none | 180 | 18 damp wood | 1 wattle (store cap 24). In the mix it takes the damp wood the hands make |
| screen_fire | hands (craft) | 4 | 30 | 24 wattle (a full store), 12 stones a stage | stage lines l_screen_1 to 4; the last stage: feature `screen` (a scene stamp) and the cold takes warmth ×0.75 |

The screen's order card ("24 or more wattle → screen_fire", offered with the card) builds a stage whenever a stage's
wattle is in, so it runs while away and is passed over at the cap. A wattle hurdle beside the fire, a second angled to
it, a third, then the screen ringing the fire: the camp made less miserable on the first night by what the hands made
while the player was gone. Sized so the typical mix has a stage up by the first return (about 3 h), three in a night
away from V1 and all four in a day; a player who builds by hand gets a stage per visit. Its pay is the cold, not a
rate, so the 2 AM test only needs it shown unready (wattle 0/24) while the player is there, which it is from the end.
Once the screen stands the weave has no use, and the player takes it out of the mix.

### Levels and finds

The opening's "?" markers each pay a find, never an opening. The curve (`curve_items`) gains levels by appending only:
to level 20, each step half again the last (60, 100, 160 … 24 400 items of XP), so no row tops out in day one on any
route and time per level never shrinks (`tests/dayone/growth.py`). Every level past the finds pays its own skill's
work a tenth faster (`target = "work"`: more made an hour, the same XP), so after the end every row has a next level
the mix drives, and the player's weighting decides which comes first (the taper; `tests/dayone/goals.py`). A "?" that
paid nothing is gone: every marker pays when its level lands (`tests/opening/test_level_pays.py`). Among the levels
day one reaches (measured on every route at B3 seen: Scavenging to 17, Woodcutting to 19, Foraging to 7, Cooking to 2),
at least every third pays a find beside its speed-up (`tests/dayone/test_dayone_level_pays.py`).

| Skill | Level | Pays |
|---|---|---|
| Scavenging | 4 | wire (the first snare) |
| | 5 | wire (the second snare) |
| | 6 | wire (snare 3) |
| | 7–20 | searches faster (×1.1 each); l_scav_faster at 7 |
| | 9, 11, 12, 15 | also a find: a roof beam (damp wood +4), a lintel (stones +3), a doorway's step (stones +3), a chimney (stones +4) |
| Woodcutting | 3 | "the builds" (lean-to and larder require it) |
| | 4–20 | cuts faster; l_wc_faster at 4 |
| | 6, 9, 12, 13, 15, 18 | also a find: deadfall (dry wood +4, at night), a tipped birch (stones +3), a green birch (damp wood +5), a hung birch (damp wood +4), a clear view to the gap (damp wood +3), a thick birch (damp wood +6) |
| Foraging | 2 | tinder fungus (the rack) |
| | 3–20 | forages faster; l_for_faster at 3 |
| | 5 | also a find: a root hollow (roots +4) |
| Cooking (row opens with the rack, D-61) | 2 | +1 smoked per smoke_catch batch |
| | 3–6 | smokes faster (both smoke cards); l_cook_faster at 3; then "no more yet" (a lane skill: the mix does not drive it) |

Scavenging 4–6 all land in V1's night on every route, so the three wires are in hand by morning and A13's three pushes
come together in V2. A wire that a level finds has no ready time the queue could wait on, so a later snare could not be
queued (the 2 AM test); spreading the snares over the day needs that first.

### The Camp

| Level | At (camp items) | ~ hands-work hours | Pays |
|---|---|---|---|
| 3 | 1500 (shipped, held; lifted by a new trigger at the same threshold) | 0.4 | the wall takes 7 (lay_to_dry batch 5 → 7) |
| 4 | 10 800 | 3 | catch holds more (6 → 9) |
| 5 | 28 800 | 8 | the smoke lane's batch +1 |
| 6 | 54 000, held ("?"); the camp store's cap rises to 53 999 so the bar fills to just below it | 15 | lifted by B3 (its outcome raises the camp cap): roots and smoked hold half again (room for two); the next marker reads as a choice (the town's first, drop 2) |

Camp bonuses never touch mix card rates: caps and lane batches only. Schema: a held level may be non-last if it names
`lifted_by` (a schema change, a later step).

## The beats

Fields as in `beats.yaml`. Facts each writer may use are the canon ids named; nothing else.

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread | Canon |
|---|---|---|---|---|---|
| H1 | V1 | the end (t_night); lines a few minutes into the night, after the end lines | The ridge light is still there, kept low; it never moves. Far off, one long howl, carried by the still air. A11 (optional): sitting up with the fire, the light is minded the way you mind yours. | down · none · dread · none · PC · opens C-promise-16 · th-ridge start | C-beat-69 |
| H2 | V2 | ~1 game hour after the end (t_morning) | A grey morning; the ridge light is out. The unwrap reads as what the night got done. | up · none · wry · time · PC · none · th-survive | C-beat-70 |
| H3 | V2 | A12 | The Hollow by day: a bowl valley, fog lying in its bottom with the warm stream's steam rising out of it, old fields under ash, scrub birch. On the ridge where the light was, something dark and square the dusk hid. Never named. Opens the scrub: set a snare. | up · yes · wonder · none · PC · advances C-promise-16 · th-ridge | C-beat-71 |
| H4 | V2 | A13 (needs wire) | In the run the player chose there is already a snare, decades old, rusted through, in the same place. Nothing says whose or how it was tied. Mundane, ominous only in hindsight; N9 pays it at B34. | down · yes_but · dread · none · PC · none · th-survive | C-beat-72 |
| H5 | V2 | A14, looking over the camp by daylight (after the first snare) | By daylight the camp shows what the night did to what was left out: ash settled on everything, the player included, and the roots stacked by the warm wall gone soft. Two builds, one choice: a lean-to (rest under cover) and a larder (food keeps). Both get built; the order is the choice. The lean-to's open side faces the gap and the ridge. | up · yes_but · wry · option · PC · advances C-promise-16 · th-survive | C-beat-73 |
| H6 | V3 | the first smoke_catch completion | In the still air the smoke stands straight up all afternoon. Anyone for miles can see you have meat. Wry, about the player's own build. | up · yes_but · wry · time · PC · advances C-promise-16 · th-ridge | C-beat-74 |
| H7 | V4, usually met on return | ~90 game min after H6, roots ≥ 3 | Prints in the ash, one set, through the gap to the larder. Three roots gone. On the warm stone, a strip of smoked meat the player didn't smoke. Someone hungry and honest came to look. True whether the player was present or away: in-world, the figure was at the snares. | down · no_and · dread · stores · N1, PC · advances C-promise-16 · th-ridge end | C-beat-75 |
| B3 ★ | V4, usually met on return | P0.4 Take stock | You count the food twice and look up. She walks out of the ash at the gap, sees food to spare, and sits down, on the player's side of the fire. She eats from the larder. The town is founded from the camp. | as `beats.yaml` (up · yes · warm · stores · PC, N1 · pays C-promise-16 · th-survive) | C-beat-3, C-beat-76 |

**The flat check, authored order:** turns B2 up, H1 down, H2 up, H3 up, H4 down, H5 up, H6 up, H7 down, B3 up (never
three the same); one clean yes (H3) between yes_buts; H7 the day's no_and; registers dread, wry, wonder, dread, wry,
wry, dread, warm (never four the same); costs time, option, stores (three kinds); the near promise touched on V1–V4.
`flatcheck.py` checks all of it per route, plus gates landing before what they gate. Result on the authored order:
clean.

**Mechanically, B3:** take_stock's completion plays B3's lines, unlocks feature n1 and standing n1_eating, takes 2
smoked at once (her first meal), and raises the camp cap so Camp 6 lands. The smoked and roots lines go red with
their answers beside them, so the ledger and rules are needed again. Not in this drop: roster, roles, souls, ties, her
work, housing (drop 2). B4 (day 3) is the first offer, so the next drop needs Offers.

## Away from the screen

- **Every planned moment plays in full on return** (binding): H2, H7 and often B3 land while the player is away;
  each is revealed in order after the return, one at a time, with its scene.
- **H7 is a story cost, never a penalty for absence** (D-59): it fires on its timer whether the player is watching or
  not, takes the same three roots and leaves the same strip, and the lines are true either way.
- **The 2 AM test:** a babysitter and a whenever-with-queue player end equal in stores, XP and rate-boost times given
  the same reveals; every rate- or cap-raising step (the builds, Take stock) is shown unready while the player is
  present, before it can be afforded, so it can be queued, or turns ready while the player is there.
- **Rebased saves:** an ended opening save loaded into day one gets night at once and morning ~1 h later; new triggers
  fire at the rebase instant, at most two unlocks, the story in order.

## Line moments, and the states each can fire in

Written by blind proposers scored on `rubric.md`, picked line by line by the lead, then a voice pass; the brief is
`day-one-lines-brief.md`. Each line must be true in every state on its list.

**How the lists were made.** `python -m tests.dayone.report --lines` (from `app/`, in the CI image) plays the ten
routes (typical, sharp, lazy, by_hand, larder_first, evenings, lunch, return_22h, babysitter, whenever) and prints, per
line key, the visit each fired in and whether the player was there ("present") or it landed while they were away
and plays on return ("on return"). The babysitter is one long visit, so it is always present. The game-state facts
beside each list are read off the same run's landed hours (what had already landed when the line fired), or, for the
failed lines no route taps, off the card's own inputs and requires in `day_one.toml`. Regenerate after any content
change.

| Id | Fires when | Where it fired (10 routes) | State on every route |
|---|---|---|---|
| l_night_1, l_night_2 (H1) | the night store's first item, minutes after the end | V1, present on all 10 | the opening just ended: fire lit, both crafts built, the roast eaten; book read or not; no wire spent, no snare in view; a rebased save gets it on first load |
| l_sit_up (A11) | sit_up | V1, present on 9 (the lazy route never taps it) | night; the same opening state |
| l_morning (H2) | t_morning, ~1 game hour after the end | on return on 9 (the return is 1.1 to 24 h after the end), present for the babysitter | night over; the rest-rule offer taken or not; all three wires already found; nothing built since the end |
| l_look_out_1, l_look_out_2 (H3) | look_out starts, finishes | V2, present on all 10 | the first thing tapped on the return, right after l_morning's unwrap; three wires held; no snare yet |
| l_wire_1, l_wire_2 | Scavenging 4, 5 | V1, present on all 10 | at night, by the mix; set_snare not yet on screen, so the wire has no visible use |
| l_wire_3 | Scavenging 6 | on return on 9, present for the babysitter | at night or in the morning, before any snare; no visible use yet |
| l_tinder | Foraging 2 | V2 present on 3 (sharp, evenings, lunch), on return on 6, babysitter present | night or day, by the mix; the rack card is not yet on screen on any route, so its use is not visible |
| l_snare_1 (H4), l_snare_2, l_snare_3 | set_snare pushes 1, 2, 3 | V2, present on all 10 | the three within about a game minute, right after look_out; the first snare is H4's |
| l_snare_fail | set_snare tapped with no wire | no route | derived: only if Scavenging 6 has not landed by the third push (a player who stopped scavenging); one or two snares already set; daytime |
| l_camp_daylight (A14) | look_over_camp | V2, present on all 10 | right after the three snares; no build yet; roots held (any count) |
| l_lean_to, l_larder (H5) | each build | V2, present on all 10 | within a minute or two of A14. Every route built the larder first (the simulator's policy), but the player may choose either order, so each line must hold with the other built or not |
| l_lean_to_fail | build_lean_to tapped unready | no route | derived: dry wood under 10 or stones under 2 (or, rarely, Woodcutting under 3); the larder built or not; V2 or later |
| l_larder_fail | build_larder tapped unready | no route | derived: dry wood under 4 or stones under 12 (or Woodcutting under 3); the lean-to built or not; V2 or later |
| l_first_catch | catch reaches 1 | on return on 9, babysitter present | ~20 min after the snares; both builds and the rack done (the rack's card, with its line, came at A14) |
| l_rack_shown | the rack card unlocked (A14; for a player who left before A14, the first catch) | V2, present on 9, babysitter present | right after l_camp_daylight's soft roots; the snares set, no catch yet; no build yet |
| l_rack | build_smoke_rack | V2, present on 9, babysitter present | the snares set and A14 done; the builds done or not; no catch yet on any route |
| l_rack_fail | build_smoke_rack tapped unready | no route | derived: damp wood under 10 or no tinder fungus (A14 is always done by then); V2 or later |
| l_cooking_open | the rack's finish | V2, present on all 10 | the same instant as l_rack; smoke_catch just appeared, no catch to smoke yet |
| l_smoke_1 (H6), l_smoke_roots | the first smoke_catch completion | on return on 8 (the catch rule's smoke), V3 present on by_hand (by hand), babysitter present | ~80 min after the snares at the soonest; builds and rack done; smoke_roots just appeared; the visitor's drain on roots starts at this instant (a ledger line under roots appears) |
| l_smoke_fail | smoke_catch or smoke_roots tapped unready | no route | derived: catch under 4 (or roots under 3 for smoke_roots), or damp wood under 2; one line for both cards; V3 or later |
| l_cooking_2 | Cooking 2 | on return on 3 (evenings, lazy, lunch), babysitter present; never before B3 on the other 6 | after the first smoke; before or after H7 |
| l_prints_1, l_prints_2 (H7) | h7_clock empties, ~90 game min after H6 | on return on 9, babysitter present | three roots gone and one smoked added; larder and rack built on every route; Take stock appears the same instant |
| l_take_stock_fail | take_stock tapped unready | no route | derived: the first blocker shown is smoked under 6, then roots under 15, then larder, rack; V4 |
| l_b3_1 to l_b3_4 (B3) | take_stock | tapped on the return after H7 (V3 on 4, V4 on 5), babysitter present | the prints already landed; smoked 6 or more, roots 15 or more; any real time of day |
| l_camp_3 | Camp 3 | on return on 9, babysitter present | after V1, night or day; anything from before the snares to after the builds |
| l_camp_4 | Camp 4 | V3 present on 2 (evenings, lunch), on return on 7, babysitter present | after the snares; before or after the rack |
| l_camp_5 | Camp 5 | on return on 8, babysitter present; not on sharp | after the rack on every route reaching it |
| l_camp_6 | Camp 6 (lifted by B3) | with B3: on return on 7, V4 present on by_hand, babysitter present; not on sharp (its camp bar is short of the held level at B3, so the line comes later) | after B3 on every route; she is there |
| l_look_out_fail | look_out tapped before first light | no route | derived: night only (the card is ready from t_morning on); H1 played; the ridge light still lit; sit_up tapped or not |
| l_wc_faster | Woodcutting 4 (the first faster level) | V1, present on all 10 | at night, by the mix, minutes after the end; nothing built since the end |
| l_scav_faster | Scavenging 7 | on return on 9, babysitter present | at night or in the morning, after the three wires; before or after the snares |
| l_for_faster | Foraging 3 | V2 present on 7, on return on 3 (lazy, return_22h, whenever) | by day, after the tinder; before or after the builds |
| l_cook_faster | Cooking 3 | babysitter present only; the other routes reach it after B3 | after the first smoke; before or after H7 |

**A shipped line that now fires in day one:** l_hungry (the opening's) fires again on return on 9 routes and present
for the babysitter. Its text was written for the opening; the voice pass checks it still holds in day one.

Labels and upsides go to the voice pass, not the writers (`day-one-lines-brief.md`, "Labels"). The must-nots are in
the brief.

## Art

Tools: `tools/scene` conventions. Composites checked at 390×844 and 3840×2160.

- **Grades:** `day` (grey, flat, low contrast), after `dusk` in GRADES; look-tested with the owner before use. Add
  until="feature:morning" on crack_glow, ridge_light and firelight_dusk; a later grade wins over the dusk pinned at
  ended_at.
- **World layers (cool):** ridge_shape (feature:morning; the faint square silhouette in the haze), valley_fog_1-4 with
  stream_steam_1-3 rising through it (A12 done), prints (feature:prints).
- **Player-made (warm):** lean_to (its open side toward the gap), larder, smoke_rack, meat_on_rack (running:smoke),
  smoke_plume (a tall, thin, straight column, running:smoke: it carries the story), snare_1 to snare_3, catch_hanging
  (store:catch).
- **Poses:** crouched at the birch setting a snare; at the rack (if a tap); building (hit frame); standing at the gap
  facing out; sitting up at night.
- **N1:** a second Time Fantasy chibi set (not 2_3), grimed like the player. Walking in at the gap during B3's lines;
  then sitting at the fire **on the player's side** (feature:n1), at an angle, not covering the seat or the stool.
  The far side of the fire is B6's (D-62).
- **Stages:** 10_night, 11_morning, 12_snares, 13_builds, 14_smoking, 15_prints, 16_arrival.

## Where canon shaped the design

- **H5 advances the near question** (the lean-to faces the gap and the ridge): one fact in a build already being
  made costs nothing, and it keeps the ridge in the player's own choices. V3's advance is H6, which lands inside V3
  (an 80-second batch run while the player answers Take stock).
- **A14 shows the camp by daylight, not the ground under it:** what the night did to what was left out (ash settled on
  everything, the player included; the roots stacked by the warm wall gone soft). The warm floor and wall are the
  opening's (P3, P4); nothing new about the ground, so B5 stays B5's.
- **H4 opens nothing.** Canon opens Q2 at B9 (C-promise-2), so the snare is softened (D-58): no "set your way".
- **H3 has fog in the valley bottom.** The Still has fog in low ground (C-season-2); the stream shows as steam
  rising out of it.
- **N1 sits on the player's side at B3,** not across the fire: B6 (C-beat-6) has her sit on the far side that night,
  which only reads if it is a move.
- **Cooking's row opens with the rack** (D-61): canon had A10 (the roast) open Cooking, but the shipped opening's
  roast opens no skill and is locked; canon now matches what shipped.
- **A13** is a new story id for the first snare, so H4 has a step to gate on; snares 2 and 3 are the same card's
  later pushes.
- **H7 also needs roots ≥ 3,** so the trade is always whole and its lines never have to cover an empty larder.
- **H1's lines come with the night store's first item** (three minutes into the night), so they don't land on the
  dusk lines.
- **The smoke batch is 80 seconds and takes 4 catch,** the snares' first 80 minutes, so with the rack built in V2 the
  first smoke (H6) is the catch rule's, while the player is away, or the player's own at their next return.
  smoke_roots opens with H6 (meat first, then the thought that roots could hang too), so the first smoke is always
  the catch's and the visitor always comes to meat.
- **The rack is the one B7's pack strips** (C-beat-7, "the drying racks"): day one builds what week one loses.

## Open (content side)

1. A11 is a night-only flavour step. Keep it on offer until morning and retire it untapped, or keep it until tapped
   (its line must then also be true by day)? Recommendation: retire at morning; it opens nothing. This one can go to
   the owner spoiler-free: "can a small optional step be on offer for a stretch (one night) and then go, if nothing depends
   on it?"
2. H7's strip of smoked meat: she has meat but comes for food. Reading: she has had nothing but dried meat for days;
   roots are what she lacked, and the strip is fair pay. If the critic finds it strains, the fallback leaves something
   that isn't food (a coil of good cord) and the cost stays the roots.
3. smoke_roots: roots smoked over the rack as a keeping trick is plausible but thin; the writers may make it "dry
   roots on the rack" if it reads better. The tradeoff (roots count for Take stock against smoked) is the point.
4. Engine (to verify in the schema step): can a lane card train a skill? If not, Cooking trains from a hands card (turning the
   meat) and smoke_catch stays untrained.
5. Woodcutting 3 is probably reached inside the opening, so for most saves "the builds" is already true at rebase;
   the line l_wc_3 then never fires, which is fine.
6. Scavenging 5's timing (above, Levels).
7. Every spine beat that takes stores (B3, B7, B18, B22) lands with nobody watching on many routes. decisions.md's
   "nothing is lost while you're away" is read as "nothing is lost because you were away" (D-59). If that reading
   needs the owner, ask spoiler-free: "can a story moment take a little of what you'd stored, if it's the same whether you
   were watching or not?"
