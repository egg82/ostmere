// The ledger (docs/design/redesign.md, "Ledger"): grouped, each group's label drawn while it has a row: the player's
// stores (Yours), then the threats at them (ui/threats.ts). A line per store the view lists, the Camp store excepted
// (it is the Camp bar), each from when it first means something (game/shown.ts): one that asks something (red, starved or carrying an offer), or is falling, full
// while fed, or covered by a rule. Once drawn a line stays, kept for the account (game/keeps.ts). A line is white unless it
// is falling with nothing covering it, or starved (dry while something waits on it, covered or not); then it is red,
// with its answer right beside it. The store's order card is never built from the line: the first time (the rule's lesson
// may start) its rule shows inline under the line with Show me, which opens the editor and walks it; after that the red
// line carries a quiet mark (until touched) and the player writes the rule in the Rules tab. A card for a rising line
// (cues.risingCard: a side lane's task or a hands build) is marked once the line is full or rising, and kept until a rule
// is set. Once a rule on that store and test exists (at whatever levels) and the line is still red, the line shows that
// rule's condition and action with Change, which opens the Rules tab on that rule's editor.
// A full store that something
// still feeds says so and that the extra is lost, never in an alarm's colour; a red line with no order card to answer it names what draws on it most, with
// Edit mix. The first full store the hands fill (game/caphint.ts) carries the quiet mark and starts the cap rule's lesson,
// once writing rules is open; nothing is built from it. The first dry store a mix card stopped on (game/dryhint.ts) carries
// it too and starts the dry store's lesson. A line's "full in" and "empty in" are the forecast's (game/forecast.ts), so a rule that takes from the
// store, tops it up or stops it short first leaves no time drawn.
// While a mix share is dragged, the lines its cards feed or draw on light up.
import type { LedgerLine, OrderCard, View } from "../api/types";
import { sample } from "../game/clock";
import { capStore } from "../game/caphint";
import { dryCue, type DryCue } from "../game/dryhint";
import { largestDrain, offeredCard, risingCard, risingLine } from "../game/cues";
import { emptyAt, fullAt } from "../game/forecast";
import { runningMix } from "../game/mix";
import { fullAndFed, LEDGER_FEATURE, lineJoins, redLine } from "../game/shown";
import { actionWords, ruleFor, rulesFull, ruleWords } from "../game/orders";
import { CAP_RULE, DRY_STORE, guided, guidedRule, ruleSubject, ruleWaits } from "../game/lessons";
import { readingMs } from "../game/reading";
import { stalled } from "../game/stall";
import { storyMarks } from "../game/story";
import { UI } from "../game/text";
import { noteOrderShown } from "../telemetry";
import { el, place, pulse, rekey, setText, tapFeedback } from "./dom";
import { markNew, unmark } from "./fresh";
import type { Part, PartContext } from "./part";
import { Threats } from "./threats";

interface Row {
  line: LedgerLine;
  /** The ledger item keyed into the list: the line, then its inline order card. */
  node: HTMLElement;
  box: HTMLElement;
  offer: HTMLElement | null;
  /** What the offer shows, so it is rebuilt only when that changes. */
  offerKey: string;
  amount: HTMLElement;
  rate: HTMLElement;
  eta: HTMLElement;
  edit: HTMLButtonElement;
}

/** What a line's inline offer shows: the store's order card on offer, the rule set on its store and test (-1: none),
 * and whether the offer is shown at all. */
interface Offer {
  card: OrderCard | undefined;
  rule: number;
  shown: boolean;
}

export class Ledger implements Part {
  readonly root = el("section", "ledger");
  private readonly list = el("div", "ledger-lines");
  /** Where a phone draws the lines that are red or full, above the task cards (`split`); empty on a desktop. */
  readonly asks = el("div", "ledger-lines ledger-asks");
  private split = false;
  private readonly threats: Threats;
  private readonly yours: HTMLElement;
  private readonly threatsLabel: HTMLElement;
  private rows = new Map<string, Row>();
  private view: View | null = null;
  /** Stores whose order card was offered by the stall rule or a rising line: kept until set, so it does not vanish
   * under a tap or a dip. */
  private readonly kept = new Set<string>();
  /** Lines whose mark the player touched this page session. */
  private readonly touched = new Set<string>();

