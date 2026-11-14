// The quick add's sentence (docs/design/opening-screen.md, "The condition editor"): the whole store rule as one line
// in the editor's foot ("When smoked falls to a quarter, Smoke the catch until three quarters"), each part a native
// select laid over the words it reads as, so a tap opens the platform's own picker in place. The levels offer the five
// named shares; a rule with an exact number is More options' (condlevels.ts), and any other share shows as it reads.
import type { OrderVerb, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { doChoices, ruleCards, taskOf, whenChoices } from "../game/ruleoffers";
import { isShare, levelWords, PRESETS, sameLevel, tryRule, type Level, type StoreRule, type Test } from "../game/storerule";
import { UI } from "../game/text";
import type { Draft } from "./conditiondraft";
import { el } from "./dom";

/** The test a store starts with in the quick add: "reaches" for one the task takes (and does not make), so the rule
 * uses it as it piles up; else "below", so the rule makes more as it runs low. */
export function quickTest(catalog: Catalog, view: View, then: OrderVerb | null, store: string): Test {
  return whenChoices(catalog, view, false, ruleCards(view, then), null).relevant.takes.includes(store) ? "reaches" : "below";
}

/** The task a draft reads as in the quick add, or null when it does not: a store rule (no chip, count or level) with
 * both levels shares, not the town's, doing a task, on a store the simple When row offers. Exact numbers are More
 * options'. */
export function quickTask(catalog: Catalog, view: View, draft: Draft, chip: boolean): string | null {
  const task = taskOf(catalog, view, draft.then);
  const { n, m } = draft.rule;
  if (chip || draft.chip || draft.subject || draft.town || m === null || !isShare(n) || !isShare(m) || task === null) return null;
  return whenChoices(catalog, view, false, ruleCards(view, draft.then), null).stores.includes(draft.rule.store) ? task : null;
}

/** The quick add's sentence for `draft` on a store of `cap` items (quickSentence), or null when it does not read as
 * one: `key` names everything the parts show, so a caller keeps the parts (and a picker open on one) while it holds. */
export function quickParts(catalog: Catalog, view: View, draft: Draft, chip: boolean, cap: number, pick: QuickPicks): { key: string; parts: () => HTMLElement[] } | null {
  const task = quickTask(catalog, view, draft, chip);
  const { rule } = draft;
  if (task === null || rule.m === null) return null;
  const stores = whenChoices(catalog, view, false, ruleCards(view, draft.then), null).stores;
  const tasks = doChoices(catalog, view, false, draft.then).flatMap((c) => (c.kind === "task" ? [c.card] : []));
  const m = rule.m;
  const can = (which: "n" | "m", l: Level) => tryRule({ ...rule, m, [which]: l }, cap) !== null;
  const offs = PRESETS.flatMap(([bp]) => (["n", "m"] as const).filter((w) => !can(w, { share: bp })).map((w) => `${w}${bp}`));
  return { key: JSON.stringify([rule, task, stores, tasks, offs]), parts: () => quickSentence(catalog, { ...rule, m }, { stores, tasks, task, can }, pick) };
}

export interface QuickChoices {
  /** The stores the store part offers (the When row's), the rule's own among them. */
  stores: readonly string[];
  /** The tasks the action part offers (the Do row's), the rule's own among them. */
  tasks: readonly string[];
  /** The rule's task. */
  task: string;
  /** Whether the rule with this level in place of n or m is one the page builds. */
  can: (which: "n" | "m", level: Level) => boolean;
}

export interface QuickPicks {
  store: (store: string) => void;
  test: (test: Test) => void;
  level: (which: "n" | "m", level: Level) => void;
  task: (card: string) => void;
}

type Option = { value: string; label: string; disabled?: boolean };

/** One part: its words, a ▾, and over them a transparent select holding `options` with `value` chosen. */
function part(cls: string, words: string, options: Option[], value: string, pick: (v: string) => void, label = ""): HTMLElement {
  const wrap = el("span", `quick-part ${cls}`);
  const select = el("select", "quick-select");
  if (label) select.setAttribute("aria-label", label);
  for (const o of options) {
    const opt = el("option", "", o.label);
    opt.value = o.value;
    opt.disabled = o.disabled === true;
    opt.selected = o.value === value;
    select.append(opt);
  }
  select.value = value;
  select.addEventListener("change", () => { if (select.value !== value) pick(select.value); });
  wrap.append(el("span", "quick-word", words), el("span", "quick-mark", "▾"), select);
  return wrap;
}

const levelValue = (l: Level): string => (isShare(l) ? `s${l.share}` : `i${l.items}`);
const readLevel = (v: string): Level => (v.startsWith("s") ? { share: Number(v.slice(1)) } : { items: Number(v.slice(1)) });

/** A level's part: the five named shares (each off where the rule would not build), and the level as it stands when
 * it is none of them. */
function levelPart(catalog: Catalog, which: "n" | "m", level: Level, choices: QuickChoices, pick: QuickPicks): HTMLElement {
  const presets: Option[] = PRESETS.map(([bp, key]) => ({ value: `s${bp}`, label: catalog.text.get(key), disabled: !choices.can(which, { share: bp }) }));
  const own = PRESETS.some(([bp]) => sameLevel(level, { share: bp })) ? [] : [{ value: levelValue(level), label: levelWords(catalog, level) }];
  return part(`quick-${which}`, levelWords(catalog, level), [...own, ...presets], levelValue(level), (v) => pick.level(which, readLevel(v)),
    catalog.text.get(which === "n" ? UI.ruleWhen : UI.ruleUntil));
}

/** The rule as one sentence of parts, by its test's template: {store} {test} {n}, {task} until {m}. */
export function quickSentence(catalog: Catalog, rule: StoreRule & { m: Level }, choices: QuickChoices, pick: QuickPicks): HTMLElement[] {
  const { text } = catalog;
  const tests: Option[] = [{ value: "below", label: text.get(UI.ruleFallsTo) }, { value: "reaches", label: text.get(UI.ruleReachesTo) }];
  const hue = `rule-action hue-${catalog.rank(choices.task) % 6}`;
  const parts: Record<string, HTMLElement> = {
    store: part("quick-store", catalog.storeLabel(rule.store), choices.stores.map((s) => ({ value: s, label: catalog.storeTitle(s) })), rule.store, pick.store),
    test: part("quick-test", text.get(rule.test === "below" ? UI.ruleFallsTo : UI.ruleReachesTo), tests, rule.test, (v) => pick.test(v as Test)),
    n: levelPart(catalog, "n", rule.n, choices, pick),
    m: levelPart(catalog, "m", rule.m, choices, pick),
    task: part(`quick-action ${hue}`, catalog.cardLabel(choices.task), choices.tasks.map((c) => ({ value: c, label: catalog.cardLabel(c) })), choices.task, pick.task,
      text.get(UI.ruleDo)),
  };
  const template = text.get(rule.test === "below" ? UI.ruleQuickDown : UI.ruleQuickUp);
  return template.split(/(\{\w+\})/).filter((s) => s !== "").map((s) => (/^\{\w+\}$/.test(s) ? parts[s.slice(1, -1)] : undefined) ?? el("span", "", s));
}
