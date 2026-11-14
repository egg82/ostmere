// What covers a ledger line (docs/design/redesign.md, "Ledger"; CONTRACT.txt, the ledger's white and red): something
// that keeps its store fed (LedgerLine.covered, the server's), or one of the player's rules drawing the store down as it
// means to. Read off the view only.
import type { LedgerLine, Order, View } from "../api/types";

type Test = "at_least" | "at_most";

/** Rule `order`'s condition watches `store`'s amount (with `test`, when given). */
export function watches(order: Order, store: string, test?: Test): boolean {
  const { when } = order;
  return when.kind !== "after_time" && when.watched.kind === "store_value" && when.watched.store === store && (test === undefined || when.kind === test);
}

/** The first rule watching this store's amount, or -1. */
export function ruleOnStore(view: View, store: string): number {
  return view.orders.findIndex((o) => watches(o, store));
}

/** `runner` is what `order` runs: its task, or a card of its mix. */
function runs(view: View, order: Order, runner: string): boolean {
  const { then } = order;
  if (then.kind === "tap_card") return then.card === runner;
  return then.kind === "switch_mix"
    && view.mixes.some((m) => m.id === then.mix_id && m.components.some((c) => c.kind === "card_share" && c.card === runner));
}

/** The rule drawing this line down as it means to, or -1: it is on, its condition is "n or more" of the store (it runs
 * while there is enough, down to where it lets go), and a card it runs is among what takes from the store. */
export function spendingRule(view: View, line: LedgerLine): number {
  return view.orders.findIndex((o, i) => view.order_states[i] === "on" && watches(o, line.store, "at_least")
    && line.contributions.some((c) => c.per_hour < 0 && runs(view, o, c.runner)));
}

/** Something keeps the store fed, or a rule of the player's is drawing it down as it means to. */
export function coveredLine(line: LedgerLine, view: View): boolean {
  return line.covered || (line.falling && spendingRule(view, line) >= 0);
}

/** The rule a line's mark opens: the one drawing it down, else the first watching it; -1 for none. */
export function lineRule(view: View, line: LedgerLine): number {
  const spending = spendingRule(view, line);
  return spending >= 0 ? spending : ruleOnStore(view, line.store);
}
