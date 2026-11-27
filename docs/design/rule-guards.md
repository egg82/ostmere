# Rule guards and "or else" actions

**Decision:** a rule gains two optional lists. `unless` holds up to three guards: conditions that pause the rule while
any of them holds. `or_else` holds up to two more actions: the rule does the first of its actions that can start. A
rule with neither is today's rule, in the save and in what it does.

    Smoke the catch, or else Smoke roots
    13 or more catch, until under 1, unless smoked is full

There is no "or" between conditions: two rules with the same action say that, and the quick add's copy makes the
second one a tap. Both lists sit in the full editor behind `More options`, open from the first rule on.

## Fit pass

- **A guard is an instance of Conditions**, the Specification the engine already has (`docs/systems.md`, Gates and
  Standing orders). A conjunction is an explicit list on the thing that needs one, never a new condition kind: a
  trigger's and a card's `requires` are that list already, and the engine turned down a conjunction type for the end
  (`engine/design/`, "Triggers", and its first "REJECTED, AND WHY"). The order vocabulary stays `AtLeast`,
  `AtMost`, `AfterTime`.
- **A guard is latched as every order condition is**, with its own release, so the engine solves its change times the
  way it solves a `when` and nothing polls. The contract in `docs/systems.md` asks for it: "a boundary-chasing order
  gets hysteresis", and "unless smoked is full" on a rule that makes smoked food is boundary-chasing.
- **A fallback is an instance of Standing orders**: verbs are Commands in one closed union (`OrderVerb`), and the
  list is read as the order list is, first that can act, an entry that cannot act passed over as a gambit with no
  target is. A rule with fallbacks does exactly what adjacent rules sharing its condition would do (statement 14), so
  evaluation gains no rule of its own.
- **A rule's state is derived, never stored as one value.** Nystrom's State chapter, "Concurrent State Machines":
  two things that vary on their own are two small machines, not one machine with a state per pair. A rule's `when`
  latch and each guard's latch are separate latches; waiting, on and paused are read off them.
- **How games do it.** Final Fantasy XII's gambits are one condition and one action per slot, the list's order the
  priority, a slot with no target skipped; the engine's orders are that already. That game first sold its
  conditions piecemeal and its re-releases moved them earlier; here they are all open from the start.
- **No new system, event kind or `Save` field.** Extends: Conditions, Standing orders and the queue, the rule editor.

## What a rule is

    Order(when, then, unless = (), or_else = ())

`when` and `then` are today's. The rule's **actions** are `then` followed by `or_else`, in that order. Each guard in
`unless` is a `Condition`, read exactly as a `when` is read: it comes on at its value, lets go past its release, and
a share level is read against the store's cap at that instant (`engine/design/`, "SHARE LEVELS").

A guard is stored as the condition that **blocks**. "And smoked is under 10" is the guard "unless smoked is 10 or
more"; an at-least and an at-most level are each other's opposite, so one form covers both and the page has one word
for it.

Limits, refused by `SetOrders` (`InvalidVerbError`):

- at most 3 guards and at most 3 actions; no guard twice, no action twice;
- a guard passes every check a `when` passes (so no `LaneRules`, and a share level only on a store);
- every action is the same kind of verb: all `TapCard` or all `SwitchMix`. A rule that answers an offer takes no
  `or_else`;
- every listed tap is of a card on one lane, and every listed mix is of one layer (hands or town).

The queue is unchanged: a queue entry has no guards and one verb. Content writes neither list: an install still makes
only a lane's always rule, and an order card is still one condition and one tap.

## A rule's states

Read off the latches and what can act, in this order; the first that fits is the rule's state.

| State | When | What the rule does |
|---|---|---|
| passed over | every action is dead (a completed card, a greyed mix) | nothing, whatever its conditions |
| waiting | its `when` latch is false | nothing; it waits for `when` to reach its value |
| paused | its `when` latch is true and a guard's latch is true | nothing; it resumes when the last guard lets go |
| outranked | it is on, and an earlier rule has its lane or its layer's mix | nothing until that rule lets go |
| on | its `when` latch is true and no guard's latch is | its first action that can act |

