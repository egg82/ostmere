# Game design 101: what the general research says, checked against the design

The general grounding the idle-game research never covered: onboarding, feedback, motivation, playtesting, making
systems legible, and game UI. It answers three questions: which principles hold across those fields, where
`decisions.md` agrees with them or runs against them, and which changes are worth testing first. Each topic's full
findings and sources are in `design-101/<topic>-writeup.txt` (Part A general, Part B what it means here) and
`design-101/<topic>-notes.jsonl` (one row per source, with its URL and whether it was read in full or only as a
snippet). Evidence is marked in a word: **research** (a study or paper), **developer** (a designer's own account),
**guideline** (a published standard), **practitioner** (guides, methods pages, postmortems without data),
**verbatim** (player text), **opinion** (critics, reviews), **snippet** (seen only in a search result),
**inference** (reasoned here from a cited source that does not say it). As of 2026-10-22.

## 1. Cross-topic findings

**Feedback should tell players what their own action did; making it bigger does not help and can hurt.**
In a preregistered study of 1,699 players, feedback that depended on whether the action succeeded raised curiosity,
competence and effectance, while amplifying the same feedback lowered competence and effectance (Kao et al., CHI 2024,
research, read in full). An earlier study by the same group found medium and high juice beat both none and extreme;
its own effect sizes were not read, only its shape as reported by two papers read in full. Rewards work the same way:
across 128 experiments, rewards promised in advance for doing a task cut later free-choice interest, while positive
feedback raised it (Deci, Koestner and Ryan 1999, research, read in full). Into the Breach shows every enemy attack
so that "it's very clear how or why you failed" (developer, Justin Ma, Road to the IGF 2018). Depth: `feedback-writeup.txt` 1 and 6,
`motivation-writeup.txt` A2.

**Curiosity, not enjoyment, predicts whether people keep playing, and a gap they can see is what drives it.**
In the same CHI 2024 study, curiosity was the only predictor of free-choice playtime; enjoyment did not predict it
(research). Loewenstein's information-gap theory (research, read in full) says curiosity grows as the player knows more
of a set, and Sid Meier's rule is to reward arrival but "focus your attention on the next thing to do" (developer).
The popular Zeigarnik claim, that unfinished tasks are remembered better, fails in a 2025 meta-analysis of 59 publications (Ghibellini & Meier, research, read in full: no memory advantage), which does find a reliable tendency to resume them (67% against 50% chance; student lab tasks, no games). No game evidence shows unfinished sessions bring players back (null).
Depth: `motivation-writeup.txt` A3, A7.

**Teach at the moment of need, on the real thing, and less than feels necessary.** Across 45,000 players, tutorials
paid off only in the most complex of three games and did nothing measurable in the two that could be learned by
experimenting (Andersen et al., CHI 2012, research, read in full). Guidance that helps a novice becomes redundant, and
can hurt, once they have the skill, so support should thin out as the player shows they have learned
(Kalyuga 2007, research, read in full; no game study). The claim that players click straight past instruction text is
from informal numbers only (practitioner, snippet). Depth: `onboarding-writeup.txt` A1, A4, A5.

**The order of encounters is the lesson, and too many new things at once is the failure playtests keep finding.**
Valve's commentary names one puzzle that "introduced too many new concepts at once" and describes portal teaching as a
clean room first, then twisting a rule the player already knows (developer, read in full). Nintendo moved the easier
features to the start of each level after beginners struggled (developer, read in full). Factorio's
developers removed an overlay from a machine once the machine showed its own state, and kept overlays for information
that only matters some of the time (developer, read in full). Depth: `onboarding-writeup.txt` A2, A3;
`legibility-writeup.txt`; `game-ui-writeup.txt` 4.

**Show cause both ways: what will happen before the player commits, and why something happened afterwards.**
Showing what will happen is well sourced: Into the Breach shows every attack before it lands and keeps the numbers small
(developer, Justin Ma, Road to the IGF 2018); Slay the Spire's intents show facts, not advice (opinion), and came out of Early Access playtesting, not up-front design (practitioner, a repost of an Ars Technica interview). Explaining afterwards is a gap in the genre. No
source was found for how FFXII's gambits, Dragon Age's tactics or Factorio's circuits show which rule fired, and a
readout of a character's state is not an explanation of why it acted (inference). Depth: `legibility-writeup.txt`,
`game-ui-writeup.txt` 3.

**The designer cannot judge clarity; watch newcomers in small rounds, fix between rounds, and decide in advance when
to stop.** Valve's playtest slides put "what people do, not what they say" first (developer, read in full). Microsoft's
RITE study recruited only players new to the genre, fixed problems between testers, and stopped once several testers in
a row hit no problem (research, read in full). Even so, a run of change-free testers only rules out problems that hit
many of them: after one clean tester, problems hitting most players; after ten, those hitting more than about one in
seven (practitioner, citing the RITE authors). "Five users" holds only as a rule about iterating, not about having
tested enough (research). Depth: `playtesting-writeup.txt` 1, 2, 6.

## 2. Checked against `decisions.md`

Only decisions the research bears on are listed. Unless another file is named, headings are in `decisions.md`; screen
sections are in `design/opening-screen.md`.

### Conflicts

- **"Rewarding at any moment": "Lots of juice" and "Juice is everywhere... nothing touched feels dead."** The stated
  reason, that more response feels better, holds up to medium–high and no further: extreme juice did worse than
  medium, and amplifying the same event lowered players' sense of competence (Kao, research). The decision sets no
  ceiling, and its reference (Leaf Blower Revolution, many things reacting at once) points the wrong way. Tiers already
  exist in practice (the "+1" pop, the level burst, the Camp flourish), but they are not written down, so each new
  effect can only add. The research supports writing a ladder whose tiers follow how much the event matters, each tier
  a fixed size, with a cap and no escalation within a tier. The juice survey (research) adds a second cost: heavy juice
  makes it harder for players to learn which effects matter mechanically.

### Gaps

- **"The editors open simple" (lessons) and the screen doc's "Lessons".** These agree with the strongest onboarding
  findings: taught at first need, on the real controls, one system at a time, skippable, nothing modal. Two gaps:
  - **The lessons never thin out.** The rule lesson re-teaches the editor pattern (pick, save, find the row) that the
    mix lesson has just taught, at the same density (Kalyuga).
  - **Nothing records where a lesson was abandoned.** The code keeps only that a lesson ended (`keepLesson(id)` in
    `ui/lessons.ts`), not which step it was skipped on or where a player waited. That is the very signal Valve
    patches from.

  "Never repeated" is not contradicted: on-demand help did nothing or harm in Andersen's simpler games, and the repeat
  offers on the hands strip already give a player who skipped a way back.
- **"Taught by need, and needed again"**, **"The screen arrives when it means something"** and **"Each new system
  arrives alone"** agree with the evidence and need nothing.
- **"Automation is designed, not clicked"** and the screen doc's **"The Rules tab"**. The `●` on the rule that is on
  goes beyond anything sourced from the genre. Three questions have no answer on screen:
  - why a rule is off ("needs under 3, now 5"),
  - that a rule holds but is outranked,
  - which rules ran while the player was away, and in what order. "Coming back" plays story lines and arrivals, not
    rule history.

  For a player who writes their own rules, "why isn't this one doing anything" is the likeliest confusion (inference).
- **"Idle time pays out mostly in the old"** and the screen doc's **"Coming back"**. Pecorella (developer, slides read
  in full) holds that the return visit is the idle game's reward moment and should grow with the absence. The rate side
  is covered (no cap, full rate). But the unwrap shows new things (features, cards, lines), not what the stores gained,
  so a seven-day return and a one-hour return may feel alike. Story lines do play in full, so only the other arrivals
  fall under the 4 s cap. Untested.
