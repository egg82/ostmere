# Week five: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `week-five.md` (beats, side layer, canon ids); the data
will be `day_twenty_nine.toml`, `day_thirty.toml`, `day_thirty_one.toml` and `day_thirty_three.toml`, where every key below
reads UNWRITTEN. The states below are the design's expectation. **Before the writers start**, regenerate them with the
simulator's `--lines` (`docs/design/week-five-plan.md`, item 9) and replace this file's "States" notes with the generated
lists; a line written against the expectation alone is a draft.

## How the lines get written

As weeks one to four, unchanged: three blind proposers (Sonnet), one lens each (below), every key plus one alternate per
key marked H; a critic scores the drafts blind on `rubric.md` plus *true in every listed state?*; the lead picks line by
line; code checks length, the must-nots as a scan, and three-word echoes against content prose and every shipped line
before them; a fresh agent's voice pass reads every picked line and label in player order after day twenty-seven's last
lines, and writes the labels. One batch per chapter, in chapter order; the journal's notes are a fifth batch; the chain
lines of the jump (item 6) are a sixth, small, when that slice ships.

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases.

**This week's risk is B24 and B25.** Model drafts of the wall map reach for awe stated ("ancient", "vast", "a map of
everything") and for meaning (the camp's mark "waiting", "calling", "as if it knew"). The beat is plain: lines of dull red
light on a wall, roads and marks, one mark where the camp is; the reader does the cold drop. B25's drafts will reach for
destiny (the door "recognising" the player, a "key", "it was meant"); the facts are a wrist in a hollow, a door that goes
in, a charcoal copy that works once. The second risk is B23 written as a spell: glowing, crackling, a word of power. It is
heat leaving one wolf through a fist of its hair and not stopping. The critic reads "Says the feeling?" first, then "Too
neat?" for B25, then "Brighter than planned?" for B23.

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase, plain. One or two short sentences. A turn the
  reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, per chapter.
- **True in every state.** Most of this plays on return. Never say when, in real time, anything happened, or how long it
  took. B23 names no hour (its step can be tapped any time from the morning).
- **People:** Lucy by name; the shipped slots `{n2}` (Martin), `{n3}` (Mary), `{n4}` (Edward), `{n5}` (Thomasina),
  `{n13}` (Sorrel), `{n14}` (the fiddler), `{n15}` (his wife), `{n23}` or "the bedesman"; the tracker is `{tracker}` from
  B22's last line on (before it, "a forager"), never a lane slot, because the tracker is whoever the save cast; the
  burners "a woman and her son" until l_burners_2 gives `{n24}` and `{n25}`; the walkers "the walkers". What each does, in
  active voice. Lucy never grateful, never sweet, never says much. Light-tier people are ordinary: no backstory past what
  they carry.
- **Sorrel is "they"** in every line, as `cast.md` has it.
- **Fights:** plain, one short line, won or lost, never gory. A long absence folds into one count line.
- **Must-nots (all lines):**
  - no "magic", "spell", "mage", "arcana", "spellcraft", "wayfinding", "ward" (the card's label is the voice pass's),
    Chequer, keels, holders, seal, faith, the burn, Drift, Clear, Still or any season name; the weather is described,
    never named;
  - the cats: "cats", "a cat", the tracker's word for them in B22 only if the voice pass gives one; never "mourner" in a
    line (it is the page's title, the voice pass's); never that they think, plan, understand or are clever; they draw a pin
    and lay it down, and the reader does the rest; never gore; they take food, never a person;
  - the hair and the pack (Y7, B23): what the hand and the heat did, what the wolves did; never how, never a rule stated,
    never "link", "like", "kin", "connected"; the grey on the arm is the cost and is said once;
  - the house (Y9, Y10, B24): dressed stone, no hinges, a hearth with no ash, lines cut in the wall; never "Chequer",
    "ancient", "old ones", "who built it"; the light is "dull red, like the cracks at camp at night" and nothing brighter;
  - the camp's mark (B24): a mark where the camp is, said once, as a fact of the map; never that it is the stone, the
    player, a holder, that it was put there, waits, or means anything; no line after B24 mentions it;
  - the ring (B24): "a ring of marks round a dark place far off"; never a count, never what the dark place is;
  - Sorrel at the house (B24): sleeps outside the door, in the ash, won't come in; never why; no line about their
    wrists, sleeves or hands this week;
  - the mark on the player's wrist (Y13, B25): "the mark", "the mark on your wrist"; it was mentioned once on the first
    morning, and these lines may say it has been there since; never a seal, a name, a brand, a key, a word for what it
    is, that it "matches", or that the door "knows" anyone;
  - the charcoal copy (B25, Y14, Y15): drawn, works once, does not work the second time, kept dry, rubbed off; never
    why once; never that the player's does not rub off (no line looks at the player's wrist at night 35);
  - the shaft (B25): down into the dark, warm air coming up; nothing else (no light, no red, no sound, no smell named);
  - the fiddle (SL37, Y15): he plays; the tune is known; no tune is named, no song's words, no reason Lucy lets it go on;
  - Mary's scraping (SL40): she scrapes; nobody says anything; never why;
  - the cutter, the first mark and the starer: nothing;
  - no line judges any answer to O-first-run, O-burners or any job's yes or no; "you said yes" may follow I'll take it,
    once, in B22's lines;
  - no proper noun but Lucy and the name slots.

