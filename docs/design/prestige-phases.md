# Prestige as phases

This note designs the decision "Prestige is the player's click"
(`docs/decisions.md`). Mechanics only: no skill, card or content numbers. The measurements behind every shape here were
taken by hand and are kept outside the repo.

## What it proposes

- **A skill at its top waits there for the click, and its XP carries over.** XP keeps accruing for up to the
  carry window (about two days) past the top. The click spends it in the new phase, so a player who returns within an
  ordinary absence ends where an instant clicker would. Past the window XP stops, the fair hit for a long absence.
  **The carry never reaches the next phase's top**, so a long absence leaves one click waiting, never a stack of them.
- **The click is only ever by hand.** It cannot be queued or written as a rule: a click set ahead and landed while
  the player is away is an auto-prestige with an extra step. The carry window is what keeps the 2 AM test level.
- **Even the fastest method in the game** takes about four times the ordinary-absence bar to go from a phase's start
  to its top, so the two-day window binds long before the one-phase cap. The cap is the guarantee if content changes.
- **A phase is the camp's held level, applied to XP.** XP climbs on one segment. The skill is held at its phase's top
  until the click lifts it, and the engine's within-phase level counts from 1 again. The player never sees that level
  or the word "phase": the page shows one level, counted across phases, that never falls. Nothing the skill earned is
  taken back.
- **Each click puts one rank into a node.** The menu offers two or three unfinished nodes, each acting on the web
  beyond the skill. Ranks are equal and add up, a full node leaves the menu, and the finite track bounds the total.
- **The loop grows steadily rather than spiralling**, because no node or level makes levels come sooner. The game
  already has a feedback path from goods to XP: goods unlock a skill's faster method. That path is capped by the
  fastest method's XP rate.
- **Breadth from the web is a rate, not a wall.** A one-track mix never stalls. It climbs on its skill's base method,
  which takes nothing, at a fraction of the rate that methods fed by other skills give.

## What was measured

Typical and sharp routes, seed 0, through to the edge of today's played content (about two weeks of game time), plus
a one-card mix at a full share, left alone for seven days from that point. Exact figures are in the scratch file.

| Question | Answer |
|---|---|
| Phase start to top, one card at a full share, the fastest card in the game | about 4x an ordinary absence; the slowest skills take years |
| Phase start to top, the other skills' best cards | 2.5x to several hundred times the fastest |
| When the first skill tops out on the routes | not by the edge of today's content. Inferred: the first two skills in weeks 7–11 of a typical game, the rest never |
| A one-track mix left a week | the base method climbs to the top uncontested; every method taking another skill's making stalls within half a day |
| Do chips and orders slow a focused mix? | about 1% |

Two findings change the design:
1. **Today's top comes too late to reach.** New content stops at day fifteen, and the first top lands weeks after
   that. Where a phase's top sits is settled below.
2. **Skills' XP rates differ by orders of magnitude.** "Every skill is paced to one shared target" does not hold yet,
   so on one shared curve only the first two skills would ever prestige.

## Fit pass

It is an instance of things the engine already does, so it adds no system.

| Part | Extends | How |
|---|---|---|
| The phase's top | Engine: "XP is a segment capped at the curve's last threshold"; the camp's held levels (`DESIGN.txt`, "THE CAMP") | The XP cap becomes the current phase's top. The click lifts it, as a card's finish lifts a held camp level |
| Phase levels | Pacing curve (one curve for every skill) | Every phase reads the same curve from level 1. Its level triggers count levels across phases, so a released trigger stays true |
| A node's ranks | Modifiers | Entries derived from the skill's picks wherever the stack is read, never stored, like `heldentries.py`. That makes an undo exact |
| The click | Commands | `Prestige(skill, node)` is an ordinary verb, but the one verb with no order (below) |
| A move | Commands; the carry's "the clock is the phase" | `MovePick(skill, node, to)`, by hand like the click. Its cost is a due phase stored on the parked rank, settled by the click, not a second clock |
| The carry | XP, which is already one currency on one curve | XP past the top is ordinary XP whose level waits for the click. Nothing is replayed at another rate |
| Where a stalled share goes | The dry-store rule (`spent.py`) | Unchanged: it already moves a stalled method's share on |
| "Tops out in…" | Forecast | One more forecast kind, alongside the level-ups it already lists |

