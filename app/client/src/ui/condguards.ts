// The full editor's "Unless" (docs/design/rule-guards.md, "How the page words it"; behind More options): the rule's
// guards as words, each with a remove, and an add that picks what to watch. A chip, a level or a task's count is one
// tap; a store then takes one test and one level, in either form (game/guarddraft.ts builds the condition and keeps
// its release one item past the value). Up to Content.limits.max_unless guards, none twice.
import type { Condition, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { guardWords } from "../game/guardwords";
import { buildGuard, defaultGuard, guardValid, otherForm, withTest, type Guard } from "../game/guarddraft";
import { sameCondition } from "../game/orders";
import { subjectChoices, whenChoices } from "../game/ruleoffers";
import { levelWords } from "../game/storerule";
import { buildSubject } from "../game/subjectrule";
import { UI } from "../game/text";
import { LevelRow } from "./condlevels";
import { subjectRows } from "./condsubject";
import { storeCap } from "./conditiondraft";
import { bringIntoView, el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

function button(cls: string, label: string, click: () => void): HTMLButtonElement {
  const b = el("button", cls, label);
  b.type = "button";
  b.addEventListener("click", () => { tapFeedback(); click(); });
  return b;
}

export class GuardEditor {
  readonly root = el("div", "cond-guards");
  private readonly level: LevelRow;
  private adding = false;
  /** The store guard being written; null until a store is picked. */
  private picked: Guard | null = null;
  private view: View | null = null;
  private unless: Condition[] = [];

  constructor(private readonly ctx: PartContext, private readonly change: (unless: Condition[]) => void) {
    this.level = new LevelRow(ctx.catalog, ctx.catalog.text.get(UI.ruleLevel), (l) => this.set({ ...this.picked!, level: l }));
  }

  /** The guards as they stand, drawn while `show` (the full editor is open). */
  draw(view: View, unless: Condition[], show: boolean): void {
    this.view = view;
    this.unless = unless;
    this.root.hidden = !show;
    const { catalog } = this.ctx;
    const { text } = catalog;
    const max = catalog.content.limits.max_unless;
    const head = el("div", "cond-guards-head");
    head.append(el("span", "rules-label", text.get(UI.ruleUnlessLabel)), el("span", "cond-guards-hint", text.get(UI.ruleUnlessHint)));
    const held = unless.map((g, i) => {
      const row = el("div", "cond-guard");
      const words = guardWords(catalog, view, g) ?? "";
      const drop = button("quiet cond-guard-drop", text.get(UI.orderRemove), () => this.change(unless.filter((_, j) => j !== i)));
      drop.setAttribute("aria-label", `${text.get(UI.orderRemove)} ${words}`);
      row.append(el("span", "cond-guard-words", words), drop);
      return row;
    });
    const add = button("quiet cond-guard-add", text.get(UI.ruleUnlessAdd), () => { this.adding = !this.adding; this.picked = null; this.draw(view, unless, show); });
    add.hidden = unless.length >= max;
    add.setAttribute("aria-expanded", String(this.adding && unless.length < max));
    this.root.replaceChildren(head, ...held, add, ...(this.adding && unless.length < max ? [this.picker(view)] : []));
  }

  private picker(view: View): HTMLElement {
    const { catalog } = this.ctx;
    const offer = whenChoices(catalog, view, true, [], null);
    const pick = el("div", "cond-guard-pick");
    const row = el("div", "cond-guard-what");
    const chips = offer.chips.map((c) => button("quiet cond-store cond-chip", catalog.label(c.label_key), () => this.add(c.when)));
    const stores = offer.stores.map((s) => {
      const b = button("quiet cond-store", catalog.storeTitle(s), () => this.set(defaultGuard(s, catalog.isLevel(s) ? storeCap(catalog, view, s) : null)));
      b.dataset.store = s;
      b.setAttribute("aria-pressed", String(this.picked?.store === s));
      return b;
    });
    row.append(...chips, ...stores, ...subjectRows(catalog, view, subjectChoices(catalog, view), (r) => this.add(buildSubject(catalog, r))));
    pick.append(row, ...(this.picked ? this.levels(view, this.picked) : []));
    return pick;
  }

  /** The picked store's test and level, and the button that adds it. */
  private levels(view: View, g: Guard): HTMLElement[] {
    const { catalog } = this.ctx;
    const { text } = catalog;
    const cap = storeCap(catalog, view, g.store);
    const items = catalog.isLevel(g.store);
    const q = catalog.content.scales.quantity_per_item;
    const tests = el("div", "cond-tests");
    for (const [test, key] of [["reaches", UI.ruleUnlessOrMore], ["below", UI.ruleUnlessUnder]] as const) {
      const b = button("quiet cond-test", text.get(key), () => this.set(withTest(g, test, cap, items)));
      b.setAttribute("aria-pressed", String(g.test === test));
      tests.append(b);
    }
    this.level.draw(catalog, g.level, cap, (l) => guardValid({ ...g, level: l }, cap), () => otherForm(g, cap), items);
    const done = button("primary cond-guard-done", text.get(UI.ruleUnlessDone), () => this.add(buildGuard(g, q, items)));
    done.disabled = !guardValid(g, cap);
    const words = el("span", "cond-guard-words", guardWords(catalog, view, buildGuard(g, q, items)) ?? levelWords(catalog, g.level));
    return [el("div", "cond-label cond-guard-store", catalog.storeTitle(g.store)), tests, this.level.root, words, done];
  }

  private set(g: Guard): void {
    this.picked = g;
    if (!this.view) return;
    this.draw(this.view, this.unless, true);
    const pick = this.root.querySelector<HTMLElement>(".cond-guard-pick");
    if (pick) bringIntoView(document, pick);
  }

  private add(guard: Condition): void {
    this.adding = false;
    this.picked = null;
    if (!this.unless.some((u) => sameCondition(u, guard))) this.change([...this.unless, guard]);
    else if (this.view) this.draw(this.view, this.unless, true);
  }
}

