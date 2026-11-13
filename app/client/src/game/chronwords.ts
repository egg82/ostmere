// The words the chronicle wears: how long the player was away, its filters, how many entries of one a stretch holds,
// and what caused a line (CONTRACT.txt, "Line causes"), worded from the served cause, never from the line. Pure.
import type { Condition, LineCause } from "../api/types";
import type { Catalog } from "./catalog";
import type { Filter } from "./chronicle";
import { UI, type Text } from "./text";

const LABEL: Record<Filter | "all", string> = {
  story: UI.chronStory, finds: UI.chronFinds, levels: UI.chronLevels, rules: UI.chronRules, fights: UI.chronFights,
  talk: UI.chronTalk, all: UI.chronAll,
};

/** "Away 54m", "Away 5h 3m", "Away 2d": the time between leaving and returning, to the minute and under a day to the hour. */
export function awayTitle(text: Text, seconds: number): string {
  const minutes = Math.round(seconds / 60);
  const h = Math.floor(minutes / 60), m = minutes % 60;
  if (minutes < 60) return text.fill(UI.chronAwayM, { m: String(minutes) });
  if (h < 24) return m === 0 ? text.fill(UI.chronAwayH, { h: String(h) }) : text.fill(UI.chronAwayHm, { h: String(h), m: String(m) });
  return text.fill(UI.chronAwayD, { d: String(Math.floor(h / 24)) });
}

export function filterLabel(text: Text, filter: Filter | "all"): string {
  return text.get(LABEL[filter]);
}

/** "Finds 3": a filter's label and how many entries of it. */
export function filterCount(text: Text, filter: Filter, n: number): string {
  return text.fill(UI.chronCount, { name: filterLabel(text, filter), n: String(n) });
}

/** What caused a line, in words; null when it has no cause or one the page cannot word. */
export function causeWords(catalog: Catalog, cause: LineCause | null): string | null {
  const { text } = catalog;
  if (cause === null) return null;
  switch (cause.kind) {
    case "runner": return catalog.runnerLabel(cause.runner) || null;
    case "when": return whenWords(catalog, cause.when);
    case "skill": return text.fill(UI.causeSkill, { skill: catalog.skillLabel(cause.skill) });
    case "camp": return text.fill(UI.causeCamp, { n: catalog.format.count(cause.level) });
    case "answer": return text.get(UI.causeAnswer);
  }
}

/** A condition met, as a cause: a store reached or fallen to, a level, a count, the thing unlocked or running, or time. */
export function whenWords(catalog: Catalog, when: Condition): string | null {
  const { text, format } = catalog;
  if (when.kind === "after_time") return text.get(UI.causeTime);
  const w = when.watched;
  if (w.kind === "store_value") return text.fill(when.kind === "at_least" ? UI.causeStore : UI.causeBelow, { store: catalog.storeLabel(w.store), n: format.items(when.value) });
  if (when.kind === "at_most") return null;
  if (w.kind === "skill_level") return text.fill(UI.causeLevel, { skill: catalog.skillLabel(w.skill), n: format.count(when.value) });
  if (w.kind === "card_count") return text.fill(UI.causeCount, { card: catalog.cardLabel(w.card), n: format.count(when.value) });
  if (w.kind === "running") return catalog.runnerLabel(w.runner) || null;
  return unlockedWords(catalog, w.unlock.category, w.unlock.id);
}

function unlockedWords(catalog: Catalog, category: string, id: string): string | null {
  if (category === "card") return catalog.cardLabel(id) || null;
  if (category === "store") return catalog.storeLabel(id) || null;
  if (category === "skill") return catalog.skillLabel(id) || null;
  if (category === "feature") return catalog.label(catalog.content.feature_infos.find((f) => f.feature === id)?.label_key) || null;
  return null;
}
