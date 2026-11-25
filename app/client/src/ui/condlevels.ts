// The condition editor's levels (condition.ts): "falls below" or "reaches", the when and until levels and the band,
// folded behind one row that states the two ("When a quarter Until three quarters ▾"). Each level is a share of the
// store's cap (the five named shares, or a percentage in five-point steps) or an exact number of items, and switches
// between the two in place (storerule.switchForm). A new rule opens folded: what it runs and the store it watches are
// the common choices, and the levels start at storerule.ts's defaults; a rule being changed opens with them shown. The
// fold opens once and stays open while the editor is.
import type { Catalog } from "../game/catalog";
import { isShare, levelAt, levelWords, PRESETS, SHARE_STEP, BP, switchForm, tryRule, type Level, type StoreRule, type Test } from "../game/storerule";
import { UI } from "../game/text";
import { el, setText, tapFeedback } from "./dom";
import { ValueSlider } from "./valueslider";

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

  /** The folded row's two levels, in the rule's words. */
  state(when: string, until: string): void {
    setText(this.whenValue, when);
    setText(this.untilValue, until);
  }
}

type Which = "n" | "m";

function quiet(cls: string, label: string, pick: () => void): HTMLButtonElement {
  const b = el("button", `quiet ${cls}`, label);
  b.type = "button";
  b.addEventListener("click", () => { tapFeedback(); pick(); });
  return b;
}

/** One level: its label, a slider (five points of the cap, or one item up to the store's maximum), its value in words
 * and the two forms; under them, while it is a share, the named shares. */
export class LevelRow {
  readonly root = el("div", "cond-level");
  private readonly forms: [HTMLButtonElement, HTMLButtonElement];
  private readonly formsRow = el("div", "cond-forms");
  private readonly presets: [number, HTMLButtonElement][];
  private readonly share = el("div", "cond-presets");
  private readonly fine: ValueSlider;
  private readonly items: ValueSlider;
  private readonly value = el("span", "cond-value");
  private level: Level = { share: 0 };
  private turn: () => Level = () => this.level;

  constructor(catalog: Catalog, label: string, pick: (l: Level) => void) {
    const { text } = catalog;
    this.forms = [quiet("cond-form", text.get(UI.ruleOfFull), () => { if (!isShare(this.level)) pick(this.turn()); }),
      quiet("cond-form", text.get(UI.ruleExact), () => { if (isShare(this.level)) pick(this.turn()); })];
    const marks: Record<number, string> = { 2500: UI.levelMarkQuarter, 5000: UI.levelMarkHalf, 7500: UI.levelMarkThreeQuarters };
    this.presets = PRESETS.map(([bp, key]) => {
      const b = quiet("cond-preset", text.get(marks[bp] ?? key), () => pick({ share: bp }));
      b.setAttribute("aria-label", `${label} ${text.get(key)}`);
      return [bp, b];
    });
    this.fine = new ValueSlider(label, (share) => pick({ share }));
    this.items = new ValueSlider(label, (items) => pick({ items }));
    this.fine.root.dataset.form = "share";
    this.items.root.dataset.form = "items";
    const head = el("div", "cond-level-head");
    this.formsRow.append(...this.forms);
    head.append(el("span", "cond-label", label), this.value, this.formsRow);
    this.share.append(...this.presets.map(([, b]) => b));
    this.root.append(head, this.fine.root, this.items.root, this.share);
  }

