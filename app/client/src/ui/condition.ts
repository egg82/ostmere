// The condition editor (docs/design/opening-screen.md, "The condition editor"), in the Rules tab. A new rule opens
// simple: Do, then When for what the chosen task answers, so the common rule is two taps; More options opens the full
// editor in place (the saved mixes, every chip and store, the levels in condlevels.ts, the Camp's and skills' levels
// and the tasks in condsubject.ts, the rate and goal rows in condfact.ts), and a
// rule being changed opens on it. The sentence and Save sit in a pinned foot. Save sends the whole list with the rule
// appended or replaced in place, a hands task as its saved solo mix (orders.ruleDecisions). What is offered is
// ruleoffers.ts's; levels and ±1 conventions are storerule.ts's. A chip's rule is the chip: changing one offers only
// what it does and Remove, never a level, so the store behind a chip is never shown as a number.
import type { ChipInfo, Condition, Order, View } from "../api/types";
import { sample } from "../game/clock";
import { actionWords, chipOf, removeRule, ruleDecisions, ruleExists, savedVerb } from "../game/orders";
import { townNewRule } from "../game/town";
import { chosen, doChoices, subjectChoices, taskOf, whenChoices, type DoChoice } from "../game/ruleoffers";
import { subjectKey, type SubjectRule } from "../game/subjectrule";
import { bounds, clampRule, defaultRule, readRule, type Test } from "../game/storerule";
import { UI } from "../game/text";
import { noteOrderRemoved, noteOrderSet, noteRuleChanged } from "../telemetry";
import { draftOrder, editDraft, headingWords, sameRule, storeCap, type Draft } from "./conditiondraft";
import { Levels } from "./condlevels";
import { DryNote } from "./conddry";
import { RuleFact } from "./condfact";
import { markPressed, sameChoice } from "./condpress";
import { doRow, footRow, whenRow } from "./condrows";
import { markSubject, SubjectControl, subjectRows } from "./condsubject";
import { bringIntoView, el, setText, tapFeedback } from "./dom";
import type { PartContext } from "./part";

export class ConditionEditor {
  readonly root = el("div", "cond");
  private readonly heading = el("h2", "panel-heading cond-heading");
  private readonly does = el("div", "cond-mixes");
  private readonly chips = el("div", "cond-stores");
  private readonly levels: Levels;
  private readonly subject: SubjectControl;
  private readonly more = el("button", "quiet cond-more");
  private readonly sentence = el("p", "rule-sentence cond-sentence");
  private readonly fact: RuleFact;
  private readonly note = el("p", "editor-note cond-note");
  private readonly dry: DryNote;
  private readonly remove = el("button", "quiet danger");
  private readonly save = el("button", "primary");
  private view: View | null = null;
  private draft: Draft | null = null;
  /** The full editor is open (More options, or a rule being changed). */
  private full = false;

  constructor(private readonly ctx: PartContext, private readonly done: () => void) {
    const { text } = ctx.catalog;
    this.fact = new RuleFact(ctx);
    this.dry = new DryNote(ctx);
    const close = el("button", "editor-close", "✕");
    close.type = "button";
    close.setAttribute("aria-label", text.get(UI.close));
    close.addEventListener("click", () => this.done());
    const head = el("div", "cond-head");
    head.append(this.heading, close);
    this.levels = new Levels(text, (t) => this.setTest(t), (which, d) => this.step(which, d));
    this.subject = new SubjectControl(ctx.catalog, (r) => this.setSubject(r));
    for (const [b, key] of [[this.remove, UI.orderRemove], [this.save, UI.save], [this.more, UI.ruleMoreOptions]] as const) {
      b.type = "button";
      setText(b, text.get(key));
    }
    this.remove.addEventListener("click", () => this.drop());
    this.save.addEventListener("click", () => this.commit());
    this.more.addEventListener("click", () => { tapFeedback(); this.showFull(); });
    const actions = el("div", "sheet-actions cond-actions");
    actions.append(this.remove, this.save);
    const foot = el("div", "cond-foot"); foot.append(this.sentence, this.note, this.dry.root, actions);   // the rule as it reads, beside Save
    const body = el("div", "cond-body"); body.append(head, this.does, this.chips, this.levels.fold.root, this.subject.root, this.fact.root, this.more);   // what scrolls; the foot is outside it
    this.root.append(body, foot);
  }

  /** A new rule, nothing chosen yet: the simple view. Given an offered condition (a guided rule), it starts at that
   * condition's levels, a chip's as the chip. `town`: a rule on the town, which does one of the town's mixes, so it
   * opens on the full editor, where the mixes are. */
  openNew(view: View, offered?: Condition, town = false): void {
    this.full = town;
    const rule = offered ? readRule(offered, this.ctx.catalog.content.scales.quantity_per_item) : null;
    const opened = offered && rule && chipOf(this.ctx.catalog, offered) ? { rule, when: offered } : undefined;
    this.start(view, { index: null, then: null, rule: rule ?? defaultRule("", "below", 0), opened, town });
  }

