# Opening v2: the first fifteen minutes, for a newcomer

Spoilers: this file is under `content/` and never shown to the owner. The screen it runs on is
`docs/design/opening-screen.md` (spoiler-free). Rules it answers to: `docs/decisions.md`, "The opening is fun first"
and the sections after it. Engine model: every card mixable (`cards-design3`, engine `DESIGN.txt`, "CARDS").

## The shape

Fifteen newcomer minutes. In the first minute, quick story steps by hand. A fire is built from four small needs, and
the first mix arrives when two of them pull at once. The fire's fuel line brings the first order, which is also the first
moment the camp runs itself (about minute 6). The camp then has two body needs, a tool that changes the mix, a
choice between two crafts, and an optional second order. Dusk ends it on a question, not a rest.

Three changes from v1 matter most:
- **No gate counts taps.** Every opening is a step the player takes, a cost shown as have/need, a level that pays a
  find, or one of the body's two clock needs. v1's six count triggers are gone.
- **The mix arrives at about minute 3.5**, when stones and wood are both needed, instead of at the edge near
  minute 5. The edge then retires hand-gathering, so the player's own choice sets off the first edit of the mix.
- **The story pulls.** One question is raised in the first minute and sharpened three times. Two clues move in from
  later in the story. The last lines open a door (below, "The pull" and "The end moment").

Newcomer minutes are estimates anchored on v1's real runs (fire at 4–8 min, the two finishes at 14.5 and 15.5 min,
newcomers about 5× the scripted player early and about 2× late). The simulator and `preview_report.py` judge them.

## The pull

**The question raised first:** *who was I?* The player wakes knowing nothing, and the coat holds a book whose front
pages are torn out at the stitching (v1, kept). **The question it grows into:** *what is this place to me?* Each step
below sharpens one of the two.

