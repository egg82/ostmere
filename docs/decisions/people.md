# People and the town

Who arrives and why, the town, its souls and its deaths.

## Nothing appears; everything is made

Slowly and painstakingly at first, faster as you get better: the early slowness is the "just a guy" feel, the later
speed the power fantasy. People are the one exception, they arrive, but always for a reason you made: you built a
campfire, someone needed to warm themselves, saw you had food to spare, and stayed. What you build decides who comes
(a tavern stops travellers, a forge draws a smith), and what they become (guard, scribe, smith) is made by you
equipping and housing them.

**The town climbs Maslow's hierarchy** (in a brutal world people get their safety needs met before anything
else). Who arrives follows which needs the town meets: survival (warmth, food) draws the desperate; safety (walls,
guards, shelter) draws families; belonging (a hall, shared meals) draws people seeking community; esteem (workshops,
trades) draws the skilled; self-actualization (learning, art, magic) is when a scholar finally has a reason to come.
Each tier met is a milestone, and growth reads as a civilisation recovering, not a list of buildings. **People also
rise into roles:** a scholar can be made like a guard, from someone who came for food and shelter but is sharp and
passionate, once the town has climbed high enough to let them. The hierarchy governs who arrives and who rises, and
rising is a natural path from the light tier to notable. Even unlocks are worked out, never handed over.

## The town

A pillar, not a side system: the town builder is the genre this game leans on most. **It starts from nothing:** you begin
alone, and the town is founded from your camp when the first person arrives (the first big beat, around the end of
day one or day two), because building it from the ground up is the bigger payoff. Banished got basically everything
right, except that it is far too hard. So: **gritty in tone and stakes, never spiral-shaped in mechanics.** The world
is harsh and the story dark, but nothing compounds into collapse and nothing is lost while you're away; pressure
shapes what you build next, it never punishes not watching. Frostpunk, likewise "perfect" and lost to spirals.
"Nothing lost while you're away" means nothing lost *because* you were away: a story moment may
take a little of what is stored when it plays the same whether the player watched or not. A small optional step may be
on offer for a stretch and then go, when nothing depends on it.

**You lead with a vision; the people carry it.** Frostpunk's twist landed: you set direction and hope the people
follow. Here standing orders are that vision at town scale, and the people's response shapes who comes, what they
say and which mini-stories happen. Unlike Frostpunk, a decree can be revised, and the response colours the story
without driving a meter toward collapse.

**The people have souls,** as habits' villagers do: Claude-written personality, memories and chatter, reacting
in their own voices to what happened. They are a main source of mini-stories, unseen until they happen. habits'
rules carry over: rates decided in code, never by a frequency word in a prompt; output validated; everything works
with Claude off.

**People have social lives, and those make quests.** They fight over food, dislike each other, make friends, and a
clique can harden into a gang. Quests come from two places: authored (a faction event tied to a beat, in `content/`)
and emergent (Claude reads days of the town's real history and, once a pattern has truly formed, offers it as a quest:
"break up the mafia before it becomes the mafia"), so each save's version differs. Code decides when an emergent quest
may be offered, Claude only what it says; declining or ignoring one changes the story (the gang grows, people talk)
and has a real, bounded cost, as an undone chore does: the light tier, a store, a slower arrival, never a spiral; with Claude off, authored versions stand in.

**Death is expected, and fairly frequent** (unlike habits): it makes impact land and lets people rotate through.
- A death is a story event, never a penalty: the role refills as someone new arrives, so nothing compounds.
- Nobody dies because you weren't watching. Deaths come from the world and the story, never from inattention.
- **Groups arrive broken:** families, or parts of families, often missing a few or about to be. Preparation and
  healing can avert a few, on the light tier only; the rest are decided when they walk in, so they are never the
  player's fault, and they are strangers not yet loved. Healing matters elsewhere; it is not a promise the world keeps.
  Almost every group arrives broken. The rare intact few are of two kinds, those who know the horrors and were spared,
  and those who have no idea; the dynamics they bring to a town of the bereaved are mini-story ground (specifics in
  `content/`).
- Attachment is tiered: most townsfolk are light (a name, a trait, a line now and then) and carry the deaths; a few
  become notable through what happens to them, stay, and somehow avoid dying, if narrowly.