  /** Rule `index` as conditiondraft.editDraft opens it, in the full editor; false for a rule it does not open. */
  openEdit(view: View, index: number): boolean {
    this.view = view;
    const draft = editDraft(this.ctx.catalog, view, index);
    if (!draft) return false;
    this.full = true;
    this.start(view, draft);
    return true;
  }

  /** A new view while open: the amounts and the tick follow it; the draft stays as it is. A rule that is gone closes. */
  update(view: View): void {
    this.view = view;
    const draft = this.draft;
    if (draft && draft.index !== null && !view.orders[draft.index]) { this.done(); return; }
    this.draw();
  }

  private start(view: View, draft: Draft): void {
    this.view = view;
    this.draft = draft;
    this.fact.reset();
    const { text } = this.ctx.catalog;
    this.save.textContent = text.get(draft.index === null ? UI.orderAdd : UI.save);
    this.remove.hidden = draft.index === null;
    this.levels.fold.open(draft.index !== null);
    this.redraw();
    void this.preview();
  }

  private showFull(): void {
    this.full = true;
    this.redraw();
    void this.preview();
  }

  /** The rows whose choices depend on the view, the task chosen and how full the editor is, then the rest. */
  private redraw(): void {
    const view = this.view;
    if (!view || !this.draft) return;
    this.more.hidden = this.full;
    this.drawDo(view);
    this.drawWhen(view);
    this.draw();
  }

  /** The chip the draft's condition is, while it is one exactly (a chip chosen, or a chip's rule as it opened). */
  private chipNow(): ChipInfo | undefined {
    const draft = this.draft;
    return draft?.opened && sameRule(draft.rule, draft.opened.rule) ? chipOf(this.ctx.catalog, draft.opened.when) : undefined;
  }

  private drawHeading(): void {
    if (this.draft) setText(this.heading, headingWords(this.ctx.catalog, this.draft));
  }

  /** Do: the tasks (and, in the full editor, the saved mixes) as one row. */
  private drawDo(view: View): void {
    this.does.replaceChildren(...doRow(this.ctx.catalog, view, doChoices(this.ctx.catalog, view, this.full, this.draft?.then ?? null, this.draft?.town === true), (c) => this.setDo(c)));
  }

  private setDo(c: DoChoice): void {
    const draft = this.draft;
    if (!draft || !this.view || sameChoice(chosen(this.ctx.catalog, this.view, draft.then), c)) return;
    tapFeedback();
    draft.then = c.kind === "task" ? { kind: "tap_card", card: c.card } : { kind: "switch_mix", mix_id: c.mix };
    this.fact.reset();
    if (!this.full) this.keepOffered(this.view);
    this.redraw();
    void this.preview();
  }

  /** In the simple view, a condition the newly chosen task does not answer is cleared, so what shows chosen is offered. */
  private keepOffered(view: View): void {
    const draft = this.draft!;
    const offer = whenChoices(this.ctx.catalog, view, false, taskOf(this.ctx.catalog, view, draft.then), null);
    const chip = this.chipNow();
    if (chip ? offer.chips.includes(chip) : offer.stores.includes(draft.rule.store)) return;
    draft.rule = defaultRule("", "below", 0);
    draft.opened = undefined;
  }

  private cap(store: string): number {
    return storeCap(this.ctx.catalog, this.view, store);
  }

  /** When: the chips, then the stores, that ruleoffers.whenChoices offers, then (full) the levels and tasks; hidden for
   * a chip's rule being changed and until there is something to offer. */
  private drawWhen(view: View): void {
    const { catalog } = this.ctx;
    const draft = this.draft;
    const editing = draft?.index === null || draft?.subject ? null : draft?.rule.store ?? null;
    const offer = whenChoices(catalog, view, this.full, taskOf(catalog, view, draft?.then ?? null), editing);
    const subjects = this.full ? subjectRows(catalog, view, subjectChoices(catalog, view), (r) => this.setSubject(r, true)) : [];
    const row = draft?.chip === true ? [] : whenRow(catalog, offer.chips, offer.stores, (c) => this.setChip(c), (s) => this.setStore(s), subjects);
    this.chips.hidden = row.length === 0;
    this.chips.replaceChildren(...row);
  }

  private setChip(chip: ChipInfo): void {
    const draft = this.draft;
    const rule = readRule(chip.when, this.ctx.catalog.content.scales.quantity_per_item);
    if (!draft || !rule || this.chipNow()?.chip === chip.chip) return;
    tapFeedback();
    draft.rule = rule;
    draft.opened = { rule, when: chip.when };
    draft.subject = undefined;
    this.draw();
  }

