// What a skill's prestige shows, read from the view and the content alone (CONTRACT.txt, "PRESTIGE PHASES"): a menu
// node's change as plain numbers before and after one more rank (never a verdict on it), the levels waiting at the top,
// and which skills reached their top between two views (the line a return brings, at its time).
import type { MenuNode, SkillBar, SkillPrestige, View } from "../api/types";
import type { Catalog } from "./catalog";
import { UI } from "./text";

/** The node's target as its numbers read now and with one more rank, each at a full share: a make per minute, a
 * card's time per completion, a store's cap in items. Empty for a node the content does not name. */
export function changeText(catalog: Catalog, menu: MenuNode): string {
  const change = catalog.nodes.get(menu.node)?.change;
  const { format, text } = catalog;
  if (!change) return "";
  if (change.target === "cap") {
    return text.fill(UI.prestigeCap, { store: catalog.storeTitle(change.id), before: format.items(menu.before_value), after: format.items(menu.after_value) });
  }
  if (change.target === "work") {
    const each = (speed: number): string => format.duration(((catalog.cards.get(change.id)?.work_s ?? 0) * catalog.content.scales.bp) / Math.max(1, speed));
    return text.fill(UI.prestigeWork, { card: catalog.cardLabel(change.id), before: each(menu.before_value), after: each(menu.after_value) });
  }
  return text.fill(UI.prestigeMake, {
    store: catalog.storeTitle(change.store ?? ""), runner: catalog.runnerLabel(change.id),
    before: format.perMinute(menu.before_value), after: format.perMinute(menu.after_value),
  });
}

/** The level a player sees: counted across phases, so it never falls at a click (SkillBar.level counts from 1 in each phase). */
export function shownLevel(bar: SkillBar): number {
  return bar.prestige?.level_counted ?? bar.level;
}

/** The counted level a skill at its top lifts the top to: one more phase of levels, each phase adding top_level - 1,
 * and the bar's level is the phase's top level there. */
export function liftedTop(bar: SkillBar, p: SkillPrestige): number {
  return p.level_counted + bar.level - 1;
}

/** "+6 levels waiting" (at one, its own words); null with none. */
export function waitingText(catalog: Catalog, levels: number): string | null {
  if (levels <= 0) return null;
  return catalog.text.fill(levels === 1 ? UI.prestigeWaitingOne : UI.prestigeWaiting, { n: catalog.format.count(levels) });
}

/** Each skill at its top in `view` that was below it in `prev` (or in an earlier phase), with when it got there. */
export function toppedSince(prev: View | null, view: View): { skill: string; at: number }[] {
  if (prev === null) return [];
  return view.skills.flatMap((bar) => {
    const now = bar.prestige;
    const was = prev.skills.find((b) => b.skill === bar.skill)?.prestige;
    if (!now?.at_top || now.topped_at === null || !was) return [];
    return was.at_top && was.phase === now.phase ? [] : [{ skill: bar.skill, at: now.topped_at }];
  });
}
