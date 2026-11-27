# Week five: from the Drift's second turn to night 35

Spoilers: this file is under `content/` and never shown to the owner. It picks up where `week-four.md` ends (I13, night
28) and runs from the Drift's second turn at save time 672 h to the end of story day 35, the Drift's last night, in four
chapters. Numbers are targets unless `week-five-numbers.md` marks them measured; lines are written from
`week-five-lines-brief.md`; engineering's side is `docs/design/week-five-plan.md` (spoiler-free). New canon is listed at
the end as proposals (tentative until the lead confirms), new decisions as D-200 to D-220.

Binding, carried: nothing is lost *because* the player was away (D-59); every return has something to spend and
something to decide (D-94); a side beat never gates a spine or chapter beat (D-97); watching earns nothing extra (the
2 AM test, held to players given the same rules and mixes the game has taught); D-119 (a staged hands build is run by one
order card); at most two moments per absence; no progress gate reads a finite pool (D-169); a season's chore arrives with
its hint dot and no ready-made rule (D-155, `docs/design/choice-not-protection.md` row 43); tools and exact information
arrive with what they serve, and a lock ships with a lead-in (`decisions.md`, "Tools early, choices kept").

**Beat ids.** Week five's letter is **Y** (D-200): every letter is spent somewhere, and Y collides only with the visit
labels of days four to seven (`days-four-to-seven-numbers.md`, `-lines-brief.md`), two closed files no data reads; V would
collide with the simulator's live visit numbers, Q with the mysteries, N and O with people and offers. Beats run Y1 to
Y15; visits are named `29a`, `30b` by the story day they start in. Side beats continue at SL37 (SL36 is day twenty-seven's).

**How this was written.** One lead, drafting alone: this pass ran as a single agent, so no blind proposers or critics
were run on the design (`docs/research/writing/studio-team.md`). To keep one model's first idea from setting every
beat, the lead drew four lenses by code (`python3 content/team/draw_lenses.py week-five-design --writers 4`: what it
costs the people; the habit that outlived its reason; the smallest object in the room; what gets written down, and what
doesn't) and put every beat and side beat through each before keeping it. The lines brief draws its own (below). The
proposer-and-critic pass belongs to the lines, where it was measured to matter.

## What week five is

The wind comes back. Warm, out of the east, ash coming down by the bucket and the noon brown; the fiddler unwraps his
fiddle. The post at the trees is finished, and something has been at its door: long-toed prints all round, the pin drawn
out of the hasp and laid on the step, nothing taken. The player takes the first cart out, and in the brown dark under
the trees the cart is pulled away from them, its pins drawn; a forager reads the tracks and says what they are. The
carts run after that, and get raided. In the warm dark the pack comes right into the yard and sits facing the hall
door. Combing the wolf pelts by the fire, the player finds that heat goes into the hair all at once, the way it never
goes into stone; they take the heat out of one wolf through a hank of its hair, and it runs through the whole pack, one
to the next. That night the hall's larder bar is lifted from outside. On the far hill seen last week stands a stone
house with a door and no hinges; the town clears it out, and when the player wakes what is in its walls, a map shows on
the wall in lines of light: the old roads, marks along them, and one mark exactly where the camp is. Sorrel won't sleep
inside. At the back of the house a door of black stone opens to the mark on the player's wrist. The tracker draws the
same mark on their own wrist in charcoal and it opens for them too, once. Behind it, warm air comes up a shaft. The
tracker keeps the charcoal dry for a day, then rubs it off at the fire.

What the player feels, in order: relief (the wind, the music), unease (the drawn pin), the dry joke of having said yes,
anger and then grim purpose (the cart, the raids), wonder (moths that eat sound), dread (the pack at the door), the best
moment of the week (one move running through a pack), the sting of the "but" (the larder), curiosity and awe (the house
on the hill, the map), a cold drop (the camp's mark), the unease of being the key, and a small warm close that turns
(the mark that rubs off, and the one that doesn't).

The front half reveals the world; this week is its hinge. B24 shows how big the network is (C-promise-9, paid), and B25
is the first beat that is about the player, not the scenery.

## The four chapters

| Chapter (file) | Beat span | Story time | Near question (proposed canon) | Typical span |
|---|---|---|---|---|
| Day twenty-nine (`day_twenty_nine.toml`) | Y1 → B22 | day 29 | C-promise-37, *what has been at the post's door?* opened Y2, advanced Y3, paid B22 | 672-696 h |
| Day thirty (`day_thirty.toml`) | B22 → B23 | days 29-31 | C-promise-38, *what will keep the pack off?* opened Y6, advanced Y7, paid B23 | 692-730 h |
| Day thirty-one (`day_thirty_one.toml`) | B23 → B24 ★ | days 31-33 | C-promise-39, *what is the house on the hill?* opened Y9, advanced Y10, paid B24 | 725-790 h |
| Day thirty-three (`day_thirty_three.toml`) | B24 → night 35 | days 33-35 | C-promise-40, *what opens the black door?* opened Y12, advanced Y13, paid B25; then C-promise-41, *will the charcoal mark last?* opened Y14, paid Y15 (the night's own list, as `day_nineteen_night`) | 770-840 h |

The calendar holds both ends: the Drift's turn is a clock beat at 672 h (2 419 200 s) and the Clear's (week six) at 840 h,
so story days 29 to 35 are calendar days 29 to 35. Between, B22 to B25 are play-driven, held on sharp by the season's clock
where a sharp floor falls after the turn (only B25's: 687 h).

**What each chapter teaches, one new system at most per visit:** day twenty-nine, the season's return with its chore
and no ready-made rule, then a choice that is the yes joke's (who takes the first cart); day thirty, the supply line
(carts in the mix, an outpost's upkeep, a raid on the line and what prepares against it), the tracker, and rule 3 (a
reagent: hair); day thirty-one, a second destination for the walks, the week's long goal (the waystation), a second
raid and its latch; day thirty-three, a door opened by who you are, and the week's night.

**What changed from `spine.md` and `beats.yaml`, and why:**

1. **B22's gate gains the first run and the turn** (D-207). On P4 alone it lands when the post's last stage does, which
   on sharp is before the turn and the season that makes the run what it is. The first run is Lucy's ask (O-first-run):
   either answer runs it, so the spine never waits on a yes; B22 lands at the run's finish.
2. **No one dies on the cart** (D-207). Week three's note listed "B22's cart" among later deaths; C-beat-22 does not,
   and its cost field is stores. Two weeks ran on a death each (the cutter, the player); this one costs the load and the
   road, and the "and" of its no_and is that they know the road now.
3. **B23's gate is a story step, B22, Arcana L1 and hair** (D-209). The spine's "arcana 25" is a pre-calibration
   number: typical stood at Arcana 14 at 504 h (measured, week four) with the phase's top at 22, so 25 means a push past
   the top in week five, which no route makes. Arcana L1 is a placeholder (15, estimated reached by every route before
   the turn); what holds B23 is the season's morning on day 31 and the hair, which is a choice of where pelts go.
4. **The repeatable cascade is a system; the first one is a story** (D-209, D-210). B23 is A42's finish, told (a beat's
   outcome carries no odds, as B20's death did). The working the player keeps is the Spells row's first slice
   (`docs/design/week-five-plan.md`), and it lands beside the chapter, never in front of it.
5. **B24's gate is A43** (D-212), the player waking the house's ward, which waits on P5's eighth stage: P5 is the town's
   labour and timber, A43 the player's Arcana (`regions.md`, P5).
6. **B25's gate: A44, B24 + 36 h, Wayfinding L2 and a floor** (D-213). Wayfinding 25 meets the same pre-calibration
   problem as B23's arcana; L2 is a placeholder (12) for the simulator to set to what typical reaches by day 34. B25's
   `unlocks: {system: skill_prestige}` is dropped: prestige ships already (`decisions.md`, "Prestige is per skill, and
   finite"), so B25 unlocks nothing systemic.
7. **The post becomes an outpost with no outpost state** (D-205): a store at the post, carts that fill it, an upkeep line
   that drinks it, a raid that takes from it. `decisions.md`, "The town": "an outpost is a building far away, its upkeep a
   line in the town's ledger... no new system".
8. **N5 is cast, not authored** (D-208): `cast.md` casts the tracker from whoever has walked most, and the town twins'
   card counts are per lane, so the cast reads them at B22.
9. **The Drift has no day-night cycle** (D-115), as before: one brown grade by day, two story nights (night 30, Y6's
   pack in the warm dark; night 35, Y15).
10. **The week's last beats are a night list** (`day_thirty_five_night`, as `day_nineteen_night`): B25 closes day
    thirty-three's list and pays its question, so the night's two beats need their own small one.

## Decided here: what week four left to week five

**1. B22's moment (D-207).** The post's last stage, the turn and the first run. O-first-run shows when the post's
twelfth stage is done and Y2 has landed (the prints), and the run is ready from the morning after (`drift_clock` ≥ 516,
684 h). Typical's last stage is estimated at 680-700 h, so B22 lands 686-705 h on typical: inside its band only if the
post finishes on time (week four's lever, the post's charwood per stage, stays week four's; the run's ready hour is a
morning and never moves).

**2. The fiddler's first tune (SL37).** On the first evening of wind (`drift_clock` ≥ 508, 676 h). He said "not while
the air's like this", and the air isn't.

**3. The Drift's chore rules at its turn (D-203).** D-155 left the shipped order cards of the Drift's and the Clear's
chores "until those seasons are next written". The Drift is written now, to row 43: the roofs' chip returns with its hint
dot and the shipped order card is not offered again (plan item 1). The rule is the player's to write, as the Still's was.

**4. A rule the player wrote for a chore, at its season's end (D-202).** Kept. `decisions.md`, "Each season brings its
own chores", says such a rule goes away when its season ends, "probably", in text written while the game wrote the
chore rules through order cards; D-126 removes rules the game made. A rule the player wrote is the player's decision,
and removing it is the game deciding for them ("Tools early, choices kept": automation never decides). The Still's rule
on `ashed` stays and cannot fire, because its chip cannot show (item 6 drains the film); when the Still comes round in
week seven it is there. Asked of the owner in spoiler-free terms (For the owner, 1); the answer changes one line of item
1, nothing else.

**5. Sorrel's book (D-218).** Not offered again: `bind_book` stays on the tasks for good (week four). While
`book_given` holds, `s_sorrel_book` writes one page a story day on `drift_clock` thresholds 528, 552, 576, 600, 624, 648
and 672 (the mornings of days 30 to 36, the last falling in week six's first hours), each a little at odds with the day
before. No page mentions a wrist, a door or a mark.

**6. The Still's machinery at the turn (D-202).** `settle` ends with `still_left` at 672 h; `film` would sit where it
stands, and with film ≥ 12 the `ashed` chip would show for three weeks. The turn adds `still_end_left` 1 and opens
`still_ends`, a standing that drains 24 film and 24 `fish_rising` an hour on that pool (week four's `thaw` idiom): the
wind breaks the water and takes the film, within the hour.

**7. N5's casting (D-208).** See "The tracker (fit pass)".

**8. Stores with no sink at night 28.** Measured at day twenty-five's end on typical (readout `weektwo-twentyfive.txt`,
an 8 h absence): stakes and wraps 100% lost, roots 98%, stones 71%, charwood 19% (73% over 24 h). Week five's sinks: the
iron latch takes stakes, P5 takes stones and charwood, the hill's walks and the upkeep line take what the carts carry.
Roots have no new sink this week; the lever is the table's eaters (the burners), never a sink made for its own sake.

**9. Who goes.** Still one person per walk (`design/banked-time.txt` "BANKED TIME", KNOWN GAPS, "Who goes"): the hill is
walked alone, the tracker scouts alone. The first trip whose fight needs a side made of who goes stays week seven's.

## Finite pools: nothing progress needs can run out

Owner direction, binding (week four): no finite resource can lock a careless player out of content or progress. Week
five meets it by the same rule: **every store a gate or a required build reads has a maker that never runs out**; the
season's pools feed only things the story does not wait on.

| Finite pool | Filled by | Drawn by | What reads it | Lock possible? |
|---|---|---|---|---|
| `drift_left` (+336) | Y1 | `ashfall` (2 an hour) | nothing: it times the roofs' chore | no: machinery |
| `track_left` (144) | B22 | `track_drift` | nothing: it times the track's chore | no: machinery |
| `still_end_left` (1) | Y1 | `still_ends` | nothing | no: machinery |
| `bloom` (+2000), `bear_sign` (+6) | Y1 (week two's sizes) | the fungus cards, `hunt_bear` | nothing | no: optional gifts |
| `moths_up` (24) | Y5 | `net_moths` and its twin | nothing: moth-dust is one of three preparations on the line | no: a raid only slows the line |

| Store progress takes this week | Taken by (required) | Its makers | Optional takers |
|---|---|---|---|
| smoked | A41 (B22's load), the carts, the table (arrivals) | the smoke lane on catch (snares, the hunts, the boar) | the bear hunt, the boar hunt |
| `post_stores` | the hill's walks (Y9), P5's stages (B24) | `run_cart` and its twin, from smoked, uncapped | the upkeep line (charwood), the jobs |
| charwood, stones, cord | P5 | the walks, the upkeep line, the hill's walks (stones), everyday cards | the iron latch (cord) |
| hair | A42 (B23), 3 | `comb_pelts`, from pelt (the wolf and boar hunts, uncapped) | `ward_gate`, the jump |
| `hill_trips` | Y9, P5 shown | every hill walk | none: a count, never drawn |

Shapes that needed care: **the raids take from `post_stores`**, which progress reads; they take at the rate preparation
earns and the carts refill from smoked, whose makers never run out, so a raided line is slower, never shut (the people
decision: "a raided line slows its outpost and loses some cargo, never collapses"). **The latch is optional**: the hall's
raid takes smoked at its rate whether or not the latch is built; the latch lowers it. **Moth-dust is finite and optional**:
the tracker's card and the latch are the uncapped preparations.

## Day twenty-nine (Y1 → B22): what has been at the post's door?

In the night the wind comes back, warm, out of the east, and by morning the ash is coming down so thick the noon is
brown and the roofs sag. That evening the man with the cloth bundle unties it. Out at the trees the post is finished,
its store shut behind a hide door on a hasp, and in the fresh ash all round it are prints with long toes, and scratches
round the hasp. Next morning the pin is out of the hasp and laid on the step, and nothing inside is touched. Lucy says
the post needs its first load taken out.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 29a | after night 28 | the wind; ash by the bucket | (will the roofs hold?) | Y1 |
| 29b | 3-9 h | the roofs' chip; the fiddle | | side SL37 |
| 29c | 3-9 h | prints at the post's door | what has been at the post's door? | Y2 (opens) |
| 29d | 3-9 h | the pin laid on the step; Lucy's ask | | Y3 (advances); O-first-run |
| 29e | 0-9 h | the cart pulled away in the brown dark; the tracks read | (they know the road now) | B22 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 29a (3-5 min) | reads Y1; the bloom against the post's last stages; the bear's sign | Y1 at 672 h: `drift_two`, the Drift's grade, `ashfall` resumed on `drift_left`, `still_ends`, the bloom and `bear_sign` refilled | brown light, ash falling heavily, the roofs thick with it | l_y1_1 to l_y1_3 |
| 29b (3-5 min) | meets the roofs' chip with its hint dot and no rule offered; clears by hand or writes the rule; reads SL37 | `ash_laden` at roof ash ≥ 16 (about 680 h); SL37 at `drift_clock` ≥ 508 | the fiddler at the fire, the cloth on his knee | l_fiddle_plays (SL37) |
| 29c (3-5 min) | reads Y2; the post's last stage | Y2 at `drift_clock` ≥ 510, `post_door` done | the post is a map stamp: the scene shows the prints only in the line | l_prints_1, l_prints_2 (Y2) |
| 29d (3-5 min) | reads Y3; answers **O-first-run** | Y3 at `drift_clock` ≥ 516, once Y2; O-first-run at Y3 once the post's twelfth stage is done | a peg on a step (the journal's sketch, not the scene) | l_pin (Y3), l_first_run_ask |
| 29e (3-6 min) | taps or has queued **Take the cart out** (A41), or has said someone else; reads B22; meets the tracker | A41 ready at `drift_clock` ≥ 516; B22 at the run's finish | the brown dark under the trees; then the cart's empty place at the post | l_b22_1 to l_b22_4 |

### The Drift, again (fit pass)

**What it is:** the second Drift, the first season to come round since seasons became content. **Instance of:** week
two's Drift (D-115): an `after_time` turn, standing actions on pools the turn fills, a chip and its cures, cards on finite
pools, a threat step on the season's clock. **Fits into:** Clock, Triggers, Standing actions, Cards, Chips, Combat. No
season state, no new clock store: the season reads `drift_clock`, which has run since B8, offset by 504 (D-201).
**New only in two ways:** it is written to row 43 (no order card for either chore), and its second chore is out on the
supply line, so the season's trouble moves with the town.

**What comes back and what is new.** The weather, the roofs, the bloom in the scrub and the bear's season come back as
they were: a returning player meets what they learned in week two, and a mix saved then still means something. What
is new is everything out past the ridge: the track to the post drifting over, moths at the post, the mourners' road.
The weather is the same; the new trouble is out where the town has moved to.

| Store | Cap | Drawn | Notes |
|---|---|---|---|
| `drift_left` (week two's) | 336 | never | Y1 adds 336; `ashfall` draws 2 an hour, so it ends at 840 h, the Clear's turn |
| `roof_ash` (week two's) | 48 | never (the chip is its face) | `ashfall` makes 2 an hour, as in week two |
| `still_end_left` | 1 | never | Y1 adds 1; `still_ends` draws it in an hour |
| `track_left` | 144 | never | B22 adds 144, so on typical's B22 (about 696 h) it ends at about the Clear's turn; `track_drift` draws 1 an hour |
| `road_ash` | 48 | never (the chip is its face) | `track_drift` makes 1 an hour |
| `bloom`, `bear_sign` (week two's) | as shipped | yes | Y1 adds 2000 and 6 |

| Card / standing | Lane | Opened by | Bar (s) | Takes | Makes | Skill |
|---|---|---|---|---|---|---|
| `still_ends` (standing) | | Y1 | | 1 `still_end_left` an hour | drains 24 film and 24 `fish_rising` an hour | |
| `track_drift` (standing) | | B22 | | 1 `track_left` an hour | 1 road ash an hour | |
| `clear_track` | hands | the chip's first showing | 600 | drains up to 12 road ash | 3 cleared | Scavenging |
| `{lane}_clear_track` (town card) | every lane | the chip's first showing | 2400 | drains up to 12 road ash | 3 cleared | |

| Chip | Shows while | Cost (words) | Cure |
|---|---|---|---|
| `ash_laden` (week two's) | roof ash ≥ 16 | "rest slower" (as shipped) | `clear_roofs`, `{lane}_clear_roofs`; **no order card** (D-203): the hint dot, and the player's rule |
| `drifted` | road ash ≥ 12 | "the carts go slower": every cart's speed −33% | `clear_track` (hands, cuts in), `{lane}_clear_track`; **no order card**; the hint dot on its first showing |

**The roofs.** As week two, and the town has more roof now: the chip costs the player's rest while it shows. Who
climbs is the decision (any lane but the old man's, or the hands). Two clears a day under a rule.

**The track.** The ash drifts over the cleared track between the road's end and the post, and the carts bog in it. Left
alone the chip shows from about 12 h after B22 to the Clear's turn and every cart is a third slower: P5 and the hill's
walks are later, never stopped. Clearing it makes cleared, the post's and the waystation's material, so the chore feeds
the build it slows. One cure a day under a rule.

**The bear and the bloom.** Week two's shapes, refilled. Nothing waits on them. The bear is the player's to seek, as
before; it never comes to the camp.

**The threat step.** The Drift's step on the pack (week two's, at `drift_clock` ≥ 12) has fired; the season adds nothing
to the pack. The week's new threat is the mourner (day thirty), and its step is R2's clock's (`r2_clock` ≥ 312, about 772
h: `regions.md`, R2 days 13+, "Mourners raiding the logging line").

**What the Drift adds and does not:** no rate raised (D-115); both chips lower a rate only while they show.

### The first run (O-first-run) (fit pass)

**What it is:** Lucy's ask that someone take the first load out to the post. The spine's "you said you'd take the first
run". **Instance of:** Lucy's jobs (D-133): an offer of no kind whose yes queues a hands one-off; and a two-answer offer
whose other answer still moves the story (O-book's shape, week four). **Fits into:** Offers, Cards, Triggers. No engine
work.

| Answer | What it changes |
|---|---|
| **I'll take it** | queues A41 `first_run` (hands, glows, cap 1, 3600 s, 6 smoked: the load), ready at `drift_clock` ≥ 516; B22 at its finish. Counts as a yes (S-yes reads it) |
| **Someone else** | starts a hidden two-hour clock (`run_town`) and drains the same 6 smoked; B22 at its end (a second trigger, guarded as D-173's pair). Lucy finds someone, never who. A small named echo: the day's chronicle names the answer |

Either way B22 lands and costs the load. The yes costs the player's hour and pays the joke ("you said yes"); the no costs
nothing more and leaves the joke unsaid. Rejected: a beat that waits on a yes (a spine lock); a run with no ask (the joke
is only ever about a choice the player made, `decisions.md`, "Tone").

### The post as an outpost (fit pass)

**What it is:** from B22 the post is the first outpost: people stay out there cutting charwood, carts take food out, and
the walks to the far hill start from it. **Instance of:** "an outpost is a building far away, its upkeep a line in the
town's ledger (food and tools out, ore back): no new system. Under-supplied, it slows, never collapses; standing orders
run the supply" (`decisions.md`, "The town"). In the engine: a store, a trip-shaped card and its town twin that fill it
from smoked (a card converting one store into another, week one's shape), a standing action that drinks it and pauses dry
(the visitor's pause, week two), and a standing fight whose losses take from it (the pack's shape, which takes smoked).
**Fits into:** Stores, Cards, Standing actions, Combat, the Chronicle. No engine work, no outpost state. Rejected: a
supply-line system with routes and cargo (a second copy of Cards and Stores); a cart that carries a person (backup stays
a KNOWN GAP); an order card for the cart (it is a flow in the mix, not a build or a chore, so the player holds it at a
share; nothing needs a rule to run it).

| Store | Cap | Drawn | Notes |
|---|---|---|---|
| `post_stores` | 24 (36 from Camp 20) | yes | what is in the post's shut store: carts fill it; the upkeep line, the hill's walks, P5 and the raids draw it |
| `line_fought`, `line_lost` | 20000 | never | the line's raid tallies |

| Card / standing | Lane | Opened by | Bar (s) | Takes | Makes | Skill |
|---|---|---|---|---|---|---|
| `run_cart` | hands | B22 | 2400 | 4 smoked | 4 `post_stores` | |
| `{lane}_run_cart` (town card) | every lane | B22 | 9600 | 4 smoked | 4 `post_stores` | |
| `post_upkeep` (standing) | | B22 | | 1 `post_stores` an hour | 1 charwood an hour (the crew out at the trees) | |

**Why smoked:** the post's crew eats what the table eats, so the line is the week's first trade against the arrivals,
as the walks were last week. The cart's bar is its haul: 4 for 4, so the line costs only its time and the smoked.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| Y1 | 29a | 672 h (`after_time` 2 419 200 s) | In the night the wind comes back, warm, out of the east, all at once. By morning the ash is coming down so thick the noon is brown, the roofs sag under it, and the fog is gone off the stream. Martin is up on the hall roof with a shovel before anyone asks. | down · none · wry · none · PC · none · th-burn middle |
| Y2 | 29c | `drift_clock` ≥ 510, `post_door` done | Out at the post the fresh ash all round the shut store is printed with tracks: a big cat's, but the front toes long and spread, like fingers. The hide door is shut. Round the hasp the wood is scratched pale. | down · none · dread · none · PC · opens C-promise-37 · th-network middle |
| Y3 | 29d | `drift_clock` ≥ 516, once Y2 | Next morning the pin is out of the hasp and laid on the step, square to the door, and the door is shut. Inside nothing is touched. | up · none · dread · none · PC · advances C-promise-37 · th-network middle |
| B22 | 29e | A41 finished or `run_town` ≥ 2; the post's twelfth stage; `drift_two` | As `spine.md`. Under the trees in the brown noon the cart is pulled backward out of the player's hands, and the tail-pins are drawn and dropped one by one in the ash; the load goes off into the dark in pieces. The player walks on to the post with nothing. Next morning a forager kneels over the tracks and says what they are: cats, that know how a pin comes out; and that they have the road now. | as `beats.yaml` (down · no_and · grim · stores · N1, N5, PC · advances C-promise-7 · th-yes middle), and pays C-promise-37 |

**Mechanically:** Y1 is a trigger at 2 419 200 s (`season = true`) whose outcome unlocks `drift_two`, `still_ends`, adds
`drift_left` 336, `still_end_left` 1, `bloom` 2000 and `bear_sign` 6, and nothing else (the roofs' chip arrives on its own
store). Y2 and Y3 are lines. O-first-run's trigger is Y3 and the post's twelfth stage. B22's outcome: the cast (D-208,
below), `run_cart` and its twins, `post_stores`, `post_upkeep`, `raid_line`, `walk_hill` and its twins, `track_left` 144,
`track_drift`, the map's label on the post's place, `e_mourner` (written at the first raid), aim_line, Lucy's jobs'
countdown, and starts `line_clock` (hidden, D-150's shape) for day thirty. The load is spent by A41's input or the
other answer's drain; B22 takes nothing more. A save rebased past 672 h when week five ships gets Y1 at the rebase
instant.

The tracker is named in B22's line by the role slot `{tracker}` (D-208); before B22 nobody is.

### Side layer (day twenty-nine)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL37 | thread | th-town | `drift_clock` ≥ 508 | That evening the fiddler unties the cloth, looks at the fiddle a while, tunes it with his ear down on the wood, and plays. The three women know the tune. Lucy doesn't stop them. | (none of its own: it shares 29b with the roofs' chip, whose decision is the rule) |

SL37 answers SL30 (no singing in the Still where Lucy comes from) without saying so: in the wind, she lets it go on.

## Day thirty (B22 → B23): what will keep the pack off?

The carts run, the tracker walking ahead of them. One doesn't come in: it is found on the track with its pins out and
laid in a row. Over the fungus at the post, moths as wide as two hands rise in the brown dark, and under them nobody can
hear their own feet. On the second night of wind the pack comes right into the yard, past the watch, and sits down facing
the hall door, more of them than anyone has counted, and nobody goes out. Combing the pelts by the fire the next day, the
player holds a hank of hair over the coals to dry it, and the heat goes into it all at once.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 30a | 3-9 h | a cart found with its pins in a row | (how do you keep a line?) | Y4; side SL38 |
| 30b | 3-9 h | moths that eat sound at the post | | Y5 |
| 30c | 3-9 h | the pack in the yard, facing the door | what will keep the pack off? | Y6 (opens); side SL39 |
| 30d | 3-9 h | heat into hair all at once | | Y7 (advances) |
| 31a | 0-9 h | one move through the whole pack | (and what did that cost?) | B23 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 30a (3-5 min) | reads Y4; the cart's share against the table's; the tracker's share; reads SL38 | Y4 at the first lost raid (`line_lost` ≥ 1), once B22; `raid_line` live since B22; SL38 with the tracker's card | (map stamp) | l_y4_1, l_y4_2, l_track (SL38) |
| 30b (3-5 min) | reads Y5; nets moths against the post's carts | Y5 at `line_clock` ≥ 14: `moths_up` 24, `net_moths`, `dust`, `dust_line`, `e_hush_moth` | (the post is a map stamp; the journal's moth) | l_moths_1, l_moths_2 (Y5) |
| 30c (3-5 min) | reads Y6; meets `comb_pelts`; reads SL39 | Y6 at `drift_clock` ≥ 540 (night 30), once B22: `comb_pelts`, `hair`; SL39 at `line_clock` ≥ 18 | night grade; wolves sitting in the yard facing the hall door | l_y6_1, l_y6_2 (Y6), l_words_elk (SL39) |
| 30d (3-5 min) | reads Y7; meets **Call the heat out** (A42), shown unready with its countdown | Y7 at `hair` ≥ 3, once Y6: A42 shown | the player's hands over the coals, a hank of grey hair | l_hair_1, l_hair_2 (Y7) |
| 31a (3-6 min) | taps or has queued A42; reads B23; meets the ward | A42 ready at `drift_clock` ≥ 552 (720 h); B23 at its finish: `ward_gate` | first light; the yard empty, tracks going out in every direction | l_b23_1 to l_b23_4 |

### Raids on the line (fit pass)

**What it is:** the mourners, who now know the road, taking from the carts and the post's store. **Instance of:** a
standing fight on a threat (the pack's, which takes smoked on a loss), its losses taking a store, its strength a
threat's base plus steps on a region clock (D-138: `r2_clock`, no region state). **Fits into:** Combat, Standing actions,
Stores, the Chronicle, Knowledge (the creature page). No engine work.

| Standing fight | Side | Threat | Fights an hour | On a loss | Tally |
|---|---|---|---|---|---|
| `raid_line` (from B22) | `line` | `mourner` (base 10, placeholder) | 0.5 | 2 `post_stores` | `line_fought`, `line_lost` |

| What holds the `line` side | How | Opened by |
|---|---|---|
| the tracker's card `{lane}_track` (only on the cast lane) | holds the side while it runs: the tracker walks ahead of the carts | B22 |
| `dust_line` (hands 600 s, town twin 2400 s; 1 dust) | holds the side while it runs: the carts' wheels and the post's hasp dusted, so nothing hears them | Y5 |
| nothing else | a line with no one on it loses about one fight in two | |

| Threat | Base | Step |
|---|---|---|
| `mourner` (R2) | 10 (placeholder: an unheld line loses about half, a held one about one in five) | +25% at `r2_clock` ≥ 312 (`t_mourner_step`) |

Odds unknown until the first raid (blind until learned); its page (`e_mourner`) is written then, with its numbers. A
raid never takes a person, never takes more than the store holds, and takes at the rate preparation earns (`decisions.md`,
"Chance shows, preparation decides"). The preparation check: a route that keeps the tracker on the line loses measurably
fewer `post_stores` from B22 to night 35 than one that puts the tracker on the post's stakes.

### The tracker (fit pass)

**What it is:** N5, risen at B22 from whoever has walked the Ashwood most, reading the mourners' tracks. **Instance
of:** a risen notable (`cast.md`: "an authored role, cast per save from whoever is in town when its gate opens"), the
first whose casting reads the save's own history. **Fits into:** People (notables, `name_key`, a later label), Unlocks
(the cast is an only-growing fact, like a join), Catalogue (a town card expanded on every lane, each requiring its lane's
cast). New: an outcome part that casts a role from per-lane card counts, and a role slot in text (`docs/design/
week-five-plan.md`, item 3). Rejected: a fixed person (on a route where that lane never walked, the line "the one who
had walked it most" would be false); a cast decided by a model (behaviour is never a model's); a new person for the role
(the tracker rises; nobody arrives with the title).

The cast (D-208): among single lanes (never a group, never a notable), the one with the most `{lane}_walk_ashwood`
completions at B22's instant; with none, or a tie, the most `{lane}_forage` completions; then the earliest to join.
B22's outcome unlocks feature `tracker_<lane>` and the lane's label becomes "the tracker" (`later_labels`); every line from
B22 names them `{tracker}`. Their card:

| Card | Lane | Opened by | Bar (s) | Takes | Makes |
|---|---|---|---|---|---|
| `{lane}_track` (town card) | every lane, each requiring `tracker_<lane>` | B22 | 2400 | | holds `line` while it runs |

The tracker works like anyone otherwise. Their share between the line and their old work is the week's people decision.

### Rule 3 (fit pass)

**What it is:** the third rule of magic, like calls like (`world.md`), found as wonder: heat moves into hair at once,
and one wolf's hair links to its pack. **Instance of:** week three's Spellcraft opening (a discovery on a glowing step,
then a working kept as a card) and the Spells row's first slice (`docs/systems.md`, "Spells": rules as data combined by
a small interpreter; cascades as chains of same-instant events under the firing cap). **Fits into:** Cards, Skills,
Combat (a card that holds a side, the watch's shape), Spells (first slice). D-135 deferred the row to here: with heat,
motion and now a link, there are three things to combine.

| Store | Cap | Drawn | Notes |
|---|---|---|---|
| `hair` | 12 | yes | wolf hair, combed from pelts: rule 3's first reagent |

| Card | Lane | Opened by | Bar (s) | Takes | Makes | Skill |
|---|---|---|---|---|---|---|
| `comb_pelts` | hands | Y6 | 900 | 1 pelt | 3 hair | |
| `{lane}_comb_pelts` (town card) | every lane | Y6 | 3600 | 1 pelt | 3 hair | |
| `call_pack` (A42) | hands | shown at Y7, ready at `drift_clock` ≥ 552 | 600 | 3 hair; Arcana L1 | B23 (glows; story, no odds) | Arcana |
| `ward_gate` | hands | B23 | 1200 | 1 hair | 1 ash (the tithe); holds `gap` +50% while it runs | Spellcraft |
| `jump_pack` | hands | B23, once the Spells row's slice ships | 1200 | 2 hair | 2 ash; the chain (below) | Spellcraft |

**The ward.** A wolf-ward: the player's hand on the gate stone with a twist of wolf hair under it, and the pack keeps off
the gap while it runs. Like into like, so the tithe is small. It holds the side as the watch does, says so on its face,
and is listed with its share in the side's strength. The player is not taught why a stone holds it (rule 4 is B31's):
it works, as the warm stone worked at B6.

**The jump (the Spells row's first slice).** The working the player keeps from B23: heat taken out of one wolf through
its hair runs along the pack, one to the next. The content contract the slice must meet (the mechanism is the plan's
item 6, interface first):

- cast on a linked-group threat (the pack, `creatures.md`'s R1 linked group), it resolves a chain in one instant whose
  length is fixed by the build: the pack's members due within the working's reach, each link a won fight with its own
  chronicle line, under the firing cap;
- the reach is shown on the card before the tap ("reaches up to n"), from Spellcraft's level and the hair it takes;
  chance never sets the length (`decisions.md`, "Chance decides how nice, never how far");
- a chain queued When ready lands the same as a watched one (the 2 AM test); a chain longer than the pack ends at the
  pack;
- its tithe follows rules 2 and 3 from data: like into like along a link is the cheapest working in the game.

Rejected: a timed buff on the side (no chain, nothing to watch run, reads as a potion); a random chain length; the
cascade as a spine requirement (B23 is told, and never waits on the engine).

**The fight it is against.** The pack (week two's `pack`, the gap side). Dying is never involved: the pack is a standing
fight, and only `hunt_boar` carries the death fields.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| Y4 | 30a | `line_lost` ≥ 1, once B22 | A cart doesn't come in. The tracker finds it on the track at the trees with its load gone and its four pins laid in a row in the ash beside the wheel, like tools put down. | down · no · grim · stores · N5 · none · th-network middle |
| Y5 | 30b | `line_clock` ≥ 14 | Over the fungus shelves round the post, moths as wide as two hands come up out of the brown dark in hundreds. Under them nobody can hear their own feet, or the axe, or each other; the dust off their wings sits on everyone's sleeves. | up · none · wonder · none · PC, N5 · none · th-network middle |
| Y6 | 30c | `drift_clock` ≥ 540 (night 30), once B22 | In the warm dark the pack comes past the watch fire and into the yard, and sits down facing the hall door, more of them than anyone has counted. They don't come closer. Nobody goes out. In the morning they are gone and the yard is printed all over. | down · none · dread · none · PC, N1 · opens C-promise-38 · th-survive middle |
| Y7 | 30d | `hair` ≥ 3, once Y6 | The player holds a hank of the combed wolf hair over the coals to dry it, and the heat goes into it all at once, the way it never goes into stone, and comes back out into the hand. | up · none · wonder · none · PC · advances C-promise-38 · th-magic middle |
| B23 | 31a | A42 finished, B22, Arcana L1, 3 hair | As `spine.md`. The next time the pack comes into the yard, the player stands in the hall door with a twist of wolf hair in a fist and takes the heat out of the nearest one through it, and it doesn't stop at one: the next shivers, and the next, all the way round the yard, and they get up and go, all of them, into the dark. The grey on the player's hand goes to the elbow. Lucy, behind them, says nothing at all. | as `beats.yaml` (up · yes_but · wonder · time · PC · th-magic end), and pays C-promise-38 |

**Mechanically:** Y4 is a trigger on `line_lost` ≥ 1 (the first loss the shuffle bag draws: its instant is the
engine's, the same watched or not). Y5's outcome adds `moths_up` 24 and unlocks the moth cards and page. Y6 unlocks the
combing and starts the night grade (`drift_clock` 540 to 552, a hidden clock the scene reads); B23's morning ends it.
B23's outcome unlocks `ward_gate`, the Arcana page's note `n_like_1` (heat goes into hair at once; one wolf's hair, the
whole pack) and starts `call_clock` (hidden) for day thirty-one. Its cost is A42's ten minutes and the hair; "time" is the
spine's field. Rule 3's "but" is Y8, the next morning: the town has a ward for wolves and none for what lifts a bar.

### Side layer (day thirty)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL38 | arc (N5) | th-network | the tracker's card first finished | The tracker walks the track ahead of the carts, bent over, reading the ash, and comes back at dusk and tells Lucy where the cats crossed, where they waited and how many, and is right the next day. | the tracker's share: the line or their old work |
| SL39 | thread | th-faith | `line_clock` ≥ 18 | A walked elk comes onto the track by the post and stops on the warm patch. The crew burn it there. The bedesman walks out from town to say the words over it, the whole way, and walks back. | (none of its own: it shares 30c with Y6's combing) |

SL39: the words are said over an animal, which nobody asked for; nobody says it is strange. No line says what moves the
elk or that the words do anything (week four's pilgrim and bedesman must-nots hold).

## Day thirty-one (B23 → B24 ★): what is the house on the hill?

In the morning the hall's larder door stands open, its bar lifted out of its brackets from outside and leaned against
the wall, and the long-toed prints go in and come out. Martin and Edward hammer an
iron latch out of the ruin's scrap. The walks go on past the post now, up the far hill, and at the top the square thing
seen from the dead tree is a stone house, its roof fallen in, a door with no hinges. The town clears it out. Under the
ash on the back wall are lines cut into the stone. Two who burn charcoal in the wood come in to the post's fire. The
latch holds; in the morning one of the cats is sitting on the hall's ridge looking down at it, and then it goes.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 31b | 3-9 h | the larder bar lifted | (the ward was for wolves) | Y8 |
| 31c | 3-9 h | a stone house on the hill | what is the house on the hill? | Y9 (opens) |
| 31d | 3-9 h | the burners; Mary scraping meat | | O-burners; side SL40 |
| 32a | 3-9 h | lines cut under the ash | | Y10 (advances) |
| 32b | 3-9 h | the bear's sign; a job | | side SL41 |
| 32c | 3-9 h | the latch holds; a watcher on the ridge | | Y11 |
| 32d-32e | 3-9 h each | P5's stages; jobs; levels | | |
| 33a | 0-9 h | the house woken | (what was that mark?) | B24 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 31b (3-5 min) | reads Y8; meets the latch (its order card under the stakes line); the latch against P5's coming stones | Y8 at `call_clock` ≥ 6: `larder_torn` (a story drain), `iron_latch`, its order card, `raid_hall`, aim_latch | the hall's larder door open at first light, a bar leaning on the wall | l_y8_1, l_y8_2 (Y8) |
| 31c (3-5 min) | reads Y9; meets P5 (its order card under the post stores line); the hill's walks against the carts | Y9 at `hill_trips` ≥ 2, once B23: `waystation` (P5), its order card, the hill's place labelled, aim_house | (map stamp: the house on the hill) | l_y9_1, l_y9_2 (Y9), l_p5_shown |
| 31d (3-5 min) | answers **O-burners**, or the kind's rule has; reads SL40 | O-burners at `meals` ≥ 380, `call_clock` ≥ 12; SL40 at `call_clock` ≥ 14 | two figures at the post's fire with a barrow of charcoal (map: the line only) | l_burners_1, l_burners_2, l_scrape (SL40) |
| 32a (3-5 min) | reads Y10; a P5 stage | Y10 at P5 stage 3 | (map stamp) | l_y10_1, l_y10_2 (Y10) |
| 32b (3-5 min) | reads SL41; the bear or not; a job | SL41 at `drift_clock` ≥ 590, once Y1 | | l_bear_sign_2 (SL41) |
| 32c (3-5 min) | reads Y11 | Y11 at the latch's last stage, once Y8 | first light; a cat on the hall's ridge, looking down | l_y11 (Y11) |
| 32d-32e (3-5 min each) | P5's stages against the carts and the walks; jobs; finds; Camp 20 | Camp 20 at P5 stage 4 | | find lines; jobs; l_camp_20 |
| 33a (3-6 min) | taps or has queued **Wake the house** (A43), shown at P5's eighth stage; reads B24 | A43 at P5 stage 8; B24 at its finish | (map: the network's places drawn in) | l_b24_1 to l_b24_5 |

### The latch, and the hall's raid (fit pass)

**What it is:** the mourners at the hall's larder from Y8, and an iron latch against them. **Instance of:** a second
standing fight on the same threat (the line's), on a side of its own, and a staged hands build run by one order card
whose finish adds a lasting entry to that side (week two's lamps, `tallow_lamps`, on the gap). **Fits into:** Combat,
Cards, Standing orders, Modifiers. No engine work. The lead-in is Y8 itself: the problem, the latch's card and its
order card arrive in one moment; nothing is locked.

| Standing fight | Side | Threat | Fights an hour | On a loss | Tally |
|---|---|---|---|---|---|
| `raid_hall` (from Y8) | `latch` | `mourner` | 0.25 | 1 smoked | `hall_fought`, `hall_lost` |

| Card | Lane | Opened by | Stages | Bar (s) | Takes (each stage) | Pays |
|---|---|---|---|---|---|---|
| `iron_latch` | hands | Y8 | 4 | 1800 | 3 scrap, 4 stakes, 1 cord | stage 4: "the larder holds" (`latch` +200%, sourced `iron_latch`) and Y11 |

Its order card: "when stakes reach 16, work on the latch". Stakes stood at their cap at day twenty-five's end (measured),
so the latch is a sink that was waiting. The watch (the gap) does not hold `latch`: the cats come over the roof, not
through the gap, which is why the wolf-ward doesn't stop them.

### The house on the hill: the walks and P5 (fit pass)

**What it is:** the walks go on from the post up the far hill (the square on it seen at Wayfinding 5), and the town
clears out the stone house there to wake it. **Instance of:** week four's trip (an uncapped hands card with inputs, a
town twin on any lane, a count store every walk adds to, finds as triggers on the count) whose input is the outpost's
store; and a staged hands build run by one order card (the post's shape), finished by the player's glowing step (A39's
shape, with Arcana's level). **Fits into:** Cards, Triggers, Stores, the Pacing curve (Wayfinding), Town map and world
map. No engine work. Rejected: a destination state for the walks (`design/banked-time.txt` "BANKED TIME", REJECTED);
P5's stages taking smoked from town (the outpost would be bypassed: the walks and the build eat at the post).

| Store | Cap | Drawn | Notes |
|---|---|---|---|
| `hill_trips` | 8760 | never | every hill walk adds 1, hands or town |

| Card | Lane | Opened by | Bar (s) | Takes | Makes | Skill |
|---|---|---|---|---|---|---|
| `walk_hill` | hands | B22 | 7200 | 2 `post_stores` | 2 stones; `hill_trips` +1 | Wayfinding (360 XP an hour) |
| `{lane}_walk_hill` (town card) | every lane | B22 | 28800 | 2 `post_stores` | 2 stones; `hill_trips` +1 | |
| `waystation` (P5) | hands | Y9 | 8 stages, 3600 each | 6 charwood, 4 stones, 2 cord, 2 `post_stores` a stage | stage 3 Y10; stage 4 lifts Camp 20; stage 8 shows A43 | |
| `wake_ward` (A43) | hands | shown at P5 stage 8 | 600 | Arcana L1 | B24 (glows; story) | Arcana |

P5's order card: "when the post's store reaches 8, work on the house". Totals: 48 charwood, 32 stones, 16 cord, 16 post
stores, 8 h of hands. **Why eight stages:** shown about 730 h on typical and done about 780 h (B24's band, 768-792);
what binds is the post's store (the carts against the walks and the upkeep line), so the line's share is what moves the
house. The finds on `hill_trips`: 2, Y9 (with B23); past it the walk keeps paying stones and Wayfinding.

### The burners (fit pass)

**What it is:** two people who have been burning charcoal alone in the Ashwood come in to the post's fire: the
outpost's first people of its own (`decisions.md`, "The town": outposts grow their own people). **Instance of:** week
four's arrivals (D-145's `work` kind: roles food and build, D-147's lasting halves, the table's cost +1 an hour). **Fits
into:** Offers (the kind's rule answers it), Triggers, Stores (arrivals), People (`told = line`). No engine work.

| Offer | Shown | Answers | Each answer |
|---|---|---|---|
| O-burners (kind `work`) | `meals` ≥ 380, `call_clock` ≥ 12 | **To the food** / **To the building** | both join (n24, n25, arrivals +2); their first task by the answer (the carts and the smoke lane, or the latch's stakes and clearing); keeps for good the smoke lane's smoked ×1.10 or all clearing ×1.10; the table +1 an hour |

- **n24**, a woman of fifty, black to the elbows, who does the talking and the bargaining. **n25**, her son, grown,
  who carries. Names by code (`content/team/draw_names.py`, `LATER`): n24 Marian, n25 Nicholas. Light tier: no backstory
  past the charcoal; they knew the house on the hill was there and never went in ("it's not ours").

Arrivals read 28 after them (26 at B21, +2). B34 needs 45 by day 50; weeks six and seven carry the rest.

### Lucy's jobs (fit pass)

As week four's (D-133, D-144): offers of no kind whose yes queues a hands one-off sized to its time; a no costs nothing;
on `ask_wait`'s countdown after the last answer. From B22.

| Id | Lucy: somebody has to... (facts) | Yes: the job (hands, bar) and its one-off | Shown |
|---|---|---|---|
| `j_post_roof` | get the ash off the post's roof before it comes in | `post_roof` (900 s): 3 ash | from B22, on the countdown |
| `j_drag_elk` | drag the walked elk off the track before the carts reach it | `drag_elk` (1200 s): 3 cleared | after `j_post_roof` |
| `j_new_pins` | whittle new pins for every cart, longer ones | `new_pins` (600 s): 2 cord | after `j_drag_elk` |
| `j_hill_stakes` | stake the path up the hill so the walkers keep to it in the dark | `hill_stakes` (1200 s): 3 stones | after `j_new_pins`, the last; waits for B24 |

Each no has its own line; she finds someone, never who. No job is dangerous in the numbers.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| Y8 | 31b | `call_clock` ≥ 6 | In the morning the hall's larder door stands open. The bar is out of its brackets and leaned against the wall beside it, neatly. The long-toed prints go in and come out, and the hams are gone off the hooks. | down · no · grim · stores · PC, N2 · none · th-network middle |
| Y9 | 31c | `hill_trips` ≥ 2, once B23 | At the top of the far hill the square thing is a house of dressed stone, its roof fallen in, a doorway with a door of the same stone and no hinges, standing a hand open. Nothing has nested in it. | up · none · wonder · none · PC · opens C-promise-39 · th-network middle |
| Y10 | 32a | P5 stage 3 | Clearing the fallen roof out, the walkers find a hearth with no ash in it and, under a drift on the back wall, lines cut into the stone, long and straight, with marks along them. | down · none · dread · none · PC · advances C-promise-39 · th-network middle |
| Y11 | 32c | `iron_latch` stage 4, once Y8 | The latch holds. At first light one of the cats is sitting on the hall's ridge with its long front feet together, looking down at the larder door, and it watches whoever comes out, and then it goes. | up · yes · wry · none · PC · none · th-survive middle |
| B24 ★ | 33a | A43 finished | As `spine.md`. The player lays both hands on the house's hearthstone and moves heat into it, and the lines on the back wall fill with a dull red light, like the cracks at camp at night: roads, the marks of houses along them, a great ring of marks round a dark place far off. One mark, near the edge, is where the camp is. The walkers and the tracker sleep inside. Sorrel sleeps outside the door, in the ash, and won't come in. | as `beats.yaml` (down · yes_but · dread · time · PC, N3 · opens C-promise-11, advances C-promise-2, C-promise-3, C-promise-5, C-promise-10 · th-network end), and pays C-promise-39 |

**Mechanically:** Y8 is the visitor's idiom (`larder_torn`: a two-hour drain of 6 smoked on its own clock, pausing at
empty), the same watched or not, and unlocks the latch, its order card and `raid_hall`. Y9 unlocks P5, its order card,
the hill's label (`p_square_hill` labelled when reached, plan item 8) and aim_house. Y10 and Y11 are lines. B24's
outcome reveals the network's places at the larger scale (plan item 8: unlabelled marks, one of them on the camp),
writes `e_waystation` and its wall sketch (the circle's second showing, `mysteries.md` Q5), and starts `ward_clock`
(hidden) for day thirty-three. It takes nothing: its cost is the hours of the house's build ("time").

B24's must-nots: the camp's mark is a mark on a map where the camp is, and nothing else (no line says it is the camp
stone, that it was put there, or that the player is anything); the ring's centre is "a dark place", never named, never a
count of marks; Sorrel's refusal is a fact without a reason.

### Side layer (day thirty-one)

| Id | Kind | Thread | Gate | What happens (facts) | Decision or spend |
|---|---|---|---|---|---|
| SL40 | thread | th-town | `call_clock` ≥ 14 | Every morning Mary takes the meat off the racks and scrapes it with her thumbnail, strip by strip, though nothing settles on it in the wind. Nobody says anything. | (none: it shares 31d with O-burners) |
| SL41 | find | th-survive | `drift_clock` ≥ 590, once Y1 | At the bloom in the scrub, bear sign again: the fungus torn up and the stumps clawed, as at this time before. | the bear hunt against P5 (its odds on the card, known since week two) |

SL40 is the habit that outlived its reason: the Still's scrape kept in the Drift. No line explains it.

## Day thirty-three (B24 → night 35): what opens the black door?

Clearing the last ash from the back of the house, the walkers find a second door, black stone, no handle, warm to the
hand. The tracker and the walkers put a bar to it and it does not move; there is a hollow in its face the width of a
wrist. The player lays their wrist in it, with the mark on it they have had since the first morning, and the door goes
in. The tracker draws the same mark on their own wrist in charcoal, shuts the door and lays their wrist in it, and it
opens for them too; the second time, it doesn't. Behind it, a shaft goes down into the dark, and warm air comes up it.
The tracker keeps the charcoal mark dry for a day, and on the Drift's last night rubs it off at the fire.

### The pull, visit by visit

| Visit | Gap before | What moves the near question | The question the player carries out | Beat |
|---|---|---|---|---|
| 33b | 3-9 h | a black door with no handle | what opens the black door? | Y12 (opens) |
| 34a | 3-9 h | the bar; the hollow the width of a wrist | | Y13 (advances) |
| 34b-34c | 3-9 h each | P5's walks and the line; jobs; levels | | |
| 35a | 0-9 h | the door opens to the mark; and once to charcoal | (what is down there?) | B25 (pays) |
| 35b | 3-9 h | the tracker keeping the mark dry | will the charcoal mark last? | Y14 (opens, the night's list) |
| 35c | 0-6 h | night 35; the mark rubbed off | (week six) | Y15 (pays) |

### Timeline

| Visit | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|
| 33b (3-5 min) | reads Y12; the hill's walks against the line | Y12 at `ward_clock` ≥ 6 | (map stamp) | l_y12_1, l_y12_2 (Y12) |
| 34a (3-5 min) | reads Y13; meets **Lay your wrist to it** (A44), shown unready with its countdown and its Wayfinding row | Y13 at `ward_clock` ≥ 20: A44 shown | | l_y13_1, l_y13_2 (Y13) |
| 34b-34c (3-5 min each) | Wayfinding against the post; jobs; finds | | | find lines; jobs |
| 35a (3-6 min) | taps or has queued A44; reads B25 | A44 ready at `ward_clock` ≥ 36, `drift_clock` ≥ 520, Wayfinding L2; B25 at its finish: aim_shaft | (map stamp) | l_b25_1 to l_b25_4 |
| 35b (3-5 min) | reads Y14 | Y14 at B25 + 6 h | the tracker at the fire, one sleeve rolled, holding the wrist away from the pot's steam | l_y14 (Y14) |
| 35c (3-5 min) | reads Y15; the week's end card | dusk 35 at save time ≥ 834 h; Y15 at dusk, once Y14 | night grade, warm and brown; everyone out in the yard, the fiddle | l_night_35, l_y15_1, l_y15_2 |

### The door (fit pass)

**What it is:** a door that opens to the player's seal, and once to a charcoal copy. **Instance of:** a glowing story
step shown unready with its countdown and a level row (A39's and A38's shape); its finish is the beat. **Fits into:**
Cards, Triggers, Skills (the step's requirement row). No engine work. The "once" is the beat's fact, never a mechanic:
nothing in play opens the door again, and nothing needs to (B26's lift, week six, is re-keyed from the other side of it,
`spine.md`). Rejected: a door that opens to a store or a count (a seal is a mechanism, not a badge: `world.md`, B25); an
offer (there is no other answer: the step is the player putting their wrist to the stone, and the choice is when).

**Why Wayfinding:** the spine gates B25 on it, and the house is the walkers' find: the step needs the player to have
walked the network, not to have read it. Placeholder L2 (12); the requirement shows as its row on the card from Y13.

### The clocks

**Night 30** is Y6's: the night grade from `drift_clock` 540 to 552 (708 to 720 h), a hidden clock the scene reads, as
night 24's. It ends at A42's ready hour. B23 lands at A42's finish, whenever that is tapped, so its line names no hour
("the next time the pack comes into the yard"), and its scene is the empty yard after.

**Night 35** ends the week on the calendar: dusk 35 at save time ≥ 834 h (3 002 400 s, `after_time`), and Y15 at dusk
once Y14. No glowing step: weeks three and four each closed on one (A38, A40), and a third in a row would be the shape
repeating; the night arrives on its own, and the player reads it. Where B25 lands after dusk (lazy), Y14 and Y15 land
after it, the night's two beats in two returns. The Clear's turn at 840 h does not wait on Y15.

### The beats

| Id | Visit | Gate | What happens (the facts) | Turn · outcome · register · cost · moves · promise · thread |
|---|---|---|---|---|
| Y12 | 33b | `ward_clock` ≥ 6 | Clearing the last ash from the back of the house, the walkers find a second door, black stone, set flush, with no handle and no keyhole. It is warm to the hand, warmer than the hearth. | down · none · dread · none · PC, N5 · opens C-promise-40 · th-network middle |
| Y13 | 34a | `ward_clock` ≥ 20 | The tracker and two of the walkers put a bar to the black door's edge and lean on it until the bar bends. It doesn't move. In the middle of its face, at waist height, is a shallow hollow, long and narrow, about the width of a wrist. | up · no · wry · none · N5 · advances C-promise-40 · th-self middle |
| B25 | 35a | A44 finished, B24, Wayfinding L2 | As `spine.md`. The player lays their wrist in the hollow, the mark on it uppermost, and the door goes in a hand's width and swings. The tracker looks at the player's wrist a long time, draws the same mark on their own wrist with a stick of charcoal, swings the door shut, lays their wrist in the hollow, and it opens for them too. They try it again and it doesn't. Behind the door a shaft goes down into the dark, and warm air comes up it. | as `beats.yaml` (up · yes · dread · none · PC · advances C-promise-1, C-promise-2 · th-self middle), and pays C-promise-40 |
| Y14 | 35b | B25 + 6 h | At supper the tracker eats with one sleeve rolled to the elbow and that wrist held out away from the pot's steam, and won't let anyone near it. | up · none · warm · none · N5 · opens C-promise-41 · th-self middle |
| Y15 | 35c | dusk 35, once Y14 | Night 35, warm, the ash still coming down. Everyone is out in the yard because nobody can sleep inside in the heat. The fiddler plays. The tracker spits on their wrist and rubs the charcoal off with a thumb, and it comes away grey. | down · none · wry · none · N5, PC · pays C-promise-41 · th-self middle |

**Mechanically:** Y12 and Y13 are lines; Y13 shows A44 (`open_ward`, glows, narrative, cap 1, 60 s), unready with its
countdown to `ward_clock` 36 (a day and a half after B24, so typical's B25 falls in day 35) and its Wayfinding row, queueable When ready. B25's outcome unlocks feature `ward_open`,
aim_shaft and the journal's day note, and nothing systemic (D-213). Y14 is a trigger on a hidden clock B25 starts
(`mark_clock` ≥ 6). Y15 is week five's last beat.

**The must-nots for day thirty-three.** The mark on the player's wrist is "the mark", the one mentioned on the first
morning: never a seal, a name, a holder, a key, Chequer, or anything it means. The tracker's look is a look. The door
opening "once" for the charcoal is shown, never said ("it doesn't" on the second try). Y15's turn is the reader's: the
charcoal comes off; nobody says the player's doesn't, and no line looks at the player's wrist at night 35. The shaft's
air is warm, and nothing more: no light, no sound, no red, no word for what is down there.

## Levels and finds (week five)

Typical's levels at 672 h are not measured (`week-five-numbers.md`): week four's expectation is Scavenging and
Woodcutting 18, Foraging 12, Cooking 19, Arcana 14-15, Melee 22 (its phase's top), Spellcraft 10, Wayfinding 8. Week
five's finds go only on skills under their phase's top (22); a skill at its top waits for the player's "Push past" click
(shipped), and the first such click may come this week on Melee or Cooking. If the simulator shows typical past a find's
level at the turn, the find moves to the next speed-only level in range; with none left, it is cut.

| Skill | Level | Pays |
|---|---|---|
| Wayfinding | 10 | find: on the path up the far hill, a road marker with its face still cut, the letters unreadable (the map's `p_marker_hill`) |
| | 12 | "Walk the hill: 25% less time" |
| Foraging | 14 | ash-caps on the dead trunks round the post in the wind (fungus +8), requires `drift_two` |
| Spellcraft | 12 | "Ward the gate: 25% less time", requires B23 |
| Arcana | 16 | "Call through hair: one more" (the jump's reach +1), requires the Spells row's slice; until it ships, cut |

No find names the tracker, the house's inside, the black door, the mark, or anything of week six.

## The Camp

| Level | At (camp items) | Pays |
|---|---|---|
| 20 | 6 100 000, held ("?") since week four; lifted by P5 stage 4 | "The post's store holds 36, was 24" |
| 21 | 7 200 000, held ("?") past week five's content | (week six) |

## Stated aims

| Aim | Starts at | Intent |
|---|---|---|
| aim_line | B22 | keep the post fed |
| aim_latch | Y8 | a latch they can't lift |
| aim_house | Y9 | clear out the house on the hill |
| aim_shaft | B25 | (a line for the week's last days: the way down, never what is down there) |

Aims are lines: no season name, no beat.

## The flat check, authored order

Spine and chapter beats from Y1, in landing order on typical: Y1 down, Y2 down, Y3 up, B22 down, Y4 down, Y5 up, Y6 down,
Y7 up, B23 up, Y8 down, Y9 up, Y10 down, Y11 up, B24 down, Y12 down, Y13 up, B25 up, Y14 up, Y15 down. Across the week's
edge: B21 up, I11 down, I12 down, I13 up, Y1 down. Never three turns the same. Y1 is down on purpose: the wind's return
is relief in the fiddle (SL37), but the turn itself is more weather to shovel, and a third up after B21's and I13's
would run three in a row wherever the simulator lands week four's beats. Outcomes: B22 no_and, Y4 no, B23 yes_but, Y8 no,
Y11 yes, B24 yes_but, Y13 no, B25 yes (never two clean yes in a row). Registers: wry, dread, dread, grim, grim, wonder,
dread, wonder, wonder, grim, wonder, dread, wry, dread, dread, wry, dread, warm, wry (never three the same in a row). Costs: none, none, none, stores, stores, none, none, none, time, stores, none, none, none,
time, none, none, none, none, none (two kinds).

**Net:** chapter beats Y1 −, Y2 −, Y3 +, Y4 −, Y5 +, Y6 −, Y7 +, Y8 −, Y9 +, Y10 −, Y11 +, Y12 −, Y13 +, Y14 +, Y15 − = −1;
spine B22 −, B23 +, B24 −, B25 + = 0. The week nets −1 (the flat check counts the chapter beats in the week), so
`week_net_up` raises nothing. The Still also netted −1; this week reads lighter through its texture (the wind, the fiddle,
the cascade), and its ★ is a dread. A scratch run of `flatcheck.py` over
`beats.yaml` with this week's lists added (and week four's day-twenty-seven list as designed) raised only the accepted
exceptions below (`week-five-numbers.md`, "Verified").

The near promises: C-promise-37 opened 29c, advanced 29d, paid 29e; C-promise-38 opened 30c, advanced 30d, paid 31a;
C-promise-39 opened 31c, advanced 32a, paid 33a; C-promise-40 opened 33b, advanced 34a, paid 35a; C-promise-41 opened 35b,
paid 35c. Expected flags to accept (D-219): 29a does not touch C-promise-37 (the prints come with the post's door); 30a and
30b do not touch C-promise-38 (the pack comes on the second night of wind); 31b and 32c do not touch C-promise-39
(near_untouched; visits with no beat raise nothing); and th-town's open end moves from O-widowers to O-burners
(thread_no_end, the acceptance week four already holds, carried to the thread's new last entry). B24's spine entry
keeps its `pays: [C-promise-9]` and gains C-promise-39 in the same list.

## Away from the screen

- **Every planned moment plays in full on return:** Y1, the chips' first showings, SL37, Y2, Y3, B22 (when A41 was
  queued, or on the other answer), Y4, Y5, Y6, Y7, Y8, Y9, O-burners, Y10, Y11, Y12, Y13, Y14 and most of P5's stages land
  while away on typical; each is revealed in order, one at a time.
- **Per absence, at most two moments:** night 28 → 29a brings Y1 (its pools, the drain and the refills are one moment);
  the roofs' chip lands about 8 h on, its own moment with SL37 two hours before it (29b counts two); Y2 waits on the post's
  door and the season's hour; Y3 is the morning after, with O-first-run (one moment); B22 is A41's finish; Y4 is the first
  raid the shuffle bag draws and the tracker's card is B22's; Y5, Y6 and Y7 are on their own clocks or stores, 4-8 h apart;
  B23 is A42's finish; Y8 is 6 h after; Y9 and P5's card are one; O-burners and SL40 two hours apart (two); Y10 and Y11
  are a stage and a build; B24 is A43's; Y12, Y13 and A44 are on `ward_clock`; Y14 is 6 h past B25; Y15 is the dusk.
- **The 2 AM test:** the chips are answered by rules every tool-using route has written before (a chip condition),
  never offered; the cart and the hill's walks are flows in the mix; the latch and P5 by their order cards; O-burners by the
  kind's rule; O-first-run, the jobs and the asks in the visit they show, one-offs queued When ready; A41 to A44 are
  glowing steps shown unready with their countdowns and queueable; the raids, the pack and the bear are flows; the
  moths yield at their end (D-125). The jump (once it ships) lands the same chain queued as watched.
- **Rebased saves:** a save past 672 h when week five ships gets Y1 at the rebase instant; nothing else of week five can
  be past.

## Sharp's floor-bound stretches

Every sharp floor this week falls before the turn but B25's (687 h, `drift_clock` ≥ 520 on A44). Sharp is held by the
season's mornings instead: B22 by A41's (684 h), B23 by A42's (720 h). Between them, sharp waits with two far goals
sharing the town: the post fed (carts against the table) against the hill's walks, and from B23 P5 against the latch and
the bear. Sharp reaches B24 on P5's throughput and B25 on `ward_clock` and Wayfinding; the decide counter keeps the
target of three visits in four with a decision.

## Art

All picked from the packs by `sprite-catalog` first; drawn only where the kit lacks it.

- **Grades:** the Drift (week two's: brown light, warm, ash falling heavy) from Y1 to week six's turn; nights 30 and 35
  (the Drift's night grade: warm dark, the hall's light and the fire the only warm points).
- **World layers:** heavy ashfall (week two's); ash on the roofs while `ash_laden` shows (week two's); the fog layer
  removed at Y1; wolves sitting in the yard facing the hall door (night 30 only, transient `yard:pack`).
- **Player-made (warm):** the iron latch on the hall's larder door (from its last stage). The post and the house on the
  hill are map stamps, not scene stamps.
- **Figures:** the fiddler playing (from SL37, at the fire in the evening grade), the burners (two figures and a
  barrow, on the map's post only: they are at the post), the tracker reading tracks (transient `track:read`, posed on
  whichever lane is cast: the pose keys on the transient id, never a lane), the player in the hall door at dusk with a
  fist raised (transient `door:call`, B23's visit), everyone out in the yard at night (transient `yard:night`, Y15's
  visit), a cat on the hall's ridge (transient `ridge:cat`, Y11's visit).
- **Journal sketches:** the mourner, the hush-moth, and the house's wall (the circle's second showing: lines and marks,
  a ring round a dark centre, by the sketch-test method, looked at before it ships).
- **The map:** the post's place labelled at B22 (`p_warm_patch`), the hill's place labelled at Y9 (`p_square_hill`),
  `p_marker_hill` (Wayfinding 10), and at B24 the network's places at the larger scale: unlabelled marks, one of them on
  the camp's place.
- **Stages:** 84_drift_two, 85_prints, 86_pin, 87_cart_taken, 88_pins_row, 89_moths, 90_pack_yard, 91_hair, 92_call,
  93_larder, 94_house, 95_wall_lines, 96_latch_watcher, 97_house_woken, 98_black_door, 99_hollow, 100_door_open,
  101_wrist_dry, 102_night_35.

## The journal (week five)

| Entry | Written by | Notes (ids; text in the brief) | Numbers shown |
|---|---|---|---|
| `e_mourner` | the first raid | `n_mourner_1` (a big cat whose front feet open like hands; learned pins the way we did: by having hands) | the line's odds, fought, lost |
| `e_hush_moth` | Y5 | `n_moth_1` (wide as two hands; eat the fungus; under them you can't hear your own feet; the dust) | none (not a fight) |
| `e_waystation` (a place) | Y9 | `n_house_1` (dressed stone; no hinges; nothing nests in it), `n_house_2` with B24 (the wall), with the wall's sketch | |
| `e_days_9` | Y1 | days notes on B22, B23, B24 and B25, each at its beat's step | |
| the Arcana page | B23 | `n_like_1` (heat goes into hair at once; one wolf's hair, the whole pack) | |
| `s_sorrel_book` | `book_given` | up to six pages in week five (D-218) | |

No note says what the mark is, what the house was for, what the ring is round, where the shaft goes, or why the cats
learn. The mourner page's numbers are the line's only figures.

## Proposed canon (tentative until the lead confirms)

- C-promise-37 to C-promise-41: the chapters' near questions, as the table above.
- C-beat-155 (Y1) to C-beat-169 (Y15), each as its row above; C-beat-170 (B22's shape), C-beat-171 (B23's shape),
  C-beat-172 (B24's shape), C-beat-173 (B25's shape).
- C-cast-36: N5 is cast per save at B22 from the single lane that walked the Ashwood most, labelled the tracker, and
  reads the mourners' tracks; their charcoal copy of the player's mark opens the black door once.
- C-cast-37: the burners, light tier: Marian, who burns charcoal and bargains, and her grown son Nicholas, who carries;
  they knew the house on the hill and never went in.
- C-creature-27: mourners as first met: they learn a pin or a bar by watching it worked, draw cart pins and lay them
  down neatly, raid the supply line and then the hall's larder, and watch a new latch from the roof.
- C-magic-19: rule 3 as first learned: heat goes into wolf hair at once, and heat taken from one wolf through its hair
  runs through the pack; the ward on the gate stone with wolf hair keeps the pack off.
- C-region-24: the house on the hill (P5): dressed stone, no hinges, a hearth with no ash; woken, its back wall shows
  the network in red light with a ring of marks round a dark place and one mark where the camp is; a black door opens
  to the player's mark; behind it a shaft with warm air coming up.
- C-season-14: the Drift's second time: the wind back warm from the east, the fiddle played, ash drifting over the
  track to the post, hush-moths over the fungus at the post, bear sign at the bloom again.

## For the owner

Two questions, asked spoiler-free in the pass's report:

1. **Rules you wrote for a season's chores.** When that season comes round again, should the rules you set up for its
   chores last time still be there, or should the season ask you to set them up again?
   Recommendation: still there. A rule you wrote is your decision; the game removing it would be deciding for you.
2. **How magic grows.** From here magic can become something you put together from a few parts, so the same few rules
   make many workings and a player who learns them can combine them. The other way is a list of fixed workings you
   unlock one by one. Which sounds more like the game you want? Recommendation: put together from parts.

## Open (content side)

1. **The carts' numbers** (2400 s, 4 smoked → 4 post stores) and the upkeep line (1 an hour) are the simulator's to set so
   typical's `post_stores` binds P5 and the hill's walks without emptying for more than an hour at a time at the
   route's share. Never lengthen a hands bar to move a band.
2. **The mourner's base** (10) and the raids' rates (0.5 and 0.25 an hour) are set so an unheld line loses about half its
   fights and a held one about one in five, and the hall's raid costs the table less than the chip does.
3. **P5's stages** (8 × 6 charwood, 4 stones, 2 cord, 2 post stores) are set so typical's eighth stage lands in day 33
   (768-792 h). If it lands early, raise the post stores per stage before adding a stage.
4. **Arcana L1** (15) and **Wayfinding L2** (12) are placeholders: the simulator sets each to the level typical reaches
   just before the beat's morning, so the level never binds typical and a route that neglected the skill sees the row
   on the card.
5. **O-burners' meals threshold** (380) is an estimate from week four's rates; the simulator sets it so they come in day
   31-32.
6. **Pelts:** hair (A42's 3, the ward and the jump) against the post's door (done), the book (2) and the hides. If pelt
   fails the cap-loss check at day thirty's end, the lever is the ward's hair per run, never a new sink.
7. **Week six must decide:** the Clear's turn at 840 h draining `road_ash` and `roof_ash` so no Drift chip shows in the
   Clear (with the player's rules kept, D-202); P6 (the lift) as week six's long goal from the shaft; the howlet in
   the next Still (week seven); the tracker's arc (`cast.md`: loves the Ashwood, hates the Seams); and the jump's second
   linked group (the moths, R2's own, `creatures.md`).
