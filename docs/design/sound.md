# Sound map

Where the game makes a sound, how loud, how often, where it stays quiet, how each sound lands on its picture, and what
a recording must measure to be a candidate. The ladder's one-shots, the bed under the scene and the evening piece are wired, silent until a sound is picked. Candidates are screened against this map, and the owner picks each sound by ear.

Fits into: Feedback (`docs/systems.md`). Each one-shot is one more field on a ladder rung in
`app/client/src/ui/feedback/ladder.ts`, fixed like the rung's effect, and the null is silence. The fire's bed and the evening
piece are one more field on a scene layer (`SceneLayer` in `app/client/src/scene/manifest.ts`), so they follow the
layer's own `when`. No new system.

## The ground rules

- **On by default, off in one tap.** A speaker button always on screen mutes everything at once, and a Sound
  switch in settings says the same; the choice is kept per device, because the same save is played on a phone in a
  waiting room and on a desktop at home, and only the player knows which one may make noise (habits' music does
  the same). Browsers hold audio until the page's first tap, so the first sound is that tap's. Nothing in the game
  needs sound (`decisions.md`, "Silent and glanceable"). The device's own volume is the volume.
- **Sound only answers something the player did or something they are looking at.** Nothing plays while the page is
  hidden, and no sound ever exists to call the player back (`decisions.md`, "Fun, but never vying for attention").
- **Every sound doubles something already on screen.** Each moment below has its visual on the ladder; with sound off
  nothing is lost. What is out of sight (a card below the fold, which shows at once and takes no turn) makes no sound.
- **A sound never grows on repeats.** A card's hundredth tap sounds like its first, as its ring looks like its first
  (`decisions.md`, "Rewarding at any moment").
- **One cue per arrival batch.** When several things arrive together (a return after hours away, a level and a new
  card at once), the batch plays its highest cue once, at that thing's own turn, and the rest arrive silent. Highest
  first: the opening's end, a story beat, a level, something new.
- **One voice.** The pitched cues are one instrument at three weights: something new is one note, a level is that
  note three times rising, a story beat is one note a fifth lower. The rest is wood and paper. Nothing is bright
  enough to read as glass, and no pack stinger is used: a phrase has a mood, and a cue must not.

Loudness is relative to the tap, the quietest sound the game makes and the one heard most: **soft** is the tap's
level, **medium** 4 dB above it, **full** 8 dB above it, the loudest the game ever gets, used once. The bed sits
under the tap, and the evening piece between the bed and the tap. These steps are where the listening room starts;
the owner's ear sets them.

## The ladder

