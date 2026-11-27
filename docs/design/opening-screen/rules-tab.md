## The Rules tab

A tab beside Tasks and Completed, there once this game has a rule or a queued tap, or, once writing rules is open in
this game (a rule seen on and then off in it, by the page or in the save's record of what its rules did) and the ledger
is in: then the tab stays with no rule left, its list empty but for `+ New rule`. A new game's first screen stays
without it. Kept for the page session if every rule is removed. A mix is what the hands do and a rule is what waits on something happening, so they
live apart: mixes in the Mixes list, rules here, one line each.

```
Tasks · Completed · Rules
≡   (Under 3 dry wood, until 8 ✎)    →  [Scavenge ▾]   top priority first
    needs under 3 dry wood · now 5                     why a rule is off, quiet, under its line
≡ ● (While tired ✎)                  →  [Rest ▾]       ● the rule on now
    Otherwise                        →  [Main ▾]       the player's own mix, the default
+ New rule                                             once writing rules is open
Rack                                                   each side lane's task rules, under its label
● (Under 2 dry wood, until 6 ✎)  →  ■ Lay to dry   Remove
```

- **Mine | Camp.** Once a second person has hands, a switch tops the list and shows one side at a time: Mine, the lists
  above (the hands' rules, Next, Otherwise, `+ New rule`, the lanes that are not people's, Answers); Camp, the town's
  rules, each person's lane and a `+ New rule` offering people's tasks under their names (`docs/decisions/mixes.md`). The
  side is kept per device; before a second person has hands there is no switch and one list.
- **Rules run mixes, in priority order.** The first hands rule whose condition holds runs its mix over the player's;
  when it lets go, the player's own comes back. A mix can have several rules (each its own line: X or Y).
- **The condition is a button** in the house button colours with an edit mark: it opens the condition editor in the
  tab. Changing a rule that exists is never gated.
- **The mix slot**, tapped, opens a picker: the rule's condition as heading, every saved mix (a greyed one off, the current one
  marked) and `New mix`, whose save points the rule at it. On `Otherwise` the same sets the default.
- **`≡` reorders the hands rules:** drag it (mouse, pen or touch; a press that moves a few pixels is a drag), tap it
  for `Move up · Move down · Remove`, or focus it and use the arrow keys. A side lane's rules keep their places. Every
  change sends the whole list in its new order (`set_orders`).
- A rule on another lane's task does that task while its condition holds, beside whatever the hands run: no slot, and
  `Remove` at its end.
