// The Rules tab (docs/design/opening-screen.md, "The Rules tab"): every rule the player has, one line each, beside
// Tasks and Completed. The hands rules, top priority first (the town's rules, ruletown.ts, are drawn as these are, in
// their own order): ≡ (drag to reorder; tap for Move up · Move down · Remove;
// arrow keys move it), the condition as a button that opens the condition editor (condition.ts) in the tab, → and the
// mix slot, which opens a picker. Then Next, what the queue will tap (nextlist.ts), and "Otherwise", the
// player's own mix, whose slot sets the default.
// "+ New rule" once writing rules is open (Keeps.ruleSeen, the taught step); changing a rule is never gated. Under it,
// each side lane's task rules under the lane's label; a ruled lane's always rule, and its row's Change, open that lane's
// task editor (laneedit.ts). Every change sends the whole list (set_orders) in its new order.
import type { Condition, Decision, RuleRun, View } from "../api/types";
import { chipOf, conditionWords, mixRules, moveRule, pointSlot, removeRule, reorderRule, rulesFull, type RuleSlot as Slot } from "../game/orders";
import { UI } from "../game/text";
import { noteOrderRemoved, noteRuleChanged } from "../telemetry";
import { ConditionEditor } from "./condition";
import { el, tapFeedback } from "./dom";
import { LaneEditor } from "./laneedit";
import { alwaysWords, ruledLaneOf } from "../game/lanes";
import { townRules } from "../game/town";
import { nextRows } from "./nextlist";
import { StintPlan } from "./stintplan";
import type { Part, PartContext, RuleTarget } from "./part";
import { RuleDrag } from "./ruledrag";
import { slotPicker } from "./rulepick";
import { laneSections, ruleDot } from "./rulelanes";
import { townSection, type TownRows } from "./ruletown";
import { latelyRows, retickLately } from "./rulelately";
import { retickWhy, whyLine } from "./rulewhy";

/** The mix rule `index` runs, or "" for a rule that does a task. */
function mixIdOf(view: View, index: number): string {
  const then = view.orders[index]?.then;
  return then?.kind === "switch_mix" ? then.mix_id : "";
}

type Mode = { kind: "list" } | { kind: "edit" } | { kind: "lane" } | { kind: "pick"; slot: Slot };

/** What a redraw depends on: a view that changes none of it leaves the tab alone (a press or a focus survives). */
function shape(view: View, fired: readonly string[], ruleSeen: boolean, runs: readonly RuleRun[]): string {
  return JSON.stringify([view.orders, view.queue, view.orders_on, view.order_states, view.order_dry, view.mixes.map((m) => m.id), view.greyed_mix_ids, view.active_mix_id, view.mix_order, view.town_mix_order, ruleSeen, fired, runs]);
}

export class RulesTab implements Part {
  readonly root = el("section", "rules");
  private readonly list = el("div", "rules-list");
  private readonly lanes = el("div", "rules-lanes");
  /** What the rules did lately (rulelately.ts), the tab's last block. */
  private readonly lately = el("div", "rules-lately");
  private readonly cond: ConditionEditor;
  private readonly laneEdit: LaneEditor;
  private readonly plan: StintPlan;
  private view: View | null = null;
  private mode: Mode = { kind: "list" };
  private drawn = "";
  /** The rule whose ≡ menu is open. */
  private menu: number | null = null;
  /** The rule whose handle takes focus after the next draw (it was moved by a key). */
  private focus: number | null = null;
  private readonly drag: RuleDrag;
  /** A press is down inside the tab: a redraw waits for it, so the node under the finger stays. */
  private pressing = false;

