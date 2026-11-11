# Core loop (strawman)

A first concrete shape for the game, to tear apart. The rules it must obey are in `decisions.md`; this file is the
proposal that obeys them. Nothing here is story: skill and resource names are placeholders the setting will rename,
and every beat, region and joint project is referred to by kind, not by content.

## The whole game in one picture

```
            you (one mix at a time)                    the town (many mixes, in parallel)
  ┌──────────────────────────────────────┐    ┌──────────────────────────────────────────┐
  │ gather · craft · fight · study magic │    │ people staffed into buildings by orders  │
  │ personal skills, levels, prestige    │    │ volume: timber, stone, food, labor       │
  └───────────┬──────────────────────────┘    └───────────────┬──────────────────────────┘
              │  knowledge, spells, drops,                    │  boosts to your skills,
              │  what expeditions bring back                  │  gear, supplies, guards
              ▼                                               ▼
        ┌─────────────────────── joint projects ───────────────────────┐
        │ need both: the milestones that open land, systems and beats  │
        └──────────────────────────────┬───────────────────────────────┘
                                       ▼
                         the world map: a new region opens
```

## Skills

Start with a small core (about a dozen) and see what falls out; add a skill only when the game needs it. A small
core keeps the focus on feel, pacing and core mechanics, and leaves room for expansions.

| Kind | Yours | Town's |
|---|---|---|
| Gathering | Woodcutting, Mining, Foraging, Scavenging (the ruins) | Logging, Quarrying, Fields |
| Making | Cooking, Smithing, Crafting, Alchemy | Workshops (volume of the same) |
| Fighting | Melee, Ranged, Defence | Guards |
| Magic | Arcana (study), Spellcraft (casting) | none: only you |
| Moving | Wayfinding (expeditions, the map, scouting and tracking) | Trackers (rise into it) |

- **Town skills are building levels, not people's levels**, so a death never loses a level.
- **Only you** study magic and lead expeditions. Not because you're irreplaceable: you're just the most convenient
  person around, and you can't figure out the word "no".
- Every skill is paced to the shared target and gains a new method or place in its late levels.

## The mix, concretely

Your day is one saved mix. A strawman early one, built goal-first:

| Action | Share | Makes | Costs |
|---|---|---|---|
| Arcana: study | 40% | knowledge | candles, energy |
| Scavenging | 25% | candles, scrap | energy |
| Cooking | 15% | meals | forage |
| Foraging | 10% | forage | energy |
| Rest | 10% | energy | none |
| **Net / hour** | | knowledge +, scrap + | candles −4 (7 h left), others steady |

You pick "knowledge", the ledger shows candles and energy falling, you tap each falling line to add what supplies
it, and nudge shares until it does what you want: here it eats into the candle store, on purpose, for faster study.
The header says "runs 7 h". Save as "Study", press go. Saved mixes nest: a "Recover" mix can be a component of
"Study". Standing orders take over from there: "when knowledge for this tier is full, run Stockpile". Mixes and orders
are one system.

The town runs the same thing at scale: each building is an action, its share is its staff, its ledger is the town's
stores.

## The town

- **Growth is driven by food.** A surplus brings newcomers; a shortfall slows arrivals. Nobody starves.
- **Buildings rise in stages** and each stage boosts something of yours (a better smithy makes Smithing faster).
  Stages max out; a maxed building can later fall in a story beat and be rebuilt into its next, better form
  (its prestige). Falls come from the story only; failed defences damage a building and never destroy it.
- **The town grows in place; the regions get outposts.** The town clears the ground around it and pushes its walls
  out. In the regions, expeditions open sites for outposts (a mining camp past the pass, a logging post, a
  watchtower), each where its resource is. An outpost is a building far away and its upkeep a line in the town's
  ledger (food and tools out, ore back); under-supplied, it slows, never collapses, and orders run the supply.
  Lines can be improved (roads, carts, waystations, escorts) and are raided like the town, farther ones more often;
  a raid slows a line, never breaks it. Outposts grow their own people and stories.
