# Getting story lines to where the eyes already are

How idle and incremental games put story text where a player watching bars and cards will read it, and what that
means for Ashfall's screen. Covers `open-work.md`, "How the story reaches the eyes". Source code was read at the
commits linked; reviews and papers were opened unless marked *snippet* (a search-result summary only).

## The finding

1. During a task the eyes go to the next thing the hand will act on and almost nowhere else. In a hand task, under 5%
   of fixations fell on objects the task didn't use, except while waiting (Land 2006). A story band off to one side is
   such an object, whatever its contrast.
2. Being near isn't enough: people notice objects and events that belong to what they're attending to, not ones that
   are merely close by (Simons & Chabris 1999). So the doubt about a line beside the card is well founded.
3. The games whose text gets read put it on the controls, or right against them, in short lines: Paperclips tells much
   of its story in project-button text, Candy Box 2 draws speech directly above the button that answers it, and A Dark
   Room's lines sit in a 200px column 20px from the buttons, median 34 characters.
4. In one scripted run of the v2 build, 22 of 31 lines landed in the same second as a visible change in the card
   panel. The line is likely to lose that contest: the change is part of the task, and attention goes to a change only
   while it happens (Rensink et al. 1997).
5. So: show each tap's line on the card that wrote it; give a line a moment alone before the thing it announces
   appears; and put the newest line at the top of the card column on desktop. Measure each change with a "was it
   seen" probe before keeping it.

## How the games do it

| Game | Where the text sits, relative to the controls | How a new line is signalled | Can it be missed? Log? | Line length | Opening pace |
|---|---|---|---|---|---|
| A Dark Room | Fixed 200px column directly left of the 700px button area, 20px gap ([css][adr-css]) | Prepended at the top, so older lines move down; 500ms fade-in; older lines fade into a gradient ([notifications.js][adr-notify]) | Lines for another location are held in a queue and printed when the player goes there, so they never land off-screen. No scrollback: they fade out | Median 34 characters, 90th percentile 62 (61 lines in [room.js][adr-room] and outside.js) | Lines on each action, with a 10s stoke cooldown, plus room and builder updates every 30s ([room.js][adr-room]) |
| Universal Paperclips | A five-line console at the top of the page, right above the clip counter and the Make Paperclip button ([index2.html][clips-html]) | Newest on the bottom row with a blinking cursor; older rows shift up, grey ([main.js][clips-main], [interface.css][clips-css]). New project cards flicker for about 0.4s ([main.js][clips-main]) | The four older rows show the last few lines, and that's all the history there is. Much of the story sits in project titles and descriptions, on the buttons themselves ([IF50][if50]) | Median 38 characters, 90th percentile 78 (138 messages in [main.js][clips-main] and [projects.js][clips-proj]) | Not measured |
| Candy Box 2 | Speech drawn into the ASCII scene beside the speaker, above the button it sets up ([CandyBox.ts][cb2-box]) | It's part of the screen state, so it stays there until the state changes | Persistent, so it can't be missed. Quests have a 10-line log ([QuestLog.ts][cb2-quest]) | Wrapped to the speech box's width | Not measured |
| Kittens Game | Separate right-hand column labelled "Game log" ([index.html][kg-html]) | Inserted under a date header, with no animation ([ui.js][kg-ui]) | 40 lines, older ones faded. Story shares the log with hunts, trades and crafting, under 20 filter tags the player can switch off ([core.js][kg-core]) | Not measured | Not measured |
| Trimps | One scrolling log box ([style.css][tr-css]) | Story lines get a star and cyan text; some get a highlight box ([updates.js][tr-upd], [style.css][tr-css]) | Story, Loot, Combat and Notices share the box, each type with its own toggle ([updates.js][tr-upd]) | Not measured | Not measured |
| Theory of Magic (Arcanum) | Log panel beside the vitals ([main.vue][arc-main]) | Story events get a title and text; repeats collapse into a count ([log.js][arc-log], [events.js][arc-events]) | Shares the log with unlocks, loot and combat, each type filterable ([outlog.vue][arc-out]) | Not measured | Not measured |
| Antimatter Dimensions | Story quotes are a centred modal, queued one at a time ([quotes.js][ad-quotes]) | The modal itself | Can't be missed, because it blocks the screen. Quote history can be reread ([modals][ad-modals]) | Not measured | Late game only |
| Spaceplan | Its "Word Outputter" (*snippet*, [GosuNoob][sp-gosu]). On mobile the messages are on their own screen, reached by swiping away from the solar system and unlocks ([PocketGamer][sp-pg]) | Not seen | One review says the story was too sparse and the text crammed into a small corner on iPad (*snippet*, [AppUnwrapper][sp-au]) | Not measured | Told "in sync with your unlocks and actions" ([PocketGamer][sp-pg]) |
| Idle Awakening: Mage's Path | A five-line story modal at the start, then a story icon under the level ring | The modal | The icon reopens it | Short | One modal, then cards |
| Frog Fractions *(contrast)* | No separate text channel: the game becomes a different genre, in the same play area ([Wikipedia][ff-wiki]) | The whole screen changes | No | Not applicable | Not applicable |
| Melvor Idle *(contrast, little story)* | Toasts, centre by default, can be set left or right ([wiki][mel-wiki]) | Toast | Gone after 2s by default. That works because the bank shows the state the toast reported | Not applicable | Not applicable |
| NGU Idle *(contrast)* | Its own store page offers "a really weird and funny story if you're into that"; the jokes are in boss and item names ([Steam][ngu-steam]) | Not applicable | The story is opt-in | Not applicable | Not applicable |