Pattern: **Type Object** for nodes (data, not classes) and **Command** for the click. Nystrom's *Game Loop* catch-up
already covers an absence: the carry is the same accrual with the level held, not a second clock.

## The design

### The click and the menu

- The first time a skill reaches its phase's top, the skill row grows a **Push past** control (the engine and this note
  still say prestige; the player's word says what the skill does, pushes past its limit, and promises no reset). That
  control's lesson
  note sits on it at that moment and nowhere earlier ("a note appears with the thing that proves it").
- The sheet shows the menu: two or three unfinished nodes, each with its rank ("2/5") and the rate it changes as
  before and after. It also shows what the new phase's first named level pays.
- **The menu is fixed from the phase's start, with no draw**, so the player can see the coming choice all phase and
  think about it. "Chance decides how nice, never how far."
- One button, **Push past**, live only once the skill is at its top. The sheet says what the click does in the
  levels the player sees: the top lifts from one level to another (22 to 43), and the carried XP takes the skill to a
  level ("takes it to level 28", the current level when nothing has carried). After the click it says the level the
  skill stands at, beside Undo.

### Phases

- XP keeps climbing on one segment. Phase *n*'s top is *n* copies of the curve up to the chosen top level. At the top,
  the shown level stops and the skill waits; XP keeps accruing for the carry window, then stops.
- The click lifts the cap by one more phase. The row's level is `level_counted` (`phases.level_counted`): the level
  never falls at a click, and with no carried XP it reads the same as before it. A level condition reads the same
  number, so the level a card's need row or a find's cue names is the one the row shows.
- **Nothing is taken back.** Unlocks only grow. The level pays already landed stay in the stack, so the skill's
  methods and work speeds stay. A saved mix's rates never drop at the click, so no ledger line turns red because of it.
- Each level of a new phase pays something, as in phase 1 ("A level is a thing"). Its work-speed pays are **adds**,
  not compounding multipliers (see "The loop"). Every third level pays a find, and a later phase's find is the
  skill's staple, never a story good: a phase lands at a different story moment for each player, so a find written
  for a story moment goes stale. It gives a store that a card which stays available takes in (an uncapped card no
  outcome retires; one-off cards and standing actions do not count, and the loader refuses any other store), in an
  amount that grows by a little each phase. Its line says the skill is getting better, drawn from a small pool per
  skill that rotates by the number of finds paid, so none comes twice running. Phases that shipped the older finds
  keep them under their released ids, gated out of reach, since a released outcome cannot change.
- The phase's first levels come in minutes, which is the cheap, visible first win at its start. Time per level never
  shrinks within a phase.

### What the page shows

| Moment | Shown |
|---|---|
| A skill whose top falls inside the forecast's horizon | "tops out in 3 h 10 m" on the row, from the forecast, so it comes true. Further out it shows nothing: a straight-line guess past the horizon could be wrong once an order switches the mix, and the carry window means nothing is lost by not knowing |
| At the top, inside the carry window | a full bar marked "at its top", the Push past control, and the carried XP as levels waiting ("+6 levels waiting"). The level beside the name is the counted one, and it stays at the top's level until the click. The method keeps running and making its goods |
| At the top, past the carry window | the same, with the waiting count stopped. Never a count of XP missed: time away shows what got done |
| Return after topping out while away | the unwrap line "reached its top" at its time; the click is the player's first act on return |
| The prestige sheet | the top lifting from one level to another, the level the carried XP takes the skill to, and each node's rate before and after; what the pick does, never a verdict on it |

### The idle math

