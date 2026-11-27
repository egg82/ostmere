# Week four: from the Still's turn to the end of story day 28

Spoilers: this file is under `content/` and never shown to the owner. It picks up where `week-three.md` ends (T13, night
21) and runs from the Still's turn at save time 504 h to the end of story day 28, the Still's last night, in four
chapters. Numbers are targets unless `week-four-numbers.md` marks them measured; lines are written from
`week-four-lines-brief.md`; engineering's side is `docs/design/week-four-plan.md` (spoiler-free). New canon is listed at
the end as proposals (tentative until the lead confirms), new decisions as D-153 to D-170.

Binding, carried: nothing is lost *because* the player was away (D-59); every return has something to spend and
something to decide (D-94); a side beat never gates a spine or chapter beat (D-97); watching earns nothing extra (the
2 AM test, held to players given the same rules and mixes the game has taught); D-119 (a staged hands build is run by one
order card; a card that can open while the player is away opens onto a full store or a finite pool); at most two
moments per absence. New and binding this week, from the owner: **no finite resource can lock a careless player out of
content or progress** ("Finite pools", below).

**Beat ids.** Week four's letter is **I** (D-153): C is canon's and combat's questions, D is the decision log's, V is the
simulator's visit numbers, and the rest are spent. I collides only with the mysteries' "item lore" column. Beats run
I1 to I13; visits are named `22a`, `23b` and so on, by the story day they start in.

## What week four is

The Still: no wind, the ash hanging in the air, fog lying in the low ground, and every sound carrying the length of the
valley. Week three made the camp a town and cut the road out; week four walks it. Past the ridge is the Ashwood, a dead
grey forest gone to fungus, where dead elk are walked toward warm ground by what grows in them. A stranger walks home
behind the player and will not come inside. Something tears up the trips' cache. The player goes after it in the fog
and dies, and wakes at the warm stone, and nobody in town thinks much of it, except one newcomer who walks in from the
seams laying hands on stones, and who asks for the names of the dead.