## Voice exemplars (shipped)

Read the exemplar tables in `day-two-lines-brief.md`, day eight's B8 set in `day_eight.toml` (the first Drift's turn,
which Y1 answers), and week four's shipped lines in `day_twenty_two.toml` to `day_twenty_five.toml`. Reuse no phrase from
them; three-word echoes are checked in code.

## Lenses

`python3 content/team/draw_lenses.py week-five-lines --writers 3`:

| Writer | Lens |
|---|---|
| writer-1 | the thing everyone has stopped mentioning |
| writer-2 | what is eaten, and who goes without |
| writer-3 | the oldest thing in it |

A lens is a way into the line, not a topic; a line that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, anything special.

### Day twenty-nine (29a-29e)

**l_y1_1 to l_y1_3** (Y1, H each). Fields: down · wry · none. Facts: in the night the wind comes back, warm, out of the
east, all at once; by morning ash coming down so thick the noon is brown; the roofs sag under it; the fog gone off the
stream; `{n2}` up on the hall roof with a shovel before anyone asks. States: on return on every route; the babysitter
present. Special: answers week two's B8 without echoing it; the last fact is the joke.

**l_fiddle_plays** (SL37). Facts: that evening `{n14}` unties the cloth, looks at the fiddle a while, tunes it with his
ear down on the wood, and plays; the three women know the tune; Lucy doesn't stop them. Special: the last fact is the turn.

**l_prints_1, l_prints_2** (Y2, H). Fields: down · dread · opens the near question. Facts: out at the post the fresh ash
round the shut store printed with tracks; a big cat's, the front toes long and spread, like fingers; the hide door shut;
round the hasp the wood scratched pale.

**l_pin** (Y3). Fields: up · dread · advances. Facts: next morning the pin out of the hasp and laid on the step, square to
the door; the door shut; inside nothing touched. Special: the smallest object is the line; "square to the door" or its
equivalent is the dread.

