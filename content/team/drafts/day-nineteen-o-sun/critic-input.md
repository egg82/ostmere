# Critic input

You score three writers' drafts blind. Below: the writers' brief, the rubric, then drafts A, B and C (writers in a shuffled order). Also answer for each item: true in every listed state? (Y/N, why).

=== BRIEF ===
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

=== RUBRIC ===
# Critic rubric

You score another writer's draft blind. Score each item (a line, a fact, a set piece) on every row below, 0–2,
with a one-line reason. Quote the words you mean. Do not rewrite anything.

| Row | 0 | 1 | 2 |
|---|---|---|---|
| **Turn** (curated items only; plain event-log records skip this row) | stated outright or absent | implied but the last step is easy | the reader completes it |
| **On the nose** | says the feeling or the moral | one word too many | leaves it hanging |
| **Repeats** | reuses a shape or phrase already in the bible or in this draft | a near echo | fresh |
| **Canon** | contradicts a canon id (name it) | strains one (name it) | consistent |
| **Rules** | breaks decisions.md (Never list, tone, tropes rule, spoiler rule) | bends one (name it) | clean |
| **Overwrought** | ornate, stacked images, arch phrasing | one flourish too many | plain and exact |
| **Pictured** (narration, asks, talk; the journal skips this row) | a reader can't tell what thing or place it means without rereading | one referent left vague (name it) | the moment is seen on first read |

Then answer yes or no for each item, quoting the span that decides it:
- **Changed?** Does the situation end different from how it started?
- **Free win?** Is a clean success missing its cost?
- **Brighter than planned?** Is the ending tidier or brighter than the beat's declared `turn`?
- **Turn stated?** Is the turn stated rather than left to the reader?

Notes:
- Most tropes should resolve as promised; flag an item that turns a trope outside the four listed in world.md.
- Facts passed as finished phrases, and key names leaking into prose, count as Repeats.
- Close with the draft's three weakest items by id and the one strongest, each with a reason.

=== DRAFT A ===
l_last_sun = "lucy ignores the pale sun. she turns to you."
l_last_sun_alt = "nobody mentions the sun. lucy looks to you."
l_last_sun_light = "an open door shines down the valley. no one looks."
l_last_sun_cellar = "meat fills the cellar. no one says why."
=== DRAFT B ===
l_last_sun = "few days of pale sun remain. lucy turns to you."
l_last_sun_alt = "the pale disc weakens. lucy looks your way."
l_last_sun_light = "a hall door lamp shines into the deep valley."
l_last_sun_cellar = "smoked meat hangs in rows from cellar beams."
=== DRAFT C ===
l_last_sun = "lucy asks how to spend the pale disc."
l_last_sun_alt = "lucy leaves the cost of the pale sun to you."
l_last_sun_light = "the open door burns oil to light the valley."
l_last_sun_cellar = "sun trades for meat. rows hang in the cellar."