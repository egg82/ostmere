# Combat

Fights, threats and what a loss costs.

## Combat is a large pillar

In a world gone to hell you are fighting somebody or something constantly. Combat opens areas (the ore is past whatever
guards the pass), supplies drops for crafting and goods to trade, and supplies food. Once there are enough people to
protect, the town needs walls, built like any building, and guards, made by handing a sturdy newcomer who needs a
purpose the helmet, shield and spear you smithed (where tower defense would live). Threats come 24/7 at random and
resolve on their own, with no response window, so being more active could never have prevented one ("things happen").
Chance picks when and what kind; preparation against the region's scheduled threat strength decides how it goes, so over
a week a prepared town fares the same whatever the timing. **Threats ramp by region and time, never by your defences**
(or by town size): each region has its own roster (hungry wolves early, liches deeper in), strength rises with the
region's schedule and time spent there, and a rare, bounded out-of-place threat (rate set in code) makes a story moment.
Scaling to defences would make better walls feel useless and reward under-building. It is decided by preparation (gear,
spells, who you bring), never reflexes.

**Combat has fangs: a fight can cost what you put into it, never what you've banked** (without them combat
goes dull). A lost fight wastes the attempt (supplies, potions, time; the expedition comes home early with little);
injuries slow you for a while and heal; light-tier companions can die when it goes badly, so who you bring matters;
standing orders choose retreat or push through, braver orders winning and losing more; your own death tops the scale
under its guardrails. Danger is readable before you commit, and preparation is how you avoid paying.

**Chance shows, preparation decides**. Fights run while you're away, so a dice roll you never
watch reads as an arbitrary penalty, not tension. Losses come at exactly the rate your preparation earns, drawn from a
shuffle bag: earn a 1-in-5 loss rate and exactly one fight in five is lost, chance picking only which. The log reads
as real wins and losses; the totals are exact, and a fight's odds are that rate.

**Food drives growth, not survival.** A surplus brings people and growth; a shortfall slows growth and newcomers stop
coming. Nobody starves because you were at work; thin rations are flavour, never a spiral.

## Combat and expeditions, as built

How these parts stand today, moved from their rows in `systems.md`.

Combat: planned in `docs/design/combat-plan.md`; interface in engine `DESIGN.txt`, "FIGHTS", and
`app/ashfall_app/api/CONTRACT.txt`, "FIGHTS". A fight (side, threat, what a loss costs) sits on a card the player runs
or a standing action that runs alone; odds are Modifiers entries from the two strengths, losses are flows, and the
region's ramp is triggers on a clock store. No Save field, event kind or verb: a fight is never an event, and the
engine keeps exact counts of fights and losses in tally stores. Only the schedule is a policy worth A/B; preparation
decides, chance shows (which fight the log calls lost is the Chronicle's).

Expeditions: planned in `docs/design/banked-time-plan.md`; interface in engine `DESIGN.txt`, "BANKED TIME". The first
slice: a trip is an uncapped card with inputs, run in the mix on its supply store; finds are triggers on its completion
count; a fighting trip carries a FightDef on the hands' side. No roster, destination state or runner of its own: those
were a second copy of Cards. Backup (members' strengths on the trip's side), stance and wide expeditions are that
part's KNOWN GAPS.
