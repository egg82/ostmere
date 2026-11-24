# Week four: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `week-four.md` (beats, side layer, canon ids); the data
will be `day_twenty_two.toml`, `day_twenty_three.toml`, `day_twenty_five.toml` and `day_twenty_seven.toml`, where every key
below reads UNWRITTEN. The states below are the design's expectation. **Before the writers start**, regenerate them with
the simulator's `--lines` (`docs/design/week-four-plan.md`, item 7) and replace this file's "States" notes with the
generated lists; a line written against the expectation alone is a draft.

## How the lines get written

As weeks one to three, unchanged: three blind proposers (Sonnet), one lens each (below), every key plus one alternate per
key marked H; a critic scores the drafts blind on `rubric.md` plus *true in every listed state?*; the lead picks line by
line; code checks length, the must-nots as a scan, and three-word echoes against content prose and every shipped line
before them; a fresh agent's voice pass reads every picked line and label in player order after day nineteen's last
lines, and writes the labels. One batch per chapter, in chapter order; the journal's notes are a fifth batch; the
forgetting pool and the death pool are a sixth, small, after day twenty-three's (below).

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases.

**This week's risk is the death.** Model drafts of B20 reach for the ceremony: a last thought, a light, a line about what
death is, a moral on waking. The beat is wry: the player is killed by a pig in the fog and wakes up cold with ash in
their mouth, and Lucy says two words. Every death line after it is smaller still. The second risk is the stillness:
"silence" and "eerie" stated instead of a sound that carries. The critic's "Says the feeling?" row is the one to read
first, then "Brighter than planned?" for I13.

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase, plain. One or two short sentences. A turn the
  reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, per chapter.
- **True in every state.** Most of this plays on return. Never say when, in real time, anything happened, or how long it
  took.
- **People:** Lucy by name; the shipped slots `{n2}` (Martin), `{n3}` (Mary), `{n4}` (Edward), `{n5}` (Thomasina), `{n6}`,
  `{n7}`, `{n8}`-`{n10}` (the three women), `{n12}` (the cutter's sister); `{n13}` is the stranger, "the stranger" or
  "they" until l_named gives `{n13}`; the fiddler and his wife "a man" and "his wife" until l_fiddle_2 gives `{n14}` and
  `{n15}`; the walkers "four" until l_walkers_2; the widowers only in the people bands' mention; the bedesman "a stranger"
  until l_b21_2, then "the bedesman" or `{n23}`; their child as "the child", never named. The cutter (`{n11}`) by name
  only in I13's line and I11's, where the name is said, never quoted. What each does, in active voice. Lucy never
  grateful, never sweet, never says much. Light-tier people are ordinary: no backstory past what they carry.
- **Sorrel is "they"** in every line, as `cast.md` has it.
- **Fights:** plain, one short line, won or lost, never gory. A long absence folds into one count line (pools, below).
- **Must-nots (all lines):**
  - no "magic", "spell", "mage", "arcana", "spellcraft", "wayfinding", Chequer, keels, holders, faith, the burn, Drift,
    Clear, Still or any season name; the weather is described, never named; never "silence", "silent", "eerie",
    "uncanny" or "still" as a mood word (a sound that carries is the stillness);
  - never "again" about the place or the player's past, any hint of having been here before; never that the camp stone
    was cut, set, or is anything but a warm stone, at B20's waking and SL36 included;
  - the walked elk (B18): pathos, never horror; it walks very slowly toward warmth; no line says what moves it, that it
    is dead in so many words past "dead", or that a person could walk so; the meat is burned, never "infected";
  - Sorrel: no line says or shows that they forget, why they won't come in, take a hand or a name, or what is under
    their sleeves; they thank people; they are never strange in a line, only apart;
  - the starer: nothing; no knot, no snare, no man who stared, no one who comes and goes at night (the bowl at I3 is
    Sorrel's, and must never read as his);
  - the death (B20, SL34, the death pool): what the fog did and where the player woke, nothing between; no light, no
    darkness, no thought, no pain named, no "you died" in the beat's lines (Lucy's two words say it); the boar is a
    pig, plain; never that the player can't die, never "again" (the second time is "the second time");
  - the forgettings (pool): small, ordinary, true for anyone; never a recipe, a store, a person's name or face, a place
    the player needs; never sad in the wording; never that something is being taken;
  - the bedesman: no "priest", "prayer" (the ring is "the words"), "god", "bless" except the beat's one "a blessing";
    never that the warmth listens, answers or is anything; "never thank the warmth" is said once, at B21; "it keeps
    accounts" may follow it once and never again;
  - the names (I11-I13): said, never quoted; no line counts them; no line says the town forgets, or that a name is kept
    or spent; the first mark's silence is a pause, never "for him", never "the nameless";
  - Lucy's names (I12): she gives hers and stops; never how many, never whose, never that she lost anyone;
  - the singing (SL30): the song carries; Lucy's hand stops it; never a reason, never the rest in their songs;
  - the cutter: nothing suggests he could come back, be found or was ever not dead; his sister looks at the road once
    (SL35) and the line ends on the stakes;
  - their child: there, plainly, never working, never in danger, never a cost;
  - no line judges any answer to O-fiddle, O-walkers, O-widowers, O-book or any job's yes or no;
  - no proper noun but Lucy and the name slots.

## Voice exemplars (shipped)

Read the exemplar tables in `day-two-lines-brief.md` and day nineteen's shipped lines in `day_nineteen.toml` (its T13
set especially, which I1 follows). Reuse no phrase from them; three-word echoes are checked in code.

