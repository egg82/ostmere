# What makes the decisions left to the player fun

The direction of 2026-11-07: bring the fun back and make this a game rather than a glorified walking simulator.
Steering this note: games like Factorio are fun with no way to fail, and many idle games have no fail state that
means starting over. The design has just stopped deciding for the
player (`design/choice-not-protection.md`). This note asks what the decisions that remain need to be fun, using
automation games and idle games with no fail state first. Mechanics only: nothing here names or paraphrases content.

Sources: `fun-from-choice/notes.jsonl`, one row per source with how much was read and its label. Labels follow the
`game-design` skill: **developer** (makers on their own game), **research** (a study), **practitioner**, **verbatim**,
**opinion**, **snippet**, **inference**. The mapping to Ostmere's systems is inference throughout: no source studied a
game shaped like this one.

## Findings

The general findings, with their sources and labels, are in the `game-design` skill:

- The bottleneck loop (find the slowest part, fix it, repeat), why a solve button removes the game, not punishing
  mistakes, and the late-game "nothing to decide" turning back when a new mechanic changes the old answer:
  `references/motivation.md`, "Decisions matter without a fail state" and "Late-game 'nothing to decide' turns back
  when a new mechanic changes the old answer". That section also holds the rule this note's proposals rest on: the
  cadence of decisions follows how often the binding constraint moves, and no source gives a number.
- Options that differ in what they give, "which upgrade next" being close to solved, opt-in constraint runs, dominance
  prevented by interacting layers, and automation as the problem or the decision: `references/genres/idle.md`,
  "Options must differ in what they give, not just how much" and "Automation".
- A predictable number then a visible result, and watching one's own machine: `references/legibility.md`.

Findings the skill does not hold:

- Factorio's team names the fixing as the fun (developer, Friday Facts #300 and #309, the Kovařík transcript).
  Kozelek: "the mini-game of trying to fit the production lines into limited, usually uneven area"; Norvaišas:
  "finding a better or more compact way to build something"; Mason: "the ability the game has to induce a state of
  flow". Oxyd was drawn in because "focusing on my 'base' was exactly what I was supposed to do" rather than fighting.
  Nothing says the bottleneck is a fail state; it is a visible target the player chose to care about.
- The fun needs the system to be calculable: "Everything can be calculated to the last item"; "it's a very precise
  game" (developer, Twinsen, Friday Facts #309; personal opinions the post says will not ship). A player can predict a
  fix, and a skip-ahead is likened to a "level up button" in an RPG.
- Makers of games with no fail state say so on purpose. Gunst, Satisfactory: "You're in control. You can stop at any
  time. You can make mistakes and no one will shout at you." Posila, Factorio, likes that he "alone owns any
  failures": a mistake costs the player's own time and layout, and the player decides to redo it (developer,
  Satisfactory interview, Heise, read in full). That fits Ostmere's fight rule ("a fight can
  cost what you put into it, never what you've banked", `decisions.md`:705).
- Idle designers (research, Spiel et al., CHI PLAY 2019, six designers, indie-weighted) describe the genre as
  exploration of a system with "little consequences of failure". Lantz: the world "invites you to think and to analyse
  and understand the systems ... in order to optimise them"; on Kittens Game, new systems whose fit with the existing
  economy "should change my decision making" (verbatim). Guidelines: intertwine system variables so different decisions
  give different states; let players disengage with no substantial consequence; let a sub-optimal allocation recover
  through time; show a change's effect without making it. Buergi 2024 (secondary) adds the cost: when almost any action
  boosts production, choice carries little weight.
- Idle Awakening's reviewer praises action lists that "mix and match" and faults "no real sense of what to progress
  aside from aiming at the next unlock" and picks that are "one guild at a time ... a handful of modest guild
  bonuses". An Increlution player: "approaching each wall has some variance in what you prioritize and when". Idle
  Loops' reviewer: saved movelists "you can hotswap between" (opinion, single sources).
- Spiel's designers want an ending that says "it's okay, you can stop playing now". Opus Magnum's leaderboard
  histogram was only a snippet and needs a population Ostmere does not have; a personal best against one's own
  earlier mixes is the single-player form (inference).

Not found: Orb of Creation (no developer words, so the owner's reference stays anchored in `idle-awakening/notes.md`, our
own play); Shapez (fan pages only); Satisfactory on optimization puzzles; whether any of this raises retention for idle
games with no notifications. The skill's "What the evidence cannot say" sections hold the rest of the gaps.

## Mapping onto Ostmere

### The belt that backs up

Factorio's backed-up belt is a visible place where the system's flow is blocked, with the cause beside it. In Ostmere
the same things already exist as numbers in the ledger (`decisions.md`:34-35 "Ledger", 746):
- **A store that falls**: "Candles −4/h · 7 h left", red when no rule covers it. It is the starved belt.
- **A store at its cap**: output with nowhere to go, so work wasted. It is the full belt. Today a default cap rule
  hides it; `choice-not-protection.md` row 30 (decided) removes the default, so the full store becomes visible.