| # | When (newcomer min) | What the player learns | Thread | From |
|---|---|---|---|---|
| P1 | 0:40, look around | ruin, grey, cold, alone, nothing moving | who | v1 |
| P2 | 1:00, search the coat | the book, its front pages torn away on purpose; charcoal stub | who | v1 (Q5's first clue) |
| P3 | 2:55, first wood off the wall | one wall of the ruin is warm, and ash doesn't settle on it; the wood comes off dry | place | moved in from B5 (warm ground), as a fact of the world |
| P4 | 3:30, the spot cleared | under the ash the floor is cut stone, fitted, warm; the boot found the slab's edge without looking | place, who | moved in: B12's "didn't think about it, just dug", softened |
| P5 | ~7:30, first knap | the flint cuts two fingers; wiping the blood, a mark on the inside of the wrist, old and neat, not a scar from anything remembered | who | Q1's wrist clue (available from B1) |
| P6 | ~11:45, read by the fire | by firelight, a page beyond the torn ones is not quite blank: pressed through from a page torn away, the ghost of a drawing, circles round a circle | who | moved in: Q5's diagram (B12 reads it as a doodle, B36 and B49 pay it) |
| P7 | ~14:30, dusk | as the light goes, the cracks in the cut floor glow dull red, in rings around the slab the player woke on; far off on the ridge, a light that is not the player's fire, then still there | place, and someone else | moved in: B5's night glow; B3's arrival foreshadowed |

The moved-in clues are P3, P4, P6 and P7's glow, all within the owner's yes (an early beat moved in, or a hint sharpened).
Each still reads as atmosphere, not as an answer: nothing says the stone is the player's or that they have been here
before. If the reveal is too much, the softer cut drops P6 to pressed-through tally strokes only (no diagram) and
keeps the rest.

## The end moment

The order matters: the last settling step lands with l_settled, then the evening runs 45 s with nothing new from the
story (the camp working, a clock line at most), so the last step's lines are read on their own. Then, with every line
white (the roots line by the second order, offered since hunger, or by foraging in the mix), the dusk lines fire and
the scene darkens to the glow. The end card follows once those lines have had time to be read (20 s, or the
player's tap after 10 s). Landing all of it in one instant, card 8 s later, read as rushed. The end card stays in the UI register; the hook is
only in the last two log lines and the scene.

**What the player knows at that moment:** they woke here with no memory. Their book was torn on purpose and carries
the ghost of a drawing of circles round a circle. They carry an old mark they can't explain. This stone is warm when
nothing else is, their feet knew it, and it now glows in rings around where they woke. And they are not alone:
someone else has a light on the ridge.

**What they want to know:** who is out there, and are they coming? (the near pull). What is under this floor, and why
did they wake on it? (the deep pull). Who drew the circles, and who tore out the pages?

**Which later beats answer it:**
- Who is out there: **B3** (day 2), the first arrival walking toward the fire. The light on the ridge is hers.
- What is under the floor: partly at **B5** (day 4, the ground is warm and glows at night, now known to the player
  and widened to the whole camp), then **B6** (day 5, the stone answers the player's hand), and in full at **B30**
  (the keel chamber, the circles on the wall).
- The circles and the torn pages: **B12** (the cellar diagram), **B36** ("again"), **B49** (the pages themselves).

The near question is answered in the next session, by a different kind of thing (a person, the town founded). That
is what brings a lunch-break player back tomorrow. The deep one carries the spine.

## Cards, stores, levels

Every card is one card: tapped by hand, or run in the mix when it is a hands card. A one-off is a card with a cap and
moves to Completed at its cap. The rack is another lane and is tapped only (by hand or by an order).

| Card | Lane | Cap | Bar (s) | Takes / per completion | Makes / per completion | Opened by (a step) |
|---|---|---|---|---|---|---|
| stand_up | hands | 3 | 3 | | figure rises a third | start (the one glow) |
| look_around | hands | 1 | 4 | | cold chip | stand_up done |
| search_coat | hands | 1 | 3 | | book (feature) | look_around |
| gather_wood (by hand) | hands, mixable | none | 5 | | 1 damp wood | search_coat |
| scavenge (the ruin, by hand) | hands, mixable | none | 6 | | 1 stone; Scavenging XP | search_coat |
| lay_to_dry (against the warm wall) | rack | none | 45 | 3 damp (5 from Camp 1) | 3 dry (5 from Camp 1) | gather_wood's first completion |
| clear_spot | hands | 2 | 3 | | | lay_to_dry's first completion |
| ring_it | hands | 1 | 3 | 5 stones; requires spot cleared | the ring (feature) | lay_to_dry's first completion (shown unready; fails with its line) |
| strike_fire | hands | 1 | 4 | 1 dry wood; requires ring, flint ≥ 1, nail ≥ 1 | fire (standing), ledger, cold clears | lay_to_dry's first completion (shown unready; fails with its line) |
| forage | hands, mixable | none | 5 | | 1 root; Foraging XP | hungry chip (clock) |
| roast_roots | hands | 1 | 4 | 3 roots; requires the fire | +7 fullness; hunger ×0.1 | hungry chip (shown with forage) |
| rest | hands, mixable | none | 10 | | energy | tired chip (clock) |
| knap_edge | hands | 2 | 3 | 1 flint each | the edge | the fire |
| woodcutting (flint edge) | hands, mixable | none | 4 | | 2 damp wood; Woodcutting XP | knap_edge done; **retires gather_wood** |
| make_stool | hands | 1 | 10 | 3 dry wood; requires Woodcutting 2 | rest ×1.5 | knap_edge done (both crafts at once, one choice) |
| build_fireback | hands | 1 | 10 | 3 dry wood, 4 stones; requires Woodcutting 2 | fire's cost ×⅔ | knap_edge done |
| read_by_fire | hands | 1 | 6 | requires the book | P6 | the first craft built (either) |

Stores: damp wood (cap 12), dry wood (12), stones (12), roots (8), flint (2), nail (1), stool (1); body stores warmth,
fullness and energy as chips only. **Scrap is cut** (v1 made it and nothing used it, so it only ever filled up).

**Finds, never openings.** The first scavenge pays the nail. Scavenging 2 pays the first flint, Scavenging 3 the
second. A find shows on the skill's row before it lands ("level 2: a find"). Knap and strike are already on screen and
name what they need.

**Skill levels and what each visibly opens.** Every skill row shows its next level and what it brings. A story unlock
shows as "?" (something is there, unsaid).

| Skill | Level 2 | Level 3 | Level 4 |
|---|---|---|---|
| Scavenging | flint (~5:00) | flint (~8:45) | ? |
| Woodcutting | both crafts ready (~10:45) | ? | |
| Foraging | ? | | |

**The bar to work toward: the Camp.** One bar, warm (it is the player's), sits with the chips from the moment the
first wood comes off the wall (~2:55). It fills by **work done**: every completion, tapped or mixed, adds its bar's
seconds. So effort and mix time both count, and taps count for no more than the time they take. It is not interactive
in the opening. Each level pays a bonus to something the player already has, stated before → after on the bar's next
marker:
- Camp 1 (~5:00): the warm wall takes 5 at a time (lay_to_dry 3 → 5). It is also v1's drying-wall fix, earned.
- Camp 2 (~12:00): stores hold half again (damp wood, dry wood, stones, roots: 12 → 18, 8 → 12).
- Camp 3 (past the opening): "?". It turns interactive when the town is founded from the camp (B3): from then on
  each level also offers a choice of two, the stool/fireback shape reused.
Camp bonuses never touch a mix card's rates, so no saved mix changes under the player.

Curve values (XP per level, Camp thresholds) are tuning; the targets are the minutes above.

## Timeline

T = taps, D = decisions, cumulative. Minutes are newcomer estimates. "New" marks something the player has not seen
before; **bold** marks a system or a decision (the bigger new things).

| # | Min | Effort | The player does | What appears, and the step that opened it | Scene | Line moments |
|---|---|---|---|---|---|---|
| 1 | 0:00 | T0 | Begin | **stand_up**, larger than any later card, with the opening's one glow | dark; a figure on the ground | |
| 2 | 0:10–0:30 | T3 | stand_up ×3 | each push raises the figure a third | figure kneels, then stands at the wall | l_up_1–3 |
| 3 | 0:40 | T4 | look_around | **cold** chip; search_coat takes stand_up's slot | grade lifts from black to dusk-grey; the ruin readable | l_look (P1) |
| 4 | 1:00 | T5 | search_coat | the book (corner, dot); gather_wood and scavenge, two cards | book icon | l_coat (P2) |
| 5 | 1:15 | T6 | gather_wood | lay_to_dry, unready, "damp wood 1/3 · Gather dead wood" | first sticks by the wall (warm palette) | l_wood |
| 6 | 1:35 | T7 | scavenge | the nail, a find; Scavenging row (next: level 2, a find) | figure at the ruin | l_nail |
| 7 | 2:10 | T9–10 | gather ×2, **lay_to_dry** | rack runs on its own bar, 45 s: the first thing that works without the hands | sticks laid against the wall, steaming | |
| 8 | 2:10–2:55 | T13 | gathers/scavenges by hand while it dries | | | |
| 9 | 2:55 | T13 | (rack lands) | **The fire plan:** clear_spot, ring_it (unready: spot, stones 1/5), strike_fire (unready: ring, flint, dry ✓); the Camp bar | dry wood stacked warm | l_wall (P3) |
| 10 | 3:00–3:30 | T15 | clear_spot ×2 | | the floor scraped back to cut stone | l_clear_1, l_clear_2 (P4) |
| 11 | 3:30 | T15 D2 | **makes the first mix**: the hands strip offers both hand jobs at once (stones for the ring and wood for the wall are both short); one tap, then drags the split | the mix | figure alternates ruin and wood line (mix poses) | |
| 12 | 4:00 | T16 D3 | lays the next batch by hand; adjusts the split as stones and wood come in | | | l_dry_fail possible |
| 13 | 4:45 | T17 | ring_it | the ring (feature) | stones ringed on cut stone | l_ring; l_ring_fail possible earlier |
| 14 | ~5:00 | | (passive) | **Scavenging 2: flint**; **Camp 1: wall takes 5** | | l_flint, l_camp_1 |
| 15 | 5:30 | T18–19 | strike_fire (often one early try first) | **The fire**: cold clears, the ledger with the fuel line red, its order card inline beneath; knap_edge (flint 1/1 for push 1) | fire, the warmest thing on screen; grade warms | l_strike_fail possible; l_fire_takes, l_fire_lit |
| 16 | 6:00 | D4 | **sets the first order** (dry wood ≤ 2: lay to dry) | line turns white; hands strip "runs on" | | **The camp now keeps itself going.** A player who leaves here strands nothing |
| 17 | ~7:00 | D5 | hungry chip (clock) → **forage**; roast_roots unready (roots 0/3) | adds forage to the running mix (a third segment, which shows what it makes per minute), or taps it; eating starts, so the roots line shows red with its order card (once the ledger is in) | figure stoops at the scrub | l_hungry, l_roots |
| 18 | ~7:30 | T20 | knap_edge push 1 | | figure at the fire, knapping | l_knap_1 (P5) |
| 19 | ~8:00 | T21 | roast_roots | the hungry chip clears | roots in the coals | l_roast; l_roast_fail possible |
| 20 | ~8:15 | D6 | tired chip (clock), hands at half speed → **rest** | adds rest to the mix, or taps it | figure sits against the wall | l_tired |
| 21 | ~8:45 | | (passive) | Scavenging 3: the second flint | | l_flint_2 |
| 22 | ~9:00 | T22 | knap_edge push 2 | **woodcutting**; gather_wood retires, so the running mix greys ("holds a retired card · Edit"); **the craft choice**, both cards together (Woodcutting 1/2) | birch felled at the scene's edge | l_knap_2, l_retire |
| 23 | ~9:30 | D7–8 | **edits the mix**: the editor opens on tap; gather is struck through and woodcutting waits beneath with a dot; dragged in, damp wood goes from about +6/min to +15/min, live, before Save | the mix runs again | | |
| 24 | ~10:45 | | (passive) Woodcutting 2 | both crafts ready (if 3 dry wood) | | l_wc_2 |
| 25 | ~11:00 | T23 D9 | **chooses** and builds one craft | the other card shows its time as it now stands; read_by_fire appears | stool (wobbling) or fireback | l_stool or l_fireback (each with its state variants) |
| 26 | ~11:45 | T24 | read_by_fire | | the figure with the book in the firelight | l_stool_first or l_fireback_first as it starts, if the other craft is not built; l_read (P6) |
| 27 | ~12:00 | | (passive) Camp 2 | stores hold half again | | l_camp_2 |
| 28 | ~13:00 | T25 | builds the other craft | the last of the three settling steps | | l_second_craft variants |
| 29 | ~13:30 | D10 | the second order (roots ≤ 3: forage) set since hunger, or foraging in the mix keeping the roots line from falling | every line white | | |
| 30 | ~13:45–14:30 | | dusk 45 s after the last settling step (the evening), with every line white: the same condition as the end card | the light goes; the cracks glow in rings round the slab; a light on the ridge | the scene's dusk grade and glow layer | l_dusk_1, l_dusk_2 (P7) |
| 31 | ~14:30 | | | **end card** (UI register), 20 s after dusk: it goes on, Keep going | | |

Filler taps (extra scavenges, forages, rests, failed early tries) add about 15–20 more, so the run is about 40–45
taps and 10 decisions. v1's two finishers made about 50–53 taps and 2–4 decisions.

## Cadence, in effort

| Bigger new thing | Min | Gap (min) | Effort since the previous one |
|---|---|---|---|
| the story steps (stand, look, coat) | 0:00–1:00 | | 5 T |
| the rack, the first thing that runs by itself | 2:10 | ~1.2 | 5 T |
| the fire plan and the Camp bar | 2:55 | ~0.8 | 3–4 T |
| the first mix (made by the player) | 3:30 | ~0.6 | 2 T, 1 D |
| a level that pays (flint), Camp 1 | 5:00 | ~1.5 | 2–4 T |
| the fire and the ledger | 5:30 | ~0.5 | 1–2 T |
| the first order | 6:00 | ~0.5 | 1 D |
| hunger: forage and roast, added to the mix | 7:00 | 1.0 | 1 D, 2–3 T |
| tiredness: rest, added to the mix | 8:15 | 1.2 | 3 T, 1 D |
| the edge: woodcutting, the greyed mix, the editor, the craft choice | 9:00–9:30 | ~1.0 | 3 T, 2 D |
| the choice made, a craft built | 11:00 | 1.5 | 1 T, 1 D, plus filler |
| the book by firelight | 11:45 | 0.8 | 1 T |
| the second craft and the (optional) second order | 13:00–13:30 | 1.5 | 1 T, 1 D, plus filler |
| dusk and the end | 14:30 | 1.0 | 0 |

So something new comes about every minute, and a bigger thing (a system, or a decision with consequences: rack,
mix, fire with ledger and order, the edge with the editor, the choice, the end) every **1.5–3.5 newcomer minutes**,
each after **about 4–8 actions** (taps plus decisions). That effort stays flat from minute 1 to minute 15 while the
bars get longer, which is the constant-effort rule. The least effort per new thing is around the fire (5:00–6:00),
on purpose: that is the payoff the first five minutes worked toward.

**Runs of one card:** the most a player must repeat one card before something else is worth doing is 3 (the first
three armfuls for the wall). Scavenging by hand is never the only useful card for more than about 3 taps, because
the mix takes it over at 3:30 (v1's worst runs were 12–14 in a row). The longest wait on the current goal is the
first rack (45 s), and it is filled with the nail find, gathering for the next batch and scavenging.

## The mix, taught by need

1. **Made (3:30).** After the spot is cleared, two needs pull at once: stones for the ring, and wood for the next
   batch (and the fire's fuel). The hands strip offers both hand cards together. One tap makes a 50/50 mix, and the
   divider is live to drag. The offer carries the one glow of this stretch, since it is the one obvious next step.
   Declining is fine: the offer stays in the strip until used, and nothing else waits on it.
2. **Grown (7:00, 8:15).** Hunger and tiredness each bring a mixable card. Each mixable card carries its own Mix
   control, so the player adds it to the running mix. The new segment joins with a real share and shows its +per
   minute, and the ledger lines it feeds light while it is dragged.
3. **Re-tuned in the editor (9:00).** The player knaps the edge (their choice), woodcutting replaces gathering, and
   the mix greys. The editor shows the retired card struck through and the new one waiting, with live before → after
   totals. The first edit is the payoff of a decision, never upkeep.
4. **After the opening.** Shipped first: the second mix as a rule. Once the end card is put away, the first time the
   player is tired with no rule on energy, the hands strip offers "While tired → Rest" with Add rule (its order card
   in `opening.toml`: store energy, the tired chip's own `when`, `chip` and `after_end`). Taking it saves a Rest mix
   and a rule that runs it; the player never sees an energy number. When that rule (or any hands rule) first comes on
   by itself, the strip's name glows as the way into the Mixes list. Measured on the scripted player resting by hand:
   the offer about seven minutes after Keep going, the rule's first run by itself about four minutes after it is
   taken. A player who mixed rest in never gets tired, so never meets it. Still to come, one step every few sessions:
   switching by tapping a saved mix in the selector, then writing a mix from scratch.

## Orders

Both are inline under the red line that needs them and show their sentence pre-filled (v1's 4-of-4 set rate after
it shipped).
- First (6:00): dry wood ≤ 2 → lay to dry. It is the first leave-it-running moment: the fire, the wall and the mix
  now run with nobody there.
- Second (~7:00): roots ≤ 3 → forage, the one hands rule. It arrives when eating starts at hunger (the roots line
  starved at 0), so every player meets it before the end; with foraging in the mix it is optional, and the end waits
  for it only while the roots line is red. The spare root v1
  kept goes (starved lines now read as a problem).

## The choice

Stool or fireback, both in view from the edge (9:00), both ready at Woodcutting 2 (~10:45). Each card names only
its upside: rest ×1.5, or the fire eats a third less. The cost is in what the other card's time now reads. Stool
first leaves the open fire eating more until the fireback is built. Fireback first leaves rest slow while tired.
Fireback now also takes 4 stones (it is stacked stone), so scavenging stays worth a share after the ring. That
departs from the spine's "3 dry wood each" only by adding stones. Both get built before the end; the order is the
choice. The stool wobbles (motif, unannounced).

## Away from the screen

With nobody there, the clock can open forage (hungry) and rest (tired). Levels pay finds and make the crafts ready,
which are not unlocks. A day forward with no player: at most two unlocks, as the content test asserts. Whatever is
mid-bar finishes. A player who leaves at 6:00 comes back to a fire still lit, wood stacked and stores full.

## Line moments, and the states each can fire in

Lines are written after this pacing is set, through a voice pass. Each must be true in every state listed. The
variable states across players: cold (until the fire), hungry (from about game minute 7 until the roast), tired (from
about game minute 8, until rested), mix made or not, which craft came first, and whether the book has been read.

| Id | Fires when | States it can fire in |
|---|---|---|
| l_up_1, l_up_2, l_up_3 | stand_up completions 1–3 | only the start |
| l_look (P1) | look_around | only after standing |
| l_coat (P2) | search_coat | before any wood |
| l_wood | gather_wood, first | cold; book found |
| l_nail | scavenge, first | cold; before or after the first wood; any damp count |
| l_dry_fail | lay_to_dry tapped with too little damp | 0, 1 or 2 damp (4 or fewer after Camp 1); first time or later; fire lit or not |
| l_wall (P3) | lay_to_dry, first completion | cold; nail found or not; tapping or idle |
| l_clear_1, l_clear_2 (P4) | clear_spot completions | cold; any stones; mix made or not |
| l_ring_fail | ring_it tapped unready | spot not cleared, or cleared with stones 0–4; mix made or not |
| l_ring | ring_it | cold; flint found or not; dry wood or none |
| l_flint, l_flint_2 | Scavenging 2, 3 | **by hand or by the mix** (the player may be doing something else); ring done or not; for flint 2, the fire lit or (slow player) not; hungry or tired possible |
| l_camp_1, l_camp_2 | Camp levels | before or after the fire (Camp 1 especially); any chips |
| l_strike_fail | strike_fire tapped unready | first blocker any of: no ring, no flint, no dry wood (damp only), spot uncleared; hungry possible for a slow player. One line true for every blocker, or one per first blocker (an engine/content question, below) |
| l_fire_takes, l_fire_lit | strike_fire | cold always; hungry or tired possible (slow players) |
| l_hungry, l_tired | the chip first shows | any point after game minutes ~7 / ~8; fire lit or not; may arrive together |
| l_roots | forage, first | fire lit or not |
| l_roast_fail | roast_roots tapped unready | roots 0–2, or no fire yet |
| l_roast | roast_roots | hungry always; tired possible; edge made or not |
| l_knap_fail | knap_edge tapped with 0 flint | push 1 or push 2 pending; fire lit always |
| l_knap_1 (P5), l_knap_2 | knap pushes | hungry, tired possible; mix made or not |
| l_retire | gather_wood retires | it was in the active mix, in no mix, or (later) in a saved mix not running |
| l_stack | woodcutting, first completion (t_stack): in the wait for Woodcutting 2 | fire lit always; before either craft (they need Woodcutting 2); hungry, tired possible; tapped or mixed |
| l_wc_2 | Woodcutting 2 | crafts ready or still short of dry wood |
| l_stool | make_stool | fireback built or not (v1's "the fireback can wait" bug); tired or not |
| l_fireback | build_fireback | stool built or not |
| l_read (P6) | read_by_fire | sitting on the stool or before the brighter fire (whichever came first); the other craft built or not; any chips |
| l_stool_first, l_fireback_first | read_by_fire starts, that craft built and the other not | the fire burning, or out for want of dry wood (as for l_read); any chips; never once both crafts stand |
| l_dusk_1, l_dusk_2 (P7) | the end condition | which craft came first; the book read or **not yet** (it can still be on the panel, so the dusk lines must not lean on the drawing; the player makes the link, or meets it later); chips any |

Easter-egg lines for early taps come last, from the full map of what can be tried when (for example ring and strike
from 2:55, roast before the fire, knap with no flint).

## Kept from v1, and why

- **The story steps by hand at the start** (stand ×3, look, coat): the A Dark Room hook, and it reads as weakness felt.
  The three pushes now each move the figure, so the very first taps change the picture.
- **Coat before wood:** the book is always found, so later lines can rely on it.
- **Damp, dry, strike-early-fails:** an honest world (B2, C-beat-65), and the failed strike is a try players enjoy.
- **Cold chip clearing at the fire, the ring that can be tried too early:** each failure line is the fun.
- **Inline order card under the red fuel line:** every player who saw it set it.
- **Hunger and tiredness arriving by the clock with their cures:** the only clock gates, and they are needs.
- **Tools before skills:** woodcutting only with the edge, which retires gathering by hand.
- **Stool or fireback** (B2), **the roots order at hunger**, and **the dusk end card** with Keep going.

## Cut or changed, and why

- **Every tap-count trigger** (6 gathers for the rack, 12 for the ruin, 4 scavenges for clearing, 10 and 13 for flint,
  5 forages for roasting): the chore that lost players. They become steps (first armful, the wall's first batch, the
  cleared spot), costs shown as have/need, and levels that pay finds.
- **The page-made first mix:** the player makes it, at the moment two needs pull.
- **Scrap:** made, never used, always full. Cut.
- **Rack 60 s for 3 → 45 s for 3, then 5 from Camp 1:** v1's drying wall. Fire, crafts and fuel need about 9 dry wood
  over the opening, which is 2–3 batches, kept moving by the first order.
- **Crafts open at the edge, not the roast:** a tool to shape wood comes first; the roast now only answers hunger.
- **The end keyed to the second craft (either), not the fireback;** dusk keyed to the same condition as the end card.
- **The first leave-it-running at about 6:00, not 14:30:** a lunch-break player can leave early; the end card still
  closes the session at about 14:30.
- **Ring 6 → 5 stones; fireback +4 stones:** so scavenging stays worth a share after the ring.

## Open (content side)

- One failed line per card, true for every blocker, or one per first blocker (the engine already knows a card's first
  blocker)? Strike has four blockers, which is a lot for one line.
- The light on the ridge must agree with B3's arrival timing (day 2) and with her being alone.
