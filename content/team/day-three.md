# Day three: from the ridge to the warm ground

Spoilers: this file is under `content/` and never shown to the owner. It picks up where `day-two.md` ends (B4, on story day 3)
and runs through story day 3's evening, the third night and story day 4 to B5, on the fourth night. It also places day
two's sinks (below) and gives the arc from B5 through B7, the end of week 1. Its data twin is `beats.yaml`'s
`day_three:` list; its canon is C-promise-19 and C-beat-87 to C-beat-93 in `canon.jsonl` (tentative until the lead
confirms); its decisions are D-93 to D-102. **Every number below is a target**: the simulator's routes set them
(`day-three-numbers.md`), and the line state lists are generated from those routes. Engineering's side is
`docs/design/day-three-plan.md` (spoiler-free); the sinks' shapes are `docs/design/banked-time-plan.md`'s, answered in
`banked-time-open.md` (BT1-BT6) and `combat-open.md` (C1-C9).

Binding, carried: day and night run on the story's clock; a planned moment that lands while the player is away plays
in full on return; nothing is lost *because* the player was away (D-59).

**Pace (D-93).** The game stays about three months and must never feel stretched. From B5 on, every spine beat
lands at `beats.yaml`'s target_day on the typical route (`pace_scale` 1, the one named number the simulator reads),
sharp no sooner than 0.83×. A normal pace reaches B4 a day or more early, so the gap to B5 is two to three real days,
and it is filled with real content, never waiting or padding: day three's own chain (K1-K5) plus a **side layer** of
minor beats (below), each with its own decision or spend. A real day two left the player waiting to come back in a few
hours with no use for the resources, just watching XP bars go up. So day three is built on three rules
(D-94): its first sinks are on screen the moment B4 lands; every return has a use for what piled up; every visit has a
decision that trades one goal against another.

## The shape

Nine visits on the typical route, as day two counts them. V1 is the rest of the session B4 lands in (or the return that
reveals it).

The day is one chain the player builds: **you walk the edge of the light, and find the one way out; the way out finds
warm water and clay; the clay makes a hearth; the hearth's smell brings someone; with three at a hearth on the stone,
the night shows what the stone is.** Every link is a step the player takes or a build they queue.

- **The near question** (C-promise-19, *why is the camp not like the rest of the Hollow?*): opened by K1 (on the walk
  round the edge, the ash lies thinner on the camp's stone than anywhere the player walked), advanced by K2 (the warm
  stream, where ash does not lie on the water) and K3 (the night, when frost greys everything past the firelight but the
  stone), paid by B5 (the ground under the camp is warm; at night the cracks glow).
- **The deep pull** gets no touch of its own: B5 opens C-promise-4 at the chapter's end. The wolves are kept at sound
  and sign only (K3, and the arc's L2); the first sight of them is B7's.
- **What day three teaches:** the trip held against a full store (V1), the comforts (V1-V2: staged builds that take
  full stores), the second offer kind and its answer order (V5), and the town's mix with people as shares (V6, at the
  second arrival; day-two Open 3). One new system per visit at most, spaced.