- **"Always something to build toward"** and the Camp bar's next marker agree with the goal-gradient and
  information-gap findings. The gap is the moment after a completion: the next bar starts from zero, which is where
  Kivetz et al. saw effort dip (research, read in full; loyalty cards and song ratings, not games, so applying it here
  is an extrapolation).
- **"Fun, but never vying for attention"**. No streaks, no daily resets and no offline cap agree with the finding on rewards
  promised in advance (Deci) and with player complaints about streak pressure (verbatim, snippet). No decision says what the screen should leave open when
  the player closes it, though that last view is where an information gap would pull them back (inference from
  Loewenstein).
- **Motion and sound** (spread over "Rewarding at any moment", "Silent and glanceable" and the screen doc). The page
  turns animation off when the OS asks for reduced motion (`game.css`, verified). There is no in-game setting, no stated
  limit on flashes, and nothing says sound never carries information alone. Game Accessibility Guidelines ask for all
  three (guideline, read in full).
- **"What can be tapped looks tappable".** This agrees with game-ui finding 1 (plain controls, with the fiction carried
  by words and art). It does not rule out meaning that is reachable only on hover. The only touch-size rule written down
  is 44 px in the condition editor. Nothing says the ledger's red, warm ownership or the dot-versus-glow difference still
  reads without colour (guideline: WCAG 2.5.8, Apple and Android touch guidance, GAG basic).
