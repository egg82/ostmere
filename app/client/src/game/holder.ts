// What holds the hands, read off the view (docs/design/opening-screen.md, "The hands strip"), so the mix bar can show
// what the hands are actually doing: a tap on the hands (by hand, a When ready step or an answer's queued one-off, a
// rule's tap, a cut-in), else a rule's mix, else a goal stint's mix, else the player's own mix. Each holder but the
// player's mix names the mix the hands go back to when it lets go.
import type { View } from "../api/types";
import { controllingEntry } from "./queue";

export type Holder =
  | { kind: "own" }
  /** `endsAt`: when the tap lands (null while a rule repeats it); `order`: the rule that taps it, if one does. */
  | { kind: "tap"; card: string; endsAt: number | null; order: number | null; then: string | null }
  | { kind: "rule"; order: number; then: string | null }
  | { kind: "stint"; entry: number; then: string | null };

/** The holder of the hands, as the engine decides it (engine DESIGN.txt, "Order mix", "Queue mix"): a hands tap
 * yields whichever mix runs; a rule's mix runs over a stint's, and a stint's over the player's. */
export function handsHolder(view: View): Holder {
  const lane = view.lanes.find((l) => l.lane === "hands");
  const stint = stintEntry(view);
  const stintMix = stint === null ? null : switchedTo(view, stint);
  const back = (mix: string | null): string | null => (mix === view.running_mix_id ? null : mix);
  if (lane?.running_card) return { kind: "tap", card: lane.running_card, endsAt: lane.completes_at, order: lane.order, then: view.running_mix_id };
  if (view.mix_order !== null) return { kind: "rule", order: view.mix_order, then: back(stintMix ?? view.active_mix_id) };
  if (stint !== null) return { kind: "stint", entry: stint, then: back(view.active_mix_id) };
  return { kind: "own" };
}

/** The index of the controlling queue entry when it is a switch (a goal stint), else null. */
function stintEntry(view: View): number | null {
  const i = controllingEntry(view);
  return i !== null && view.queue[i]?.verb.kind === "switch_mix" ? i : null;
}

function switchedTo(view: View, entry: number): string | null {
  const verb = view.queue[entry]?.verb;
  return verb?.kind === "switch_mix" ? verb.mix_id : null;
}
