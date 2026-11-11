# Days four to seven: from the warm ground to the end of week 1

Spoilers: this file is under `content/` and never shown to the owner. It picks up where `day-three.md` ends (B5, night 4)
and runs to the end of story day 7, the last night of the Still, in four chapters. It extends `day-three.md`'s "B5 to
B7" outline and keeps it except where a section below says why not. Numbers are targets
(`days-four-to-seven-numbers.md`); lines are written from `days-four-to-seven-lines-brief.md`; engineering's side is
`docs/design/days-four-to-seven-plan.md` (spoiler-free). Combat's shapes are `combat-open.md`'s answers (C1-C9),
banked time's are `banked-time-open.md`'s (BT1-BT6). New canon is listed at the end as proposals (tentative until the
lead confirms), new decisions as D-103 to D-110.

Binding, carried: day and night run on the story's clock; a planned moment that lands while the player is away plays
in full on return; nothing is lost *because* the player was away (D-59). Every return has something to spend and
something to decide (D-94). A side beat never gates a spine or chapter beat (D-97).

## The four chapters

A chapter named "day N" plays from story day N's evening through story day N+1 to night N+1, as day one to day three
do. So:

| Chapter (file) | Beat span | Story time | Near question (proposed canon) | Typical span |
|---|---|---|---|---|
| Day four (`day_four.toml`) | B5 → B6 | morning 5 to night 5 | C-promise-20, *will the fire last?* opened L1, advanced L3, paid B6 | about 20 h |
| Day five (`day_five.toml`) | B6 → B7's eve | morning 6 to night 6 | C-promise-21, *who else will come to the fire?* opened M2, advanced M1, paid B7 | about 20 h |
| B7 (`b7.toml`, combat-plan item 8) | B7 | night 6 | (pays C-promise-21) | minutes |
| Day six (`day_six.toml`) | B7 → night 7 | morning 7 to night 7 | C-promise-22, *can the camp keep what it has?* opened G1, paid G2 | about 35 h (to the calendar's day 7) |

Week 2 opens on B8, the season's turn to the Drift on the calendar's day 8 (`beats.yaml`, `season_cycle`), so the last
night of week 1 is held to the calendar, not to B7 (below, "Day six", the clock).

**What each chapter teaches, one new system at most per visit:** day four, a bad state that day three's comfort
already cured (the fog against the rack roof) and the woodshed; day five, Arcana (B6) and a pair arriving at once into
the town's mix; B7, combat by a story fight; day six, the hunt, gear, the pests' standing fights, a hurt and its cure.

**What changed from day three's outline, and why:**

1. **L2's gate.** Day three set n₃ (wolf sign) at a run count of the track, which typical reaches a day before B5. L2
   lands two game hours after L1 instead, so it falls in day four on every route and counts no runs (`decisions.md`,
   "No gate counts taps").
2. **The day's length.** Story days 5, 6 and 7 end on a clock with a floor in save time (`after_time`), not on a long
   build: day three already uses the cure-lane idiom for its floor, and a second long lay-and-wait would be samey.
   The play-driven gates beside them (B6's Scavenging level, B7's arrivals) are what a sharp setup moves.
3. **The stakes at the gap are cut** from day five. Nothing in week 1 raids the camp from the dark (lone wolves are the
   hunt, C3), so a stakes comfort could only name an upside it doesn't deliver until week 2. They go to week 2 with
   the packs.
4. **Arcana's first card makes dry wood from damp** (6 damp in, 2 dry out) rather than burning kindling for XP alone
   (BT6). Same rule (the stone's heat moved into the wood); it drinks the store that overflows first, and the fog
   chapter has just made dry wood the thing that's short.
5. **The spear's handing-over is a side beat**, not a chapter beat, so the B5-B7 chapters net -1 in turn (D-96; flat
   check below).

## Day four (B5 → B6): will the fire last?

The Still at its stillest. Fog comes down on morning 5 and doesn't lift. Everything that hangs to dry hangs wet, and
the stack goes soft. Wolf sign on the track. He and Lucy stack the woodshed together and something between them
eases. Night 5, the fire low on fog-wet wood; the player sits up with it, and B6.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| W1 | after night 4 | fog on morning 5; the hang dripping (or dry under the roof); the woodshed in view | will the wood stay dry enough to burn? | L1 (opens) |
| W2 | 3-9 h | on the track, a kill and prints of several, a ring of them round the camp at the scrub's edge | (dread beside the question) | L2; side SL8 |
| W3 | 3-9 h | the woodshed's second stage: he and Lucy stack it | will it be enough? | L3 (advances) |
| W4 | 3-9 h | the woodshed whole; dusk 5, the fire smoking on wet wood | will it last the night? | SL7; A21; B6 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| W1 (3-6 min) | reads L1; pays the **woodshed**'s first stage from full damp wood and stones; **chooses** the rack roof (if not built) or the woodshed first; re-tunes the track's hold against the woodshed | morning 5 (A20 + 1 h), L1 with it; `woodshed`; the chip `fogbound` only on a save without the rack roof, its cure already a card | fog over everything past the fire; the hang dripping or pale under the roof | l_morning_5, l_fog_1, l_fog_roofed or l_fog_open (L1), l_shed_1 |
| W2 (3-5 min) | reads L2; sets his share at Lucy's watch fire (SL8) against his woodcutting; pays a stage | L2 (L1 + 2 h); SL8 at L2 + 2 h | the far end of the track: the kill, the prints; then him at the watch fire | l_sign_1, l_sign_2 (L2), l_his_watch (SL8) |
| W3 (3-5 min) | reads L3; pays the woodshed's last stage; Camp 11 | L3 at `woodshed` stage 2; Camp 11 by the mix | the two of them at the stack | l_stack_1, l_stack_2 (L3), l_shed_2, l_camp_11 |
| W4 (3-6 min) | reads SL7; taps **Sit up with the fire** (A21) in night 5; reads B6 | SL7 at stage 3; dusk 5 (`t_dusk_5`: morning 5 + L5 h and save time ≥ 90 h); night 5 + 0.25 h; A21 (requires night 5); B6 | night grade; the fire low and smoking | l_shed_done (SL7), l_night_5, l_b6_1 to l_b6_3 |

### Cards and stores

| Card | Lane | Opened by | Cap / stages | Bar (s) | Takes | Pays |
|---|---|---|---|---|---|---|
| `woodshed` | hands | L1 (rides morning 5) | 3 stages | 2400 | 18 damp wood, 12 stones a stage | stage 2 shows L3; stage 3: "Dry wood holds 54, was 36"; scene: a frame, a roof, a full stack |
| `n2_watch` | his share in the town's mix | SL8 | none | 600 | 1 dry wood | nothing yet (week 2's packs read it) |
| `sit_up` (A21) | hands | B5 | 1 | 5 | requires night_5 ≥ 1 | B6 |

