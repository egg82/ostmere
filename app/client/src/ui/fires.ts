// Which running cards an order started. The view does not say what started a tap (CONTRACT.txt names no origin), so
// this infers it: a card that begins on a lane with no tap from the player, that a standing order whose condition holds
// taps and no queue entry does. `fresh` is the cards an order started in the latest view; `running` holds them while they run.
import type { View } from "../api/types";

const runningOf = (view: View | null): Set<string> =>
  new Set((view?.lanes ?? []).flatMap((l) => (l.running_card === null ? [] : [l.running_card])));

export class OrderFires {
  readonly running = new Set<string>();
  fresh: string[] = [];
  private readonly tapped = new Set<string>();

  /** The player tapped this card (a tap_card decision is on its way). */
  tap(card: string): void {
    this.tapped.add(card);
  }

  observe(view: View, prev: View | null): void {
    this.fresh = [];
    const now = runningOf(view);
    const before = runningOf(prev);
    for (const card of now) {
      if (before.has(card) || this.tapped.has(card)) continue;
      const ordered = view.orders.some((o, i) => view.orders_on[i] === true && o.then.kind === "tap_card" && o.then.card === card);
      const queued = (prev?.queue ?? []).some((q) => q.verb.kind === "tap_card" && q.verb.card === card);
      if (ordered && !queued) {
        this.fresh.push(card);
        this.running.add(card);
      }
    }
    for (const card of [...this.running]) if (!now.has(card)) this.running.delete(card);
    for (const card of [...this.tapped]) if (now.has(card) || !before.has(card)) this.tapped.delete(card);
  }
}