Player **P** clicks the instant the skill tops out. Player **Q** returns *d* hours after it topped out. Let *T* be the
phase's length at Q's mix.

- **XP:** while *d* is inside the carry window *W*, Q's XP equals P's: nothing aims at XP, so P's new phase earned XP
  at the same rate Q's wait did. Q clicks on return and lands on P's level. Gap 0.
- **Goods:** P's new phase pays its first levels and one node rank during those *d* hours; Q's skill keeps the old
  rates until the click. Q's gap is that difference on one skill's goods for *d* hours: a few level pays' worth,
  never the skill's progress. It is the one residual, and it is small by construction (ranks are sized to two or three
  level pays, and later phases' pays are adds).
- **Past the window:** Q loses that skill's XP for *d − W* hours, a fraction of one phase. That is the "absence that
  was just too long" hit decisions.md accepts, and nothing else in the save is touched.
- **Can a whole phase fall inside one ordinary absence?** No. Even at a full share on the fastest card, a phase takes
  about four times the ordinary-absence bar. A gate holds this from the rules (below), so later content cannot break
  it quietly.

### Nodes and their ranks

- A node is data: what it changes (a rate or cap on a card or store **outside** the prestiging skill), its rank count,
  and its per-rank amount. Every rank is equal, and ranks within a node add. The shipped tracks use one-rank nodes only (the loader
  refuses more): a multi-rank node lets the others fill first and leave a click with nothing to choose.
- **The bound:** a full node gives *R* × *a*. Nodes of different kinds compound with each other, so a skill's whole
  track tops out at the product of (1 + *R*·*a*) over its nodes: a fixed number known when the content is written.
  Five nodes of five ranks at a modest per-rank amount land between about 3x and 8x on the rates they touch.
- **Size a rank so it is felt:** about two or three of the skill's level pays. Smaller than one level's pay, a pick
  reads as nothing.
- **Undo the last pick** until the skill gains its first level from work done after the click; levels the carried
  XP lands at the click don't close it. The undo swaps the pick and nothing else (the phase and its levels stay).
  Because a rank's entries are derived from the pick, the swap is exact. It is a misclick window, and the player is
  always there for it, since the click is only by hand.
- **Can a pick strand a player?** No: every click but the last has two unfinished nodes to choose between. A pick can leave a node unfinished, and that is the point: when every node completes, a pick only orders them and two players' skills end the same. So a track
  holds more nodes than a typical game clicks, and the pick says what the skill is for. "Moving a pick" below is what
  makes that safe to choose.
- **Size each skill's track** so a typical game fills about two thirds of it. Measured with the ladder readout
  (`python -m tests.ladder.readout typical sharp --skills`, from `app/`) to the edge of played content (day 13.8): the
  two first skills stand at 82% and 76% of their first phase there, on sharp 88% and 75%, and the rest under 3%.
  Extrapolated, not measured, past the edge: each skill's XP rate since its level 20 held to day 90, the typical
  game's length (`decisions.md`, "Length"), with no new content. Woodcutting then clicks five times (a phase about 16
  days, the first top near day 17) and scavenging four (a phase about 22 days, the first near day 19); foraging,
  cooking, arcana and melee reach no click. Tracks are seven nodes for woodcutting and six for scavenging, so a typical
  game fills five of seven and four of six; the other four keep two, the least a choice needs. More played content
  moves the clicks, so resize a track when the readout moves.

### Moving a pick

A move takes the rank a picked node holds and puts it on another node of the menu, paying that rank's progress: the
rank is out of play for the rest of this phase and the whole of the next, and takes effect at the click that lifts the
skill into the phase after next. It costs between one and two phases of one rank's bonus, the same whenever in the
phase it is made, so rearranging before an absence loses a phase's worth and is never the best play, while a pick that
turned out wrong is worth fixing once.

- **By hand only, never queued or ruled**, as the click is. It is `MovePick(skill, node, to)`; `to` must be on the
  menu now, and a parked rank holds its node as a taken one does, so the menu moves on.
