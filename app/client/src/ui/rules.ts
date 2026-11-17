// The Rules tab (docs/design/opening-screen.md, "The Rules tab"): every rule the player has, one line each, beside
// Tasks and Completed. The hands rules, top priority first (the town's rules, ruletown.ts, are drawn as these are, in
// their own order): ≡ (drag to reorder; tap for Move up · Move down · Remove; arrow keys move it), the condition as a
// button that opens the condition editor (condition.ts) in the tab, → and the mix slot, which opens a picker. Among
// them Next, what the queue will tap (nextlist.ts, ordered by nextorder.ts), a row moved like a rule (game/nextrow.ts:
// the rules under it wait for a ready head), at the bottom until moved. Then "Otherwise", the player's own mix, whose
// slot sets the default. "+ New rule" once writing rules is open (Keeps.ruleSeen, the taught step); changing a rule is
// never gated. Under it, each side lane's task rules under the lane's label; a ruled lane's always rule, and its row's
// Change, open that lane's task editor (laneedit.ts). Every change sends the whole list (set_orders) in its new order.
// Once a second person has hands, a switch at the top, Mine | Camp (ruleswitch.ts), shows one side at a time
// (game/ruleside.ts), kept per device (app/ruleside.ts); it follows a rule the player adds or opens.
import type { Condition, Decision, View } from "../api/types";
import { mixRules, pointSlot, removeRule, rulesFull, type RuleSlot as Slot } from "../game/orders";
import { UI } from "../game/text";
import { actionsOf, ruleActions } from "../game/guardwords";
import { Slider } from "./ruleslide";
import { noteOrderRemoved, noteRuleChanged } from "../telemetry";
import { ConditionEditor } from "./condition";
import { el, tapFeedback } from "./dom";
import { LaneEditor } from "./laneedit";
import type { RuleSide } from "../game/ruleside";
import { browserSide, type SideKept } from "../app/ruleside";
import { condButton } from "./rulecond";
import { ruleHandle, ruleMenu } from "./rulemenu";
import { shape } from "./ruleshape";
import { RuleSides, sideSwitch } from "./ruleswitch";
import { whoChoices, whoPicker, type Who } from "./rulewho";
import { nextHead, nextRows } from "./nextlist";
import { NEXT, nextItems, reorderedItems, steppedItems } from "../game/nextrow";
import { handsGroup, itemsMoved, itemsOf } from "./handsitems";
import { NextOrder } from "./nextorder";
import { StintPlan } from "./stintplan";
import type { Part, PartContext, RuleTarget } from "./part";
import { RuleDrag } from "./ruledrag";
import { slotPicker } from "./rulepick";
import { laneSections, ruleDot } from "./rulelanes";
import { townSection, type TownRows } from "./ruletown";
import { latelyRows, retickLately } from "./rulelately";
import { retickWhy, whyLine } from "./rulewhy";

