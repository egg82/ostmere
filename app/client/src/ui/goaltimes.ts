// The editors' goal rows (CONTRACT.txt, "Goal rows"): each goal whose time or limit a dry run changes, now → after,
// and under it the line that binds it after the edit, as the server states it. The page computes no rate or time.
import type { GoalRow, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el } from "./dom";

const key = (r: GoalRow): string => `${r.kind}|${r.store ?? ""}|${r.skill ?? ""}|${r.target}`;

/** The rows, or none when the edit moves no goal. `afterHead` names the second column ("after", "if run", ...). */
export function goalRows(catalog: Catalog, view: View, after: View | null, afterHead: string): HTMLElement[] {
  if (after === null) return [];
  const was = new Map(view.goal_rows.map((r) => [key(r), r]));
  const moved = after.goal_rows.flatMap((r) => {
    const before = was.get(key(r));
    if (!before) return [];
    const now = goalLeft(catalog, before, view.at), then = goalLeft(catalog, r, after.at);
    return now !== then || binds(catalog, before) !== binds(catalog, r) ? [{ r, now, then }] : [];
  });
  if (moved.length === 0) return [];
  const { text } = catalog;
  const head = el("div", "totals-row totals-head goal-head");
  head.append(el("span", "", text.get(UI.goalHead)), el("span", "", text.get(UI.now)), el("span", "", "→"), el("span", "", afterHead));
  return [head, ...moved.flatMap(({ r, now, then }) => {
    const row = el("div", "totals-row goal-row");
    row.append(el("span", "totals-store", goalLabel(catalog, r)), el("span", "", now), el("span", "totals-arrow", "→"),
      el("span", "totals-after changed", then));
    return [row, el("div", "goal-binds", binds(catalog, r))];
  })];
}

/** The goal: a store and its target, or a skill and its level. */
export function goalLabel(catalog: Catalog, r: GoalRow): string {
  const { text } = catalog;
  if (r.store !== null) return text.fill(UI.goalStore, { store: catalog.storeTitle(r.store), n: catalog.format.items(r.target) });
  const skill = catalog.skillLabel(r.skill ?? "");
  return text.fill(UI.goalLevel, { skill: skill.charAt(0).toUpperCase() + skill.slice(1), n: String(r.target) });
}

/** The time left until the row lands, counted from `at`, or never. */
export function goalLeft(catalog: Catalog, r: GoalRow, at: number): string {
  return r.lands_at === null ? catalog.text.get(UI.goalNever) : catalog.format.duration(r.lands_at - at);
}

/** The line that binds the goal: the dry store a card moving it waits on, else its own line. */
export function binds(catalog: Catalog, r: GoalRow): string {
  const { text, format } = catalog;
  if (r.limit) return text.fill(UI.goalLimited, { store: catalog.storeLabel(r.limit.store), n: format.perMinute(r.limit.in_per_hour) });
  if (r.store !== null) return `${catalog.storeLabel(r.store)} ${format.perMinute(r.per_hour)}`;
  return text.fill(UI.goalXp, { n: format.perMinute(r.per_hour) });
}
