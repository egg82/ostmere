# Week two: from the season's turn to the end of story day 14

Spoilers: this file is under `content/` and never shown to the owner. It picks up where `days-four-to-seven.md` ends (G2,
night 7) and runs from B8, the turn to the Drift at save time 168 h, to the end of story day 14, the Drift's last night,
in four chapters. Numbers are targets (`week-two-numbers.md`); lines are written from `week-two-lines-brief.md`;
engineering's side is `docs/design/week-two-plan.md` (spoiler-free). New canon is listed at the end as proposals
(tentative until the lead confirms), new decisions as D-111 to D-123 (week 1's back half proposed D-103 to D-110,
which collide with ids since recorded; see "Open").

Binding, carried: nothing is lost *because* the player was away (D-59); every return has something to spend and
something to decide (D-94); a side beat never gates a spine or chapter beat (D-97); watching earns nothing extra (the
2 AM test); the 10-14 week band. Week 1's verification lessons are designed in, each where it bites (below, "The six
lessons").

## The four chapters

Week 2 runs on the calendar: B8 is a clock beat at 168 h and the Clear's turn (B13, week 3) at 336 h, so story days
8 to 14 are calendar days 8 to 14 and a chapter is named for the story day it starts on.

| Chapter (file) | Beat span | Story time | Near question (proposed canon) | Typical span |
|---|---|---|---|---|
| Day eight (`day_eight.toml`) | B8 → B9 | days 8-9 | C-promise-23, *what is circling the camp?* opened U1, advanced U3, paid B9 | 168-197 h |
| Day nine (`day_nine.toml`) | B9 → B10 ★ | days 9-11 | C-promise-24, *can the camp be closed?* opened E1, advanced E3, paid B10 | 197-250 h |
| Day eleven (`day_eleven.toml`) | B10 → B11 | days 11-12 | C-promise-25, *will the man who came with them last?* opened Z1, advanced Z3, paid B11 | 250-280 h |
| Day twelve (`day_twelve.toml`) | B11 → night 14 | days 12-14 | C-promise-26, *what is under the camp?* opened S1, advanced S2, paid B12; C-promise-27, *what does it want?* opened S3, paid S4 | 280-336 h |

**What each chapter teaches, one new system at most per visit:** week 1's last visit, the joint project (the palisade
shown as the week's long goal); day eight, the season (roof ash as a chip with a rule-run cure, the bloom as a new
Foraging method) and, on its last visit, the journal; day nine, the gap side (packs at the camp, watch shares and
builds as entries on it); day eleven, a group arrival and the guard; day twelve, the dig, the bear hunt (a Drift-only
fight) and its tallow.

**What changed from `spine.md` and `beats.yaml`, and why:**

1. **B9's gate is kept** (3 journal entries + B7). The journal opens at the first pack fight and writes its first
   three entries then (the three things fought so far), so B9 lands with it. Opening the book earlier would land B9
   on day 8; tying it to the pack puts the margin note beside the creature it describes.
2. **B10 gains a save-time floor** (209 h, the sharp floor): the palisade is play-driven and sharp can close it first.
3. **B11 gains two steps**, as B7 gained A29 (D-101): the vigil (A31, in night 12) and the guard made (Z2). On tier
   safety alone B11 fires the instant B10 does.
4. **B12 gains the dig and a floor** (`dig_cellar` stage 4, 249 h) beside canon's Scavenging 15 and B9, which every
   route met in week 1.
5. **n4 lives through week 2.** B11 is canon's first death in town and is a nameless stranger's; a death before it
   breaks canon, and a second within days blunts it. Week 1's open question (Open 4 there) is closed: not this week.
6. **Her third moment (n3) is in day eight**, on the first roof ash, and points at B13's fields. The week-1 question
   for the owner about growing food is not re-asked: canon already has fields at B13 and crops in `decisions.md`; the
   moment's lines hold whatever he answers.
7. **The Drift raises no rate.** "A season adds and raises, never lowers" and "a saved mix keeps its rates" cannot
   both hold for a raise that ends with its season, so the Drift adds cards, pools, a chip and a threat step only.
8. **No day-night cycle inside the Drift.** Brown dark days hold one grade; only nights 12 and 14 are story nights,
   each with its presence step, because a beat needs each. Five more hand-built nights would be five per-night taps,
   the busywork lesson 1 names.
