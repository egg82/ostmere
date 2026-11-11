# Mixes and standing orders

The mix, the rules that switch it, and the two layers it runs.

## You and the town: two layers, joint projects

You do one mix at a time and level personal skills (the Melvor/Idle Fantasy feel); the town's people work in
parallel under your standing orders (the town-builder feel). Some resources only the town can make (volume: stone,
timber, labor), some only you can (knowledge, spells, what expeditions bring back). Big things are **joint
projects** needing both: a wizard's tower takes the town's stone and labor, books from its scribes, and your
knowledge of magic. Each is a milestone the nobody and the town achieve together, the theme made mechanical.

## The mix: several actions at once

**In one line: Idle Awakening's mixes and its rules merged into one system, on one kind of card, designed so the best
way to play never means watching** (2026-10-15). From it: lists with shares, an editor with live
before/after totals, saved lists to pick and switch, rules that choose what runs, capped actions that complete, the
mix arriving when juggling by hand starts to hurt (studied in own-play notes kept outside the repo).
Better than it: a card is tapped or mixed alike; an order always runs a mix (one card is a one-card mix); a greyed
mix hands over to the queue or orders; shares and totals are exact, never an opaque "auto"; taught by need, each
system's first use a short lesson on its own controls; completed things in plain view; a full store is answered by a rule the player writes.

From Idle Awakening, whose mixes work well: pick several actions and give each a share of your time; all
their bars fill at the same time at different rates. A live ledger shows what the mix spends and makes as you adjust,
and you tune it, then hit go.
- Available from the start, not a late unlock; the actions you can add grow with your skills, so it is taught a
  piece at a time.
- **One card per kind of work, used both ways** (from Idle Awakening). Tapping a card does it by hand, which
  pauses the mix while the hands are busy; the mix runs the same cards, which show their share and progress. There is
  never a separate control for the same work. **A mix holding a retired or completed card greys out whole**: it
  stops, and the player can only edit or delete it, so a saved mix never quietly starts doing something else (see
  re-tuning below). The stop is the point (it sends the player to the editor), so it is never quiet either: the strip
  says the mix stopped and which card is done, and Edit takes the glow (a cold tester's grey mix ran nothing for the
  rest of her session and she never noticed). Unlike Idle Awakening, a greyed mix falls through to the queue or the
  orders, so the hands go idle only when nothing else is lined up (the 2 AM test). The player's mix holds the cards
  their own hands do; work on a rack or a building is tapped, by hand or by orders, until the town has a mix of its own
  (decided 2026-10-12).
- **The game states facts, never a verdict on the mix.** No "balanced" label: "balanced" means something different to
  each player, and draining a stockpile on purpose is a legitimate play (faster progress now, or a store that has to
  go). Each ledger line shows its rate and, when it falls, how long the stock lasts ("Candles −4/h · 7 h left"); the
  mix header shows how long the whole mix runs as set ("runs 7 h", or "runs indefinitely").
- Shares are percentages and the ledger is exact per hour (Idle Awakening took raw counts, so exact targets sometimes
  needed absurd numbers). A resource line once carried a control for its targets (hold it steady, make it last, let it
  run down). Superseded, 2026-11-09: a target is a rule ("No hold on a line", below).
- It is built goal-first, as a chain: pick what you want ("knowledge"), see what it costs, add what supplies that
  (work for money), then what supplies the new costs (rest or walking for energy). A falling line shows the actions
  that supply it, as cards beneath it (never behind a tap on the line; see "What can be tapped looks tappable").
- **Re-tuning comes from progress, never from drift.** A mix's rates never change by themselves (no input costs
  creeping up with level), so a saved mix keeps doing exactly what it did. New actions, tools and materials do
  replace old ones at unlocks, so the best mix changes every so often and re-fiddling your blocks is part of play
  (Idle Awakening makes it necessary, which is good, but too often). A saved mix with a better option
  available is never marked (that would be a verdict); the editors' goal-time rows show what a change does once the
  player opens one. **A re-tune is never necessary:**
  nothing the game does lowers a mix. What the player chooses (an upgrade bought, a tool made) or
  what the game brings (a season, an ask) may make one worth making, so tweaking a mix pays off a
  decision, never upkeep the game imposes; it counts as the decisions kind of effort, not the taps kind. Mixes and
  rules should be worth coming back to more than basically never (`design/worth-a-change.md`). **Give the player the
  tools, not a button**: after the guided first mix, second mix and first rule, no offer builds a mix or a
  rule: a quiet dot marks the card, chip or line one could answer.
- **Mixes are building blocks:** named and saved ("Study", "Stockpile wood", "Recover"). Standing orders switch
  between saved mixes ("when knowledge is capped, run Stockpile wood") while the order's condition holds; the
  player's own mix comes back after. So orders and mixes are one system: a default mix everything falls back to,
  and mixes that run when something happens, in priority order.
