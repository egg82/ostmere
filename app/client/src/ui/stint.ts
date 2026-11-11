// Goal stints (CONTRACT.txt, "Goal stints"): "run {mix} until {goal}" as a queue entry. The mix editor's "Run until…"
// lists the goals the edit's dry run shows, each with its time if run; Next names a stint by its mix and goal, and the
// one that runs says when its goal lands or that it never does at today's rates, and what binds it. Facts, never advice.
import type { Condition, GoalRow, QueueEntry, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { mixLabel } from "../game/orders";
import { controllingEntry, stintRow } from "../game/queue";
import { UI } from "../game/text";
import { el } from "./dom";
import { binds, goalLabel, goalLeft } from "./goaltimes";

/** One button per goal of `after` not met yet, each with its time if run; `pick` takes the chosen row. */
export function goalPicker(catalog: Catalog, after: View, pick: (row: GoalRow) => void): HTMLElement {
  const list = el("div", "stint-goals");
  list.append(...after.goal_rows.filter((r) => r.lands_at !== after.at).map((r) => {
    const b = el("button", "stint-goal");
    b.type = "button";
    b.append(el("span", "", goalLabel(catalog, r)), el("span", "stint-time", goalLeft(catalog, r, after.at)));
    b.addEventListener("click", () => pick(r));
    return b;
  }));
  return list;
}

/** The editor's button and, while `open`, the goal picker over `after`; `pick` takes the chosen row. */
export function stintParts(catalog: Catalog, after: View | null, open: boolean, disabled: boolean, toggle: () => void,
  pick: (row: GoalRow) => void): HTMLElement[] {
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
  if (w.kind === "store_value") return catalog.text.fill(UI.goalStore, { store: catalog.storeTitle(w.store), n: catalog.format.items(until.value) });
  if (w.kind !== "skill_level") return "";
  const skill = catalog.skillLabel(w.skill);
  return catalog.text.fill(UI.goalLevel, { skill: skill.charAt(0).toUpperCase() + skill.slice(1), n: String(until.value) });
}