| Chip | Shows while | Cost (words) | Cure |
|---|---|---|---|
| `fogbound` | morning 5 unlocked, morning 6 not, and `rack_roof` stage 2 not done | "rack slower": rack −50% | `rack_roof`, a card since A22 |

The chip reads one count store, `fog_lift`, which `rack_roof`'s second completion (a trigger on its count) and
morning 6 each add one to: a chip reads one condition and must turn off at either. The cures gate learns to read a
cure through its card's count trigger, and gives a build a stage's time (plan item 14); the content stays as it is.

A save that built the rack roof never sees the chip: day three's comfort pays off in the scene and the lines (L1's two
sets, chosen by the roof's stage, never by text). A save that didn't sees the chip with its cure already a card.

| Store | Cap | Notes |
|---|---|---|
| night_5 | 20 | never unlocked; the night's clock, as `night_4` |

Standing: `night_5` (+20/h from `t_dusk_5`).

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| L1 | W1 | morning 5 (A20 + 1 h) | Fog comes down in the night and is there at morning, white to the scrub's edge, the fire a smear in it. Nothing dries. Under the rack roof the hang is pale; without it, it drips. The stack has gone soft at the edges. | down · none · dread · time · PC · opens C-promise-20 · th-survive middle |
| L2 | W2 | L1 + 2 h | Out along the track, in the fog: a kill half eaten, a small deer, and prints, more than two sets. Coming back the long way, the same prints in a ring round the camp at the scrub's edge, never nearer. | down · none · dread · none · PC · none · th-survive middle |
| L3 | W3 | `woodshed` stage 2 | He stacks the wood the way he was taught somewhere else, bark up. Lucy takes it down and stacks it bark down. He laughs. She doesn't, quite, and leaves the last row his way. | up · none · warm · none · N1, PC · advances C-promise-20 · th-town middle |
| B6 | W4 | A21 + Scavenging N + B5 | As `spine.md`: the fire dying in night 5 on fog-wet wood; the player's hand on the warm stone moves its heat into the kindling without knowing how; grey ash on the fingers that won't wash off; Arcana opens. That night Lucy sits on the far side of the fire. | as `beats.yaml` (down · yes_but · wonder · trust · PC, N1 · advances C-promise-1, th-magic start), and pays C-promise-20 |

