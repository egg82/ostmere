## The mix editor

Opened from the strip's `Edit` (or from a greyed strip), or from `New mix` in the Mixes list or a rule slot's picker.
On desktop it replaces the card area beside the art, which stays visible; on a phone it is a full-height sheet
whose top shows the strip.

```
┌──────────────────────────────────────────────┐
│ Name [ Main                    ]   Save  ✕   │
│                                              │
│ [ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓|▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ] │  drag dividers; drag a segment off, or tap ✕ on its row
│ ■ Woodcutting 60%  ■ Scavenge 40%            │  the legend, following a drag
│                                              │
│ per minute        now   →   after            │  live, before Save; and the goal rows, right under the
│ damp wood        +6.0   →   +9.0             │  bar so a drag shows its effect without scrolling
│ stones           +5.0   →   +4.0             │
│ Run until…                                   │
│                                              │
│ Woodcutting   60%   damp wood +9/min     ✕   │  each entry shows what it does at its share
│ Scavenge      40%   stones +4/min        ✕   │
│ Gather (retired) ~~struck~~                ✕ │  a retired card, shown until removed
│                                              │
│ + Add                                        │  one control: opens the cards that can join, in place
│ ┌────────┐ ┌────────┐ ┌────────┐             │  tap or drag in; joins with a real share
│ │Forage •│ │ Rest   │ │Woodcut•│             │
│ └────────┘ └────────┘ └────────┘             │
│                                   Delete mix │
└──────────────────────────────────────────────┘
```


- The **before → after** totals update while a divider moves, before anything is committed. They list only the stores
  the edit changes, and are not drawn until it changes something; for a mix that Save will not run, the second column
  reads `if run`. `Save` commits; `✕` leaves without a change.
- **`+ Add` is folded** so the editor does not grow with every unlocked card. A tap opens the cards that can join in
  place and a second tap closes it; picking a card leaves it open, so several can join in a row. It opens by itself
  when a lesson's step points at a card inside it, and a new card's dot shows on `+ Add` while it is closed.
- **Saving never changes which mix runs** (`decisions.md`, "The mix"). Editing the mix that runs changes what runs;
  saving a new or another mix only saves it, and the Mixes list runs it. A rule slot's `New mix` points that rule at the
  new mix.
- A card joining takes an equal slice from the others (two at 50% plus one becomes three at a third). A card never
  joins at 0%.
- The name field is there from the first edit, pre-filled; the player may leave it. The header is one row, Name then
  `Save` and `✕` as a group; the name field shrinks first, and on a phone the group wraps as one. `Save as new` sits at
  the foot, left of `Delete mix`, when editing a saved mix; it keeps the original and is off while the name is empty or
  already a saved mix's.
- `New mix` opens the editor with no cards and a pre-filled name no saved mix has. `Save` stays off until a card has
  been added and the name is free; saving creates the mix.
- A typed name never reaches another mix. `Save` is off for another saved mix's name (it would overwrite that mix) and
  for a name beginning as the game's own mixes do (`limits.reserved_mix_prefix`), and one line under the name says
  which; the server refuses the same.
- `Delete mix` asks once, in place (`Delete? Yes · No`). A mix named by a rule (`a rule uses it`; in the Mixes list
  `used by 2 rules`), or nested in another, says so instead of deleting.
- Renaming a mix that rules run points those rules at the new name; renaming the player's own keeps it the player's
  own.
- Rates are facts: `runs on` or `runs 7h`, `empty in 20m`. Nothing in the editor says balanced, efficient or better.

## The Mixes list

From the strip's name ▾ (or its `Mixes ▾`): the player's saved mixes and nothing else, the player's own first. A town
mix is never listed: it runs by rules and is changed in the town's editor. A centred sheet
on a desktop, a full-width bottom sheet on a phone (as every sheet there, "Phone"; scrolling). Each mix's row draws its split as a small bar of hues with the legend under it.

- **Tapping a mix makes it the default,** what runs when no rule's mix does; while a rule's mix runs, it sets what
  comes back, not what runs now. Each mix it can run says `Run`; ● and `running` (or, for the player's own, how long it
  runs) mark the mix running now.
- A mix rules run says how many (`used by 2 rules`, `used by a rule`) where `Delete mix` would be; one nested in
  another says so. A greyed mix (it holds a retired or completed card) can't be run, only edited or deleted, so a
  saved mix never quietly does something else.
- `Edit` on every row; `New mix` last.

