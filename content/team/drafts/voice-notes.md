# Day one: the voice pass

Spoilers: under `content/`, never shown to the owner. Read every `l_*` line and label in `day_one.toml` in player order
against `opening.toml`. Lines not listed here were read and left as picked.

## Lines changed (6)

| Key | Why |
|---|---|
| l_smoke_roots | "keep" straight after l_cooking_open's "keeps", same instant; the turn ("they stop being roots") kept |
| l_smoke_fail | "quiet" also in l_first_catch, which can play in the same visit |
| l_cooking_2 | carried its level label's words ("a bigger batch") |
| l_b3_4 | "larder" back to back with l_b3_3; "sums for two" still carries the cost |
| l_camp_5 | echoed its label, and "takes more" was false: the rack takes the same and yields more |
| l_camp_6 | "for two" right after l_b3_4's; "half more" read wrong. "half as much again" was tried and dropped: "again" is a must-not |

## Labels changed (6 of 29)

| Key | Why |
|---|---|
| action_visitor | "Gone missing" pointed at a taker. "Losses" is true, mundane, names no one, and is no penalty |
| store_h7_clock | never drawn (below), but the label ships in the content payload, so "visit" was a spoiler in devtools |
| camp_pays_5 | "the rack" means the drying rack in the opening (l_dry_fail, ui.end.body); and the effect is output, not intake |
| up_lean_to | the opening's upsides name the effect ("Faster rest", "Slower burn"); the lean-to slows weariness |
| up_larder | "Food keeps" claimed spoilage the rules don't have; the larder raises roots and smoked caps |
| action_n1_eating | "Two eating" sat beside the opening's own "Eating" and read as double; shown only from B3 |

## Hidden stores

store_h7_clock and store_stock_ready are in no `unlock_kind = "store"` entry (opening `start`, any trigger or card), so
`gates.is_unlocked` (engine/gates.py:14) is false for them; `view._ledger` (engine/view.py, the `continue` on a locked
store) leaves them out of view.ledger. Every client surface that draws a store label reads view.ledger or Card.needs
(inputs then requires; no card names either store). So neither is ever drawn.

## l_hungry in day one

Holds: "on nothing" is the stomach, not the stores, so it reads true with food in the larder, on return or watching.
