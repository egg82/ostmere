# Week three: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `week-three.md` (beats, side layer, canon ids); the data
will be `day_fifteen.toml`, `day_sixteen.toml`, `day_eighteen.toml` and `day_nineteen.toml`, where every key below
reads UNWRITTEN. The states below are the design's expectation. **Before the writers start**, regenerate them with the
simulator's `--lines` (`docs/design/week-three-plan.md`, item 6) and replace this file's "States" notes with the
generated lists; a line written against the expectation alone is a draft.

## How the lines get written

As weeks one and two, unchanged: three blind proposers (Sonnet), one lens each (below), every key plus one alternate per
key marked H; a critic scores the drafts blind on `rubric.md` plus *true in every listed state?*; the lead picks line by
line; code checks length, the must-nots as a scan, and three-word echoes against content prose and every shipped line
before them; a fresh agent's voice pass reads every picked line and label in player order after day twelve's last
lines, and writes the labels. One batch per chapter, in chapter order; the journal's notes are a fifth batch (below);
the yes pool is a sixth, small, after day sixteen's (below).

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases.

**This week's risk is warmth.** The Clear is the lightest week so far (sun, a hall, a full table, singing, people
arriving), and model drafts slide toward the bright ending the beat did not earn: a closing line that says the town is
a home now, the sun as hope, the singing as healing. Every warm beat here has its cost in the same moment (B14's pot,
T7's rest, T13's second mark), and the cost is the last fact of the moment, stated as a fact. The critic's "Brighter
than planned?" row is the one to read first.

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase, plain. One or two short sentences. A turn the
  reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, per chapter.
- **True in every state.** Most of this plays on return. Never say when, in real time, anything happened, or how long it
  took.
- **People:** Lucy by name; the shipped slots `{n2}` (Martin), `{n3}` (Mary), `{n4}` (Edward), `{n5}`-`{n7}`; the three
  women as "three women" until l_choir_2 gives `{n8}`, `{n9}`, `{n10}`; the pair as "a man" and "his sister" until
  l_pair_2 gives `{n11}` and `{n12}`; the starer only ever as "a newcomer", "the newcomer" or "him" where clear, **never
  named, never a slot**; the family's child as "the child" or "their child", never named. What each does, in active
  voice. Lucy never grateful, never sweet, never says much. Light-tier people are ordinary: no backstory past what they
  carry.
- **Fights:** plain, one short line, won or lost, never gory; the deer hunt told as a way of life. A long absence folds
  into one count line (pools, below).
- **Must-nots (all lines):**
  - no "magic", "spell", "mage", "arcana", "spellcraft", Chequer, keels, holders, faith, the burn, Drift, Clear, Still or
    any season name; the weather is described, never named; the sun is "the sun" or "a pale disc", never hope;
  - never "again", or any hint of having been here before, including at the snares and the field stone; never that the
    camp stone was cut, set or is anything but a warm stone; the rime stopping short of it is a fact, never why;
  - the field stone (B15): what the hand did and what the stone and the ash did, nothing about why the camp stone is
    different, no "rule", no lesson stated;
  - the three women's rest (T7): the bar where nobody sings is described as a pause they wait out; never a fourth
    voice, never a count, never who is missing, never that anyone is;
  - the starer (B16): he looks; he says nothing; no line says what he wanted, who he was, that he knew the player, or
    that he tied the snares; the snares are re-tied "with the knot your hands tie" at most, never "your knot", never
    who taught it;
  - the cutter (B17): nothing in any line may suggest he could have been kept back, found, or saved, by anyone, or that
    anything the player did or had matters to it; nobody says he is dead; the wolves' prints go "either side" of his,
    never "with", "after", "hunting" or "escorting"; never that the wolves sat, waited or were like the others;
  - the greycoats: in lines they are wolves; the sitting is a fact ("two sit outside the gate"), never compared to S3's
    wolf or the margin note, never said to be waiting for anything;
  - their child (`decisions.md`, "Never"): there, plainly, never working, never a cost or counted among mouths or
    hands, never in danger in these lines (j_ridge's walk included);
  - the board (T13): plain; the name is said, not quoted; never "tally" as a Chequer word; no line compares the two
    marks;
  - no line judges either answer to O-road, O-choir or O-pair, or any job's yes or no;
  - no proper noun but Lucy and the name slots.

## Voice exemplars (shipped)

Read the exemplar tables in `day-two-lines-brief.md` and day twelve's shipped lines in `day_twelve.toml` (its S4 set
especially, which B13 follows). Reuse no phrase from them; three-word echoes are checked in code.

