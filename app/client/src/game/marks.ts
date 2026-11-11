// Which controls carry the quiet "new" dot (decisions.md, "Shown in the design, not claimed"). A dot marks something the
// player can act on and has not yet; plain text never gets one. Any interaction clears it, and so does the thing being
// put to work: held by a saved mix, named by a rule, or running.
import type { View } from "../api/types";

/** Cards that are already at work: in any saved mix, named by a rule or a queued entry, or running in a lane. */
export function inUse(view: View): Set<string> {
  const used = new Set<string>();
  for (const m of view.mixes) for (const c of m.components) if (c.kind === "card_share") used.add(c.card);
  for (const verb of [...view.orders.map((o) => o.then), ...view.queue.map((q) => q.verb)]) if (verb.kind === "tap_card") used.add(verb.card);
  for (const l of view.lanes) if (l.running_card !== null) used.add(l.running_card);
  for (const c of view.cards) if (c.run !== null) used.add(c.card);
  return used;
}

/** The controls (by card id) that still carry a dot. */
export class NewMarks {
  private readonly ids = new Set<string>();

  has(card: string): boolean {
    return this.ids.has(card);
  }

  add(card: string): void {
    this.ids.add(card);
  }

  /** The player touched the card, or joined it to a mix. */
  clear(card: string): void {
    this.ids.delete(card);
  }

  /** Clears every card the view shows at work. */
  sync(view: View): void {
    for (const card of inUse(view)) this.ids.delete(card);
  }
}