Kittens, Trimps and Arcanum all ended up with log filters. That's a sign the shared log is noise first and story
second.

## Patterns that work

- **Text on the control.** Much of Paperclips' story is in the project buttons the player is about to click
  ([IF50][if50], [projects.js][clips-proj]). Candy Box 2 draws speech above the button it sets up ([CandyBox.ts][cb2-box]).
  Why it works: during a task, the eyes go to the object the hand needs next, in the second before acting (Land 2006,
  [PDF][land]).
- **The text column touches the controls.** A Dark Room's lines are 20px from its buttons, and Paperclips' console sits
  just above its counter and first button. Neither makes the eye cross the screen.
- **Short lines.** Medians of 34 and 38 characters fit in one or two fixations. Ashfall's opening lines run longer:
  median 46, 90th percentile 74 (38 lines in `opening.toml`).
- **A line never lands off-screen.** A Dark Room holds a location's lines until the player is there
  ([notifications.js][adr-notify]). Ashfall's arrival queue already does this for what a return brings
  (`opening-screen.md`, "Coming back"), but it deliberately leaves story lines out.
- **The line comes before its consequence.** Spaceplan tells its story "in sync with your unlocks and actions"
  ([PocketGamer][sp-pg]). The line explains the card, so it should be read first. Two simultaneous onsets compete for
  attention, and the one in the task wins (Land 2006).
- **A crisp onset, not a slow fade.** Motion that has just started captures attention, while ongoing motion does not
  (Abrams & Christ 2003, [APS][abrams]). One short arrival movement is enough; it must not repeat.
- **Waiting is when the eyes are free.** In Land's tasks, fixations on unused objects happened mainly while waiting
  (for the kettle to boil, for example). An Ashfall bar filling is that wait, but the eyes spend it on the bar. So a line
  read during a wait has to be on or beside the bar.