## Lenses

`python3 content/team/draw_lenses.py week-three-lines --writers 3`:

| Writer | Lens |
|---|---|
| writer-1 | what it sounds like when nobody is talking |
| writer-2 | the joke nobody laughs at |
| writer-3 | what is eaten, and who goes without |

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, anything special.

### Week two's last visit (S4's, in `day_fifteen.toml`)

**l_floor_paced** (the hall shown, keyed on `week_two_end`). Facts: in the dark Lucy paces out a long floor beside the
bays, counting under her breath; she stops at nine. States: present on every route (A32 is a tap). Special: the hall is
never named; the card says what it is; the count is paces, not people, and the line does not say so.

### Day fifteen (15a-15f)

**l_b13_1 to l_b13_3** (B13, H each). Fields: up · wonder · none. Canon C-beat-13. Facts: the wind turns in the night
and comes cold from the far side of the valley; by morning a pale disc shows through a thinner sky; everything has a
shadow, posts, the hut, the people; the family stop in the open and look up at it a long time; Lucy, `{n2}` and `{n4}`
keep working and don't look up; green in `{n3}`'s dark beds by noon. States: on return on typical, sharp and whenever;
the babysitter present. Special: the shadows are the wonder, not the sun; the ones who don't look up are the last
fact, unexplained.

**l_sow** (SL22). Facts: `{n3}` unties the seed bag counted out in the warm weeks and sows her dark ground in rows,
pressing each seed in with her thumb; the bag empty by the end. Special: never what will grow.

**l_frost_1, l_frost_2** (T1, H). Fields: down · grim · opens the near question. Facts: night; under the clear sky the
cold comes down hard; rime on everything past the warm ground, the beds at its edge white; the hut's door frozen into
its frame; the family come out to the fire wrapped in all they have; nine round one fire three deep till morning.
States: on return (nearly always). **l_night_15**: the light going; cold coming down.

**l_deer** (T2). Fields: up · wonder. Facts: first light; four small deer at the edge of the warm ground, heads low,
grazing the rime off the ash where it melts; when `{n2}` stands up they are gone. Special: nothing ominous; the deer's
page carries the facts, the line the moment.

**l_beams** (SL23). Facts: under the ruin's fallen roof the old beams are sound to the heart under their char, adzed
square, too heavy for one person.

**l_walls_1, l_walls_2** (T3, H). Fields: up · yes · warm · advances. Facts: the hall's walls stand to the eaves, long
enough that the fire at its end looks small; the child runs from one end to the other and back, and does it again.