  private setStore(store: string): void {
    const draft = this.draft;
    if (!draft || (draft.rule.store === store && !this.chipNow())) return;
    tapFeedback();
    draft.rule = defaultRule(store, draft.rule.test, this.cap(store));
    draft.subject = undefined;
    this.draw();
    reveal(this.levels.fold.root);
    void this.preview();
  }

  /** A count, a level or a task running: `picked` from the When row (the same subject again changes nothing), else from
   * its control. */
  private setSubject(rule: SubjectRule, picked = false): void {
    const draft = this.draft;
    if (!draft || (picked && draft.subject && subjectKey(draft.subject) === subjectKey(rule))) return;
    if (picked) tapFeedback();
    draft.subject = rule;
    draft.rule = defaultRule("", draft.rule.test, 0);
    draft.opened = undefined;
    this.draw();
    if (picked) reveal(this.subject.root);
  }

  private setTest(test: Test): void {
    if (!this.draft || this.draft.rule.test === test) return;
    tapFeedback();
    this.draft.rule = defaultRule(this.draft.rule.store, test, this.cap(this.draft.rule.store));
    this.draw();
  }

  private step(which: "n" | "m", d: -1 | 1): void {
    if (!this.draft) return;
    const rule = this.draft.rule;
    const next = which === "n" ? { ...rule, n: rule.n + d } : { ...rule, m: (rule.m ?? rule.n) + d };
    this.draft.rule = clampRule(next, this.cap(rule.store));
    this.draw();
  }

  private order(): Order | null {
    return draftOrder(this.ctx.catalog, this.view, this.draft, this.chipNow() !== undefined);
  }

  private draw(): void {
    const { view, draft } = this;
    if (!view || !draft) return;
    const { catalog } = this.ctx;
    const { rule } = draft;
    const chip = this.chipNow();
    const room = bounds(rule.test, this.cap(rule.store), rule.n);
    this.drawHeading();
    const pick = chosen(catalog, view, draft.then);
    markPressed(catalog, view, this.does, this.chips, pick, chip, rule);
    this.levels.fold.root.hidden = !this.full || draft.chip === true || chip !== undefined || rule.store === "";
    const line = view.ledger.find((l) => l.store === rule.store);
    this.levels.draw(rule, room, this.cap(rule.store), line ? sample(line.segment, view.at) / catalog.content.scales.quantity_per_item : null, (n) => catalog.format.count(n));
    this.subject.draw(view, draft.chip ? undefined : draft.subject);
    markSubject(this.chips, draft.subject);
    this.drawSentence(view);
    this.drawFact();
    void this.dry.show(view, draft.index, this.order(), draft.town === true);
  }

  private drawSentence(view: View): void {
    footRow(this.ctx.catalog, view, this.draft?.index ?? null, this.draft?.then ?? null, this.order(), { sentence: this.sentence, note: this.note, save: this.save });
  }

  /** The engine's own number, in the full editor: the view after clearing the rules and running the rule's mix (a dry
   * run, never kept). A task on another lane lands in lumps, so its rate says nothing; a chip's store is never a
   * number; a store with no ledger line has no rate to state. */
  private async preview(): Promise<void> {
    const { draft, view } = this;
    const then = draft?.then && view ? savedVerb(view, this.ctx.catalog, draft.then) : null;
    if (!this.full || then?.kind !== "switch_mix" || draft?.chip || draft?.town || this.chipNow()) return;   // a town mix is set by a rule alone: nothing to run for a number
    if (!view?.ledger.some((l) => l.store === draft?.rule.store)) return;
    await this.fact.ask(then.mix_id, () => this.drawFact());
  }

  private drawFact(): void {
    const draft = this.draft;
    this.fact.show(draft?.then && this.full && !this.chipNow() ? draft.rule.store : null, draft?.then ? actionWords(this.ctx.catalog, draft.then) : "", this.view);
  }

  private commit(): void {
    const order = this.order();
    const { draft, view } = this;
    if (!order || !draft?.then || !view || ruleExists(view, draft.index, order)) return;
    tapFeedback();
    if (draft.index === null) noteOrderSet();
    else noteRuleChanged();
    const decisions = draft.town && draft.index === null ? [townNewRule(view, order)] : ruleDecisions(view, this.ctx.catalog, draft.index, order);
    for (const d of decisions) this.ctx.actions.decide(d);
    this.done();
  }

  private drop(): void {
    const draft = this.draft;
    if (!draft || draft.index === null || !this.view) return;
    tapFeedback();
    noteOrderRemoved();
    this.ctx.actions.decide(removeRule(this.view, draft.index));
    this.done();
  }
}

/** The control a pick just showed, centred in its scroll box (dom.bringIntoView), so it never opens under the foot. */
const reveal = (control: HTMLElement): void => { if (!control.hidden) bringIntoView(document, control); };
