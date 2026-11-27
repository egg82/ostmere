## The hands strip (the mix's slim view)

One row that says what the hands are doing, the mix's home. It takes no room, so no empty band shows, until the first
mix's offer (or once a mix or rule exists); it then arrives like any other new part, in its turn in the arrival queue,
and the cards below make way once. Until then each card's own bar says what the hands do. Once drawn it stays, and
the rows below apply.

| State | Shows |
|---|---|
| Tapping | `HANDS · Stand up` and the card's name; the bar itself stays on the card |
| Idle | `HANDS · idle` in grey |
| Mix offered (first time) | the two cards' names side by side and one button, `Show me` while the mix's lesson may start (the glow, if nothing else has it), which opens a new mix on the real editor where the lesson walks it. After the lesson is done or skipped with no mix made, the same button reads `New mix` and opens the editor with nothing built |
| Mix running | the split bar, one segment per card in its hue with no text inside, and a legend beneath naming each card and its share; under that the mix's name as plain text (a long one truncates, but gives way after the status text and the queue's head: a covered status keeps its width unseen, so the name is never squeezed for it). The rest arrive when they first mean something and then stay: `Mixes ▾` before the name once a mix is saved, `runs on` or `runs 7h` (never broken mid-value) once the ledger is there, and `Edit` at the end once a mix greys or an action card the first mix does not hold is in play |
| A tap holding the hands | whoever started it (the player, When ready, an answer's queued one-off, a rule, a cut-in), the bar is that card alone: one full segment in its hue, the legend naming it with its time left (`Stool 3 s`; no time while a rule repeats it). The name slot reads `then {mix}`, the mix that comes back, with `runs …` gone; a rule's tap also shows where the rule lets go. `next:` names the entry after it, never the step already running. When the tap lands, the mix's bar returns. No `paused` label: the bar already shows what runs (`game/holder.ts`, `ui/handsheld.ts`) |
| A card of the mix stopped (its store dry) | under the bar the player set, which never changes on its own, `running now` and the split that runs: each card at its share plus what it gains, `+25% from {card}` naming each source, and the stopped card's slice greyed, `{card} waiting`; a spent card also puts `{store} is used up` in the status. It comes through the arrival queue the first time; after that its row keeps its room and shows nothing while the splits match, so nothing under a finger moves when a store runs dry or refills. The town's rows show the same under each person's split (`ui/runningnow.ts`) |
| Greyed | the bar in grey with the cards left, a retired or completed card's share divided among them in proportion (the editor still shows it struck, until removed); under it `stopped · {card} done`, naming the card that left, in plain ink, since the grey bar alone still reads as work under way; and `Edit` |
| Any saved mix | `Mixes ▾` is the button that opens the Mixes list (the mixes only), so the way in says what it is; tapping a mix there makes it the default |
| A rule's mix running | that mix's bar, `Mixes ▾` and its name, where the rule lets go (`until 8 dry wood`, `until under 10 stones`; a rule with no band: `while under 2 dry wood`) where `runs …` would be, as a button that opens the Rules tab (its row and `Lately`), `then {mix}` after it (a queued goal stint's mix, else the player's; it gives way first when the row is short), and `Edit` (it edits that mix); a tap holding the hands still wins |
| A goal stint running | the stint's mix bar and its name, `until {goal}` where `runs …` would be (the goal as Next words it, `until Dead wood 30`), the same button into the Rules tab, and `then {mix}`, the player's mix that comes back when the goal lands |
| A rule's task on the hands | `HANDS · {task}` and where the rule lets go, the same button, as above |
| No mix running, mixes or rules saved | `Mixes ▾` in the meta slot, opening the list (or `Rules ▾` with only rules, opening the Rules tab) |
| Hint: a card the mix could take (once per card) | a quiet dot on the card itself (the new-card dot, `markNew`), no row and no sentence: a hands card in play, doable again, not in the player's own mix (saved, not greyed), tapped `hand_taps` times within `hand_taps_within_s` while a mix without it ran (opening.toml's `[repeat_offers]`, counted by the server, Step.repeats). Touching the card clears it and it is kept in the save (`Keeps.mixOffered`). It opens nothing and highlights nothing: every card could join a mix or be its own rule, so the game does not choose, and the player uses what the lessons taught. Never during a lesson, nor while the mix's lesson may still start. The first such card, once the first rule's lesson is behind, also starts the second mix's lesson (Lessons). Fits into: the new-card dot (`game/marks.ts`, `ui/fresh.ts`), detection `game/hints.ts` |
| Hint: a mix switch or an order card (once per chip) | the same dot on the chip in the story strip: a switch of the player's own mix made `switches` times under it within `switches_within_s` (Step.repeats, kept in `Keeps.switchOffered`), or a chip whose order card has no rule yet (once a page session), or a season's chore with no order card from its first showing while no rule is set on its store and test (`ChipInfo.chore`; once a page session): its rule is the player's to write. On a red ledger line whose order card has no rule, the dot sits on the line (the red line stays the signal; once a page session). Only once the first rule's lesson is behind; nothing is built, opened or highlighted. Fits into: as the card's |
| Hint: the first full store (once) | the same dot on the store's ledger line, the first time a store the player's mix or tap makes reaches its cap while another hands task could use the time and no rule watches it reach a level, once the player has seen a rule of theirs come on and let go (`game/caphint.ts`). No cap rule is installed in a new save; the dot opens nothing, and the cap rule's lesson (Lessons) starts from the line. Done or skipped, it never comes back. A player who ignores it loses only the overflow, which the full line shows. Fits into: as the card's, and lessons (`game/lessons.ts`) |
| Hint: the first dry store (once) | the same dot on the store's ledger line, the first time a card of the running mix stops on a store that ran dry (its line starved), no rule covers that store, and a hands card in play that makes it is ready and outside the mix (`game/dryhint.ts`), once rules are taught. The dot opens nothing, and the dry store's lesson (Lessons) starts from the line. Done or skipped, it never comes back. A spent card (nothing in play can refill its store) is not marked: no card added would help. Fits into: as the first full store's |
| First rule's entry (after the end) | on its own row under the mix row, only while the first rule's lesson may start: a chip's rule, `While {chip} → {task}`, and `Show me`, which opens a new rule on the real editor and the lesson walks it. It comes the first time the chip is on with no rule on its store, once the end lines have been read, and stays until a rule is set (not when the chip clears), so the strip moves once, on its arrival. Once the lesson is done or skipped no row is drawn: the chip carries the hint dot. No offer builds a mix or a rule |