**l_stage_hall_1 .. l_stage_hall_8** (the hall's stages; the last carried by B14). Facts: posts, wall-stakes, beams
up, the roof lashed, hides at the doors. No two share a verb.

**l_b14_1 to l_b14_3** (B14, H each). Fields: down · yes_but · warm · stores · pays the near question; canon C-beat-14,
C-beat-134. Facts: the roof on, the door hung; everyone inside at one long table for the first time, the fire at its
end; `{n3}` dishes out; the pot goes round once; Lucy sits where she can see the door; everyone can see the bottom of
the pot from where they sit. States: present or on return. Special: the week's first big moment; the pot's bottom is
the "but" and the last fact.

**l_camp_17** (barley holds 36). **l_table_first** (the table's lesson line, UI voice: the voice pass's).

**The asks** (`o_door_ice`, `o_sun_rack`; their `a_*` labels and costs): facts and answers in `week-three.md`, "The
asks (day fifteen)". As week two's: who asks, in their own active voice, and neither answer judged.

### Day sixteen (16a-16i)

**l_road_ask** (O-road's line, with B14). Facts: Lucy says the old road runs under the ash past the ridge and somebody
has to walk it and mark where it goes; she looks at the player. Special: the two answers are the player or `{n2}`;
the line prefers neither.

**l_road_marked** (SL24, both answers). Facts: past the ridge, under a yard of ash, the old road runs as a straight
dent going away over the next hill, wider than a cart. Special: true whoever walked it; never "you" as the walker.

**l_rows_black_1, l_rows_black_2** (T4, H). Fields: down · no · grim · stores · opens the near question. Facts: a clear
night; the frost got in under the covers at the beds' far end; by morning the outer rows black and limp; `{n3}` pulls
them up and carries them to the fire without a word.

**l_hall_hearth** (SL25). Facts: a hearth of stones laid at the hall's end where the fire was on bare ash.

**l_rime_stone_1, l_rime_stone_2** (T5, H). Fields: up · wonder · advances. Facts: morning; the rime lies white on
every stone in the valley, the field stones by the beds included, and stops a hand's width short of the camp stone all
the way round, as if drawn. Special: no line says why or what the stone is; "as if drawn" is the furthest a line goes.

**l_covers_torn** (T6). Fields: down · no · grim · stores. Facts: the hides froze to the beds in the night; lifted in
the morning, they tear along the frost line; half go to the fire.

**l_sun_back** (SL26). Facts: in the pale sun `{n4}` works stripped to the waist with his back to it; he says it's
warmer than it looks. Special: his line, his words, active voice.

**l_try_stone_fail** (A35's failed tap, before it is ready: the voice pass's; one plain sentence).

**l_b15_1 to l_b15_3** (B15, H each). Fields: up · no · wonder · time · pays the near question; canon C-beat-15,
C-beat-135. Facts: the player kneels at the beds with a hand on a field stone, the way they warm kindling at the fire;
the stone goes cold under the hand, colder than the frost; nothing warms; when the hand comes away there is a fist of
grey ash on the stone where it lay; the camp stone has never gone cold. States: A35 is a tap: present. Special: the
last line is the camp stone, plainly, with nothing after it.

**l_road_1 .. l_road_10** (the road's stages; the last carried by B17). Facts: ash shovelled off, the old bed found, the
stretch laid with stones, markers driven; stage 6 the bridge over the warm stream. No two share a verb; no wolf in them.

**Lucy's jobs** (`j_steps`, `j_smoke_hole`, `j_wedged`, `j_cellar_steps`, `j_snares`, `j_ridge`, `j_tally`,
`j_frames`; text, yes and no labels; the job's card line on its finish): facts in `week-three.md`, "Lucy's jobs".
Lucy's line is one sentence of what needs doing and that somebody has to; it never asks the player by name and never
says please. The no label is the voice pass's. Special: `j_ridge`'s walk is quiet; the child sees the sun; nothing
happens on the way.

**The yes pool** (a sixth batch): one line lands after every job's yes, drawn from a pool by a shuffle bag (the fights'
pools' code, keyed by save and job), so no two jobs in a row get the same line. Eight lines per writer. The shape: what
the player just agreed to, seen from outside a beat after the yes; the joke is the player's own reflex to take the job,
and only ever that (`decisions.md`, "You're just a dude": the joke is only about choices the player made). Never "of
course", never "again", never that anyone else could have done it, never that Lucy expected it. No quoted model line
goes in this brief: the shipped ones are the voice, and an example here would become the template.

### Day eighteen (18a-18f)

**l_first_working** (SL27). Facts: the player lays one hand on the camp stone and the other flat on a bed; the rime goes
off the bed like breath off glass; the hand on the bed comes away grey. Special: never what was done or how; never a
word for it.

**l_choir_1, l_choir_2** (T7, H). Fields: up · warm · people · opens the near question. Facts: at dusk three women at the
hall's door, who followed its light down the valley; they don't ask; they sing for their supper, three parts; in every
verse a bar where nobody sings and they wait it out together before going on. l_choir_2 gives `{n8}`, `{n9}`, `{n10}`.
Special: the waited bar is the last fact of l_choir_1; nothing explains it.

**l_choir_beds / l_choir_road** (each answer). Facts: where they go to work in the morning.

**l_pot_out** (T8). Fields: down · no · grim · stores. Facts: at the table `{n3}` counts heads against the pot, ladles,
serves herself last, and the ladle comes up empty; she sits down with the bowl anyway.

**l_pair_1, l_pair_2** (T9, H). Fields: up · wry · people · advances. Facts: a man and his sister come in along the old
road, an axe on his shoulder; he has cut roads, he says; he looks along the marked line to the ridge and says it's
crooked; in the morning he is out on it before anyone. l_pair_2 gives `{n11}` and `{n12}`. Special: the wry is at the
line, whoever marked it; true in both O-road states.

**l_pair_beds / l_pair_pot** (each answer).

**l_starer_in** (the fifteenth arrival). Facts: a newcomer comes in at supper and sits at the table's end; nobody asks
him anything. Special: no look yet; the look is B16's.

**l_b16_1 to l_b16_3** (B16, H each). Fields: down · dread · trust · pays the near question; canon C-beat-16,
C-beat-136. Facts: the newcomer who sat down to supper stared at the player across the table the whole meal and said
nothing; in the morning his place is empty, his bowl unwashed; the snares in the near runs re-tied in the night, every
one, with the knot the player's hands tie. States: on return (nearly always). Special: in that order; the knot is the
last fact; never "your knot".

### Day nineteen (19a-21a)

**l_far_hills_1, l_far_hills_2** (T10, H). Fields: up · wonder · opens the near question. Facts: from the road's head on
the ridge, in the clear air, a line of hills on the far side nobody in the valley has seen, grey, a long way off; the
cutter looks at them a while and goes back to cutting.

**l_cut_night** (T11). Fields: up · yes · warm. Facts: the cut goes over the ridge a stretch a day, the cutter ahead of
everyone, the rest behind him with shovels (who they are depends on O-choir's answer and the split: never
named); at night it shows as a pale line in the starlight from the hall's door.

**l_cloth** (SL28). Facts: `{n12}` ties a strip of cloth to every marker stake he set, so the line shows in the dark.
Special: never why beyond that; it is written before B17 and must read the same after.

**l_b17_1 to l_b17_3** (B17, H each). Fields: down · yes_but · grim · people · pays the near question; canon C-beat-17,
C-beat-137. Facts: on the last morning `{n11}` went out ahead alone to start the last stretch and did not come back by
dark; when the last stretch is laid, his axe is in the last stump of it; his prints go on down the far side, and a
wolf's either side of his, close, all the way down; past the hill the world is grey as far as anyone can see. States:
present or on return. Special: the week's ★; the grey is the last fact; nobody in a line says he is dead.

**l_map_first** (the map's lesson line, UI voice: the voice pass's).

**l_lamp_out** (T12). Fields: down · grim · opens the near question. Facts: at dusk `{n12}` takes a lamp along the road to
its end and sits by it facing the far side; still there when the light goes.

**l_night_21**. Facts: the light going; stars; a lamp at the end of the road.

**l_sit_road_end_fail** (A38's failed tap before night: the voice pass's).

**l_t13_1 to l_t13_3** (T13, H each). Fields: up · yes_but · warm · pays the near question. Facts: night; the player
walks out along the road in the starlight and sits with her by the lamp till it burns down; at first light she gets up
and walks back with the player; at the fire she says his name to Lucy, and Lucy cuts a second mark on the board, his
name beside it. States: night 21, present (A38 is a tap). Special: the week's quiet close; the name beside the mark is
the last fact; never what the name is, never that the first mark has none.

**l_camp_18** (cleared holds 36).

**The finds** (Foraging 15, Woodcutting 25, Scavenging 25, Cooking 11, Melee 8, Spellcraft 3): one line each, by the
mix, any visit. No find names the starer, the knot, the cutter, the wolves at the gate, or anything of week four.

### Fights (pools)

From the line-state lists of item 6. Eight lines per writer per pool, any order, true for any count:

- **fight_deer_won**, **fight_deer_lost**: the deer hunt, plain; a lost one is the deer getting away, never a hurt.
- **fight_pack_won**, **fight_pack_lost**: unchanged pools from week two; the threat step adds none.
- **fight_summary**: unchanged.

## The journal's notes (a batch of their own)

The register is not the lines': `decisions.md`, "The journal is the player-character's own voice" and "Art": first
person, lowercase, past tense, fragments jotted at different times, a later line under an earlier one, dry and
clinical, sometimes wrong; mostly mundane (sizes, counts, guesses); at most one ominous note per page; numbers sit
beside the notes in the UI font and are never written into them. Must-nots as the lines', and: no note says what the
wolves are, names the starer, or answers the margin.

| Note | Page | When | Facts |
|---|---|---|---|
| n_deer_1 | ash-deer | T2 | small, short in the leg, head low; graze rime where it melts at the warm edge; gone at any movement |
| n_greycoat_1 | (the player's word; the voice pass's title) | the first pack fight after the Clear's step | one dead at the gap; the toes on the forefeet longer than a wolf's; the others sat down before they ran; its one ominous note |
| n_ground_2 | the warm ground (day three's) | T5 | rime on every stone but this one; stops a hand short all round (a later line under n_ground_1) |
| n_ground_3 | the warm ground | B15 | a field stone goes cold if its heat is taken; this one hasn't; ash on the hand both times (a later line; may cross out a guess in n_ground_2) |
| n_day_b13 .. n_day_b17 | days (`e_days_7`) | each spine beat's step | the beat retold after the fact, in the journal's voice, the facts of its row and nothing past them |

## Labels: the voice pass's, not the writers'

- **Cards:** c_hall, c_pull_beams, c_n3_sow, c_reap (and the town card's), c_barley_stew, c_cover_beds, c_n3_cover_beds,
  c_hunt_deer, c_hall_hearth, c_mark_road, c_n2_mark_road, c_cut_road, c_shovel_road, c_clear_road (the town card's),
  c_try_stone ("Warm the beds from a stone" or the pass's shorter), c_warm_beds, c_road_cloths, c_sit_road_end ("Sit
  with her" or the pass's), each job's card
- **Upsides** (UI register, numbers): up_hall ("Rest +10%" at stage 4, "Rest +20%" finished), up_hall_hearth ("Rest
  +10%"), up_road_cloths ("Road +25%"), the table's line ("2 smoked an hour; a fed table draws travellers" in the
  pass's words), Spellcraft 4's pays
- **Chips:** chip_frosted ("beds slower")
- **Offers:** o_road and its two answers by name slot; o_choir, o_pair and their answers; each job's yes and no labels
- **Order cards:** the hall's ("build when stakes reach 16"), the road's ("lay the road when cleared reaches 12"), her
  sowing's, the reap cards' ("over 12 ripe"), the covers' ("when frosted"), the working's ("when frosted, warm the
  beds")
- **Fights:** threat_ash_deer
- **Rows and stores:** store_beams, store_ripe, store_barley, store_cleared, store_deer_down ("deer near the warm
  ground" or the pass's), store_ruin_beams ("beams in the ruin" or the pass's); lane_n8..n12 before their names
- **Journal:** the ash-deer page's title, the greycoat page's title (see above)
- **The map:** its sheet's button, its lesson line, the one label it draws for the valley (the place's name is canon's:
  `world.md`, "the Hollow"; whether the map shows it yet is the pass's call, by "names appearing as you reach them")
- **Aims:** aim_roof, aim_table, aim_road, aim_after
- **End cards:** dayend21_* (the edge of week three's content); week two's dayend14_2 rewritten now it is no longer the
  edge
- **Never drawn:** store_frost_left, store_grow_left, store_roof_wind_left, store_clear_clock, store_rime, store_meals,
  store_starer_clock, the floors' clocks, store_deer_lost

Two to check first: **l_b17_1 to l_b17_3** must leave both readings open (he walked on; he was taken) and close on the
grey, not on him; **l_choir_1** must work as a song before it works as an absence.
