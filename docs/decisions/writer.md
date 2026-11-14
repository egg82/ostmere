# Writer

What is written for the game, by whom, and on what budget.

## Public, eventually: every save its own, on one budget

The finished game opens to the public internet if possible, so nothing a stranger can do may run up
the Claude bill, and nobody manages anyone's access, which would be a terrible job. Yet every save should
grow differently, souls and emergent quests included, which react to that town's own history. Four layers, cheapest
first. Each kind of call's model is set by model-golfing it (the blind model test in issue #29); the estimate until
then is Sonnet for short lines that need little thought about the world, Opus for a kind that must reason over it (an
emergent quest read from days of history):
1. **Combination, free per player.** Most of what makes a save unique is code combining pooled pieces by the save's
   seed (a soul from pooled traits, backstory, manner of speech, grudges). A daily batch job adds new pieces to one
   shared pool; what a save draws is copied into it and frozen for good, and undrawn pieces retire after about a day,
   so saves differ by seed and by when they were played. The roll is code, never the model (a fresh call cannot keep a
   rate).
2. **The opening is authored**, so a player who stops after a day costs next to nothing.
3. **Claude writes for one world only when its player will see it**: a soul's reaction to last night, an emergent
   quest, written when the player comes back, in a background batch call with the setting and voice cached, from the
   world's history kept by code as structured facts. An abandoned world never triggers a call.
4. **One global daily budget, split across the worlds played that day**, each world's share growing with the days
   its player has come back, up to a cap. When the day's budget is spent, layer 1 and the authored stand-ins carry
   on: nothing breaks, nobody sees an error, and more players means smaller shares, never a bigger bill.
Strangers get anonymous accounts like everyone (above); open: the abuse limits that come with that (account creation
and request rates); decide before the public launch, not now.

## Content is a pipeline

Idle Fantasy's other gap is volume ("still very early and very basic"). Content is produced deliberately on three
lines: authored story for the spine, Claude-written souls and mini-stories for volume, per-save generation (the map)
for variety.

**A line is written for every moment it can appear, not the script's one** (after "the fireback can wait" fired
after the fireback was built, and "one flint" fired with none). Lines are written after the pacing is set. Each line
gets the list of states it can fire in, generated from the content's gates and from simulated players taking every
order of a choice and tapping early (not only the scripted path); the writer and the voice pass both see it, and a
line ships only if it is true in all of them. The easter-egg lines for early taps come last, from the full map of
what can be tried when.