  constructor(private readonly ctx: PartContext) {
    this.cond = new ConditionEditor(ctx, () => this.back());
    this.laneEdit = new LaneEditor(ctx, () => this.back());
    this.plan = new StintPlan(ctx, () => this.draw());
    this.drag = new RuleDrag({
      root: this.root, view: () => this.view, group: (view, rule) => this.groupOf(view, rule),
      dropped: (what, target) => this.send(reorderRule(this.view!, what.rule, Number(target.dataset.rule), this.groupOf(this.view!, what.rule))),
      ended: () => { this.pressing = false; this.draw(); },
    });
    this.root.append(this.list, this.lanes, this.lately);
    this.root.addEventListener("pointerdown", () => { this.pressing = true; });
    for (const t of ["pointerup", "pointercancel"]) document.addEventListener(t, () => this.release());
  }

  update(view: View): void {
    this.view = view;
    if (this.menu !== null && this.groupOf(view, this.menu).length === 0) this.menu = null;
    if (this.mode.kind === "pick" && this.mode.slot !== "otherwise" && !mixRules(view).includes(this.mode.slot)) this.mode = { kind: "list" };
    if (this.mode.kind === "edit") { this.cond.update(view); return; }
    if (this.mode.kind === "lane") { this.laneEdit.update(view); return; }
    if (this.pressing || this.drag.active) return;   // drawn on release
    if (this.shape(view) !== this.drawn) this.draw();
  }

  tick(t: number): void {
    if (!this.view || this.mode.kind !== "list") return;
    retickWhy(this.ctx.catalog, this.view, this.root, t);
    retickLately(this.ctx.catalog, this.view, this.ctx.ruleRuns(), this.lately, t);
  }

  /** Opens on the list, on the condition editor for rule `rule`, ("new") on a new rule's, or on a lane's task editor. */
  open(view: View, rule: RuleTarget, offered?: Condition): void {
    this.view = view;
    this.menu = null;
    if (rule !== null && typeof rule === "object") { this.openLane(view, rule.lane, rule.rule); return; }
    if (rule === "new") this.cond.openNew(view, offered);
    this.mode = rule === "new" || (rule !== null && this.cond.openEdit(view, rule)) ? { kind: "edit" } : { kind: "list" };
    this.draw();
  }

  private openLane(view: View, lane: string, rule: number | null): void {
    this.laneEdit.open(view, { lane, rule });
    this.mode = { kind: "lane" };
    this.draw();
  }

  private release(): void {
    if (!this.pressing) return;
    this.pressing = false;
    if (!this.drag.active && this.view && this.mode.kind !== "edit" && this.shape(this.view) !== this.drawn) this.draw();
  }

  /** The rules drawn together with rule `index`, in order: the town's rules, or the hands' (none when it is neither). */
  private groupOf(view: View, index: number): number[] {
    const town = townRules(this.ctx.catalog, view);
    const group = town.includes(index) ? town : mixRules(view).filter((i) => !town.includes(i));
    return group.includes(index) ? group : [];
  }

  private shape(view: View): string {
    return shape(view, this.ctx.fires.fresh, this.ctx.keeps.ruleSeen(), this.ctx.ruleRuns());
  }

  private back(): void {
    this.mode = { kind: "list" };
    this.draw();
  }

  private send(decision: Decision | null): void {
    if (decision === null) return;
    tapFeedback();
    noteRuleChanged();
    this.ctx.actions.decide(decision);
  }

  private draw(): void {
    const view = this.view;
    if (!view) return;
    this.drawn = this.shape(view);
    if (this.mode.kind !== "list") {
      this.list.replaceChildren(...(this.mode.kind === "edit" ? [this.cond.root] : this.mode.kind === "lane" ? [this.laneEdit.root] : this.pickSlot(view, this.mode.slot)));
      this.lanes.replaceChildren();
      this.lately.replaceChildren();
      return;
    }
    const town = townRules(this.ctx.catalog, view);   // listed under the town's heading (ruletown.ts), not here
    const rules = mixRules(view).filter((i) => !town.includes(i));
    const rows = rules.flatMap((i) => this.ruleRow(view, i, [this.condButton(view, i), el("span", "rule-arrow", "→"), this.slot(i, mixIdOf(view, i))], false));
    const write = this.ctx.keeps.ruleSeen() ? [this.newRule(view)] : [];
    this.list.replaceChildren(...rows, ...nextRows(this.ctx, view, this.plan), this.otherwiseRow(view), ...write);
    this.lanes.replaceChildren(...townSection(this.ctx, view, this.townRows(view)), ...laneSections(this.ctx, view, (i) => this.condButton(view, i)));
    this.lately.replaceChildren(...latelyRows(this.ctx.catalog, view, this.ctx.ruleRuns()));
    if (this.focus !== null) {
      this.list.querySelector<HTMLElement>(`.rule-handle[data-rule="${this.focus}"]`)?.focus();
      this.focus = null;
    }
  }

