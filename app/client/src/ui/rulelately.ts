// What the rules did lately (docs/design/opening-screen.md, "Lately"): the Rules tab's last block, from Step.rule_runs
// (CONTRACT.txt, "Rule runs"), in the server's order, the most recent change first. One entry per rule the view still
// has: its words, then how many times it came on, its last start and, once it has let go since, its last let-go, each
// with the store's level then (never a chip's: its store is never a number) and how long ago by the frame's clock.
import type { Order, RuleRun, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { chipOf, ruleWords, storeRule } from "../game/orders";
import { unplacedKey } from "../game/nextrow";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import { madeFact, stintFacts, stintLine } from "./stintlately";

const same = (a: Order, b: Order): boolean => unplacedKey(a) === unplacedKey(b);

/** The entries to draw: those whose rule the view still has, and those the game ended (their rule is gone). */
export function shownRuns(view: View, runs: readonly RuleRun[]): RuleRun[] {
  return runs.filter((r) => r.ended !== null || view.orders.some((o) => same(o, r.order)));
}

/** An ended entry's one line: its rule worded, and why the game removed it (the person: the name of the lane of the card
 * the rule taps, else the lane's label). */
export function endedLine(catalog: Catalog, view: View, run: RuleRun): string {
  const { text } = catalog;
  const words = ruleWords(catalog, view, run.order);
  const rule = words ? `${words.when} → ${words.action}` : "";
  if (run.ended !== "left") return text.fill(UI.ruleEndedSeason, { rule });
  const lane = run.order.then.kind === "tap_card" ? catalog.laneOf(run.order.then.card) : "";
  const name = catalog.lanes.get(lane)?.name_key;
  return text.fill(UI.ruleEndedLeft, { rule, person: name ? text.get(name) : catalog.laneLabel(lane) });
}

/** The quiet line under an entry, at time `t`. */
export function runFacts(catalog: Catalog, run: RuleRun, t: number): string {
  if (run.ended === "stint" || run.ended === "dry") return stintFacts(catalog, run, t);
  const { text, format } = catalog;
  const store = chipOf(catalog, run.order.when) ? null : storeRule(catalog, run.order)?.store ?? null;
  const when = (bare: string, withLevel: string, at: number, level: number | null): string => {
    const ago = format.duration(Math.max(0, t - at));
    return store === null || level === null ? text.fill(bare, { ago })
      : text.fill(withLevel, { have: format.items(level), store: catalog.storeLabel(store), ago });
  };
  const parts = [run.starts === 1 ? text.get(UI.ruleRanOnce) : text.fill(UI.ruleRan, { n: format.count(run.starts) })];
  if (run.on_at !== null) parts.push(when(UI.ruleCameOn, UI.ruleCameOnAt, run.on_at, run.on_level));
  if (run.off_at !== null && run.off_at >= (run.on_at ?? 0)) parts.push(when(UI.ruleLetGo, UI.ruleLetGoAt, run.off_at, run.off_level));
  const made = madeFact(catalog, run);
  if (made) parts.push(made);
  return parts.join(" · ");
}

/** The heading and two lines per entry, at the view's time; nothing when no entry is shown. */
export function latelyRows(catalog: Catalog, view: View, runs: readonly RuleRun[]): HTMLElement[] {
  const shown = shownRuns(view, runs);
  if (shown.length === 0) return [];
  const rows = shown.flatMap((run, i) => {
    if (run.ended !== null && run.ended !== "stint" && run.ended !== "dry") return [el("div", "lately-rule lately-line", endedLine(catalog, view, run))];
    const words = ruleWords(catalog, view, run.order);
    const facts = el("div", "lately-facts lately-line", runFacts(catalog, run, view.at));
    facts.dataset.run = String(i);
    const rule = run.ended === "stint" || run.ended === "dry" ? stintLine(catalog, view, run) : words ? `${words.when} → ${words.action}` : "";
    return [el("div", "lately-rule lately-line", rule), facts];
  });
  return [el("h3", "rules-next lately-line", catalog.text.get(UI.ruleLately)), ...rows];
}

/** Each drawn entry's facts at time `t`: how long ago moves with the clock. */
export function retickLately(catalog: Catalog, view: View, runs: readonly RuleRun[], root: ParentNode, t: number): void {
  const shown = shownRuns(view, runs);
  for (const line of root.querySelectorAll<HTMLElement>(".lately-facts")) {
    const run = shown[Number(line.dataset.run)];
    if (run) setText(line, runFacts(catalog, run, t));
  }
}