| Rung | Its picture | Sounds? | Loudness | How often |
|---|---|---|---|---|
| Background (a card done by the mix or a rule) | the "+1" | No | — | — |
| Tap (a card done from the player's tap, Next included) | the `landed` ring | Yes: one short, dry knock on wood | Soft | Every landed tap; taps within a tenth of a second play one. The pitch steps through a fixed cycle of five small offsets, each within a third of a semitone, so a run of taps is not a machine gun |
| Tap, its chain (each link of a live step's cascade lighting) | the link's ember mark | Yes: a wooden tick per link after the first, each a step higher, the volume fixed | Soft | The first link is the tap's own knock. Up to five ticks follow at the link pace, one per turn, rising through the pentatonic on the First note; the next chain starts low again. Links that light together play one tick |
| First (something new arrives: a card, chip, skill row, ledger line, feature, an offer) | the `arrive` pulse | Yes: one struck note | Soft | One per batch |
| Level (a skill or the Camp reaches a level) | the `burst` | Yes: the First note three times, rising (root, third, fifth) | Medium | One per batch, however many levels landed in it. A level that is a link in a chain plays this in place of its tick |
| Big: the opening's end | the end's first line, the evening firelight coming up | Yes: one low strike that rings and settles | Full | Once per save, whenever the end's lines play; a return that shows the dusk alone, without its lines, plays nothing |
| Big: a feature's card (the end of the content shipped so far) | — | No cue of its own; its beat's story cue already played | — | — |

The chain's rising pitch is the one place a sound changes from play to play. It marks a link's place in one chain,
not a repeat, and it resets every chain: a good build setting off a long cascade should sound like one
(`decisions.md`, "Cascades are the peak"). A chain the mix or a rule started stays silent, like its completion.

**Below the ladder**, each no louder than the tap:

| Moment | Sounds? |
|---|---|
| A failed tap (its card and blocker pulse red) | Yes: the tap's kind of knock, plainly duller and 4 dB under it; it may fall in pitch |
| A journal page turned | Yes: a page |
| A rule saved, or a rule offer accepted (it flies to the Rules tab) | Yes: a small settle as it lands on the tab, in place of the First note that landing would otherwise play |
| A card pressed (it sinks) | No: the tap's own sound comes when the card lands |
| A share divider dragged, a ledger line settling back from red, a rule row lighting as it starts a card | No |

## Story moments

| Moment | Sounds? |
|---|---|
| A main story beat (B1 to B52) | The story cue, medium, once, as the beat's first line shows, before it is read |
| A weekly beat (B3, B10, B17 and the rest marked weekly) | The same story cue, no bigger: the words carry the weight |
| A season-turn beat (B8, B13) | The same story cue; later season turns that are not beats are silent |
| B53 | The same story cue and nothing more (`decisions.md`, "The ending is a real finish without fanfare") |
| The ending offers (O ids) | The First note, like any offer the player can act on; nothing marks them apart |
| Side-layer moments (SL ids) and side beats (F ids and the one other) | Silent: they arrive as lines, and the story cue keeps meaning "the main story moved" |
| Mini-stories, people's lines, daily mentions, chronicle lines | Silent |

Every beat shares one cue, so the sound never tells the player what kind of beat is coming before the words do. The
cue is one low note, level in pitch: a rise would celebrate and a fall would mourn.

## The bed under the scene

A quiet loop under everything while the scene shows, below the tap's level, so it is felt more than heard; it
serves "Something to watch, any time, for hours" (`decisions.md`).

| Layer | When | Level |
|---|---|---|
| Wind | From the first open, always | Fixed. It fades in over 2.5 s from the page's first tap |
| The fire | Once the fire is built, on the same condition that lights the scene's firelight; it never plays before | Follows the firelight layer's alpha, then fixed |

The fire's sound follows its picture: its gain is the alpha the scene draws the first firelight layer at. The scene
fades a layer in over `FADE_S` (0.8 s, `app/client/src/scene/scene.ts`), so the fire catches in sound over the same
0.8 s it catches in light, and the two cannot disagree. The flicker (`app/client/src/scene/flicker.ts`) does not move
the gain: the crackle is the flicker, and under reduced motion the light holds steady while the sound stays as it is.

The grades (`tools/scene/grades.py`) do not move the bed. Dusk and night dim the picture and leave the fire's light
alone, since a light that is the player's is never dimmed; the same holds for its sound.

Each loop is seamless as a file: where a recording's loop point steps in level or clicks, a crossfade is baked into
the asset, and the page loops it sample-exact. The bed is never ducked under a one-shot. It sits well under the tap
already, and taps come in runs, so ducking would make the wind pump at the pace of the taps.

## Music: the evening piece

There is no score under play. The game is left open for hours, where a loop of a minute or two comes round thirty
times an hour; the pitched cues would sound against whatever key it was in; and its mood, the one thing that decides
whether it fits, is the one thing no screen here can judge.

Music has one place: **the evening, at the fire.** When the evening firelight comes up in front of the player, one
piece plays once through and ends. It is not looped and not repeated that evening.

- **It starts** with the layer: a firelight layer the manifest marks as the evening's begins to show while the page
  is in view. It fades in over 2.5 s, the default grade ease (`GRADE_S`, `app/client/src/scene/manifest.ts`).
- **At the opening's end** it is heard for the first time. The low strike lands on the end's first line; the piece
  enters 4 s later, when the strike is over. Both sit inside the 20 s the end's lines are given to be read
  (`READ_MS`, `app/client/src/ui/story/end.ts`), when nothing else arrives.
- **It leaves** by itself at its last note. If the grade changes first (night falls), it fades out over that grade's
  ease.
- **Under a story cue or the opening's strike** it drops 9 dB over 0.2 s, holds for the cue, and comes back over
  2.5 s. Shorter cues play over it.
- **Never:** before the fire is built; by day; in the night's own grade; on a return, for an evening that began
  while the page was hidden or shut (the opening's end aside, which plays whenever its lines do); twice in one
  evening.

## Changes of state

| Change | What the sound does |
|---|---|
| The page's first tap | The audio starts. That tap's own sound plays; the wind fades in over 2.5 s; the fire, if built, over 0.8 s |
| A layer or grade changes while watched | The fire follows its layer's alpha (0.8 s). The evening piece starts or fades as above. Nothing else moves |
| The page is hidden | Everything ramps to silence in 50 ms and the audio is suspended. Sounds waiting their turn are dropped |
| The page is shown again, or a return after hours | The bed comes back over 0.8 s, as the scene now is. Nothing that happened while away is replayed. The return's batch plays its one cue. An evening piece cut off under 30 s ago carries on from where it stopped; an older one is over |
| Mute | The same as hidden: silence in 50 ms, audio suspended |
| Unmute | The same as shown again. No one-shot is replayed |
| Reduced motion | No change to what sounds. Links and arrivals that show together play one sound |

## Landing a sound on its picture

A sound belongs to its animation: its attack lands as the animation starts, and it is over before the animation is.
The window for the attack is from 45 ms before the picture's first frame to 125 ms after it, the range in which sound
and picture are not seen to be apart (ITU-R BT.1359). Durations are the code's own.

| Sound | Starts on | Its animation | Longest it may be heard |
|---|---|---|---|
| Tap | the `landed` class going on the card | `landed`, 0.7 s (`app/client/src/game.css`) | 0.3 s |
| Chain tick | the link's turn in the cascade | link pace 90 ms (`LINK_GAP_MS`, `app/client/src/game/story/arrivals.ts`); the mark fades over 0.4 s (`--link-ms`) | 0.12 s, so ticks stay apart |
| First | the `arrive` class going on the thing | `arrive`, 0.5 s | 0.5 s |
| Level | the `burst` class going on the row | `burst`, 0.9 s; the card's line stays 2 s (`LEVEL_MS`, `app/client/src/ui/cards/cardlevel.ts`) | 0.9 s |
| Story cue | the beat's first line showing | `line-in`, 0.2 s; the line is then held 3.5 s or more (`READING.floorMs`, `app/client/src/game/story/reading.ts`) | 2.5 s, over before anything else can show |
| Opening's end | the end's first line showing | the evening firelight, 0.8 s; the lines' 20 s | 4 s |
| Failed tap | the `tap-failed` class going on the card | 0.4 s (`--fail-ms`), reddest at 0.14 s | 0.3 s |
| Page turn | the page's slide starting | `journal-turn`, 0.15 s | 0.5 s, with its peak inside the first 0.27 s |
| Rule settle | the flight ending on the Rules tab | the flight, 0.45 s (`FLY_MS`, `app/client/src/ui/asks/flight.ts`), then `arrive` on the tab | 0.3 s |

How the page makes it land:

- **One audio context**, made at the first tap with the interactive latency hint. Every one-shot is decoded into
  memory then; a sound that is not decoded when its moment comes is skipped, since silence is better than late.
- **No lead-in.** Each asset starts within 5 ms of its first sound. Several recordings open on silence (one page
  turn on 0.2 s of it, one card on a full second), which would put the sound that far behind its picture.
- **A sound that answers the moment** (tap, failed tap, page, First, story cue, the strike, the settle) starts in the
  same call that puts the class on. It is heard the output latency later and the picture paints a frame later, so
  the two are apart by the output latency less a frame. That is inside the window up to about 140 ms of latency.
  Past that (some Bluetooth), a sound that answers a tap cannot be on time, and it is not delayed further to try.
- **A sound in a rhythm** (the chain's ticks, the level's three notes) is scheduled as a group on the audio clock
  when its first sound starts: tick *n* at the first tick's start plus *n* × 90 ms. Frames come every 16.7 ms, so
  ticks started one by one from the frame loop would wander by up to a fifth of their spacing, and the ear hears
  that where the eye does not. A tap that sets off every waiting link stops the ticks not yet begun and plays one.
- **A sound due at a known later time** is placed with the context's output timestamp, which pairs a context time
  with the clock time it is heard at; where a browser lacks it, the context's reported output latency is taken off.
- **Pitch is set by playback rate**, in exact ratios: the level's notes at 1, 5/4 and 3/2 of the First note; the
  chain's ticks at 1, 9/8, 5/4, 3/2 and 5/3 of a lowest tick tuned to the First note's own pitch, in whichever
  octave keeps the tick inside its length and brightness. A level that lands mid-chain plays its three notes in
  place of a tick, so the ticks have to be in those notes' key.
- **The opening's strike is tuned the same way**, to the tonic or the fifth of the evening piece, which enters four
  seconds after it. A strike a semitone off makes the piece sound out of tune as it arrives.
- **Cut off cleanly.** A one-shot stopped early (hidden, muted, links set off at once) fades over 50 ms.

## What a candidate must measure

Kind comes from the two listeners agreeing; where they split, the clip is flagged for the ear. Shape comes from
measurement. Brightness is the spectral centroid: wood sits at 600 to 1,300 Hz, and from about 3,600 Hz a knock reads
as glass. One-shots under 0.4 s are levelled by true peak, since integrated loudness cannot measure a tenth of a
second. A pitched cue's slope is never below −0.5 semitones a second, the failed tap aside.

| Job | Kind | Events | Attack | Heard for | Brightness | Also |
|---|---|---|---|---|---|---|
| Tap | a knock | one (onsets under 60 ms apart are one) | 35 ms or less | 0.2 s or less | 600 to 1,300 Hz | — |
| Failed tap | a knock | one | 35 ms or less | 0.3 s or less | at most 0.7 of the tap's | may fall in pitch |
| Chain tick | a tick or knock | one | 25 ms or less | 0.09 s or less at its lowest rate | 2,500 Hz or less at its top rate | pitch steady within half a semitone, so it can be tuned |
| First | a struck note | one | 35 ms or less | 0.2 to 0.5 s | 1,500 to 3,000 Hz | pitch level or rising |
| Level | the First clip | three plays, 110 ms apart | as First | 0.9 s or less in all | as First | rising by construction |
| Story cue | a struck note | one | 50 ms or less | 1 to 2.5 s | 2,000 Hz or less | pitch level within half a semitone a second, and below the First note |
| Opening's end | a low strike, or one swell | one | 50 ms or less for a strike; a swell no slower than 0.8 s | 2 to 4 s | 2,000 Hz or less | pitch level |
| Page turn | paper | one gesture | peak within 0.27 s | 0.5 s or less | — | — |
| Rule settle | something set down | one, or a contact and one smaller | 35 ms or less | 0.3 s or less | 3,000 Hz or less | — |
| Wind | wind, a recording | — | — | a loop of 90 s or more | 1,000 Hz or less | loudness range 7 LU or less, with no swell or trough at the seam; seam step 1 dB or less, no click |
| Fire | fire | — | — | a loop of 60 s or more | 1,500 Hz or less | loudness range 6 LU or less; peaks at most 14 dB over its loudness, so no pop is louder than a tap; seam step 1 dB or less |
| Evening piece | music, one or two instruments | under one onset a second | — | 80 to 180 s, ending in its own tail | 1,200 Hz or less | its key measured, with the story cue's note and the Level's three notes in its scale |

The evening piece's mood is judged by ear and by nothing else.

The wind's loudness range is as wide as the way it is played allows: at a fixed gain well under the tap and never
ducked, a gust at the top of a 7 LU range is still under the tap. Its length is not traded away, because a loop's
period is what hours of play expose. The fire's peak limit is not traded either: a pop over the tap's level reads as
a tap the player did not make. A fire recorded with louder pops is clipped to the limit in the asset, sample by
sample, which leaves the seam alone; whether it still crackles after that is for the ear.

## Never sounded

- Anything the mix or the rules do on their own: completions, rule runs, chains they start.
- Anything going wrong in the world: a red, falling or starved ledger line, a store full and spilling, threats,
  fights, losses and deaths. The red line is the signal, and an alarm would summon the player to a game that never
  needs them.
- A wait or countdown finishing. A ding at the end of a timer teaches watching the timer.
- Anything while the page is hidden, and anything on opening the app beyond the bed and the return batch's one cue.
- A grade changing. The light going is watched, not announced; only the evening firelight brings the piece.

## Rejected, and why

- **Sound off by default.** Sound is part of how the game feels, and a player who must not make noise has the
  speaker button one tap away.
- **One setting for the whole account.** The right answer differs by device (phone in public, desktop at home), so
  the switch belongs to the device.
- **A score under play, or a loop per grade.** See "Music: the evening piece".
- **The fire's sound from the start.** There is no fire to hear until it is built, and the scene does not draw one.
- **The bed changing with the grade, or growing with each firelight layer.** The wind does not know the hour, and
  three firelight layers summed would lift the fire over the tap.
- **Ducking the bed under one-shots.** See "The bed under the scene".
- **The fire's level following the flicker.** A level that wanders eleven times a second is a tremolo.
- **A sting per beat, matched to its mood.** It would give the mood away before the line is read, and every beat
  would need its own sound screened.
- **Pack stingers as cues.** They are phrases of four seconds and more against animations of half a second to four,
  and a phrase cut short by a fade is worse than a single note.
- **A bigger cue for weekly beats or for the last beat.** Bigger sound for the same kind of event lowers the
  player's sense of competence, and the last beat is decided as a finish without fanfare.
- **A sound on each arrival of a batch.** Several notes in a row would be louder, in sum, than the level above them.
- **Alarms for trouble.** See "Never sounded".
- **Sound for the mix's and rules' completions.** The mix runs all the time; a sound per completion becomes a
  metronome, and it would also take the tap's sound away from the tap.
- **Sounds that grow with streaks, combos or repeats.** The ladder's ceiling: a fixed effect per kind of event.
- **A click on press as well as on landing.** Two sounds per tap for one action; the press already answers at once
  by sinking.
- **Delaying the picture to wait for slow audio.** The tap's answer on screen comes first; a late sound on a
  Bluetooth speaker is the speaker's.
- **Voiced lines.** The lines are read at the player's pace, and a voice would set a tone the text owns.
- **Separate volume sliders.** The owner's ear sets the mix once and the device has a volume.

## What wiring needs

- The view has to say which line is a beat's first line, as an explicit field: a served line (`LogLine` in
  `app/ashfall_app/api/models.py`) carries only its key and card, and the client must not guess beats from keys.
  Built: `LogLine.opens_beat`, from each chapter's `[beat_lines]` table. The opening's end is not a served line, so
  its first line is still the first of the end's line keys.
- A scene layer says what it sounds as, an explicit field beside `flicker`: the fire's bed on the first firelight
  layer, the evening piece on the evening's. The page never reads a layer's id to decide. Built: `sound` on a
  layer, `fire` on the first firelight and `evening` on every dusk firelight.
- A cascade has to know a tap started it, as its completion's rung does (`completionRung`). Built:
  `Reveal.tapStarted`.
- The part that starts the evening piece keeps the last view it saw while the page was in view; the first view after
  the page is shown only resets it.
- habits' tap ladder and reward sounds are candidates like any others, screened and picked by ear, never defaults.