  constructor(private readonly ctx: PartContext) {
    const { text } = ctx.catalog;
    this.threats = new Threats(ctx);
    this.yours = el("h3", "ledger-group", text.get(UI.ledgerYours));
    this.threatsLabel = el("h3", "ledger-group", text.get(UI.ledgerThreats));
    this.root.append(el("h2", "panel-heading", text.get(UI.ledgerHeading)), this.yours, this.list, this.threatsLabel, this.threats.root);
  }

  update(view: View, prev: View | null): void {
    this.view = view;
    const { catalog } = this.ctx;
    const all = view.ledger.filter((l) => l.store !== catalog.campStore && !catalog.stores.get(l.store)?.hidden);
    const offers = new Map(all.map((l) => [l.store, this.offerFor(l, view)]));
    const on = this.ctx.catalog.unlocked(view, "feature", LEDGER_FEATURE);
    const story = storyMarks(catalog, view).stores;
    const lines = on ? all.filter((l) => this.drawn(l, view, offers.get(l.store)?.shown === true, story.has(l.store))) : [];
    this.threats.update(view, prev);
    const was = new Map((prev?.ledger ?? []).map((l) => [l.store, l]));
    const fresh = new Set(lines.filter((l) => !this.rows.has(l.store)).map((l) => l.store));
    const cap = guided(CAP_RULE, view, this.ctx.keeps) ? capStore(catalog, view) : null;
    const dry = guided(DRY_STORE, view, this.ctx.keeps) ? dryCue(catalog, view) : null;
    this.rows = rekey(lines, (l) => l.store, this.rows, (l) => this.make(l));
    for (const line of lines) {
      const row = this.rows.get(line.store);
      const offer = offers.get(line.store);
      if (!row || !offer) continue;
      row.line = line;
      row.box.classList.toggle("story", story.has(line.store));   // the story mark (game/story.ts)
      this.restyle(row, view, offer, was.get(line.store), prev !== null && fresh.has(line.store), cap === line.store, dry?.store === line.store ? dry : null);
    }
    this.arrange(view.at);
  }

  tick(t: number): void {
    const { format, text } = this.ctx.catalog;
    for (const row of this.rows.values()) {
      const { line } = row;
      const { cap } = line;
      const value = sample(line.segment, t);
      setText(row.amount, format.amount(value, cap));
      const full = fullAndFed(line, t);
      const drain = row.offer === null && this.red(line) ? this.drain(line) : "";
      if (row.box.classList.contains("full") !== full) { row.box.classList.toggle("full", full); this.arrange(t); }
      row.edit.hidden = !drain || !this.view || runningMix(this.view) === null;
      const eta = full ? text.get(UI.full) : this.eta(line, t);
      setText(row.eta, drain ? `${eta} · ${drain}` : eta);
    }
  }

  /** Draw the red and full lines apart from the rest (`on`, a phone: they sit above the cards, the rest stay with the
   * ledger) or all together. */
  setSplit(on: boolean): void {
    this.split = on;
    this.arrange(this.view?.at ?? 0);
  }

  /** Seat each row in the list or, when split, in `asks` if its line is red or full at `t`; the ledger hides with no
   * line left in it and no threat, and each group's label with its group. */
  private arrange(t: number): void {
    const rest: HTMLElement[] = [];
    const asks: HTMLElement[] = [];
    for (const { line, node } of this.rows.values()) (this.split && (this.red(line) || fullAndFed(line, t)) ? asks : rest).push(node);
    place(this.list, rest);
    place(this.asks, asks);
    this.yours.hidden = rest.length === 0;
    this.threatsLabel.hidden = this.threats.empty;
    this.root.hidden = rest.length === 0 && this.threats.empty;
  }

  /** Lights the lines these cards feed or draw on (null: none). */
  highlight(cards: string[] | null): void {
    const lit = new Set(cards ?? []);
    for (const row of this.rows.values()) row.box.classList.toggle("lit", row.line.contributions.some((c) => lit.has(c.runner)));
  }

