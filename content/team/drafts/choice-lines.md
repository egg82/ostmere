# The craft choice: order lines

Spoilers: under `content/`, never shown to the owner. Two lines answer which craft the player built first, in the register
the owner asked for: second person, dry, about the decision itself, and the player left to live with it.

## The moment

Both lines land as `read_by_fire` starts with one craft built and the other not (`t_stool_first`, `t_fireback_first`
in `opening.toml`). The moments the brief suggested (the fire burning low, the next tiredness) never fall inside the
gap on any simulated route: the second craft follows the first by 20-35 s, with dry wood still near 5 and energy
above the tired chip's 3, so a line waiting for them would almost never play. Reading is the first thing either craft
opens, it is where the player sits at the fire, and it is where both upsides would be felt. Landing as it *starts*
leaves `l_read` (P6) the last word 6 s later. A player who builds both before reading gets neither line, which is
right: nothing is missing.

States (also in `opening-v2.md`, "Line moments"): the fire burning, or out for want of dry wood; any chips; the
book not yet read (this is the reading). So no line may claim the fire is burning now.

## l_stool_first (stool built, no fireback)

| Candidate | Notes |
|---|---|
| "you decided a seat mattered more. the fire, with nothing at its back, is already wanting wood." | closest to the owner's paraphrase, but "mattered more" states the comparison the reader should make |
| **"you got a seat first. the fire, with nothing at its back, already wants wood."** | the choice as a plain fact; "nothing at its back" names the missing fireback without the word; "already wants wood" is true burning or out |
| "the seat first, then. you settle in to read, and the fire's already wanting wood." | "settle in" cushions the turn; "then" reads as the narrator shrugging rather than the player choosing |

Pick: the second. A first draft, "you read in comfort, and get up every few pages to feed the fire", was dropped: six
seconds later `l_read` is on the first page, and with no dry wood there is nothing to feed.

## l_fireback_first (fireback built, no stool)

| Candidate | Notes |
|---|---|
| "you decided the fire needed a back more than you needed a seat. you read on your knees." | states the joke; long |
| **"the fire got a back to lean on first. you read on your knees."** | the fire got furniture before you did, left for the reader; picks up `l_fireback`'s "the fire's back"; true in every state |
| "the fire first, then. you read on your knees on the cold stone." | true and dry, but "cold" is false while the fire burns, and the joke is thinner |

Pick: the second. "it burns slow" was dropped from every draft: false while the fire is out.

## A payoff line when both stand: none

The second craft lands with its own line, and `l_settled` ("somewhere to stay") closes the settling steps soon after
on most routes. A third line at the pair's completion would crowd that moment and say what `l_settled` already says.