- **A card whose input is dry**: its share is handed to the rest of the mix (`decisions.md`:516-520). It is the idle
  machine.
- **A goal's arrival day**: the throughput figure, and the thing every fix moves.

What Ostmere lacks is the moving constraint: after a fix, the next binding line is not named. The player sees the
red line fixed and has to work out what now limits the goal. That is the loop Kovařík describes as the fun.

### Proposals, ranked by fun per effort

1. **Name the binding line for each open goal, as a fact.** Extends: the ledger and the goal-time rows planned in
   `worth-a-change.md` (one what-if fork per edit). Each open goal reads "arrives day N, limited by Rope, 2/h"; after
   an edit the editor shows the goal moving and the limit moving. Effort: low, since the fork exists and the
   limiter is the store that gates the goal's date. Fun: this is the Factorio loop. Fits `decisions.md`:335 only if
   it names the line and its rate and never says what to do. It does not reinstate the dropped "better-option" mark
   (`decisions.md`:757), which computed a best mix and pointed at it. Depends on the defaults leaving ordinary caps
   and starved inputs to the player (`choice-not-protection.md` rows 4, 30, 45); while a default hides them there is
   no belt to back up.

2. **Prestige picks that change what a card or store does, exclusive within a tier.** Extends: prestige nodes
   (`design/prestige-phases.md`). The Gnorp rule (change behaviour, combine, never "buy all") plus the decided
   two-thirds track sizing and respec at the rank's progress (settled Q2) already give exclusivity. Effort: content
   only. Conflict: none; `decisions.md`:592 holds if each pick states its effect. Conflicts with the current
   `prestige-phases.md`:143-146 (picks only order the nodes) only until row 15 lands.

3. **A dominance readout in the simulator, not in the game.** Extends: the pacing simulator (open-work item 1, "what a
   re-mix is worth"). Per phase, each source's share of income (Pecorella) and whether one saved-mix shape wins from
   every starting state. A shape that always wins is a bug in the choice, found in a number. Effort: low. Fun: a guard,
   so proposals 1, 2, 4 stay choices.

4. **Compare saved mixes on separate numbers, with a personal best.** Extends: the Mixes list and the editor's before
   and after block. Per mix: goal arrival days, each store's net rate, hours it runs, never one score
   (Opus Magnum's three metrics). A kept "best so far" per goal comes from the player's own earlier mixes, with the
   mix that set it. Effort: medium. Conflict: `decisions.md`:335 if worded as "better"; keep it "earlier".

5. **Fights as a loadout choice with a telegraphed forecast.** Extends: combat and standing orders ("danger is readable
   before you commit", `decisions.md`:705-707). Show likely cost before committing as numbers (Into the Breach, developer, Justin Ma, Road to the IGF 2018; from
   the skill's evidence), let the orders' retreat or push-through setting be the FFXII-style list the player edits.
   Effort: medium. Consistent with "preparation decides" and "chance shows".

6. **A season that moves the binding line.** Extends: seasons and chores (`decisions.md`:1005-1024). A season brings a
   card or an input that makes a different store the limit, so the mix worth running changes, in the Space Age manner
   of "new mechanics, not repeats". Effort: content. Conflict check: `decisions.md`:1013 says a season "adds and
   raises, never lowers", so it must add a demand rather than cut a rate. That is a constraint on the content.

7. **Opt-in constraint runs.** Extends: prestige and seasons. A modified stretch entered at will (one input
   withheld, one share capped), run through the same mix and rules, paid in something that is not automation.
   Effort: high, balance-heavy. Conflicts: Q3 ("automation is not earned") rules out Antimatter Dimensions' reward of
   improved autobuyers; pay in story or a prestige-node rank instead. `decisions.md`:48-58 means a run must continue
   while away and never end in idleness, and it must be always available (`decisions.md`:1015, "nothing is
   missable"). Recommend only after 1 to 4 show the base loop works.

8. **A scarce slot in the camp or town** (a limited number of racks or hands, so builds compete): the "fit lines into
   limited area" fun. Effort: medium, but it conflicts with `decisions.md`:659 ("every choice only adds ... nothing
   needs tearing down and re-placing") and with the Township verdict. Do not build without the owner's say; the closer
   Ostmere version is proposal 6.

### Verdict

Build 1, 2 and 3 together. The research agrees on one claim across sources as different as Factorio's team, Satisfactory's
makers and idle-game designers: the fun is the player's own redesign against a constraint they can see, with the
cost of a mistake falling on their own time. Ostmere has the redesign (the mix, free to change) and the numbers (the
ledger); what it lacks is the constraint that moves, which proposal 1 supplies. Proposals 7 and 8 are the two that
add machinery against recorded decisions, and both should wait.

### The test that would show this wrong

A cold player who has met the first mix and rule plays two days. Observe, from the decision log and not from what
they say: do they open the mix editor after a goal lands, and do they change a share toward the named binding line?
If they open it and change nothing, the readout is noise. If they never open it, the constraint is not moving often
enough (`worth-a-change.md`'s readout measures this).