  /** What the town's section needs of the tab: a rule's condition button, a rule's row (the hands' own, ≡ and menu
   * included, around the town's words), and the new-rule control. */
  private townRows(view: View): TownRows {
    return {
      cond: (i) => this.condButton(view, i),
      row: (i, body) => this.ruleRow(view, i, body, true),
      add: () => (this.ctx.keeps.ruleSeen() ? [this.newRule(view, true)] : []),
    };
  }

  /** A rule on one line: ≡, ●, `body` (the hands': its condition, which opens the editor, → and its mix slot), and ≡'s
   * menu under it when open. The town's rules are drawn so too, `town` marking which mix is running. */
  private ruleRow(view: View, index: number, body: HTMLElement[], town: boolean): HTMLElement[] {
    const { catalog } = this.ctx;
    const group = this.groupOf(view, index);
    const first = group[0] === index, last = group[group.length - 1] === index;
    const on = town ? view.town_mix_order : view.mix_order;
    const mixId = mixIdOf(view, index);
    const row = el("div", town ? "rules-row town-rule" : "rules-row");
    row.dataset.rule = String(index);
    row.classList.toggle("active", on === index);
    row.classList.toggle("greyed", view.greyed_mix_ids.includes(mixId));
    const handle = el("button", "rule-handle", "≡");
    handle.type = "button";
    handle.dataset.rule = String(index);
    handle.setAttribute("aria-label", catalog.text.get(UI.ruleHandle));
    handle.setAttribute("aria-expanded", String(this.menu === index));
    handle.addEventListener("click", () => { tapFeedback(); this.menu = this.menu === index ? null : index; this.draw(); });
    handle.addEventListener("keydown", (e) => {
      const step = e.key === "ArrowUp" ? -1 : e.key === "ArrowDown" ? 1 : 0;
      if (step === 0) return;
      e.preventDefault();
      this.move(view, index, step);
    });
    this.drag.attach(handle, () => ({ rule: index }));
    row.append(handle, ruleDot(this.ctx.catalog, on === index), ...body);
    const why = whyLine(catalog, view, index, view.at);
    if (this.menu !== index) return [row, ...why];
    const menu = el("div", "rule-menu");
    const tool = (label: string, disabled: boolean, act: () => void, cls = "quiet"): HTMLButtonElement => {
      const b = el("button", cls, label);
      b.type = "button";
      b.disabled = disabled;
      b.addEventListener("click", act);
      return b;
    };
    menu.append(
      tool(catalog.text.get(UI.ruleUp), first, () => this.move(view, index, -1)),
      tool(catalog.text.get(UI.ruleDown), last, () => this.move(view, index, 1)),
      tool(catalog.text.get(UI.orderRemove), false, () => { this.menu = null; noteOrderRemoved(); tapFeedback(); this.ctx.actions.decide(removeRule(view, index)); }, "quiet danger"),
    );
    return [row, ...why, menu];
  }

  /** Rule `index` one place up or down; its handle keeps the focus, and its menu stays open if it was, where it lands. */
  private move(view: View, index: number, step: -1 | 1): void {
    const group = this.groupOf(view, index);
    const d = moveRule(view, index, step, group);
    const to = group[group.indexOf(index) + step];
    if (!d || to === undefined) return;
    this.focus = to;
    if (this.menu === index) this.menu = to;
    this.send(d);
  }

