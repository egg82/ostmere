# Day two: the voice pass

Spoilers: under `content/`, never shown to the owner. Read every `l_*` line and label in `day_two.toml` in the brief's
order, after day one's l_b3_1..l_b3_4 and l_camp_6, against `opening.toml` and `day_one.toml`. Lines not listed here
were read and left as picked.

## Lines changed (4)

| Key | Why |
|---|---|
| l_her_rule | "goes on" is l_night_2a's ending, and on two routes the rule is given in the same visit the night's lines unwrap |
| l_night_2b | "she feeds the fire" played straight into l_morning_3's "the fire fed" (the four night lines unwrap together). Her silence now carries the turn through an ordinary act |
| l_woodstack | its second sentence was the upside label word for word ("Room for twice the dry wood"), which sits on the card just above it |
| l_offer_2 | "she asks you" right after l_offer_1's "asks you something"; now the asking is hers, unquoted, and still names neither answer as the right one |

## Labels written (42)

Cards are imperatives, upsides name the effect, aims are lowercase sentences under 40 characters, level pays are short
noun phrases for the find, as day one's are.

Weighed:

- **lane_n1 "Her hands"**: her work, never her name, beside the player's "Hands". After l_name, "Lucy".
- **o_cart and its answers**: the question asks *who* goes, so both answers ("You go", "She goes") answer it equally;
  the costs are parallel ("{d} of your time" / "{d} of her time"), filled with the same walk's duration.
- **aim_cart "get back what she left on the ridge."**: the brief's "bring back" read as a promise the day breaks, and
  as a nudge toward Go; "get back" holds for either answer and says nothing about what is still there.
- **aim_after "dig in. something knows you're here."**: "keep the camp worth keeping" echoed day one's aim_worth and
  aim_hold, which would hint at having been here before.
- **aim_night_2**: "see the night out" was the obvious line and is day one's aim_night; avoided for the same reason.
- **pays_old_bed "an old root bed"**: "an old bed" alone reads as furniture in a ruin.
- **pays_tighter_rack "a tighter rack"**: a noun phrase like the finds; the line beside it says how.
- **dayend2_***: day one's end card's pattern. dayend2_1 says the camp runs on, and she with it; dayend2_2 is the
  "still being written" line, now for day three.

## Never-drawn stores and actions

store_evening_2, store_night_2, store_walk, store_walk_out and store_n1_worked are in no `unlock_kind = "store"`
entry in any chapter, so the ledger never shows them. make_room's `requires` on night_2 reaches Card.needs, but the
client draws no need row for a store never shown (`client/src/ui/cardneeds.ts`, the `seen` set). action_evening_2,
action_night_2 and action_walk_out are unlocked, but a standing action's label is drawn only as the largest drain on a
ledger line (`client/src/ui/ledger.ts`), and these three only make into hidden stores. Their labels ship in the
content payload: "evening", "night", "walk", "clock", "work"; "Evening", "Night", "Walk". None names who or what.

## Left for the chapter's release

With every line written, `test_the_guard_sees_an_unwritten_line` fails: it asserts day two, while in `IN_WRITING`,
still holds an unwritten line. Moving day two into `CHAPTERS` is the release step, not this pass.