- **A mix is what the hands do; a rule is what waits on something happening.** A side lane's rule (drying) is a
  single task, not a mix. Superseded for people, 2026-11-10: the first helper joins the camp's mix when the first
  other person does, her always task becoming her whole share, and her time splits as theirs does from then on. Her
  single task was a leftover from before mixes existed, its intent drifted over time. A lane that is not a person (drying, a cure) still runs one task.
- **Blocks nest:** a saved mix can contain other saved mixes ("Recover" dropped into "Study" with one share).
- Running dry never stalls the mix: a dry card's share goes to the rest of the mix until its store refills (the dry
  store's handover). Nothing answers the dry store for the player; a rule the player writes can ("if food runs low,
  more foraging"), and so can a maker of the store in the same mix, which takes the dry card's share and refills it.
  The ledger shows the line as starved until something does. The first time a mix card stops on a store a card in play
  could refill, the line gets the hint dot and a lesson walks adding that maker to the mix.
- **A rule that cannot let go says so, and nothing more.** "Under 6 wattle, until 15 -> Weave wattle" with damp wood
  gone never reaches 15 and holds the hands. The game does not release it, change the defaults or block Save
  (choice-not-protection.md): the rule's row states the fact ("can't reach 15: out of damp wood"), and the editor
  states beside Save, before it is written, that nothing in the mix makes a store the mix consumes. Server decision
  (CONTRACT.txt, "Dry rules"); the client words it.
