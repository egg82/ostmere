// A stopped card in the running mix (CONTRACT.txt, "SPENT"): the engine says which cards of the running mix are paused
// or spent and which cards run their shares. The page words that and works out nothing.
import type { SpentShare, View } from "../api/types";
import type { Catalog } from "./catalog";
import { UI } from "./text";

/** The strip's note on a spent card: the store it is stopped on, which nothing can make again; "" when none is. */
export function spentNote(catalog: Catalog, view: View): string {
  const store = view.cards.find((c) => c.run === "spent")?.spent_store;
  return store ? catalog.text.fill(UI.spent, { store: catalog.storeLabel(store) }) : "";
}

/** One card's part of the split that runs now: its share plus what it gains, each gain with its source; a stopped
 * card's is 0. */
export interface RunningPart { card: string; bp: number; from: SpentShare[]; stopped: boolean }

/** The split the running mix runs now on `lane`, in the view's card order, or null while it is the split set: it
 * differs exactly while a card of the mix there is paused or spent. */
export function runningNow(catalog: Catalog, view: View, lane: string): RunningPart[] | null {
  const own = view.cards.filter((c) => c.share_bp > 0 && catalog.laneOf(c.card) === lane);
  if (!own.some((c) => c.run === "paused" || c.run === "spent")) return null;
  return own.map((c) => {
    const stopped = c.run === "paused" || c.run === "spent";
    const bp = stopped ? 0 : c.share_bp + c.gained.reduce((n, g) => n + g.share_bp, 0);
    return { card: c.card, bp, from: c.gained, stopped };
  });
}
