# Choice, not protection

This note audits the design's attention and pacing rules against the direction of 2026-11-07 below. Mechanics only: no
content, card or beat specifics. Line numbers are `origin/main` at `40c64452`; where branch `offers-step-back` has
already rewritten a line, the table says so.

## The principle

A player tapping by hand at 2 AM is not being made to babysit: either they don't know they can automate it, or they
choose not to. The first is a teaching problem and the second is a deliberate choice. The game gives every player the
chance not to need 2 AM babysitting and guides them to the tools for it, but never *prevents* babysitting for whoever
wants it.

Many of the babysitting and 2 AM checks rested on preventing the player from making bad choices, and on simulating the
worst possible player, which watered the game down to the lowest common denominator. The buttons that do everything
for the player came from the same place: catering to a player who refuses to play and decide for themselves strips the
game out of the game.

Each rule falls into one of these classes:

- **A, guarantee.** It makes sure a player who uses the tools the game teaches never needs to babysit, or it keeps
  the game legible and fair. Keep it.
- **B, protection.** It stops a player choosing badly, removes a choice, or caps a reward so that a neglectful player
  isn't behind. Redesign it.
- **C, worst-player check.** A check or band is tuned to the lazy, neglectful or no-tools route instead of a typical
  player who uses the tools. Redesign it.
- **D, decides for the player.** It makes a decision the player could make: an automatic spend or switch, a default
  order, a suggested pick, a one-tap fix, a verdict. D is a column alongside the class, because a D can also be a
  guarantee (some decisions no tool could make in advance).

The model for every rewrite is what changed today on `offers-step-back` (`f16f6c9b`, `d5bd4324`, `87ce60a8`). The
2 AM test now compares players "given the same setup: the rules and mixes the game has taught". Upkeep that a rule can
answer is left to the player, marked by a hint and never installed. No offer builds a mix or a rule once the lessons
are done.

## Every rule

`dec` is `docs/decisions.md`; `pp` is `docs/design/prestige-phases.md`; `wac` is `docs/design/worth-a-change.md`.