9. **The Drift's chores follow `decisions.md`, "Each season brings its own chores"**. Roof ash is
   one: its own trouble, a suggested rule (the order card), a sink for n2's time and the hands'. Still to do in the
   content pass: (a) the order card ends with the Drift, so the next Drift asks for it again; nothing retires an
   installed rule today, so this needs a fit pass and an engine call before it is built (until then the order idles
   once no ash falls); (b) the second Drift chore is the wind at the hides, in day nine (`day_nine.toml`): the same
   warm wind that brings the ash keeps tearing the flaps hung against it loose (day nine's `wind` standing makes
   `wind_torn`, 1 an hour from the turn, drawing its own pool so it ends with the season's hours). It shows when it is
   due, on the season's clock (`drift_clock` 23, 191 h on every route), so it lands in day eight's empty stretch on
   typical and sharp, not with E3. Pegging them again takes 12 `wind_torn`, 3 pelts and 4 stones (to weigh the hems),
   by hand (`peg_flaps`) or on Lucy's lane (`n1_peg_flaps`) by its suggested rule, an order card offered with the chip;
   left undone, the chip `draughty` shows (rest −10%), a cost that stays small. Why this sink: the cap-loss check at day nine's end failed
   pelt at 8 h and 24 h without it (the flaps were pelts' last sink), and stones sit full most of the Drift. Stakes
   were its third input while it showed with E3; shown from 184 h with stakes, typical's B10 moved to 266 h, past its
   band, and the stakes left over once the ring closes are the town's split's to stop (the simulator's typical and
   sharp move n2 off stakes at the ring's closing). No third chore yet: no gathered store fails the cap-loss check at
   day eight's or day nine's end on typical without one. Day twelve's end gets no third: the season ends at 336 h, so a
   chore shown at night 14 would last hours, and the stores that fail there (smoked, pelt) are B14's to take
   (`week-two-numbers.md`, "Stores without a sink at night 14").

## The six lessons, designed in

1. **One order covers every stage.** The palisade and the cellar are staged hands builds run by one content order card
   each ("when stakes reach a stage's cost, build"), offered under the stakes line; the order goes inert at the cap,
   so nothing greys and nothing is re-queued. Every visit's decision comes from content (the numbers file lists one
   per visit), never from queuing a stage.
2. **Show it before it is ready, at a moment the player sees.** The palisade and the stakes cards appear at G2's visit
   (week 1's last, a tap, so the player is there) hours before the season turns; the dig appears with A31 (a
   tap); the vigil and the last night's step appear unready with their countdowns, queueable When ready. Cards that
   can only land while away (B8's fungus cards, the bear hunt) open onto a full store or a finite pool, so a watcher's
   head start buys nothing the absent player loses (the 2 AM test checks it).
3. **Cut-ins.** A31 and A32 glow and cut in on the order-run builds; `clear_roofs` is a cure and cuts in on any hands
   task but a cure; build stages stay at 30-40 minutes so a rule-run cure waits at most that long.
4. **Cap loss.** Every gathered store has a sink at each chapter's end (numbers file, "Cap loss"); the bloom is a
   finite pool drawn by labour, not a store a standing action overfills.
5. **Combat's first slice as built.** The pack is a standing fight on a new side; the bear a fight card. G7 and G8 are
   closed by content (`hurt` in quarters, below). The watch shares and the guard need one engine part: entries a
   running card adds to a side (plan item 2).
   *Superseded 2026-10-31:* G7 and G8 closed by the drain, not quarters (D-117's note).
6. **Art from the packs.** Every figure and prop below names a kit candidate; one transient pose (the vigil's body)
   gets a transient id.

## Week 1's last visit: the long goal

G2's visit is a tap (A30), so it is the one moment of week 1's end every player is present for. Day eight's file adds a
trigger on `still_end` (new id; week 1's released ids untouched) that opens, with one line from Lucy's side of the
fire:

- `palisade` (P1), unready, on the cards: the week's long goal. Its card shows its 12 stages and what each takes.
- `cut_stakes` (hands, Woodcutting) and the stakes town card on Lucy's and his lanes (`n1_stakes`, `n2_stakes`).
- `twist_cord` (hands), and the cord store; `n4_cord` on his lane (released `n4_mend` made nothing, and an earlier file
  cannot name a store this one declares), run by a rule under the cord line, so his share is the cheaper cord.
- `hide_flaps` (hands), so the pelts week 1's hunt keeps bringing have somewhere to go.

Why here: Lucy has wanted a wall since B7 took the rack; a goal shown now lets the whenever player set the town's
split before the overnight absence that carries B8, so the babysitter gains nothing at the turn. The line is a fact
(she scores a line in the ash round the bays with a stick), never a plan stated.

## Day eight (B8 → B9): what is circling the camp?

The burn exhales. Warm wind, ash by the bucket, dark at noon. The roofs bow under it. Fungus comes up overnight on every
dead thing and the larder is full for the first time. The crows on the roof's ridge are counting under their breath.
In the warm dark there are howls from more than one place, and in the morning the prints are at the bays. The first
pack comes to the gap; the book comes out; the wolf page already has writing in the margin.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 8a | after night 7 | B8; howls from several places in the warm dark, prints of many at the bays by morning | what is circling the camp? | B8; U1 (opens) |
| 8b | 3-9 h | the first pot of fungus, sorted by her hands; the roofs' first clearing | (plenty, for once) | U2; side SL15 |
| 8c | 3-9 h | the palisade's stages rising; his mending makes cord | will the wall be up before they come in? | side SL16 |
| 8d | 3-9 h | the pack at the gap; the book out; the margin note | (B9) | U3 (advances); B9 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 8a (4-6 min) | reads B8 and U1; adds the fungus to the mix (`fungus_stew` against full fungus) and moves her share to picking or not; accepts the stakes order card ("build when stakes reach 24"); pays a palisade stage | B8 at 168 h: `drift` feature, the Drift grade, `pick_fungus`, `n3_pick`, `fungus_stew`, `clear_roofs`, the bloom, fungus at its cap, the ash on the roofs; U1 at B8 + 6 h | brown dark, ash falling heavy, fungus shelves on the dead birch, crows on the ridge | l_b8_1 to l_b8_3, l_howls (U1) |
| 8b (3-5 min) | reads U2; reads SL15 and sets her share between picking and the ashed ground; accepts the roofs' order card (offered with the chip) or clears by hand | U2 at `fungus_stew`'s first finish; the chip `ash_laden` at roof ash 16 with its order card; SL15 at the first clear + B8 + 12 h | her at a cloth of sorted caps; ash shovelled off the bays | l_caps_1, l_caps_2 (U2), l_roofs_first, l_ash_ground (SL15) |
| 8c (3-5 min) | reads SL16 and moves the old man's share between the watch and mending; re-tunes stakes against the stone card | SL16 at B8 + 14 h once `n4_cord` has finished once; Camp 13 by the mix | the old man twisting bark by the fire; the palisade's first stretch | l_cord (SL16), l_stage_1.., l_camp_13 |
| 8d (3-6 min) | reads U3 and B9; opens the journal (its lesson); moves shares to the watch against stakes as the pack's losses show | U3 at `r1_clock` ≥ 70 and `drift_clock` ≥ 12: the `pack` fight, the `gap` side; the journal at the first pack fight (`pack_fought` ≥ 1), three entries; B9 with them | wolves at the gap in the warm dark, the fire between | l_pack_1, l_pack_2 (U3), l_b9_1, l_b9_2 (B9) |

### The season (fit pass)

**What it is:** a week of changed weather on the calendar, with things only it brings. **Instance of:** a story clock
(the nights' idiom: an `after_time` trigger and never-drawn clock stores) plus content unlocked by it. **Fits into:**
Clock (the season is save time), Triggers, Standing actions (the visitor's pause: a standing that draws a pool stops
when the pool is empty), Cards, Chips. **No engine work, no season state.** The Drift's end at 336 h is reached by its
pools running out, so nothing is retired and no saved mix greys at the turn.

| Store | Cap | Drawn | Notes |
|---|---|---|---|
| `drift_left` | 336 | never | B8's outcome adds 336; `ashfall` draws 2 an hour, so it empties at 336 h exactly |
| `drift_clock` | 8760 | never | a clock store from B8 (+1/h), for the Drift's threat step and the bear sign |
| `roof_ash` | 48 | never (the chip is its face) | `ashfall` makes 2 an hour |
| `bloom` ("fungus in the scrub") | 2000 | yes | B8's outcome adds 2000; nothing makes more; picking draws it |
| `fungus` | 24 | yes | B8's outcome adds 24 (the larder full); picking makes it |
| `ash` | 24 | yes | the roofs' clearing makes it |
| `ashed_ground` | 24 | yes | her card makes it; week 3's fields read it |

| Card | Lane | Opened by | Cap | Bar (s) | Takes | Makes | Skill |
|---|---|---|---|---|---|---|---|
| `pick_fungus` | hands | B8 | none | 30 | 1 bloom | 2 fungus | Foraging |
| `n3_pick` (town card) | n3, later n5-n7 | B8 | none | 120 | 1 bloom | 1 fungus | |
| `fungus_stew` | hands | B8 | none | 40 | 6 fungus, 1 dry wood | 3 stew | Cooking |
| `clear_roofs` | hands | B8 | none | 120 | 16 roof ash | 4 ash | |
| `n2_clear_roofs` | n2 | B8 | none | 1200 | 16 roof ash | 4 ash | |
| `n3_ash_ground` | n3 | SL15 | none | 1800 | 4 ash | 1 ashed ground | |
| `hide_flaps` | hands | `still_end` (G2's visit) | 4 stages | 600 | 2 pelt, 4 damp wood a stage | stage 4: "Rest +10%" (hides over the bays' openings against the wind); the pelts' sink after week 1's bedding |

| Chip | Shows while | Cost (words) | Cure |
|---|---|---|---|
| `ash_laden` | roof ash ≥ 16 | "rest slower": rest −15% | `clear_roofs` (hands, cuts in) or `n2_clear_roofs`; an order card offered with the chip's first showing: "when ash-laden, {n2} clears the roofs" (day one's hunger card, on his lane, D-91's shape) |

Two clears a day with the order on; the chip shows for the twenty minutes he is up there. Who clears is the decision
(his stakes, the hands' time); the ash it makes is the Drift's harvest and her ground's input.

**Fungus as food:** the stew pot takes it, and five (later eight) mouths eat stew. Food drives growth: when stew runs
out, eating pauses and nothing compounds. The bloom is sized so typical never empties it by night 14; a route that
does finds `pick_fungus` unready with its need marked, which costs nothing it had.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| B8 | 8a | 168 h (`after_time`) | As `spine.md`: the exhale. Warm wind out of the east all at once; ash coming down so thick the noon is brown; the bays' roofs sag under it by morning. Fungus up overnight on every dead birch and stump, shelves of it; the larder full for the first time. On the roof's ridge the crows sit in a row, beaks moving, and it is numbers they are saying. | as `beats.yaml` (up · yes_but · dread · time · PC · advances C-promise-4 · th-burn middle) |
| U1 | 8a | B8 + 6 h | In the warm dark, howls from three places round the Hollow at once, answering. By morning, prints of many in the fresh ash between the bays, round the rack and away; none at the fire. | down · none · dread · none · PC · opens C-promise-23 · th-survive middle |
| U2 | 8b | `fungus_stew`'s first finish | She tips the picked caps out on a cloth and sorts them without a word, half thrown into the fire. The pot goes round and comes back with some in it. Everyone eats until they stop. | up · yes · warm · none · PC, n3 · none · th-town middle |
| U3 | 8d | `r1_clock` ≥ 70 and `drift_clock` ≥ 12 | Wolves at the gap between the bays and the woodshed, five or six, in the warm dark; one comes as far as the rack and is driven back with a brand; the rest wait outside the light and go before dawn with what hung lowest. | down · yes_but · grim · stores · PC, N1 · advances C-promise-23 · th-survive middle |
| B9 | 8d | 3 journal entries + B7 | As `spine.md`. The book comes out by the fire for the first time and the player writes what is known: the rats, the crows, the wolves. On the wolf page, before a word is written, a note in the margin in pencil, in the player's own hand: wolves that came to the edge of the light and sat facing the fire, as if waiting to be asked in. | as `beats.yaml` (down · dread · none · PC · opens C-promise-2, advances C-promise-5 · th-past start), and pays C-promise-23 |

**Mechanically:** B8 is a trigger at 604 800 s whose outcome unlocks `drift`, the cards above and `ashfall`,
`drift_clock`, and adds the pools. U3 unlocks the `pack` fight; a trigger on `pack_fought` ≥ 1 unlocks the `journal`
feature and the three entries (each adds 1 to `entries`, never drawn); B9 is a trigger on `entries` ≥ 3. A save
rebased past 168 h when week 2 ships gets B8 at the rebase instant and U3 no sooner than twelve hours later (the
`drift_clock` require), so a long-idle save meets the turn and the pack in two returns.

### Side layer (day eight)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL15 | arc (n3, 3 of 3) | th-town | the first clear (`ash` ≥ 4) and B8 + 12 h | The first heap of roof ash comes down. She carries it to her turned ground by the stone in a sack and works it in with her hands, then unties the seed bag, counts seed out on the cloth in rows, and ties it up again. | her share: `n3_ash_ground` (ash into the ground) against picking; whatever week 3 plants does not depend on how much |
| SL16 | arc (n4) | th-town | B8 + 14 h and `n4_cord` finished once | In the warm wind the old man sits outside the bay for the first time, stripping bark and twisting it into cord against his good knee, fast, the way someone taught him. | his share: mending (cord for the palisade) against the watch (the pack's odds) |

## Day nine (B9 → B10 ★): can the camp be closed?

The book open by the fire. Lucy walks the line where the wall will be and the size of the job is plain. The pack comes
round the open side one night and takes what hung there. Posts go up a stretch at a time, stakes and cord from every
pair of hands. Smoke on the road beyond the ridge: people, coming slowly toward the Hollow. The last post goes in, the
ring is closed, and they are at the gate.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 9a | 0-9 h | the journal's margin; Lucy scoring the whole ring | can the camp be closed? | E1 (opens) |
| 9b | 3-9 h | a fire at the gap; the pack's odds on the card | (the gap) | side SL18 |
| 9c | 3-9 h | old wire on the track, set the way the player's own snares are | (who set it) | side SL17 |
| 9d | 3-9 h | the pack in through the open side; the rack stripped low | will it be up before they come back? | E2 |
| 9e | 3-9 h | stages rising; the pack losing more | | |
| 9f | 3-9 h | smoke on the road, more than one fire, coming | who is coming? | E3 (advances) |
| 9g | 3-9 h | the last stage; people at the gate | (who they are) | B10 (pays); O-family |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 9a (3-6 min) | reads the journal (the wolf page's margin, the odds as numbers); reads E1; moves shares: stakes, cord, the watch | E1 at B9 + 2 h; the journal's crow page's second note after B8 | Lucy walking the line in the ash with a stick | l_ring_1, l_ring_2 (E1) |
| 9b (3-5 min) | reads SL18; pays the **gap fire**'s first stage or holds the stones for the palisade | SL18 at E1 + 3 h; the pack's ramp step at `r1_clock` ≥ 130, its odds moving on the card | a fire laid at the gap | l_gap_fire_1 (SL18) |
| 9c (3-5 min) | reads SL17; pays the fourth snare from the wire or keeps it | SL17 at `field_track`'s run count n5; `set_snare_4` with it | old wire on a run in the scrub | l_old_wire (SL17) |
| 9d (3-5 min) | reads E2; re-hangs the rack (the hunt's share against stakes) | E2 at `palisade` stage 6 and B9 + 6 h: the visitor's drain on smoked | the ring half up; the rack stripped low | l_open_side_1, l_open_side_2 (E2) |
| 9e (3-5 min) | pays a stage; a Woodcutting find; Camp 14's marker held ("?") | Woodcutting 23 find | | l_find_pole |
| 9f (3-5 min) | reads E3; stakes past the palisade's need (the hut will want them; Camp 13's cap) | E3 at `palisade` stage 9 | smoke on the road beyond the ridge | l_smoke_1, l_smoke_2 (E3) |
| 9g (3-6 min) | reads B10; answers **O-family** (or its kind's rule already has); Camp 14 lifted | B10 at `palisade` stage 12 and save time ≥ 209 h; O-family with it | the ring closed; a gate; people outside it | l_b10_1 to l_b10_3, l_family_1, l_family_2, l_camp_14 |

### The palisade (P1) and the gap (fit pass)

**What it is:** the camp's first wall, built by the player from what the town makes, and the pack it keeps out.
**Instance of:** a staged comfort build (week 1's woodshed) on the hands, run by a content order card (D-85's order
cards, `at_least` on the stakes a stage takes), whose stages are entries on a side (week 1's `larder_floor` against
the rats); its materials are town cards on ruled lanes (week 1's per-lane gathering). The pack is a standing fight
(week 1's rats). The watch shares as entries on the side are the one new engine part (plan item 2): a card running on
a lane adds its entries while it runs, scaled by its share; week 1 deferred the watch fires' worth to here (D-108 as
proposed).

| Card | Lane | Opened by | Cap / stages | Bar (s) | Takes | Pays |
|---|---|---|---|---|---|---|
| `palisade` (P1) | hands | `still_end` (G2's visit) | 12 stages | 1800 | 24 stakes, 4 cord, 6 stones a stage | "Gap +50%" a stage; stage 12 closes the ring (B10 with the floor); scene: four states |
| `cut_stakes` | hands | `still_end` | none | 600 | 4 damp wood | 1 stake (Woodcutting) |
| `n1_stakes`, `n2_stakes` (town card; n6 and n7 from day eleven) | ruled lanes | `still_end` | none | 1800 | 4 damp wood | 1 stake |
| `twist_cord` | hands | `still_end` | none | 600 | 2 damp wood | 1 cord |
| `n4_cord` | n4 | `still_end` | none | 900 | 2 damp wood | 1 cord |
| `gap_fire` (SL18) | hands | E1 + 3 h | 2 stages | 1200 | 6 dry wood, 8 stones a stage | stage 2: "Watch +50%" (the watch shares' entries half again) |
| `set_snare_4` (SL17) | hands | SL17 | 1 | 600 | 2 wire, 2 dry wood | a fourth snare (week 1's `snare_*` standing shape) |

**The order card:** under the stakes line, offered once stakes first reach 24: "when stakes reach 24, build the
palisade" (an `at_least` with release 24, tapping `palisade`). It runs a stage whenever a stage's stakes are in, cord
and stones allowing, and is passed over at the cap.

| Side / threat | Base | Entries |
|---|---|---|
| side `gap` | 4 | `palisade` +50% a stage; while running, at their share: `n1_watch`, `n2_watch`, `n4_watch` +50% each (`gap_fire` stage 2 raises each to +75%); the guard +150% (day eleven); `n6_posts` +50%; `tallow_lamps` stage 3 +100% |
| threat `wolf_pack` | 8 | +25% at `r1_clock` ≥ 130 (a trigger on the clock store, combat's ramp idiom) |
| threat `ashrats` | 4 (week 1) | +50% at `drift_clock` ≥ 1: in the Drift the rats come indoors (a clock store, so the content check passes) |

| Fight | Kind | Side vs threat | Rate | On a loss | Opened by |
|---|---|---|---|---|---|
| `pack` | standing | `gap` vs `wolf_pack` | 1 a game h | 1 smoked; tallies `pack_fought`, `pack_lost` | U3 |

So the pack at U3 against the bare gap and a half share at the watch wins about two in three; with half the ring up,
about one in three; with the ring closed and the guard, under one in four (numbers file). Its loss is the rack's meat,
which the hunt and the snares make back; a pack with nothing on the rack takes nothing (the dry pause).

**Why 12 stages of 24 stakes:** the stakes cap is 24 (36 from Camp 13), so a stage is a cap's worth, and the stage
count, not the stage size, carries the length. The palisade is the week's ★ goal and runs from G2's visit to B10, about
85 h on typical: the town's split (stakes, cord, the watch) is what moves it, so a sharp setup closes it sooner and the
floor holds sharp's B10 at 209 h.

### The journal (fit pass)

**What it is:** the book from the coat (A3), now written in: one page per thing known, with its learned numbers.
**Instance of:** the Knowledge row's first real use, rendered as `decisions.md` asks (field-note hand, sketches,
numbers below). **Fits into:** Unlocks (an entry is an unlock of a new kind, grown only by outcomes; its notes are
unlocks too, so a later line under an earlier one is a later outcome), Knowledge (as a page reading: an entry's
numbers are the served fight view, exact once fought), Lessons (its first use), the page shell (a sheet). Not a system:
one caller, nothing to swap (plan item 5). A count store `entries` (never drawn) is what B9's gate reads, as
`arrivals` is for arrivals.

| Entry | Written by | Notes (ids; text in the brief) | Numbers shown |
|---|---|---|---|
| `e_wolf` | the first pack fight | `n_wolf_1` (plain: sizes, how many), `n_wolf_margin` (old ink, already there: B9) | the hunt's and the pack's odds, fought, lost |
| `e_ashrat` | the first pack fight | `n_rat_1`; `n_rat_2` at the Drift's rat step | the rats' odds, fought, lost |
| `e_crow` | the first pack fight | `n_crow_1` (they count); `n_crow_2` after B10 (the number they say is higher than the camp) | the crows' odds, fought, lost |
| `e_bear` | `hunt_bear`'s first finish | `n_bear_1`; `n_gutter_1` (a pencil drawing of a knot near the gutter of the next page) | the bear's odds, fought, lost |

No entry on the greycoat in week 2 (a sighting is not knowing; S3 writes nothing), on the stone, or on the fungus. At
most one ominous note per page: the wolf page's is the margin, the crow page's the second note.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| E1 | 9a | B9 + 2 h | Lucy takes a stick and scores a line in the ash round the camp, bays, rack, woodshed and the stone inside it, all the way round, and comes back to where she started. She looks at the line, and at the stack of stakes, and starts cutting. | up · none · warm · time · N1, PC · opens C-promise-24 · th-survive middle |
| E2 | 9d | `palisade` stage 6 and B9 + 6 h | In the night the pack comes round the side where there are no posts yet, quiet, and is gone before anyone is up; the rack's low rows are stripped and a pelt pegged out is dragged off into the scrub. | down · no · grim · stores · PC · advances C-promise-24 · th-survive middle |
| E3 | 9f | `palisade` stage 9 | From the ridge, smoke on the road beyond it, more than one fire, low, moving slowly toward the Hollow over the day. | up · none · wonder · none · PC, N1 · advances C-promise-24 · th-town middle |
| B10 | 9g | `palisade` stage 12 and save time ≥ 209 h | As `spine.md`: the last post set and lashed; the ring closed with a gate of stakes. By evening, people at the gate: a family of four, one a child, and a man behind them who has not said his name. Broken as families are: there is a gap where someone walked with them. | as `beats.yaml` (up · yes_but · warm · people · PC · advances C-promise-6 · th-survive middle), and pays C-promise-24 |

E2's take is the visitor's idiom (`e2_strip`, a standing drain on smoked with a clock store, 6 smoked and 1 pelt, pausing
at empty), the same whether watched or not. B10 is a trigger; its outcome unlocks `safety`, O-family and the aim, and
carries the ceremony (the feedback ladder's big-moment rung).

### Side layer (day nine)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL17 | find (the track) | th-past | `field_track`'s run count n5 | On a run in the scrub along the track, snare wire rusted to a stake, set with a knot that the player's own hands tie without thinking. Nobody in camp set it. | `set_snare_4` from the wire (catch) or hold the wire; a Q2 clue (`mysteries.md`: old snares set your way) |
| SL18 | comfort | th-survive | E1 + 3 h | A fire laid at the gap itself, stones round it, so whoever sits the watch sits where the wolves come. | `gap_fire` (dry wood, stones) against the stones the palisade wants |

### The asks (day nine)

Typical returns more often than the chapter's 6-8 visits (11 from B9 to B10), and from E2 to B10 nothing arrived but the
palisade's stages and E3's lines, so seven returns had nothing to decide (no calendar day may be dead
content-wise). The asks fill them: small things the camp puts to the player while the ring goes up, each an offer of
no kind whose two answers are a modifier or a few stores, neither judged (SL6's shape, `o_bank`).
**Fits into:** Offers (no kind, answered by hand), Modifiers, Triggers (the gates); the pacing is a hidden countdown
store drained by a standing action (the visitor's clock, `e2_clock`), so no new system. From E2 one ask shows at a
time: the first comes with E2 (one moment), each answer fills the countdown, and the next ask waits for it to empty and
for the last answer, so no absence brings two asks and a player away for a day finds one. Not chores (considered and rejected for this).

| Id | Gate | Who asks, and what (facts) | Answers (what each changes) |
|---|---|---|---|
| `o_posts` | `palisade` stage 2 (day eight's stretch) | Edward lashes the first stretch himself; his wet-twisted cord holds best. Keep him twisting, or back at the gap fire? | his cord made 25% faster · the gap +10% |
| `o_margin` | B9's moment | The wolf page's old-ink margin marks where the pack comes in. Set the watch there, or keep it by the fire? | the gap +25% · rest 5% faster |
| `o_rack` | E2's moment | Mary: what the strip left on the rack. Hang it high inside the posts that stand, or smoke it down hard now? | smoked holds 25% more · 6 smoked now |
| `o_deep` | the last answered + 1.5 h | Martin: the low side's ground is soft. Sink the posts a hand deeper there, or keep the pace? | the gap +25%, his stakes 10% slower · nothing |
| `o_bark` | the same | Lucy: the bark stripped off the poles. Dry it for tinder, or twist it into cord? | the fire takes 10% less dry wood · 4 cord now |
| `o_footing` | the same | Mary: stones turned up digging the footings. A hearth ring in the bays, or onto the pile? | rest 5% faster · 6 stones now |
| `o_fed` | the same | Mary: the watch eats cold. A share of the pot carried out to the gap each night, or the pot kept for the bays? | the gap +10%, stew 5% slower · nothing |
| `o_lookout` | the same | Martin wants a man up on the stacked stakes to watch the road. One up there, or everyone on the wall? | the gap +15%, his stakes 5% slower · nothing |
| `o_gate` | the same | Lucy: where the gate goes. Facing the road, or the track? | a line (the road side is where B10's people come to it) · the track takes 10% fewer roots |
| `o_skin` | the same | Martin: the wolf the watch killed. Its skin nailed on the posts, or on the flaps? | the gap +10% · 1 pelt |

Every route answers the same way in the simulator (`tests/weektwo/content.py`, `ASKS_EIGHT`, `ASKS_NINE`): the cord, the
watch at the margin, the rack high, the pace, tinder, the hearth ring, the pot, the wall, the road, the flaps.

## Day eleven (B10 → B11): will the man who came with them last?

The family takes the hut the town builds, or builds it. The man who came behind them lies by the fire and won't eat and
won't say his name. Someone has to stand the gap at night now; the player makes a spear and hands it over. The crows on
the ridge count, and the count is one short, and then someone goes to wake him. The town sits up with him by the fire,
and burns him at first light, and Lucy cuts his mark on a board with no name beside it.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 11a | 0 (B10's visit) | the family at the gate; the hut | will they stay? | (O-family) |
| 11b | 3-9 h | eight at the fire; he lies apart, won't eat, won't give a name | will he last? | Z1 (opens) |
| 11c | 3-9 h | the spear handed; someone at the gap | | Z2; side SL19 |
| 11d | 3-9 h | the crows' count one short; he's dead | (the night) | Z3 (advances) |
| 11e | 0-9 h | the vigil; first light; the mark on the board | (what now) | B11 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 11a (3-5 min, the rest of B10's visit) | answers **O-family**: **Make room** (`make_hut`, hands) / **Let them build** (`n5_build_hut`) | O-family at B10; the arrival kind's rule answers it at once where the player set one (week 1, plan items 10-12) | four figures at the gate, one sitting apart | l_hut_go, l_hut_theirs |
| 11b (4-6 min) | reads Z1; **splits** the town's mix across seven; answers **O-guard** ({n2} or {n7}) | Z1 at the hut done (arrivals 9); O-guard with Z1 | eight at the fire; the stranger lying apart, wrapped | l_join3_1, l_join3_2 (Z1), l_guard_ask |
| 11c (3-5 min) | reads Z2; reads SL19 and gives the husband the leftover stakes or not | Z2 at `arm_n2` or `arm_n7` done (queued by the answer); SL19 at Z1 + 4 h once O-guard is answered | the guard at the gap fire with the spear; the husband walking the ring | l_guard_1, l_guard_2 (Z2), l_posts (SL19) |
| 11d (3-5 min) | reads Z3; queues **Keep the vigil** (A31) When ready, shown unready with its countdown | Z3 at `stranger_clock` ≥ 20 (hours from B10) once Z1 has landed; dusk 12 at 22 after Z3; A31 on the cards from Z3 | crows on the ridge; him covered | l_count (Z3), l_night_12 |
| 11e (3-5 min) | taps or has queued A31; reads B11; meets the dig (its order card) | B11 at A31 and Z2; `dig_cellar` with A31's finish | night grade; the vigil, then a fire at the scrub's edge at first light; a board by the fire with one mark | l_b11_1 to l_b11_3, l_dig_open |

### The third arrival group (fit pass)

**What it is:** four people from one offer, three who will work and their child, who never will (`decisions.md`,
"Never": children live in the town, never workers, a cost or a fight outcome). **Instance of:** the arrival idiom (D-100,
O-pair): an offer of kind `arrival` whose two answers build the same room by either lane in the same time, a join on
completion. **Fits into:** Offers (the kind's rule answers it), Cards (the hut on either lane), Triggers (one outcome
with three `joins` and arrivals +3, and the child's own at the same instant, arrivals +1, since each join adds one),
Mixes (three shares in the town's mix), People (light tier). The stranger is not the offer's: he comes in with B10's
moment, an arrival (+1 to `arrivals`) with no lane, a scene figure and a clock (`stranger_clock`, from B10), so his death
needs no lane removed and no person-shaped loss in the engine (combat's KNOWN GAP stays closed). Arrivals read 9 after
Z1.

| Offer | Shown | Answers | Each answer | Expires |
|---|---|---|---|---|
| O-family (kind `arrival`) | B10 | **Make room** / **Let them build** (labels to the voice pass) | Make room: `make_hut` (A33) on the hands. Let them build: `n5_build_hut` (A34), equal real time at her base pace. Same stores: 24 stakes, 12 stones. On completion all four join: n5, n6, n7 as lanes and their child, arrivals +4, scrap +6 (what they carried) | never |

`make_hut` bar 10 800 s (the second bay's measured length).

**Who they are** (light tier; souls from the save's seed, Claude-off stand-ins; names from `names.jsonl` by the seed;
lines say "the woman", "her husband", "her brother", "their child" until Z1 gives the names):

- **n5**, a woman of thirty-five who does the talking for all of them. Plain pace.
- **n6**, her husband, broad, says nothing he doesn't need to; he laid hedges and fences once, which shows in how he
  looks at posts (SL19).
- **n7**, her brother, nineteen, who looks at the spear on the wall before he looks at anything else.
- **Their child**, young, who stays close to the woman; no lane, never a hand or a mouth in the numbers, never in danger
  in this chapter, and not the one they are missing.
- They are missing someone. No line counts, names or says who; the scene shows four where the way they stand leaves
  room for a fifth. `young_loss_rate` is not drawn on: nothing says who it was.
- **The stranger**: a man who walked behind them on the road for days, keeping his distance, and sat at the edge of their
  fire each night until they let him come in. A wound gone bad, wrapped. He does not say his name to them or to anyone.
  His death is decided as of his arrival (`decisions.md`, "Groups arrive broken"): nothing the player has or does
  reads on him, no card or line offers a cure, and no line suggests one could have.

Their cards: the town cards (forage, gather, cut, stakes, pick) on n5-n7 by item 4's expansion. Default split on
joining: n5 forages, n6 keeps the watch (his stakes by a rule offered with the join: under 15, until 23), n7 picks fungus.

### The guard (fit pass)

**What it is:** a townsperson given the spear and set at the gap. **Instance of:** a ruled lane whose task is a fight's
preparation (combat-plan: "the guard is a townsperson's lane given a side"). **Fits into:** Lanes (a ruled lane's
always rule), Offers (who, as the answer), Cards (the queued one-off that makes the spear, o_pelt's idiom), Modifiers
(plan item 2: the guard card's entry on `gap` while it runs), Triggers (the install on the arm card's count).

| Offer | Shown | Answers | Each answer |
|---|---|---|---|
| O-guard | with Z1 | **{n2}** / **{n7}** | queues `arm_n2` / `arm_n7` (hands, 600 s, 6 scrap, 1 stake, cap 1) and unlocks that lane's `n2_guard` / `n7_guard`; a trigger on the arm card's count installs that lane's always rule on its guard card, first (`RuleInstall`, `first = true`) |

`n2_guard` / `n7_guard`: on that lane, bar 3600 s, makes nothing, while running "Gap +150%". Whoever guards stops
gathering; the player can edit the installed rule like any other. Neither answer is judged: him, who carried the shaft
the first spear was made from, or the young man who wanted it.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| Z1 | 11b | the hut done (arrivals 9) | They take the hut. The woman gives the three names. The man who came behind them lies by the fire on the side away from the family, wrapped, and does not eat what is given him. Asked his name, he looks at the fire. | down · none · grim · none · PC, N1 · opens C-promise-25 · th-town middle |
| Z2 | 11c | `arm_n2` or `arm_n7` done | The spear's head beaten on the stone and bound on; the player hands it over at the gap fire, and the one who takes it goes out to the gap and stands there through the dark with it, facing out. | up · yes · warm · none · PC · none · th-survive middle |
| Z3 | 11d | `stranger_clock` ≥ 20, once Z1 | On the bays' ridge the crows count, as they do every morning, and the count is one short of yesterday's. Then Lucy goes over to wake him, and he is dead. | down · none · dread · none · PC, N1 · advances C-promise-25 · th-town middle |
| B11 | 11e | A31 (in night 12) and Z2 | As `spine.md`: the town sits up with the body by the fire through the night, the guard at the gap; at first light they burn him at the scrub's edge, not on the camp stone. Someone lays a hand flat on the warm ground while it burns. Nobody knew his name, so Lucy cuts his mark on a board by the fire with nothing beside it. | as `beats.yaml` (down · yes_but · grim · people · PC, N1 · th-survive middle), and pays C-promise-25 |

Z2 is two triggers, one on each arm card's count, each with its own line set naming its guard and its install; the
feature `guard_made` is unlocked by either. The board is the town's first tally board, a scene state from B11 (one mark)
that B12's mirrors; no line connects the two. The crows' count is the tallymen's rule (`creatures.md`); no line says what they count or in what.

### Side layer (day eleven)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL19 | arc (n6) | th-town | Z1 + 4 h, once O-guard is answered | The husband walks the ring with a hand on each post, stops at three that lean, and asks for the stakes left over. | `n6_posts` (his lane, cap 1, 12 stakes, 3600 s; "Gap +50%") against the dig's stakes |

### The asks (day eleven)

Day nine's asks carried on while the hut waits on its stakes (typical's first return after B10 had nothing to decide):
the same shape (offers of no kind, day nine's hidden countdown `ask_wait`, one a return), the first once day nine's last
is answered and B10 has landed. Every route answers the same way in the simulator (`ASKS_ELEVEN`): the gate, the pot,
the ditch.

| Id | Who asks, and what (facts) | Answers (what each changes) |
|---|---|---|
| `o_door` | Martin: the hut's door. Facing the fire, or the gate? | rest 5% faster · the gap +10% |
| `o_pot` | the woman: they carried a pot of their own. Hang it by the camp's, or trade it for what Martin can use? | stew 5% faster · 6 scrap |
| `o_ditch` | Lucy: ash heaped against the posts inside the ring. Dig it out to a ditch outside, or bank it and take the stones from under it? | the gap +10% · 6 stones |

**The watch on the new lanes:** `{lane}_watch` on n5-n7 (town cards, 1200 s, 1 dry wood, "Gap +50%" held while it
runs), so Z1's seven-way split is gathering against the watch. Her husband joins on the watch (forage or gather on his
lane lost over half the roots or dry wood made at the chapter's end).

## Day twelve (B11 → night 14): what is under the camp?

Morning after the burning. With eight to feed and the larder full, the town needs somewhere to keep it. The player starts
digging by the ruin's north wall before anyone asks where, and the spade goes through into cut steps going down, dry
air, a real cellar. No stores in it: a board scored with marks in groups, the last group unfinished, and a stool short
on the same leg. The bear comes for the fungus. On the Drift's last evening a wolf sits at the edge of the light facing
the fire and doesn't move; when the wind drops before dawn, it's gone.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 12a | after night 12 | the dig started where nobody chose | what is under the camp? | S1 (opens) |
| 12b | 3-9 h | bear sign at the bloom | (the bear) | side SL20 |
| 12c | 3-9 h | cut steps under the ash, dry air | what is down there? | S2 (advances) |
| 12d | 3-9 h | the cellar opened: no stores | (the board, the stool) | B12 (pays) |
| 12e-12f | 3-9 h each | tallow; lamps at the gate; levels | | side SL21 |
| 12g | 3-9 h | a wolf sitting at the edge of the light, facing it | what does it want? | S3 (opens) |
| 12h | 0-9 h | night 14, the wind dropping | (week 3) | S4 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 12a (3-5 min) | reads morning 13 and S1; accepts the dig's order card ("when stakes reach 12, dig"); re-tunes stakes now the palisade is done | morning 13 at A31 + 1 h; S1 at `dig_cellar` stage 1 | the player at the ruin's north wall with a spade | l_morning_13, l_dig_1, l_dig_2 (S1) |
| 12b (3-5 min) | reads SL20; **chooses** a bear hunt (odds unknown) or not; the hunt's share | SL20 at `drift_clock` ≥ 96: `hunt_bear`, `bear_sign` 6 | torn shelves on the dead birch, claw marks high up | l_bear_sign (SL20) |
| 12c (3-5 min) | reads S2; the first bear hunt home or lost; the bear's journal page | S2 at `dig_cellar` stage 3; `e_bear` at the first bear hunt's finish | a stair cut in stone going down | l_steps_1, l_steps_2 (S2) |
| 12d (3-5 min) | reads B12; re-tunes roots and fungus now they hold more; Camp 15 | B12 at `dig_cellar` stage 4, save time ≥ 249 h and B9 | the cellar mouth open | l_b12_1 to l_b12_3, l_camp_15 |
| 12e (3-5 min) | reads SL21; pays **tallow lamps** from the bear's tallow | SL21 15 h after SL20 (`sign_clock`) | lamps on the gate posts | l_lamps (SL21) |
| 12f (3-5 min) | levels and finds; the hunt and the dig's last stakes; her ground | finds (below) | | find lines |
| 12g (3-5 min) | reads S3; queues **Sit the last night** (A32), shown unready with its countdown; Camp 16's marker held ("?") | S3 at `drift_clock` ≥ 150 (318 h); A32 on the cards from S3 | a grey wolf sitting just outside the light, facing the fire | l_sitter_1, l_sitter_2 (S3) |
| 12h (3-5 min) | taps or has queued A32; reads S4; Camp 16 lifted | dusk 14 at save time ≥ 330 h; night 14 + 0.25 h; S4 at A32 and S3; the week's end card | night grade; eight at the fire; the guard at the gap; the edge of the light empty by dawn | l_night_14, l_s4_1 to l_s4_3, l_camp_16 |

### The cellar (fit pass)

**What it is:** a dig that becomes a store-room. **Instance of:** a staged comfort build (the woodshed again) run by an
order card, whose finish raises caps and a side (the woodshed's cap raise, the larder floor's entry). **Fits into:**
Cards, Modifiers, Standing orders (the order card). No engine work.

| Card | Lane | Opened by | Stages | Bar (s) | Takes | Pays |
|---|---|---|---|---|---|---|
| `dig_cellar` | hands | A31's finish (B11) | 4 | 2400 | 16 stakes, 6 damp wood a stage (props and shoring) | stage 1 S1, stage 3 S2, stage 4 B12 (with the floor); finished: "Roots hold +50%", "Larder +200%" (against the rats); fungus's room is Camp 15's, lifted by the last stage; scene: four states |

The order card under the stakes line, offered with A31's finish: "when stakes reach 16, dig". The dig is the stakes'
sink from B11: with the posts done, nothing in day eleven took stakes, and sharp and whenever lost over half their
stakes making to the cap in day eleven's long absence; the dig's order card is set in B11's visit. The dig gains no
Scavenging: a new XP source would move every route's levels and their finds.

### The bear (fit pass)

**What it is:** a Drift-only beast the player can choose to hunt. **Instance of:** a fight card (C3's hunt) whose input
includes a finite pool, so it stops when the pool is spent (week 1's rule that everything has a cap, kept on an uncapped
fight card). **Fits into:** Cards (a FightDef), Combat (a new threat), Stores (the pool, tallow), the journal (an entry
on first finish). No engine work.

| Card | Lane | Fight | Bar (s) | Takes | Makes (won share) | On a loss |
|---|---|---|---|---|---|---|
| `hunt_bear` | hands | `hands` vs `ash_bear` (16) | 2400 | 2 smoked, 1 bear sign | 3 catch, 1 pelt, 2 tallow | `hurt` +2 (the drain's whole hurts); tally `bear_lost` |
| `tallow_lamps` (SL21) | hands | | 600 | 2 tallow and 2 stakes (split for the wicks' holders) a stage, 3 stages, run by its order card | stage 3: "Gap +100%" | |

With the spear and Melee 4 the hands' side is about 22 against 16: a bear hunt loses about two in five, and its odds read
unknown until the first one. Six hunts at most this Drift. Its page (`e_bear`) is written with SL20, the sign at the
bloom: one moment, and its numbers fill in at the first hunt (blind until learned). The bear's tallow goes to the gate's lamps: the optional hunt
pays into the week's defence. No bear at the camp: the bear is the player's to seek, never a raid.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| S1 | 12a | `dig_cellar` stage 1 | The player takes the spade to the ruin's north wall and starts digging before anyone has asked where, and only then looks round to see if anyone minds. Nobody does. | up · yes · wry · time · PC · opens C-promise-26 · th-past middle |
| S2 | 12c | `dig_cellar` stage 3 | Under a yard of ash the spade rings on cut stone: steps going down, whole, and the air coming up them dry and cold. | up · yes_but · wonder · none · PC · advances C-promise-26 · th-past middle |
| B12 | 12d | `dig_cellar` stage 4, save time ≥ 249 h, B9 (Scavenging 15 met) | As `spine.md`: a cellar, square, dry, dug for stores. No stores. On one wall a board scored with marks in groups of five, the last group four; in the corner a stool, short on the same leg as the one at the fire. | as `beats.yaml` (down · no · wry · time · PC · advances C-promise-2, C-promise-5, pays C-promise-8 · th-past middle), and pays C-promise-26 |
| S3 | 12g | `drift_clock` ≥ 150 (318 h on every route) | At dusk a wolf comes to the edge of the light, grey, alone, and sits down facing the fire. It sits longer than a wolf sits. The guard doesn't move; nor does it. | down · none · dread · none · PC · opens C-promise-27, advances C-promise-2 · th-past middle |
| S4 | 12h | A32 (in night 14) and S3 | Night 14. The wind that has blown all week drops before dawn, all at once, and the ash stops coming down so hard. Eight at the fire, the guard at the gap. When it is light enough to see, the edge of the light is empty and there are no prints where it sat. | up · yes · warm · none · PC, N1 · pays C-promise-27 · th-survive middle |

B12's board and stool are the canon joke: no count matches anything (four in the last group says nothing; the town's
own board has one mark). S3 is the margin note's behaviour come true, never named and never tied to the note by a line.
S4's dropping wind is the Drift ending, the calendar's fact; it says nothing of the Clear (B13's).

### Side layer (day twelve)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL20 | find | th-survive | B11 + 5 h (`dig_clock` 5), once `drift_clock` ≥ 96 | At the bloom on the dead birch, the shelves torn down and eaten, claw marks higher on the trunk than a man can reach. | `hunt_bear` (odds unknown) against the hunt and the dig |
| SL21 | comfort | th-survive | 15 h after SL20 (`sign_clock`) | Tallow from the bear rendered in the stew pot, poured into split stakes for lamps on the gate posts. | `tallow_lamps` (tallow) |

### The clocks

**Night 12** is a story night for the vigil: dusk 12 at `stranger_clock` ≥ 22 (hours from B10, whose 210 h floor keeps
it past B11's sharp floor) after Z3; A31 (`keep_vigil`, "Keep the vigil", glows) requires `stranger_clock` ≥ 22.25 and a
guard made (`guard_made`, a hidden clock either arm card's finish unlocks), so its countdown shows from Z3; morning 13 at
A31 + 1 h (day twelve). A31 is on the cards from Z3, unready with the night's countdown, queueable When ready.

**Night 14** ends the week on the calendar: dusk 14 at save time ≥ 330 h (`after_time`), so night 14 falls before the
Clear's turn at 336 h on every route; A32 (`sit_last_night`, glows) requires `night_14` ≥ 5 and S3's feature, on the
cards from S3. Built: A32 requires `drift_clock` ≥ 163 (the season's clock, from B8 at 168 h on every route: 331 h, an
hour into the night), since a countdown needs a clock already running when S3 shows it, and `night_14` runs only from
dusk. S3 is on the season's clock (`drift_clock` ≥ 150, 318 h), not combat's: at `r1_clock` 175, typical's S3 shared
SL21's absence and lay 15 h before the night, and a later reading put whenever's past 330 h. S4 is week 2's last beat; B13 does not wait
on it.

### The asks (day twelve)

Day eleven's asks carried on while the cellar goes down: the same shape (offers of no kind, the hidden countdown
`ask_wait`, one a return), the first once `o_ditch` is answered and the dig is open, so it can share B11's moment. Every
route answers the same way in the simulator (`ASKS_TWELVE`): the ring, the fire, bound, the meat, the wood, the bedding,
the drain, let them be, propped.

| Id | Who asks, and what (facts) | Answers (what each changes) |
|---|---|---|
| `o_spoil` | her husband: the spoil from the dig. Bank it against the ring outside, or sieve the stones out of it? | the gap +10% · 6 stones |
| `o_cradle` | the woman: their child won't sleep in the hut. A place by the fire, or the pot moved into the hut? | rest 5% faster · stew 5% faster |
| `o_shaft` | her brother: the spear's shaft has split at the binding. Bind it again tighter, or cut a new head-socket from the iron in the scrap? | the hands +10% · 4 scrap |
| `o_cold_air` | Lucy: the cold air coming up the steps. Hang the meat below, or keep it on the rack where she can see it? | the larder +10% · the rack +10% |
| `o_lean_to` | Martin: a lean-to on the hut's side. For the wood, or for the hides? | dry wood holds 10% more · pelts hold 50% more |
| `o_lye` | the woman: lye leached from the roof ash. Scrub the bedding with it, or the pot? | rest 5% faster · stew 5% faster |
| `o_wet` | Martin: the hut's floor is wet at one corner where the ash-water runs in. Drain it to the ditch, or pave it? | rest 5% faster · 6 stones |
| `o_crows` | the old man: the crows have come down off the ridge to the rack. Drive them off, or let them be (they cry at whatever comes near in the dark)? | the rack +10% · the gap +10% |
| `o_sag` | her husband: the hut's roof sags under the ash. Prop it with a pole, or let it come down and burn the poles? | rest 5% faster · 6 dry wood |

## Levels and finds (week 2)

Ranges are expectations for typical by night 14 (simulator). Finds go only on speed-only levels (week 1's G3 rule),
restate the level's row, and require feature `drift`, so a save already past the level gets it at B8. All in
`day_eight.toml` but Melee's (`day_twelve.toml`). If the simulator shows typical past a level at B8, the find moves to the
next speed-only level in range; with none left, it is cut.

| Skill | Level | Pays |
|---|---|---|
| Foraging (12-15) | 13 | a shelf of fungus as wide as a cartwheel on one stump (fungus +12) |
| Woodcutting (22-26) | 23 | a dead ash pole standing straight, sound to the heart (stakes +8) |
| Scavenging (22-25) | 23 | a hoe blade with no handle in the ruin's footing (scrap +3) |
| Cooking (8-11) | 9 | the fungus pot thicker by morning (stew +6) |
| Melee (5-8) | 7 | a wolf dead at the gap, older than the pack's (pelt +1) |
| Arcana (9-12) | 9 | "Rest +10%" (the stone's heat moved into the bays' floors under the pelts) |
| | 10 | speed |
| | 11 | find: the roof ash heaped by the stone dry and fine by morning (ash +6) |
| | 12 | "Stone +20%" (`hand_on_stone`) |

No find names wolves sitting at the light, the stone's heat past what the hand does, the cellar before B12, or anything
of week 3.

## The Camp

| Level | At (camp items) | Pays |
|---|---|---|
| 13 | 1 200 000 | "Stakes hold 36, was 24" |
| 14 | 1 600 000, held ("?"); lifted by `palisade`'s last stage | "Stew holds 30, was 18" |
| 15 | 2 100 000, held ("?") since day nine; lifted by `dig_cellar`'s last stage (B12) | "Fungus holds 36, was 24" |
| 16 | 2 700 000, held ("?"); lifted by `sit_last_night` (A32) | "Smoked holds 60, was 45" (o_rack_high's answer counted) |
| 17 | 3 400 000, held ("?") past week 2's content | (week 3) |

## Stated aims

| Aim | Starts at | Intent |
|---|---|---|
| aim_keep (week 1's) | feature wolves (B7) | ends at B8 |
| aim_wall | feature drift (B8) | close the camp |
| aim_room | O-family shown | room for them |
| aim_gap | Z1's feature | someone at the gap |
| aim_store | feature dig (A31's finish) | somewhere to keep it all |
| aim_wind | feature cellar (B12) | see out the wind |

Aims are lines: no season name, no beat.

## The flat check, authored order

Spine and chapter beats from B8, in landing order on typical: B8 up, U1 down, U2 up, U3 down, B9 down, E1 up, E2 down,
E3 up, B10 up, Z1 down, Z2 up, Z3 down, B11 down, S1 up, S2 up, B12 down, S3 down, S4 up. Never three turns the same.
Outcomes: B8 yes_but, U2 yes, U3 yes_but, E2 no, B10 yes_but, Z2 yes, B11 yes_but, S1 yes, S2 yes_but, B12 no, S4 yes
(no run of yes). Registers: dread, dread, warm, grim, dread, warm, grim, wonder, warm, grim, warm, dread, grim, wry,
wonder, wry, dread, warm (never four the same). Costs: time, none, none, stores, none, time, stores, none, people, none,
none, none, people, time, none, time, none, none.

**Net:** chapter beats U1 −, U2 +, U3 −, E1 +, E2 −, E3 +, Z1 −, Z2 +, Z3 −, S1 +, S2 +, S3 −, S4 + = +1; spine B8 +,
B9 −, B10 +, B11 −, B12 − = −1; week 2's `week_net_up` settles at 0. The near promises: C-promise-23 opened 8a, advanced
and paid 8d; C-promise-24 opened 9a, advanced 9d and 9f, paid 9g; C-promise-25 opened 11b, advanced 11d, paid 11e; C-promise-26
opened 12a, advanced 12c, paid 12d; C-promise-27 opened 12g, paid 12h. Expected flags to accept (as D-103's): 8b and 8c
do not touch C-promise-23 (near_untouched), 12e and 12f touch none (between two near questions).

## Away from the screen

- **Every planned moment plays in full on return:** B8, U1, U3, B9, E2, E3, Z3, S3 and most stage finishes land while
  away on typical; each is revealed in order, one at a time.
- **Per absence, at most two unlocks:** night 7 → 8a brings B8 (its cards are one moment) and U1; 8c → 8d brings U3
  and B9 (an hour apart); the rest are one per absence. A return that brings O-family answered by rule and Z1 counts two.
- **The 2 AM test:** the palisade, its stakes and cord are on screen from G2's visit, before the turn; B8's cards open
  onto full fungus and a pool, so picking has nothing to add until the pot draws it; the dig opens with A31, a tap; the
  vigil and the last night are queueable When ready from the visit before. The pack, the rats and the bear are flows
  (invariant 81). The roofs' chip costs only while it shows, and its order card covers absences once accepted.
- **Rebased saves:** a save past G2 when week 2 ships gets the palisade and stakes at the rebase instant; past 168 h, B8
  at the rebase instant and U3 no sooner than twelve hours later; nothing else of week 2 can be past.

## Art

All picked from the packs by `sprite-catalog` first; drawn only where the kit lacks it.

- **Grades:** the Drift (brown at noon, ash falling heavy, warm), from B8 to week 3's B13; nights 12 and 14 (night
  grade, each until its morning; night 12's keyed on `action:night_12`).
- **World layers (cool):** ash heaped on the bays' roofs while `ash_laden` shows; fungus shelves on the dead birch and
  stumps (Drift; the kit's cave fungus and stump-with-mushrooms tiles, recoloured); wolves at the gap (U3 to B10,
  dusk and night only: week 1's lean wolf, four of it); claw marks and torn shelves (SL20); the sitting wolf at the
  light's edge (S3 to S4, dusk and night: the same wolf sprite seated, recoloured greyer; drawn only if the kit has no
  seated wolf); smoke on the road beyond the ridge (E3 to B10); old wire on a stake (SL17, off-scene: the track).
- **Player-made (warm):** the palisade (four states by stages 3, 6, 9, 12: the kit's stockade panels, `desert.png`);
  a stakes stack (firewood stack tiles); the gap fire (2 states); the hut (3 states: ruined-wall strips building up,
  `house.png`, and a log-wall strip); the cellar mouth (4 states: the kit's shovel and mining props, a boarded doorway
  strip for the opened mouth); the tally board by the fire (the kit's notice board, one mark from B11); lamps on the gate
  posts (lantern props); her ash-dark ground (a darker state of week 1's turned ground); the fourth snare.
- **Figures:** the woman, her husband, her brother and their child (picked from the character sheets, grimed in code; the
  child from the kit's small figures, never posed working); the stranger lying
  wrapped apart from the fire (Z1 to Z3; a lying pose from the kit if one exists, else a bedroll prop with a head); his
  body covered through the vigil (transient id `vigil:body`, A31's finish to morning 13); the burning at the scrub's
  edge at first light (transient id `vigil:pyre`, morning 13 to + 1 h; the kit's brazier and firewood); the guard at the
  gap fire with a spear (`running:n2_guard` / `running:n7_guard`); the player raising posts (`running:palisade`) and
  digging (`running:dig_cellar`); the old man twisting cord (`running:n4_cord`); the bear off-scene (the hunt has no
  carry-back pose, as week 1 dropped the wolf's).
- **Journal sketches** (make-or-break, `decisions.md`): wolf, ashrat, crow, ash-bear, each code-drawn by the sketch-test
  method and looked at before it ships; the wolf page's margin note and the gutter knot in the old hand's pencil.
- **Stages:** 41_drift, 42_ash_roofs, 43_pack_gap, 44_journal, 45_ring_half, 46_ring_closed, 47_family, 48_guard,
  49_vigil, 50_cellar, 51_sitter, 52_night_fourteen.

## Proposed canon (tentative until the lead confirms)

- C-promise-23: day eight's near question, *what is circling the camp?*, opened by U1, advanced by U3, paid by B9.
- C-promise-24: day nine's, *can the camp be closed?*, opened by E1, advanced by E3, paid by B10.
- C-promise-25: day eleven's, *will the man who came with them last?*, opened by Z1, advanced by Z3, paid by B11.
- C-promise-26: day twelve's, *what is under the camp?*, opened by S1, advanced by S2, paid by B12.
- C-promise-27: day twelve's second, *what does it want?*, opened by S3, paid by S4.
- C-beat-103 (U1), C-beat-104 (U2), C-beat-105 (U3), C-beat-106 (B9's shape: the journal opens at the first pack fight
  with three entries; the margin note is on the wolf page), C-beat-107 (E1), C-beat-108 (E2), C-beat-109 (E3),
  C-beat-110 (B10's arrivals: a family of four, one a child, and a stranger), C-beat-111 (O-family), C-beat-112 (Z1), C-beat-113
  (O-guard and Z2), C-beat-114 (Z3), C-beat-115 (B11's shape: the vigil, the burning at the scrub's edge, Lucy's board
  with one unnamed mark), C-beat-116 (S1), C-beat-117 (S2), C-beat-118 (B12's count: groups of five, the last four),
  C-beat-119 (S3), C-beat-120 (S4), each as its row above.
- The fourth arrival group is a family of four missing someone (a woman who talks for them, their child, her husband who laid
  hedges, her brother of nineteen) and a nameless stranger who walked behind them and dies the next day; light tier.
- The town's first tally board is Lucy's, by the fire, from B11.
- The Drift's things in R1: roof ash to clear (and its harvest), a bloom of fungus on dead wood, ashrats coming indoors,
  the ash-bear at the bloom.

Decisions to record:
- D-111: B10's gate gains a save-time floor (209 h).
- D-112: B11's gate becomes A31 (the vigil in night 12) and the guard made, beside tier safety.
- D-113: B12's gate gains `dig_cellar` stage 4 and a save-time floor (249 h).
- D-114: the journal opens at the first pack fight with three entries (wolf, ashrat, crow), and B9 lands with them on
  its canon gate.
- D-115: season content is pools drained by standing actions and cards on those pools; a season raises no rate; the Drift
  has no day-night cycle, only nights 12 and 14.
- D-116: n4 lives through week 2; B11's death is a stranger with no lane.
- D-117: `hurt` is kept in quarters (wounds 4, heal 1 an hour, poultice takes 4, cap 12) and never drawn; the chip is
  its face (closes G7 and G8).
  *Superseded 2026-10-31:* the drain shipped instead of quarters (!153; heal 1 per 4 h, the chip at a quarter, a cure drains
  up to 3); see docs/design/week-two-plan.md, item 10. The text above is kept as decided then.
- D-118: watch shares and the guard are entries on the `gap` side while their cards run, scaled by share.
- D-119: every staged hands build from week 2 on is run by one order card that covers every stage and is passed over at
  its cap; a card that can open while the player is away opens onto a full store or a finite pool, or arrives running by
  a default.
- D-120: the palisade and its materials appear at G2's visit, before the turn.
- D-121: week 2 ends at night 14, dusk on the calendar's 330 h.
- D-122: her third moment (n3) is the roof ash worked into her ground in day eight; week 1's growing-food question is
  answered by canon (B13's fields).
- D-123: ACCEPTED EXCEPTIONS: near_untouched at 8b, 8c, 12e and 12f.

## For the owner

Two questions, asked spoiler-free in this pass's report:

1. **Children among arrivals.** Answered (`decisions.md`, "Never", 2026-10-30): children live in the town. Day eleven's
   family brings their child, who takes no lane.
2. **A recurring seasonal chore.** The roofs' chip and its order card are a chore that repeats for the week, handled by
   a rule once accepted. If he would rather seasons only add things to do, the chip goes and the roof ash becomes a plain
   card on his lane; the ash and her moment stay.

## Open (content side)

1. **The palisade's length** (12 stages × 24 stakes) and the stakes cards' bars are the simulator's to set so typical
   lands B10 mid-band; the floor holds sharp. Never lengthen a hands bar to move a band.
2. **U3's clock** (`r1_clock` ≥ 70) is set so typical lands B9 mid-band from B7's spread; if B7 moves, move it.
3. **The bloom's size** (2000) is B8's released outcome, so day twelve holds "typical never empties it by night 14"
   from the draw side: the cellar's finish (B12) makes every pick draw three quarters of a bloom for the same fungus.
   Without it typical ran dry in night 14 (numbers file, "Measured (day twelve)");
   `test_typical_never_empties_the_bloom_by_the_last_night` holds it.
4. **Ash** is a cure's by-product: if the cap-loss check fails it, the lever is the clear's yield (4), not a new sink.
5. **Week 1's proposed D-103 to D-110 and C-beat-94 to C-beat-102** were never recorded and three of the D ids are
   taken; whoever records them renumbers them. Week 2's start at D-111 and C-beat-103 to stay clear.
6. **Week 3 must decide** what a share does when its season's pool runs dry (the bloom at 336 h): `decisions.md` says a
   re-tune is only ever set off by something the player chose, so the share should yield its time to the rest of the
   mix, not idle (plan, "After week 2").
