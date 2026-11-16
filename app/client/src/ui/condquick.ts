// The quick add's sentence (docs/design/opening-screen.md, "The condition editor"): the whole store rule as one line
// in the editor's foot ("When smoked falls to a quarter, Smoke the catch until three quarters"), each part a native
// select laid over the words it reads as, so a tap opens the platform's own picker in place. The levels offer the five
// named shares; a rule with an exact number is More options' (condlevels.ts), and any other share shows as it reads.
import type { OrderVerb, View } from "../api/types";
import { sectioned } from "../game/cardsections";
import type { Catalog } from "../game/catalog";
import { doChoices, ruleCards, taskOf, whenChoices } from "../game/ruleoffers";
import { isShare, itemsAt, levelWords, PRESETS, sameLevel, shownAt, tryRule, type Level, type StoreRule, type Test } from "../game/storerule";
import { UI } from "../game/text";
import type { Draft } from "./conditiondraft";
import { el } from "./dom";

/** The test a store starts with in the quick add: "reaches" for one the task takes (and does not make), so the rule
 * uses it as it piles up; else "below", so the rule makes more as it runs low. */
export function quickTest(catalog: Catalog, view: View, then: OrderVerb | null, store: string): Test {
  return whenChoices(catalog, view, false, ruleCards(view, then), null).relevant.takes.includes(store) ? "reaches" : "below";
}

/** The task a draft reads as in the quick add, or null when it does not: a store rule (no chip, count or level) with
 * both levels shares (whole items on a store a lost fight adds to, Catalog.isLevel, whose chip shows items), not the
 * town's, doing a task, on a store the simple When row offers. Exact numbers are More options'. */
export function quickTask(catalog: Catalog, view: View, draft: Draft, chip: boolean): string | null {
  const task = taskOf(catalog, view, draft.then);
  const { n, m } = draft.rule;
  if (chip || draft.chip || draft.subject || draft.town || draft.unless.length > 0 || draft.orElse.length > 0 || m === null || isShare(n) === catalog.isLevel(draft.rule.store) || isShare(m) === catalog.isLevel(draft.rule.store) || task === null) return null;
  return whenChoices(catalog, view, false, ruleCards(view, draft.then), null).stores.includes(draft.rule.store) ? task : null;
}

/** The quick add's sentence for `draft` on a store of `cap` items (quickSentence), or null when it does not read as
 * one: `key` names everything the parts show, so a caller keeps the parts (and a picker open on one) while it holds. */
export function quickParts(catalog: Catalog, view: View, draft: Draft, chip: boolean, cap: number, pick: QuickPicks): { key: string; parts: () => HTMLElement[] } | null {
  const task = quickTask(catalog, view, draft, chip);
  const { rule } = draft;
  if (task === null || rule.m === null) return null;
  const stores = whenChoices(catalog, view, false, ruleCards(view, draft.then), null).stores;
  const tasks = doChoices(catalog, view, false, draft.then, false, draft.scope, draft.lane).flatMap((c) => (c.kind === "task" ? [c.card] : []));
  const m = rule.m;
  const can = (which: "n" | "m", l: Level) => sameLevel(tryRule({ ...rule, m, [which]: l }, cap)?.[which] ?? null, l);
  const items = catalog.isLevel(rule.store) ? cap : null;
  const offered = items === null ? PRESETS.map(([bp]) => ({ share: bp })) : Array.from({ length: items }, (_, i) => ({ items: i + 1 }));
  const offs = offered.flatMap((l) => (["n", "m"] as const).filter((w) => !can(w, l)).map((w) => `${w}${levelValue(l)}`));
  return { key: JSON.stringify([rule, task, stores, tasks, offs]), parts: () => quickSentence(catalog, { ...rule, m }, { stores, tasks, task, can, items, view }, pick) };
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
  /** The store's cap in items when its levels are whole items (a store a lost fight adds to), else null: shares. */
  items: number | null;
  /** The save the sentence is drawn for: a lane's label in the task list is the one it holds. */
  view: View;
}