## Lenses

`python3 content/team/draw_lenses.py week-four-lines --writers 3`:

| Writer | Lens |
|---|---|
| writer-1 | what the hands are doing |
| writer-2 | the thing everyone has stopped mentioning |
| writer-3 | the rule someone keeps breaking |

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, anything special.

### Week three's last visit (in `day_twenty_two.toml`)

**l_walk_shown** (the walk shown, keyed on `week_three_end`). Facts: at first light, back from the road's end, the road
going on past where it was laid, down into the grey. States: present on every route (A38 is a tap). Special: after
T13's close, so quiet; nothing about the cutter.

### Day twenty-two (22a-23c)

**l_i1_1 to l_i1_3** (I1, H each). Fields: down · dread · none. Facts: in the night the wind drops and doesn't come back;
in the morning the ash hangs in the air without falling; fog in the low ground over the stream and the beds; the hall's
smoke goes straight up; the stream at the valley's far end can be heard; a crow on the hall roof clicking; nobody talks
much. States: on return on typical, sharp and whenever; the babysitter present. Special: the sounds are the line; the
last fact is the people keeping their voices down, unexplained.

**l_b18_1 to l_b18_3** (B18, H each). Fields: up · yes_but · wonder · stores; canon C-beat-18, C-beat-151. Facts: over
the ridge the grey becomes a forest of dead trunks standing as they died; shelf fungus up them like stairs, some wider
than a man is tall; on a warm patch by the old road a dead elk walking very slowly, fungus along its spine; drag-marks
from it to every warm patch in sight; at dusk `{n2}` and `{n4}` drag in an elk they brought down near the trees; `{n3}`
turns its back to the fire, sees the fungus along the spine, and it goes on the fire whole. States: on return (the walk
lands away) or present. Special: wonder first; the burned elk is the "but" and the last fact.

**l_map_ashwood** (the map's new place, UI voice: the voice pass's).

**l_fish** (SL29). Facts: on the warm stream the fog lies flat on the water; under it, with no wind, pale fish rise and
hang near the surface; they can be lifted out by hand.

**l_film_1, l_film_2** (I2, H). Fields: down · no · grim · stores. Facts: the ash settles out of the air onto anything
left open; by noon the meat on the racks has a grey film on it; `{n3}` scrapes a strip with her thumbnail, looks, and
puts it aside. Special: never why nobody eats it; the chip's word and hint are the voice pass's (UI register).

**l_bowl** (I3). Fields: up · warm · opens the near question. Facts: a bowl left at the fire's edge with the last of the
stew is there in the morning, empty, rinsed, set upside down on a stone. Special: who is never guessed at.

**l_pace_1, l_pace_2** (I4, H). Fields: down · dread · advances. Facts: on the walk back, at the trees' edge, someone in
the fog keeps level with you, too far to see; stops when you stop; walks on when you walk on.

