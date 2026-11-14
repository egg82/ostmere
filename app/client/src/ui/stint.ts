// Goal stints (CONTRACT.txt, "Goal stints"): "run {mix} until {goal}" as a queue entry. The mix editor's "Run until…"
// lists the goals the edit's dry run shows, each with its time if run, and under a store's goal that store's named
// shares not yet reached (a share of its cap, which keeps up as the cap grows; no time is served for those); Next names
// a stint by its mix and goal, and the one that runs says when its goal lands or that it never does at today's rates,
// and what binds it. Facts, never advice.
import type { Condition, GoalRow, QueueEntry, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { sample } from "../game/clock";
import { mixLabel } from "../game/orders";
import { controllingEntry, shareUntil, stintRow } from "../game/queue";
import { BP, levelWords, PRESETS } from "../game/storerule";
import { UI } from "../game/text";
import { el } from "./dom";
import { binds, goalLabel, goalLeft } from "./goaltimes";

/** One button per goal of `after` not met yet, each with its time if run, and under a store's its shares; `pick` takes
 * the chosen goal's `until`. */
export function goalPicker(catalog: Catalog, after: View, pick: (until: Condition) => void): HTMLElement {
  const list = el("div", "stint-goals");
  list.append(...after.goal_rows.filter((r) => r.lands_at !== after.at).flatMap((r) => {
    const b = el("button", "stint-goal");
    b.type = "button";
    b.append(el("span", "", goalLabel(catalog, r)), el("span", "stint-time", goalLeft(catalog, r, after.at)));
    b.addEventListener("click", () => pick(r.until));
    return r.store === null ? [b] : [b, ...shareGoals(catalog, after, r.store, pick)];
  }));
  return list;
}

/** The named shares of `store`'s cap its whole items have not reached, as one row of marks; none on a store with no
 * line. */
function shareGoals(catalog: Catalog, after: View, store: string, pick: (until: Condition) => void): HTMLElement[] {
  const line = after.ledger.find((l) => l.store === store);
  const q = catalog.content.scales.quantity_per_item;
  if (!line) return [];
  const cap = Math.floor(line.cap / q), shown = Math.floor(sample(line.segment, after.at) / q);
  const marks: Record<number, string> = { 2500: UI.levelMarkQuarter, 5000: UI.levelMarkHalf, 7500: UI.levelMarkThreeQuarters };
  const open = PRESETS.filter(([bp]) => bp > 0 && shown < Math.ceil((bp * cap) / BP));
  if (open.length === 0) return [];
  const row = el("div", "stint-shares");
  row.append(el("span", "stint-or", catalog.text.get(UI.stintOrUntil)), ...open.map(([bp, key]) => {
    const b = el("button", "quiet cond-preset", catalog.text.get(marks[bp] ?? key));
    b.type = "button";
    b.setAttribute("aria-label", catalog.text.fill(UI.goalStoreShare, { store: catalog.storeTitle(store), n: levelWords(catalog, { share: bp }) }));
    b.addEventListener("click", () => pick(shareUntil(store, bp)));
    return b;
  }));
  return [row];
}

/** The editor's button and, while `open`, the goal picker over `after`; `pick` takes the chosen row. */
export function stintParts(catalog: Catalog, after: View | null, open: boolean, disabled: boolean, toggle: () => void,
  pick: (until: Condition) => void): HTMLElement[] {
  const run = el("button", "quiet", catalog.text.get(UI.stintRun));
  run.type = "button";
  run.disabled = disabled;
  run.setAttribute("aria-expanded", String(open && !disabled));
  run.addEventListener("click", toggle);
  return !open || disabled || after === null ? [run] : [run, goalPicker(catalog, after, pick)];
}

/** A switch entry's words in Next: "{mix} until {goal}". */
export function stintWords(catalog: Catalog, view: View, entry: QueueEntry): string {
  const mix = entry.verb.kind === "switch_mix" ? mixLabel(catalog, entry.verb.mix_id) : "";
  const row = stintRow(view, entry.until);
  return catalog.text.fill(UI.stintEntry, { mix, goal: row ? goalLabel(catalog, row) : untilLabel(catalog, entry.until) });
}

/** For the stint whose mix runs now: when its goal lands (or never) and the line that binds it; nothing otherwise. */
export function stintFacts(catalog: Catalog, view: View, index: number): string | null {
  const entry = view.queue[index];
  if (entry?.verb.kind !== "switch_mix" || controllingEntry(view) !== index || view.mix_order !== null) return null;
  const row = stintRow(view, entry.until);
  if (!row) return null;
  const when = row.lands_at === null ? catalog.text.get(UI.goalNever) : catalog.text.fill(UI.goalIn, { d: goalLeft(catalog, row, view.at) });
  return `${when} · ${binds(catalog, row)}`;
}

/** The goal read off the condition itself, for a stint whose row has left view.goal_rows. */
export function untilLabel(catalog: Catalog, until: Condition): string {
  if (until.kind !== "at_least") return "";
  const w = until.watched;
  if (w.kind === "store_value" && until.value_of_cap) return catalog.text.fill(UI.goalStoreShare, { store: catalog.storeTitle(w.store), n: levelWords(catalog, { share: until.value }) });
  if (w.kind === "store_value") return catalog.text.fill(UI.goalStore, { store: catalog.storeTitle(w.store), n: catalog.format.items(until.value) });
  if (w.kind !== "skill_level") return "";
  const skill = catalog.skillLabel(w.skill);
  return catalog.text.fill(UI.goalLevel, { skill: skill.charAt(0).toUpperCase() + skill.slice(1), n: String(until.value) });
}