A rule is **on** when its `when` latch is true and no guard's latch is. Everything in the engine that today reads "the
order's latch is true" (which mix runs, which tap starts, which lane a rule holds, READY) reads "the rule is on".

## Guards

- **A guard pauses; it never lets the rule go.** The `when` latch reads `when` alone and keeps moving while the rule
  is paused. A rule paused inside its band (past `when`'s value, short of its "until") resumes at the instant its last
  guard lets go, without `when` reaching its value again. A rule whose "until" is reached while it is paused is
  waiting from then on, and a guard letting go later changes nothing.
- **Checked every instant, by solving, not polling.** A guard's latch changes at the exact second its subject
  crosses, as a `when` latch does, and that change evaluates. So a guard coming on while the rule's mix runs hands
  the layer over at that instant (the next rule's mix, the queue's, or the player's own), and a guard letting go
  brings it back at that instant.
- **A tap already running lands.** Nothing cancels a tap. A guard that comes on mid-tap stops the next one from
  starting. A guard reads the stores as they are, never what a tap is about to make: a rule guarded by "unless smoked
  is full" starts a tap with one space left and may overflow it.
- **A guard keeps a band.** The page writes a guard as one level and sets its release one item past it: "unless
  smoked is 10 or more" blocks from 10 and lets go under 9. A guard on a share level stores the same share for both
  levels and takes the one-item band SHARE LEVELS gives a condition whose levels meet, so "unless smoked is full"
  blocks at full and lets go once the store is under one item short of full. Without the band a rule whose own mix fills the guarded store would
  switch on and off every second at the level.
- **A store's maximum rising** moves a share guard with it at that instant, as it moves any share level: the guard's
  latch keeps its state and is read against the new quantities, so a rule paused on "full" resumes at the raise if the
  store is now more than a full item short (exactly one short is not under the release, and stays paused).
- **Several guards**: the rule is paused while any one is latched. Each has its own latch and band, kept whether or
  not the rule's `when` holds, so a guard reads the same when the `when` turns true.
- **Editing a rule** follows today's rule for orders: `SetOrders` matches by equality, guards and actions included. A
  rule kept or moved keeps its `when` latch and every guard latch; a rule edited in any part is a new rule, each
  latch set from its threshold alone.
- **At the firing cap**, a guard latch change on a rule whose actions are mixes waits as its `when` latch change
  does, for the same reason: it moves the running mix with no verb applied.
- **Same instant**: latch changes resolve in rule order, and within a rule its `when` before its guards, in list
  order.

## "Or else"

- **Can act** means what it means for a rule today, per kind: a tap can act when its card is unlocked, not completed
  or retired, has no blocker, its lane is free and its speed is above 0; a mix can act when it is not greyed. Nothing
  new is judged.
- **The rule's action** at an evaluation is the first in its list that can act. A rule holds one place in the rule
  list, and its actions are tried there, top down, before any later rule gets its turn.
- **A guard pauses the whole rule**, fallbacks included. A fallback is for an action that cannot start, never for a
  guard that blocks; "do something else while smoked is full" is a second rule.
- **A better action coming back.** For taps: the running fallback lands as it would have, the list is read from the
  top at that landing, and the earlier action starts if it can. A fallback that runs as a rate (REPEATING TAPS) lands
  at its next completion once an earlier action can act, because its task has changed. For mixes: the earlier mix runs
  from the instant it stops being greyed.
- **None can act.** The rule does nothing at that evaluation and is skipped as a rule whose one action cannot act is
  skipped today: later rules and the queue get their turn, and its latches keep their state. READY falls at the first
  time any listed tap of a rule that is on turns ready on a free lane, so the rule takes the lane up at that second
  and nothing waits on another event. If the lane has gone to a later rule's tap meanwhile, that tap lands first.
- **All dead**: passed over. One action dead and another alive: the rule lives through the one that is alive.
- **A season retiring a chore** (`Outcome.retire_orders`) takes the named cards out of a rule's list and removes the
  rule only when none is left; the rule keeps its latches.
- **No memory.** Which action runs is a function of the save at that instant. Nothing records that a fallback was
  chosen, and nothing holds a rule to it.

## Evaluation, determinism and replay

Evaluation already applies every verb that can act (`engine/design/`, "Evaluation applies every verb"; the loop in
`app/ashfall_app/engine/instant.py`). That loop is unchanged. Two of its sources read differently:

- the tap source walks the rules in order and takes, from each rule that is on, its first listed tap that can act;
- the running mix is found the same way: from each rule that is on, its first listed mix that is not greyed, and the
  first one found runs.

Invariant 57 keeps its meaning with "a true latch" read as "on" and "its TapCard" as "a tap it lists". The loop still
ends: a tap that changes anything fills a free lane, and a rule's taps share one lane, so a rule starts at most one
tap an instant.

Guard latches are saved state that changes only at events and decisions, by the same exact integer arithmetic as
every latch, and the action choice is a pure function of the save. So splitting an advance changes nothing, a
decision log replays to the same save, and a forecast plays guards and fallbacks out as an advance does. A save
holding no guard and no fallback takes the same path through the engine as before: unlike the change to evaluation,
this one cannot make an old save's replay differ.

## The saved shape

Additive. No `FORMAT` change, no upgrade step, no rebase, no migration.

- `Order.unless` and `Order.or_else` are left out of the codec's text while empty, as an outcome's empty lists are.
  A rule with neither encodes to the text it has today, in the save and in the decision log.
- `Save.latches[i]` stays one entry per rule, and `Save` gains no field. For a rule with no guard the entry is the
  bare `bool` it is today. For a rule with guards it is `GuardedLatch(when: bool, unless: tuple[bool, ...])`, one
  `bool` per guard in list order. Each form is the only one for its rule, so equal saves still encode alike.
- Rules hold no `Order`, so the rules digest and the release lock do not move.
- A rename across releases renames ids inside `unless` and `or_else` as it does inside `when` and `then`.
- A build from before this change cannot decode a save that holds a guard or a fallback. The build order ships the
  engine that reads them before anything can write one.

On the wire: `Order` gains `unless: Condition[]` and `or_else: OrderVerb[]`, both empty by default. `View` gains the
state `paused` in `order_states`; `order_guards[i]`, one `{on, lets_go}` per guard, `lets_go` the quantity the guard
lets go at as the engine reads it now (null off a store); and `order_doing[i]`, the index in the rule's actions of the
one it runs now (its lane runs that card for this rule, or the running mix is that mix by this rule), else null.
`orders_on` keeps its meaning, the `when` latch.

## How the page words it

A rule reads as it does today, what it does and then when, with two additions.

| Part | Words |
|---|---|
| actions | `{first}, or else {next}` · "Smoke the catch, or else Smoke roots" |
| first guard | `{condition}, unless {guard}` · "13 or more catch, until under 1, unless smoked is full" |
| each further guard | `, and unless {guard}` · "…, unless smoked is full, and unless wood is under 5" |
| a guard on a store | "smoked is full", "smoked is empty", "smoked is 10 or more", "smoked is under 10", "smoked is half or more", "smoked is a quarter or less" |
| a guard on a chip, a task, a level | "hungry", "Forage is done 5 times", "Foraging is level 3 or more" |
| paused | "paused until smoked is under 19 · now 20"; off a store, "paused while hungry" |
| on, running a fallback | "on now · Smoke roots" |
| on, nothing can start | "on now · nothing it lists can start yet" |
| passed over, with fallbacks | "passed over · every task it lists is done" |
| editor, over the guards | "Unless" · "Pauses the rule while this holds." |
| editor, over the actions | "Or else" · "Does the first one it can start." |

- **"Or else" stays with the action.** Put after the guard ("…unless smoked is full; or else smoke roots") it reads
  as what happens when the guard blocks, which is the one thing a fallback never does.
- **A guard is a state, so it takes "is".** A `when` names a crossing ("13 or more catch"); a guard names what must
  not be so. "And unless" joins guards because "unless smoked is full or hungry" reads as one guard about smoked.
- **The paused line names what it waits for and what is there now**, from `lets_go` and the ledger, so the band never
  shows as a rule paused on "full" beside a store reading 19. The page never works the level out.
- **The band is not in the rule's sentence.** One item is too small to earn a second "until" in it.
- **Why a first action cannot start is on its card**, where every need is already drawn. The row names the action
  that runs.
- No semicolons or brackets: the row is read on every visit.

The editor: `More options` gains "Unless" under the condition and "Or else" under what the rule does, each with an add
button that goes away at the limit. A guard picks from everything a `when` can watch, with one level in either form
(of full, exact). An action picks from the same lane's tasks, or the same layer's mixes. A rule that holds a guard or
a fallback opens in the full editor, so the simple view never saves over a part it does not show. No lesson and no
hint dot: beyond the first rule, discovery is the way in (`docs/decisions/mixes.md`, the editors).

## Contract (blind)

For a test writer with the interface and this note, no code. `on(rule)` is as defined under "A rule's states". Q is
one item.

Shape and validation

1. An `Order` with empty `unless` and `or_else` encodes to the text the same order had before the fields existed,
   as a save's order and as a logged `SetOrders`; a save holding only such orders has `bool` latches and its old text.
2. `decode(encode(s)) == s` for saves holding guards and fallbacks; `verb_from_json(verb_to_json(v)) == v` for a
   `SetOrders` holding them.
3. `SetOrders` raises `InvalidVerbError` for each of: four guards; four actions; a guard listed twice; an action
   listed twice; a guard that `SetOrders` would refuse as a `when`; a tap and a mix in one rule; taps on two lanes;
   mixes of two layers; `or_else` on a rule whose `then` answers an offer.
4. Under any rules and decisions where no order holds a guard or a fallback, every engine call returns what it
   returned before (the existing suites, unchanged, are this statement).

Guards

5. With guard `AtLeast(S, v, v - Q)` on a rule that is on: no tap of the rule starts, and none of its mixes is the
   running mix, from the first instant S >= v until the first instant S < v - Q; at that instant a ready tap starts
   or its mix runs, with no other event needed.
6. A tap the rule started before a guard came on lands at the time and with the outcome it would have had.
7. While a rule is paused its `when` latch changes exactly when it would with no guard on the rule, given the same
   store values. Paused inside `when`'s band, it resumes when the guard lets go though S never reached `when`'s value
   again. Paused while `when`'s release is crossed, it is waiting, and stays so after the guard lets go.
8. With two guards the rule is paused while either is latched and resumes at the instant the second lets go.
9. A guard with both levels the same share b of S's cap comes on where a `when` of that share would, and lets go at
   least one item past it, never past full or empty (SHARE LEVELS, invariant 167). At full (b = 10000) it comes on
   exactly when S's whole items equal the cap's.
10. A cap raise at T on a rule paused by a share guard: the guard's latch is read against the new cap at T, and the
    rule resumes at T exactly when S is then past the new release.
11. A `SetOrders` holding an order equal to an old one (guards and actions included) keeps its `when` latch and each
    guard latch; an order that differs in a guard or an action has every latch set from its threshold alone at that
    instant.
12. `view.order_states[i]` is paused exactly when no earlier state in the table fits, the `when` latch is true and a
    guard latch is true; `view.orders_on[i]` is the `when` latch throughout; `view.order_guards[i][j].on` is guard j's
    latch.
13. Past the firing cap at T, a guard latch change on a rule that lists mixes does not change the running mix at T
    and is seen at the next instant where something else fires.

Or else

14. Expansion. Let rule o at index i have actions a1..an, and let save B hold, in o's place, the n adjacent orders
    `Order(o.when, ak, o.unless)`. From the same save, the same `SetOrders` instant and the same later decisions,
    saves A (holding o) and B agree at every time on stores, skills, lanes, cards, pauses, unlocks, the queue and
    `view.running_mix`, at instants that do not hit the firing cap, under rules where no trigger reads `LaneRules`
    (it counts A's rule once and B's n times).
15. With a1 unready and a2 ready on their free lane, an evaluation starts a2. With both ready it starts a1.
16. a2 running and a1 turning ready mid-tap: a2 lands at the time it would have, and a1 starts at that landing.
17. No action can act, the rule on, its lane free: nothing of the rule starts, a later rule's ready tap on that lane
    does, and with no later rule the first of the rule's taps to turn ready starts at that second (READY), no other
    event falling there.
18. A rule listing mixes M1 then M2, on: the running mix is M1 while M1 is not greyed; M2 from the instant M1 greys;
    M1 again from the instant a raise or a `SaveMix` un-greys it.
19. A guard latched on a rule with fallbacks: no listed action starts or runs for the rule, whichever can act.
20. `view.order_states[i]` is passed over exactly when every listed action is dead. `view.order_doing[i]` is k while
    the rule's lane runs ak for this rule or the running mix is ak by this rule, else null.
21. `Outcome.retire_orders` naming a1 leaves the rule with a2..an and its latches; naming every action removes it.

Replay

22. Invariants 1, 3 and 25 (split, decide advances first, logged split) hold for saves holding guards and fallbacks.
23. Every lane driven: after an advance that did not hit the firing cap, no rule that is on lists a tap that can act.
24. A forecast from s lists the times an advance from s then reaches.

The page

25. A rule's words are built from the table above, by key; a rule with no guard and no fallback is worded as today.
26. A paused rule's line names the guard's subject, the level from `order_guards[i][j].lets_go` in whole items, and
    the store's amount now; it reads no level off the rule.
27. The simple editor never opens a rule holding a guard or a fallback; such a rule opens in the full editor.
28. The editor builds only what statement 3 allows, and a store guard's release one item past its value (the same
    share for both levels of a share guard).

## Left out, on purpose

- **Pauses are not in the rule log or the chronicle.** A rule topping a store up pauses and resumes once an item, and
  the log's "came on" and "let go" stay the `when` latch's. The row shows a pause while it lasts.
- **A mix that runs but makes nothing still "can act".** Whether a mix's cards are all dry depends on pauses that
  clear when the running mix changes, so the first mix would look able again the moment the fallback took over. The
  row's "can't reach" line stays the answer there.
- **A guard's wider band.** The saved shape holds any release; the page writes one item. Opening it up later is an
  editor change.

## Rejected, and why

- **Full boolean conditions** (brackets, and/or/not nested): a rule stops being one sentence, and its reader has to
  work out precedence before knowing what the hands will do. Each leaf would still need its own latch and band, so
  the tree buys no engine simplicity, only an expression editor on a phone.
- **"Or" between conditions**: each arm needs its own "until", which makes it two rules written on one row. Two
  rules with the same action are that already, each with its own line saying why it is off.
- **Guards or fallbacks unlocked by progression**: which conditions a rule may test is a different lever from when
  automation arrives. Final Fantasy XII sold its gambit conditions piecemeal and its re-releases moved them
  earlier; a player who looks for a condition once and does not find it concludes the tool cannot do it. `More options`
  already keeps the first view small.
- **A separate rules engine** (an expression language or script interpreter beside orders): a second system answering
  "when X, do Y", and one that would be polled, where every order condition today is solved to its exact second.
  Forecasts, the split invariant and "why is it off" all rest on that.
- **A guard with no latch** (a plain level, as a card's `requires` is): no state to save, but a rule whose mix fills
  the guarded store flips at the level every second, each flip an instant the engine resolves and a forecast pays for.
- **A guard that lets the rule go** (a second "until"): the rule would not come back inside its band, so "smoke the
  catch until it is gone, unless smoked is full" would stop for good at the first full store.
- **One paused bit per rule in place of a latch per guard**: a guard sitting inside its band, never having blocked,
  would keep a rule paused, and the line saying why would name a guard that is not on.
- **An "and" form beside "unless"**: two words for one thing, since every level has an opposite, and a second
  sentence shape to teach.
- **A new `Save` field for guard latches, or guard latches appended to `Save.latches`**: the first is what the held
  list of `Save`'s fields refuses; the second hides a second list in the tail of the first, which every writer of
  orders would have to keep aligned by hand.
- **Fallbacks across lanes or kinds**: with every verb applied at an instant, "the first that can act" on two lanes
  becomes "both", once the first lane is busy. Two rules say that honestly.
- **A fallback for a blocked guard**: "or else" would mean two things. The opposite condition on a second rule is
  the same behaviour, visible.
- **Holding a rule to the fallback it chose** until some count or level: state with no home, and a second "until".
