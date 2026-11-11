# Days four to seven: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `days-four-to-seven.md` (beats, side layer, canon ids);
the data will be `day_four.toml`, `day_five.toml`, `b7.toml` and `day_six.toml`, where every key below reads
"[line to write]". The states below are the design's expectation. **Before the writers start**, regenerate them with
the simulator's `--lines` (`docs/design/days-four-to-seven-plan.md`, item 1, and combat-plan item 9 for `b7.toml` and
day six) and replace this file's "States" notes with the generated lists; a line written against the expectation alone
is a draft.

## How the lines get written

As day three's brief, unchanged: three blind proposers (Sonnet), one lens each (below), every key plus one alternate per
key marked H; a critic scores the drafts blind on `rubric.md` plus *true in every listed state?*; the lead picks line by
line; code checks length, the must-nots as a scan, and three-word echoes against content prose and every shipped line
before them; a fresh agent's voice pass reads every picked line and label in player order after day three's last lines,
and writes the labels. One batch per chapter, in chapter order, so each voice pass reads the last chapter's picks.

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases.

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase, plain. One or two short sentences. A turn the
  reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, per chapter.
- **True in every state.** Most of this plays on return. Never say when, in real time, anything happened, or how long
  it took.
- **People:** Lucy by name where "she" would be unclear; him as `{n2}`; the pair as "she" and "the old man" until
  l_join2_2 gives `{n3}` and `{n4}`. What each does, in active voice. Lucy never grateful, never sweet, never says
  much; no line gives anyone a need the player could tend. Light-tier people are ordinary: no backstory past what they
  carry.
- **Fights** (B7 and day six): plain, one short line, won or lost, never gory, never dwelling on how a beast dies;
  hunting and skinning told as a way of life. A long absence folds into one count line (`fight_*` pools, below).
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

## Voice exemplars (shipped)

Read the exemplar tables in `day-two-lines-brief.md` and day three's shipped lines in `day_three.toml` (B5's set
especially, which day four follows directly). Reuse no phrase from them.

## Lenses

`python3 content/team/draw_lenses.py days-four-to-seven-lines --writers 3`:

| Writer | Lens |
|---|---|
| writer-1 | what a stranger would get wrong |
| writer-2 | what it costs the people |
| writer-3 | what the hands are doing |

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, and anything special.

### Day four: the fog (W1-W4)

**l_morning_5** (morning 5; no beat). Facts: white past the scrub's edge at first light. States: on return after night
4, nearly always.

**l_fog_1** (L1, H). Fields: down · dread · time · opens the near question. Canon C-beat-94. Facts: fog down in the night
and still there; the fire a smear in it; nothing dries; the stack soft at the edges. States: morning 5, any comfort
state.

