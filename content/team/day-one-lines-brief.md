# Day one's lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `day-one.md` (the beats, the canon ids, and the state
table each line here is drawn from); the data is `app/ashfall_app/opening/day_one.toml`, where every line below
reads "unwritten".

## How the lines get written

1. **Three proposers** (Sonnet), blind to each other, each with one lens drawn by code (below). Each writes every
   line key in "The lines", plus one alternate for each line marked H.
2. **A critic** scores the other proposers' drafts blind on `rubric.md`, plus one row: *true in every listed state?*
   (quote the state it breaks). Writers revise their own drafts once.
3. **The lead** picks line by line. Code then checks: length (below), the must-nots as a scan, id references, and
   n-gram echoes against content prose and the shipped opening lines (no run of three words shared with either).
4. **A voice pass** by a fresh agent reads every picked line and every label in `day_one.toml` in player order.

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases: a word from an attribute may appear in a line, its phrasing should not.

## Rules for every line

- **Voice:** the shipped opening's. Second person, present tense, lowercase, plain. One or two short sentences. A
  turn the reader completes, never stated; no feeling named, no moral. Dry about the player's own choices only.
- **Length:** the lines show on the task card. Across all of day one's lines, the median is 45 characters or fewer
  and the 90th percentile 75 or fewer. The shipped exemplars below run longer: match their voice, not their length.
- **True in every state** on the line's list. A line that plays on return must read right whether the player watched
  it happen or is reading it hours later. Never say when, in real time, anything happened.
- **Must-nots (all lines):**
  - nothing from B5 or B6: no new warmth in the ground, no glow beyond the opening's, nothing about the player's hands
    moving heat;
  - never "again", or any hint of having been here or done this before; H4's old snare is the only echo, and it says
    nothing about whose it was;
  - the thing on the ridge is never called a cart, a wagon or anything with wheels;
  - no wolves at or near the camp (one far-off howl at night, H1, is all);
  - the stool at most once across all of day one's lines;
  - nothing about who she is before B3: no name, no number of people, no "her", no "someone's" light (the light is
    kept, minded, low; nobody is seen); in B3's lines, still no name (her name comes with her first words, a later
    beat), and never anything about the people she lost;
  - the trade (H7) is never a penalty for being away: no "while you were gone", "you weren't there", "you left it";
    in-world the player was out at the snares, which is true whether the player watched or not;
  - no proper nouns; no Chequer, keels, holders, magic, faith, the burn.

## Voice exemplars (shipped, `opening.toml`)

Quoted as shipped, by key. Read them for voice; reuse no phrase from them.

| Key | Line |
|---|---|
| l_up_1 | you get an arm under you. it gives. |
| l_up_2 | knees under you this time. then not. |
| l_look | walls, mostly. a roof over one corner. grey every way you look, nothing moving in it. your hands have been cold a long while. |
| l_coat | inside the coat, a book with its first pages gone at the stitching. wrapped with it, a charcoal stick worn short. |
| l_wood | dead birch, snapped off by hand. wet through, like everything here. |
| l_nail | under a fallen beam, a bent nail. you keep it. |
| l_dry_fail | too little wet wood to lay out. the rack stands bare. |
| l_ring_fail | you set down what stones you have. it isn't a ring yet. |
| l_strike_fail | you strike at the dry wood for a good while. it stays wood. |
| l_fire_takes | it takes. you sit close enough to smell your sleeves. |
| l_roots | roots under the scrub, bitter and full of grit. |
| l_roast | roasted, they go soft enough to eat. you eat three. |
| l_stool | four legs, one of them short. you sit on it anyway. |
| l_fireback_fail | you start on the fireback. halfway up, it comes down. |
| l_wall | the wood comes off the wall dry. the wall is warm, and clean of ash. nothing else here is. |
| l_ring | five stones in a ring on the cut stone. none of them rocks. |
| l_camp_1 | you've stopped tripping on the rubble. |
| l_camp_2 | you could find anything here in the dark. there isn't much to find. |
| l_tired | your arms go heavy. you work at half the pace, and it wasn't much of one. |
| l_retire | no more snapping dead wood by hand. the edge does it better, and it doesn't bleed. |
| l_wc_2 | you split the birch where you mean to now. |
| l_dusk_1 | the grey goes to brown, and the brown to dark. then the cracks in the floor begin to glow, a dull red, in rings around the place you woke. |
| l_dusk_2 | far off on the ridge, a light comes up that isn't yours. it doesn't move. it doesn't go out. |

