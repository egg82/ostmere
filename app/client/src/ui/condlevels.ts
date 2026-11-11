// The condition editor's levels (condition.ts): "falls below" or "reaches", the when and until steppers and the band,
// folded behind one row that states the two numbers ("When 10 Until 25 ▾"). A new rule opens folded: what it runs and
// the store it watches are the common choices, and the levels start at storerule.ts's defaults; a rule being changed
// opens with them shown. The fold opens once and stays open while the editor is.
import type { StoreRule, Test } from "../game/storerule";
import { UI } from "../game/text";
import { el, setText, tapFeedback } from "./dom";

export interface Stepper {
  root: HTMLElement;
  value: HTMLElement;
  less: HTMLButtonElement;
  more: HTMLButtonElement;
}

/** A labelled − value + row; `less` and `more` name the buttons for a screen reader after the label. */
export function stepper(label: string, less: string, more: string, step: (d: -1 | 1) => void): Stepper {
  const root = el("div", "cond-stepper");
  const value = el("span", "cond-value");
  const down = el("button", "primary cond-step", "−");
  const up = el("button", "primary cond-step", "+");
  down.type = up.type = "button";
  down.setAttribute("aria-label", `${label} ${less}`);
  up.setAttribute("aria-label", `${label} ${more}`);
  down.addEventListener("click", () => { tapFeedback(); step(-1); });
  up.addEventListener("click", () => { tapFeedback(); step(1); });
  root.append(el("span", "cond-label", label), down, value, up);
  return { root, value, less: down, more: up };
}

export class LevelsFold {
  readonly root = el("div", "cond-levels");
  private readonly toggle = el("button", "cond-fold");
  private readonly whenValue = el("b", "cond-fold-value");
  private readonly untilValue = el("b", "cond-fold-value");
  private readonly body = el("div", "cond-fold-body");

  constructor(whenLabel: string, untilLabel: string, ...parts: HTMLElement[]) {
    this.toggle.type = "button";
    this.toggle.append(el("span", "cond-label", whenLabel), this.whenValue, el("span", "cond-label", untilLabel), this.untilValue,
      el("span", "cond-fold-mark", "▾"));
    this.toggle.addEventListener("click", () => { tapFeedback(); this.open(true); });
    this.body.append(...parts);
    this.root.append(this.toggle, this.body);
  }

  open(on: boolean): void {
    this.body.hidden = !on;
    this.toggle.hidden = on;
    this.toggle.setAttribute("aria-expanded", String(on));
  }

  /** The folded row's numbers, as the steppers show them. */
  state(when: string, until: string): void {
    setText(this.whenValue, when);
    setText(this.untilValue, until);
  }
}

/** A stepper showing `value` ("–" when there is none), its buttons off at the ends of `range`. */
function drawStepper(s: Stepper, value: number | null, range: [number, number] | null, count: (n: number) => string): void {
  setText(s.value, value === null || range === null ? "–" : count(value));
  s.less.disabled = range === null || value === null || value <= range[0];
  s.more.disabled = range === null || value === null || value >= range[1];
}

/** The levels as one part of the editor: the two tests, the two steppers and the band, inside the fold. */
export class Levels {
  readonly fold: LevelsFold;
  private readonly tests = new Map<Test, HTMLButtonElement>();
  private readonly when: Stepper;
  private readonly until: Stepper;
  private readonly span = el("i", "cond-span");
  private readonly tick = el("i", "cond-now");

  constructor(text: { get(key: string): string }, onTest: (test: Test) => void, onStep: (which: "n" | "m", d: -1 | 1) => void) {
    const tests = el("div", "cond-tests");
    for (const [test, key] of [["below", UI.ruleFallsBelow], ["reaches", UI.ruleReachesLabel]] as const) {
      const b = el("button", "quiet cond-test", text.get(key));
      b.type = "button";
      b.dataset.test = test;   // a lesson's mark of the test (game/lessons.ts, CAP_RULE)
      b.addEventListener("click", () => onTest(test));
      this.tests.set(test, b);
      tests.append(b);
    }
    this.when = stepper(text.get(UI.ruleWhen), text.get(UI.ruleLess), text.get(UI.ruleMore), (d) => onStep("n", d));
    this.until = stepper(text.get(UI.ruleUntil), text.get(UI.ruleLess), text.get(UI.ruleMore), (d) => onStep("m", d));
    const steppers = el("div", "cond-steppers");
    steppers.append(this.when.root, this.until.root);
    const band = el("div", "cond-band");
    band.setAttribute("aria-hidden", "true");
    band.append(this.span, this.tick);
    this.fold = new LevelsFold(text.get(UI.ruleWhen), text.get(UI.ruleUntil), tests, steppers, band);
  }

  /** The rule's test pressed, its levels inside `room`, and the band: n..m over 0..cap, the tick at `now` items (none
   * when the store has no line). */
  draw(rule: StoreRule, room: { n: [number, number]; m: [number, number] } | null, cap: number, now: number | null, count: (n: number) => string): void {
    for (const [test, b] of this.tests) b.setAttribute("aria-pressed", String(test === rule.test));
    drawStepper(this.when, rule.n, room?.n ?? null, count);
    drawStepper(this.until, rule.m, room?.m ?? null, count);
    this.fold.state(this.when.value.textContent ?? "", this.until.value.textContent ?? "");
    const pct = (items: number) => `${cap > 0 ? (100 * Math.min(cap, Math.max(0, items))) / cap : 0}%`;
    const lo = Math.min(rule.n, rule.m ?? rule.n), hi = Math.max(rule.n, rule.m ?? rule.n);
    this.span.style.left = pct(lo);
    this.span.style.width = `calc(${pct(hi)} - ${pct(lo)})`;
    this.tick.hidden = now === null;
    if (now !== null) this.tick.style.left = pct(now);
  }
}
