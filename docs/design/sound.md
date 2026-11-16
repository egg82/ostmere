# Sound map

Where the game makes a sound, how loud, how often, and where it stays quiet. Nothing here is built yet; this is the
map the sound candidates are screened against, and the owner picks each sound by ear.

Fits into: Feedback (`docs/systems.md`). Each sound is one more field on a ladder rung in
`app/client/src/ui/ladder.ts`, fixed like the rung's effect, and the null is silence. No new system.

## The ground rules

- **Off until the player turns it on.** One Sound switch, kept per device: the same save is played on a phone in a
  waiting room and on a desktop at home, and only the player knows which one may make noise. Off by default because
  the game is played in spare minutes in public, and `decisions.md`, "Silent and glanceable", asks that nothing in it
  needs sound. The device's own volume is the volume.
- **Sound only answers something the player did or something they are looking at.** Nothing plays while the page is
  hidden, and no sound ever exists to call the player back (`decisions.md`, "Fun, but never vying for attention").
- **Every sound doubles something already on screen.** Each moment below has its visual on the ladder; with sound off
  nothing is lost.
- **A sound never grows on repeats.** A card's hundredth tap sounds like its first, as its ring looks like its first
  (`decisions.md`, "Rewarding at any moment").
- **One cue per arrival batch.** When several things arrive together (a return after hours away, a level and a new
  card at once), the batch plays its highest cue once and the rest arrive silent. Highest first: the opening's end,
  a story beat, a level, something new.

Loudness is relative to the tap, the quietest sound the game makes and the one heard most: **soft** is the tap's
level, **medium** a clear step above it, **full** the loudest the game ever gets, used once.

## The ladder

| Rung | Sounds? | Loudness | How often |
|---|---|---|---|
| Background (a card done by the mix or a rule) | No | — | — |
| Tap (a card done from the player's tap, Next included) | Yes: a short, dry knock | Soft | Every landed tap; taps within a tenth of a second play one. A slight change of pitch between plays so a run of taps is not a machine gun |
| Tap, its chain (each link of a live step's cascade lighting) | Yes: a small tick per link, each a step higher in pitch, the volume fixed | Soft | One per link at the link pace, only for a chain a tap started; the pitch stops rising after eight links and starts low again on the next chain |
| First (something new arrives: a card, chip, skill row, ledger line, feature, an offer) | Yes: a short, light tone | Soft | One per batch |
| Level (a skill or the Camp reaches a level) | Yes: a fuller tone, a little longer than First | Medium | One per batch, however many levels landed in it |
| Big: the opening's end (the scene going to dusk) | Yes: one low, settling cue under the dusk | Full | Once per save; a return that shows the dusk alone, without its lines, plays nothing |
| Big: a feature's card (the end of the content shipped so far) | No cue of its own; its beat's story cue already played | — | — |

The chain's rising pitch is the one place a sound changes from play to play. It marks a link's place in one chain,
not a repeat, and it resets every chain: a good build setting off a long cascade should sound like one
(`decisions.md`, "Cascades are the peak"). A chain the mix or a rule started stays silent, like its completion.

**Below the ladder**, each no louder than the tap:

| Moment | Sounds? |
|---|---|
| A failed tap (its card and blocker pulse red) | Yes: a dull, muted knock, softer than a landed tap |
| A journal page turned | Yes: a page |
| A rule saved, or a rule offer accepted (it flies to the Rules tab) | Yes: a small settle |
| A card pressed (it sinks) | No: the tap's own sound comes when the card lands |
| A share divider dragged, a ledger line settling back from red, a rule row lighting as it starts a card | No |

## Story moments

| Moment | Sounds? |
|---|---|
| A main story beat (B1 to B52) | The story cue, medium, once, as the beat's first line shows, before it is read |
| A weekly beat (B3, B10, B17 and the rest marked weekly) | The same story cue, no bigger: the words carry the weight |
| A season-turn beat (B8, B13) | The same story cue; later season turns that are not beats are silent |
| B53 | The same story cue and nothing more (`decisions.md`, "The ending is a real finish without fanfare") |
| The ending offers (O ids) | The First tone, like any offer the player can act on; nothing marks them apart |
| Side-layer moments (SL ids) and side beats (F ids and the one other) | Silent: they arrive as lines, and the story cue keeps meaning "the main story moved" |
| Mini-stories, people's lines, daily mentions, chronicle lines | Silent |

Every beat shares one cue, so the sound never tells the player what kind of beat is coming before the words do.

## Never sounded

- Anything the mix or the rules do on their own: completions, rule runs, chains they start.
- Anything going wrong in the world: a red, falling or starved ledger line, a store full and spilling, threats,
  fights, losses and deaths. The red line is the signal, and an alarm would summon the player to a game that never
  needs them.
- A wait or countdown finishing. A ding at the end of a timer teaches watching the timer.
- Anything while the page is hidden, and anything on opening the app beyond the return batch's one cue.

## Rejected, and why

- **Sound on by default.** It would make the first public open loud for a game whose decisions say it needs no
  sound; the Sound switch is one tap for a player who wants it.
- **One setting for the whole account.** The right answer differs by device (phone in public, desktop at home), so
  the switch belongs to the device.
- **Music.** Played in spare minutes, often somewhere a phone stays quiet, so music would mostly be muted, and a
  score is the most expensive thing on this page to find and screen. Revisit if the owner wants it.
- **An ambient bed under the scene** (fire, wind, the town's noise). Same reasons as music, for now. It is the one
  addition here that would serve "something to watch, for hours" (`decisions.md`, "Something to watch, any time, for
  hours"), so it is the first thing to reconsider.
- **A sting per beat, matched to its mood.** It would give the mood away before the line is read, and every beat
  would need its own sound screened.
- **A bigger cue for weekly beats or for the last beat.** Bigger sound for the same kind of event lowers the
  player's sense of competence, and the last beat is decided as a finish without fanfare.
- **Alarms for trouble.** See "Never sounded".
- **Sound for the mix's and rules' completions.** The mix runs all the time; a sound per completion becomes a
  metronome, and it would also take the tap's sound away from the tap.
- **Sounds that grow with streaks, combos or repeats.** The ladder's ceiling: a fixed effect per kind of event.
- **A click on press as well as on landing.** Two sounds per tap for one action; the press already answers at once
  by sinking.
- **Voiced lines.** The lines are read at the player's pace, and a voice would set a tone the text owns.
- **Separate volume sliders.** There is one kind of sound and the device has a volume.

## What wiring needs

- The view has to say which line is a beat's first line, as an explicit field: a served line (`LogLine` in
  `app/ashfall_app/api/models.py`) carries only its key and card, and the client must not guess beats from keys.
- habits' tap ladder and reward sounds are candidates like any others, screened and picked by ear, never defaults.
