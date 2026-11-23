# Day nineteen's last stretch: the writers' brief (one ask)

Spoilers: never shown to the owner. You write three lines for one moment in an idle survival game's story. This file
is all you may see; read nothing else. Facts are given as attributes, not phrases: never lift a fact's wording.

## How the lines get written

Three blind proposers, one lens each; a critic scores the drafts blind on a rubric plus *true in every listed state?*;
the lead picks line by line; code checks length, the must-nots and three-word echoes against every shipped line; a
fresh reader's voice pass reads the picks in player order and writes the labels (not yours).

## Rules for every line

- **Voice:** the shipped lines'. Second person, present tense, lowercase (names too: "lucy"), plain. One or two short
  sentences. A turn the reader completes, never stated; no feeling named, no moral. Dry about the player's own choices
  only.
- **Length:** median 45 characters or fewer; no line over 75.
- **True in every state.** This plays on return: never say when, in real time, anything happened, or how long it took;
  never say what time of day it is.
- **People:** lucy by name (she runs the town; never grateful, never sweet, never says much); `{n12}` is the sister of
  a man who went over the ridge and did not come back; light-tier people are ordinary. What each does, in active
  voice.
- **Must-nots:**
  - no "magic", "spell", "faith", "the burn", "winter", or any season's name; the weather is described, never named;
    the sun is "the sun" or "a pale disc", never hope;
  - never "again", or any hint of having been here before;
  - nothing in any line may suggest the man who went over the ridge could be found, brought back or saved, or that a
    light or a store is for him; nobody says he is dead; do not mention him;
  - never that anyone arrives, or that a light brings anyone: what the light does is the game's numbers, not the line;
  - no line judges either answer, or says which was wiser, or what it cost;
  - no proper noun but lucy and the name slot.

## Voice exemplars (shipped; reuse no phrase from them)

- "lucy says a road runs under the ash past the ridge. she looks at you."
- "three women sing for their supper at the hall door. each verse, they wait out a bar."
- "{n8}, {n9} and {n10}. they followed the hall's light down the valley."
- "by morning the three are out among the beds."
- "by morning the three are shovelling ash off the road."
- "bear fat melts in the stew pot. you split stakes into troughs to pour it in."
- "lamps stand lit on the gate posts."
- "at dusk {n12} carries a lamp out to the end of the road."
- "she sits by it facing the far side, and is still there when the light goes."
- "you are looking for a flat stone before she has finished."
- "lucy nods and goes to find someone."

## Where this sits

The season of a pale sun is ending: frost on everything past the warm ground, a long hall with one table where the
town eats, a cellar dug earlier in the year, a road just laid over the ridge. The day before, a man went ahead over
the ridge alone and did not come back; his sister now sits at the road's end with a lamp at dusk. The town has a few
days of sun left, and lucy puts a question to the player: what the town does with them. Two answers, each kept for
good: **keep a light burning in the hall's door all night** (the hall's light once brought three women down the
valley), or **fill the cellar** (meat smoked and hung for the dark days to come).

## The lines

**l_last_sun** (H: write it and one alternate). The line that puts the question up. Facts: lucy; the sun lower and
paler each day; a few days of it left; she turns to the player with it. States: the player comes back to it (on
return), any hour, the day after the man was lost and after the sister first sat out with her lamp. Special: the line
prefers neither answer and names neither; the question itself is the page's, not the line's.

**l_last_sun_light** (the light answer). Facts: from then on a lamp burns in the hall's open door through every night;
it can be seen from far down the valley. States: right after the player answers, any hour. Special: nobody comes in
the line; it must not echo the sister's lamp at the road's end or set the two side by side.

**l_last_sun_cellar** (the cellar answer). Facts: the sun's last days go to smoking meat on racks and carrying it down
into the cellar; it hangs in rows from the beams down there. States: right after the player answers, any hour.
Special: never says it will be enough, or for how long.

## Output

Return exactly this, nothing else, one line per key, the text in double quotes:

l_last_sun = "..."
l_last_sun_alt = "..."
l_last_sun_light = "..."
l_last_sun_cellar = "..."