- **"It is paced for someone who has never seen the game"** and the queue item on teaching the mix, which is
  judged by "a cold tester who doesn't play idle games, never the owner". This is the RITE and Hodent finding applied
  correctly. The gap is that nothing says when testing stops: there is no pass condition fixed before the sessions,
  so one tester's accident can count as a finding, or a lesson is never called finished.

### Agrees, with the evidence behind it

- **"The game never judges, in words"** and **"The game states facts, never a verdict on the mix"**: rewards as
  information (Deci), intents as facts (Slay the Spire, opinion).
- **"What the mods added is built in"**: show the consequence beside the thing and work out the number for the
  player (game-ui 3, opinion and developer).
- **"Shown in the design, not claimed"** (one glow at a time, quiet dots, no pulses for urgency): an always-on
  highlight turns into wallpaper (Factorio forum, verbatim; Friday Facts, developer).
- **"The 2 AM test"** and **"Watching earns nothing extra"**: healthy play went with need satisfaction and did not
  raise hours played (Przybylski et al. 2009, research, abstract only).
- **"Leaving and coming back always pays"**: an idle-game developer reports players confused when a shown unlock
  condition did not match when the content arrived (snippet).

## 3. Proposals to test, ranked

Ranked by how much each serves the current queue (teaching the mix for galaxy.click), then by the strength of the
evidence, then by cost.

1. **A tester protocol: RITE rounds with a stopping rule, read one person at a time.** Change: before the first
   session, write the pass condition (for example, reaches the first built mix and first built rule without help) and
   the stop (three testers in a row pass with no change). Say the observer stays silent. After each tester, fill a
   fixed table from the decision log: time to first tap, the first idle gap over a minute and what the screen showed,
   offers shown against offers taken, last action before leaving. Ask three questions: did you choose what the camp
   did, did it work, would you come back without being told? Ask one more about where they left off: "what were you
   about to do?". Report the result as "no problem hitting more than about half of testers", never "verified". Survey
   ratings at this sample size decide nothing. Test: the protocol is the test; it succeeds if it ends the teach-the-mix
   item with a stated result. Fits into: no system; it reads the decision log (Saves) and tester notes (Feedback, under
   Logs, job runs, retention) and judges the queue item on teaching the mix.
2. **Record the step each lesson is skipped on, and the step it waits longest on.** Change: one field per lesson
   end, written to the decision log or the page's telemetry. Test: across a round of testers, a skip that clusters on
   one step, or on a reading step, marks that step to cut or to replace with a visible result (Valve's playtests;
   players skip text). This also
   tells proposal 6 which steps to drop. Fits into: Lessons (`systems.md`), recorded through Logs, job runs, retention.
3. **Write the feedback ladder, with a ceiling, and give background completions a tier of their own.** Change: tiers
   by event (an ordinary completion by the mix or a rule, a completion from a tap, a first of its kind, a level-up, a
   big beat), a fixed effect per tier, no escalation within a tier. Completions by the mix sit one step below a tap,
   so tapping stays special and watching is not flat. Test: a cold tester watches a long stretch with today's effects
   and with every tier one step down; ask which they would rather watch and whether either felt busy. With the mix
   running and no taps, ask after ten seconds what changed. Fits into: Feedback (`systems.md`), whose effects are
   already data and tokens in `game.css`.
4. **A gapped cold session.** Change: two or three cold testers each play two short sittings a few hours apart, the
   second opened from the return screen (the shape Kolibri used for Idle Miner Tycoon, developer). Test: from the
   decision log and the recording, do the repeat offers appear and get taken after a return, and what does the tester
   do first? This is the only instrument proposed here that sees a return before the public build. Fits into: no
   system; it extends proposal 1 and feeds the queue item "The night visits go quiet" with real returns.
