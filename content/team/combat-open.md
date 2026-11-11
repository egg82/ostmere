# Combat, first slice: open content questions

Engineering's side is `docs/design/combat-plan.md` and engine `DESIGN.txt`, "FIGHTS". These are the story and numbers
calls the slice needs before its content file (plan item 8) can be written. Each names its recommendation; the lead
decides, and anything that needs the owner goes to him spoiler-free in the words given.

**C1. Which chapter carries B7.** B5 and B6 wait on day three's steps, and B7 needs three arrivals by about day 6
(day-two.md, Open 7). Recommendation: B7 and the combat parts are their own chapter file, merged after whichever chapter
brings the third arrival, so combat can ship and be simulated before days four and five are written.

**C2. B7 itself.** spine.md has a plain fight that goes fine while the pack strips the drying racks. Recommendation: the
fight is a story card with lines and no odds (a beat never rolls); the strip is the visitor's idiom from day one (a
standing drain on the rack's stores with a clock store, B7 landing when the clock empties). How much it takes: enough
to feel (the rack's whole hang), never stores outside the rack. Spoiler-free for the owner if the reading of "nothing lost
while you're away" needs him again: day-one.md, Open 7, already asked the same question.

**C3. What the player can fight in week 1.** Recommendation: one fight card, hunting the lone hungry wolves of R1's
first roster, yielding pelts and meat; costs the time and a little food carried. Ash-deer stay a plain hunt (no odds:
they don't fight back), if they appear at all in week 1.

**C4. What comes to the town on its own after B7.** regions.md's days 1–7 roster: ashrats in the stores, crows at the
drying racks, lone wolves. Recommendation: ashrats and crows as two standing fights against the camp's side, each
taking a little of one store per lost fight (rats: roots; crows: what hangs on the rack); lone wolves as the hunt
(C3), not a raid, until there is someone at the edge of the light to wound. Each needs its cure in reach the moment it
shows (a covered rack, a stone-floored larder or traps raising the camp's strength).

**C5. What a lost hunt costs the player.** Recommendation: the attempt (time, the food carried) and one unit of a
"hurt" store, which shows a chip (hands slower, and weaker in the next fight) and heals by itself over a few hours,
faster with a cure card (a poultice from what Foraging gives). Never a death in week 1; companions do not exist yet.

**C6. Preparation in week 1.** Recommendation: one piece of gear (a spear, from scrap and deadwood), and Melee opening
at B7 with its level pays raising the hands' side. Defence opens later with walls and guards (B11). Whether the camp's
side has a base above zero at B7 (so pests are lost to, but not always) is a numbers call for the simulator.

**C7. The ramp.** R1's roster changes at days 8 and 15 in the Hollow. Recommendation: the clock starts at B7, not day
1, so the first week's threats begin weak at the moment combat is taught, and the 8–14 roster arrives about a week
after. The ramp steps (how much each threat rises, when) are the simulator's to set against the landing band.

**C8. How the log tells a fight.** Recommendation: plain, one short line per fight, won or lost, never gory; the
arrival queue folds a long absence into one count line. The line pools for won and lost hunts and for each pest are
the writers' brief, written from the simulator's line-state lists like day two's.

**C9. Art.** A wolf (the pack and a lone one), an ashrat, crows at the rack, a spear in hand, the rack stripped and
re-hung. Picked from the packs first (`sprite-catalog`).

## Answers (lead, day three's design, 2026-10-27)

The B5-B7 arc these sit in is `day-three.md`, "B5 to B7". Landing bands are `day-three-numbers.md`'s (B7 at
`target_day × pace_scale` days, not day 6 of real time).

- **C1: agreed.** B7 and the combat parts are their own chapter file (`b7.toml`), merged after the B6-B7 chapter's
  file, which brings arrival 3. Combat ships and simulates before anything past week 1 is written.
- **C2: agreed, with one gate change.** The fight is a story card with lines and no odds; the strip is the visitor's
  idiom (a standing drain on the rack lane's stores, a clock store, B7 landing when it empties) and takes the rack's
  hang only: what is on the drying wall and the smoking rack (catch, smoked, and wood in drying), never another store.
  "Wolves at the edge of the firelight" is a night, so **B7's gate gains a step**: A29, "bank the fire", on night 6
  (requires the night's clock started), beside arrivals 3 and B6. Without it the beat fires the instant arrival 3 joins,
  often at midday. Canon change, recorded as D-101.
- **C3: agreed.** One fight card, `hunt_wolf`, the lone hungry wolves; takes time and smoked meat carried; makes pelts
  and catch. No ash-deer in week 1: one new card.
- **C4: agreed, and the cures already stand.** Ashrats (roots) and crows (the rack's hang) as two standing fights on the
  camp's side from B7. Their cures are day three's comforts: `larder_floor` (stone floor) and `rack_roof`, each an
  entry raising the camp's side against its pest, added by combat's content. Most routes have built both by B7, so
  the pests start losing often and preparation shows at once; a route that hasn't still has them in reach. Lone wolves
  stay the hunt, not a raid.
- **C5: agreed; the poultice is clay and roots.** A lost hunt costs the attempt and one `hurt`; the chip shows hands
  slower and the next fight weaker; heals by itself in a few hours, faster with `poultice` (clay from `dig_clay`,
  roots), so day three's clay gets a second use. No deaths in week 1.
- **C6: agreed, the spear arrives with B7.** `make_spear` (scrap 6, dry wood 4) opens with the combat feature, not
  before (a system arrives with the problem it cures). The track's scrap is banked all week (BT2), so a held trip makes
  it affordable at once. Melee opens at B7; its level pays raise the hands' side. The camp side's base is the
  simulator's.
- **C7: agreed.** The ramp's clock starts at B7.
- **C8: agreed.** One plain line per fight; a long absence folds into one count line. Pools from the B7 chapter's
  line-state lists.
- **C9: agreed, plus** the scene states day three's cures add (the stone floor, the roofed rack), which the pests' art
  must read against: crows on the roof's ridge, not in the hang, once it is built.