| # | Rule | Where | Class | D | What it costs the game | Proposed change |
|---|---|---|---|---|---|---|
| 1 | 2 AM test, same setup | dec:48 (rewritten on `offers-step-back`) | A | | nothing; it is the corrected model | keep |
| 2 | No offline cap, full rate | dec:52 | A | | nothing; the carry window (13) is its one stated exception | keep |
| 3 | Covering an absence is never an upgrade | dec:54 | A | | automation can't be earned as progression | keep; automation itself is never gated behind progress either (Q3) |
| 4 | Routine spends are automatic | dec:56 | B | D | every routine spend is a decision taken away; nothing in the engine implements it beyond the queue and rules | "Routine spends can be automated": the queue's When ready and rules do it once the player sets them |
| 5 | No daily resets | dec:57 | A | | nothing | keep |
| 6 | Nothing finishes into idleness | dec:58 | A | (D) | "crops replant" is a default; the rest runs by the player's rules | keep; continuing work runs by the player's rules, the queue or their own mix, never a default the game picks |
| 7 | Watching earns nothing extra | dec:128 | A | | nothing | keep |
| 8 | Chance decides how nice, never how far | dec:150; `docs/systems.md`:61 | A | | flatter risk, but this is taste, not a protection | keep |
| 9 | The game never judges | dec:335 | A | | nothing; it is the anti-D rule | keep |
| 10 | Idle time pays mostly in the old; one or two unlocks a day away | dec:509; `app/tests/dayone/checks.py`, `absences` | taste | | nothing | keep as a design aim; what each absence opens is printed, never held to a number (`sim-invariants.md`) |
| 11 | Dry store hands its share to the rest of the mix | dec:516; engine `DESIGN.txt`:35 | A | D | small: where the freed share goes | keep: a store can't go negative, and the share goes to the player's own mix, the answer that decides least |
| 12 | A greyed mix falls through to the queue and rules | dec:740 | A | | nothing; it is the player's own plan | keep |
| 13 | Carry window; an ordinary absence loses no prestige XP | dec:566; pp:9-14 | A | | a cap on XP about two days past a top | keep: the click is by hand, so no tool can cover it; the window is that tool's stand-in |
| 14 | A phase takes at least 4x an ordinary absence | pp:15, pp:224 | A | | the fastest methods can't be very fast | keep while 13 stands; it exists only because of 13 |
| 15 | Prestige tracks sized so every node completes on typical; a pick only orders them | pp:143-146 | B | | picks have no lasting effect; every typical skill ends the same | size tracks so a typical game completes about two thirds; picks shape the run (Q2) |
| 16 | No respec, because rearranging before each absence is busywork | pp:246-248 | B | | removes a choice for fear of the optimizer; under the same-setup test a respec is setup, not attention | a respec at a real cost (the rank's progress or a store), so it is a rare decision (Q2) |
| 17 | The prestige click is only by hand, never queued | pp:253 | A | anti-D | nothing; it keeps the decision with the player | keep |
| 18 | No bonus depends on remembering a hand action | dec:588 | A | | nothing; a rule can do it | keep |
| 19 | No blind permanent choices | dec:592 | A | | nothing; legibility | keep |
| 20 | A building falls only to the story, never to failed defences | dec:584 | B | | walls and guards have no stake for buildings | failed defences damage (a repair cost, a slowed building), never destroy; the fall stays a story beat |
| 21 | Nothing compounds into collapse; nothing is lost because you were away | dec:610 | A | | nothing; anti-spiral, a matter of taste | keep |
| 22 | A declined or ignored quest never costs progress | dec:630 | B | | emergent quests become flavour you can skip at no cost | declining has a real, bounded cost, as an undone chore does (dec:1019): light tier, a store, a slower arrival, never a spiral |
| 23 | Nobody dies because you weren't watching | dec:635 | A | | nothing | keep |
| 24 | A broken group's deaths are fixed on arrival, never the player's fault | dec:636 | B | | healing can't change an outcome | low priority: let preparation avert a few, light tier only |
| 25 | Your own death: only from a chosen fight or the story, costs no progress | dec:646 | A | | nothing | keep |
| 26 | Combat has fangs; preparation decides; threats ramp by region | dec:699, 705, 711 | A | | nothing; already choice with consequence | keep; it is the model for 20 and 22 |
| 27 | A raided line slows; food drives growth; nobody starves | dec:670, 716 | A | | nothing; anti-spiral | keep |
| 28 | Every choice only adds; the town decides where to build | dec:659, 673 | A | (D) | placement is decided for you, by choice (Township was fiddly) | keep |
| 29 | A saved mix with a better option is marked, with the gain | dec:757; wac:35 (decided, not built) | | D | the game computes the best mix and points at it, which is the optimise button `wac` rejects | drop the mark; the editors' goal-time rows show what a change does once the player opens one |
| 30 | Hitting a cap is an order's job; new players start with default orders | dec:773 (upkeep half rewritten on `offers-step-back`) | B | D | the first cap decision is made before the player meets it | the cap rule is a lesson's subject and a hint on the full line, never pre-installed (Q1) |
| 31 | Length band: sharp about 10 weeks, lazy about 14, held on neglectful routes | dec:834-838 | C | | content is sized so neglect stays near sharp, which compresses what decisions are worth | the band holds typical; sharp has only clock floors; lazy and neglectful are reported, never a floor (as `day-three-plan.md`:45 already does) |
| 32 | A sharp setup never reaches a beat weeks early; save-time floors | dec:887; `days-four-to-seven-plan.md`:24, 50; week plans' floors | B | | the optimizer's reward is capped at "arrives with more" | keep floors the story's clock gives (a night, a season); let a sharp route lead by days elsewhere (Q4) |
| 33 | Every bad state has a cure in reach; costs small and says what | dec:899, 903 | A | | nothing; legibility, no spiral | keep |
| 34 | A cure or a glowing step cuts in on the plan | dec:918 and above | A | | nothing; the player's tap wins | keep |
| 35 | Leaving and coming back always pays | dec:894 | A | | nothing | keep |
| 36 | No calendar day is dead | dec:941; `app/tests/weekone/test_weekone_routes.py`:68 | A | | nothing; held on typical, sharp and whenever | keep |
| 37 | Day one's checks run on `by_hand` (no rules, no queue) every push and on `lazy` nightly | `app/tests/dayone/routes.py`:45, 50; `verdicts.py` | C | | content is tuned so a player who writes no rules meets every per-visit, absence and goals bar | hold typical, whenever and sharp; report `by_hand` and `lazy`, plus one check that they land measurably behind (`human_flags.classify` already wants that gap) |
| 38 | Day two holds per-visit misses for `by_hand` and `lazy` | `app/tests/daytwo/verdicts.py`:61-66 | C | | the same, as held debt | delete those entries once 37 lands; those routes stop being checked |
| 39 | Babysitter floors; routes lag the babysitter only by their gaps | `app/tests/dayone/bands.py`, `b3_relative`; `daytwo/checks.py`, `b4_relative` | A (the lag); taste (the floors) | | nothing | keep the lag bound on players who use the tools; the floors go, and each beat's day is printed beside its target day (`sim-invariants.md`) |
| 40 | Every verb has an order | `docs/systems.md`:53 | A | | nothing; it is what makes the 2 AM guarantee possible | keep |
| 41 | Cap loss at most half over 8 h and 24 h, on typical | `banked-time-plan.md`:28; `app/tests/dayone/capcheck.py` | A | | nothing; measured on typical with its sinks | keep |
| 42 | A rate-raising step is shown queueable before it is due | `app/tests/dayone/checks.py`:259 | A | | nothing; tool availability | keep |
| 43 | Each chore comes with a suggested rule | dec:1019; wac:59 | B | D | the chore's answer is offered ready-made, against "no offer builds a rule" | the chore arrives with its problem and a hint mark; the rule is the player's to write |
| 44 | Nothing is missable in a season | dec:1015 | A | | nothing; no schedule to keep | keep |
| 45 | Every re-mix reason (cap, dry store, starved input) is automated and stays so | wac:11 | B | D | removes the reasons to open the mix editor, so `wac` must invent new ones | caps and starved inputs are answered by rules the player writes; only the dry handover (11) stays engine mechanics |
| 46 | Upkeep answered by offers and defaults, so ignoring it is never wasteful | wac:62, 127 (127 reverted on `offers-step-back`; 62 remains) | C | D | ignoring upkeep is made free | ignoring upkeep costs what it costs, shown in the ledger as a fact |
| 47 | Defaults never wasteful; keeper stays in the length band; its gap to tuner is goals, never beats | wac:169-170 | C | | content must carry a player who never touches a mix | keeper is reported; its gap may include beats, inside the band's lazy end |
| 48 | Ceiling of about one worthwhile change per ordinary absence | wac:198 | B | | caps the opportunities a keen player gets, to spare one who feels compelled | drop the ceiling and the floor; changes per absence are a readout (`sim-invariants.md`) |
| 49 | An arrival's first task is an installed rule | `day-two-plan.md`:13, 31; engine `DESIGN.txt` "TOWNSFOLK" | A | D | small | keep: no rule could name a person before they existed, so an idle arrival would fail a tool user; it is an ordinary, editable rule |
| 50 | A townsperson's card can't be tapped by hand | engine `DESIGN.txt`:919 | B | | removes the choice to micromanage | low priority: a hand tap on a ruled lane runs once, then the rules resume |
| 51 | Teaching cues: idle nudge, hint dots, Show me lessons, first-mix lesson, the switch-mix lesson | `app/client/src/ui/nudge.ts`, `game/teach.ts`, `game/hints.ts`, `ui/chipoffer.ts` (`offers-step-back`) | A | (D) | the switch-mix lesson names one saved mix, once per save | keep: they point and never build; the nudge stops at the first mix |

**Counts.** A: 32. B: 12. C: 5. Row 10 is taste (`sim-invariants.md`, which sorted the simulator's checks after this
audit). Row 29 is D with no other class. D is flagged on 11 rows. Six of them change
(4, 29, 30, 43, 45, 46) and five stay as guarantees or as taste (6, 11, 28, 49, 51).

## The top changes, ranked by how much they would un-water the game

All six are decided; their build order is issue #37.

1. **Retire "defaults are never wasteful" (rows 4, 30, 45, 46, 47).** Caps, starved inputs and routine spends become
   things the player answers with rules the game taught. This brings back the reason mixes and rules exist, which
   `wac` currently has to invent through goals alone. *Cost:* a newcomer who never writes a rule loses output to caps.
   The lessons and hint marks are the answer to that, and the galaxy reviewer's 91 hand taps are the case to retest
   with a cold player.
2. **Stop tuning content to the no-tools and neglectful routes (31, 37, 38, 47).** Hold typical, whenever and sharp.
   Report `by_hand`, `lazy` and keeper, and add one check that they land measurably behind. *Cost:* no simulated
   floor on how slow neglect gets. What bounds it is "never blocked, never a spiral" (rows 21, 27, 33), which already
   holds structurally.
3. **Prestige picks that matter (15, 16).** Tracks a typical game only partly completes, plus a respec that costs
   something. Two players' skills then differ, and multiple saves give a reason to pick differently. *Cost:* a pick
   can leave a node unfinished. "No blind permanent choices" stays satisfied because the respec exists and each
   node states its effect before the pick.
4. **Real costs for ignoring chores and quests, with no suggested rule (22, 43).** The chores section already says
   "either way, it's a choice". Quests and chore rules are brought into line with it. *Cost:* content has to write a
   bounded cost for each, with no spiral.
5. **Drop the better-option mark and the worthwhile-change ceiling (29, 48).** One is a verdict in all but words; the
   other limits opportunity to protect a compulsive player. *Cost:* fewer pointers. The editors' goal-time rows carry
   the information when the player looks.
6. **Defences with stakes for buildings (20).** Failed defences damage and never destroy. *Cost:* repair content, and
   a building state the page must show.

## What stays, and why

The guarantees all make the same promise: **a player who uses the tools never has to watch, and can see everything
they need to choose well.** That covers the same-setup 2 AM test with its instrument (every verb has an order, the
the lag bound on tool users, the queueable check), no offline cap, no daily resets, nothing finishing into idleness, leaving
always paying, the carry window while the click has no tool, no blind permanent choices, a cure in reach, and facts
never verdicts. The anti-spiral and tone rules also stay: chance never moves progress, no deaths from
inattention, nothing compounds into collapse, combat that costs only what you put in. These are taste, not
protection. None of them stops a player choosing badly; they stop the game punishing a player for not watching.

Three D rows stay because no tool could have made the decision in advance, or because they decide the least:
handing a dry store's share to the rest of the mix (11), an arrival's first task (49), and teaching cues that point
and never build (51).

## Settled

The six top changes stand, and:

- **Q1. No ready-made cap rule in a new save.** The first full store gets the hint dot, and the cap rule is a lesson's
  subject. A player who skips it loses only the overflow, which the ledger shows.
- **Q2. Prestige tracks sized at about two thirds of what a typical game reaches,** with a respec that costs the
  rank's progress.
- **Q3. Automation is not earned** (a correction to the recommendation of "earned, modestly"). The player sets things up as needed
  rather than sitting and waiting for an unlock condition (such as sleep when tired), unless it ties into the story. Every rule condition and kind is available once the thing it watches exists
  in the game; one about something the story introduces arrives with it; nothing is held back as a reward or behind
  a progress gate. Covering an ordinary absence stays complete from the start.
- **Q4. A sharp player may lead the story's usual pace by up to a few days per week of play.** Beats held by the
  calendar or a night stay where they are.
