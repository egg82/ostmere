// A stint that popped at its goal, in Lately (CONTRACT.txt, "Rule runs", "Ended stint"): its mix and goal as Next words
// them, then how long it ran, when its goal landed and what the save gained while it ran. Facts the save recorded.
import type { RuleRun } from "../api/types";
import type { Catalog } from "../game/catalog";
import { mixLabel } from "../game/orders";
import { UI } from "../game/text";
import { untilLabel } from "./stint";

/** "{mix} until {goal}", read off the entry's order: its switch and its until. */
export function stintLine(catalog: Catalog, run: RuleRun): string {
  const mix = run.order.then.kind === "switch_mix" ? mixLabel(catalog, run.order.then.mix_id) : "";
  return catalog.text.fill(UI.stintEntry, { mix, goal: untilLabel(catalog, run.order.when) });
}

/** "ran {d} · goal landed {ago} ago · made {n} {store}" at time `t`; the first part only when the stint's start was
 * seen, the last only when the server served a gain. */
export function stintFacts(catalog: Catalog, run: RuleRun, t: number): string {
  const { text, format } = catalog;
  const parts: string[] = [];
  if (run.on_at !== null && run.off_at !== null) parts.push(text.fill(UI.stintRan, { d: format.duration(run.off_at - run.on_at) }));
  if (run.off_at !== null) parts.push(text.fill(UI.stintLanded, { ago: format.duration(Math.max(0, t - run.off_at)) }));
  const made = madeFact(catalog, run);
  if (made) parts.push(made);
  return parts.join(" · ");
}

/** The gains the server served (at most two), worded; "" for none. */
function madeFact(catalog: Catalog, run: RuleRun): string {
  const { text, format } = catalog;
  const [a, b] = run.made;
  if (!a) return "";
  const first = { n: format.items(a.quantity), store: catalog.storeLabel(a.store) };
  return b ? text.fill(UI.stintMadeTwo, { ...first, m: format.items(b.quantity), store_b: catalog.storeLabel(b.store) })
    : text.fill(UI.stintMade, first);
}