5. **Show a rule's reason in the Rules tab, and what ran while away.** Change: a quiet line under a rule that is off,
   in the ledger's grammar (`needs under 3 dry wood · now 5`, `outranked by {rule}`). From the strip's `until …`
   button, a short list of the last rule starts and let-gos, each with the store level at the time. Test: give a tester
   a rule that never fires and time how long they take to find out why. Then show a returning player the screen with
   and without the list and ask why this mix is running. Fits into: Standing orders and the queue (the engine already
   knows which conditions hold), and Chronicle and unwrap for the history.
6. **Thin out the rule lesson after the mix lesson.** Change: when the mix lesson was completed, the rule lesson drops
   the steps that repeat the editor pattern (the save step, the "where it lives" reading step) and keeps the when/do
   pair. Test: inside proposal 1's rounds, not by rate (too few testers to count), by whether players who see the
   shorter version still build a working rule unaided. Fits into: Lessons (`game/lessons.ts`; a lesson's steps are
   data).
7. **One motion and sound rule, plus a mechanical phone check.** Change: in the decision, an in-game motion toggle
   beside the OS preference already honoured, a flash cap, "sound never carries information alone", "nothing is
   reachable only by hover", and a minimum hit area for every control (44 CSS px on the short side, or WCAG's 24 px
   spacing test). Test: render the phone at 390×844 in a headless container under emulated reduced motion, then:
   - check every effect still says what happened,
   - measure every clickable's box,
   - screenshot in greyscale,
   - load the pinned stage with the address bar shown and hidden, and with the condition editor's keyboard open.

   List the failures before designing anything. Fits into: Feedback (the calm form of each effect) and Page shell. The
   size and greyscale checks sit beside `app/tests/test_client_contrast.py`.
8. **An absence ladder in the simulator, then start each new marker partly filled.** Change: none at first. Run returns
   after 1 h, 8 h, 24 h, 3 days and 7 days and count the milestone-class arrivals each unwrap holds. Check that longer
   absences hold a recognisably bigger moment, and that the 4 s cap does not flatten the non-story arrivals. Only if the
   ladder is flat, start a new Camp or feature marker with the real surplus carried over (never invented progress).
   Test: the simulator's per-absence counters. Fits into: Simulator, and Chronicle and unwrap if the unwrap changes.

**Dropped, with what already covers them:**
- A recognition check ("pick the lines you saw from real and invented ones"): issue #26, "How the story reaches
  the eyes".
- Keeping a skipped lesson's offer reachable, and a new card saying it can join the mix (`teach-automation.md`): the
  repeat offers on the hands strip, under the queue item on teaching the mix.
- A narrow causal overlay, one question per lens: its own writeup says to build it only if proposal 5 proves not
  enough.
- A late-game screen budget (which regions stay on screen and what gets demoted): real, but nothing is testable until
  surfaces past the opening exist; raise it when the town or the map is designed.

## 4. What the evidence can't say

- **What brings a player back on days 2 to 7 without notifications or daily rewards.** No study measures it. What
  exists is theory (information gaps, goal gradient, need satisfaction) and one designer's testimony (Pecorella).
- **How often something new should arrive.** No source gives "a new thing every N minutes" for idle or any other games.
  The Idle Awakening cadence in `decisions.md` is a design choice, judged on real players' runs, and should stay
  labelled that way.
- **How idle games design feedback and screen growth.** Developer sources on feedback were not found for Cookie
  Clicker, Melvor Idle, Kittens Game or Antimatter Dimensions, and none were found on how an idle game's screen grows
  as panels unlock.
- **How a rule-list game shows which rule fired, or why one did not.** There is no developer source for FFXII, Dragon
  Age or Factorio circuits.
- **Whether NPC relationships stand in for relatedness** in a single-player game. Relatedness was measured only in
  multiplayer play.
- **How playtesting works for a solo developer across several sessions of an idle game.** No account of one was
  found, and nothing compares RITE with ordinary rapid testing.
- **Primary talks**, read only through summaries: Jonasson & Purho, Nijman, Swink, Schell, Hodent's book, the Into the
  Breach and RimWorld GDC talks. Claims from them carry the summary's label, not the speaker's.