type Mode = { kind: "list" } | { kind: "edit" } | { kind: "lane" } | { kind: "pick"; slot: Slot } | { kind: "who" };

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
  private readonly sides: RuleSides;
  private readonly drag: RuleDrag;
  private readonly order: NextOrder;
  private readonly slider = new Slider(this.root);
  /** A press is down inside the tab: a redraw waits for it, so the node under the finger stays. */
  private pressing = false;

  constructor(private readonly ctx: PartContext, kept: SideKept = browserSide()) {
    this.sides = new RuleSides(ctx.catalog, kept);
    const editing = { ...ctx, actions: { ...ctx.actions, decide: (d: Decision) => { if (this.view) this.sides.land(this.view, d); ctx.actions.decide(d); } } };   // a saved rule lands on its own side
    this.cond = new ConditionEditor(editing, () => this.back());
    this.laneEdit = new LaneEditor(editing, () => this.back());
    this.plan = new StintPlan(ctx, () => this.draw());
    this.drag = new RuleDrag({
      root: this.root, view: () => this.view, group: (view, rule) => this.itemsOf(view, rule),
      dropped: (what, target) => this.sendItems(this.view!, what.rule, reorderedItems(this.itemsOf(this.view!, what.rule), what.rule, Number(target.dataset.rule))),
      ended: () => { this.pressing = false; this.draw(); },
    });
    this.order = new NextOrder(ctx, this.root, () => this.view, () => { this.pressing = false; this.draw(); });
    this.root.append(this.list, this.lanes, this.lately);
    this.root.addEventListener("pointerdown", () => { this.pressing = true; });
    for (const t of ["pointerup", "pointercancel"]) document.addEventListener(t, () => this.release());
  }

  update(view: View): void {
    this.view = view;
    if (this.menu !== null && this.itemsOf(view, this.menu).length === 0) this.menu = null;
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
    if (rule !== null && typeof rule === "object" && "newFor" in rule) { this.sides.follow(view, "camp"); this.openNew(view, "camp", { lane: rule.newFor }); return; }
    if (rule !== null && typeof rule === "object") { this.openLane(view, rule.lane, rule.rule); return; }
    if (typeof rule === "number") this.sides.follow(view, rule);
    if (rule === "new") this.cond.openNew(view, offered);
    this.mode = rule === "new" || (rule !== null && this.cond.openEdit(view, rule)) ? { kind: "edit" } : { kind: "list" };
    this.draw();
  }

  /** A lane's task editor is the simple one: a rule holding a guard or a fallback opens the full editor instead (or
   * the list, when the full editor does not open it). */
  private openLane(view: View, lane: string, rule: number | null): void {
    const held = rule === null ? undefined : view.orders[rule];
    if (rule !== null && held && (held.unless.length > 0 || held.or_else.length > 0)) { this.open(view, rule); return; }
    this.sides.follow(view, "camp");
    this.laneEdit.open(view, { lane, rule });
    this.mode = { kind: "lane" };
    this.draw();
  }

  private release(): void {
    if (!this.pressing) return;
    this.pressing = false;
    if (!this.drag.active && this.view && this.mode.kind !== "edit" && this.shape(this.view) !== this.drawn) this.draw();
  }

  /** The rows moved with `index` (ui/handsitems.ts). */
  private itemsOf(view: View, index: number): number[] {
    return itemsOf(this.ctx.catalog, view, index, view.queue.length > 0 || this.plan.rows(view).length > 0);
  }

  /** The rows moved with `item` now `moved`, sent; where `item`'s row lands, or null when nothing moved. */
  private sendItems(view: View, item: number, moved: number[] | null): number | null {
    const m = itemsMoved(this.ctx.catalog, view, item, moved);
    if (m) this.send(m.decision, m.shift);
    return m ? m.lands : null;
  }

  private shape(view: View): string {
    return shape(view, this.ctx.fires.fresh, this.ctx.keeps.ruleSeen(), this.ctx.ruleRuns(), this.plan.shape(view), this.sides.now(view));
  }

  private back(): void {
    this.mode = { kind: "list" };
    this.draw();
  }

  private send(decision: Decision | null, shift?: Map<number, number>): void {
    if (decision === null) return;
    this.slider.arm(decision, shift);
    tapFeedback();
    noteRuleChanged();
    this.ctx.actions.decide(decision);
  }

  private draw(): void {
    const view = this.view;
    if (!view) return;
    this.drawn = this.shape(view);
    if (this.mode.kind !== "list") {
      this.list.replaceChildren(...(this.mode.kind === "edit" ? [this.cond.root] : this.mode.kind === "lane" ? [this.laneEdit.root] : this.mode.kind === "who" ? whoPicker(this.ctx, view, (who) => this.openNew(view, "camp", who), () => this.back()) : this.pickSlot(view, this.mode.slot)));
      this.lanes.replaceChildren();
      this.lately.replaceChildren();
      return;
    }
    const side = this.sides.now(view);
    const head = side === null ? [] : [sideSwitch(this.ctx.catalog, side, (to) => { this.sides.set(to); this.menu = null; this.draw(); })];
    const write = (scope?: RuleSide): HTMLElement[] => (this.ctx.keeps.ruleSeen() ? [this.newRule(view, scope)] : []);
    this.list.replaceChildren(...head, ...(side === "camp" ? [] : [...this.handsRows(view), this.otherwiseRow(view), ...write(side ?? undefined)]));
    this.lanes.replaceChildren(...(side === "mine" ? [] : townSection(this.ctx, view, this.townRows(view))), ...laneSections(this.ctx, view, (i) => this.condButton(view, i), side), ...(side === "camp" ? write("camp") : []));
    this.lately.replaceChildren(...latelyRows(this.ctx.catalog, view, this.ctx.ruleRuns()));
    this.slider.play(view);
    if (this.focus !== null) this.list.querySelector<HTMLElement>(`.rule-handle[data-rule="${this.focus}"]`)?.focus();
    this.focus = null;
  }

  /** The hands' rules, one row each, and Next's rows where its row sits (the town's are drawn under its heading,
   * ruletown.ts). */
  private handsRows(view: View): HTMLElement[] {
    const head = nextHead(this.ctx.catalog, this.itemsOf(view, NEXT), this.menu === NEXT, () => this.handle(view, NEXT, UI.ruleNextHandle), (step) => this.move(view, NEXT, step));
    return nextItems(view, handsGroup(this.ctx.catalog, view)).flatMap((i) => (i === NEXT ? nextRows(this.ctx, view, this.plan, this.order, head)
      : this.ruleRow(view, i, [this.condButton(view, i), el("span", "rule-arrow", "→"), this.slot(i, ruleActions(this.ctx.catalog, view.orders[i]!), view.orders[i]!.or_else.length > 0)], false)));
  }

  /** The ≡ of row `index` (a rule's, or NEXT), draggable. */
  private handle(view: View, index: number, label: string): HTMLButtonElement {
    const handle = ruleHandle(this.ctx.catalog.text.get(label), index, this.menu === index, () => { this.menu = this.menu === index ? null : index; this.draw(); }, (step) => this.move(view, index, step));
    this.drag.attach(handle, () => ({ rule: index }));
    return handle;
  }

  /** What the town's section needs of the tab: a rule's condition button, a rule's row (the hands' own, ≡ and menu
   * included, around the town's words). */
  private townRows(view: View): TownRows {
    return {
      cond: (i) => this.condButton(view, i),
      row: (i, body) => this.ruleRow(view, i, body, true),
    };
  }

  /** A rule on one line: ≡, ●, `body` (the hands': its condition, which opens the editor, → and its mix slot), and ≡'s
   * menu under it when open. The town's rules are drawn so too, `town` marking which mix is running. */
  private ruleRow(view: View, index: number, body: HTMLElement[], town: boolean): HTMLElement[] {
    const { catalog } = this.ctx;
    const group = this.itemsOf(view, index);
    const first = group[0] === index, last = group[group.length - 1] === index;
    const on = town ? view.town_mix_order : view.mix_order;
    const row = el("div", town ? "rules-row town-rule" : "rules-row");
    row.dataset.rule = String(index);
    row.classList.toggle("active", on === index);
    row.classList.toggle("greyed", actionsOf(view.orders[index]!).every((a) => a.kind === "switch_mix" && view.greyed_mix_ids.includes(a.mix_id)));
    const handle = this.handle(view, index, UI.ruleHandle);
    row.append(handle, ruleDot(this.ctx.catalog, on === index), ...body);
    const why = whyLine(catalog, view, index, view.at);
    if (this.menu !== index) return [row, ...why];
    const menu = ruleMenu(catalog, {
      first, last, move: (step) => this.move(view, index, step),
      remove: () => { this.menu = null; noteOrderRemoved(); tapFeedback(); this.ctx.actions.decide(removeRule(view, index)); },
    });
    return [row, ...why, menu];
  }

  /** Row `index` (a rule's, or NEXT) one place up or down; its handle keeps the focus, and its menu stays open if it
   * was, where it lands. */
  private move(view: View, index: number, step: -1 | 1): void {
    const to = this.sendItems(view, index, steppedItems(this.itemsOf(view, index), index, step));
    if (to === null) return;
    this.focus = to;
    if (this.menu === index) this.menu = to;
  }

  /** A rule's condition: the button of rulecond.ts, opening the lane's task editor or the condition editor. */
  private condButton(view: View, index: number): HTMLElement {
    return condButton(this.ctx, view, index, {
      lane: (lane, i) => this.openLane(view, lane, i),
      edit: (i) => { if (this.cond.openEdit(view, i)) { this.mode = { kind: "edit" }; this.draw(); } },
    });
  }

  /** A mix slot, worded as `label` (the rule's mixes, or the player's own; with fallbacks it wraps, so none is cut
   * off): tap for the picker. */
  private slot(slot: Slot, label: string, fallbacks = false): HTMLElement {
    const b = el("button", "rule-slot");
    b.type = "button";
    b.dataset.slot = String(slot);
    b.title = label;   // the slot truncates: its full wording on hover, in the picker on touch
    b.append(el("span", fallbacks ? "rule-slot-name has-else" : "rule-slot-name", label || this.ctx.catalog.text.get(UI.handsIdle)), " ▾");
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
      place: (mixId) => {
        const d = pointSlot(view, slot, mixId);
        if (d?.kind === "set_orders") noteRuleChanged();
        if (d) this.ctx.actions.decide(d);
        this.back();
      },
      fresh: () => { this.mode = { kind: "list" }; this.ctx.actions.newMix(slot === "otherwise" ? null : slot); },
      close: () => this.back(),
    });
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

  /** A new rule from scratch, in the condition editor's simple view (`scope`: the side of the page it is made on, offering
   * that side's tasks; on Camp, who it is for is picked first, rulewho.ts). */
  private newRule(view: View, scope?: RuleSide): HTMLElement {
    if (rulesFull(this.ctx.catalog, view)) return el("p", "rules-full", this.ctx.catalog.text.get(UI.ruleFull));
    const b = el("button", "quiet rules-new", `+ ${this.ctx.catalog.text.get(UI.ruleNew)}`);
    b.type = "button";
    b.addEventListener("click", () => {
      tapFeedback();
      const who = scope === "camp" ? whoChoices(this.ctx, view) : [];
      if (who.length > 1) { this.mode = { kind: "who" }; this.draw(); } else this.openNew(view, scope, who[0]);
    });
    return b;
  }

  private openNew(view: View, scope: RuleSide | undefined, who?: Who): void {
    this.cond.openNew(view, undefined, who?.town === true, scope, who?.lane);
    this.mode = { kind: "edit" };
    this.draw();
  }
}