What the player feels, in order: unease (the stillness), wonder (the forest), the wrongness of meat nobody will eat,
curiosity (someone out there), tenderness (the stranger who won't come in), annoyance and then purpose (the cache), the
shock of the death and the joke of the return, the shrug of a town that has seen it before, and a quiet close: names
said into still air, and one nobody has.

## The four chapters

| Chapter (file) | Beat span | Story time | Near question (proposed canon) | Typical span |
|---|---|---|---|---|
| Day twenty-two (`day_twenty_two.toml`) | I1 → B19 | days 22-23 | C-promise-33, *who is out in the fog?* opened I3, advanced I4, paid B19 | 504-536 h |
| Day twenty-three (`day_twenty_three.toml`) | B19 → B20 ★ | days 23-25 | C-promise-34, *what is tearing up the cache?* opened I6, advanced I7, paid B20 | 536-580 h |
| Day twenty-five (`day_twenty_five.toml`) | B20 → B21 | days 25-27 | C-promise-35, *does anyone think it strange?* opened I8, advanced I9 and I10, paid B21 | 580-630 h |
| Day twenty-seven (`day_twenty_seven.toml`) | B21 → night 28 | days 27-28 | C-promise-36, *will anyone know the first name?* opened I11, advanced I12, paid I13 | 630-672 h |

The calendar holds both ends: the Still's turn is a clock beat at 504 h and the Drift's turn (week five) at 672 h, so
story days 22 to 28 are calendar days 22 to 28. Between, B18 to B21 are play-driven and held to their days by the
season's clock (`still_clock`, hours since the turn), not by save-time floors: every sharp floor this week (428 to 528 h)
falls before the turn or before the clock it would guard.

**What each chapter teaches, one new system at most per visit:** day twenty-two, the second season's chore with no
ready-made rule (the chip and its hint; the rule is the player's), then the first expeditions (a trip held in the mix,
its finds, Wayfinding); day twenty-three, a newcomer's first task by the kind's rule again, the long goal out in the
wood (the logging post), Lucy's jobs back, and a second working; day twenty-five, the player's death and what a death
means from here (a fight whose loss is told as dying); day twenty-seven, the town's dead named, and the week's night.

**What changed from `spine.md` and `beats.yaml`, and why:**

1. **B18's gate gains the first walk into the Ashwood** (D-156). On R2 open alone it would land at B17's instant, in
   week three. The walk (`walk_ashwood`) is shown at T13, unready with its countdown to the turn, so every route can
   queue it before the overnight absence; B18 lands at its first finish.
2. **B19's gate is six walks, I4 and the season's clock** (D-157), not "R2 2 days". `r2_clock` reaches 48 at B17 + 48 h,
   about 508 h on typical and 504 h on sharp (measured: B17 at 460.2 and 456.1), which is day 22 and before B18 could
   ask anything. N3 comes home with the player, so the walks are what bring them.
3. **B20 is a chosen step** (D-159). Its spine gate, three R2 expeditions and B19, is met by day 23. The death is a glowing
   one-off (A39, `go_wallow`) that Lucy's ask introduces and that waits for the player's tap, shown at night 24 and ready
   at the season's hour 72 (576 h, day 25). Tapping it is the yes.
4. **B21's gate gains B20 and a clock** (D-163): N4 is the one who looks strangely at the player about B20, so B20 must be
   behind them, and they walk in eight hours after the twenty-fifth arrival sits down (B16's shape). The arrivals come
   from the table's meals, as week three's did, so O-sun's light pays.
5. **The arrivals' count is capped at 20** (measured): the turn doubles its cap (D-164), since week four takes it to 26.
6. **The logging post (P4) is week four's long goal** (D-165): shown at I6, built across days 24 to 28, no beams in it.
   Its last stage is B22's; B22 also waits on the Drift's turn (672 h), so it is always week five's first spine beat.
7. **No progress gate reads a finite pool** (D-169). Every store a gate or a required build takes has a maker that never
   runs out; the season's pools feed only optional things.
8. **The Still has no day-night cycle**, as the Drift and the Clear: one flat grade by day, two story nights (night 24,
   SL33's sound in the dark; night 28, I13).
9. **The Clear's chores end at the turn** (D-154; D-126 applies unchanged): the rules tapping `cover_beds`,
   `n3_cover_beds` and `warm_beds` are retired, and an hour's thaw empties the rime.
10. **The Still's chore has no order card** (D-155): it arrives with its chip's hint dot, and the rule is the player's to
    write (`docs/design/choice-not-protection.md`, row 43, decided; issue #37 (g)). The shipped order cards of the Drift's
    and the Clear's chores stay until those seasons are next written.

## Decided here: what week three left to week four

**1. The Clear's chore rule at the Still's turn (D-154).** D-126 applies as written. The turn's outcome carries
`retire_orders = ["cover_beds", "n3_cover_beds", "warm_beds"]`: each is the cure of `frosted`, whose store (`rime`)
only the season's `frost` standing makes, so the loader's retire check takes them. Rime stands at 7.8 at 504 h on
typical and whenever (measured), under the chip's 12, but nothing would ever drain it again; the turn adds
`thaw_left` 1 and opens `thaw`, a standing that drains 24 rime an hour on its own pool (`roof_wind`'s idiom), so it is
gone within the hour and the frost's chip cannot show for three weeks. The reap rule (`n3_reap`) is not a chore cure and
stays: ripe sits at 1.3 with the beds stopped (`grow_left` 2.5 on typical, measured), so the rule is passed over until
the Clear comes round, and D-125 hands its share on. `warm_beds` stays a card the player owns; with no rime it has
nothing to cure, which is why the Still brings Spellcraft a second working (SL32).

**2. B18's floor (D-156).** The floor is structural, not a clock: B18 waits on the first walk, and the walk cannot run
before the turn (it requires `clear_clock` ≥ 168, the season's 504 h, the clock A38 already read). On sharp it lands
within an hour or two of the turn; on typical a few hours in; band 504-528.

**3. The starer's thread (D-166): it rests through week four, on purpose.** He is B16's and the snares'. B19 brings a
stranger in from the forest edge two days after B18, and anything of his in the Ashwood before that (a knot, a print, a
snare) would make the player read N3 as him. N3 is not from town 3, and that mistake would cost B42 its turn. His next
trace is Q2's decades-old snare wire (`mysteries.md`), any time from week six, then B34 and B36.

**4. O-sun's answers, into week four.** Both are kept live, as week three asked:

| Answer (typical, measured: light) | What it does in week four |
|---|---|
| A light in the hall door (meals ×1.25) | Every week-four arrival waits on a `meals` threshold (175, 230, 285), so the light brings the fiddler, the walkers and the widowers sooner, and N4 with them (B21). The groups raise the table's bill, which the cellar would have banked against. |
| Fill the cellar (smoked's cap ×1.5) | Smoked is taken three ways this week: the table (4 an hour at the turn, +1 a group), every walk's supplies (2), and the boar hunt's (2). A deeper larder keeps the table fed through long absences while the walks run, so meals never stop and the arrivals never stall. |

Neither covers the other: the light grows the bill, the cellar carries it. The measured route (typical, the light)
holds smoked at 69.3 of 72 at 504 h; the simulator measures the cellar route too.

**5. `r2_open`, `r2_clock`.** `r2_open` is the walk's opening condition beside the turn. `r2_clock` carries R2's own
ramp, its first content use (D-138 holds: a clock store, no region state): at `r2_clock` ≥ 144 (six days in R2, about
604 h on typical) the ash-boar's strength steps +25% ("boar sounders", `regions.md`, days 6-12).

**6. "After week 3" (`docs/design/week-three-plan.md`).** The turn retires week three's chore rules (item 3 applies
unchanged) and refills nothing of week three's pools: the beds, the deer and the ruin's beams stay spent, and D-125 hands
their shares on. B18 opens week four with the floor above. The map gains a place per region reached: four this week.

**7. Stores with no sink at night 21** (measured, 504 h): cleared stands at 50.9 of 72 on typical and 72 of 72 on
whenever (the road is done and nothing takes it), cord at 12 of 12, stones at 18 of 18, barley at 36 of 36. The post
takes cleared, cord, stones and stakes; barley drains into `barley_stew` once nothing makes it.

## Finite pools: nothing progress needs can run out

Owner direction (binding): "any finite resources, if something requires them, we need to make sure players can't
softlock themselves out of content or progress." The engine half (a job never spends inputs on an outcome that would be
lost entirely to caps) and the content check (every finite store covers every consumer progress requires, and no
optional consumer can spend what progress needs) are issue #438's, a sibling's work. Week four's content is designed to
pass that check with room, by one rule: **every store a gate or a required build reads has a maker that never runs out**;
a finite pool feeds only things the story does not wait on.

| Finite pool | Filled by | Drawn by | What reads it | Lock possible? |
|---|---|---|---|---|
| `still_left` (168) | the turn | `settle` | nothing: it times the chore | no: machinery |
| `thaw_left` (1) | the turn | `thaw` | nothing | no: machinery |
| `fish_rising` (24) | the turn | `fog_fish` and its town twin | nothing: catch has four other makers | no: an optional gift |
| `deer_down`, `ruin_beams`, `grow_left`, the bloom (week two and three) | their seasons | their cards | nothing in week four | no: nothing in week four takes deer, beams, barley or bloom |

| Store progress takes this week | Taken by (required) | Its makers | Optional takers |
|---|---|---|---|
| smoked | every walk (B18, B19, I4, I6), A39 (B20), the table (arrivals, B21) | the smoke lane on catch from the snares, the wolf hunt, the fish, the boar hunt | none: the table and walks are the progress takers |
| charwood | the post (B22) | every walk, hands and town, uncapped | none in week four |
| cleared | the post | `shovel_road` and every lane's clearing, uncapped | none |
| stakes, stones, cord | the post | their everyday cards, uncapped | Lucy's jobs pay into stones; nothing optional takes them |
| pelt | the post's last three stages, `bind_book` | the wolf hunt, the boar hunt | `bind_book` (story, never a gate: below) |
| meals | the arrivals, B21 | the table while fed | none: a count, never drawn |
| ashwood_trips | B18, I4, B19, I6 | every walk | none: a count, never drawn |

Two shapes in week four needed care:

- **The post takes no beams.** Beams come only from the ruin's pool (12, week three), already spent on the hall and the
  bridge, and a player who pulled them into a full store wasted some (#438's case). Charwood is the post's timber.
- **The book never locks an ending.** E-c needs the book given (`spine.md`, O-book). Its offer's second answer is "not
  now", which leaves `bind_book` on the tasks for good, and the ending reads the book given, not the answer (D-162). A
  player who said no keeps the way open as long as they play.

The chore's chip costs meals while it shows, so it slows the arrivals and B21; it never stops them (the count only
waits), and its cure takes no store. The death costs the attempt's supplies (2 smoked), never a store a gate reads.

## Day twenty-two (I1 → B19): who is out in the fog?

In the night the wind drops and does not come back. In the morning the ash hangs in the air without falling, fog lies
in the low ground over the stream and the beds, and the town can hear the stream at the valley's far end. The player
walks the road over the ridge and down into the grey: a dead forest of standing trunks, shelf fungus up them like
stairs. A dead elk walks very slowly toward a warm patch with fungus along its spine; the hunters bring in another and
Mary won't cook it. A film of ash settles on the open meat. A bowl left at the fire overnight is found empty and washed.
On the walks someone keeps pace in the fog at the edge of the trees and stops when the player stops. One evening they
walk in behind the player and sit down across the fire.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 22a | after night 21 | the stillness; sound carrying; the walk running | (what is out there?) | I1 |
| 22b | 0-9 h | the forest; the walked elk; the meat condemned | | B18 |
| 22c | 3-9 h | fish rising under the fog | | side SL29 |
| 22d | 3-9 h | ash on the meat | | I2 |
| 23a | 3-9 h | the bowl empty and washed | who is out in the fog? | I3 (opens) |
| 23b | 3-9 h | someone keeping pace at the trees | | I4 (advances) |
| 23c | 0-9 h | they walk in behind you | (who are they?) | B19 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 21a (week three's last) | queues the walk When ready, or sets it in the hands' mix | `t_walk_shown` on `week_three_end`: `walk_ashwood`, unready, its countdown to 504 h | (week three's) | l_walk_shown |
| 22a (3-5 min) | reads I1; sets the walk's share; Wayfinding's row; the arrivals' count | I1 at 504 h: `still`, the Still's grade, `settle`, `thaw`, `fish_rising` 24, `still_clock`; the Clear's chore rules retired (D-154); `arrivals` cap ×2 (D-164); the walk ready | flat grey light, fog in the low ground, ash motes hanging | l_i1_1 to l_i1_3 |
| 22b (3-5 min) | reads B18; the walk's makes (charwood, fungus); the town's walk card on a lane | B18 at the first walk's finish: the map's Ashwood place, `e_pilgrim`, aim_ashwood; `{lane}_walk_ashwood` announced | the road's end, grey trunks; at dusk an elk dragged in and burned | l_b18_1 to l_b18_3, l_map_ashwood |
| 22c (3-5 min) | reads SL29; fish against the walk in the hands' mix | SL29 at `still_clock` ≥ 6: `fog_fish`, `{lane}_fog_fish` | rings on the water under the fog | l_fish (SL29) |
| 22d (3-5 min) | reads I2; meets the chip with its hint dot and no rule offered; washes by hand or writes a rule | I2 at `film` ≥ 12 (the chip's first showing): `ashed`, `wash_meat`, `{lane}_wash_meat` | a grey film on the racks' meat | l_film_1, l_film_2 (I2) |
| 23a (3-5 min) | reads I3; the walks' share against the fish | I3 at `still_clock` ≥ 26, once B18 | a bowl at the fire's edge, clean, set upside down | l_bowl (I3) |
| 23b (3-5 min) | reads I4; a Wayfinding find | I4 at `ashwood_trips` ≥ 4, once I3 | a figure in the fog at the trees' edge | l_pace_1, l_pace_2 (I4) |
| 23c (3-5 min) | reads B19; meets Sorrel's lane (first task their kind's rule's or the player's) | B19 at `ashwood_trips` ≥ 6, I4 + 3 h, `still_clock` ≥ 30: n13 joins, arrivals +1 | a figure sitting across the fire, sleeves down | l_b19_1 to l_b19_3 |

### The Still (fit pass)

**What it is:** the third season's week, the first Still since the season system was built (week one was a Still before
seasons were content). **Instance of:** week two's and three's season (D-115): an `after_time` trigger, standing actions
on pools the turn fills, a chip and its cures, cards on a finite pool, a threat step on the season's clock. **Fits into:**
Clock, Triggers, Standing actions, Cards, Chips, Combat (the step). No season state. New only in what it carries, and in
one thing it leaves out: no order card for its chore (D-155).

| Store | Cap | Drawn | Notes |
|---|---|---|---|
| `still_left` | 168 | never | the turn adds 168; `settle` draws 1 an hour, so it ends at 672 h |
| `thaw_left` | 1 | never | the turn adds 1; `thaw` draws it in an hour |
| `still_clock` | 8760 | never | a clock store from the turn (+1/h), opened by its own trigger on feature `still` (as `clear_clock`) |
| `film` | 24 | never (the chip is its face) | `settle` makes 1 an hour; starts at 0 |
| `fish_rising` | 24 | yes | the turn adds 24 (fish rising under the fog on the warm stream); only the fish cards draw it |

| Card / standing | Lane | Opened by | Bar (s) | Takes | Makes | Skill |
|---|---|---|---|---|---|---|
| `settle` (standing) | | I1 | | 1 `still_left` an hour | 1 film an hour | |
| `thaw` (standing) | | I1 | | 1 `thaw_left`, 24 rime an hour | | |
| `fog_fish` | hands | SL29 | 1200 | 1 `fish_rising` | 2 catch | Foraging |
| `{lane}_fog_fish` (town card) | n1-n10, n12 and later lanes | SL29 | 4800 | 1 `fish_rising` | 2 catch | |
| `wash_meat` | hands | I2 | 600 | drains up to 12 film | | Cooking |
| `{lane}_wash_meat` (town card) | every lane | I2 | 2400 | drains up to 12 film | | |
| `stir_air` | hands | SL32 | 300 | drains up to 12 film | 2 ash (the tithe) | Spellcraft |

| Chip | Shows while | Cost (words) | Cure |
|---|---|---|---|
| `ashed` | film ≥ 12 | "the table feeds fewer": the table's meals −25% | `wash_meat` (hands, cuts in), `{lane}_wash_meat` on any lane, `stir_air` from SL32; **no order card**: the chip's first showing carries its hint dot, and the player writes the rule ("when ashed, {lane} washes the meat") in the editor, as they did for the frost |

**The chore.** In still air the ash does not blow through; it hangs and settles, a fine grey film on whatever is left
open, and the racks and the table's meat are open. Nobody eats meat with ash on it ("never eat a thing that ate the
ash", the Taking: `world.md`), so Mary scrapes it, and the table feeds fewer while it lies there. A wash in the stream
takes the film off. Left alone, the chip shows from about 516 h for the rest of the season and the table makes three
quarters of its meals: the arrivals come later, B21 a day or so later on typical, never stopped. Who washes is the
decision (a lane's time against what it makes, the hands' time, and from SL32 the player's working, which pays ash for
the ground). One cure a day covers it with a rule; the chip shows for the half hour before the cure lands.

**Why no order card.** Choice, not protection: the frost and the roofs taught the chip rule by offering it ready-made,
which the owner has since ruled against for chores ("the chore arrives with its problem and a hint mark; the rule is the
player's to write", `docs/design/choice-not-protection.md`, row 43, decided). The rule editor offers a chip condition
once the chip exists (Q3 there), and every route in the simulator has written one before (the frost's). The 2 AM test
compares players given that setup, so a policy that writes the rule at the chip's first showing is the typical and
whenever player; the lazy route writes none and is reported.

**The fish.** On the warm stream the fog lies flat, and with no wind on the water the pale fish rise under it to the
surface and can be taken by hand. Twenty-four in the season, a finite gift (the deer's shape): catch for the smoke lane,
so for the table. Nothing waits on them. The fish card is spent when the pool is, and D-125 hands its share on.

**The threat step.** At `still_clock` ≥ 40 (544 h) the pack's strength steps +25% (`t_still_step`, a trigger on the
season's clock; `fight_checks` takes it): in the fog they come close before anyone sees them. Nothing new is fought. The
preparation check from week three carries on: a route that keeps the watch through the Still loses measurably fewer
pack fights than one that moves it to the post.

**What the Still adds and does not:** no rate raised (D-115). The arrivals' cap is a count's ceiling, not a rate.

### Into the Ashwood (fit pass)

**What it is:** the first expeditions: walks over the ridge into the dead forest, out and back, bringing timber and
fungus, finding things, and training a new skill. **Instance of:** the trip (`docs/design/banked-time-plan.md`; design/banked-time.txt
"BANKED TIME": an uncapped hands card with inputs, run in the mix, finds as triggers on a completion count), with a town
twin on any lane (week three's `{lane}_clear_road`), and a count store every walk adds to (`meals`'s and
`track_laid`'s idiom) so finds read one number whoever walked. **Fits into:** Cards, Triggers, Stores, the Pacing curve
(one more skill), Town map and world map (places by unlock), Expeditions (its first content: the row's first slice as
built). No engine work. Rejected: a roster of who goes (backup) now: each walk is one person alone, the player or a
townsperson, until the first expedition whose fight needs a side made of who goes (R3's companions at B28; design/banked-time.txt
"BANKED TIME", KNOWN GAPS, "Who goes"; D-158); a capped trip per destination (greys the mix at 03:00, the engine design's
rejection); finds on each card's own count (a find would wait on whoever the player happened to send).

| Store | Cap | Drawn | Notes |
|---|---|---|---|
| `ashwood_trips` | 8760 | never | every walk's outcome adds 1, hands or town |
| `charwood` | 24 (36 from Camp 19) | yes | dead hardwood, dry to the heart; the post's timber |
| `fungus` (week two's) | as shipped | yes | bracket fungus; `fungus_stew` takes it |

| Card | Lane | Opened by | Bar (s) | Takes | Makes | Skill |
|---|---|---|---|---|---|---|
| `walk_ashwood` | hands | shown at T13 (`t_walk_shown`), ready from the turn (`clear_clock` ≥ 168, `r2_open`) | 3600 | 2 smoked (food for a day out) | 2 charwood, 1 fungus; `ashwood_trips` +1 | Wayfinding (new row, 360 XP an hour) |
| `{lane}_walk_ashwood` (town card) | every lane | B18 | 14400 | 2 smoked | 2 charwood, 1 fungus; `ashwood_trips` +1 | |

**Wayfinding opens** (D-167) with the walk: a skill on the pacing curve, its row shown with the walk's first run. Its
pays are the walk's speed and three finds (levels 3 and 5, and "Walk the Ashwood: 25% less time" at 8). It needs to:
B25 (day 35) waits on Wayfinding 25 and B30 on 35, so the skill has to start in week four.

**The walk's finds** (triggers on `ashwood_trips`): 1, B18; 4, I4 (with I3); 6, B19 (with I4's clock and the season's);
14, I6 (with B19's clock). Past them the walk keeps paying its makes, so the hold stays a real choice (BT2's answer).

**Why smoked as the supplies:** the walks take what the table takes, so the week's first real trade is the forest against
the table, which is the arrivals against the expeditions. Stew sat at 0.2 on typical at 504 h (measured) and would pause
the walks; smoked sat at 69.3 of 72.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| I1 | 22a | 504 h (`after_time` 1 814 400 s) | The wind drops in the night and does not come back. In the morning the ash hangs in the air, not falling; fog lies in the low ground over the stream and the beds; the smoke from the hall goes straight up. The town can hear the stream at the valley's far end, and a crow on the hall roof clicking under its breath, and nobody talks much, as if they would be heard. | down · none · dread · none · PC · none · th-burn middle |
| B18 | 22b | the first walk finished (`ashwood_trips` ≥ 1), `r2_open` | As `spine.md`. Over the ridge and down, the grey becomes a forest: dead trunks standing as they died, shelf fungus up them like stairs, some shelves wider than a man is tall. On a warm patch by the old road a dead elk is walking, very slowly, fungus along its spine, and drag-marks run from it to every warm patch in sight. At dusk Martin and Edward drag in an elk they brought down near the trees; Mary turns its back to the fire, sees the fungus along the spine, and it goes on the fire whole. | as `beats.yaml` (up · yes_but · wonder · stores · PC · advances C-promise-3, C-promise-9 · th-network middle) |
| I2 | 22d | `film` ≥ 12, once I1 | The ash settles out of the still air onto everything left open. By noon the meat on the racks has a grey film on it, and Mary scrapes a strip with her thumbnail, looks, and puts it aside. | down · no · grim · stores · N2 · none · th-survive middle |
| I3 | 23a | `still_clock` ≥ 26, once B18 | The bowl somebody left at the fire's edge with the last of the stew in it is there in the morning, empty, rinsed, and set upside down on a stone. | up · none · warm · none · PC · opens C-promise-33 · th-stranger start |
| I4 | 23b | `ashwood_trips` ≥ 4, once I3 | On the walk back, at the edge of the trees, someone in the fog keeps level with the player, too far to see, and stops when the player stops. When the player walks on, they walk on. | down · none · dread · none · PC · advances C-promise-33 · th-stranger middle |
| B19 | 23c | `ashwood_trips` ≥ 6, I4 + 3 h (`pace_3h`), `still_clock` ≥ 30 | As `spine.md`. They walk in behind the player at dusk, a stranger in a coat with the sleeves pulled down over the hands, and sit down across the fire from everyone. They take the bowl Mary hands them and the blanket. Lucy shows them a place in the hall; they thank her and sleep by the fire outside. Asked their name, they say they don't have one to give. | as `beats.yaml` (down · no · warm · none · N3, PC · opens C-promise-10, advances C-promise-1 · th-stranger start), and pays C-promise-33 |

**Mechanically:** I1 is a trigger at 1 814 400 s (`season = true`) whose outcome unlocks `still`, `settle`, `thaw`, adds
the pools, raises `arrivals`' cap (×2, sourced `still_turn`, D-164), and retires the Clear's chore rules (D-154). B18's
outcome unlocks the town twin, the map's `p_ashwood`, `e_pilgrim` and aim_ashwood; it takes nothing (the condemned elk
never entered a store; the cost is the line). B19's outcome joins n13 (`told = line`, label "the stranger" until SL31),
an eating standing (a stew and a root an hour, as everyone's), arrivals +1, and starts `sorrel_clock` (a hidden clock,
D-150's shape) for SL31 and O-book. A save rebased past 504 h when week four ships gets I1 at the rebase instant.

### Side layer (day twenty-two)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL29 | find | th-survive | `still_clock` ≥ 6 | On the warm stream the fog lies flat on the water, and under it, with no wind to break the surface, pale fish rise and hang there, and can be lifted out by hand. | the fish against the walk in the hands' mix; a lane to the stream |
| SL30 | texture | th-faith | `still_clock` ≥ 30, the choir joined | At supper the three women start to sing and the sound goes down the valley in the still air as if the hills were singing it back. Lucy puts her hand on the nearest one's arm. Nobody sings in the Still where she comes from. They stop. | (none of its own: it shares 23c with B19, whose decision is Sorrel's task) |

SL30 is the faith's first texture (`world.md`, "Faith": no singing in the Still) a week before N4 brings its words. Lucy
gives no reason; nobody asks. Its line never mentions the rest in their songs.

## Day twenty-three (B19 → B20 ★): what is tearing up the cache?

The stranger sleeps by the fire and works at whatever is put in front of them. Mary gives them a name, after a leaf, and
it sticks though they never answer to it first. A man comes down the road with his wife and a fiddle wrapped in cloth,
and won't unwrap it. The walks leave a cache of food at the warm patch where the old road meets the trees; one morning
it is rooted up and gone, and the tracks round it are pigs', big ones. Lucy says there should be a post out there with a
store that shuts; its first ring of stakes goes up and the next cache is untouched. In the night, in the still air, the
whole town hears them rooting in the wood as if they were in the yard. Lucy says somebody has to go after them.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 23d | 3-9 h | Sorrel named; a lane's first task | | side SL31 |
| 23e | 3-9 h | the fiddler on the road | | I5; O-fiddle |
| 24a | 3-9 h | the cache torn up; pigs' tracks | what is tearing up the cache? | I6 (opens); the post shown |
| 24b | 3-9 h | O-book | | (O-book) |
| 24c | 3-9 h | the working on the racks; a job | | side SL32 |
| 24d | 3-9 h | the post's first ring; the cache untouched | | I7 (advances) |
| 24e | 3-9 h | the rooting heard in the night | | side SL33 |
| 25a | 0-9 h | Lucy's ask; the fog; you go | (B20) | B20 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 23d (3-5 min) | reads SL31; Sorrel's share | SL31 at `sorrel_clock` ≥ 6: n13's label becomes the name | Sorrel at the fire's edge, Mary pointing at a leaf | l_named (SL31) |
| 23e (3-5 min) | reads I5; answers **O-fiddle** (food or build), or the kind's rule has | I5 and O-fiddle at `meals` ≥ 175, `sorrel_clock` ≥ 4 | a man and a woman on the road, a cloth bundle on his back | l_fiddle_1, l_fiddle_2 (I5) |
| 24a (3-5 min) | reads I6; meets the post (its order card under the charwood line); the walk's share against the post's inputs | I6 at `ashwood_trips` ≥ 14, `sorrel_clock` ≥ 12: `post` (P4), its order card, the map's `p_warm_patch`, aim_post | a torn sack at the trees' edge, rooted ground | l_cache_1, l_cache_2 (I6), l_post_shown |
| 24b (3-5 min) | answers **O-book** | O-book at `sorrel_clock` ≥ 24 | Sorrel watching the player write in the journal | l_book_ask |
| 24c (3-5 min) | reads SL32; the working against the wash; Lucy's first job | SL32 at `still_clock` ≥ 44, once I2: `stir_air` | the player's hand flat on the stream's surface, the other over the racks; the film lifting | l_stir_air (SL32) |
| 24d (3-5 min) | reads I7; a post stage | I7 at `post` stage 1, once I6 | a ring of charwood stakes round a sack | l_ring_1, l_ring_2 (I7) |
| 24e (3-5 min) | reads SL33; a job; levels | SL33 at `still_clock` ≥ 64 (night 24) | night grade; the town at the hall door listening | l_rooting (SL33), l_night_24 |
| 25a (3-6 min) | taps or has queued **Go after them** (A39), shown at SL33's visit unready with its countdown; reads B20 | A39 at `still_clock` ≥ 72 (576 h), shown at `still_clock` ≥ 66 once I7; B20 at its finish | fog in the trees; then the camp stone at first light, the player lying beside it | l_go_ask, l_b20_1 to l_b20_5 |

### Sorrel (fit pass)

**What it is:** N3, a fixed notable, joining the town. **Instance of:** a joined lane (week three's arrivals: `joins`,
an eating standing, `told = line`) with `later_labels` (the lane's label changes at SL31). **Fits into:** People, Lanes,
Catalogue (every everyday town card by the lane expansion). No engine work. They work like anyone: their tell is in
the story (no place in the hall, no hand, no name of their own), never a mechanic, and no line in week four shows them
forgetting (the book's pages are the only trace, and only if it is given). Rejected: a lane-less figure (the starer's
shape; a notable who stays all game needs a name slot, and slots are a lane's); a lane that takes no rules (a mechanic
for the tell, and a person-shaped hole in the Rules tab with no reason on it); a lane that runs one installed task (it
decides for the player).

### The book (O-book) (fit pass)

**What it is:** the spine's O-book: give Sorrel a book to write in. **Instance of:** an offer of no kind whose yes queues
a hands one-off (Lucy's jobs, `o_pelt`'s idiom), and whose other answer unlocks the same card without queuing it.
**Fits into:** Offers, Cards, Knowledge (a journal subject whose notes land on triggers). No engine work.

| Answer | What it changes |
|---|---|
| **Make them one** | queues `bind_book` (hands, cap 1, 1800 s, 2 pelt, 2 cord: birch-bark leaves sewn into a hide); at its finish, feature `book_given` |
| **Not now** | unlocks `bind_book` on the tasks without queuing it; it stays there for good, and tapping it later is the same as the yes |

When `book_given` holds, a journal subject (`s_sorrel_book`) writes one page a story day from the next morning (notes on
`still_clock` thresholds 96, 120, 144 and 168 after `book_given`, so up to four in week four), each a few lines in
Sorrel's own hand, each a little at odds with the day before. The ending reads `book_given` (D-162), so E-c never turns on
whether the player said yes the day it was asked. The yes costs two pelts and half an hour; the no keeps them. The S-yes
strand reads the share declined, so "not now" counts as a no there, whatever is done later.

### The arrivals (fit pass)

**What it is:** the people the table draws in the Still: a fiddler and his wife, four who walked toward any light, three
widowers. **Instance of:** week three's arrivals (D-145's `work` kind: roles food and build; joins on its answer, the
table's cost +1 an hour at each join) and pooled lanes for the two larger groups (GROUPS: a group card runs at its share
times its free members). **Fits into:** Offers (the kind's rule answers them), Triggers, Stores (arrivals), People
(`told`: line for the pair and the walkers, mention for the widowers), GROUPS. No engine work.

| Offer | Shown | Answers | Each answer |
|---|---|---|---|
| O-fiddle (kind `work`) | `meals` ≥ 175, `sorrel_clock` ≥ 4 | **To the food** / **To the building** | both join (n14, n15, arrivals +2); their first task by the answer (the smoke lane and the fish, or clearing and stakes); keeps for good the smoke lane's smoked ×1.10 or all clearing ×1.10 (D-147's size); the table +1 an hour |
| O-walkers (kind `work`) | `meals` ≥ 230, `kept` (B20) | **To the food** / **To the building** | four join as group `g_walkers` (n16-n19, arrivals +4), the group's share by the answer; the same lasting halves; the table +1 an hour |
| O-widowers (kind `work`) | `meals` ≥ 285, `walkers_6h` | **To the food** / **To the building** | three join as group `g_widowers` (n20-n22, arrivals +3, `told = mention`: the day's mention line, no beat); the same; the table +1 an hour |

Arrivals read 25 after the widowers: 15 at 504 h (measured), +1 (Sorrel), +2, +4, +3. N4 is the twenty-sixth (B21).
Each answer is a share the player re-splits at any time. The kind's rule set in week three answers all three while the
player is away.

**Who they are** (light tier; souls from the save's seed, stand-ins with Claude off; names from `names.jsonl` by the
seed):

- **n14**, a man of forty with a fiddle wrapped in cloth on his back, who won't unwrap it in the Still ("not while the
  air's like this"). He plays when the wind comes back (week five's Drift: hand forward). **n15**, his wife, who does the
  talking.
- **n16-n19**, four who walked toward the hall's light from the south, not kin, met on the road. Lines say "four" until
  I9's line; the group's page names them.
- **n20-n22**, three widowers who came together and say little (belonging tier: `cast.md`). A mention, no beat.

### The logging post (P4) (fit pass)

**What it is:** a post at the warm patch where the old road meets the trees, with a store that shuts, so the walks have
somewhere to leave things and people can stay out to cut charwood. Week five makes it an outpost with a supply line
(B22). **Instance of:** a staged hands build run by one content order card (D-119; the road, the hall), its material a
store the walks make. **Fits into:** Cards, Standing orders, Modifiers, Town map and world map (a place revealed). No
engine work in week four; the outpost and supply-line system is week five's (B22 `unlocks: system: supply_lines`).

| Card | Lane | Opened by | Stages | Bar (s) | Takes (each stage) | Pays |
|---|---|---|---|---|---|---|
| `post` (P4) | hands | I6 | 12 | 2400 | 10 charwood, 6 cleared, 4 stakes, 3 stones, 2 cord; stages 10-12 also 1 pelt (the door's hide) | stage 1 I7; stage 6 lifts Camp 19; stage 12 B22 (with the Drift's turn: week five) |

The order card under the charwood line, offered once charwood first reaches 10: "when charwood reaches 10, build the
post". Totals: 120 charwood, 72 cleared, 48 stakes, 36 stones, 24 cord, 3 pelts, 8 h of hands. Cleared is the track
from the road's end to the warm patch, and it sits idle at 504 h (50.9 of 72 on typical, 72 of 72 on whenever,
measured): the post is its sink. **No beams** (finite pools, above). **Why twelve stages of 10 charwood:** shown about
545 h on typical and landing day 29 (672-696), about 135 h. By I6 charwood, cleared, stones and cord all sit at or near
their caps, enough for four to six stages at once; what is left waits on charwood, which only the walks make (about 0.7
an hour at typical's share), so the walk's share against the table's smoked is what moves the post. Smaller stages
would finish it by day 25.

### Lucy's jobs, and A39 (fit pass)

**What it is:** Lucy asks again, and after B20 she asks the player first, for the jobs nobody else will do. **Instance
of:** week three's jobs (D-133, D-144): offers of no kind whose yes queues a hands one-off sized to its time, whose no
costs nothing, on `ask_wait`'s countdown after the last answer. **Fits into:** Offers, Cards, Triggers. No engine work.

| Id | Lucy: somebody has to... (facts) | Yes: the job (hands, bar) and its one-off | Shown |
|---|---|---|---|
| `j_drag_marks` | follow the drag-marks from the warm patch to the next one, and see where they go | `follow_marks` (900 s): 3 charwood | from I6, on the countdown |
| `j_show_fish` | show the newcomers where the fish rise under the fog | `show_fish` (600 s): 3 catch | after `j_drag_marks` |
| `j_midden` | dig out the midden pit before it reaches the hall | `dig_midden` (1200 s): 4 ash | from B20 (below) |
| `j_leaning_wall` | pull down the ruin's leaning wall that nobody will stand under | `pull_wall` (1200 s): 3 stones | after `j_midden` |
| `j_steam_hole` | go down the hole by the stream where the steam comes up, and see how far it goes | `steam_hole` (900 s): 4 clay | after `j_leaning_wall` |
| `j_far_snares` | check the far snares past the gate in the fog | `far_snares` (900 s): 3 catch | after `j_steam_hole`, the last; waits for B21 |

Each no has its own line; she finds someone, never who. The last four start with B20 (`kept`): "the next morning's job
list has you down for the worst job on the board, because you come back" (`spine.md`). That is their joke and nothing
else: no job is dangerous in the numbers, none can kill, and each pays as its time is worth (D-144).

**A39 (`go_wallow`, "Go after them").** A glowing one-off on the hands (`only_player = "story"`, cap 1, 3600 s, 2
smoked), shown at `still_clock` ≥ 66 once I7 with Lucy's line, unready with its countdown to `still_clock` 72 (576 h),
queueable When ready. Its finish is B20. It is a story fight: no FightDef, no odds, no roll (design/fights.txt "FIGHTS": a beat's
outcome never carries odds). There is no other answer: Lucy asks the room, and the card is the player standing up. The
choice is when. Rejected: an offer whose no defers B20 forever (a spine lock); a fight card whose loss is B20 (a beat
that rolls, and a player with good odds would never die).

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| I5 | 23e | `meals` ≥ 175, `sorrel_clock` ≥ 4 (O-fiddle's moment) | A man and his wife come down the road from the ridge, he with a bundle on his back wrapped in cloth and tied. At the fire someone asks what it is. A fiddle, he says, and doesn't untie it; not in air like this. | up · yes · warm · people · PC · none · th-town middle |
| I6 | 24a | `ashwood_trips` ≥ 14, `sorrel_clock` ≥ 12 | The cache the walks leave at the warm patch where the road meets the trees is rooted out of the ground in the night, the sacks torn, the meat gone. The ground round it is churned, and the tracks are a pig's, split-hooved, wider than a hand. | down · no · grim · stores · PC, N1 · opens C-promise-34 · th-network middle |
| I7 | 24d | `post` stage 1, once I6 | A ring of charwood stakes stands at the warm patch, the next sack hung inside it. In the morning the ground outside the ring is churned all the way round, and the sack hangs where it was. | up · yes · warm · none · PC · advances C-promise-34 · th-network middle |
| B20 ★ | 25a | A39 finished, B19, `ashwood_trips` ≥ 3 | As `spine.md`. In the fog under the trees every sound is close and from nowhere: the player hears them rooting to the left, then behind, then all round. The boar comes out of the fog from the side the player wasn't facing. The player wakes at first light on the warm stone at camp, cold through, with ash in their mouth. Lucy is sitting by the fire. She looks a long while and says: "Kept, are you." The next morning the player's name is first on her list, beside the worst job on it. | as `beats.yaml` (down · no · wry · time · PC, N1 · advances C-promise-1 · th-self start), and pays C-promise-34 |

**Mechanically:** I6's outcome takes 6 smoked by a two-hour drain on its own clock (the visitor's idiom, `cache_torn`,
pausing at empty: the cache's meat), unlocks `post` and its order card, `p_warm_patch` and aim_post. I7 is a line. B20's
outcome unlocks feature `kept` (Lucy's later jobs, the walkers' offer and the death mechanic read it), `hunt_boar`,
`e_ash_boar`'s entry (written at the first hunt) and the first forgetting note (`n_forget_1`, "Kept", below), and starts
`kept_clock` (hidden) for I8 and I10. A39's supplies are spent whatever happens: a lost fight wastes the attempt.

### Side layer (day twenty-three)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL31 | arc (n13) | th-stranger | `sorrel_clock` ≥ 6 | Mary calls the stranger after the sour leaf that grows by the warm stream, because they ate a handful of it, and by supper everyone does. They don't answer to it the first few times. | their share: a lane's first real task (the walks, the fish, the wash) |
| SL32 | thread (magic) | th-magic | `still_clock` ≥ 44, once I2 | The player lays one hand flat on the stream where it runs, and holds the other over the racks, and the still air over the meat moves, once, like a breath, and the film lifts off it and blows away. The hand in the water comes out grey. | the working (the player's time; ash for her ground) against the wash (a lane's time) |
| SL33 | texture | th-network | `still_clock` ≥ 64 (night 24) | In the night, with no wind, the town hears them in the wood over the ridge: rooting, grunting, wood breaking, as near as the yard. People come to the hall door and listen. Nobody goes out. | (none: A39 shows with it, unready; the decision is the post's split and whether to queue it) |

`stir_air` (SL32) moves motion, not heat: the stream's run into the air over the racks, like into like, so the tithe is
small (2 ash). It is the second working and the first that is not heat. The Spells row's interpreter still waits for rule
3 (D-135): two cards are not a grammar.

## Day twenty-five (B20 → B21): does anyone think it strange?

At the fire that night Mary dishes the player's bowl as she always does. Nobody says anything. A newcomer asks what
happened to the player's coat and is told, and shrugs: kept, then. Lucy's list has the player down for the midden, the
leaning wall and the steam hole. The boar are still out there, and now the player can go after them as often as they
like; it goes as it goes. Thomasina lays her hand flat on the camp stone where the player woke, and says thank you to
it. Then a stranger walks in along the road, stopping at every warm stone to lay a hand on it, and at the fire looks at
the player for a long time.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 25b | 3-9 h | the bowl set out; nobody says anything | does anyone think it strange? | I8 (opens) |
| 25c | 3-9 h | the boar hunt; the first worst job | | |
| 25d | 3-9 h | four who walked toward the light; a shrug | | I9 (advances); O-walkers |
| 26a | 3-9 h | a post stage; Camp 19 | | |
| 26b | 3-9 h | a hand on the stone, a thank-you | | I10 (advances) |
| 26c-26d | 3-9 h each | the widowers (a mention); jobs; levels | | |
| 27a | 0-9 h | someone laying hands on stones; a long look | (who is this?) | B21 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 25b (3-5 min) | reads I8; puts the boar hunt in the mix or not (its odds and its on-loss line shown); the first worst job | I8 at `kept_clock` ≥ 8; `hunt_boar` open since B20; `j_midden` on the countdown | the hall at supper, a bowl set at the player's place | l_bowl_set (I8) |
| 25c (3-5 min) | the boar's page; a job; the post against the hunt | `e_ash_boar` at the first hunt | | find lines |
| 25d (3-5 min) | reads I9; answers **O-walkers**, or the kind's rule has | I9 and O-walkers at `meals` ≥ 230, `kept` | four at the gate in the fog | l_walkers_1, l_walkers_2 (I9) |
| 26a (3-5 min) | a post stage; Camp 19 | Camp 19 at `post` stage 6 | the post's walls on the map's place | l_camp_19 |
| 26b (3-5 min) | reads I10; a job | I10 at `kept_clock` ≥ 30, once I9 | Thomasina kneeling at the camp stone | l_thanks (I10) |
| 26c-26d (3-5 min each) | the widowers' mention; jobs; finds; the post's split | O-widowers at `meals` ≥ 285, `walkers_6h` | | the day's mention line |
| 27a (3-5 min) | reads B21; meets N4's lane | B21 at arrivals ≥ 25, `belonging`, `kept`, `bede_wait` ≥ 8 | a figure on the road kneeling at a stone; a ring at the fire, one outside it | l_b21_1 to l_b21_4 |

### Kept (fit pass)

**What it is:** from B20, the player's own death is part of the game (`regions.md`, "Death"; `decisions.md`, "Your own
death may be a mechanic, never a punishment"): it comes only from a fight the player chose or a story beat, costs what
the attempt carried and nothing banked, returns the player to the warm stone, and each return adds one margin line of a
small forgetting. Progression from death happens once, as B20. **Instance of:** a lost fight (FIGHTS: losses are flows,
counted exactly in a tally store; which fights the log calls lost is the Chronicle's shuffle-bag draw) **told** as a
death, and a journal note written from the save's history (the composer folds a day's moments). **Fits into:** Combat
(a FightDef's lost tally), Chronicle and unwrap (the loss lines), Knowledge (the composer's notes), Catalogue (one
authored field). No engine work: the engine already pays a lost fight as a wasted attempt and counts it.

What is new is three authored fields on a fight card's `fight` table, because nothing may be decided by matching a
card's name: `loss_pool` (the pool its lost labels draw from), `loss_notes` (a journal note pool written per whole loss)
and `on_loss_key` (its on-loss wording). The plan names them neutrally on purpose (`docs/design/week-four-plan.md`,
item 1, "LOSS LINES"): `docs/` is the owner's, and whether the player can die is behind a spoiler the owner chose not
to open (`open-questions.md`, 4). The loader refuses them on a town card, on a card with a town twin, on a standing
fight, on a card whose `only_player` is not `"self"`, and on a card that can open before `kept` (`loss_after`).
`hunt_boar` carries all three:

- shows its on-loss line as the player's death in the card's own words (UI voice: "a loss: you die, and wake at the
  stone; what you carried is lost");
- draws its lost lines from a death pool (`fight_<card>_death`: the attempt, the fog, waking at the stone), never a hurt;
- adds one margin forgetting to the journal per whole unit its tally crosses, drawn from the forgetting pool by a
  shuffle bag keyed by the save (Chance's stream, never the engine), on the day page of the day it landed; at most one per
  day's page is shown in full and the rest fold into a count line in the journal's voice. B20 writes the first
  (`n_forget_1`) itself.
- adds nothing to `hurt` and takes nothing banked.

The forgetting pool's notes are trivial and never a recipe, an odd, a store, a name of a notable or anything the player
needs (`regions.md`): the word for the hook a pot hangs from; which hand they start a knot with; whether the stream is
left or right of the hall from the door. Twelve authored stand-ins; the writer's job kind for them comes with runtime
writing (issue #29).

Dying on purpose is never the best route: a death pays nothing, and a hunt lost is its supplies gone and its catch
missing. Rejected: a death that takes stores or levels (the guardrail); a death as an engine event or a respawn timer
(no instant per fight, design/fights.txt "FIGHTS"); deaths on the walks (they are not fights, and deaths come only from fights the
player chose); a light-tier companion's death on a loss (FIGHTS' KNOWN GAP "Whole losses that are people" stays open:
nobody goes with the player in week four).

### The boar hunt (fit pass)

**What it is:** going back for the boar, as often as the player likes, now that dying is a thing they come back from.
**Instance of:** a fighting trip (design/banked-time.txt "BANKED TIME": a trip card carrying a FightDef on the hands' side; week three's
deer). **Fits into:** Cards, Combat, the Kept field above. No engine work.

| Card | Lane | Opened by | Bar (s) | Takes | Won share makes | On loss | Skill |
|---|---|---|---|---|---|---|---|
| `hunt_boar` (`only_player = "self"`) | hands | B20 | 7200 | 2 smoked | 6 catch, 1 pelt | death (`loss_pool`, `loss_notes`, `on_loss_key`); tally `boar_lost` | Melee |

| Threat | Base | Step |
|---|---|---|
| `ash_boar` (R2) | 14 (placeholder: the hands' side about 4 to 1, one hunt in five lost) | +25% at `r2_clock` ≥ 144 (`t_boar_sounders`), R2's first ramp step |

Odds unknown until the first hunt (the deer's shape). The catch goes to the smoke lane, so the boar feeds the table that
the walks and the arrivals contend for, and the pelt is the post's door. The long bar keeps deaths few: at a typical 20%
share, about one hunt every ten hours, so about one death every two days.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| I8 | 25b | `kept_clock` ≥ 8 | At supper Mary dishes the player's bowl and sets it at their place, as every night. Nobody says anything about the morning. Martin passes the bread. Edward asks if the player is going out after the pigs again. | up · none · wry · none · PC, N2 · opens C-promise-35 · th-self middle |
| I9 | 25d | `meals` ≥ 230, `kept` (O-walkers' moment) | Four come in out of the fog at the gate, who walked toward the hall's light from the south, not kin, met on the road. One of them asks why the player's coat is torn down the back and stiff. Someone tells her. She shrugs: kept, then, and asks where they sleep. | up · yes · warm · people · PC · advances C-promise-35 · th-town middle |
| I10 | 26b | `kept_clock` ≥ 30, once I9 | In the morning Thomasina kneels at the camp stone where the player woke, lays her hand flat on it, and says thank you to it, quietly, the way you'd thank someone for a kindness. | down · none · dread · trust · PC · advances C-promise-35 · th-faith start |
| B21 | 27a | arrivals ≥ 25, `belonging`, `kept`, `bede_wait` ≥ 8 | As `spine.md`. A stranger walks in along the road, stopping at every warm stone to kneel and lay both hands on it, the camp stone last. At the fire they look at the player a long time, the only one who does, and then say it's a blessing, and mean it. When Thomasina tells them she thanked the stone, they take her hands off it: never thank the warmth. It keeps accounts. That night they make a ring at the fire, hands joined, and say the words; Sorrel stands outside it and won't take the hand held out. | as `beats.yaml` (up · none · dread · trust · N4, N3 · advances C-promise-3, C-promise-4, C-promise-10 · th-faith start), and pays C-promise-35 |

**Mechanically:** I9 and O-walkers are one moment. I10 is a line. The twenty-fifth arrival (the widowers' join) starts
`bede_wait` (hidden, D-150); B21 at 8 h on it joins n23 (N4, `told = line`, every everyday town card; no faith bonus,
`cast.md`, N4's rule), its eating standing and arrivals +1, and starts `bede_clock` for day twenty-seven's beats. Nobody
says what N4 is called by the town until I11's line; the lane's label is "the bedesman" (`cast.md`'s role word) from the
join, and their name from `names.jsonl`.

### Side layer (day twenty-five)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL34 | texture | th-self | the first lost boar hunt | The second time, the player knows the fog is coming before it does. It makes no difference. They wake at the stone. Lucy has left a blanket on it. | the boar's share against the post (the hunt's odds and its supplies are on the card) |
| SL35 | arc (n12) | th-town | `kept_clock` ≥ 20 | The cutter's sister watches the player come back up from the stone in the morning, and for a moment she looks at the road. Then she goes back to the stakes. | her share: the post's stakes or the walks |

SL35 must never suggest he could come back: she looks at the road, once, and the line ends on the stakes (week three's
cutter rule holds for every line after B17).

## Day twenty-seven (B21 → night 28): will anyone know the first name?

The bedesman goes from house to house. At the board they read the marks: the cutter's name, said aloud, and the first
mark with nothing beside it. They ask Lucy whose it was. Nobody knows. They ask every household for the names of its
dead, and the newcomers give them, a few each. The post goes up at the warm patch, a stage at a time. On the Still's last
night the town sits at the fire and the bedesman says every name they were given, into air so still that the names carry
down the valley; at the first mark they stop, and say nothing, for as long as a name would take.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 27b | 3-9 h | the board read; the first mark asked about | will anyone know the first name? | I11 (opens) |
| 27c | 3-9 h | the bedesman's hands on every stone | | side SL36 |
| 27d | 3-9 h | names given, house by house | | I12 (advances) |
| 28a-28c | 3-9 h each | the post near done; jobs; levels; the boar | | |
| 28d | 0-9 h | night 28; the names said; the silence | (week five) | I13 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 27b (3-5 min) | reads I11; N4's share | I11 at `bede_clock` ≥ 4 | the board by the fire, a figure reading it | l_board_1, l_board_2 (I11) |
| 27c (3-5 min) | reads SL36; a post stage | SL36 at `bede_clock` ≥ 10 | the bedesman kneeling at a field stone | l_hands (SL36) |
| 27d (3-5 min) | reads I12; meets **Sit at the fire** (A40), shown unready with its countdown | I12 at `bede_clock` ≥ 20: A40 shown | the bedesman at a doorway, a woman counting on her fingers | l_names_given_1, l_names_given_2 (I12) |
| 28a-28c (3-5 min each) | the post's last stages against the boar and the walks; jobs; finds | | | find lines; jobs |
| 28d (3-5 min) | taps or has queued A40; reads I13; the week's end card | dusk 28 at save time ≥ 666 h; A40 at `still_clock` ≥ 163 (667 h); I13 at its finish | night grade; everyone at the fire, the bedesman standing | l_night_28, l_i13_1 to l_i13_3 |

### The bedesman (fit pass)

**What it is:** N4 in the town: a person who works like anyone, and who asks for the names of the dead. **Instance of:**
a joined lane (above) and the asks' shape for its moments (lines on clocks and a glowing step for the night, week three's
A38). **Fits into:** People, Lanes, Triggers, Cards. No engine work. The names are never a store and never counted: the
faith is never a mechanic (`cast.md`, N4's rule), and C-promise-17 is planted without fields (`spine.md`, B21's row in
Q6).

### The clocks

**Night 24** is SL33's: the night grade from `still_clock` 64 to 72 (568 to 576 h), a hidden clock the scene reads, as
night 21's. It ends at A39's ready hour: the morning is the fog.

**Night 28** ends the week on the calendar: dusk 28 at save time ≥ 666 h (2 397 600 s, `after_time`); A40
(`sit_names`, "Sit at the fire", glows, narrative, cap 1, 5 s) requires `still_clock` ≥ 163 (667 h) and I12's feature;
on the cards from I12, unready with its countdown, queueable When ready (A38's shape). I13 is week four's last beat; the
Drift's turn at 672 h does not wait on it.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| I11 | 27b | `bede_clock` ≥ 4 | The bedesman stands at the board by the fire and reads the marks with a finger. At the second they say the cutter's name aloud. At the first, with nothing beside it, they ask Lucy whose it was. She says nobody knew. They ask who sat up with him; Lucy did. They ask what he was like. She thinks, and says he had a cough. | down · no · grim · none · PC, N1, N4 · opens C-promise-36 · th-faith middle |
| I12 | 27d | `bede_clock` ≥ 20 | The bedesman goes door to door with the same question: who have you lost, and what were they called. The newcomers give them, a few each, counting on their fingers. The widowers give one name each and nothing else. Lucy gives hers, and stops partway, and says that's all. | down · none · grim · none · N4, N1 · advances C-promise-36 · th-faith middle |
| I13 | 28d | A40 (in night 28), I12 | Night 28. The town sits at the fire and the bedesman stands and says every name they were given, one after another, into air so still the names go down the valley and come back off the far side. At the cutter's they say it twice. At the end they stop, and say nothing, for as long as a name would take, and sit down. | up · yes_but · warm · none · PC, N4 · pays C-promise-36 · th-faith middle |

I11's "a cough" is the only fact anyone has of the first dead, and it is said once. No line says the town has forgotten
anything, that names are a payment, or that anything listens: the names go down the valley and come back, which is an
echo in still air. Lucy's names are her people's (`cast.md`: "the last of five", canon only): no line counts them or says
whose they were; the line says she gives hers and stops. I13 closes on the silence, which is the
first mark, and never says so. The week's ★ is B20.

### Side layer (day twenty-seven)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL36 | texture | th-faith | `bede_clock` ≥ 10 | The bedesman walks the valley and kneels at every warm stone in it, both hands flat, a moment each. At the camp stone they keep them there longer, and get up without saying anything. | N4's share: the post or the walks |

SL36 says nothing about the camp stone beyond the hands staying longer: never why, never warmer, never that it is
different (week three's camp-stone must-not holds).

## Levels and finds (week four)

Typical stands at Scavenging 16, Woodcutting 16, Foraging 10, Cooking 17, Arcana 14, Melee 21, Spellcraft 8 at 504 h
(measured; levels as shown under prestige phases). Week four's finds go on the next speed-only level past those that
typical reaches by night 28, require feature `still`, and restate the level's row. If the simulator shows typical past a
level at the turn, the find moves to the next speed-only level in range; with none left, it is cut.

| Skill | Level | Pays |
|---|---|---|
| Wayfinding (new; 1-10) | 3 | find: a Chequer road marker half-buried by the old road, its face worn blank (the map's `p_marker`) |
| | 5 | find: from a dead tree on a rise, far off over the forest, a hill with something square on top (the map's `p_square_hill`, unlabelled) |
| | 8 | "Walk the Ashwood: 25% less time" |
| Woodcutting (17-19) | 18 | a charwood trunk fallen across the old road, seasoned through (charwood +6) |
| Foraging (11-13) | 12 | a shelf fungus as wide as a table (fungus +8) |
| Scavenging (17-19) | 18 | a road-iron spike in the old road's bed (scrap +4) |
| Cooking (18-20) | 19 | fish wrapped in leaves and laid in the coals (stew +8) |
| Melee (22-24) | 23 | a boar's tusk, from the first won hunt (cord +2), requires `kept` |
| Spellcraft (9-12) | 10 | "Move the air: 25% less time" |

The square on the far hill is P5's waystation (week five), seen and unlabelled: C-promise-9, how big the world is.
No find names Sorrel's past, the boar's fog, the first mark, the starer, the cutter, or anything of week five.

## The Camp

| Level | At (camp items) | Pays |
|---|---|---|
| 19 | 5 100 000, held ("?") since week three (the camp store sits at it: 5 099 995 at 504 h, measured); lifted by `post` stage 6 | "Charwood holds 36, was 24" |
| 20 | 6 100 000, held ("?") past week four's content | (week five) |

## Stated aims

| Aim | Starts at | Intent |
|---|---|---|
| aim_ashwood | B18 | see what the wood holds |
| aim_post | I6 (the post shown) | a post out at the trees |
| aim_names | I11 | (a line for the week's last days: the names, never the first mark's) |

Aims are lines: no season name, no beat.

## The flat check, authored order

Spine and chapter beats from I1, in landing order on typical: I1 down, B18 up, I2 down, I3 up, I4 down, B19 down, I5 up,
I6 down, I7 up, B20 down, I8 up, I9 up, I10 down, B21 up, I11 down, I12 down, I13 up. Never three turns the same.
Outcomes: B18 yes_but, I2 no, B19 no, I5 yes, I6 no, I7 yes, B20 no, I9 yes, I11 no, I13 yes_but (no two yes without a
no between). Registers: dread, wonder, grim, warm, dread, warm, warm, grim, warm, wry, wry, warm, dread, dread, grim,
grim, warm (never four the same; never three). Costs: none, stores, stores, none, none, none, people, stores, none,
time, none, people, trust, trust, none, none, none.

**Net:** chapter beats I1 −, I2 −, I3 +, I4 −, I5 +, I6 −, I7 +, I8 +, I9 +, I10 −, I11 −, I12 −, I13 + = −1; spine B18 +,
B19 −, B20 −, B21 + = 0. The week nets down, so the flat check's `week_net_up` raises nothing: the Still is the darker
week, its ★ a death. The near promises: C-promise-33 opened 23a, advanced 23b, paid 23c; C-promise-34 opened 24a,
advanced 24d, paid 25a; C-promise-35 opened 25b, advanced 25d and 26b, paid 27a; C-promise-36 opened 27b, advanced 27d,
paid 28d. Expected flags to accept (D-170): 22a, 22b, 22c and 22d do not touch C-promise-33 (near_untouched; the
question opens at 23a, the first morning a stranger can have eaten); 23d and 23e touch no near question (between two);
24b, 24c and 24e do not touch C-promise-34; 25c, 26a and 26c-26d do not touch C-promise-35; 27c and 28a-28c do not touch
C-promise-36.

## Away from the screen

- **Every planned moment plays in full on return:** I1, B18, SL29, I2, I3, I4, B19, I5, I6, I7, SL33, I8, I9, I10, B21,
  I11, I12 and most post stages land while away on typical; each is revealed in order, one at a time.
- **Per absence, at most two moments:** night 21 → 22a brings I1 (its pools, the retired rules and the cap are one
  moment) and B18 when the walk was queued at T13 (two); SL29 is six hours on; I2 lands on the film's 12th hour; I3 and
  I4 are the morning and the walks after; B19 is 3 h past I4 by its own clock; I5 and O-fiddle are one moment; I6, the
  post and its order card are one; I9 and O-walkers are one; the widowers are a mention, which counts; B21 is 8 h past the
  twenty-fifth arrival; A40 and night 28 are I13's visit. A return that brings an arrival answered by rule and its next
  job counts two.
- **The 2 AM test:** the walk is on screen from T13 and queueable before the turn; the turn's cards open onto a finite
  pool (the fish) and a chip; the chore is answered by a rule every tool-using route has written before (a chip
  condition), never offered; the post by its order card; the arrivals by the kind's rule; the jobs are answered in the
  visit they show and their one-offs queue When ready; A39 and A40 are glowing steps shown unready with their countdowns
  and queueable; the boar hunt and the walks are flows in the mix. The pack, the rats and the crows are flows
  (invariant 81). The chip costs only while it shows. D-125 removes the babysitter's head start at the fish's end.
- **Rebased saves:** a save past 499 h when week four ships gets the walk at the rebase instant; past 504 h, I1 at the
  rebase instant; nothing else of week four can be past.

## Sharp's floor-bound stretches

Week four holds sharp with the season's clock, not save-time floors: B19 waits on `still_clock` 30, B20 on A39's 72, and
B21 on the meals the table makes, which the cellar route (sharp's answer to O-sun) makes at 1.0 an hour against
typical's 1.25. Sharp will reach B19 and B20 at their clocks and then wait. What fills the waits is never more asks: it
is two far goals sharing the town's time, so a share change moves which lands first: the post (charwood from the walks,
cleared from the lanes) against Wayfinding 8 and Camp 19's marker from B19; from B20 the post against the boar (catch for
the table, and so the arrivals). The decide counter on sharp keeps week three's target: at least three visits of every
four with a decision.

## Art

All picked from the packs by `sprite-catalog` first; drawn only where the kit lacks it.

- **Grades:** the Still (flat grey light, no shadows, cool and close; fog in the low ground; ash motes hanging in the
  air, still), from I1 to week five's turn; nights 24 and 28 (the night grade, the fog pale under the hall's light; each
  until its morning).
- **World layers (cool):** fog in the low ground over the stream and the beds; ash motes in the air (still: a few
  layers, no drift); rings on the stream under the fog (SL29 to the fish's end); a grey film on the racks while `ashed`
  shows; two wolves at the gate in fog from the step (week three's two, fainter).
- **Player-made (warm):** the post is out in the wood, so it is a map stamp, not a scene stamp (`p_warm_patch`, revealed
  at I6); the racks with their meat (as shipped, the film layer above). The board by the fire: unchanged marks (no new
  mark this week).
- **Figures:** Sorrel (a long coat, sleeves over the hands; sitting apart at the fire; sleeping by the fire outside the
  hall at night), the fiddler with a cloth bundle on his back and his wife, the four walkers (one group, standing close),
  the three widowers, the bedesman (kneeling at a stone, both hands flat; the kit's robed figure, grimed in code); the
  player lying at the camp stone at first light (transient id `stone:wake`, B20's visit); the ring at the fire with one
  figure outside it (transient `fire:ring`, B21's visit); everyone at the fire, the bedesman standing (transient
  `fire:names`, I13's visit).
- **Journal sketches:** the pilgrim (a walking elk, fungus along its spine) and the ash-boar, each by the sketch-test
  method, looked at before it ships.
- **The map:** four places, by the Widman stamps (`docs/research/art-sourcing.md`): `p_ashwood` (forest, at B18),
  `p_warm_patch` (the post's site, at I6), `p_marker` (a small marker, Wayfinding 3), `p_square_hill` (a hill, far,
  unlabelled, Wayfinding 5).
- **Stages:** 67_still, 68_ashwood, 69_walked_elk, 70_film, 71_bowl, 72_keeping_pace, 73_stranger_home, 74_fiddle,
  75_cache, 76_ring, 77_fog, 78_stone_wake, 79_bowl_set, 80_thanks, 81_bedesman, 82_board, 83_names_night.

## The journal (week four)

| Entry | Written by | Notes (ids; text in the brief) | Numbers shown |
|---|---|---|---|
| `e_pilgrim` | B18 | `n_pilgrim_1` (walks slower than anything alive; fungus along the spine; drag-marks to every warm patch; meat from one is not eaten) | none (not a fight) |
| `e_ash_boar` | the first boar hunt | `n_boar_1` (bigger than a pig has any right to be; caked grey; comes from the side you aren't facing) | the hunt's odds, fought, lost |
| `e_ashwood` (a place) | B18 | `n_ashwood_1` (dead trunks still standing; shelves up them like stairs; warm patches where the ash is thin) | |
| `e_days_8` | I1 | days notes on B18, B19, B20 and B21, each at its beat's step | |
| the days pages | B20 and each death after | `n_forget_1` .. `n_forget_12` (margin forgettings, Kept above) | |
| `s_sorrel_book` | `book_given` | up to four pages in week four, one a story day (the book, above) | |

No note says what Sorrel is, why they won't come in, what the bedesman is for, that the names are anything but names, or
that the player is anything but kept. The boar page's numbers are the death mechanic's only figures.

## Proposed canon (tentative until the lead confirms)

- C-promise-33: day twenty-two's near question, *who is out in the fog?*, opened by I3, advanced by I4, paid by B19.
- C-promise-34: day twenty-three's, *what is tearing up the cache?*, opened by I6, advanced by I7, paid by B20.
- C-promise-35: day twenty-five's, *does anyone think it strange?*, opened by I8, advanced by I9 and I10, paid by B21.
- C-promise-36: day twenty-seven's, *will anyone know the first name?*, opened by I11, advanced by I12, paid by I13.
- C-beat-138 (I1) to C-beat-150 (I13), each as its row above; C-beat-151 (B18's shape: the forest of standing dead
  trunks and fungus shelves, a walked elk on a warm patch, the hunters' elk burned whole), C-beat-152 (B19's shape: N3
  walks in behind the player at dusk, takes the bowl and the blanket, sleeps by the fire outside the hall, has no name to
  give), C-beat-153 (B20's shape: the boar out of the fog, the wake at the camp stone, "Kept, are you", the player first
  on Lucy's list), C-beat-154 (B21's shape: N4 kneels at every warm stone, looks long at the player, calls it a blessing,
  stops a thank-you to the stone, and Sorrel stands outside the ring).
- C-cast-33: N3 is named Sorrel by Mary after the sour leaf by the warm stream; they work like anyone and sleep by the fire outside
  the hall.
- C-cast-34: week four's arrivals, light tier: a fiddler who won't unwrap his fiddle in the Still, and his wife; four who walked
  toward the hall's light, not kin; three widowers.
- C-cast-35: N4's lane is labelled the bedesman; N4 asks every household for the names of its dead and says them at the fire.
- C-motif-10: the first mark on the board has no name; the only thing anyone remembers of the man is a cough (I11).
- C-season-13: the Still in R1: the ash hangs and settles on open meat; fog on the warm stream lets pale fish be lifted out by hand;
  sound carries the length of the valley; nobody sings in the Still where Lucy comes from.
- C-region-22: R2's edge: the Ashwood's dead standing trunks and shelf fungus; walked elk on warm patches; ash-boar at the warm patch
  where the old road meets the trees; a Chequer road marker by the old road; a hill far off with something square on it.
- C-region-23: the death mechanic as built: from B20 a lost boar hunt is the player's death and wake at the stone, and each adds one
  small margin forgetting.

## For the owner

Three questions, asked spoiler-free in the pass's report:

1. **Something seen far off before it can be reached.** When the map could show a place the character has only seen in
   the distance, should it go on the map unlabelled at once, or stay off until someone gets there?
2. **One long build across several days.** This week's long goal takes about five days of play to finish, with smaller
   things landing between. Is that a good length, or does a goal that long start to feel like a slog?
3. **A season's second time round.** The first season to come back is here. Should a season's return bring mostly new
   things, or mostly the same things again with a twist?

## Open (content side)

1. **The walk's numbers** (3600 s, 2 smoked, 2 charwood, 1 fungus) and the finds' counts (1, 4, 6, 14) are the
   simulator's to set so typical lands B18 by 512 h and B19 mid-band; the season's clock (26, 30) holds sharp. Never
   lengthen a hands bar to move a band.
2. **The post's stages** (12 × 10 charwood, 6 cleared) are set so typical's last stage lands in day 29 (672-696 h); B22's
   floor (the Drift's turn) holds sharp.
3. **The meals thresholds** (175, 230, 285) and the table's raise per group (+1 an hour) are set so typical lands B21
   mid-band (624-648) with a rule on the chip, and the lazy route (no rule) inside its band. If the table never runs dry
   on typical, raise its cost before adding a threshold; if it starves, lower the walk's supplies before the table's
   cost.
4. **The boar** (base 14, 7200 s, 2 smoked) is set so typical's chosen share sees about one death every two days and
   the hunt pays its supplies back in catch on the won share. If deaths read as a farm (more than about three a day on
   any route), lengthen the bar.
5. **Charwood** fails the cap-loss check until the post shows (I6): the walks make it from 504 h and nothing takes it.
   The lever is the post shown sooner (I6's count), never a new sink.
6. **Pelts:** the post's last three stages (3) and the book (2) against the wolf and boar hunts. If pelt fails the
   cap-loss check at day twenty-three's end, the lever is the post's door hides on more stages, never a new sink.
7. **Week five must decide** B22's moment (the post's last stage and the Drift's turn), the fiddler's first tune in the
   Drift, the Drift's chore rules at its turn (the roofs' order cards come back with the ash, D-126), whether Sorrel's book
   is offered again if declined (it never needs to be: `bind_book` stays on the tasks), and N5's casting at B22 from
   whoever has walked most (`ashwood_trips` is not per person: the town twins' card counts are).