export interface QuickPicks {
  store: (store: string) => void;
  test: (test: Test) => void;
  level: (which: "n" | "m", level: Level) => void;
  task: (card: string) => void;
}

/** An option; ones in a row with the same `group` sit under one option group of that name. */
type Option = { value: string; label: string; disabled?: boolean; group?: string };

/** One part: its words, a ▾, and over them a transparent select holding `options` with `value` chosen. */
function part(cls: string, words: string, options: Option[], value: string, pick: (v: string) => void, label = ""): HTMLElement {
  const wrap = el("span", `quick-part ${cls}`);
  const select = el("select", "quick-select");
  if (label) select.setAttribute("aria-label", label);
  let group: HTMLElement | null = null;
  let named: string | undefined;
  for (const o of options) {
    if (o.group !== named || (o.group && !group)) {
      named = o.group;
      group = o.group ? el("optgroup") : null;
      if (group && o.group) { group.setAttribute("label", o.group); select.append(group); }
    }
    const opt = el("option", "", o.label);
    opt.value = o.value;
    opt.disabled = o.disabled === true;
    opt.selected = o.value === value;
    (group ?? select).append(opt);
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
function levelPart(catalog: Catalog, rule: StoreRule, which: "n" | "m", level: Level, choices: QuickChoices, pick: QuickPicks): HTMLElement {
  if (choices.items !== null && !isShare(level)) return itemsPart(catalog, rule, which, level.items, choices.items, choices, pick);
  const presets: Option[] = PRESETS.map(([bp, key]) => ({ value: `s${bp}`, label: catalog.text.get(key), disabled: !choices.can(which, { share: bp }) }));
  const own = PRESETS.some(([bp]) => sameLevel(level, { share: bp })) ? [] : [{ value: levelValue(level), label: levelWords(catalog, level) }];
  return part(`quick-${which}`, levelWords(catalog, level), [...own, ...presets], levelValue(level), (v) => pick.level(which, readLevel(v)),
    catalog.text.get(which === "n" ? UI.ruleWhen : UI.ruleUntil));
}

/** A whole-item level's part, worded as the amount the chip shows where the rule holds or lets go ("reaches 2", "until
 * down to empty"), one choice for each amount from empty to the cap. */
function itemsPart(catalog: Catalog, rule: StoreRule, which: "n" | "m", items: number, cap: number, choices: QuickChoices, pick: QuickPicks): HTMLElement {
  const side = which === "n" ? "on" : "off";
  const words = (shown: number): string => (shown === 0 ? catalog.text.get(UI.levelEmpty) : catalog.format.count(shown));
  const options = Array.from({ length: cap + 1 }, (_, shown) => {
    const level = { items: itemsAt(shown, rule.test, side) };
    return { value: levelValue(level), label: words(shown), disabled: !choices.can(which, level) };
  });
  return part(`quick-${which}`, words(shownAt({ items }, rule.test, side, cap)), options, levelValue({ items }), (v) => pick.level(which, readLevel(v)),
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
    n: levelPart(catalog, rule, "n", rule.n, choices, pick),
    m: levelPart(catalog, rule, "m", rule.m, choices, pick),
    task: part(`quick-action ${hue}`, catalog.cardLabel(choices.task), sectioned(catalog, choices.tasks, (c) => c, choices.view).flatMap((g) => g.items.map((c) => ({ value: c, label: catalog.cardLabel(c), group: g.heading || undefined }))), choices.task, pick.task,
      text.get(UI.ruleDo)),
  };
  const template = text.get(rule.test === "below" ? UI.ruleQuickDown : UI.ruleQuickUp);
  return template.split(/(\{\w+\})/).filter((s) => s !== "").map((s) => (/^\{\w+\}$/.test(s) ? parts[s.slice(1, -1)] : undefined) ?? el("span", "", s));
}