- **Walls are built and guards are made, once there are enough people to protect.** Walls go up like any building;
  a guard is a sturdy newcomer who needs a purpose, handed the helmet, shield and spear you smithed. Threats come at any hour, at random, and
  resolve on their own: no response window, so being active could never have prevented one. Chance picks when and
  what kind; preparation against the region's scheduled threat strength decides how it goes. Each region has its own roster
  (wolves early, liches deeper in), ramping with time there, never with your defences; a breach costs light-tier lives and some stores, never a building or a notable, never a spiral.
- **People** are mostly light (a name, a trait, a line now and then); a few become notable through what happens.
  The code for their souls, chatter and memories comes over from habits, the owner's earlier app.

## Joint projects

The milestones. Each needs town volume plus something only you can make (the wizard's tower: stone, labor, the
scribes' books, your knowledge of magic). Each one either opens a region, adds a system, or advances the story,
usually two of the three. Projects are visible ahead, so planning toward one is the main thing an optimizer does.

## Combat and expeditions

- **Fighting is an action in your mix**, like any other: "clear the pass" fills at a rate set by your power against
  the threat. A lost fight wastes the attempt (supplies, time, an early return with little), injuries slow you
  until they heal, light-tier companions can die, and orders choose retreat or push through. Nothing banked is ever
  at stake. Your death may be a mechanic but never a punishment (see decisions.md).
- **An expedition is a longer mix away from town, and its kind decides who goes:** solo (only you can do it, or
  it's small), with backup (notables or guards when it's dangerous, so who you bring matters), or wide (an area too
  large for one person even with magic: you lead, the town sends people out). It reveals map, finds drops, opens outpost sites,
  land, turns up clues. It runs while you're at work and ends in the unwrap.
- **You are not the strongest mage around;** others in town may be better.
- **Spells are built, not bought.** Arcana teaches rules (an element, a shape, a target); Spellcraft combines them.
  Cascades (chain lightning jumping target to target) come from a good combination, deterministic from the build.

## Magic outside combat

Spells also work on the economy: a growth spell on the fields, a binding on the walls, a light that lets the scribes
work at night. This is where magic is the multiplier layer and where most cascades live.

## The arc

- **Regions are the acts.** A strawman of five regions over about 12 weeks, roughly two and a half each. Each brings
  new land, new resources, new methods for existing skills (not new bolted-on skills), at least one joint project and
  a run of story beats.
- **Cadence target for the simulation:** something new every day or two, a bigger beat about weekly, and the same
  rate in region five as in region one.
- **Prestige** opens per skill once a skill reaches its point on the shared target, mid region two or three.
  Buildings prestige by falling and being rebuilt (above).

## Visits

| Visit | What happens |
|---|---|
| Peek, 1–3 min | The unwrap (you, the town, any beat), a buy or two, tap through what the hours produced |
| Set-up, 5–10 min | Adjust or swap a mix, reorder orders, pick the next building, send an expedition |
| Long, weekends | A region's big beat, a prestige, rethinking the town's orders |

## The first day

1. You wake alone with nothing. One action: Scavenging. The bar fills, with juice (the feedback that makes a fill
   feel good).
2. You work out a second thing to do (Rest), and with it the mix: two bars at once, a ledger, tapping a line to set what it should do.
3. You make the rest yourself, slowly and painstakingly: a fire, a shelter, something to eat. Just you, surviving.
4. You figure out standing orders with the first thing you'd otherwise have to babysit.

There is no town at the start. The first person to arrive, drawn by your fire and food to spare around the end of the
first day or the second, is the first big beat: the town is founded from your camp, from nothing. Each system arrives
alone with a small first use; nothing else is shown until it matters.

## What the simulation checks

- **The 2 AM test:** a babysitter versus a whenever-player over the same weeks; any gap is a bug.
- **The band:** the typical route reaches the ending in about 12 weeks and sharp in about 10; routes that write no
  rules are reported, never held.
- **The back half:** new things per week, region by region, stays flat.
- **Skills:** time to max per skill lands near the shared target.

## Open for the owner


Art direction is decided: a drawn living town over bars (`decisions.md`).
