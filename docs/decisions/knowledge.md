# Knowledge

What the player is shown and knows: numbers built in, the registers, taps, the journal.

## What the mods added is built in

Melvor's popular QoL mods (a combat simulator, "likely to die" warnings, time-to-level, rates per hour) made it
better, and Idle Fantasy's copy of them was poor; if a game's best mods are information, the game was hiding it.
Built in, first-class: every fight shows its odds before you commit (expected outcome, chance of a loss, likely
spend and haul); every bar shows its ETA and per-hour rates, straight off the mix ledger; drop and yield rates are
visible once discovered. The optimizer plans from real numbers, never a spreadsheet beside the game.

**A third register for people talking to each other** (as habits is building one): the game's
world voice (clipped, lowercase, A Dark Room-like) sounds unnatural as conversation, so when townsfolk speak to one
another they talk the way people usually do. Start from habits' third register when the souls are built; it is
the same need.

**The journal is the player-character's own voice**. Its writer is a person with a will, so it is
not the narration's register: first person, lowercase and spare like the rest of the game, past tense and written
after the fact, dry and clinical, sometimes wrong or unsure of itself. It is someone writing to themselves, not talking,
so not the townsfolk's conversational register either. The log stays the live feed in the narration's voice; the
journal's `days` section retells the bigger beats in this one (`api/CONTRACT.txt`, "JOURNAL"), behind bookmarks for
days, creatures and places.

**Two registers, and Claude's own is neither.** World lines (the log, arrivals) are in the game's voice.
Controls and labels are game UI: terse nouns and verbs ("Target", "Run down", "Loss 8%", "Unscouted"), never
questions to the player or narration. A line that says what a change does is one short plain sentence: the thing, what
it now does, the new amount ("Camp level 2: the warm wall dries 7 wood at a time instead of 5"), never arrow notation
(after galaxy.click's reviewer read "→ 5 → 7" as notation). The first design pass read as Claude's register
("What should this line do?", "odds unknown until someone goes and looks"). Every new or changed
player-facing line gets a voice pass by a fresh agent before it ships, as in habits.

**What can be tapped looks tappable**. Anything that matters is reached through something that reads as a control
at a glance, a card or a button; never through a tap on a line, a number or a picture that looks like plain display.
Hidden taps are for easter eggs and other inconsequential extras only, knowing that what is not obvious goes unfound by
nearly everyone. Tapping a card that plainly isn't ready is one: an unready card looks unready (muted, only the
number its missing need is short of marked, never glowing; red is the ledger's alarm, never a need) but still answers a tap. A failed tap takes no time and nothing on screen looks
like progress: the card pulses red, what it is missing pulses with it (the need, skill level or step its blocker names,
or its countdown when that is all the card shows, as for a store never shown), and its failed line lands at once. A busy
card cannot be tapped and looks it. **Tapping never moves the layout**: one progress bar per thing, on the thing
itself, and anything that appears or changes state does so in space already reserved, so the next card is where the
player's finger expects it. The preview hid its order card behind a tap on a red ledger line, and no player ever set an
order. **Make it far more obvious than seems needed** (the yellow paint on climbable ledges), above all when the
builder and tester is a bot that already knows the answer. The first card, until its first tap, is only its verb under
the glow: a count, an empty bar and a time beside it read as something already under way, and a cold tester who doesn't
play games waited for it.

**A story line stays until it can be read.** Time never takes a line off the story strip: a line leaves only when
newer ones push it out of the room, and never before its reading time since it showed (`game/reading.ts`; the arrival
queue holds the next line back). The strip sits off the art, under it, and shows as many of the newest lines as fit,
whole: its height is the tallest line in the content at its width, so no line is cut and none arriving moves anything (lines on the art, in a band
under the chips, were cut at their first row by the chip row through ten-odd fixes; a phone band cut to a line or two
lost lines mid-sentence for that same cold tester). A line that leaves the strip before the player has touched anything since
it showed may not have been read, so the Log button takes the quiet dot until it is touched. A tap's line also shows
on its card for its reading time, for the eye at the finger; the strip and the Log are the record.

**The game never judges, in words, how you're doing or what you're after.** It states facts (rates, odds, how long
a store lasts, what a better option would gain) and never labels them: no "balanced", "inefficient", "wasteful" or
"recommended". Draining a store, running a slow mix or ignoring a better option can all be deliberate, and the
player is the one who knows why.

**Blind until learned, perfect once known** (going in blind fits the worldbuilding, an idle game wants perfect
information, and there is a place for both). A new region or a never-fought creature shows its odds as unknown,
honestly, never a guessed number. Once fought, scouted or studied, the numbers are exact. Discovery (scouting, a first
cautious encounter, a scholar's study, a watchtower) is how one becomes the other, and is progress in itself. Scouting
and tracking belong to Wayfinding, not a new skill: it is what turns unknown into exact numbers.

**What you learn is written in a journal, Gravity Falls style** (a plain bestiary is rarely read; a journal
can work). Handwritten, sketched, annotated, with crossed-out guesses corrected once you know better. Each creature,
place or method gets its entry when it turns from unknown to known, carrying the exact odds and rates, so the journal
is the perfect-information layer in costume: skimmable for numbers, readable for flavour. It suits someone who can't
trust their memory; whose handwriting is in it is decided in `content/`. It is also the lore's home, the second
layer under the direct story (the piece-it-together reading of Idle Fantasy's item descriptions), full
enough to reward a long bored read, with clues for whoever reads closely.
