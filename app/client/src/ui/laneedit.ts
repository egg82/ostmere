// The rule editor's simple view scoped to a lane run by rules (CONTRACT.txt, "A lane run by rules"), in the Rules tab:
// opened by the lane row's Change or an always rule's words. It picks the task only, from the lane's own cards in
// view.cards; the rule's condition stays as it is. Save sends set_orders with that rule's tap_card changed in place,
// or a new always rule appended. Its parts are the condition editor's (condition.ts): the head, the Do row (condrows.ts)
// and the pinned foot with the sentence and Save.
import type { Card, Order, View } from "../api/types";
import { ALWAYS, alwaysWords, laneTask } from "../game/lanes";
import { conditionWords } from "../game/orders";
import { UI } from "../game/text";
import { noteOrderSet, noteRuleChanged } from "../telemetry";
import { sectionHead } from "./condrows";
import { pickRow } from "./cardpick";
import { sectioned } from "../game/cardsections";
import { el, setText, tapFeedback } from "./dom";
import type { PartContext } from "./part";

/** What the lane editor is on: the lane, and the rule it changes (null: a new always rule). */
export interface LaneTarget { lane: string; rule: number | null }

export class LaneEditor {
  readonly root = el("div", "cond");
  private readonly heading = el("h2", "panel-heading cond-heading");
  private readonly does = el("div", "cond-mixes");
  private readonly sentence = el("p", "rule-sentence cond-sentence");
  private readonly save = el("button", "primary");
  private view: View | null = null;
  private target: LaneTarget = { lane: "", rule: null };
  private card: string | null = null;

  constructor(private readonly ctx: PartContext, private readonly done: () => void) {
    const close = el("button", "editor-close", "✕");
    close.type = "button";
    close.setAttribute("aria-label", ctx.catalog.text.get(UI.close));
    close.addEventListener("click", () => this.done());
    this.save.type = "button";
    this.save.addEventListener("click", () => this.commit());
    const head = el("div", "cond-head");
    head.append(this.heading, close);
    const actions = el("div", "sheet-actions cond-actions");
    actions.append(this.save);
    const foot = el("div", "cond-foot");
    foot.append(this.sentence, actions);
    const body = el("div", "cond-body");
    body.append(head, this.does);
    this.root.append(body, foot);
  }

  open(view: View, target: LaneTarget): void {
    this.view = view;
    this.target = target;
    const then = target.rule === null ? undefined : view.orders[target.rule]?.then;
    this.card = then?.kind === "tap_card" ? then.card : null;
    setText(this.save, this.ctx.catalog.text.get(target.rule === null ? UI.orderAdd : UI.save));
    this.draw();
  }

  /** A new view while open: the lane's cards follow it. A rule that is gone closes. */
  update(view: View): void {
    this.view = view;
    if (this.target.rule !== null && !view.orders[this.target.rule]) { this.done(); return; }
    this.draw();
  }

  /** The lane's tasks: its cards in the view. */
  private tasks(view: View): Card[] {
    return view.cards.filter((c) => this.ctx.catalog.laneOf(c.card) === this.target.lane);
  }

  /** The rule as Save would set it, or null while no task is chosen. */
  private order(): Order | null {
    if (this.card === null) return null;
    const when = this.target.rule === null ? ALWAYS : this.view?.orders[this.target.rule]?.when ?? ALWAYS;
    return { when, then: { kind: "tap_card", card: this.card }, unless: [], or_else: [], below_next: false };
  }

  private draw(): void {
    const view = this.view;
    if (!view) return;
    const { catalog } = this.ctx;
    setText(this.heading, catalog.laneLabel(this.target.lane, view));
    const tasks = this.tasks(view);
    this.does.replaceChildren(el("span", "rules-label", catalog.text.get(UI.ruleDo)), ...sectioned(catalog, tasks, (c) => c.card, view).flatMap((g) => {
      const list = el("div", "card-list");
      list.append(...g.items.map((c) => pickRow(this.ctx, c, view, () => this.pick(c.card))));
      return [...sectionHead(g.heading), list];
    }));
    for (const tap of this.does.querySelectorAll<HTMLButtonElement>(".card-tap")) tap.setAttribute("aria-pressed", String(tap.closest<HTMLElement>(".card")?.dataset.card === this.card));
    const order = this.order();
    const hue = this.card === null ? 5 : catalog.rank(this.card) % 6;
    const always = order ? alwaysWords(catalog, order) : null;
    this.sentence.replaceChildren(...(order === null ? [] : always !== null ? [el("b", `rule-action hue-${hue}`, always)]
      : [el("span", "", conditionWords(catalog, order.when) ?? ""), " → ", el("b", `rule-action hue-${hue}`, catalog.cardLabel(this.card ?? ""))]));
    const was = this.target.rule === null ? undefined : view.orders[this.target.rule]?.then;
    this.save.disabled = order === null || (was?.kind === "tap_card" && was.card === this.card);
  }

  private pick(card: string | null): void {
    if (card === null || card === this.card) return;
    tapFeedback();
    this.card = card;
    this.draw();
  }

  private commit(): void {
    const view = this.view;
    if (!view || this.card === null) return;
    tapFeedback();
    if (this.target.rule === null) noteOrderSet();
    else noteRuleChanged();
    this.ctx.actions.decide(laneTask(view, this.target.rule, this.card));
    this.done();
  }
}