**l_first_run_ask** (O-first-run's line). Facts: Lucy: somebody has to take the post its first load; she says it to the
room. **l_first_run_yes**, **l_first_run_other** (each answer's line): you load the cart; or she finds someone, never who.

**l_b22_1 to l_b22_4** (B22, H each). Fields: down · no_and · grim · stores · pays the near question; canon C-beat-22,
C-beat-170. Facts: under the trees in the brown noon the cart pulled backward out of your hands; the tail-pins drawn and
dropped one by one in the ash; the load going off into the dark in pieces; you walk on to the post with nothing; next
morning a forager kneels over the tracks: cats, that know how a pin comes out; they have the road now; l_b22_4 names
`{tracker}`. States: on return or present; either answer of O-first-run (on "Someone else" the cart is someone's, the
first fact is theirs, and "you said yes" is not available). Special: two sets, keyed by the answer (`l_b22_1y` .. and
`l_b22_1o` ..); nothing about a person hurt; the last fact is the road.

**The chips** (the voice pass's, UI register): chip_drifted ("the carts go slower" or the pass's) and both chips' hint
dots; `ash_laden`'s words are shipped.

### Day thirty (30a-31a)

**l_y4_1, l_y4_2** (Y4, H). Fields: down · no · grim · stores. Facts: a cart doesn't come in; `{tracker}` finds it on the
track at the trees, its load gone, its four pins laid in a row in the ash beside the wheel, like tools put down.

**l_track** (SL38). Facts: `{tracker}` walks the track ahead of the carts bent over the ash; comes back at dusk and tells
Lucy where the cats crossed, where they waited, how many; is right the next day.

**l_moths_1, l_moths_2** (Y5, H). Fields: up · wonder. Facts: over the fungus shelves round the post, moths as wide as two
hands come up out of the brown dark in hundreds; under them nobody can hear their own feet, or the axe, or each other;
the dust off their wings on everyone's sleeves. Special: the sound that goes is the line, never "silence".

**l_words_elk** (SL39). Facts: a walked elk comes onto the track by the post and stops on the warm patch; the crew burn
it there; the bedesman walks out from town to say the words over it, the whole way, and walks back.

**l_y6_1, l_y6_2** (Y6, H). Fields: down · dread · opens the near question. Facts: in the warm dark the pack comes past the
watch fire into the yard; sits down facing the hall door; more of them than anyone has counted; they don't come closer;
nobody goes out; in the morning gone, the yard printed all over. States: on return (night 30's grade) or present.
**l_night_30**: the light going warm and brown.

**l_comb** (`comb_pelts` first finish): the pelts by the hall door combed; the hair comes away in grey handfuls.

**l_hair_1, l_hair_2** (Y7, H). Fields: up · wonder · advances. Facts: you hold a hank of the combed wolf hair over the
coals to dry it; the heat goes into it all at once, the way it never goes into stone; and comes back out into your hand.

**l_call_ask** (A42 shown, with Y7's visit). Facts: none spoken; the card's line: the hair in your fist, the yard. The
voice pass labels the card ("Call the heat out" or the pass's) and its early tap.

**l_b23_1 to l_b23_4** (B23, H each). Fields: up · yes_but · wonder · time · pays the near question; canon C-beat-23,
C-beat-171. Facts: the next time the pack comes into the yard; you in the hall door with a twist of wolf hair in a fist;
you take the heat out of the nearest one through it; it doesn't stop at one: the next shivers, and the next, all the way
round the yard; they get up and go, all of them, into the dark; the grey on your hand goes to the elbow; Lucy, behind you,
says nothing at all. States: on return or present; no hour. Special: the week's best moment; the chain is told as a
count the reader sees (the next, and the next), never a light; Lucy's silence is the last fact.

**l_ward_first** (`ward_gate`'s first finish): your hand on the gate stone, a twist of hair under it; the pack keeps off
the gap. Special: nothing about why the stone holds it.

### Day thirty-one (31b-33a)

**l_y8_1, l_y8_2** (Y8, H). Fields: down · no · grim · stores. Facts: in the morning the hall's larder door standing
open; the bar out of its brackets and leaned against the wall beside it, neatly; the long-toed prints go in and come out;
the hams gone off the hooks. Special: "neatly" or its equivalent carries it; no line connects it to the ward.

**l_latch_shown**: `{n2}` and `{n4}` at the ruin's scrap with a hammer: a latch they can't lift.

**l_y9_1, l_y9_2** (Y9, H). Fields: up · wonder · opens the near question. Facts: at the top of the far hill the square
thing a house of dressed stone; its roof fallen in; a doorway with a door of the same stone and no hinges, standing a hand
open; nothing has nested in it. **l_p5_shown**: Lucy: it wants clearing out.

**l_burners_1, l_burners_2** (O-burners' line). Fields: up · people. Facts: a woman and her son come in to the post's fire
from the wood with a barrow of charcoal; black to the elbows; she does the talking; they knew the house on the hill was
there and never went in: it's not ours. Special: l_burners_2 gives `{n24}` and `{n25}`.

**l_scrape** (SL40). Facts: every morning `{n3}` takes the meat off the racks and scrapes it with her thumbnail, strip by
strip; nothing settles on it in the wind; nobody says anything.

**l_y10_1, l_y10_2** (Y10, H). Fields: down · dread · advances. Facts: clearing the fallen roof out, the walkers find a
hearth with no ash in it; under a drift on the back wall, lines cut into the stone, long and straight, with marks along
them.

**l_bear_sign_2** (SL41). Facts: at the bloom in the scrub, bear sign again: the fungus torn up, the stumps clawed, as at
this time before. Special: "again" here is the bear's, and the only "again" allowed this week.

**l_y11** (Y11). Fields: up · yes · wry. Facts: the latch holds; at first light one of the cats sitting on the hall's
ridge with its long front feet together, looking down at the larder door; it watches whoever comes out, and then it goes.

**l_stage_house_1 .. l_stage_house_8** (P5's stages; the third carried by Y10, the eighth showing A43). Facts: the fallen
roof dragged out, ash shovelled, the doorway cleared, the hearth swept, a lintel propped, the floor's flags, the back wall
cleared. No two share a verb.

**l_wake_ask** (A43 shown). Facts: the hearthstone swept bare; your hands. The card's label is the voice pass's.

**l_b24_1 to l_b24_5** (B24 ★, H each). Fields: down · yes_but · dread · time · pays the near question; canon C-beat-24,
C-beat-172. Facts: you lay both hands on the hearthstone and move heat into it; the lines on the back wall fill with a
dull red light, like the cracks at camp at night; roads, the marks of houses along them; a great ring of marks round a dark
place far off; one mark, near the edge, where the camp is; the walkers and `{tracker}` sleep inside; `{n13}` sleeps outside
the door, in the ash, and won't come in. States: on return (the step runs ten minutes) or present. Special: the week's ★;
the camp's mark is said once, flat, as the fourth fact of five; Sorrel's refusal is the last.

### Day thirty-three (33b-35c)

**l_y12_1, l_y12_2** (Y12, H). Fields: down · dread · opens the near question. Facts: clearing the last ash from the back
of the house, the walkers find a second door; black stone, set flush, no handle, no keyhole; warm to the hand, warmer than
the hearth.

**l_y13_1, l_y13_2** (Y13, H). Fields: up · no · wry · advances. Facts: `{tracker}` and two of the walkers put a bar to the
black door's edge and lean on it until the bar bends; it doesn't move; in the middle of its face, at waist height, a
shallow hollow, long and narrow, about the width of a wrist.

**l_b25_1 to l_b25_4** (B25, H each). Fields: up · yes · dread · none · pays the near question; canon C-beat-25,
C-beat-173. Facts: you lay your wrist in the hollow, the mark on it uppermost; the door goes in a hand's width and swings;
`{tracker}` looks at your wrist a long time; draws the same mark on their own wrist with a stick of charcoal; swings the
door shut, lays their wrist in the hollow, and it opens for them too; they try it again and it doesn't; behind the door a
shaft going down into the dark, warm air coming up it. States: on return or present. Special: the second try is the turn;
"it doesn't" and nothing after it about the door.

**l_y14** (Y14). Fields: up · warm · opens the night's question. Facts: at supper `{tracker}` eats with one sleeve rolled to
the elbow and that wrist held out away from the pot's steam; won't let anyone near it.

**l_night_35**: warm, the ash still coming down, everyone out in the yard.

**l_y15_1, l_y15_2** (Y15, H). Fields: down · wry · pays. Facts: night, warm, ash coming down; everyone out in the yard
because nobody can sleep inside in the heat; `{n14}` plays; `{tracker}` spits on their wrist and rubs the charcoal off with
a thumb; it comes away grey. Special: the week's last line ends on the grey thumb; nothing about anyone else's wrist.

**The finds:** Wayfinding 10 (a road marker on the hill path, its face still cut, the letters unreadable), Foraging 14
(ash-caps on the dead trunks round the post). One line each, any visit.

**The jobs:** each yes and no line for `j_post_roof`, `j_drag_elk`, `j_new_pins`, `j_hill_stakes`: Lucy's ask, plain; each
no, she finds someone, never who. `j_new_pins` must not suggest the pins will stop the cats.

**The fights:** `raid_line` won and lost (six each: a cart in, a cart short; pins on the track), `raid_hall` won and lost
(six each: the larder shut in the morning; the larder open and the bar leaned). The fold line for each.

## The journal (fifth batch)

| Note | Page | Written by | Facts |
|---|---|---|---|
| n_mourner_1 | the cats (the voice pass's title) | the first raid | a big cat whose front feet open like hands; draws pins and lays them down; "learned pins the way we did: by having hands" (its one ominous note, `creatures.md`) |
| n_moth_1 | the moths | Y5 | wide as two hands; eat the fungus; under them you can't hear your own feet; the dust on the sleeves |
| n_house_1 | the house on the hill (a place) | Y9 | dressed stone; no hinges; nothing nests in it |
| n_house_2 | the same | B24 | the wall lit: roads, marks, a ring round a dark place; one mark where the camp is (said as plainly as the rest; the page's sketch is the wall) |
| n_like_1 | the arcana page (the voice pass's title) | B23 | heat went into the hair at once; took it from one; went through all of them |
| n_day_b22 .. n_day_b25 | days (`e_days_9`) | each spine beat's step | the beat retold after the fact, in the journal's voice, the facts of its row and nothing past them |
| n_book_5 .. n_book_10 | Sorrel's book (their hand: plain, short, no capitals, no names) | `drift_clock` 528 to 648, one a story day while `book_given` | each a few lines of the day, a little at odds with the last (the wind is warm / a man played something, I knew it / I slept by a door on a hill, I don't know whose); never a wrist, a door, a mark or a fact of what they are |

## Labels: the voice pass's, not the writers'

- **Cards:** c_run_cart (and the town card's), c_walk_hill (and the town card's), c_clear_track (and the town card's),
  c_comb_pelts (and the town card's), c_net_moths (and the town card's), c_dust_line (and the town card's), c_track (the
  tracker's), c_first_run, c_call_pack, c_ward_gate, c_jump_pack (when it ships), c_iron_latch, c_waystation, c_wake_ward,
  c_open_ward, each job's card
- **Upsides** (UI register, numbers): Camp 20's pays, Wayfinding 12's and Spellcraft 12's pays, O-burners' lasting halves,
  the latch's side, the ward's side, the tracker's card's side, the cart's line (what it takes and where it goes)
- **Chips:** chip_drifted and its hint; `ash_laden`'s hint dot this time
- **Offers:** o_first_run ("I'll take it" / "Someone else", or the pass's), o_burners and its answers, each job's yes and no
- **Order cards:** the latch's ("work on the latch when stakes reach 16"), P5's ("work on the house when the post's store
  reaches 8"); none for either chip
- **Fights:** threat_mourner; the line's and the hall's sides (`line`, `latch`) as the strength rows name them
- **Rows and stores:** store_post_stores ("the post's store" or the pass's), store_hair, store_dust, store_moths_up,
  store_road_ash, store_hill_trips (shown on the walk's goal); lane labels: the tracker's later label ("the tracker"),
  lane_n24, lane_n25
- **Journal:** the cats' page title, the moths', the house's, the arcana page's note heading
- **The map:** the post's label, the house's label, `p_marker_hill`'s; the network's marks have none
- **Aims:** aim_line, aim_latch, aim_house, aim_shaft
- **End cards:** dayend35_* (the edge of week five's content); week four's dayend28_* rewritten now it is no longer the
  edge
- **Never drawn:** store_drift_left, store_still_end_left, store_track_left, store_line_clock, store_call_clock,
  store_ward_clock, store_mark_clock, store_run_town, store_larder_torn, store_night_30, store_night_35,
  store_line_fought, store_line_lost, store_hall_fought, store_hall_lost

Two to check first: **l_b24_1 to l_b24_5** must say the camp's mark as flatly as the roads; **l_b25_1 to l_b25_4** must end
the door on the second try and the shaft on warm air, and nothing after.