The day picks up from l_dusk_2: the player has seen that light and nothing else of anyone.

## Lenses

`lenses.txt`, one per line:

- what it costs the people
- what a child would notice
- the oldest thing in it
- the joke nobody laughs at
- what gets written down, and what doesn't
- what the hands are doing
- what it sounds like when nobody is talking
- the thing everyone has stopped mentioning
- what a stranger would get wrong
- what is traded for it, and who sets the price
- the habit that outlived its reason
- the smallest object in the room
- what the animals already know
- the day after
- what is eaten, and who goes without
- the rule someone keeps breaking

**The draw:** `python3 content/team/draw_lenses.py <task id> --writers 3` prints one distinct lens per writer, seeded
from the task id, so the same id always draws the same lenses and a reviewer can rerun it. Use the task id
`day-one-lines` for the first pass and a new id for any redraw. A lens is a way into the line, not a topic: a line
that cannot take it plainly ignores it.

## The lines

Each entry: the moment, the beat and its fields (where there is one), the facts as attributes, the states (from
`day-one.md`'s table, condensed), and anything special. "H" marks a beat line: write an alternate too.

### The night (V1)

H1's fields: turn down · dread · cost none · moves PC · opens C-promise-16 (who is out there) · thread th-ridge start.
Canon C-beat-69.

**l_night_1** (H). First line of the night. Facts: the light on the ridge: still there; kept low; has not moved.
States: minutes after the end, every route; fire lit, both crafts built, roast eaten; book read or not; also a
rebased save's first load. Special: picks up from l_dusk_2 without repeating it.

**l_night_2** (H). Second line of the night. Facts: one long howl; far off; carried by air with no wind in it; nothing
comes. States: as l_night_1, straight after it.

**l_sit_up** (A11, no beat). Sitting up with the fire. Facts: the light never moves all night; it is being minded,
the way the player minds their own fire. States: night only, V1, present; optional (most players tap it). Special:
mind the light, never the person; this is the closest day one comes to her before H7.

### The morning (V2)

**l_morning** (H2, H). Fields: up · wry · cost time · moves PC · thread th-survive. Canon C-beat-70. Facts: morning,
grey; the ridge light out; the camp kept going through the night. States: plays on return on almost every route
(1 to 24 h after the end) or while watching (babysitter); rest rule taken or not. Special: true for a one-hour night
and a day-long absence alike; it heads the unwrap of what the night got done.

**l_look_out_1** (H3). Fields: up · yes · wonder · cost none · advances C-promise-16 · thread th-ridge. Canon
C-beat-71. Facts: the valley by day: a bowl; fog lying in its bottom; the warm stream's steam rising out of the fog;
old fields under ash; scrub birch. States: V2, the first tap of the return, every route.

**l_look_out_2** (H3, H). Second line of looking out. Facts: on the ridge where the light was, something dark and
square; the dusk hid it. States: as l_look_out_1, straight after. Special: never named, never with wheels; no person.

**l_wire_1**, **l_wire_2** (finds, no beat). Scavenging 4 and 5 pay wire. Facts: wire from the ruins; good for a
snare (but the snare card isn't on screen yet). States: V1, at night, by the mix, every route. Special: two lines for
two finds; don't name a use the player can't see yet, or name it as an idea, not a plan.

**l_wire_3** (find). Scavenging 6, the third wire. States: on return (night or morning) on 9 routes, before any
snare. Special: as above; the third of a kind, so it can be shorter.

**l_tinder** (find, no beat). Foraging 2 pays tinder fungus. Facts: a bracket fungus on dead birch; dry inside; takes
a spark and smoulders. States: night or day, present or on return; its use (the rack) is not on screen yet.

**l_snare_1** (H4, H). Fields: down · yes_but · dread · cost none · moves PC · thread th-survive. Canon C-beat-72.
Facts: the player picks a run in the scrub; there is already a snare there; decades old; rusted through; the same
place. Nothing about whose, or how it was tied. States: V2, right after looking out, every route. Special: mundane;
ominous only in hindsight. This is day one's one deep-pull line: no "again", no "you knew".

**l_snare_2**, **l_snare_3** (no beat). The second and third snares, within a minute of the first. Facts: other runs
in the scrub; wire set. States: V2, every route. Special: plain, short; don't add more old snares.

**l_snare_fail** (failed line). set_snare tapped with no wire. States: derived, no route hits it: one or two snares
set, the next wire not yet found; daytime. Special: wry about trying.

**l_camp_daylight** (A14, leads into H5). Canon C-beat-78. Facts: by daylight; ash settled overnight on everything left
out, the player included; the roots stacked by the warm wall gone soft. States: V2, straight after the snares, every
route; no build yet. Special: shows what the camp lacks (cover, a cool dry place for food) without naming the builds;
nothing new about the ground.

**l_lean_to** (H5, H). Fields: up · yes_but · wry · cost option · advances C-promise-16 · thread th-survive. Canon
C-beat-73. Facts: a lean-to of birch poles; its open side faces the gap and the ridge; rest under cover. States: V2,
present; the larder built or not (the player chooses the order). Special: the facing is the near question's advance:
the player put the view of the ridge in their own shelter; don't say why.

**l_larder** (H5, H). Facts: a larder of stacked stone, off the warm ground; food keeps there. States: V2, present;
the lean-to built or not. Special: wry about the player's own choice of order is allowed only if true both ways.

**l_lean_to_fail**, **l_larder_fail** (failed lines). Tapped unready: the lean-to short of dry wood (needs 10) or
stones (2); the larder short of stones (12) or dry wood (4). States: derived; the other build done or not. Special:
true whichever input is short.

### The rack and the smoke (V3)

**l_first_catch** (no beat). The first catch in a snare. Facts: ashrats, the only small game here; one in a snare.
States: on return on 9 routes (~20 min after the snares), both builds done. Special: plain record; it plays first in
V3's unwrap.

**l_rack_shown** (no beat). The rack card appears, the same instant. Facts: meat won't keep on warm ground; it needs
smoking. States: as l_first_catch, straight after.

**l_rack** (no beat). The smoking rack built. Facts: a rack of birch over a smoulder; the tinder fungus under it.
States: V3, present, every route; both builds done; catch held.

**l_rack_fail** (failed line). Tapped unready: dry wood under 10, or no tinder fungus. States: derived, V3 or later.

**l_cooking_open** (no beat). Cooking opens with the rack. Facts: smoking is cooking that keeps; it makes meat safe to
eat. States: the same instant as l_rack.

**l_smoke_roots** (no beat). smoke_roots appears with the rack. Facts: roots can go over the smoke too; then they
keep, but they are no longer roots. States: the same instant as l_rack; Take stock has just appeared needing roots
and smoked food. Special: the tradeoff is the player's to see; the line only makes it thinkable.

**l_smoke_1** (H6, H). Fields: up · yes_but · wry · cost time · advances C-promise-16 · thread th-ridge. Canon
C-beat-74. Facts: no wind; the smoke rises straight up; a tall thin column; it stays all afternoon; anyone for miles
can see there is meat here. States: V3, present on every route; by hand or by the catch rule; both builds done.
Special: wry, about the player's own build; the turn (they've told the valley) is the reader's. From this instant a
ledger line starts taking roots (the visitor): the line must not mention it.

**l_smoke_fail** (failed line). Either smoke card tapped unready: catch (or roots) under 4, or damp wood under 2.
States: derived, V3 or later. Special: one line for both cards.

**l_cooking_2** (level, no beat). Cooking 2: a bigger batch. States: on return on a few routes, never on most before
B3; before or after H7.

### The prints and the arrival (V4)

**l_prints_1** (H7, H). Fields: down · no_and · dread · cost stores · moves N1, PC · advances C-promise-16 · thread
th-ridge end. Canon C-beat-75. Facts: prints in the ash; one set; through the gap to the larder; the player was out at
the snares. States: on return on 9 routes, present for the babysitter; larder and rack built. Special: on 8 routes
B3's lines follow at once, so this must not close the question: it sharpens it.

**l_prints_2** (H7, H). Facts: three roots gone; on the warm stone, a strip of smoked meat the player didn't smoke;
someone hungry and honest. States: as l_prints_1, straight after. Special: the strip is fair pay, never a taunt or a
gift; never a penalty for being away.

**l_take_stock_fail** (failed line). Take stock tapped unready. Facts: counting what there is; not enough yet.
States: derived; the first blocker shown is smoked under 6, then roots under 15, then the larder, the rack, the
prints. Special: true for any blocker; before H7 too, so nothing about anyone coming.

**l_b3_1** (B3, H). Fields (from `beats.yaml`): up · yes · warm · cost stores · moves PC, N1 · pays C-promise-16 ·
thread th-survive. Canon C-beat-3, C-beat-76. Facts: the player counts the food twice; looks up. States: on return on
8 routes, straight after the prints; tapped in V4 on by_hand; babysitter present. Special: the count is the player's
own doing (Take stock); the looking up is the hinge.

**l_b3_2** (B3, H). Facts: a figure walks out of the ash at the gap; alone. States: as l_b3_1, straight after.
Special: no name, no description beyond what a glance gives; the prints are hers, but don't say so.

**l_b3_3** (B3, H). Facts: she sees food to spare; she sits down at the fire, on the player's side. States: as above.
Special: the far side of the fire is a later beat's; this one is near.

**l_b3_4** (B3, H). Facts: she eats from the larder; the camp is two now. States: as above; the smoked and roots lines
go red with this. Special: warm, never sweet; the cost (food) is the warmth's own price. Ends the day: no hook
sentence, no question.

### The Camp

**l_camp_3** (level). The wall takes 7 to dry. States: on return on 9 routes, night or day; anywhere from before
the snares to after the builds. Special: like l_camp_1 and l_camp_2: the camp getting known, not grand.

**l_camp_4** (level). The catch holds more. States: V3 present on 2 routes, on return on 7; after the snares; before
or after the rack.

**l_camp_5** (level). The rack takes more. States: on return on 8 routes; after the rack.

**l_camp_6** (level, with B3). Room for two. States: with B3 on most routes, after it on one (sharp); she is there in
every case. Special: may be the day's last line; plain.

## Labels: the voice pass's, not the writers'

These keys in `day_one.toml` are UI, written in the voice pass with the opening's labels beside them (card names are
imperatives, upsides are short noun phrases, stores and skills plain nouns):

- **Cards:** c_sit_up, c_look_out, c_set_snare, c_look_over_camp, c_build_lean_to, c_build_larder,
  c_build_smoke_rack, c_smoke_catch, c_smoke_roots, c_take_stock
- **Upsides:** up_lean_to, up_larder
- **Stores:** store_wire, store_tinder_fungus, store_catch, store_smoked, store_night, store_h7_clock,
  store_stock_ready
- **Skills and level rewards:** skill_cooking, pays_builds, pays_smoke_batch, camp_pays_4, camp_pays_5
- **Standing actions (ledger lines):** action_night, action_snare, action_visitor, action_n1_eating
- **Lanes:** lane_smoke

Two to check before anything else:
- **action_visitor** is the ledger line that takes roots for ~90 game minutes after the first smoke, and on many
  routes the player sees it before H7. It is the only sign on screen that something is coming: it may be uneasy, it
  must not name or imply a person, and it must not read as a penalty.
- **store_h7_clock** and **store_stock_ready** should never be shown (they count for the engine). Confirm they stay
  hidden, and if either can show, give it a label that spoils nothing.

The shipped **l_hungry** now also fires in day one (on return on most routes). It is not rewritten; the voice pass
confirms it still reads true there.