- **Story clock.** B4 lands on story day 3. A22 starts the evening's clock: night 3 a quarter of a game hour after it,
  about one game hour long, morning 4 at A22 + 1.25 h (day two's clock again, D-84). Story day 4 lasts until the clay
  hearth's fourth stage completes; night 4 follows a quarter of an hour later, and A20 is tapped in it. Still the Still.

## The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| V1 | 0 | walking the edge: the camp in plain view from the ridge, one way out over the old fields, and the ash thin on the stone | why is the stone different? | K1 (opens), K2 (first run) |
| V2 | 2-9 h | in the night, howls answering across the Hollow, nearer than the first night's; by morning, frost on everything but the stone | what keeps the frost off it? | K3; side: SL1 |
| V3-V4 | 3-9 h each | the larder floor laid; the track reaches the old field, dead ground and a ploughshare rusted to a lump; the hearth's first stage, and the pot | is there food for more than two? | K4; side: SL2, SL3 |
| V5 | 3-9 h | the hearth's smell has brought someone to the firelight | will he stay, and whose hands make room? | O-stay |
| V6 | 3-9 h | he joins; three at the fire | what will he be like? | K5; side: SL4 |
| V7-V8 | 3-9 h each | his first days; he and Lucy each bank the fire their own way; the hearth's last stages go on the stone | what will the hearth be like at night? | side: SL5, SL6 |
| V9 | 0-9 h | night 4: the cracks in the stone round the hearth glow faintly red | (the deep question opens) | B5 (pays) |

## Timeline

Game hours are after B4 lands, on the typical route; the simulator sets them. **Bold** marks the bigger new things.

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| V1 (4-7 min) | reads B4; taps **Walk the edge** (A22, glows: the one next step); meets **the track** and adds it to the mix held against damp wood (the mix offer on the full damp wood line); its first run lands K2; **chooses** a first comfort (the larder floor or the rack roof) and pays a stage from full stores | A22 (B4); `field_track`, `larder_floor`, `rack_roof` and the mix offer (A22); K2 at the track's first completion: clay, `dig_clay`, `clay_hearth` in view unready (needs clay) | the player walking the edge, then out along the track and back; cairns begin by the gap | l_edge_1, l_edge_2 (K1), l_track_first, l_stream (K2), l_larder_1, l_roof_1 |
| V2 (3-6 min) | reads the night (K3); digs clay (by hand or a rule); queues **the hearth's first stage**; pays the next comfort stage; re-tunes the mix between the track, clay and the gatherers | night 3 (A22 + 0.25 h), K3 three minutes in; morning 4 (A22 + 1.25 h); the clay order card; `stew` at the hearth's first stage | night grade, frost past the firelight, none on the stone; then day 4 | l_night_3a, l_night_3b (K3), l_morning_4, l_clay_first, l_hearth_1, l_stew_first |
| V2 also | sees **Lucy's watch fire** begun at the gap (SL1); **chooses** whose time builds it (her lane, slowly, or the hands' two stages) | SL1 at morning 4 (rides `t_morning_4`'s outcome) | a ring of stones at the gap facing the track | l_watch_1, l_watch_2 |
| V3-V4 (3-5 min each) | pays the larder floor's last stage (SL2: the stores off the wet ground, a re-tune for the bigger roots line); reads K4 when the track reaches the field; makes the **first stew**; sets Lucy's share at the lit watch fire (SL3) | SL2 at `larder_floor`'s third stage; K4 at the track's run n₂; `stew` at the hearth's first stage; SL3 at `watch_fire`'s completion | stone floor in the larder; the track's far end; the pot on the hearth | l_larder_done (SL2), l_field_1, l_field_2 (K4), l_stew_first, l_watch_lit (SL3), l_camp_9 |
| V5 (3-6 min) | answers **the second offer** (O-stay); builds the bay or lets him | O-stay with the first stew | a stranger at the fire's edge | l_stay_1, l_stay_2, l_bay_go, l_bay_his |
| V6 (3-6 min) | meets **the town's mix** (its lesson: shares for two people); sets his share; reads SL4 | K5 when the bay completes (arrivals 2); the town's mix; the answer order in Rules (the second offer kind); SL4 an hour after K5 | three at the fire; his bay against the lean-to | l_join_1, l_join_2 (K5), l_his_first, l_scrap_ask (SL4) |
| V7-V8 (3-5 min each) | pays the rack roof (SL5's scene if not yet); **chooses** how the town banks the fire (SL6); queues the hearth's last stages | SL5 at `rack_roof`'s second stage; SL6 (`o_bank`, a small offer) at the hearth's third stage | the roofed rack; two ways of banking a fire | l_roof_done (SL5), l_bank_1, l_bank_hers, l_bank_his (SL6) |
| V9, or V8 for a player who waits (B5) | taps **Bank the hearth** (A20) in night 4; reads B5 | the hearth complete (fourth stage); night 4 (+0.25 h); A20 (requires night 4 begun); B5 at A20; Camp 10 lifted by B5 | night grade; the cracks round the hearth faintly red (feature:warm_ground) | l_hearth_done, l_night_4, l_b5_1 to l_b5_3, l_camp_10 |

**Per visit** (`day-three-numbers.md` has the counts): day one's bar, plus two from the owner's play: **something to spend**
(a card the player can afford that takes a store at or near its cap) and **something to decide** (a choice where
moving the mix or the queue changes which of two goals comes first) on every return. The pairs that make the crunch
share stores on purpose: the larder floor and the hearth both want stones; the rack roof and the track both want damp
wood; the bay (Make room) and the hearth both want the hands' time.

**Per absence:** at most two unlocks. V1→V2: night 3 and morning 4 (no separate dusk feature: the grade follows the
night's clock, so day two's third unlock does not recur). Later absences: at most a comfort's or a course's finish and
one of O-stay, K4 or K5. A return that reveals B4 brings B4 with A22 (one moment).

**Landing:** B5 inside its band (`day-three-numbers.md`): on typical 72-96 h from the save's start (about 48-72 h after
B4), on sharp no sooner than 70 h. The chain that holds the floor is work the player queued, not waiting on the
player: four courses of the clay hearth, each laid in half an hour by the hands and then left to dry about eleven hours
on a lane of its own (the rack's idiom, so the mix runs on meanwhile), with the bay built beside the drying. The cure's
bar is the lever the simulator turns; the hands stay free for the track and the comforts.

## Day two's sinks

The owner replays from a new save, so day two may gain sinks, additively (new ids only), where its stores first cap (D-95).
Day two's gathered stores cap from B3 on. D-95 opened the sink with J3 (morning 3) on the premise that V1 was day
two's fullest visit; measured, V1 held one tap, so D-105 opens it at A15, in V1:

| Card | Opened by | Cap | Bar (s) | Takes (per stage) | Pays |
|---|---|---|---|---|---|
| `raised_bed` | `t_bed_open`, at A15's finish with the player there (D-105; was morning 3, D-95) | 3 stages | 1200 | 12 damp wood, 6 stones | at the third stage, "Rest +30%" (rest's energy ×1.3); each stage a scene state (a frame of poles, a stone footing, a bed off the wet ground) |

A bed off the wet ground is honest to the Still (fog in low ground; the wood is damp through). It is a third thing
beside J4's two builds and never part of their choice: it opens before them, takes the same stores, and leaves the
offer waiting on the shelter, so day two's chain is untouched; the policies build it after both builds (the simulator
checks B4's band does not move). One comfort, not two: day two's job is the first person and the first offer, and
day three starts with a sink on screen at B4. Lines: l_bed_1, l_bed_2, l_bed_3 (one per stage), written with day
three's brief.

## Cards, stores, lanes, standing actions

All targets. Same schema as `day_two.toml`; everything additive except where `docs/design/day-three-plan.md` names a
schema change.

### The track (fit pass)

**What it is:** work out past the camp that takes stores and comes back with finds. **Instance of:** an expedition's
first slice (`docs/systems.md`, Expeditions: data on Cards). **Fits into:** Cards (an uncapped card with inputs on the
hands lane, run in the mix held against its supply store), Triggers (finds on its completion count). Fight-free (BT5).

- **`field_track`:** takes 18 damp wood, 4 stones, 14 roots a run; bar 30 s; makes nothing a run; trains Scavenging
  at scavenge's rate. Held against damp wood by default (the mix offer), so it drinks what the hands make past that.
  The three stores it takes are the three that overflow, in about the ratio the camp makes them ("Sinks after
  measuring").
- **Finds:** **1 run** (a trigger on `card_count`), K2: the warm stream; clay +6, opens `dig_clay` and the clay
  line. **K4 is a step of its own**, `track_end` (narrative, cap 1, glows), shown with the track at K1 and ready at
  Scavenging 16, the level the track trains toward (`decisions.md`, "No gate counts taps": a run count may pay, never
  open): the dead field; scrap +4, and the scrap line shows. The arc's L2 (wolf sign) takes the same shape when its
  chapter is written; its level is the one typical reaches about 24-30 h after B4 (simulator).
- **After the finds** it keeps paying Scavenging XP. Scrap (cap 12) comes only from finds on its run count and level
  finds, never a lump a run (BT2 as revised).

### The comforts

Capped crafts on the hands lane, built a stage at a time, queued with When ready across absences; each stage takes up
to a full store, so a return with full stores always has one to pay for. Each names only its upside ("No blind
permanent choices"); two of them are B7's pest cures (C4), learned then.

| Card | Opened by | Stages | Bar (s) per stage | Takes per stage | Pays (UI register, at the last stage) |
|---|---|---|---|---|---|
| `larder_floor` | A22 | 3 | 2400 | 18 stones, 6 damp wood | "Roots hold 54, was 36" (roots cap ×1.5) |
| `rack_roof` | A22 | 2 | 2400 | 18 damp wood, 6 dry wood | "Rack +25%" (LaneSpeed rack ×1.25) |
| `clay_hearth` | K2 (unready until clay) | 4 | 1800, and each course requires the last one cured (`cure_hearth` count ≥ courses laid) | 6 clay, 12 stones, 2 dry wood | stage 1 opens `stew`; stage 3 shows SL6; stage 4: "Stew 3 a pot, was 2", and starts the evening's clock (night 4) |
| `cure_hearth` | each course laid (a rule on lane `hearth`, installed by the first course) | none | 30 000 (about 8.3 h), cap 4 | | the dry token for the next course; lane `hearth`, the rack's shape: nothing taken, nothing paused |
| `watch_fire` | SL1 | 2 | 3600 | 12 stones, 6 dry wood | opens `n1_watch` on her lane (below); scene: a second, small fire at the gap |

### Clay and stew

| Card | Lane | Cap | Bar (s) | Takes | Makes | Skill | Opened by |
|---|---|---|---|---|---|---|---|
| `dig_clay` | hands | none | 10 | | clay 1 | Foraging (forage's rate) | K2 |
| `stew` | hands | none | 20 | 4 roots, 1 smoked | stew 2 (3 after the hearth) | Cooking | `clay_hearth` stage 1 |
| `make_bay` (A23) | hands | 1 | 21 600 | 12 damp wood, 12 stones | arrivals +1 on completion | | O-stay, Make room |
| `n1_build_watch` | n1 | 2 | 4× the hands' bar | 12 stones, 6 dry wood | the same stages as `watch_fire`; one card's stage count is the other's (shared done store `watch_done`) | | SL1 |
| `n1_watch` | n1 (a share in the town's mix after K5) | none | 600 | 1 dry wood | nothing yet (from B7, an entry on the camp's side, combat's content) | | `watch_fire` done |
| `n2_build_bay` (A24) | n2 | 1 | set for equal real time at his base pace | 12 damp wood, 12 stones | arrivals +1 on completion | | O-stay, the other answer |
| `bank_hearth` (A20) | hands | 1 | 5 | requires night_4 ≥ 1 | B5 | | the hearth's fourth stage |

`dig_clay` is why Foraging trains again (day two's numbers: no foraging XP on any route, because Lucy forages), so
B5's level gate can stay on Foraging. Stew brings Cooking back, and the town's food reads it from K5 on.

### Stores

| Store | Cap | Notes |
|---|---|---|
| clay | 12 | from `dig_clay` and K2 |
| scrap | 12 | from the track's finds (K4 shows it); the spear takes it at B7 (C6) |
| stew | 12 | O-stay's gate reads it; `n2_eating` takes it |
| roots | 36, 54 with the larder floor | existing |
| arrivals | 10 (tally, never drawn) | B3's outcome sets 1 (rebased saves too); the bay's completion adds 1; B7's gate reads it |
| night_3, night_4 | 20 each | never unlocked; the nights' clocks, as day two's `night_2` |
| watch_done | 2 (never drawn) | the watch fire's stages from either lane |

### Standing actions

| Id | Unlocked by | Per hour |
|---|---|---|
| night_3 | `t_dusk_3` (A22 + 0.25 h) | night_3 +20 |
| night_4 | `t_dusk_4` (the hearth's fourth stage + 0.25 h) | night_4 +20 |
| n2_eating | K5 | stew −1, smoked −1, roots −1 |

### The second arrival (fit pass)

**What it is:** someone drawn by food to spare who stays and works. **Instance of:** the arrival idiom (BT4), an offer
whose answers start a one-off that ends in the person joining. **Fits into:** Offers (O-stay, the second kind, so the
answer order shows in Rules, day-two Open 4), Cards (the bay on either lane), Triggers (the join), Mixes (the town's mix
with people as shares, day-two Open 3: two people is the first real split).

| Offer | Shown | Answers | Each answer | Expires |
|---|---|---|---|---|
| O-stay | the first stew (`t_stay_offer`) | **Make room** / **Let him build** (labels to the voice pass) | Make room: `make_bay` on the hands, 6 h. Let him build: his lane starts at once, `n2_build_bay` on it for the same real time. Same stores either way | never; he waits at the fire's edge until answered |

He is light tier: a soul from the save's seed (layer 1, pooled traits), with an authored stand-in when Claude is off.
The stand-in, for the writers: a deserter from nobody's army, alone, carrying a spear's shaft with no head on it. He
came for the smell of the stew. Named by the save's seed from `names.jsonl`'s pool ("Names come from outside the
model"); lines say "he" until K5 gives the name. Groups arrive broken: whoever walked with him did not arrive, and no
line says who or how (`decisions.md`, "Groups arrive broken").

### The town's mix, at K5

The join replaces Lucy's lane with the town's mix: one mix whose shares are people's time, with each townsperson's
cards (`n1_*`, and his `n2_forage`, `n2_gather`, `n2_cut`, `n2_scavenge` at base rate, no XP, camp items at the hands'
rate). Default on joining: Lucy keeps her current task at her whole share, he forages at his. Her installed rules
become the town's standing orders. Its lesson runs on its own controls when it first shows (`decisions.md`,
"Lessons"). The engine shape is the plan's (item 3).

### Order cards and mix offers

- **On the full damp wood line, from A22:** the mix offer "add the track, held at 12". The first trip is taught by the
  need on screen: a full store with nowhere to go.
- **Under the clay line, from K2:** "Under 6 clay → dig clay, until 12" (a rule on the hands).
- **After K5:** none new; the town's mix lesson is the teaching.

### Levels and finds

Day three's routes reach Foraging 5-10 (clay), Scavenging 15-17 (the track), Woodcutting 17-19 and Cooking 3-6. Each
range keeps "at least every third level pays a thing"; added finds are new triggers (additive under the lock):

| Skill | Level | Pays |
|---|---|---|
| Foraging | 6 *added* | a clay seam in the stream bank, firmer than the first (clay +4) |
| | 8 *added* | lichen in the cairns' lee (roots +6) |
| Scavenging | 17 *added* | a buckle and a length of chain by the track (scrap +2) |
| Cooking | 4 *added* | the knack of a thicker pot (stew +2) |
| | 6 *added* | (none yet: the next finds are the B5-B6 chapter's; listed so the check sees the gap) |

Finds never name or hint at warmth under the ground, wolves seen, or anything of B5's or B7's.

### The Camp

| Level | At (camp items) | Pays |
|---|---|---|
| 9 | 250 000 | "Drying wall 11, was 9" (lay_to_dry batch 9 → 11) |
| 10 | 400 000, held ("?"); cap 399 999 until lifted | lifted by B5: "Smoked holds 27, was 18"; the marker is a goal on screen through day three |

## Sinks after measuring

Typical, seed 0, after day three's content was integrated: the cap-loss check failed on damp wood, roots and scrap
(88, 71 and 100% lost away 24 h), and V10, V14 and V15 had nothing to decide. What each store's overflow goes to now,
using only shapes the chapter already has (numbers and measurements: `day-three-numbers.md`, "Sinks after measuring"):

- **damp wood, roots, stones: the track, reshaped.** The track was too small for what it drinks: at its old takes a
  share of the mix on it drew a tenth of what the same share makes gathering, and stones bound it before damp wood
  did. Its takes now follow the ratio the camp makes the three stores in (a full store of damp wood, a little stone,
  a lot of food carried), at the 30 s floor, so at the route's half share it drinks most of what the hands and Lucy
  make and no one take starves the others. No cap moved, and no bar went under the floor.
- **His time: foraging, not cutting.** Every task a townsperson has gathers into a full store, and cutting poured his
  whole share into the one line the track can't keep up with. He came for the pot and the aim is a fire that feeds
  three, so he joins foraging; the track carries the food out. Choosing his share stays the town's mix lesson.
- **Scrap: finds only.** One scrap a run filled its 12 in a few minutes on every route, so it was never banked by the
  hold, only lost past it. Scrap now comes from the track's finds on its run count (K4) and level finds, so every run
  away moves the next find closer and none is wasted. The scrap line shows at K4, its first find. The spear's 6 at B7
  is K4's 4 plus the Scavenging 16 find's 2; the B5-B7 chapters' own finds take it toward 12.
- **Smoked: a second mouth.** He eats what she eats and the pot (`n2_eating` gains smoked), so the snares' smoked line,
  made a little faster than she eats it, has a drain once there are three.

**Something to decide late in the day.** Two comforts, each a choice of what the hands build next from full stores,
placed in the visits that had none. Both are in view from a moment the player is present (A22, K2) and unready until
the build they stand on is part laid, so neither appears while away (the 2 AM rule):

| Card | In view | Ready | Stages | Bar (s) | Takes per stage | Pays (at the last stage) |
|---|---|---|---|---|---|---|
| `wood_stack` | A22 | the larder floor's second stage (`stack_ready` +3) | 3 | 2400 | 18 damp wood, 6 stones | "Dry wood holds 54, was 36" (dry wood cap ×1.5) |
| `pot_shelf` | K2 | the hearth's second course (`shelf_ready` +3) | 3 | 2400 | 12 stones, 6 damp wood | "Stew holds 18, was 12" (stew cap ×1.5) |

The stack competes with the watch fire's and the rack roof's stages for the hands and the damp wood; the shelf runs
beside the last two cures, the one stretch where the chain gives the hands nothing. Each pay is a cap, so neither makes
anything a store must then drink. Lines: l_stack_1..3, l_shelf_1..3 and each card's failed line, for the brief.

**The gate is a token, not a requires** (the hearth's own idiom): a card's blocker shows only its first unmet need, so a
requires behind a short input shows a ready time that isn't one, and a When ready queue headed by it stalls. The
hearth's courses had the same stall (their token was listed last); the token now comes first. With the stall gone the
chain runs faster, so `cure_hearth`'s bar went back up to hold sharp's floor (the lever "Sizing the chain" names).

## The beats

Fields as in `beats.yaml`. Facts each writer may use are the canon ids named; nothing else.

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread | Canon |
|---|---|---|---|---|---|
| B4 | V1 | A19 (day two's) | as day two | as `beats.yaml` | C-beat-4 |
| K1 | V1 | A22, walking the edge | The player walks the edge of the firelight. The camp sits in plain view of the ridge; scrub and thorn on three sides; one way out that is not through scrub, a track over the old fields, half sunk. Coming back, the ash lies thinner on the camp's stone than anywhere on the walk. | down · none · grim · none · PC · opens C-promise-19 · th-burn start | C-beat-87 |
| K2 | V1 | `field_track` run 1 | Out along the track, a stream that steams a little in the cold; the ash does not lie on the water. Its bank is soft grey clay, warm in the hand. | up · none · wonder · none · PC · advances C-promise-19 · th-burn middle | C-beat-88 |
| K3 | V2, on return | three minutes into night 3 | Howls answering each other across the Hollow, two voices, nearer than the first night's. Lucy banks the fire higher and says nothing. Nothing comes. By morning frost greys everything past the firelight, and none on the stone. | down · none · dread · none · PC, N1 · advances C-promise-19 · th-survive middle | C-beat-89 |
| K4 | V3 | `track_end`, at Scavenging 16 | The track reaches the old field: furrows under the ash, nothing growing, nothing that will. In the last furrow a ploughshare rusted to a lump. It comes back as scrap. | down · no · wry · time · PC · none · th-survive middle | C-beat-90 |
| O-stay | V2 or V3 | the first stew | A man at the edge of the firelight, drawn by the stew's smell, alone, a spear's shaft with no head. He asks to stay. Either answer gives him a place; the answer is whose hands build it. | (an offer, not a beat) · th-town start | C-beat-91 |
| K5 | V6 | the bay done (arrivals 2), either answer | He takes his place at the fire; Lucy looks him over once and goes back to work. He gives his name. Three at the fire; the stores are for three now. | up · yes_but · warm · stores · PC, N1 · none · th-town middle | C-beat-92 |
| B5 | V9 | A20 + foraging N + B4 | Night 4, the hearth on the stone banked for the first time. The ground under the camp is warm; the ash melts there first; the cracks round the hearth glow faintly red. | as `beats.yaml` (up · yes · wonder · none · PC · opens C-promise-4, advances C-promise-6), and pays C-promise-19 | C-beat-5, C-beat-93 |

**The flat check, authored order:** turns B4 down, K1 down, K2 up, K3 down, K4 down, K5 up, B5 up (never three the
same); outcomes K4 no, K5 yes_but, B5 yes; registers grim, grim, wonder, dread, wry, warm, wonder (never four the
same); costs time, none, none, none, time, stores, none; the near promise opened V1, advanced V1 and V2, paid V9. Day
three's net is −1, and the arc's (below) −1, so week 1's `week_net_up` (+2 with day two) settles at 0 (D-96).

**Mechanically, B5:** A20's completion plays B5's lines, sets the feature that draws the glowing cracks (night layers
only), lifts Camp 10, moves the aim on, and carries the chapter's end card. Nothing else changes.

## Away from the screen

- **Every planned moment plays in full on return:** K3 and morning 4 nearly always land while away; O-stay often; the
  hearth's stages and the bay nearly always; K4 whenever the track's count falls in an absence. Each is revealed in
  order, one at a time.
- **The trip runs while away** at exactly the share its hold allows; the unwrap shows the runs made and what came back,
  never what overflowed.
- **The 2 AM test:** every sink is on screen unready before it can be afforded (A22 opens the comforts and the track
  together; the hearth shows at K2 before any clay; O-stay's builds start from the answer), so the babysitter has no
  instant to exploit. Both answers to O-stay cost the same stores and time. The track's finds count runs, never the
  clock.
- **Rebased saves:** a save already past B4 when day three ships gets A22 on its cards at the rebase instant, with its
  full stores: the first sink is one tap away (D-94).

## Line moments, and the states each can fire in

Expected states; the shipped lists are generated by the simulator once `day_three.toml` exists, and replace these.

| Id | Fires when | Expected states |
|---|---|---|
| l_edge_1, l_edge_2 (K1) | A22 | V1 or the return that revealed B4; day 3; after either B4 answer, so no line says who walked to the ridge |
| l_track_first, l_stream (K2) | the track's first run | within minutes of A22, present on most routes |
| l_larder_1..3, l_roof_1..2 | each comfort stage | present or by the queue; in either order; any day |
| l_night_3a, l_night_3b (K3) | night_3's first item | at night; on return on most routes; the track has run at least once |
| l_morning_4 | `t_morning_4` | on return; frost past the firelight |
| l_clay_first, l_hearth_1..3, l_stew_first | each first | day 4 mostly; the hearth's stages often by the queue while away |
| l_stay_1, l_stay_2 | O-stay shown | stew just reached 6; present or on return; any comfort built or not |
| l_bay_go, l_bay_his | each answer's build starts | the player's hands / his |
| l_bay_help (`t_bay_begun`) | the hands' bay starts work (Make room only) | often by the queue while away; he has not joined yet |
| l_field_1, l_field_2 (K4) | `track_end` done | any visit from V2; before or after O-stay; before or after K5 |
| l_join_1, l_join_2 (K5), l_his_first | the bay done | either answer; his name given in l_join_2 |
| l_hearth_done | the hearth's fourth stage | by the queue, often while away |
| l_night_4 | night_4's first item | before A20; three at the fire |
| l_b5_1 to l_b5_3 (B5) | A20 | night 4; present (A20 is a tap) |
| l_camp_9, l_camp_10 | each level | Camp 10 with B5 |
| l_bed_1..3 (day two) | each stage | day 3, before or after the builds, before or after B4 |
| l_watch_1, l_watch_2 (SL1), l_watch_lit (SL3) | morning 4; the watch fire built | on return mostly; built by either lane |
| l_larder_done (SL2), l_roof_done (SL5) | each comfort's last stage | by the queue, often while away; in either order |
| l_scrap_ask (SL4) | K5 + 1 game h | his first day; any scrap count, so no number |
| l_bank_1, l_bank_hers, l_bank_his (SL6) | the hearth's third stage; each answer | late day 4; three at the fire |
| find lines | each added find | by the mix, any visit |

**Must-nots for the brief:** never say the ground or stone is warm before B5 (K1 is thin ash, K3 is frost that isn't
there: facts, never causes); never show a wolf (K3 is voices, and B7 is the first sight); never count who he lost or
say how; Lucy's lines are what she does, never what she feels about him; no line judges either answer to O-stay; no
Chequer, keels, holders, magic or faith.

### Stated aims

| Aim | Starts at | Intent |
|---|---|---|
| aim_after (day two's) | feature cart_news (B4) | unchanged; ends at K1 |
| aim_field | feature track_open (A22) | see what the old fields still have |
| aim_stay | O-stay shown | make room for one more |
| aim_three | feature n2_joined (K5) | a fire that feeds three |
| aim_warm | feature warm_ground (B5) | the arc's first aim (below) |

## Art

- **Grades:** night grade for night 3 and night 4 (`until="feature:morning_4"` / the arc's morning 5); frost overlay
  past the firelight on night 3 (cool, world layer); day 4 normal grade.
- **World layers (cool):** the track out through the gap, half sunk (feature:track_open); the far field at the track's
  end (feature:dead_field, K4); frost (night 3); the cracks' faint red glow round the hearth (feature:warm_ground, night
  layers only; B5).
- **Player-made (warm):** cairns along the track (grow with runs, three states); the larder's stone floor (3 states);
  the rack's roof (2 states); the clay hearth on the stone (3 states); the bay against the lean-to; the raised bed
  (day two, 3 states).
- **Figures:** the player walking the edge (A22), away down the track while it runs on a tap and for its share while
  mixed (banked-time plan item 6), digging at the stream (running:dig_clay, off-scene: a pose at the gap); the newcomer
  (pack figure: a man with a staff, picked by `sprite-catalog`) at the firelight's edge, then building, cutting, at the
  fire; Lucy as day two.
- **Stages:** 25_edge, 26_track, 27_night_three, 28_hearth, 29_stranger, 30_three, 31_warm_ground.

## Side layer

Minor beats that hang off the spine between its beats, so the gaps the schedule leaves are content, never waiting
(D-97). The spine is untouched: a side beat never gates a spine or chapter beat, never opens, advances or pays a spine
promise, and carries no turn field (the flat check reads the spine and the chapters only). What it must carry is **its
own decision or spend**: a choice, a stage to pay for, a share to set, a store to use.

**Kinds** (each is data on an existing system; none is a new mechanism):

| Kind | What it is | Built from | Its decision or spend |
|---|---|---|---|
| find | a level's or a trip's discovery, a line and a small store | Triggers on a level or a completion count | the store it brings is spent on the next stage |
| trip | a trip's named discovery past its finds (a place, a sign) | Triggers on a completion count | re-tune the hold, or a card it opens |
| arc | a townsperson's small arc: three moments over a few days, each ending in something to set or answer | Triggers on time-since-joining or a store, a small offer, a card on their lane | whose time, which way, a share |
| comfort | a staged build's last stage changing the camp, a scene state and a line | Cards (the comfort's stage count) | the re-tune its pay invites, or the next comfort |
| thread | a short side thread (two to four moments) tied to a spine thread by its `thread` id | Triggers, Offers | an answer or a spend per moment |

**Rate.** The spine has 4-5 beats a week after week 1; the side layer roughly doubles events per week, about one a
real day in week 1's long gaps and 4-6 a week after. Inside a chapter: at least one side beat in every stretch between
chapter beats longer than one typical visit gap, and no visit that brings only a bar to watch
(`day-three-numbers.md`, per-visit density).

**Ties.** Each side beat names the spine thread it hangs off (`thread`: th-survive, th-burn, th-town, ...) and may
touch a chapter's near question, never a spine promise. An arc belongs to one person; a light-tier person gets at most
one arc at a time, and notables' arcs stay the spine's. Data: `beats.yaml`'s `side_layer:` list (id, kind, chapter,
thread, gate, `spend` or `decision`), counted by the simulator toward new things per visit and per week.

**Day three's six:**

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL1 | arc (Lucy, 1 of 3) | th-survive | morning 4 (`t_morning_4`) | Lucy has begun a ring of stones at the gap, facing the track: a fire of her own to sit at, between the camp and the dark. | whose time builds it: her lane (`n1_build_watch`, slow) or the hands' two stages (`watch_fire`); either takes the same stores |
| SL2 | comfort | th-survive | `larder_floor` stage 3 | The roots go in rows on a stone floor, off the wet ground. Lucy rearranges them. | the larger roots line invites a re-tune; the next comfort |
| SL3 | arc (Lucy, 2 of 3) | th-survive | the watch fire built | She sits at the watch fire through the day with her back to the camp, feeding it a stick at a time. | her share at the fire (`n1_watch`, takes dry wood) against her gathering |
| SL4 | arc (him, 1 of 3) | th-town | K5 + 1 game h | He turns the scrap pile over with his foot and holds up the shaft he carries, and puts it down again. | none asked aloud; the scrap is still the track's to bank (the spend is the hold) |
| SL5 | comfort | th-survive | `rack_roof` stage 2 | Rain-dark ash runs off the new roof; the hang underneath stays pale. | the faster rack invites a re-tune of the drying wall |
| SL6 | arc (Lucy 3 of 3, him 2 of 3) | th-town | `clay_hearth` stage 3 | They bank the fire differently: she buries it in ash, he rings it with stones. Each thinks the other's way wastes wood. | `o_bank`, a small offer with two answers, whose way the camp keeps: hers ("Fire −10% dry wood") or his ("Rest +10%"); either is fine, neither is judged |

His arc's third moment and the B5-B7 chapters' side beats are theirs to write, from the kinds above.

## B5 to B7: the arc to the end of week 1

Three chapter files after `day_three.toml`: `day_four.toml` (B5 → B6), `day_five.toml` (B6 → B7's eve, with arrival 3),
`b7.toml` (B7 and combat, C1). Each spans about one real day on typical (B6 on day 5, B7 on day 6), filled with its
chapter beats and two to three side beats (bands and density in `day-three-numbers.md`). Each later chapter is written
by its own design pass from this page; what is fixed here is what day three sets up.

**Day four (B5 → B6): will the fire last?** The Still at its stillest: on morning 5 a fog comes down that the rack
can't dry through (a chip on the rack lane, "Rack −50%", whose cure is the rack roof, already in reach: day three's
comfort pays off). Beats: **L1** (the fog; down · dread · stores), **L2** (the track's third find, wolf sign: a kill
by the track, prints of several, a ring round the camp at the scrub's edge, never nearer; down · dread · none), **L3**
(the newcomer and Lucy at the fire: a small exchange that makes him a person, not a mouth; up · warm), then night 5,
**A21** ("Sit up with the fire", the fire low on fog-wet wood), and **B6** (spine; Arcana opens). Sinks: a woodshed
(staged; dry wood cap), the track still held, the town's mix re-tasked against the fog (its second use, taught by
need). B6's level: Scavenging, the value the held track reaches (day-two numbers proposed 16).

**Day five (B6 → B7's eve): what does the stone do, and who else is coming?** Arcana's first card takes materials
(`hand_on_stone`: kindling in, Arcana XP; BT6), with a level pay that warms the rack (Arcana feeding drying: a skill
that feeds another, visibly). Arrival 3 by the O-stay idiom: a broken pair, which takes arrivals to 4 (the gate reads
≥ 3); the third offer of the kind is where the answer order in Rules first saves a trip back. Beats: **M1** (the pair
arrives; up · yes_but · warm · stores), **M2** (by day, the pack on the ridge where the cart stood, watching; down ·
dread). Night 6: **A29** ("Bank the fire") → B7. Comforts: one more (a screen of stakes at the gap, honest to wolves
known to be near; it pays camp-side strength from B7 on, learned then).

**B7 (`b7.toml`, a later agent's):** as `combat-open.md`'s answers: the fight a story card with no odds; the pack
strips the rack's hang (the drain, the clock); the combat feature with `hunt_wolf`, `make_spear` (affordable from
the track's banked scrap), Melee; ashrats and crows as standing fights whose cures (larder floor, rack roof) most
routes already built; `hurt` and `poultice` (clay); the ramp's clock from B7. B7 is the week's last beat; week 2
opens on the Drift's clock (B8).

The arc's turns: L1 down, L2 down, L3 up, M1 up, M2 down: net −1, which with day three's −1 brings week 1 to 0.

## Where canon shaped the design

- **The track, not a new place.** R1 has old fields under ash, a warm stream and seam-warm clay (`regions.md`); a trip
  there needs no map and spoils nothing past the next hill.
- **Thin ash, then frost, then the glow.** C-mystery-2 lists "the too-regular warm stone" as a clue; the near question
  shows its effects three ways before B5 names the cause, so B5 lands as an answer the player half had.
- **The hearth on the stone.** B5 needs a reason to be at the stone at night with the ash swept off: laying a clay
  hearth there is a build the player chose, and the glow shows round it.
- **The spear's shaft.** He carries a shaft with no head; the ploughshare comes back as scrap; B7's spear takes scrap.
  Laid side by side, never said.
- **He stays either way.** Declining costs nothing (`decisions.md`, "Tone"), and B7's gate counts arrivals, so O-stay's
  answers are about whose hands, never whether.
- **No wolf seen before B7.** K3 is voices; L2 is sign; M2 is the pack watching from the ridge by day, which is sight
  at a distance and not the edge of the firelight (C-beat-7).

## For the owner

One question, spoiler-free:

1. **Small moments for ordinary townsfolk.** The gaps between story moments are filled partly with small arcs for
   ordinary people in camp (three short moments each, with a choice or two). Ordinary townsfolk can die later; the main
   characters never do. Is it fine for someone who has had a few small moments of their own to be at risk later, or
   should anyone given moments of their own be kept safe? (Today's rule keeps only the main characters safe.)

## Open (content side)

1. **K4's Scavenging level, L2's and B5's Foraging level** are the simulator's (`day-three-numbers.md`). If sharp
   reaches K4's level inside V1, K4 crowds V1: raise the level, never slow the track.
2. **The 50% cap-loss target** at day three's end (banked-time plan item 2). The track's draw per run is small against
   the hands' making (`day-three-numbers.md`, "Sizing the track"); if the check fails, shorten the track's bar before
   adding a sink.
3. **The lazy route** reaches B4 at about 125 h, past B7's band; day one and day two are not retuned for it. Reported,
   not banded, until they are.
4. **Lucy and the town's mix.** Her lane becomes a share at K5; if the lesson reads as her being taken from the
   player's control, keep her lane and give the mix only his share until the third arrival (the plan's item 3 can do
   either).
