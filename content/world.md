# World bible

Spoilers: this whole folder. Never shown to the owner (`CLAUDE.md`). Design notes, not fiction. Every later file
(`regions.md`, `spine.md`, `cast.md`, `creatures.md`, `mysteries.md`) follows from the facts here; when one disagrees
with this file, this file wins until it is changed on purpose.

## The one-paragraph version

A guild-empire of mages, **the Chequer**, ran for centuries on magic drawn cheaply from something vast under the
land. When the draw failed and a long cold set in, they **set it alight** (the Essart, deliberate) and held the
burning in check with a ring of anchors called **keels**, each held by one living person, a **holder**, paid for in
the holder's memory. Thirty good years. Then one holder **said no**, their keel failed, and because keels were linked,
the failure jumped keel to keel (the Breaking, an accident). The burn has run unheld for forty years; its waste is the
ash that never stops falling. A few keels held. The player is the holder of one of them: not its mage, not its
designer, its *battery*, who was there, had no one, and put their own name forward. Every few years the keel strains,
spends the holder's memory to hold on, and the holder wakes with nothing in the ruins of the town they built last
time. That is "again". The game is the cycle the player finally breaks: not by fixing the world, but by remaking the
keel so that the town's remembrance of its dead pays its upkeep. The town keeps its dead's names and loses their
faces.

## Names

| Thing | Name | Notes |
|---|---|---|
| The land (world map) | **Ostmere** | Chequer name; folk just say "the land" or "here". |
| The empire | **the Chequer** | A guild-state of mages and clerks. Language bureaucratic to the end. |
| The thing under the land | Chequer: **the Deep Account**. Folk: **Old Warmth**, **the Sloom** | Never named as more than warmth or an account by anyone with authority. See "The thing under the land, implied". |
| The deliberate burning | **the Essart** | ~70 years before day 1. A Chequer word: forest ground grubbed up and burned for tillage, its rents on the Chequer's books. Never glossed in player text. |
| The cascade failure | **the Breaking** | ~40 years before day 1. Folk date things "before / after the Breaking". |
| Anchors of the great working | **keels** | Chequer engineering term; the keels were linked, so they shared load. Folk who've seen one call it "a hearthstone". |
| A holder's wrist mark | **the seal** | A Chequer clerk's seal naming the keel, legible once the script is (B33). Never a number. |
| The town's list of its dead, under E-d | **the roll** | Kept by N8. |
| A keel's living anchor | **holder** (Chequer); folk who return from death are **the kept** | Folk don't know the kept are holders. |
| Magic's law of exchange | **the Tally** | Chequer term; mages "keep tally". |
| Magic's waste | **tithe**, or just ash | Every exchange pays it. |
| The starting valley | **the Hollow** | |