  /** `level` shown in its form, the slider running to `cap` items, each choice off where `can` says the rule would not be
   * one the page builds; `turn` is the level in the other form. `items`: the store's levels are whole items only (a
   * store a lost fight adds to), so a share (one saved before) can only be turned into items. */
  draw(catalog: Catalog, level: Level, cap: number, can: (l: Level) => boolean, turn: () => Level, items: boolean): void {
    this.level = level;
    this.turn = turn;
    const share = isShare(level);
    this.formsRow.hidden = items && !share;
    this.forms[0].hidden = items;
    this.forms[0].setAttribute("aria-pressed", String(share));
    this.forms[1].setAttribute("aria-pressed", String(!share));
    this.forms[share ? 1 : 0].disabled = !can(turn());
    this.forms[share ? 0 : 1].disabled = false;
    this.share.hidden = this.fine.root.hidden = !share;
    this.items.root.hidden = share;
    for (const [bp, b] of this.presets) {
      b.setAttribute("aria-pressed", String(share && level.share === bp));
      b.disabled = !can({ share: bp });
    }
    const words = levelWords(catalog, level);
    setText(this.value, words);
    if (isShare(level)) this.fine.draw({ min: 0, max: BP, step: SHARE_STEP }, level.share, words, (share) => can({ share }));
    else this.items.draw({ min: 0, max: Math.max(cap, level.items), step: 1 }, level.items, words, (items) => can({ items }));
  }
}

/** The levels as one part of the editor: the two tests, the two levels and the band, inside the fold. */
export class Levels {
  readonly fold: LevelsFold;
  private readonly tests = new Map<Test, HTMLButtonElement>();
  private readonly rows: Record<Which, LevelRow>;
  private readonly span = el("i", "cond-span");
  private readonly tick = el("i", "cond-now");

  constructor(catalog: Catalog, onTest: (test: Test) => void, onLevel: (which: Which, level: Level) => void) {
    const { text } = catalog;
    const tests = el("div", "cond-tests");
    for (const [test, key] of [["below", UI.ruleFallsBelow], ["reaches", UI.ruleReachesLabel]] as const) {
      const b = el("button", "quiet cond-test", text.get(key));
      b.type = "button";
      b.dataset.test = test;   // a lesson's mark of the test (game/lessons.ts, CAP_RULE)
      b.addEventListener("click", () => onTest(test));
      this.tests.set(test, b);
      tests.append(b);
    }
    this.rows = { n: new LevelRow(catalog, text.get(UI.ruleWhen), (l) => onLevel("n", l)),
      m: new LevelRow(catalog, text.get(UI.ruleUntil), (l) => onLevel("m", l)) };
    const steppers = el("div", "cond-steppers");
    steppers.append(this.rows.n.root, this.rows.m.root);
    const band = el("div", "cond-band");
    band.setAttribute("aria-hidden", "true");
    band.append(this.span, this.tick);
    this.fold = new LevelsFold(text.get(UI.ruleWhen), text.get(UI.ruleUntil), tests, steppers, band);
  }

  /** The rule's test pressed, its two levels with what the store of `cap` items allows, and the band: n..m over
   * 0..cap, the tick at `now` items (none when the store has no line). */
  draw(catalog: Catalog, rule: StoreRule, cap: number, now: number | null): void {
    const items = catalog.isLevel(rule.store);
    for (const [test, b] of this.tests) b.setAttribute("aria-pressed", String(test === rule.test));
    const m = rule.m ?? rule.n;
    const can = (which: Which) => (l: Level) => tryRule({ ...rule, m, [which]: l }, cap, catalog.risesInSteps(rule.store)) !== null;
    this.rows.n.draw(catalog, rule.n, cap, can("n"), () => switchForm(rule.n, rule.test, "on", cap), items);
    this.rows.m.draw(catalog, m, cap, can("m"), () => switchForm(m, rule.test, "off", cap), items);
    this.fold.state(levelWords(catalog, rule.n), levelWords(catalog, m));
    const pct = (items: number) => `${cap > 0 ? (100 * Math.min(cap, Math.max(0, items))) / cap : 0}%`;
    const a = levelAt(rule.n, cap), b = levelAt(m, cap);
    this.span.style.left = pct(Math.min(a, b));
    this.span.style.width = `calc(${pct(Math.max(a, b))} - ${pct(Math.min(a, b))})`;
    this.tick.hidden = now === null;
    if (now !== null) this.tick.style.left = pct(now);
  }
}
