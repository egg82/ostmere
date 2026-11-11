// The condition editor's subjects past the stores (condition.ts, the full editor; docs/design/opening-screen.md, "The
// condition editor"): under When, a Levels row (the Camp and each skill, at the level each stands at now) and a Tasks
// row (each task in play); and, once one is chosen, its one stepper in the levels' place: "Level" for a level, "Times"
// for a task's count of times done. What is offered is ruleoffers.subjectChoices's; numbers and conditions are
// subjectrule.ts's.
import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { clampSubject, defaultSubject, subjectKey, subjectName, subjectNow, subjectRange, type SubjectRule } from "../game/subjectrule";
import { UI } from "../game/text";
import { stepper, type Stepper } from "./condlevels";
import { el, setText } from "./dom";

/** The Levels and Tasks heads and their buttons; each button carries data-subject, read back to mark the one chosen. */
export function subjectRows(catalog: Catalog, view: View, choices: { levels: SubjectRule[]; tasks: SubjectRule[] }, pick: (r: SubjectRule) => void): HTMLElement[] {
  const button = (rule: SubjectRule): HTMLElement => {
    const b = el("button", "quiet cond-subject");
    b.type = "button";
    b.dataset.subject = subjectKey(rule);
    b.append(el("span", "", subjectName(catalog, rule)));
    if (rule.kind !== "count") b.append(el("span", "cond-amount", catalog.text.fill(UI.level, { n: catalog.format.count(subjectNow(catalog, view, rule)) })));
    b.addEventListener("click", () => pick(defaultSubject(catalog, view, rule)));
    return b;
  };
  const head = (key: string, rules: SubjectRule[]) => (rules.length === 0 ? [] : [el("span", "rules-label cond-subhead", catalog.text.get(key)), ...rules.map(button)]);
  return [...head(UI.ruleLevels, choices.levels), ...head(UI.ruleTasks, choices.tasks)];
}

/** Pressed on the subject button that is `rule`'s. */
export function markSubject(root: ParentNode, rule: SubjectRule | undefined): void {
  const key = rule ? subjectKey(rule) : null;
  for (const b of root.querySelectorAll<HTMLElement>(".cond-subject")) b.setAttribute("aria-pressed", String(b.dataset.subject === key));
}

/** The chosen subject's stepper: a count's "Times" or a level's "Level". */
export class SubjectControl {
  readonly root = el("div", "cond-levels cond-subject-control");
  private readonly times: Stepper;
  private readonly level: Stepper;
  private rule: SubjectRule | null = null;
  private view: View | null = null;

  constructor(private readonly catalog: Catalog, private readonly changed: (rule: SubjectRule) => void) {
    const { text } = catalog;
    const step = (d: -1 | 1) => this.step(d);
    this.times = stepper(text.get(UI.ruleTimes), text.get(UI.ruleLess), text.get(UI.ruleMore), step);
    this.level = stepper(text.get(UI.ruleLevel), text.get(UI.ruleLess), text.get(UI.ruleMore), step);
    this.root.append(this.times.root, this.level.root);
  }

  /** Shows `rule`'s stepper, its buttons off at the ends of what the subject allows; hidden with no subject chosen. */
  draw(view: View, rule: SubjectRule | undefined): void {
    this.view = view;
    this.rule = rule ?? null;
    this.root.hidden = rule === undefined;
    if (!rule) return;
    this.times.root.hidden = rule.kind !== "count";
    this.level.root.hidden = rule.kind === "count";
    const shown = rule.kind === "count" ? this.times : this.level;
    const [lo, hi] = subjectRange(this.catalog, view, rule);
    setText(shown.value, this.catalog.format.count(rule.n));
    shown.less.disabled = rule.n <= lo;
    shown.more.disabled = rule.n >= hi;
  }

  private step(d: -1 | 1): void {
    const { rule, view } = this;
    if (!rule || !view) return;
    const next = clampSubject(this.catalog, view, { ...rule, n: rule.n + d });
    if (next.n !== rule.n) this.changed(next);
  }
}
