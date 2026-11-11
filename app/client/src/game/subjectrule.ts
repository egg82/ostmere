// A rule's condition on a count or a level, as the page builds, reads and words it (CONTRACT.txt, "a subject rule"): a
// task's count of times done, a skill's level, the Camp's level. Counts and levels only ever go up, so each is one
// threshold with no band, the plain AtLeast the engine already validates for its subject:
//   done n times       at_least(card_count(card), n, n)
//   skill level n      at_least(skill_level(skill), n, n)
//   Camp level n       at_least(store_value(camp), at, at), `at` the level's Content.camp.camp_levels entry; only the
//                      levels below the first held one still waiting to be lifted, which the bar would not count yet
// No rule watches Running: set_orders refuses it (an order on what its own mix stops would flip at every instant).
import type { CampLevel, Condition, View } from "../api/types";
import { sample } from "./clock";
import type { Catalog } from "./catalog";
import { UI } from "./text";

export type SubjectRule =
  | { kind: "count"; card: string; n: number }
  | { kind: "level"; skill: string; n: number }
  | { kind: "camp"; n: number };

/** The subject rule a condition is, or null for any other (a store rule, a chip's, a time). */
export function readSubject(catalog: Catalog, when: Condition): SubjectRule | null {
  if (when.kind !== "at_least" || when.value !== when.release) return null;
  const w = when.watched;
  if (w.kind === "card_count") return { kind: "count", card: w.card, n: when.value };
  if (w.kind === "skill_level") return { kind: "level", skill: w.skill, n: when.value };
  if (w.kind !== "store_value" || w.store !== catalog.campStore) return null;
  const level = campLevels(catalog).findIndex((l) => l.at === when.value);
  return level < 0 ? null : { kind: "camp", n: level + 1 };
}

/** The condition for a subject rule. */
export function buildSubject(catalog: Catalog, rule: SubjectRule): Condition {
  if (rule.kind === "count") return { kind: "at_least", watched: { kind: "card_count", card: rule.card }, value: rule.n, release: rule.n };
  if (rule.kind === "level") return { kind: "at_least", watched: { kind: "skill_level", skill: rule.skill }, value: rule.n, release: rule.n };
  const at = campLevels(catalog)[rule.n - 1]?.at ?? 0;
  return { kind: "at_least", watched: { kind: "store_value", store: catalog.campStore ?? "" }, value: at, release: at };
}

/** The condition in the player's words: "Once Forage is done 3 times", "Once Forage is done", "Once Camp reaches
 * level 2". */
export function subjectWords(catalog: Catalog, rule: SubjectRule): string {
  const { text, format } = catalog;
  if (rule.kind === "count") return text.fill(rule.n === 1 ? UI.ruleDoneOnce : UI.ruleDone, { card: catalog.cardLabel(rule.card), n: format.count(rule.n) });
  return text.fill(UI.ruleReachesLevel, { name: subjectName(catalog, rule), n: format.count(rule.n) });
}

/** What a rule watches, by name: the task's, the skill's, or the Camp store's. */
export function subjectName(catalog: Catalog, rule: SubjectRule): string {
  return rule.kind === "count" ? catalog.cardLabel(rule.card) : rule.kind === "level" ? catalog.skillLabel(rule.skill) : catalog.storeLabel(catalog.campStore ?? "");
}

/** Where the count or level stands in `view`: times done, the skill's level, the Camp's level as its bar counts it. */
export function subjectNow(catalog: Catalog, view: View, rule: SubjectRule): number {
  if (rule.kind === "count") return [...view.cards, ...view.completed].find((c) => c.card === rule.card)?.completions ?? 0;
  if (rule.kind === "level") return view.skills.find((s) => s.skill === rule.skill)?.level ?? 0;
  const line = view.ledger.find((l) => l.store === catalog.campStore);
  const v = line ? sample(line.segment, view.at) : 0;
  return campLevels(catalog).filter((l) => (!l.held || lifted(view, l)) && v >= l.at).length;
}

const campLevels = (catalog: Catalog): CampLevel[] => catalog.content.camp?.camp_levels ?? [];

/** A held Camp level counts once one of its lifted_by cards is done (CONTRACT.txt, the Camp bar). */
const lifted = (view: View, level: CampLevel): boolean => level.lifted_by.some((card) => view.completed.some((c) => c.card === card));

/** The Camp levels a rule can name exactly: those before the first held level not yet lifted. The store passes a held
 * level's `at` before the bar counts it, so a rule on it would come on while the bar still reads the level below. */
function campTop(catalog: Catalog, view: View): number {
  const levels = campLevels(catalog);
  const held = levels.findIndex((l) => l.held && !lifted(view, l));
  return Math.max(1, held < 0 ? levels.length : held);
}

/** The values n may take: from 1 to a card's cap, to the Camp's last level a rule can name, or with no top. */
export function subjectRange(catalog: Catalog, view: View, rule: SubjectRule): [number, number] {
  if (rule.kind === "camp") return [1, campTop(catalog, view)];
  const cap = rule.kind === "count" ? view.cards.find((c) => c.card === rule.card)?.cap ?? null : null;
  return [1, cap ?? Number.POSITIVE_INFINITY];
}

/** n held inside what the subject allows. */
export function clampSubject(catalog: Catalog, view: View, rule: SubjectRule): SubjectRule {
  const [lo, hi] = subjectRange(catalog, view, rule);
  return { ...rule, n: Math.min(hi, Math.max(lo, rule.n)) };
}

/** Where a new rule on the subject starts: the next count or level from now. */
export function defaultSubject(catalog: Catalog, view: View, rule: SubjectRule): SubjectRule {
  return clampSubject(catalog, view, { ...rule, n: subjectNow(catalog, view, rule) + 1 });
}

/** One key per subject, whatever its n. */
export function subjectKey(rule: SubjectRule): string {
  return rule.kind === "count" ? `task:${rule.card}` : rule.kind === "level" ? `level:${rule.skill}` : "camp";
}