**l_fog_roofed / l_fog_open** (L1's second line, chosen by `rack_roof` stage 2 done or not). Facts: under the roof the
hang stays pale / without it, it drips. Special: the roofed line is quietly smug about the player's own earlier choice,
never about the weather.

**l_shed_1, l_shed_2** (woodshed stages 1 and 3's start; a frame, then a roof). States: any order with the day's other
builds.

**l_sign_1, l_sign_2** (L2, H). Fields: down · dread. Canon C-beat-95. Facts: out along the track in the fog, a small
deer half eaten; prints, more than two sets; coming back the long way, the same prints in a ring round the camp at the
scrub's edge, never nearer. States: day 5; before or after his watch; any track share. Special: prints, never animals.

**l_his_watch** (SL8). Facts: `{n2}` takes a turn at Lucy's watch fire, the headless shaft across his knees, facing the
track. States: day 5, after L2.

**l_stack_1, l_stack_2** (L3, H). Fields: up · warm · advances the near question. Canon C-beat-96. Facts: he stacks the
wood bark up; Lucy takes it down and stacks it bark down; he laughs; she doesn't, quite, and leaves the last row his
way. States: woodshed stage 2, by the queue or present. Special: the warmth is in the last row, unstated.

**l_shed_done** (SL7). Facts: the stack under a roof, split ends out, dry at the heart; Lucy pulls a log from the
middle to check and puts it back.

**l_night_5** (night 5's first item). Facts: the fire smoking on wet wood as the light goes.

**l_b6_1 to l_b6_3** (A21, B6, H each). Fields: down · yes_but · wonder · trust. Canon C-beat-6. Facts: the fire
dying in the night; the player's hand on the warm stone; the heat goes into the kindling without the player knowing
how; grey ash on the fingers that won't wash off; Lucy sits on the far side of the fire that night. States: night 5,
present (A21 is a tap). Special: wonder first, the cost last and unexplained; Lucy's move is a fact, never a feeling.

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
the old man lowers himself onto the stool Lucy brings without looking at it; the woman gives both names (`{n3}`,
`{n4}` in l_join2_2); five at the fire; the pot goes round twice and comes back light. Special: the yes_but is the pot,
said as a fact.

**l_seed** (SL10). Facts: `{n3}` turns a strip of ground at the stone's edge with a flat stone, edges it, lays seed out on
a cloth in rows, and ties it up again unplanted. Special: no reason, no hope said.

**l_old_watch** (SL11). Facts: `{n4}` settles at Lucy's watch fire with his leg out straight and feeds it; Lucy stands
there a while, then goes back to the roots.

**l_stones_1..3** (`hearth_stones` stages). Facts: stones lifted off the camp stone hot, set round the pot.

**l_night_6** (night 6's first item). Facts: five round the fire; the player banks it for the night. States: present
mostly (A29 follows).

### B7 (`b7.toml`)

**l_b7_1 to l_b7_3** (A29, B7, H each). Fields: down · yes_but · grim · stores · pays the near question. Canon
C-beat-7, C-beat-100. Facts: wolves at the edge of the firelight, more eyes than can be counted; they don't come in.
States: night 6, present (A29 is a tap). Special: the first wolf a line may show.

**l_stand_1, l_stand_2** (`b7_stand`'s completion, "Drive them off"). Facts: a plain fight that goes fine: one wolf
turned with a burning brand, the rest gone into the dark; behind, the rack stripped while it went. States: present, or
on return after the strip's clock (the hang gone either way). Special: the fight is easy; the loss is the rack, said
last.

**l_combat_first** (the `combat` feature). One line under the new cards. Facts: the spear, the hunt.

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

### Fights, pests and hurts (pools)

From the line-state lists of combat-plan item 9. Each pool gets eight lines per writer, any order, true for any count:

- **fight_hunt_won**, **fight_hunt_lost**: the hunt, one plain line each.
- **fight_rats_won**, **fight_rats_lost**; **fight_crows_won**, **fight_crows_lost**: the pests at the stores; a lost
  one says only what is short ("the roots are fewer").
- **fight_summary**: the arrival queue's count line for a long absence (`{won}`, `{lost}`, the runner's name slot).
- **l_hurt**, **l_poultice**, **l_healed**: the chip shows; a poultice of clay and roots; it clears by itself.

### The Camp, finds and Arcana levels

**l_camp_11** (stew holds 18), **l_camp_12** (lifted by G2: smoked holds 36).
**l_find_ashroot_bank** (Foraging 12), **l_find_pot_hook** (Scavenging 18), **l_find_hoop** (Scavenging 21),
**l_find_dry_birch** (Woodcutting 20), **l_find_thick_stew** (Cooking 6), **l_find_old_wolf** (Melee 3),
**l_find_dry_kindling** (Arcana 5): one line each, by the mix, any visit; never wolves at the camp's edge, never the
stone's heat past what the player's hand does, nothing of week 2.

## Labels: the voice pass's, not the writers'

- **Cards:** c_woodshed, c_n2_watch, c_sit_up, c_hand_on_stone, c_hearth_stones, c_make_bay2, c_n3_build_bay,
  c_n3_forage, c_n3_gather, c_n3_dig_bed, c_n4_watch, c_n4_mend, c_bank_fire, c_b7_stand ("Drive them off"),
  c_hunt_wolf, c_make_spear, c_poultice, c_pelt_bedding
- **Upsides** (UI register, numbers): up_woodshed ("Dry wood holds 54, was 36"), up_hearth_stones ("Stew 4 a pot, was
  3"), up_make_spear ("Hunting side +150%"), up_pelt_bedding ("Rest +20%"); Arcana pays ("Rack +10%", "Smoking +25%");
  Melee pays ("Hunting side +10%")
- **Chips:** chip_fogbound ("rack slower"), chip_hurt ("hands slower")
- **Offers:** o_pair, a_make_room2, a_let_her_build, their cost lines (`{d}`); o_pelt, a_pelt_give, a_pelt_keep
- **Fights:** side_hands, side_larder, side_rack, threat_lone_wolf, threat_ashrats, threat_crows (as the page's
  strength rows), the odds' unknown state ("Unknown until fought" or the pass's shorter word)
- **Rows and stores:** lane_n3, lane_n4 (before their names), their named forms; store_pelt, store_hurt; skill_arcana,
  skill_melee; the mix offer on the full damp wood line for the stone ("add hand on stone, held at 12")
- **Aims:** aim_dry, aim_stone, aim_pair, aim_keep
- **End cards:** dayend4_*, dayend5_*, the B7 card, dayend6_* (the edge of week 1's content, `waits-and-ends.md`)
- **Never drawn:** store_night_5..7, store_b7_clock, store_r1_clock, the tallies, store_arrivals

Two to check first: **o_pair** sits on screen across absences and neither answer may read as the right one; **o_pelt**
is a small thing asked by someone new, and "keep it" must read as an ordinary answer, not a refusal.