**How names are made** (each name's verdict and source: `team/names.jsonl`; never take one from a model's head):
- **People** take a given name from late-16th-century English records (Talan Gwynek, "Late 16C English Given Names",
  https://heraldry.sca.org/names/eng16/eng16ffreq.html for women) and, when they need one, a family name from the
  Durham and Northumberland marriage registers, 1521-1615
  (https://www.s-gabriel.org/names/juetta/parish/surnames_top.html). Code draws them, weighted by the counts. Folk
  go by given name; the Chequer addresses its own by family name.
- **Places** are a specific plus a generic from Old English and Old Norse place-name elements (English Place-Name
  Society, https://epns.nottingham.ac.uk/): Caldrigg is *cald* "cold" + *hrycg* / *hryggr* "ridge", joined as in
  Askrigg.
- **Folk words** are northern English dialect words, spelled plainly (the Sloom, a howlet). The Chequer's words are
  accounting terms (the Tally, the Deep Account, and the Chequer itself: the counting table under checked cloth).

## Magic: the rules

Magic is a craft with five rules. The player relearns them in this order (beats in `spine.md`), and every story
problem magic solves is solved inside the rules the player has by then.

1. **Nothing is made, only moved.** A spell moves something that exists from one place to another: **heat, light,
   motion, quick** (growth, the stuff of living), **shape** (binding: making a thing keep a form), and at the deep end
   **sense** (memory, meaning). The fire you light by magic warms you because a stone somewhere went cold. Echoes the
   game's own law ("nothing appears; everything is made").
2. **Every move pays a tithe, as ash.** The tithe rises with the difference in kind (heat to heat is cheap, heat to
   light dearer, motion to quick very dear) and with distance. Mages' hands are grey to the wrist. A big working
   leaves a drift. **The ash in the sky is the tithe of a working still running.**
3. **Like calls like.** A working is cheaper along a link: the same material, a piece of the target, a name, a shared
   history. Wolf hair makes a wolf-ward cheap; one wolf in a pack links to the pack. This is the optimizer's rule:
   drops are reagents, and **cascades** come from it (a jump-shaped working runs along kin-links target to target,
   chain lightning being heat and motion jumped through a pack).
4. **A held working needs an anchor, and the anchor carries its weight.** A spell that must keep going (a ward, a
   lamp, a keel) is anchored. Stone holds small things (a ward on a door, fed by fuel). Only a living mind holds great
   ones, because only a mind carries enough weight. Let an anchor go and **the moved thing snaps back, with
   interest**: that is why breaking a ward hurts, why destroying a lich's anchor is how you kill it, and why one keel
   failing pulled the next.
5. **Sense is the heaviest coin.** A memory moves more than a forge-load of coal, for almost no ash. That is why the
   Chequer paid its great workings in memory, why holders forget, and why the Unpaid (liches) feed on it. It is the
   edge of the craft: mages know *that* it works and roughly *what* it buys. Where spent memory goes, nobody knows.

**Spell grammar (for Arcana and Spellcraft):** what is moved (heat, light, motion, quick, shape; sense only at the
end) + how it moves (a line, a spread, a jump, a hold) + the link (a reagent, a name, a place). Arcana teaches each
piece; Spellcraft combines them. A held working is a "hold" shape plus an anchor.

**Where magic stops.** Everything inside the world balances in the Tally. The thing under the land does not: what
goes in and what comes out never match, and nobody has found the rule. Exchanges with it are the unknowable edge, and
the journal's entries on it are never finished. Mages call this "an open account". It is the only place the game's
"perfect once known" fails on purpose.

**Wonder to craft.** At first the player sees fire from a cold hand and stones that hum. By the end they read a
keel like a ledger. Wonder moves outward each region to the next thing not understood, and stops at the burn.

## What broke, and how

**Intent:** the Essart, a budget decision. The draw from the Deep Account had been getting dearer for generations (it
was cooling; nobody asked why something under the ground should cool like a body). A long cold failed the Chequer's
warm-farmed crops, and the warm-farm account ran short. The Chequer covered the shortfall by "realising the
principal": it burned the source to release its warmth at once, held in check by a ring of keels so the burn gave
heat and light up through the land without running wild. It worked. Warm ground, green winters, a little ash ("the
tithe; acceptable"). Thirty years.

**The costing.** The keels' upkeep was priced line by line, in the Chequer's usual way. One line priced it from
*remembrance of the deceased* and was struck: *rejected, supply irregular*. Beside it, in the hand of the clerk who
did the sums (N6): *requires the leave of every household; not obtainable*. So the upkeep went to the holders' own
memory instead. The note is his premise, and it is wrong: leave can be given name by name, and does not need every
household. The costing survives in N6's daybook (B39).

**Accident:** the Breaking. The keels were linked (rule 3) so they shared load. One holder refused to go on and let
go. Their keel's held working snapped back (rule 4), and the load jumped along the links to the next keel, and the
next: a cascade, the world's worst chain lightning. Most keels failed within days. The burn ran unheld. The Chequer
fell inside one season. Nobody intended it; nobody at the Chequer had planned for a holder saying no, because every
holder had put their own name forward.

**Who is to blame** is left honestly mixed: the Chequer built a machine that ran on nobodies; one nobody finally
refused; the refusal was right and broke the world. Magic is a tool; people did what was done.

## The honest knock-on consequences

**Light.** The burn's tithe rises as a veil of ash that covers the sky. Days run from brown twilight to grey; only in
the Clear (seasons, below) does a pale sun show as a disc and cast real shadow. Nights are black, except that the
cracks in warm ground glow a dull red: **the Hollow glows faintly at night.** Fire, candles and lamp-oil are precious
(the strawman's candle line is a real need).

**Heat.** The veil alone would freeze the world: a sunless valley is a dead one. It isn't, because the burn heats
the ground from below along **seams** (cracks, warm rock, hot springs). **The thing that broke the world is the
thing keeping the survivors alive.** Away from seams it is cold and dead; life clusters on seam lines like life on
deep-sea vents. Putting the burn out would kill everything left. That is the turn that kills the obvious goal
(spine B32).

**Food and what still grows.**
- Green crops grow only on warm ground and only well in the Clear: hardy roots (ashroot, a turnip-kin), a bitter
  barley, beans. Weathered ash is fertile (as volcanic soil is), so a field fallen under ash three cycles ago is the
  best field you have: an honest reason Fields improve with time.
- **Fungus is the new base of the food web.** Forty years of dead forest and dead everything, buried under warm ash,
  is a feast: shelf fungus, ash-caps, the bracket growths of the Ashwood. They fruit in the Drift.
- Animals that survived eat fungus, roots, lichen on bone, and each other. Meat is scarce, fish are pale and blind in
  warm streams.
- **The Taking** (below) makes meat a risk: cooking and washing are the craft that makes it safe.

**Water.** Streams run grey. Warm springs on seams run clean. Filtering through sand and charcoal is a Crafting
method; cisterns fill in the Drift (rain carries ash).

**The Taking: you become what you eat.** Tithe-ash carries the leftover of exchange: it "wants" to finish moving
things. A creature that eats, over and over, things that lived in the ash slowly takes traits from what it ate. A
little in a lifetime; a lot over generations; very fast in things that ate the dead, because a human carries more
weight (sense) than any animal. This one rule drives most of the bestiary (`creatures.md`). Cooking through,
washing in running water, and fire "spend" the leftover, so cooked food is safe; this is why Cooking matters and why
folk say "never eat a thing that ate a man." People who ate wrong in the bad years have small changes nobody mentions.

**Why anything still works.** Seam heat; the Clear's light; fungus; fertile ash; Chequer leftovers (small wards on
old buildings still hold, anchored to keystones fed by seam warmth, rule 4: stone holds small things); and the surviving
keels, which keep their valleys from the worst. **The Hollow is one of the few places with a surviving keel. It is
alive because the player held on.**

## The seasons: the burn breathes

The world's year is gone (the sun no longer rules the weather). What rules it is the burn, which **breathes**: a
cycle of **21 real days**, three seasons of **7 days**. Day 1 falls on the first day of the Still. A typical run sees
each season four times. Nobody can explain why a fire breathes.

| Season | Days in cycle | What happens and why | How the game changes |
|---|---|---|---|
| **the Still** | 1–7 | The burn holds its breath. No wind; ash hangs; fog in the low ground; sound carries a long way. | Ambush predators, things that come up from the ground; scouting is slower and finds more; eerie lines weighted up; fog-fishing, mist-catching water. |
| **the Drift** | 8–14 | The exhale: warm wind from the burn, heavy ashfall, brown dark days, warm nights. | Ash must be cleared from roofs (an honest roof-collapse risk, the building-fall beats use it); fungus blooms (big foraging/cooking options); ash-harvest for alchemy; Drift-only creatures (moths, the bear's hunting season); fire-fed spells cheaper. |
| **the Clear** | 15–21 | The inhale: cold wind toward the burn, the veil thins, a pale sun, frost at night, stars. | Crops grow fast on warm ground; light lets scribes work; long sight lines for wayfinding; starlight hunters; light-moving spells cheaper; frost threatens exposed outposts. |

Once every 9 to 12 years the exhale is enormous, a **Black Drift**. It strains every keel. The last one was months
before day 1. Black Drifts are history and lore, never scheduled in play (no countdown).

## The player's real situation

What the player is told: you woke in a ruin, alone, with nothing, and remember nothing.

What is true:
- You were an ordinary person, bound as **holder of the Hollow keel** at the Essart, ~70 years ago. You volunteered.
  The Chequer registry's selection field reads, in effect, *present, no dependants*, and the tick beside "offered
  self" is in your own hand (B40). Not a mage. Not chosen by destiny. You were there, you had no one, and you said yes.
- The seal on your wrist is a Chequer clerk's seal naming the Hollow keel. It also shuts your links to the keel's
  draw (see "The ending, as world fact"), which is why a holder had to have no dependants.
- The keel holds its holder too: you **do not age**, and **you come back from death** at the keel (the warm stone at
  your first camp). Folk have seen returners since the Breaking and call them **the kept**; to them it's a known, odd
  thing, like a stammer. Nobody finds it remarkable, which keeps you just a guy.
- Your keel **held at the Breaking** because you didn't let go. That's the whole reason the Hollow lives. Nobody knows,
  including you.
- At each Black Drift the keel spends your memory to hold on. You forget everything. The town around you, which
  never knew why it lived, falls apart. You wake in its ruins. **This is the fourth time** (chronology below). The
  ruins you scavenge from day 1 are your own previous towns, in layers.
- The journal in your coat is your own. Its front pages were torn out by a previous you (found again in R5,
  spine B49). Notes already in its margins are in your hand from before, written by the yous of towns 2 to 4. They
  sometimes contradict each other, and they are not always right. The later pages were never blank: a few carry
  small pencil notes near the gutter, found as entries reach them.
- Your memories were **moved, not destroyed** (rule 1): they are spent into the keel's hold. Some of what you'd call
  luck in the Hollow is that.
- Not irreplaceable: any person could hold a keel. You are just the one who did, and who keeps saying yes.

### Chronology

| When (before day 1) | What |
|---|---|
| ~70 years | The Essart. You are bound to the Hollow keel. You were present, had no one, and put your own name forward. |
| 70–40 years | The thirty good years. The linked keels share the load, and no holder forgets. |
| ~40 years | The Breaking. Your keel holds. From now on each Black Drift (every 9–12 years) spends its holder whole. |
| 40–~30 years | **Town 1.** N9 is a child there; you teach her to set snares. The first forgetting ends it. |
| ~30–20 years | **Town 2.** This you tried to leave the valley, died on the road, and woke at the stone. Its notes say not to go past the ridge. |
| ~20–10 years | **Town 3.** This you worked out what you were and built a shared keel, about thirty people, none of them sealed. At the Black Drift the draw reached the first sharer and ran through the rest along everything they shared. Every one of them forgot everything at once, woke a stranger to the others, and scattered. B16's stranger is one of them. |
| ~10 years to months | **Town 4.** This you found town 3's design and names, went as far as the refuser's keel looking for another way, found none, and left the pages there sealed, where only a you with a town that could reach R5 would find them. Its notes disagree with town 3's. The last Black Drift, months before day 1, took this you; the small town left. The ruin you wake in is town 4's. |

This is one of the few places the story spends a turn (the list is in "Tropes" below): the amnesiac's answer is
neither "you caused it" nor "you were the hero". Learning the truth **lowers** your status, and the dry humor lives
in that. It is **not a loop and not predetermined**: the previous towns were real, their people lived and died, the
cycle is a mechanism with a cause, and this run breaks it. Nothing turns out not to have mattered.

## Tropes: where the turns are spent

Most tropes pay off as promised; that is what they're for. Only these turn:

| Trope | Turns how |
|---|---|
| The amnesiac's past | Neither villain nor hero: a volunteer nobody, present and without dependants, whose tick is in their own hand (B30, B40). |
| "Fix the catastrophe" | The catastrophe is what keeps the survivors warm; the player's own working freezes an outpost and costs a life (B32). |
| The running joke | The stool and the yes both turn into evidence: a stool in every layer, the tick on the form (B36, B40). |
| The gentle stranger | The one who always says no is the one whose no broke the world (B42–B43). |
| The ending | Sharing the weight among the living has already been tried, and failed (B49). The town's remembrance of its dead pays instead, and the town gives its leave name by name (B50–B52). |

Everything else resolves as expected, on purpose: the old mage is a real mentor and his secret is a confession, not a
betrayal; liches are liches and die by their anchor; the town pays for how it ends; the deep places are worse than
the near ones; the faithful are partly right; the first person who shows up stays.

## Content lines the story never crosses

From `decisions.md` "Never" (main): no sexual violence; no harm to children shown (a past or off-screen loss, rare
and sad, never for shock; for runtime lines the rate is a number in code, `young_loss_rate`, never a frequency word);
no "none of it mattered" twist; no karma meter deciding the ending; one run sees the real ending; no notable betrays
you (betrayal stays on the light tier). Animals: hunting and skinning are told plainly as a way of life; no cruelty
on screen; companion animals never die (they may be in danger and scrape through, like notables); wrong or made
creatures are monsters and fair game.

## The thing under the land, implied

Never stated anywhere in game text. Implied only by:
- the Deep Account *cooled* over centuries, like a body;
- the burn *breathes*;
- the folk faith's one taboo, *never thank the warmth*: it keeps accounts;
- **the even draw** (spine B47): at the turn of a breath, deep in R5, every lamp on the road dims at once and
  everyone on the expedition goes cold by the same amount. The journal records the same loss beside each name.

Nobody in the game ever names what it is, and no sound comes from below. A journal entry on it trails off.
Godsgrave guardrail: no reveal, no corpse-shaped land or map, no character who explains.

## The ending, as world fact

The fix that's possible (spine B50–B53, ending E-d): **remake the Hollow keel as the Hearth**, still anchored by
you, with its upkeep paid from the town's remembrance of its dead. It runs on these rules:

- **A draw on the living cascades.** A memory of a living person is a link to someone who holds memories of their
  own (rule 3: a shared history is a link). A working that draws sense from one living mind runs along those links,
  person to person, as chain lightning runs through a pack. A keel shared among the living is the Breaking in small:
  when the first sharer is drawn on, the draw jumps to everyone they share a life with, and each loses everything.
  More sharers make it worse. Town 3 found this out (B49).
- **The seal shuts a holder's links.** The Chequer seal on a holder's wrist closes that mind's links to a working's
  draw, so a draw on a sealed holder takes the holder and goes no further. That is why the registry picked holders
  present and without dependants, and why every Black Drift stopped at you while the people of towns 1 to 4 kept
  their own memories. Town 3's sharers carried no seals. N3 is sealed too. A charcoal copy of a seal works once
  (B25): a seal is a mechanism, not a badge.
- **A draw on a memory of the burned dead stops.** Fire spends what sense a body still carries (the Taking), so a
  link to someone burned has no far end. A draw addressed to them takes what every living mind remembers of them
  (face, voice, what they were like) and goes no further. An unburned body would let the draw through, so the dead
  are burned and, after B51, carried home from outposts to be burned.
- **The name is the address, and it stays only if it is written.** The draw finds its memory by the dead person's
  name, written (rule 3: a name is a link). What is written is not sense in a mind, so the draw leaves it. The Warm
  scratch their dead's names on the lip of a seam crack and say them into it; they keep the names and lose the rest.
- **The anchor is still you** (rule 4: only a mind holds a great working). What changes is what pays the keel's
  upkeep: the town's remembrance of its dead, entered by name in N8's roll, instead of your own memory.

Nothing of the dead is used: their bodies are burned as before, and the stone you return to is never involved. What
is spent is the living's own memory, given by name, with leave. Leave is given per name: a household brings the
names it gives, and a household that refuses keeps its dead's faces. **The cost:** within days of a name being
entered, nobody living can call up that person's face or voice or say what they were like; the roll keeps the
names. Every later death whose household gives leave is paid the same way. **The reserve:** the Hearth banks what is
paid between Black Drifts. The supply is deaths and leave, so it is irregular; if the reserve is short at a Black
Drift, the keel takes the balance from you, some of your memory and not all. Nobody can tell whether the next one is
covered.

The Hearth's hold also moves the falling ash out of the air over the valley; the ash comes down at the edge instead,
in a ring of grey dunes, **the Rim**: a visible border round the part of the world you saved. Beyond it, the world is
still falling apart (expansions), and the other keels still each have a holder forgetting at every Black Drift.

## The running motif: the stool

The first recipes on day 1 are a stool and a fireback, each a tradeoff shown when chosen; both get built, and the order is the player's. It wobbles: one leg short. No upgrade ever fixes it
("Stool (wobbly, oak)", "Stool (wobbly, iron-shod)"). Townsfolk try to fix it in chatter and fail. In the cellar in
week 2 there's another, short on the same leg (it reads as a joke). In week 8 the ruins turn out to hold one per
layer, all short on the same leg (it lands as the "again" turn). E-b's last image is the leg being cut short. Other
variants leave the stool where it stands. It is never explained in text: you always cut that leg short, and nobody, including you, knows why.

Rules: never named as a motif, never more than one stool line in a day's unwrap, never in a dark moment's own line.

## What the dry humor draws on

- **The yes.** Every job is an offer the player picked. Lines land after the player's yes ("You said yes. Of course you
  did."), and at B40 the registry's selection line turns the running joke into the twist, which the player completes.
  Never about something the player didn't choose.
- **Competence against status.** You kill the wolf in a second; you still carry the night-soil cart because you were
  standing nearest.
- **Chequer bureaucracy surviving the apocalypse.** Forms, stamps, "Holder (1), replaceable." Clerks still filing in a
  dead city. Euphemism as a world-ender ("the Deep Account", "an open account", "acceptable tithe").
- **The shrug.** Folk shrug at the kept, at miracles, at the stool.
- **Gallows humor of the bereaved**, never at a specific death's expense.
- **The journal's clinical understatement** meeting a wrong fact ("counted 9. counted 9 again. there are 8.").

## Faith

Folk faith, not a system: **Old Warmth**, or the Sloom. Prayers are said to warm ground; a hand laid flat on a seam
stone is a blessing. Its one taboo is *never thank the warmth*: it keeps accounts, and thanks would be a debt. The
dead are sat up with by the fire for one night and burned at first light, and at every burning the names of the dead
are said aloud. It is neither true nor false: it's closer to the truth than it knows, and wrong about what that
means. Its keeper is a notable, N4 (`cast.md`). Never a currency, building bonus or mechanic.

## Tone samples

Event log (plain record): *Drift, day 3. Cleared the hall roof twice. Six sacks of meal spoiled by the damp.*

After a yes: *Lucy asked who'd go up the ridge for the cart. You said you would. She waited, in case you'd take it
back.*

Journal margin: *wolves at the edge again. didn't come in. sat facing the fire like they were waiting to be asked.*

Goosebumps, by the fire: *"My gran said it used to be warm on purpose."*

Item lore: *Chequer ledger, water-stained. Every line is a name and a number. The numbers go down.*