  /** Red as game/shown.ts says, except a store that only feeds a bonus (StoreInfo.bonus_bp): running low on it misses
   * the bonus and asks nothing, so it is never drawn as an alarm. */
  private red(line: LedgerLine): boolean {
    return redLine(line) && this.ctx.catalog.stores.get(line.store)?.bonus_bp == null;
  }

  /** The label of what draws on a red line most (a card or a standing action), or "" (cues.largestDrain). */
  private drain(line: LedgerLine): string {
    const { catalog } = this.ctx;
    const runner = this.view ? largestDrain(line, this.view) : null;
    if (runner === null) return "";
    if (catalog.cards.has(runner)) return catalog.cardLabel(runner);
    return catalog.label(catalog.content.standing_infos.find((a) => a.action === runner)?.label_key);
  }

  private eta(line: LedgerLine, t: number): string {
    const { text, format } = this.ctx.catalog;
    const bonus = this.ctx.catalog.stores.get(line.store)?.bonus_bp;
    if (line.starved) return bonus == null ? text.get(UI.starved) : text.fill(UI.unfed, format.figures([bonus]));
    const view = this.view;   // the times are the forecast's: a rule that tops up or takes from the store first leaves none
    const empty = line.falling && view ? emptyAt(view, line.store, t) : null;
    if (empty !== null) return text.fill(UI.empties, { d: format.duration(empty - t) });
    const full = line.net_per_hour > 0 && view ? fullAt(view, line.store, t) : null;
    if (full !== null) return text.fill(UI.fills, { d: format.duration(full - t) });
    return "";
  }

  /** A line is drawn once it joins (game/shown.ts) or a story beat waits on it (`story`), and stays: kept for the
   * account, so a reload keeps it too. */
  private drawn(line: LedgerLine, view: View, offered: boolean, story: boolean): boolean {
    const { keeps } = this.ctx;
    if (keeps.ledgerShown(line.store)) return true;
    if (!story && !lineJoins(line, view, offered)) return false;
    keeps.keepLedgerLine(line.store);
    return true;
  }

  /** `arriving`: the line joins the ledger with this view, so it takes its turn in the reveal. `capped`: the line is the
   * cap rule's lesson's subject (game/caphint.ts); `dry`, the dry store's lesson's (game/dryhint.ts). */
  private restyle(row: Row, view: View, offer: Offer, before: LedgerLine | undefined, arriving: boolean, capped: boolean, dry: DryCue | null): void {
    const { line } = row;
    const red = this.red(line);
    row.box.classList.toggle("alarm", red);
    row.box.classList.toggle("rising", line.net_per_hour > 0);
    const { card, rule, shown } = offer;
    this.inline(row, shown ? card : undefined, rule);
    this.capLine(row, capped);
    this.dryLine(row, dry);
    this.hint(row, (capped && [null, CAP_RULE].includes(this.ctx.lesson())) || (dry !== null && [null, DRY_STORE].includes(this.ctx.lesson())) || (shown && card !== undefined && rule < 0 && this.view !== null && !guidedRule(this.view, this.ctx.keeps, card)));
    row.offer?.classList.toggle("calm", !red);
    setText(row.rate, this.ctx.catalog.format.perMinute(line.net_per_hour));
    if (before && this.red(before) && !red) this.ctx.arrivals.effect(row.box, "store", () => pulse(row.box, "settle"));
    if (arriving) this.ctx.arrivals.arrive(row.box, "store", line.store, readingMs(row.node.textContent ?? ""));   // read before the cards
  }

  /** The line's offer now; a card offered by the stall rule or a rising line is kept until a rule is set. */
  private offerFor(line: LedgerLine, view: View): Offer {
    const { catalog } = this.ctx;
    const red = this.red(line);
    const card = offeredCard(catalog, view, line.store);
    const rule = card === undefined ? -1 : ruleFor(view, card);
    if (card && (stalled(this.ctx.streak, card) || (risingCard(catalog, card) && risingLine(line, view.at)))) this.kept.add(line.store);
    if (rule >= 0) this.kept.delete(line.store);
    const shown = card !== undefined && (rule >= 0 ? red : (red || this.kept.has(line.store)) && !rulesFull(catalog, view));
    return { card, rule, shown };
  }