**Attention research, only as it bears on placement.** In change blindness, large repeated changes went unseen for up
to 20s unless attention was on the item while it changed; attention follows local motion and high-level interest
(Rensink, O'Regan & Clark 1997, [abstract][rensink]). In inattentional blindness, about half of observers counting
passes missed an unexpected event. Noticing depended on how similar the event was to what they were tracking, not on
how close it was (Simons & Chabris 1999, [abstract][simons]). For reading, a line has to be looked at directly: the
perceptual span reaches only about 14–15 letters right of the fixation point (Rayner 1998, *snippet*, [via][rayner]).
Peripheral motion can at best draw the eye there. The F and Z patterns describe skimming an unformatted page "when
there are no strong cues" ([NN/g][nng-f]). A game's task cues override them, so they barely apply here, except that a
line's first words get the most fixations, so a line should start where the eye already is. A mouse cursor trails
gaze by 250–700ms and averages 130–280px away, closer while acting (Huang, White & Buscher, CHI 2012, [PDF][huang]).
That makes the last tap a usable but rough stand-in for where the eyes are.

## What to try in Ashfall

The screen as it is now (v2 build, rendered at 1280×800 and 390×844): on desktop the band sits on the art's top-left.
The newest line starts about 770px left of the card column and about 60px above the first card's title. On a phone it
sits at the top of the pinned art, about 360px above the cards, with the hands strip between them. A line arrives with
a 1.2s fade and a 4px rise.

Ranked by expected effect:

1. **The tap's line appears on the card that wrote it.** When a completion writes a line, the line shows in a slot
   reserved on that card (the meta row, where the timer sits) for about its reading time (characters ÷ 15 per second,
   at least 3s), then leaves the card. The band keeps its copy as the record. Lines written by the mix, by time, or by a
   standing action have no card and go to the band as now. Text on the control is the strongest pattern above, and it
   works the same on desktop and phone. Because the slot is reserved, taps still don't move the layout.
   *Fits into:* Cards (a second view of the line the Step already carries; the band stays the log). *Test:* the probe
   below. Pass if at least 80% of tap-written lines score "seen", against today's baseline.
2. **One onset at a time: the line first, then what it announces.** Put live story lines into the arrival queue at the
   head of their batch. The new card, chip, skill row or ledger line that came with a line shows one reading time
   later, or at the next tap, whichever is sooner, so input is never held. Today 22 of 31 lines share their second
   with a panel change. *Fits into:* Chronicle and unwrap, as the arrival queue's second use (live, not just on
   return): an Event Queue, which separates when something happens from when it is shown
   ([Nystrom][nystrom-eq]). *Test:* the same probe's "alone" condition: no other visible onset in the line's reading
   window. Pass if 90% of lines get one.
3. **On desktop, the newest line goes at the top of the card column**, in a fixed-height row under the hands strip,
   left-aligned with the card titles. The band on the art keeps the older lines, the chips and Log. This is A Dark Room's
   and Paperclips' placement: the line starts where the eye already works. It is cheaper than (1) and might do without
   it for lines that no tap wrote. *Test:* the probe's distance condition, with (1) off, so each change is measured on
   its own.

Swap the 1.2s fade for a short slide-in from the cards' side (about 200ms, once). This is a tweak that comes with (1)
or (3). It is not a separate item.

### The "was it seen" probe

Add a pass to the Playwright playthrough. For each line it records when the line landed, using the run log's
`NEW line` events. A line counts as seen when all of these hold during its reading window:

- **Visible:** its box is inside the viewport with the page visible, and `elementFromPoint` at its start, middle and
  end returns the line, so nothing covers it.
- **Near the eyes:** its first word is within 300 CSS px of the last tap, or within 300px of the bar that tap started.
  The threshold is set from Huang et al.'s cursor offsets. It is an assumed threshold, not a measured one for touch.
- **Alone:** no other visible onset elsewhere on screen.

Report the share of lines seen per build and per form factor, plus the lines that failed and which condition failed.
Run it on the scripted sharp route and on a lazy route (taps spaced out, mostly the mix running).

The probe is a proxy and can't replace a person. Confirm with one tester session per change. Afterwards, ask the
tester to pick which lines they saw from a mix of real and invented lines. That can't be the owner: invented story lines
would spoil the owner. Live, the same three conditions could become one telemetry event per line (line id, seen yes/no, and
which condition failed), which stays within `telemetry.ts`'s ids-and-counts rule.

## What to avoid

- **Modals and pauses for story** (Antimatter Dimensions' quotes, Idle Awakening's opening). They get read, but they
  break "never vying for attention" and stop input.
