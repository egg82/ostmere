// The condition editor's subjects past the stores (condition.ts, the full editor; docs/design/opening-screen.md, "The
// condition editor"): under When, a Levels row (the Camp and each skill, at the level each stands at now) and a Tasks
// row (each task in play); and, once one is chosen, its one slider in the levels' place: "Level" for a level, "Times"
// for a task's count of times done. What is offered is ruleoffers.subjectChoices's; numbers and conditions are
// subjectrule.ts's.
import type { View } from "../api/types";
import { sectioned } from "../game/cardsections";
import type { Catalog } from "../game/catalog";
import { clampSubject, defaultSubject, subjectKey, subjectName, subjectNow, subjectRange, type SubjectRule } from "../game/subjectrule";
import { UI } from "../game/text";
import { sectionHead } from "./condrows";
import { el, setText } from "./dom";
import { ValueSlider } from "./valueslider";

/** The Levels and Tasks heads and their buttons; each button carries data-subject, read back to mark the one chosen. */
export function subjectRows(catalog: Catalog, view: View, choices: { levels: SubjectRule[]; tasks: SubjectRule[]; running?: SubjectRule[] }, pick: (r: SubjectRule) => void): HTMLElement[] {
  const button = (rule: SubjectRule) => subjectButton(catalog, view, rule, pick);
  const head = (key: string, rules: SubjectRule[]) => (rules.length === 0 ? [] : [el("span", "rules-label cond-subhead", catalog.text.get(key)), ...rules.map(button)]);
  const cards = (key: string, rules: SubjectRule[]) => {   // under its head, by section as the Tasks page has them, each by name
    const rows = sectioned(catalog, rules, (r) => (r.kind === "count" || r.kind === "running" ? r.card : null), view).flatMap((g) => [...sectionHead(g.heading), ...g.items.map(button)]);
    return rows.length === 0 ? [] : [el("span", "rules-label cond-subhead", catalog.text.get(key)), ...rows];
  };
  return [...head(UI.ruleLevels, choices.levels), ...cards(UI.ruleTasks, choices.tasks), ...cards(UI.ruleRunning, choices.running ?? [])];
}

function subjectButton(catalog: Catalog, view: View, rule: SubjectRule, pick: (r: SubjectRule) => void): HTMLElement {
  const b = el("button", "quiet cond-subject");
  b.type = "button";
  b.dataset.subject = subjectKey(rule);
  b.append(el("span", "", subjectName(catalog, rule)));
  if (rule.kind === "level" || rule.kind === "camp") b.append(el("span", "cond-amount", catalog.text.fill(UI.level, { n: catalog.format.count(subjectNow(catalog, view, rule)) })));
  b.addEventListener("click", () => pick(defaultSubject(catalog, view, rule)));
  return b;
}

/** The simple view's Running head and its few cards in the order given (ruleoffers.quickRunning), none by section. */
export function quickRunningRows(catalog: Catalog, view: View, rules: SubjectRule[], pick: (r: SubjectRule) => void): HTMLElement[] {
  return rules.length === 0 ? [] : [el("span", "rules-label cond-subhead", catalog.text.get(UI.ruleRunning)), ...rules.map((r) => subjectButton(catalog, view, r, pick))];
}

/** Pressed on the subject button that is `rule`'s. */
export function markSubject(root: ParentNode, rule: SubjectRule | undefined): void {
  const key = rule ? subjectKey(rule) : null;
  for (const b of root.querySelectorAll<HTMLElement>(".cond-subject")) b.setAttribute("aria-pressed", String(b.dataset.subject === key));
}

/** A subject with no top slides this far past where it stands now (a number written higher is shown whole). */
const OPEN_REACH = 10;

/** One of the subject's numbers: its label, the number, and a slider by one from `lo` to `hi`. */
class SubjectNumber {
  readonly root = el("div", "cond-level");
  private readonly value = el("span", "cond-value");
  private readonly slider: ValueSlider;

  constructor(label: string, pick: (n: number) => void) {
    this.slider = new ValueSlider(label, pick);
    const head = el("div", "cond-level-head");
    head.append(el("span", "cond-label", label), this.value);
    this.root.append(head, this.slider.root);
  }

  draw(catalog: Catalog, n: number, lo: number, hi: number): void {
    const words = catalog.format.count(n);
    setText(this.value, words);
    this.slider.draw({ min: lo, max: hi, step: 1 }, n, words, () => true);
  }
}

/** The chosen subject's number: a count's "Times" or a level's "Level", from the least to the most it can reach. */
export class SubjectControl {
  readonly root = el("div", "cond-levels cond-subject-control");
  private readonly times: SubjectNumber;
  private readonly level: SubjectNumber;
  private rule: SubjectRule | null = null;
  private view: View | null = null;
  private kept: number | undefined;

  constructor(private readonly catalog: Catalog, private readonly changed: (rule: SubjectRule) => void) {
    const { text } = catalog;
    this.times = new SubjectNumber(text.get(UI.ruleTimes), (n) => this.set(n));
    this.level = new SubjectNumber(text.get(UI.ruleLevel), (n) => this.set(n));
    this.root.append(this.times.root, this.level.root);
  }

  /** Shows `rule`'s number over what the subject allows (`kept` as subjectRange has it); hidden with no subject chosen. */
  draw(view: View, rule: SubjectRule | undefined, kept?: number): void {
    this.view = view;
    this.rule = rule ?? null;
    this.kept = kept;
    this.root.hidden = rule === undefined || rule.kind === "running";
    if (!rule || rule.kind === "running") return;
    this.times.root.hidden = rule.kind !== "count";
    this.level.root.hidden = rule.kind === "count";
    const [lo, top] = subjectRange(this.catalog, view, rule, kept);
    const hi = Number.isFinite(top) ? top : Math.max(rule.n, subjectNow(this.catalog, view, rule) + OPEN_REACH);
    (rule.kind === "count" ? this.times : this.level).draw(this.catalog, rule.n, lo, hi);
  }

  private set(n: number): void {
    const { rule, view } = this;
    if (!rule || !view) return;
    const next = clampSubject(this.catalog, view, { ...rule, n }, this.kept);
    if (next.n !== rule.n) this.changed(next);
  }
}