- **No hold on a line**. The Hold, which kept a store at a level by slowing one card of the mix, is
  gone, from the engine to the page. It was left over from protecting players who don't want to play the game
  ("Choice, not protection", `design/choice-not-protection.md`): mixes and rules cover everything met so far,
  for a player paying a little attention. A card that drains its input hands its share to the rest of the mix (the dry
  store's handover), and a reserve kept for a second consumer is a rule the player writes. No player had saved a mix
  with one.
- **Hitting a cap is a rule for the player to write, and the game teaches it.** Idle Awakening's knowledge maxed in
  seconds, so pausing to swap by hand was optimal and the game turned active. Here a rule switches instantly
  ("when it's full, move to the next thing"), and better rules are faster. A new save starts with no cap rule: the first full store the hands fill gets the hint dot and starts the cap rule's lesson, once the player
  has seen a rule of their own come on and let go. The lesson walks the Rules tab's own New rule with nothing filled in.
  A player who skips it loses only the overflow, which the full line states ("full"). The 2 AM test fails any design where swapping by hand beats the
  rules the game has taught. Upkeep the player can answer with a rule
  (a chip's cure, a store that falls) is left to the player, guided by a hint, not installed for them.
- **Orders are the player's to edit and write**: change an order's threshold ("dry wood ≤ 2" to 4), pause or
  remove it, or write a new one from any line and any card ("when wood is low, forage", even if it is odd). It
  arrives as its own taught step, after the first pre-filled orders have been set and seen working, never alongside
  them; until then orders come only from the order cards.
- **The editors open simple; the full editor is one deliberate tap away** (after playing day one:
  poking around found the editors, and they were a bit much). A new rule opens on what it does and, once
  that is chosen, what that answers (a chip such as hungry, or a store the task makes), so a rule like "cook roots when
  hungry" takes two taps. `More options` opens the full editor in place: every mix, chip and store, the levels and the
  rate. The full editor keeps all its power, since it is what makes rules handy later; only its first view shrinks.
  The mix editor likewise shows only what an edit changes. Each is first met through a lesson on its real controls
  at the moment it matters, the mix before rules, skippable and never repeated (after the galaxy.click
  reviewer's mix ran nothing for fifty minutes: `docs/design/opening-screen.md`, "Lessons"); beyond the first rule,
  discovery stays the way in.
- **Lessons are kept per save, and a player who knows the game can turn them off**. A new game
  teaches everything again from each lesson's own moment, whatever another game kept; one account-wide setting, on by
  default, turns every lesson and the hints only a lesson gives off, and back on from where each game stands.
- **Saving a mix never changes which mix runs** (a new mix took over, and getting back to Main took working
  out). Running a mix is its own tap, in the Mixes list, which says which one runs and offers `Run` on the rest. It is
  the hands' version of "a saved mix never quietly starts doing something else".
- One mechanism for both layers: your mix runs your day, the town's mix runs its buildings and people.

## Automation is designed, not clicked

The Farmer Was Replaced and scripting past Clicker Heroes' anti-macro bits both hit. On a phone that means rules
built by tapping: standing orders, a priority list of "when X, do Y" lines (FF12 gambit-style); a smarter list is
a faster route.

## Cards, mixes, lanes, orders and modifiers, as built

How these engine parts behave today, moved from their rows in `systems.md`.

Cards: one card per kind of work, tapped by hand or run in the mix (gathering, making, studying, resting, one-off story
steps, building stages, recipes). A one-off is a card with a cap; at its cap it moves to Completed, and the story can
raise the cap. Standing actions (a fire burning) are not cards. Semantics: engine `DESIGN.txt`, "CARDS".

Mixes: one mechanism for both layers, the player's time (hands) and the town's. A mix is a hands mix or a town mix by
the lanes its cards sit on (`engine.plan.mix_layer`); a town mix's share is a part of one person's time, the person
being the lane its card is on, each person's shares summing to at most 100%, and the running one is set by the town's
always rule, a SwitchMix order, never the player's switch (`app/ashfall_app/engine/mixruns.py`; engine `DESIGN.txt`,
"THE TOWN'S MIX"). A mix holding a completed card greys whole and falls through to the queue or the orders. A card
paused on a dry store gives its share to the rest of its mix on its lane until its pause lifts (a store a maker refills
at its hourly resume, a spent one, which nothing in play can make again, when an outcome refills it), each gain named
in `explain()` and shown on the page as the split that runs now: derived at the instant, never saved
(`app/ashfall_app/engine/spent.py`; engine `DESIGN.txt`, "SPENT"). Buildings running cards remain planned: pooled
work is a known gap.

Standing orders and the queue: an order's mix is a pushdown of one over the player's, read per layer (a town mix's
order never moves the hands' running mix), and a tap yields the mix. Planned: evaluation applies every verb that can
act at an instant, not only the first, so no lane idles on a ready order (engine `DESIGN.txt`, "Evaluation applies
every verb"). A story outcome installs a ruled lane's always rule as an ordinary order, and an answer can queue a hands
one-off as a When ready entry (engine `DESIGN.txt`, "Installed rule", "Queued one-off";
`app/ashfall_app/engine/installs.py`); a new save has neither, and nothing installs a rule that watches a store.
Content order cards are never built for the player: they feed the first rule's lesson and the hint dots. Where each
order stands (on, waiting, outranked, passed over) is served on the View as order_states (`engine.plan.order_states`),
and the Rules tab says why a rule is off under it (`app/client/src/ui/rulewhy.ts`). The page queues one tap of a step
that will turn ready by itself (When ready, held until its next completion), and a mix until a goal row lands (a goal
stint: a queued switch runs over the player's mix until it pops, engine `DESIGN.txt`, "Queue mix";
`app/client/src/ui/stint.ts`), and lists the queue as Next in the Rules tab (`app/client/src/game/queue.ts`).

Modifiers: buildings, tools, spells, prestige, seasons, injuries and supply are all modifiers, and a cap only rises.
Planned for combat: a side's and a threat's strength are targets too, a threat's raised only by its region's schedule
triggers, and a fight's odds join the effective stack while it runs (engine `DESIGN.txt`, "FIGHTS"). A card's
`while_running` entries on a side join the stack while it runs, at its share of its lane's time
(`app/ashfall_app/engine/heldentries.py`, "ENTRIES HELD WHILE A CARD RUNS"): derived from the lanes and running mixes
wherever the stack is read, never stored.

Lanes: tapping trades mix time one for one, so attention earns nothing. Tapping a card unready is a failed tap: no
time, nothing changed, its line at once (known at the tap, never chance). A glowing step not yet done cuts in on a
hands task the queue or a rule holds (a stage an order names too, its latch having fallen as the stage drank the
store), which takes it up again once the step lands, and a player's tap of a cure for a chip shown now cuts in on any
hands task but a cure, the task going to the queue's front if nothing else would take it up (engine `DESIGN.txt`,
"CUT-IN", "CURE CUT-IN", "ORDER CARD ON A STAGED BUILD"; `app/ashfall_app/engine/decisions.py`,
`app/ashfall_app/engine/cure_reading.py`). Other lanes (a drying rack, later buildings) never touch the player's time.
A ruled lane's person is in the town mix once they have joined, and a tap on that lane (a rule's) takes the whole of
the person while their shares yield, as a hands tap yields the hands' mix. A townsperson who works is a ruled lane: the
player's rules set its task (a single task, never a mix), the player never taps it, its rules' order is its priority,
and the view names the rule whose task it runs (engine `DESIGN.txt`, "Ruled lane", "Lane order", "THE TOWN'S MIX";
`app/ashfall_app/engine/plan.py`). A lane whose rules would start the same card again at each completion runs it as a
rate, as a mix runs its cards, and lands only when its task changes (engine `DESIGN.txt`, "REPEATING TAPS";
`app/ashfall_app/engine/retap.py`).