- **A separate screen or tab for the text** (Spaceplan's mobile message screen). A line the player has to go and find
  is a line they miss.
- **One log for story and everything else** (Kittens, Trimps, Arcanum). It ends up needing filters, and the story is
  buried under the noise.
- **Blinks, pulses and looping motion to pull the eye** (Paperclips' blink). `decisions.md` rules them out. A single
  onset does the job.
- **Toasts for story** (Melvor's 2s toasts). They work only where the state they report stays visible somewhere else.
- **Relying on proximity alone.** A line that sits near the card but looks like a different kind of thing can still go
  unseen (Simons & Chabris 1999). Change (3) is the one most exposed to this, which is why it ranks below (1).
- **Typewriter text and slow fades.** They delay the onset and stretch the change past the moment the eye is there.

[adr-css]: https://github.com/doublespeakgames/adarkroom/blob/1fada4620b6c66bd07bf15a3f1eb8223df8bc1d7/css/main.css#L41-L46
[adr-notify]: https://github.com/doublespeakgames/adarkroom/blob/1fada4620b6c66bd07bf15a3f1eb8223df8bc1d7/script/notifications.js
[adr-room]: https://github.com/doublespeakgames/adarkroom/blob/1fada4620b6c66bd07bf15a3f1eb8223df8bc1d7/script/room.js#L5-L10
[clips-html]: https://www.decisionproblem.com/paperclips/index2.html
[clips-main]: https://www.decisionproblem.com/paperclips/main.js
[clips-css]: https://www.decisionproblem.com/paperclips/interface.css
[clips-proj]: https://www.decisionproblem.com/paperclips/projects.js
[if50]: https://if50.substack.com/p/2017-universal-paperclips
[cb2-box]: https://github.com/candybox2/candybox2.github.io/blob/35301d438aa2c1e58e8cb3ea215b0af323bddf9b/code/main/CandyBox.ts#L53-L78
[cb2-quest]: https://github.com/candybox2/candybox2.github.io/blob/35301d438aa2c1e58e8cb3ea215b0af323bddf9b/code/main/QuestLog.ts
[kg-html]: https://github.com/nuclear-unicorn/kittensgame/blob/781e379f79f1e7512d168849cba21ed111502644/index.html#L430
[kg-ui]: https://github.com/nuclear-unicorn/kittensgame/blob/781e379f79f1e7512d168849cba21ed111502644/js/ui.js#L1018-L1081
[kg-core]: https://github.com/nuclear-unicorn/kittensgame/blob/781e379f79f1e7512d168849cba21ed111502644/core.js#L405-L570
[tr-upd]: https://github.com/Trimps/Trimps.github.io/blob/b9edb1dfee270ebf81bef8d934dc71276bf8d963/updates.js#L5098-L5143
[tr-css]: https://github.com/Trimps/Trimps.github.io/blob/b9edb1dfee270ebf81bef8d934dc71276bf8d963/css/style.css#L3524-L3531
[arc-main]: https://gitlab.com/lerpinglemur/arcanum/-/blob/35437ed4869856220d17ea9564b339cd02b03035/src/ui/main.vue#L425
[arc-log]: https://gitlab.com/lerpinglemur/arcanum/-/blob/35437ed4869856220d17ea9564b339cd02b03035/src/log.js
[arc-events]: https://gitlab.com/lerpinglemur/arcanum/-/blob/35437ed4869856220d17ea9564b339cd02b03035/src/events.js#L295-L300
[arc-out]: https://gitlab.com/lerpinglemur/arcanum/-/blob/35437ed4869856220d17ea9564b339cd02b03035/src/ui/outlog.vue
[ad-quotes]: https://github.com/IvarK/AntimatterDimensionsSourceCode/blob/5409e320cecef96a917cca1dfb68f1f183e499ca/src/core/celestials/quotes.js
[ad-modals]: https://github.com/IvarK/AntimatterDimensionsSourceCode/tree/5409e320cecef96a917cca1dfb68f1f183e499ca/src/components/modals/celestial-quotes
[sp-gosu]: https://www.gosunoob.com/news/spaceplan-comes-out-several-platforms-gets-launch-trailer/
[sp-pg]: https://www.pocketgamer.com/spaceplan/review/
[sp-au]: https://appunwrapper.com/2017/05/09/spaceplan-ios-review/
[ff-wiki]: https://en.wikipedia.org/wiki/Frog_Fractions
[mel-wiki]: https://wiki.melvoridle.com/w/Settings
[ngu-steam]: https://store.steampowered.com/app/1147690/
[land]: https://www.cis.rit.edu/pelz/scanpaths/papers/eye-movements-every-day-life-land-2006.pdf
[abrams]: https://www.psychologicalscience.org/journals/psychological-science/1467-9280.01458/
[rensink]: https://www2.psych.ubc.ca/~rensink/publications/abs.96.2.html
[simons]: https://www.citedrive.com/en/discovery/gorillas-in-our-midst-sustained-inattentional-blindness-for-dynamic-events/
[rayner]: https://speedreading.com/research/eye-movements-visual-processing.php
[nng-f]: https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
[huang]: https://www.microsoft.com/en-us/research/wp-content/uploads/2012/01/Final_GazeCursor_CHI12.pdf
[nystrom-eq]: https://gameprogrammingpatterns.com/event-queue.html