  /** The cap rule's lesson starts from this line while it is the subject: its trigger, with the store it is about. */
  private capLine(row: Row, on: boolean): void {
    if (on) Object.assign(row.box.dataset, { teach: "cap-line", store: row.line.store });
    else if (row.box.dataset.teach === "cap-line") { delete row.box.dataset.teach; delete row.box.dataset.store; }
  }

  /** The dry store's lesson starts from this line while it is the subject: its trigger, with the stopped card and its maker. */
  private dryLine(row: Row, cue: DryCue | null): void {
    if (cue) Object.assign(row.box.dataset, { teach: "dry-line", store: cue.store, card: cue.card, maker: cue.maker });
    else if (row.box.dataset.teach === "dry-line") { delete row.box.dataset.teach; delete row.box.dataset.store; delete row.box.dataset.card; delete row.box.dataset.maker; }
  }

  /** The quiet mark, until the player touches the line: on a red line a rule could answer once the first rule's lesson
   * is behind, and on the cap rule's or the dry store's line while no other lesson runs. Nothing is offered or built. */
  private hint(row: Row, on: boolean): void {
    const store = row.line.store;
    if (on && !this.touched.has(store)) markNew(row.box, () => this.touched.add(store));
    else unmark(row.box);
  }

  /** The line's guide to the first rule's lesson, shown under it while the line is red and gone when it is not: Add rule, or, when a rule on
   * its condition is set (`rule` >= 0) and the line is still red, that rule's action and Change. */
  private inline(row: Row, card: OrderCard | undefined, rule: number): void {
    const { catalog } = this.ctx;
    const order = rule >= 0 ? this.view?.orders[rule] : undefined;
    const words = card ? ruleWords(catalog, order ? { when: order.when, then: order.then } : { when: card.when, then: card.then }) : null;
    const guide = card !== undefined && rule < 0 && this.view !== null && guidedRule(this.view, this.ctx.keeps, card);
    const waits = guide && ruleWaits(card, this.ctx.lesson(), this.ctx.lessonSubject());   // guided, it waits out another lesson or offer
    const key = card && words && !waits && (guide || rule >= 0) ? `${rule >= 0}|${words.when}|${words.action}|${guide}` : "";
    if (key === row.offerKey) return;
    row.offerKey = key;
    row.offer?.remove();
    row.offer = null;
    if (key === "" || !card || !words) return;
    const offer = el("div", "line-order");
    const change = rule >= 0;
    const button = el("button", change ? "quiet" : "primary lesson-go", catalog.text.get(change ? UI.orderChange : UI.lessonShow));
    button.type = "button";
    if (guide) Object.assign(button.dataset, { teach: "rule-offer" }, ruleSubject(card));
    button.addEventListener("click", () => {
      tapFeedback();
      if (change) { this.ctx.actions.openRules(rule); return; }
      this.ctx.actions.openRules("new", card.when);   // the rule's lesson: built on the editor
    });
    const sentence = el("p", "rule-sentence");
    const hue = card.then.kind === "tap_card" ? catalog.rank(card.then.card) % 6 : 5;
    sentence.append(el("span", "", words.when), " → ", el("b", `rule-action hue-${hue}`, order ? actionWords(catalog, order.then) : words.action));
    offer.append(sentence, button);
    row.offer = offer;
    row.node.append(offer);
    if (noteOrderShown(row.line.store)) this.ctx.arrivals.arrive(offer, "store", row.line.store);
  }

  private make(line: LedgerLine): Row {
    const box = el("div", "line");
    const node = el("div", "ledger-item");
    node.append(box);
    const edit = el("button", "line-edit", this.ctx.catalog.text.get(UI.editMix));
    edit.type = "button";
    edit.hidden = true;
    edit.addEventListener("click", () => { tapFeedback(); this.ctx.actions.editMix(null); });
    const row: Row = {
      line, node, box, offer: null, offerKey: "", edit,
      rate: el("span", "line-rate"), amount: el("span", "line-amount"), eta: el("span", "line-eta"),
    };
    box.append(el("span", "line-name", this.ctx.catalog.storeTitle(line.store)), row.rate, row.amount, row.eta, edit);
    return row;
  }
}