- Refused while a pick is owed after an undo (fill it first) and for a node that holds no rank.
- The undo window is unchanged: it still takes back the click's own pick, and a rank a click settles joins just before it.
- The prestige sheet lists the skill's picks, each with Move, says what a move costs before it is made, and lists parked
  ranks with the push they return at. A skill row shows Picks while it has a pick to move and a menu to move it to.

### The loop

Pecorella's model ("The Math of Idle Games", GDC Europe 2016): costs grow exponentially and production linearly, and
prestige reins growth back in. Here:

- **Cost per phase is fixed.** Every phase reads the same curve, and nothing speeds XP, so a phase takes the same
  hours at the same share each time. Prestiges per game are bounded by the game's length over a phase's length.
- **Production per phase grows linearly.** The levels of phase 1 compound once, to a fixed factor at its top. Later
  phases' work pays are adds, so each phase adds about the same again. Nodes add within a kind and compound across a
  handful of kinds. Over a game, production is a polynomial in the number of clicks, capped by the track. Stores' caps
  and the world's fixed costs bound it again.
- **The goods-to-XP path is capped.** More goods let a skill run its faster methods instead of stalling, which is the
  web's pull. A skill's XP rate can never exceed its fastest method's, so the phase-length floor holds whatever the
  bonuses.
- **Pecorella's rule of thumb (reset at roughly +50% to +200% prestige currency)** is for endless games, where each run
  must outgrow exponential costs. Here a run's cost is fixed and the track ends, so a click does not have to pay 1.5x.
  It has to be felt, which is the rank size above.

**Where it would spiral, each held by a loader check:**
1. A node or level aimed at XP, or at the hands' lane speed. Lane speed joins every line on the lane, XP included, so
   it would make levels come sooner. Nodes and levels may aim at a card's work and at rates and caps only.
2. Later phases' work pays as multipliers. Phase 1's compounding, repeated each phase, is geometric in clicks: tens of
   times the top speed after two phases, hundreds after three.
3. A node whose value grows with clicks or with goods.
4. A card whose XP rate is high enough that a full share tops a phase inside an ordinary absence.

### Breadth

Measured: each skill's faster methods take another skill's making, and they stall within half a day of a one-track
mix. The dry-store rule then moves their share to the rest of the mix. Each skill's base method takes nothing, though,
so a one-track mix on it climbs to the top at that base rate. The web is worth about 2.5x XP on the first skill.

Breadth therefore comes from the rate the web gives, and from the menu: every node pays out in other skills, so a
player who prestiges one track is handed reasons to run the others. Making base methods depend on the web would
contradict "bare hands gather" and would add the stall that the dry-store rule exists to avoid.

## Decisions this changes

- **"Prestige is the player's click":** add "only by hand; XP past the top carries over for about two days, then
  stops". "Banking … is an option the design weighs" becomes that carry.
- **Systems, "Every verb has an order":** prestige leaves the list. The carry window takes the order's job: inside it,
  a babysitter clicking at 03:00 gains nothing on a player clicking at breakfast. The simulator plays the click at its
  next visit and checks that gap.
- **"Breadth comes from the web … a one-track mix runs into the web":** becomes "the web makes a one-track mix
  slower, never stuck", as measured.
- **"Its timing has a flat optimum":** holds for XP anywhere inside the carry window. The new phase's early pays and
  rank start at the click, so a later click costs a few level pays' worth of one skill's goods.
- **Pacing curve, "its steps never shrinking":** holds within a phase. A new phase starts again at level 1.
- **"A level is a thing":** holds for every phase. Later phases' work pays are adds.
- **Engine, "XP is a segment capped at the curve's last threshold":** becomes "capped at the skill's current phase
  top".
- **"Every skill is paced to one shared target":** it does not hold yet. Tuning skills' XP rates to it is what makes
  prestige reach more than two skills. The shared rate, and what holds each slow skill below it, are in
  `decisions.md` under that rule.

## Engine interface (a sketch, not a contract)