- **A lane run by rules** has its section under its label like any side lane, every rule that taps one of its tasks in
  list order. Its always rule reads `{task}, always` (the task is in the words, so no `→`), a button that opens the
  lane's task editor; its ● marks the rule the lane runs now. A rule on a one-off whose task is done (an installed
  rule, or one the player wrote) stays listed, `passed over`, until removed. A new rule on that lane (written, or an offer's `Add rule`) goes just before the lane's first always
  rule, so it can act. `outranked by …` names the rule the lane runs now: its condition, or its always words.
- A rule or a queue entry that answers an offer (set by an answer, never by this page) reads `Answer: {answer}`; such
  rules sit last, under `Answers`. An always answer rule (the answer
  order, set ahead) is listed there too, in list order, in its own words with no arrow; an offer whose answers start
  nothing shows each answer's effect where a time would be.
- A rule whose mix is greyed is passed over; while the player's own is greyed, the hands fall through to the rules or
  the queue.
- **A rule whose condition is exactly a chip's is the chip:** `While tired → Rest` here, `while tired` on the strip,
  and its editor offers only its mix and `Remove`. The player never sees that store as a number.
- Rules on a store's amount, a task's count and a skill's or the Camp's level are drawn, the kinds the editor writes.
  None is written or drawn on time, an unlock (unlocks only grow, so one the save holds is always true) or a task
  running (`set_orders` refuses it: an order on what its own mix stops would flip at every instant).
- **Shortcuts:** a ledger line a rule watches opens the tab on that rule's editor; the strip's
  `until …` or `while …` opens the tab itself, where `Lately` says what the rules did.
- On a phone, tapping is the primary path (the picker, ≡'s menu); dragging ≡ works with touch too.
- **A rule that is off says why** in a quiet line under it, in the ledger's grammar, from the engine's own
  reading of where each rule stands (`View.order_states`), never from the page's: `needs under 3 dry wood · now 5`
  (`needs 12 or more dry wood · now 5`) while its condition does not hold, the store's amount live; `outranked by
  {rule}`, the condition of the earlier rule whose mix has the hands, while its condition holds; `passed over · a task
  it runs is done` while its mix is greyed or its task completed, whatever its condition. A rule that is on has no
  line, and nor has a chip's rule that is waiting (its store is never a number). A side lane's task rule counts as on
  while its condition holds, as its ● does, even while its task waits to be ready.
- **Next**, the queue, sits between the hands rules and `Otherwise`, the order the engine gives the hands: a rule that
  is on, then the queue's head once it is ready, else the player's own mix. One line per entry, `Remove` at its end.
  The tab shows once the queue holds something.
- **`+ Plan`**, under Next while the queue has room, adds either kind of entry. Its list starts with the cards
  `When ready` takes, ready now ones included (each reading `When ready`, picked exactly as that button picks it); a
  step with no ready time the page can see kept is listed too, its row the one its card's face draws for that wait
  (`Flint 3/4`, `Opens after dark`, `Foraging level 2/3`), and picked the same way: any unlocked step can be planned, and
  an entry that cannot run yet waits while the hands work what can (engine DESIGN.txt, "Never ready"). Then the saved
  mixes, a mix leading on to its goals. It is offered once there is a card or a mix to pick.

### Lately

What the rules did, so a returning player can see why this mix is running (`research/design-101.md` §3, proposal 5). The tab's last block, under the side lanes, headed
`Lately`, there once any rule has come on. One entry per rule, the most recent change first:

```
Lately
Under 3 dry wood, until 8 → Scavenge
    ran 4 times · came on at 2 dry wood, 3h ago · let go at 8 dry wood, 2h ago
While tired → Rest
    ran once · came on 20m 5s ago                     a chip's rule: no levels; still on: no let-go
```

- **Facts only, in the ledger's grammar:** how many times the rule came on, then its last start and, once it has let
  go since, its last let-go, each with the store's level at that moment (never for a chip's rule) and how long ago.
- **The record is the server's,** since a rule can come on and let go while the page is closed (Step.rule_runs,
  contract/). It is a chronicle record, not a new system: the engine reports each order's latch turning true or
  false (`engine/rulelog.py`), and the save keeps one entry per rule, the most recent few, pruned as it is written.
- **A rule is known by what it says,** its condition and what it runs, since rules have no id. A reorder keeps its
  entry. An edit makes it a new rule, so the old entry goes and the edited one starts its own the next time it comes
  on; a removed rule's entry goes with it.

### When ready

After the end, a step (not work done again and again, which is the mix's) that is unready but will be ready by itself
(its blocker has a ready time, drawn as the card's countdown) carries a small `When ready` button over the free right
end of its foot, beside the tap target. A waiting card's foot reads `Opens in 2h`; only a running tap's foot is the bare
timer. A ready time is a promise, so it is drawn only while the page can see it kept:
a rule on the store the card waits on that is on and lets go below the need stops the store short, and then the card
shows its need and maker with no countdown and no `When ready`. A step waiting on a store the player has never been
shown (the night) is a clock, not something to plan around: it draws when it opens and its countdown, with no
have/need and no `When ready`, since what it opens must open in front of the player (queued, the morning's step would open the snares
unseen, and the 2 AM test fails). It queues one tap of the card, held until that tap
completes, and the card flies to the Rules tab. A step ready now carries it too while its lane runs another tap, so
the build runs after that task. It is a shortcut: Next's `+ Plan` lists these cards, and every other unlocked step, and
queues the same entry. Queued, it stays as a quiet `in Next` mark, so the card keeps its size;
the strip notes `next: {task}` (the first thing to give way on a phone). The first time it is on show it takes the one
glow.

### The condition editor

Writing a new rule is its own taught step (`decisions.md`, "The mix"): `+ New rule` shows once the page has seen one of
the player's rules come on and then let go, remembered in the browser. Until then rules come only from the offers.
Changing a rule's levels is open from the first rule on.

The editor takes the Rules tab's place until it is closed. A new rule opens **simple**:

```
New rule                                          ✕
Do    [Forage] [Cook roots] [Rest] [Smoke roots]     the tasks a rule can do, hands and other lanes
When  [smoked 2 / 12] [roots 6 / 24] [damp wood …]   once a task is chosen: the stores relevant to it, and its chips
[More options]
────────────────────────────────────────────────
When smoked▾ falls to▾ a quarter▾, Smoke roots▾      the foot, pinned to the bottom of the screen while it scrolls;
until three quarters▾                                each part a choice in place
                                         [Add rule]
```

`More options` opens the **full** editor in place, and a rule being changed opens on it:

```
Run Evening when…                                 ✕
Do    [Forage] [Cook roots] [Rest] [Main] [Evening]  the tasks, then the saved mixes
When  [hungry] [tired] [dry wood 3 / 12] [stones 5 / 12] …     every chip shown so far, every store
Levels  [Camp level 1] [Foraging level 2] …         the Camp and each skill, at the level each stands at
Tasks   [Hatchet] [Lean-to] …                       each task in play with a cap, by its count of times done
[ When 3  Until 8                       ▾ ]         the levels, folded on a new rule; open when changing one
  [ falls below | reaches ]
  When  [−] 3 [+]      Until  [−] 8 [+]             stacked on a phone; 44 px targets
  ░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░                      the band n..m over 0..cap, a tick for now: drawn, not a control
while Evening runs: dry wood +0.80/min              a fact from one dry run, never a verdict
────────────────────────────────────────────────
Under 3 dry wood, until 8 → Evening
Remove                       [Copy rule] [Add rule] Remove and Copy rule only when editing; Save in place of Add rule
```

- **The common rule is two taps:** what it does, then the chip or store it waits on. A new rule starts with nothing
  chosen and `Add rule` off. In the simple view, `When` appears once a task is chosen and offers what that task
  answers: the chips whose store it makes, and the stores relevant to it with a ledger line, in this order: what it
  makes, what it takes, then one step out (the other stores of each card in play that makes what it takes or takes
  what it makes). Relevance is read off the cards' own makes and takes (`CardInfo.makes`, `CardInfo.takes`), never
  off words in a name, so a task named for one thing never pulls in an unrelated store that shares the word. Choosing
  another task clears a condition it does not answer. The rule and Save stay pinned at the screen's foot, under the
  thumb, whatever is scrolled.
- **The quick add is one sentence with its levels showing:** a store rule in the simple view reads `When smoked falls
  to a quarter, Smoke roots until three quarters` (`reaches`: `When catch reaches full, Smoke the catch until down to
  half`), and each part is a choice in place, a native picker laid over its words: the store among the relevant
  ones, the test, each level among the five named shares (off where the band would not fit), the task among the
  tasks. A store the task takes starts at `reaches full, until down to half`, so the rule uses it as it piles up;
  any other at `falls to a quarter, until three quarters`, so it makes more as it runs low. An exact number, a
  percentage step and a store outside the relevant ones are `More options`'; a rule with an exact number reads as
  the full editor's sentence below.
- **The full editor keeps every choice** (`decisions.md`, "The mix"): the saved mixes beside the tasks, every chip,
  store (the relevant ones first), level and task count a rule may watch, the levels (folded behind one row stating
  them, which opens them in place; a rule being changed opens with them shown) and the rate fact. `More options` goes
  once it is open.
- **`Copy rule`** on a rule being changed starts a new rule with the same task and condition, `Add rule` off until
  something differs: two rules with the same task are how a rule comes on at either of two conditions. It opens in the
  quick add when the rule reads as one there, else in the full editor. A chip's rule has none (its condition cannot
  change), and it is off while the rules are full.
- **A saved mix of one task alone is that task:** `Do` offers the task once, and choosing it runs that mix. A hands task
  with no such mix gets one when the rule is added (named by the task), as the offers do.
- A chip chosen is the chip's own condition, worded `While hungry`, with no levels: the player never sees that store as
  a number. The full editor offers every chip from its first showing on (`View.chips_seen`), whether it shows now and
  whatever task the rule then does: a player who meets a need and goes to write its rule finds it there, even before
  the task that answers it is open or after the chip has cleared. The simple view's narrowing stays: there a chip
  appears under a task that makes its store.
  Only stores of two items or more are offered (a smaller one has no room for a band).
- **A rule runs a mix or a task.** `Do` lists the unlocked tasks that can be done again, by their card labels; a
  one-off, a card at its cap and a retired one are not offered. A task on another lane saves the same order an offered
  card does (`tap_card`). A task on another lane has no rate to state, so it shows no `while … runs` fact.
- `falls below` comes on below `When` and lets go once the store reaches `Until`; `reaches` comes on at `When` and
  lets go below `Until`. Each of `When` and `Until` is a share of the store's cap or an exact number, chosen beside
  it (`of full` or `exact`): a share is picked by name (empty, ¼, ½, ¾, full) or stepped five points at a time, a
  number stepped an item at a time, and switching keeps the level where it reads now. A share is reached at the share
  itself from either side, so `down to empty` and `until empty` both mean nothing shown. The band is at least one
  item and inside the store's cap, so a rule never flips at one level and is never always true (the conventions:
  `api/contract/`), except on a store nothing that runs raises (only a lost fight, a find or an answer adds to
  it, as to hurt), which cannot flip on a flow: there the band may be none (`hurt reaches 1, until down to empty`). A store under two items is off.
- The words put a number before the store and use no verb (`Under 3 stones, until 8`, `12 or more dry wood, until
  under 6`), so they read right whatever the store's name; a share follows the store (`Dry wood down to a quarter,
  until three quarters`, `Dry wood up to full, until down to empty`).
- A new store rule starts as shares, down to a quarter, until three quarters (`reaches`: up to full, until down to
  half), in items only on a store too small for those to keep a band, and is added as the lowest priority. Editing keeps the rule's place; a rule written before bands (an offer with no release) opens with `Until`
  already filled in, visible in the sentence before Save.
- **A level or a task's count takes one stepper** in the store levels' place: `Level [−] 3 [+]` reads `Once Foraging
  reaches level 3`, `Times [−] 4 [+]` reads `Once Forage is done 4 times` (`Once Forage is done` at one). Each starts
  one past where it stands now, so a new rule is not already true, and reaches 1 at the bottom; a capped task stops at
  its cap. Counts and levels only go up, so there is no `Until`. The Camp stops below its first held level not yet
  lifted: the store passes that level's mark before the bar counts it, so a rule on it would come on while the bar
  still read the level below. Only what the save holds is offered, so the list grows with the story; a done task's
  count no longer moves and is not offered.
- **A pick that shows a control brings it into view,** centred in the editor's scroll (at once under reduced motion),
  so the store levels or a stepper never open under the pinned foot.
- Save is off, with `a rule already does this`, for a rule identical to another.
- Changing a chip's rule shows its chip as the heading, its `Do` row, the sentence and `Remove`: no stores, test,
  levels, band or fact.

Known limit: a rule whose task or mix makes a store covers that store's line whatever its condition (a rule that would
never come on still covers it). The rule's own line in the Rules tab says it is waiting and on what.