**l_b19_1 to l_b19_3** (B19, H each). Fields: down · no · warm · pays the near question; canon C-beat-19, C-beat-152.
Facts: at dusk a stranger walks in behind you, a coat with the sleeves pulled down over the hands; sits across the fire
from everyone; takes the bowl `{n3}` hands them, and the blanket; Lucy shows them a place in the hall; they thank her
and sleep by the fire outside; asked their name, they say they don't have one to give. States: present or on return.
Special: gentle; the "no" is the place in the hall, said kindly; the last fact is the name.

**l_stage_post_1 .. l_stage_post_12** are day twenty-three's (below).

**The finds** (Wayfinding 3 and 5; the week's others below): one line each, any visit.

### Day twenty-three (23d-25a)

**l_named** (SL31). Facts: `{n3}` calls the stranger `{n13}` after the sour leaf by the warm stream, because they ate a
handful of it; by supper everyone does; they don't answer to it the first few times. Special: the slot carries the name,
so the line never spells the leaf's name out.

**l_fiddle_1, l_fiddle_2** (I5, H; O-fiddle's line). Fields: up · yes · warm · people. Facts: a man and his wife come down
the road from the ridge; a bundle on his back wrapped in cloth and tied; at the fire someone asks; a fiddle, he says, and
doesn't untie it; not in air like this. Special: l_fiddle_2 gives `{n14}` and `{n15}`; nobody plays this week.

**l_cache_1, l_cache_2** (I6, H). Fields: down · no · grim · stores · opens the near question. Facts: the cache at the
warm patch where the road meets the trees, rooted out in the night; sacks torn, the meat gone; the ground churned; a
pig's tracks, split-hooved, wider than a hand. **l_post_shown**: Lucy: somebody should put a post out there with a store
that shuts. Special: the post's line is Lucy's, plain, no "we".

**l_book_ask** (O-book's line). Facts: `{n13}` watches you write in your book at the fire, the way you'd watch someone
eat. Special: prefers neither answer. **l_book_yes**, **l_book_no** (each answer): you cut birch bark into leaves and sew
them into a hide; or you close your book. **l_book_given** (at `bind_book`'s finish): `{n13}` takes it in both hands,
and says thank you, and doesn't open it while you're there.

**l_stir_air** (SL32). Facts: one hand flat on the stream where it runs, the other held over the racks; the air over the
meat moves once, like a breath; the film lifts and blows away; the hand in the water comes out grey. Special: as B15's:
what the hands did, what the air and the ash did, nothing about how.

**l_ring_1, l_ring_2** (I7, H). Fields: up · yes · warm · advances. Facts: a ring of charwood stakes at the warm patch,
the next sack hung inside it; in the morning the ground outside the ring churned all the way round; the sack where it
was.

**l_stage_post_1 .. l_stage_post_12** (the post's stages; the first carried by I7, the last by B22 in week five). Facts:
charwood stakes, a ring, walls, a store with a door that shuts, a latch, a roof, a hide door. No two share a verb.

**l_rooting** (SL33). Facts: night, no wind; the town hears them in the wood over the ridge, rooting, grunting, wood
breaking, as near as the yard; people come to the hall door and listen; nobody goes out. **l_night_24**: the light
going; fog pale under the hall's light.

**l_go_ask** (A39's line, with SL33's visit). Facts: Lucy, in the morning, to the room: somebody has to go after them;
she doesn't look at anyone; she looks at you. Special: the card is the yes; the line never asks a question the player
answers with words.

**l_go_wallow_fail** (A39 tapped before its hour: the voice pass's).

**l_b20_1 to l_b20_5** (B20 ★, H each). Fields: down · no · wry · time · pays the near question; canon C-beat-20,
C-beat-153. Facts: in the fog under the trees every sound is close and from nowhere; rooting to the left, then behind,
then all round; the boar comes out of the fog from the side you weren't facing; then: first light, the warm stone at
camp, you lying on it, cold through, ash in your mouth; Lucy sitting by the fire; she looks a long while and says:
"Kept, are you."; next morning your name is first on her list, beside the worst job on it. States: on return (the step
runs an hour) or present. Special: the week's ★; nothing between the boar and the stone (the cut is the death); Lucy's
two words are the only speech and the only place the death is named; the list is the last fact and the joke.

**The death pool** (`fight_hunt_boar_death`, eight lines a writer): a lost boar hunt: the fog, the side you weren't
facing, and waking at the stone; true for the second death and the twentieth; never the same wake twice in a row;
SL34's is the second time (below).

**The forgetting pool** (`n_forget_1` .. `n_forget_12`, journal voice, below).

### Day twenty-five (25b-27a)

**l_bowl_set** (I8). Fields: up · wry · opens the near question. Facts: at supper `{n3}` dishes your bowl and sets it at
your place, as every night; nobody says anything about the morning; `{n2}` passes the bread; `{n4}` asks if you're going
out after the pigs again. Special: "again" here is about the pigs, and the only "again" allowed this week.

**l_walkers_1, l_walkers_2** (I9, H; O-walkers' line). Fields: up · yes · warm · people. Facts: four come in out of the
fog at the gate, who walked toward the hall's light from the south, not kin, met on the road; one asks why your coat is
torn down the back and stiff; someone tells her; she shrugs: kept, then; asks where they sleep. Special: the shrug is
the line; l_walkers_2 can give the group's word.

**l_thanks** (I10). Fields: down · dread · trust. Facts: in the morning `{n5}` kneels at the camp stone where you woke,
lays her hand flat on it, and says thank you to it, quietly, as you'd thank someone for a kindness. Special: never why
it is wrong; it isn't yet.

**l_b21_1 to l_b21_4** (B21, H each). Fields: up · dread · trust · pays the near question; canon C-beat-21, C-beat-154.
Facts: a stranger walks in along the road, stopping at every warm stone to kneel and lay both hands on it, the camp
stone last; at the fire looks at you a long time, the only one who does; says it's a blessing, and means it; when `{n5}`
says she thanked the stone, takes her hands off it: never thank the warmth; it keeps accounts; that night a ring at the
fire, hands joined, the words said; `{n13}` stands outside it and won't take the hand held out. States: present or on
return. Special: l_b21_2 gives "the bedesman"; the last fact is `{n13}` outside the ring.

**l_camp_19** (charwood holds 36).

**SL34's line, l_second_wake**. Facts: the second time, you know the fog is coming before it does; it makes no
difference; you wake at the stone; Lucy has left a blanket on it.

**l_sister_road** (SL35). Facts: `{n12}` watches you come up from the stone in the morning; for a moment she looks at the
road; then she goes back to the stakes.

### Day twenty-seven (27b-28d)

**l_board_1, l_board_2** (I11, H). Fields: down · no · grim · opens the near question. Facts: the bedesman at the board by
the fire, reading the marks with a finger; at the second, says `{n11}`'s name aloud; at the first, with nothing beside
it, asks Lucy whose it was; nobody knew; who sat up with him; Lucy did; what was he like; she thinks; he had a cough.
Special: the cough is the last fact and is said once in the game.

**l_hands** (SL36). Facts: the bedesman kneels at every warm stone in the valley, both hands flat, a moment each; at the
camp stone they keep them there longer, and get up saying nothing.

**l_names_given_1, l_names_given_2** (I12, H). Fields: down · grim · advances. Facts: door to door, the same question:
who have you lost, and what were they called; the newcomers give them, counting on their fingers; the widowers give one
name each and nothing else; Lucy gives hers, and stops partway, and says that's all.

**l_night_28**. Facts: the light going; the fog pale; everyone coming to the fire.

**l_sit_names_fail** (A40's failed tap before night: the voice pass's).

**l_i13_1 to l_i13_3** (I13, H each). Fields: up · yes_but · warm · pays the near question. Facts: night; the town at the
fire; the bedesman stands and says every name they were given, one after another; the air so still the names go down
the valley and come back off the far side; at `{n11}`'s they say it twice; at the end they stop and say nothing, as long
as a name would take, and sit down. States: night 28, present (A40 is a tap). Special: the week's quiet close; the
pause is the last fact; never what it is for.

**The finds** (Woodcutting 18, Foraging 12, Scavenging 18, Cooking 19, Melee 23, Spellcraft 10's pay, Wayfinding 3
and 5): one line each, by the mix, any visit. No find names Sorrel, the boar's fog, the first mark or anything of week
five; Wayfinding 5's square on the far hill is "something square", never a building's word.

### Fights (pools)

From the line-state lists of item 7. Eight lines per writer per pool, any order, true for any count:

- **fight_hunt_boar_won**: the hunt plain; the boar brought back on a pole, or its meat.
- **fight_hunt_boar_death**: the death pool above.
- **fight_pack_won**, **fight_pack_lost**: unchanged; the step adds none.
- **fight_summary**: unchanged; a count line for boar deaths is "came back from the stone" plus the count's word, the
  voice pass's.

## The journal's notes (a batch of their own)

The register is not the lines': first person, lowercase, past tense, fragments jotted at different times, a later line
under an earlier one, dry and clinical, sometimes wrong; mostly mundane; at most one ominous note per page; numbers sit
beside the notes in the UI font and are never written into them. Must-nots as the lines'.

| Note | Page | When | Facts |
|---|---|---|---|
| n_pilgrim_1 | the walked elk (the voice pass's title) | B18 | walks slower than anything alive; fungus along the spine; drag-marks to every warm patch; meat from one not eaten (its one ominous note) |
| n_ashwood_1 | the wood (a place) | B18 | dead trunks standing; shelves up them like stairs; warm patches where the ash is thin |
| n_boar_1 | ash-boar | the first boar hunt | bigger than a pig should be; caked grey; came from the side I wasn't facing |
| n_forget_1 | the day's page, margin | B20 | the first forgetting: small, ordinary (the word for the hook a pot hangs from; had it yesterday) |
| n_forget_2 .. n_forget_12 | the day's page, margin | each death after, by a shuffle bag | the same register: which hand starts a knot; whether the stream is left or right of the door; a tune's next line; the name of a knot, not the knot; how many steps to the stream |
| n_book_1 .. n_book_4 | Sorrel's book (their own page, their hand: plain, short, no capitals, no names of anyone) | a story day after `book_given`, up to four | each a few lines of the day, each a little at odds with the last (the people here are kind / I came here this morning / the woman with the pot gave me a name, I don't know why); never a fact of what they are |
| n_day_b18 .. n_day_b21 | days (`e_days_8`) | each spine beat's step | the beat retold after the fact, in the journal's voice, the facts of its row and nothing past them |

Sorrel's pages are in their hand, not the player's: the voice pass gives them their own register (no capitals, no
names, short lines). A forgetting is written as the player noticing a gap, never as loss: "couldn't think of the word
for the pot hook. had it yesterday."

## Labels: the voice pass's, not the writers'

- **Cards:** c_walk_ashwood (and the town card's), c_fog_fish (and the town card's), c_wash_meat (and the town card's),
  c_stir_air, c_post, c_bind_book, c_go_wallow ("Go after them" or the pass's), c_hunt_boar, c_sit_names ("Sit at the
  fire" or the pass's), each job's card
- **Upsides** (UI register, numbers): Camp 19's pays, Wayfinding 8's and Spellcraft 10's pays, O-fiddle's, O-walkers'
  and O-widowers' lasting halves, the walk's line (what it takes and brings, and that it finds things)
- **Chips:** chip_ashed ("the table feeds fewer" or the pass's) and its hint
- **Offers:** o_fiddle, o_walkers, o_widowers and their answers; o_book ("Make them one" / "Not now"); each job's yes
  and no labels
- **Order cards:** the post's ("build when charwood reaches 10"); none for the chip
- **Fights:** threat_ash_boar; the boar's on-loss line ("a loss: you die, and wake at the stone; what you carried is
  lost", or the pass's)
- **Rows and stores:** store_charwood, store_fish_rising ("fish under the fog" or the pass's); lane_n13 before and after
  SL31 ("the stranger", then the name), lane_n23 ("the bedesman"), the two groups' words
- **Journal:** the walked elk's page title, the ash-boar's, the wood's, Sorrel's book's
- **The map:** the four places' labels (`p_square_hill` has none)
- **Aims:** aim_ashwood, aim_post, aim_names
- **End cards:** dayend28_* (the edge of week four's content); week three's dayend21_* rewritten now it is no longer the
  edge
- **The people bands:** the widowers' mention reads the shipped `[people]` bands; no new band
- **Never drawn:** store_still_left, store_thaw_left, store_still_clock, store_film, store_ashwood_trips,
  store_sorrel_clock, store_kept_clock, store_bede_wait, store_bede_clock, store_pace_3h, store_walkers_6h,
  store_cache_torn, store_night_24, store_night_28, store_boar_lost

Two to check first: **l_b20_1 to l_b20_5** must cut from the boar to the stone with nothing between, and close on the
list; **l_i13_1** must work as names said at a fire before it works as anything else.