```
PhaseState (new state type, one per skill; never a field on Save)
    skill: SkillId
    phase: int                    # 1 until the first click
    picks: tuple[NodeId, ...]     # one per click, in order
    parked: tuple[ParkedRank, ...]  # ranks a move set aside: (node, due phase); a click into `due` settles them
    topped_at: Instant | None     # when the skill reached its current phase top; bounds the carry

NodeDef (Type Object, content)
    id, ranks: int, per_rank: Modifier   # target: a card's work, a rate or a cap; never XP or LaneSpeed
    skill: SkillId                        # whose track it is on

Prestige(skill, node)             # verb; by hand only, never queued or ruled; refused unless at the phase top and node is on the menu
UndoPick(skill)                   # verb; until the first level earned by work after the click
MovePick(skill, node, to)         # verb; by hand only; the rank leaves node, parks on to (a menu node) until phase + 2
menu(save, rules, skill) -> tuple[NodeId, ...]   # fixed for the phase, read only

xp accrual     : stops at the earlier of topped_at + rules.carry_window (about two days) and the next phase's top
level_shown    = level_for(curve, min(xp, phase_top * phase) - phase_top * (phase - 1))
effective stack += derived entries: per_rank x count(picks == node), sourced by the node
forecast       += TopOut(skill, at)
loader checks  : no node or level aims at XP or LaneSpeed; later phases' work pays are adds;
                 phase_top / max card xp_per_hour >= the ordinary-absence bar, per skill
```

## Rejected, and why

- **A queued click ("prestige when it tops out, with this pick"):** it lands while the player is away, which is an
  auto-prestige with an extra step, and the return shows a skill in a new phase that the player chose days ago and
  never saw happen. The carry gives the same XP without it.
- **Replaying the wait's goods at the new phase's rates:** a second clock, goods earned at one rate and credited at
  another, for a gap of a few level pays on one skill.
- **Auto-prestige on topping out:** a skill found at level 1 is the "won't know what's happening" return.
- **OSRS-style random events against idling:** an offline cap in disguise. They interrupt work to make a player watch.
- **Capping XP and nothing more (today's engine):** the top becomes a dead end that the skill's story never leaves,
  and the work past it is lost with no way on.
- **Resetting the level pays at the click:** it lowers a saved mix's rates (red lines from a click), it gives the click
  a right moment to compute, and it would need released outcomes un-landed, which the release lock forbids.
- **Later phases continuing the curve upward:** the steps compound, so phase 2 would be impossibly long. Every phase
  reads the same curve.
- **A tree:** it has a hidden optimal path, and an early pick can trap a player.
- **A bonus that repeats with diminishing value (1/N of its first value):** it never completes, and completing a node is
  the point.
- **Multiplicative ranks:** they compound within a node. Adds are bounded and read plainly ("+N%").
- **A drawn menu:** chance would decide which bonus a player can reach.
- **A free respec, or re-choosing freely:** free reordering makes rearranging before each absence the best play, which
  is busywork the 2 AM test fails. A respec that costs a phase answers it ("Moving a pick"). Seasons
  need no respec, since a season adds and never lowers.
- **A move paid in XP or goods:** XP is a rate, never written by a verb, and a level never falls; goods have no one
  price every skill feels. **A cost that shrinks late in a phase:** a move just before the click would cost nothing.

## Settled

- **Picks must matter**: tracks are longer than a typical game's clicks, and a move costs a phase.

- **The click is only by hand** (a queued click defeats the point). The carry window keeps the 2 AM test level
  instead.
- **A phase's top sits lower than today's last level:** the level typical reaches on its fastest skills by the edge of
  played content, while a full share on the fastest card still needs more than an ordinary absence. The simulator
  picks the level; the saves-forward check holds it against live saves already past it. Pays above it move to later
  phases.
- **The undo lasts until the first level**, counted from work after the click. The case for a longer window was
  a queued click landing unseen; with the click by hand, the player is there for the window.
