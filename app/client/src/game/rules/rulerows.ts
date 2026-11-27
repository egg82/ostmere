// A rule's entries in the chronicle, read off what the rules did lately (Step.rule_runs, contract/rule-runs.txt "Rule runs"):
// each run's last start and last let-go, the rule in the player's words, and as cause the store's level then (a chip's
// rule or a count or level rule has none: its words already say what it waits on). The runs are a summary, so starts a
// later start replaced before any page saw them are not entries. Pure.
import type { Order, RuleRun, View } from "../../api/types";
import type { Catalog } from "../page/catalog";
import type { Entry } from "../book/chronicle";
import { chipOf, ruleWords, storeRule } from "./orders";
import { UI } from "../page/text";

/** One entry and the id that keeps it from being added twice as later Steps repeat the run. */
export interface RuleEntry {
  id: string;
  entry: Entry;
}

/** A rule in the player's words, "when → action"; null when it cannot be worded. */
export function ruleText(catalog: Catalog, view: View, order: Order): string | null {
  const words = ruleWords(catalog, view, order);
  return words === null ? null : `${words.when} → ${words.action}`;
}

export function ruleEntries(catalog: Catalog, view: View, runs: readonly RuleRun[]): RuleEntry[] {
  return runs.flatMap((run) => {
    const rule = ruleText(catalog, view, run.order);
    if (rule === null) return [];
    const store = chipOf(catalog, run.order.when) ? null : storeRule(catalog, run.order)?.store ?? null;
    const cause = (level: number | null): string | null => (store === null || level === null ? null
      : catalog.text.fill(UI.causeStore, { store: catalog.storeLabel(store), n: catalog.format.items(level) }));
    const one = (on: boolean, at: number, level: number | null): RuleEntry => ({
      id: `rule:${JSON.stringify(run.order)}:${on ? "on" : "off"}:${at}`,
      entry: { text: catalog.text.fill(on ? UI.chronRuleOn : UI.chronRuleOff, { rule }), at, kind: "rule", cause: cause(level) },
    });
    return [
      ...(run.on_at === null ? [] : [one(true, run.on_at, run.on_level)]),
      ...(run.off_at === null ? [] : [one(false, run.off_at, run.off_level)]),
    ];
  });
}