**Mechanically, B6:** A21's completion plays B6's lines, unlocks the Arcana skill and `hand_on_stone`, moves the aim
on, and carries the chapter's end card. Lucy's place on the far side of the fire is a scene state from B6 (her figure
at the fire's far mark), which no later week-1 line moves.

### Side layer (day four)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL7 | comfort | th-survive | `woodshed` stage 3 | The stack under a roof, split ends out, dry at the heart. Lucy pulls a log from the middle to check and puts it back. | the bigger dry wood line invites a re-tune of the rack against the fire's draw |
| SL8 | arc (him, 3 of 3) | th-town | L2 + 2 game h | He takes a turn at Lucy's watch fire, the headless shaft across his knees, facing the track. | his share at the watch (`n2_watch`, dry wood) against his woodcutting |

## Day five (B6 → B7's eve): who else will come to the fire?

The day after B6. The stone does what the hand asked of it, again, and the player starts to learn it. By day, shapes on
the ridge where the cart stood, watching. A pair walk in out of the fog, drawn by the fire and the pot. Night 6, the
player banks the fire, and B7.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| X1 | 0 (B6's visit) | the hand on the stone, deliberately this time | what else does it do? | (Arcana's first card) |
| X2 | after night 5 | grey shapes on the ridge where the cart stood, watching, gone when Lucy looks | what are they waiting for? | M2 (opens); side SL9 |
| X3 | 3-9 h | two at the fire's edge out of the fog | will they stay, and whose hands make room? | O-pair |
| X4 | 3-9 h | they join; five at the fire | (who they are) | M1 (advances); side SL10, SL11 |
| X5 | 3-9 h | night 6, banking the fire for five | (B7) | A29 → B7 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| X1 (2-4 min, the rest of B6's visit) | taps **Hand on the stone** for the first time (glows: the first of a new skill); adds it to the mix and moves the damp wood hold to it, the track's hold to stones (the page's hold, plan item 13) | B6: Arcana, `hand_on_stone`, the mix offer | night grade; the player's hand on the stone, steam off the wood | l_stone_first |
| X2 (3-5 min) | reads M2; reads SL9 (Arcana 2) and **re-tunes** the rack against the stone; pays the last day-four stage | morning 6 (A21 + 1 h); M2 at morning 6 + 2 h; SL9 at Arcana 2 | day grade, fog thinning to haze; the ridge | l_morning_6, l_ridge_1, l_ridge_2 (M2), l_arcana_2 (SL9) |
| X3 (3-6 min) | answers **O-pair**; builds their bay or lets her build it | O-pair at morning 6 (often while away); the arrival kind's answer rule answers it if the player set one after O-stay (plan items 10-12) | two figures at the fire's edge, one sitting | l_pair_1, l_pair_2, l_bay2_go, l_bay2_hers |
| X4 (3-6 min) | reads M1; **splits** the town's mix across four; reads SL10 and sets her share at the bed (or not); reads SL11 and moves Lucy's share off the watch (or not); pays **hearth stones**' first stage (Arcana 4) | M1 at the bay done (arrivals 4); SL10 at M1 + 1 h; SL11 at M1 + 3 h; `hearth_stones` at Arcana 4 | five at the fire; a second bay; turned ground at the stone's edge | l_join2_1, l_join2_2 (M1), l_seed (SL10), l_old_watch (SL11), l_stones_1 |
| X5 (3-5 min) | taps **Bank the fire** (A29) in night 6; reads B7 | dusk 6 (`t_dusk_6`: morning 6 + L6 h and save time ≥ 110 h); night 6 + 0.25 h; A29 (requires night 6); B7 (arrivals 3, B6, A29) | night grade | l_night_6, B7's lines (b7.toml) |

### Arcana (fit pass)

**What it is:** the player moving the stone's heat into things by hand. **Instance of:** a skill with cards (Cards,
Skills, the pacing curve) whose level pays aim at other lanes (Modifiers): "skills feed each other, visibly". The
Spells row (rules combined by an interpreter) is not needed until Spellcraft opens at B15; nothing in week 1 combines
anything. **No engine work.**

| Card | Lane | Opened by | Cap | Bar (s) | Takes | Makes | Skill |
|---|---|---|---|---|---|---|---|
| `hand_on_stone` | hands | B6 | none | 20 | 6 damp wood | 2 dry wood | Arcana |
| `hearth_stones` | hands | Arcana 4 | 3 stages | 1800 | 12 stones, 4 clay a stage | stage 3: "Stew 4 a pot, was 3" | Arcana |

Held against damp wood at 12 by the page's hold, so `hand_on_stone` drinks what the hands make past that, as the track
did in day three. A mix holds one store by one card only (engine `mixes.Hold`; plan, "Gaps the chapter files found",
G2), so when the stone card joins, the track's hold moves to stones, its other overflowing supply, and its damp wood
is drawn unheld at its stones-held rate. The two still compete for damp wood by
their shares, which cap each one's draw: that is the share to set. If stones then fail the cap-loss check, the track
holds roots instead. It reads as heat moved, never made: the wood
steams, the stone stays as it was (canon: the camp stone never goes cold, C-beat-15's contrast later). Rule 2 (ash)
is not taught: the grey on the fingers is B6's fact and no card's.

**Levels** (week 1 reaches Arcana 6-9 on typical; simulator):

| Level | Pays |
|---|---|
| 2 | "Rack +10%" (the drying wall over bare stone): SL9 |
| 3 | speed |
| 4 | `hearth_stones` opens (hot stones from the camp stone into the pot) |
| 5 | find: kindling left on the stone overnight is dry by morning (dry wood +12) |
| 6 | "Smoking +25%" (`smoke_catch`'s rate on the rack) |
| 7-8 | speed |
| 9 | (none yet: week 2's; listed so the check sees the gap) |

### The third arrival (fit pass)

**What it is:** two people who walked together arriving at once. **Instance of:** the arrival idiom (BT4, D-100):
an offer whose answers build a bay on either lane, a join on completion. **Fits into:** Offers (O-pair and O-stay both
of kind `arrival`, roles `room` for Make room and `theirs` for the other answer, so the kind's answer rule the player
sets after O-stay answers O-pair on its own: plan items 10-12; until those land, O-pair waits for a visit), Cards (the bay), Triggers (the join,
with two `joins` in one outcome), Mixes (the town's mix gains two shares), Stores (arrivals +2, to 4; B7 reads ≥ 3).

| Offer | Shown | Answers | Each answer | Expires |
|---|---|---|---|---|
| O-pair | morning 6 (`t_pair_offer`) | **Make room** / **Let her build** (labels to the voice pass) | Make room: `make_bay2` (A25) on the hands. Let her build: her lane starts at once, `n3_build_bay` (A26), equal real time at her base pace. Same stores: 18 damp wood (the store's whole cap; 24 is more than a save holds), 18 stones | never |

`make_bay2` bar 10 800 s (measured: at 21 600 s the bay held the hearth stones' first stage behind it past a visit, and the hands' body chips ran uncured under it). On completion both join; arrivals +2.

**Who they are** (light tier, souls from the save's seed; stand-ins for when Claude is off; names from
`names.jsonl`'s pool by the seed, lines say "she" and "he" or "the old man" until M1 gives the names):

- **n3**, a woman of thirty or so, carrying a sack of seed she won't open in company. She works at a plain pace, as
  Lucy does. Her arc is three moments: SL10, SL13 and one in week 2.
- **n4**, an old man with a leg that doesn't bend, who walked with her from somewhere on the road. He can sit a watch
  and mend; he doesn't gather. His one moment in week 1 is SL11.
- They met on the road. Whoever each of them walked with first did not arrive, and no line says who or how
  ("Groups arrive broken").

n4 is the light-tier townsperson week 2 may let die (townsfolk with small arcs of their own are fair game). That
is week 2's decision and not made here; nothing in week 1 is written to need him alive or dead, and no line promises
either. If week 2 takes him, it is decided as of his arrival (`decisions.md`: never the player's fault), so no week-1
choice may look as if it would have saved him: none of SL11's answers, and no poultice, reads on him.

Their cards: `n3_forage`, `n3_gather`, `n3_dig_bed` (SL10) at base rate; `n4_watch` (1 dry wood / 600 s, as
`n1_watch`), `n4_mend` (he keeps the hunt's gear sound: while it runs, +25% on the hands' side at his share of
it, declared in `b7.toml` with the side; it makes nothing and costs nothing). Default split on joining: she forages at her whole share, he sits the watch.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| M2 | X2 | morning 6 + 2 h | The haze thins by midday. On the ridge, where the cart stood, grey shapes sitting in a row, facing the camp. When Lucy looks up they are gone. | down · none · dread · none · PC, N1 · opens C-promise-21 · th-survive middle |
| O-pair | X3 | morning 6 | Two at the fire's edge out of the haze: a woman with a sack over her shoulder and an old man on her arm, his leg straight. She asks if the fire is theirs to share. | (an offer) · th-town middle |
| M1 | X4 | the second bay done (arrivals 4) | They take their places. The old man lowers himself onto the stool Lucy brings without looking at it. The woman gives both names. Five at the fire; the pot goes round twice and comes back light. | up · yes_but · warm · stores · PC, N1 · advances C-promise-21 · th-town middle |
| B7 | X5 | arrivals 3, B6, A29 | `b7.toml`, below | as `beats.yaml`, and pays C-promise-21 |

The stool is day one's; its short leg is canon (the cellar's stool at B12 is another). M1's line may show it rock, and
must never connect the two.

### Side layer (day five)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL9 | find | th-magic | Arcana 2 | Wood laid on the drying wall where the stone shows through the ash dries first. | the faster rack invites a re-tune: the stone card's share against the rack's |
| SL10 | arc (n3, 1 of 3) | th-town | M1 + 1 game h | She turns a strip of ground at the stone's edge with a flat stone, edges it with stones, and lays seed out on a cloth beside it in rows, and ties it up again unplanted. | her share at the bed (`n3_dig_bed`: 6 stones a stage, 3 stages; it builds turned ground and nothing else) against her foraging |
| SL11 | arc (n4, his one moment) | th-survive | M1 + 3 game h | The old man settles at Lucy's watch fire with his leg out straight and feeds it. Lucy stands there a while, then goes back to the roots. | Lucy's share can come off the watch to gathering, his on it; or both at the fire |

## B7 (`b7.toml`): wolves at the edge of the firelight

Combat-plan item 8's content, settled here from C1-C9's answers. B7 is the last spine beat of week 1.

**The moment.** A29 ("Bank the fire") in night 6 plays B7's lines: wolves at the edge of the firelight, eyes, more than
can be counted; they don't come in. B7's outcome does three things at once:

1. **Starts the strip** (C2): `b7_strip`, a standing drain on the rack's hang, `catch` and `smoked` only, sized to empty
   both inside the clock, pausing at empty (the visitor's idiom). Clock store `b7_clock`, 15 game s. Never another
   store.
2. **Opens `b7_stand`** with B7 (`t_stand_open`, on the feature `wolves`), so it is tapped in B7's visit; its bar
   (20 s, and the hands are only ever slowed) outlasts the strip's clock, so the rack is bare whenever it finishes (A27, "Drive them off", glows: the one next step), a one-off
   on the hands, bar 20 s, no FightDef (a beat never rolls). Its completion plays the fight's lines: a plain fight that goes fine, one wolf turned
   with a burning brand, the rest gone into the dark; and, while it went, the rack stripped behind them. Its outcome
   unlocks the `combat` feature and everything below.
3. **Moves the aim** to aim_keep.

If the player leaves before tapping `b7_stand`, the strip still runs to its clock (the hang is gone on return either
way) and the card waits glowing: the story fight is a presence step like A20 and A21, and nothing is lost by the
wait. B7 · cost stores: the hang, and nothing else.

### Combat in week 1

| Id | Kind | Fight (side vs threat) | Bar / rate | Takes | Makes (won share) | On a loss | Opened by |
|---|---|---|---|---|---|---|---|
| `hunt_wolf` | card, hands, uncapped | `hands` vs `lone_wolf` | 1200 s | 1 smoked (food carried) | 3 catch, 1 pelt | `hurt` +1; tally `hunt_lost` | `combat` |
| `make_spear` | card, hands, cap 1 | | 600 s | 6 scrap, 4 dry wood | `hands` side +150% | | `combat` |
| `poultice` | card, hands, uncapped | | 60 s | 1 hurt, 2 clay, 6 roots | (heals one hurt) | | `combat` (unready until hurt) |
| `rats` | standing fight | `larder` vs `ashrats` | 1 a game h | | | 2 roots; tallies `rats_fought`, `rats_lost` | `combat` |
| `crows` | standing fight | `rack` vs `crows` | 1 a game h | | | 1 smoked; tallies `crows_fought`, `crows_lost` | `combat` |
| `heal` | standing | | | hurt −1 per 4 game h | | | `combat` |

**Sides and threats** (starting values; the simulator sets them against the odds targets in the numbers file):

| Strength | Base | Entries |
|---|---|---|
| side `hands` | 8 | spear +150%; Melee 2 +10%, Melee 4 +10%; chip `hurt` −25% |
| side `larder` | 4 | `larder_floor` stage 3 +300% |
| side `rack` | 4 | `rack_roof` stage 2 +300% |
| threat `lone_wolf` | 4 | (no ramp step in week 1) |
| threats `ashrats`, `crows` | 4 each | (no ramp step in week 1) |

So a hunt without the spear loses about one in three, with it about one in six; a pest against an unbuilt cure loses
one in two, against a built one about one in five. Most routes built both cures in day three (C4), so the pests show
mostly losing from their first hour and preparation is visible at once. The hunt's odds read "unknown" until the first
hunt (`decisions.md`, "Blind until learned"; the plan's new item).

**Chip `hurt`** (hurt ≥ 1): "hands slower": hands −15% and side `hands` −25%; cure in reach: `poultice` (clay from
`dig_clay`, roots), and it heals by itself. Never a death in week 1 (C5).

**Melee** opens with `combat`; trained by `hunt_wolf`. Levels: 2 "Hunting side +10%"; 3 find (below); 4 "Hunting side
+10%"; 5 speed.

**The ramp's clock** (C7): `r1_clock`, a never-drawn store filled at 1 an hour from `combat`. Week 1 has no ramp step;
week 2's first step (packs, days 8-14 of the region) reads it.

**Stores:** `pelt` (cap 12, so a day away after the bedding loses under half the hunt's pelts), `hurt` (cap 3), the tallies (cap a year of the fastest rate), `b7_clock`, `r1_clock`.

### Lucy's watch fire after B7

Day three left `n1_watch` making "nothing yet (from B7, an entry on the camp's side)". In week 1 nothing comes at the
camp from the dark (C4: lone wolves are the hunt), so the watch fires stay "nothing yet" until week 2's packs, which
read `n1_watch`, `n2_watch` and `n4_watch` as entries on a gap side. Changed from day three's note because an entry with
no fight to raise would be a number with nothing behind it.

## Day six (B7 → night 7): can the camp keep what it has?

The morning after: the rack bare, everyone counting. The spear made from his shaft and the ploughshare's iron. The
first hunt: a lone wolf, starving, ribs showing. Rats in the roots and crows on the roof's ridge, losing more than
they win where the cures stand. The rack hung again by night 7, the Still's last night.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| Y1 | 0 (B7's visit) | the rack bare; the hunt, the spear, the pests in the ledger | what can be put back? | (combat) |
| Y2 | after night 6 | morning 7; the spear made (if not in Y1) | (he gave the shaft) | side SL12 |
| Y3 | 3-9 h | the first hunt home: a wolf as hungry as anything in the Hollow | is there enough here for anything? | G1 (opens) |
| Y4-Y5 | 3-9 h each | pelts; a bed of turned ground covered or not; bedding in the bays | (the rack filling) | side SL13, SL14 |
| Y6 | 0-9 h | night 7: the rack hung again, five at the fire | (week 2) | G2 (pays) |

Sharp reaches B7 about fifteen hours before typical and night 7 at the same calendar hour, so sharp gets one or two
more visits here, filled by Melee and Arcana levels, the comforts and the hunt's gear (numbers file, "Day six").

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| Y1 (3-6 min, the rest of B7's visit) | taps **Drive them off** (A27); meets the hunt (odds unknown) and the spear; **chooses** spear first (scrap, dry wood) or a first hunt bare-handed | `combat` at A27's completion: `hunt_wolf`, `make_spear`, `poultice` (unready), Melee, `rats`, `crows` in the ledger | night grade, the rack bare | B7's lines, l_stand_1, l_stand_2, l_combat_first |
| Y2 (3-5 min) | pays the spear if not yet; reads SL12; puts the hunt in the mix against smoked; re-hangs the rack (`smoke_catch` on what the hunt brings) | morning 7 (A27 + 1 h); SL12 at `make_spear` done | day grade; the rack empty | l_morning_7, l_spear (SL12), l_rats_first, l_crows_first |
| Y3 (3-5 min) | reads G1; spends the first pelts on **pelt bedding** or holds one; heals a hurt by poultice if any | G1 at `hunt_wolf`'s first finish; `pelt_bedding` with it (one moment) | a pelt pegged out by the rack | l_hunt_1, l_hunt_2 (G1), l_bedding_1 |
| Y4 (3-5 min) | answers **o_pelt** (SL13); a Melee or Arcana level | SL13 at G1 + 2 h and `n3_dig_bed` stage 3 (or G1 + 6 h if the bed was never dug) | turned ground at the stone's edge | l_pelt_ask, l_pelt_given, l_pelt_kept (SL13) |
| Y5 (3-5 min) | reads SL14; re-tunes; Camp 12's marker held | SL14 at `pelt_bedding` stage 6 | pelts on the bays' floors | l_bedding_done (SL14), find lines |
| Y6 (3-5 min) | reads G2; Camp 12 lifted | dusk 7 (`t_dusk_7`: save time ≥ 162 h and morning 7 + 6 h); night 7 + 0.25 h; G2 at night 7, smoked ≥ 18 and a first hunt (its card on the cards from A27) | night grade; the rack hung, five at the fire, Lucy on the far side | l_night_7, l_g2_1 to l_g2_3, l_camp_12 |

### Cards

| Card | Lane | Opened by | Stages | Bar (s) | Takes | Pays |
|---|---|---|---|---|---|---|
| `pelt_bedding` | hands | G1 (`hunt_wolf`'s first finish) | 6 | 1800 | 1 pelt, 6 damp wood a stage | stage 6: "Rest +20%"; scene: pelts on the bays' floors |

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| G1 | Y3 | `hunt_wolf`'s first finish, won or lost (a fight pays by the share won, so a pelt can take more than one hunt; no gate counts taps) | The first wolf the hunt brings back is alone and starving, ribs like a rack of its own, its teeth worn. It comes back as meat and a pelt. Everything out there is as hungry as the camp. | down · yes_but · grim · time · PC · opens C-promise-22 · th-survive middle |
| G2 | Y6 | night 7 and smoked ≥ 18 | Night 7, the Still's last. The rack is hung again, fuller than before. Five at the fire, Lucy still on the far side of it. Nothing at the edge of the light tonight. The air has changed: for the first time in a week there is a little wind. | up · yes · warm · none · PC, N1 · pays C-promise-22 · th-survive middle |

G2's wind is the Still ending, the calendar's fact; it says nothing of what the Drift brings (B8's). Lucy stays on the
far side: B6's cost is not paid back in week 1.

### Side layer (day six)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL12 | thread | th-town | `make_spear` done | He hands over the shaft he has carried since he came. The ploughshare's iron, beaten flat on the stone and bound on, is its head. He holds it once and gives it back. | the spend is the spear itself (scrap banked all week); the hunt's odds change on screen |
| SL13 | arc (n3, 2 of 3) | th-town | G1 + 2 game h and `n3_dig_bed` stage 3 (or G1 + 6 h without it) | She asks for a pelt to lay over the turned ground at night. | `o_pelt`, a small offer: **give it** (pelt −1) / **keep it** (nothing); whatever week 2 finds in that ground does not depend on the answer; the answer shows as a scene state and a line |
| SL14 | comfort | th-survive | `pelt_bedding` stage 6 | Pelts on the floors of the bays; the old man sleeps through the night for the first time. | the faster rest invites a re-tune toward the hunt or the stone |

### Day six's clock

Story day 7 ends on the calendar: dusk 7 at save time 162 h (the calendar's day 7, evening), but never sooner than six
game hours after morning 7, so a late route still has a day, unless that would pass 165 h: from then dusk 7 falls as soon
as morning 7 has come (`t_dusk_7_late`), so night 7 is before the turn on every route. Night 7 is the Still's last; week 2's B8 is the season's
turn at 168 h. A route that reaches night 7 with the rack not yet at 18 smoked gets G2 when it is: G2 is the last
week-1 beat, and nothing of week 2 waits on it.

## Levels and finds (week 1's back half)

Ranges are expectations for typical by night 7 (simulator). "At least every third level pays a thing" holds in each.

A find goes only on a level whose row pays speed alone, never on one that already pays a find: Foraging 12 and
Scavenging 18 and 21 already pay day two's finds. As day three's finds do, each is a new trigger beside the speed-up
(which stays), restates the level's row in `skill_levels` with a pays key naming both the find and the speed-up, and
requires feature `morning_5`, so a save already past the level gets it inside the back half. All go in
`day_four.toml` but Melee's (`b7.toml`). If day four's report shows typical already past a level at morning 5, the
find moves to the next speed-only level in the range; with none left, it is cut.

| Skill | Level | Pays |
|---|---|---|
| Foraging (10-12) | 11 *added* (12 has a find) | a bank of ashroot the fog kept soft (roots +12) |
| Scavenging (18-22) | 19 *added* (18 has a find, and is B6's level) | a pot hook and chain in the ditch by the track (scrap +2) |
| | 20 *added* (21 has a find) | an iron hoop off a barrel, half under the ash (scrap +4) |
| Woodcutting (19-22) | 20 *added*, beside its speed-up | a birch dead on its feet, dry right through (dry wood +12) |
| Cooking (5-8) | 6 *added*, beside its speed-up | a stew that keeps: the pot thicker by morning (stew +3) |
| Arcana (6-9) | as the Arcana table | |
| Melee (3-5) | 3 *added* | a wolf dead in the thorn, older than the hunt's (pelt +1) |

No find names wolves at the camp's edge, the stone's heat in any way past B5's facts, or anything of week 2.

## The Camp

| Level | At (camp items) | Pays |
|---|---|---|
| 11 | 600 000 | "Stew holds 18, was 12" |
| 12 | 900 000, held ("?"); cap 899 999 until lifted | lifted by G2: "Smoked holds 36, was 27"; the marker is a goal on screen through day six |

## Stated aims

| Aim | Starts at | Intent |
|---|---|---|
| aim_warm (day three's) | feature warm_ground (B5) | ends at L1 |
| aim_dry | feature fog_5 (L1) | keep the fire through the fog |
| aim_stone | feature arcana (B6) | learn what the stone will do |
| aim_pair | O-pair shown | room for two more |
| aim_keep | feature wolves (B7) | keep what the camp has |
| (week 2's first) | B8 | aim_keep stands until it |

## The flat check, authored order

Spine and chapter beats from B5, in landing order on typical: B5 up, L1 down, L2 down, L3 up, B6 down, M2 down, M1 up,
B7 down, G1 down, G2 up. Never three turns the same. Outcomes: B5 yes, B6 yes_but, M1 yes_but, B7 yes_but, G1 yes_but,
G2 yes (no run of yes; week 1's failure is day three's K4 no). Registers: wonder, dread, dread, warm, wonder, dread,
warm, grim, grim, warm (never four the same). Costs: time, none, none, trust, none, stores, stores, time, none.

**Net:** the chapter beats here are L1 −, L2 −, L3 +, M2 −, M1 +, G1 −, G2 + = −1, as D-96 asks of the B5-B7
chapters; with day three's −1, week 1's `week_net_up` settles at 0. The near promises: C-promise-20 opened W1,
advanced W3, paid W4; C-promise-21 opened X2, advanced X4, paid by B7 (X5); C-promise-22 opened Y3, paid Y6.

## Away from the screen

- **Every planned moment plays in full on return:** morning 5 and L1, L2, morning 6 and M2, O-pair, M1, morning 7, SL12
  to SL14 and most stage completions land while away on typical; each is revealed in order, one at a time.
- **Per absence, at most two unlocks:** night 4 → W1 brings morning 5 with L1 (one moment) and the woodshed with it;
  night 5 → X2 brings morning 6 and M2; night 6 → Y2 brings morning 7 and, if the spear was paid, SL12.
- **The 2 AM test:** every sink is on screen unready before it can be afforded: the woodshed at L1 (the stores are full,
  so it is affordable at once, which is the point); `hearth_stones` on the cards with B6, needing Arcana 4, which the level's marker names;
  `pelt_bedding` at the first pelt; `poultice` with `combat`, unready until a hurt. The fights are flows (invariant
  81), so a babysitter's hunts and the whenever player's come out the same.
- **Rebased saves:** a save past B5 when day four ships gets morning 5 at the rebase instant if night 4 is over; past
  B6, `hand_on_stone` with full stores; past B7 (impossible before `b7.toml`), nothing.

## Art

- **Grades:** night 5, 6 and 7 (each until its morning; night 7 until week 2's B8); fog over the whole scene on story
  day 5 (cool, world layer, lifting to haze at morning 6).
- **World layers (cool):** the kill and prints at the track's far end (L2); the ring of prints at the scrub's edge (L2,
  day layers only until B7); grey shapes on the ridge (M2, day 6 only, a feature that clears with the haze);
  eyes at the edge of the firelight (B7, night 6 only).
- **Player-made (warm):** the woodshed (3 states); the second bay; turned ground at the stone's edge (3 states, and a
  pelt over it at night if given); hearth stones round the pot (3 states); the rack bare (B7 to the first re-hang) and
  hung (the existing states); pelts pegged by the rack; pelts on the bays' floors (3 states); the spear leaning at the
  lean-to.
- **Figures** (picked from the packs by `sprite-catalog`, drawn only if the kit lacks them): the player's hand on the
  stone (`running:hand_on_stone`, a crouch at the stone); the woman with a sack; the old man with a stick, seated by
  default; him at the watch fire with a staff (the pack figure from day three, the shaft); Lucy at the fire's far mark
  from B6; the player with a spear (`running:hunt_wolf`, off-scene: a pose at the gap); a lean wolf (B7 and the hunt's
  carry-back); a fat grey rat at the larder; crows on the roof's ridge once `rack_roof` is built, in the hang if not
  (C9).
- **Stages:** 32_fog, 33_sign, 34_stone_hand, 35_ridge, 36_five, 37_wolves, 38_bare_rack, 39_hunt, 40_night_seven.

## Proposed canon (tentative until the lead confirms)

- C-promise-20: day four's near question, *will the fire last?*, opened by L1, advanced by L3, paid by B6.
- C-promise-21: day five's near question, *who else will come to the fire?*, opened by M2, advanced by M1, paid by B7.
- C-promise-22: day six's near question, *can the camp keep what it has?*, opened by G1, paid by G2.
- C-beat-94 (L1), C-beat-95 (L2), C-beat-96 (L3), C-beat-97 (M2), C-beat-98 (O-pair), C-beat-99 (M1), C-beat-100 (B7's
  shape: the strip takes the hang only, a story fight driven off with a brand, combat opens at its end), C-beat-101
  (G1), C-beat-102 (G2), each as its row above.
- The third arrival is a pair who met on the road (a woman with seed, an old man who can't gather); light tier.

Decisions to record: D-103 (L2's B5-relative gate), D-104 (story days 5-7 end on a clock with a save-time floor),
D-105 (Arcana's first card: 6 damp wood to 2 dry wood, held against damp wood), D-106 (the stakes go to week 2),
D-107 (B7 as A29's lines, the strip, and a one-off story fight that opens combat), D-108 (the watch fires make nothing
until week 2's packs), D-109 (the spear's handing-over is a side beat; chapter net −1), D-110 (week 1 ends at night 7,
dusk on the calendar's 162 h).

## For the owner

One question, spoiler-free:

1. **Growing food.** A small character moment late in week 1 can point toward someone in camp wanting to grow food.
   Is growing crops something you want in the game at some point? If yes, the moment points at it, and a later week
   builds on it; if no, the same moment points at something else and nothing in the design depends on it.

## Open (content side)

1. **L5, L6 and the floors** (the day lengths and their save-time floors) are the simulator's to set so typical lands
   mid-band (numbers file). Never lengthen a hands bar to move a band.
2. **B6's Scavenging level** (20 in `beats.yaml`) is a placeholder: if typical can't reach it by about 100 h, lower it
   to what typical reaches about twelve hours after B5.
3. **Dry wood overflow.** Settled by the card's input: 18 damp wood to 1 dry wood a run, Arcana's XP raised to match
   (measured: at 6 to 2 the stone made about 60 dry wood an hour against under 10 drunk).
4. **n4's week 2.** Whether he dies in week 2 is week 2's design pass, under the rules above.
5. **Her arc's third moment** waits on the For the owner answer.