**On a phone the mix's controls and the rows under the mix row (a chip's rule offer) sit under the pinned strip, not in
it** (`Hands.rows`, placed by the screen right under the pin): they scroll with the cards, so a prompt does not cost the
cards their room, and the pin keeps the mix's bar, legend and name (`Main ▾`). The controls arrive with the strip; the
rows still arrive through the arrival queue, and a row that arrives out of sight shows at once. On a wider screen they
stay in the strip.

The dividers on the strip are draggable for a quick change; the strip never shows a 0% divider (a card joins with a
real share, see the editor).

**A lane run by rules** (a townsperson who works: api `CONTRACT.txt`, "A lane run by rules") gets a row in the Town
view, under the town's people, in their row form: a face, the lane's label (a later label once its unlock is held), what it
does (the task's name, or `idle`), the task's bar, and `Change`. A row arrives through the arrival queue the first time
its lane is in view, then stays. `Change` opens the person's
page (`ui/personpage.ts`), which takes the card area's place and is laid out as the Tasks page is: once the person has
joined, their split of the town's mix as a share bar (`ui/personmix.ts`); their cards drawn in full by the Tasks panel's card
face (`ui/cardpick.ts`, a lane's crafts in their section after the rest), a tap on one joining it to their time or taking it
out, a divider setting the split, each change sent as it is made with no Save; then the rules that tap their cards, each a
button into the Rules tab. A capped card, a one-off, is never in the town's mix (a mix greyed by a finished build would idle the
person: `engine/DESIGN.txt`, "THE TOWN'S MIX"); a tap on it has the person do its next completion, as a tap on one of
yours does, with no rule made, and then they go back to their mix. While it runs the card
counts down and fills its bar as a Tasks card does, and their split bar, on the page and on their Town row, is that card
alone with its time left and "then {their split}", as the hands strip draws a tap. Every person's row, joined or not, has its own Change, and a quiet dot on it marks a task not
yet in front of the player until their page is opened; the Town tab wears the same dot while any person's does. A rule's button opens the lane's task editor: the rule editor's
simple view with only `Do` (the lane's tasks as the same card faces), the rule's sentence and Save; Save changes that
rule's task in place (its condition kept) or adds the always rule. The lane's tasks are never cards in Tasks or Done:
the page and the editor are their only way in. Fits into: the Town view (`ui/lanerows.ts`, owned by `ui/hands.ts`), the
Rules tab's editor (`ui/laneedit.ts`), the hands' share bar (`ui/sharebar.ts`).