- **Off-limits: heavy investment in anything that can be taken** (the line for everyone who plays). Your
  character, the town, the notables and the story are safe; losses land only on the light tier. Notables never die.
- **Your own death may be a mechanic, never a punishment** (many games use death as progression, and it
  might tie into the story, as Grim Dawn balanced it). Guardrails: it costs no progress, levels or stores (Grim Dawn's
  return-to-the-last-safe-spot is the ceiling); it never comes from absence, only from a fight you chose or a story
  beat; and if it gives progression, that comes from the story, once, never from each death, or dying on purpose
  becomes the optimal route. Whether and how it happens, and what it means, is in `content/`. Nobody in town finding it
  remarkable keeps it "just a guy".

**Take habits' living world whole**, its spatial layer as well as its social one. The long bored
wait and replay variety tipped it: souls, memories, chatter, events, chronicle and storyteller, and also the day
planner, routines, visitors, scenes and pathing, so the town builds itself around daily lives and every save grows
differently. It is taken as modules once habits' cleanup lands, never as a copy of the tangle.

**Manage a whole town, expand its land, upgrade its places, never fiddly.**
- Every choice only adds: no build depends on current goals, nothing needs tearing down and re-placing. (Melvor's
  Township was fiddly because the best layout changed with what you wanted to do.)
- Upgrades feed the skill web (Idle Fantasy's buildings: a better forge makes smithing better), never replace it
  (Melvor's resource boxes made 5–7 skills pointless).
- **The town grows in place; the regions get outposts** (one town spreading over regions was the
  rejected alternative). The town clears its surroundings and pushes its walls out; expeditions open outpost sites in the regions
  (a mining camp past the pass, a logging post, a watchtower). An outpost is a building far away, its upkeep a line
  in the town's ledger (food and tools out, ore back): no new system. Under-supplied, it slows, never collapses;
  standing orders run the supply. Each new site is a story beat.
- **Supply lines are things to improve and to defend.** Roads, carts, waystations and escorts make a line faster and
  safer. Attacks and disruptions are the threat system extended outward (random timing, preparation decides), and
  farther outposts are more exposed; a raided line slows its outpost and loses some cargo, never collapses, and orders
  reroute or wait it out without the player. Outposts grow their own character and people, small stages for
  mini-stories (WoW's outposts carried much of its worldbuilding).
- You choose what to build; the town decides where, on a map generated per save that fills in as it grows.

## People, as built

How people stand today, moved from their row in `systems.md`. Arrival policy is the A/B target. Notables never die. A
person's name is content beside their lane (`name_key`), which the page fills into any text's `{<lane>}` slot
(`app/ashfall_app/opening/name_checks.py`; CONTRACT.txt, "Text and numbers"); one name per person in every save for
now, the per-save draw from a pool still planned.

**A person who matters is written into the story when they join or leave; the rest are a daily mention.** A journal
of daily life writes up the first stranger at the fire, and stops writing up each of the five who came today; at most
it mentions them (owner, 2026-11-13). Which a person gets is authored on their lane (`told`, `line` or `mention`,
required of every ruled lane), never a count threshold: a late arrival can matter and an early one may not. A `line`
person is told by the story lines of the outcome that joins or leaves them, kind story so they reach the strip and the
chronicle's Story; the loader refuses one whose joining or leaving writes no story line of its own, a counted join
aside, since that person came earlier and was told then (`app/ashfall_app/opening/people_checks.py`). A `mention`
person writes no line of their own: the loader gives each outcome that moves one a mention line with no text, so it
lands in the save's log at the second it happened, and the page words each game day's mentions of a way as one line,
from the `[people]` bands for how many came or went, drawn by a shuffle bag keyed by the save, the way and the band
(`app/ashfall_app/opening/people.py`, `app/client/src/game/people.ts`; CONTRACT.txt, "PEOPLE"). The bands are words,
never a count, after A Dark Room, whose arrivals read as a stranger, a family, a group or a convoy by their size. The
mention is decided in code and written by authored lines: no frequency word anywhere. Every person in the shipped
chapters is `line`, since each joining so far is a beat with lines of its own. Rejected: a per-person line for everyone, which
buries the people who matter under a roll call once groups arrive; a count threshold (the first N get lines), which
the owner ruled out; and wording the mention on the page from the view's joined unlocks, which carry no time, so a
return spanning days would collapse into one line at the wrong second.
