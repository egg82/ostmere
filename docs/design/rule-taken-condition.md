# A condition on a ruled lane's rules

**Decision:** one new discrete subject in the order vocabulary, `LaneRules(lane)`: the number of orders in
`save.orders` whose verb is a `TapCard` of a card on `lane` (a declared ruled lane) and whose `when` is not
`AfterTime(0)`. It is allowed only as a trigger's `when`. Day two's `l_her_rule` trigger is then:

```toml
[[triggers]]
id = "t_her_rule"
when = { test = "at_least", subject_kind = "lane_rules", id = "n1", value = 1 }
outcome = { line_keys = ["l_her_rule"] }
```

## Fit pass

It is a content gate: Triggers firing a condition from Gates' one vocabulary (`docs/systems.md`). No existing subject
can express it:

- **`unlocked`**: taking a rule writes no unlock. Accepting an order card sends `set_orders` with one order added
  (`api/CONTRACT.txt`, order cards), the same verb the editor sends; only outcomes grow the unlock set.
- **`running` / `card_count` on the rule's card**: `Change` can make that card her always task, which is a task
  change, not a rule, so it fires falsely. It also lags: the rule may wait hours for its store to fall.
- **An offer**: the order card is not an offer, and a rule the player writes in the editor answers the same line.

The defining property is checkable: an install only ever makes `Order(AfterTime(0), TapCard(c))` (engine
`DESIGN.txt`, "Installed rule"), so an order on the lane with any other `when` was set by the player. Editing the
always rule's task, or an answer installing a one-off always rule above it, leaves the count unchanged.

## Interface

- **Engine:** `LaneRules(lane: LaneId)` joins `Subject` and `DiscreteSubject`. `discrete_value` counts as above. An
  order naming an unknown card is not counted.
- **When it turns true:** `save.orders` changes only at a `SetOrders` (a decision) and at an install, which adds only
  `AfterTime(0)` orders. Rebase renames keep each card's lane, because the release lock forbids moving a card onto or
  off a ruled lane. So the value changes only at a decision. `rise_time` returns `None` for it, as for every discrete
  subject. `decide` resolves the instant, `pending` finds the trigger (`rise_time == save.time` once it holds), and
  the line lands in that decision's `Step.lines`. Forecasts and what-if forks, where nobody decides, never fire it.
- **Only in a trigger's `when`.** `rules_check` refuses it in chips, card `requires`, and trigger `requires`.
  `checks.check_condition` refuses it in `SetOrders` and `SetQueue` (`InvalidVerbError`). Saves therefore never hold
  it, so the codec, `FORMAT`, the manifest, save renaming and the wire `Condition` stay as they are. Offer gates are
  triggers the loader makes, so it is allowed there too.
- **Save and rebase:** no new field, no format change. The released lock records trigger outcomes, not `when`, so a
  new trigger is additive. A save already holding such a rule when the trigger first ships gets the line at the
  rebase instant (step 6 evaluation, forward only), as any new trigger that is already true.
- **Loader:** `ConditionEntry.subject_kind` gains `"lane_rules"`. `refs._check_condition` needs `id` to be a declared
  lane with `ruled = true`, `test = "at_least"`, and no `release`. Using it anywhere but `[[triggers]].when` or an
  offer's `gate` fails, naming the place. `convert._subject` maps it.

Lead's answers (2026-10-25): changing a ruled lane's task through Change does not count, because the task is the always
rule. A rule the player sets and later removes has still landed the line, since a trigger fires once.

## Rejected, and why

- **A generic orders count** (all orders, or filters by kind, lane and store): the player's own hands rules and the
  installed always rules would count, and filters are a query language for one need.
- **A per-lane flag in the save** ("has taken a rule"): a new `Save` field, which the engine contract forbids, holding
  a copy of what `save.orders` already says, so the two can disagree.
- **An unlock written by `SetOrders`**: makes a verb a second writer of the only-growing set, and the page or the
  simulator would have to know which orders count.
- **A line fired from the client**: the client never decides. The simulator's line states and the save's lines would
  miss it, and a rule set by an order or the simulator would never land it.
- **Allowing it in orders and chips**: an order on its own lane would count itself, and the wire, codec and rename
  code would all need to learn a shape no rule needs.
- **A 0/1 "has a rule" subject**: the same cost as a count, and narrower only by clamping. The count stays true to
  what it reads.
- **Marking player-set orders**: already rejected for installs (`DESIGN.txt`), because an `Order` stays (condition,
  verb).

## Contract tests (blind)

1. A fresh save under rules with ruled lane L reads `LaneRules(L)` as 0. An install of L's always rule leaves it 0.
2. `SetOrders` adding `AtMost(StoreValue(s)) -> TapCard(c)`, with c on L, makes it 1. Removing that order makes it 0.
3. Orders tapping cards on other lanes, mix orders, `AfterTime(0)` orders on L, and an order naming an unknown card do
   not count. An `AfterTime(t > 0)` order on L counts.
4. A trigger `AtLeast(LaneRules(L), 1)` fires at the `SetOrders` instant T. Its line is in `decide_logged`'s lines at
   T. It fires at most once, even after the rule is removed and set again.
5. Advancing any length of time without decisions never fires it, and the forecast never shows it.
6. Editing L's always rule to another card (`Change`) does not fire it. A `first=True` install of an always rule does
   not fire it.
7. `SetOrders` or `SetQueue` holding a `LaneRules` condition raises `InvalidVerbError`. Rules with it in a chip, a card
   `requires` or a trigger `requires`, or naming an unruled or unknown lane, raise `InvalidRulesError`.
8. The loader refuses `lane_rules` outside `[[triggers]].when` or an offer's gate, with `at_most`, with a `release`, or
   on an unknown or unruled lane. The day-two chapter loads with `t_her_rule`.
9. A save already holding a qualifying order, rebased onto rules that add the trigger, fires it at the rebase instant.

## Files

| File | Change | Size |
|---|---|---|
| `app/ashfall_app/engine/orders.py` | `LaneRules` and the two unions | ~10 |
| `app/ashfall_app/engine/discrete.py` | the count | ~8 |
| `app/ashfall_app/engine/conditions.py` | discrete branches | ~2 |
| `app/ashfall_app/engine/rules_check.py`, `checks.py` | known ruled lane, placement, verb refusal | ~15 |
| `app/ashfall_app/engine/renaming.py`, `app/ashfall_app/api/convert.py` | unreachable arms the exhaustive matches need | ~4 |
| `app/ashfall_app/engine/DESIGN.txt` | a "Lane rules" entry, invariants, rejected | ~20 |
| `app/ashfall_app/opening/entries.py`, `refs.py`, `convert.py` | `lane_rules` kind and checks | ~20 |
| `app/ashfall_app/opening/day_two.toml` | `t_her_rule` | 4 |
| tests (engine contract, loader) | the statements above | ~150 |

That is about 85 lines of code and docs plus tests, size **S**.