  /** A rule's condition: a button with an edit mark that opens the condition editor (a ruled lane's always rule: its
   * words, opening the lane's task editor). Never gated. */
  private condButton(view: View, index: number): HTMLElement {
    const order = view.orders[index]!;
    const lane = ruledLaneOf(this.ctx.catalog, order);
    const always = alwaysWords(this.ctx.catalog, order);
    const b = el("button", "rule-cond");
    b.type = "button";
    if (view.orders_on[index] === true) b.dataset.teach = "rule-on";   // a lesson's mark of a rule at work
    b.classList.toggle("chip-rule", chipOf(this.ctx.catalog, order.when) !== undefined);
    b.append(el("span", "rule-cond-text", always ?? conditionWords(this.ctx.catalog, order.when) ?? ""), el("span", "rule-edit-mark", "✎"));
    b.querySelector(".rule-edit-mark")?.setAttribute("aria-hidden", "true");
    b.addEventListener("click", () => {
      tapFeedback();
      if (always !== null && lane !== null) this.openLane(view, lane, index);
      else if (this.cond.openEdit(view, index)) { this.mode = { kind: "edit" }; this.draw(); }
    });
    return b;
  }

  /** A mix slot: tap for the picker. */
  private slot(slot: Slot, mixId: string): HTMLElement {
    const b = el("button", "rule-slot");
    b.type = "button";
    b.dataset.slot = String(slot);
    b.append(el("span", "rule-slot-name", mixId || this.ctx.catalog.text.get(UI.handsIdle)), " ▾");
    b.addEventListener("click", () => {
      tapFeedback();
      this.menu = null;
      this.mode = { kind: "pick", slot };
      this.draw();
    });
    return b;
  }

  private pickSlot(view: View, slot: Slot): HTMLElement[] {
    return slotPicker(this.ctx, view, slot, {
      place: (mixId) => { this.place(view, slot, mixId); this.back(); },
      fresh: () => { this.mode = { kind: "list" }; this.ctx.actions.newMix(slot === "otherwise" ? null : slot); },
      close: () => this.back(),
    });
  }

  private place(view: View, slot: Slot, mixId: string): void {
    const d = pointSlot(view, slot, mixId);
    if (!d) return;
    if (d.kind === "set_orders") noteRuleChanged();
    this.ctx.actions.decide(d);
  }

  /** The last line: what runs when no rule does, the player's own mix. */
  private otherwiseRow(view: View): HTMLElement {
    const row = el("div", "rules-row otherwise");
    const running = view.mix_order === null && view.active_mix_id !== null && !view.greyed_mix_ids.includes(view.active_mix_id);
    row.classList.toggle("active", running);
    row.append(el("span", "rule-handle-gap"), ruleDot(this.ctx.catalog, running), el("span", "rule-when", this.ctx.catalog.text.get(UI.ruleOtherwise)),
      el("span", "rule-arrow", "→"), this.slot("otherwise", view.active_mix_id ?? ""));
    return row;
  }

  /** A new rule from scratch, in the condition editor's simple view (`town`: a rule on the town, in the full view, doing
   * one of the town's mixes). */
  private newRule(view: View, town = false): HTMLElement {
    if (rulesFull(this.ctx.catalog, view)) return el("p", "rules-full", this.ctx.catalog.text.get(UI.ruleFull));
    const b = el("button", town ? "quiet rules-new town-new" : "quiet rules-new", `+ ${this.ctx.catalog.text.get(UI.ruleNew)}`);
    b.type = "button";
    b.addEventListener("click", () => {
      tapFeedback();
      this.cond.openNew(view, undefined, town);
      this.mode = { kind: "edit" };
      this.draw();
    });
    return b;
  }
}
