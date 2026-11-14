// The story at the seam between the art and the controls (docs/design/opening-screen.md, "One column of attention").
// The head, at the art's top: the Camp bar, the chips (an icon from the tone, the word, and under it what the chip
// costs; each once its cure is on screen, game/shown.ts), what the player carries (a feature with a label, dotted
// when it arrives) and the Chronicle button (on a phone the bottom bar's Book instead), dotted when a line left the strip
// before the player touched anything after it showed. The story strip, off the art: the newest story lines that fit (game/chronicle.ts, inStrip), whole and oldest
// first, the older dimmer, in room kept for the tallest story line the content can write (Content.line_infos, laid out
// unseen in the strip's one cell; ui/stripfit.ts counts how many fit, at least the newest). The Feedback button
// (feedback.ts) opens the tester's sheet from the panel's foot. Every line, every rule's start and let-go and every fight
// goes to the chronicle (ui/chroniclesheet.ts) with its game second, kind and cause. Lines arrive in (at, seq) order with
// each Step; their text is the content's. The aim (ui/aim.ts) is the story's too. ui/headseat.ts seats the head, the
// aim and the strip.
import type { LogLine, View } from "../api/types";
import { awayLines, type Placement } from "../game/awaylines";
import { entries, poolLine, type Window } from "../game/fights";
import { toppedSince } from "../game/prestige";
import { readingMs } from "../game/reading";
import type { Catalog } from "../game/catalog";
import { shownChips } from "../game/shown";
import { UI } from "../game/text";
import { AimLine } from "./aim";
import { CampBar } from "./camp";
import { el, keyed, tapFeedback } from "./dom";
import { FeedbackSheet } from "./feedback";
import { Journal } from "./journal";
import { ChronicleSheet } from "./chroniclesheet";
import { chipHints } from "../game/hints";
import { markNew, unmark } from "./fresh";
import { fitting } from "./stripfit";
import type { Part, PartContext } from "./part";
import { inStrip, type EntryKind, type Past } from "../game/chronicle";
import { causeWords } from "../game/chronwords";
import { ruleEntries } from "../game/rulerows";

const TOUCHES = ["pointerdown", "keydown"] as const;
const KEEP = 200;

export class Story implements Part {
  /** The story strip: the newest lines that fit its room, whole (ui/headseat.ts seats it under the art). */
  readonly root = el("section", "strip");
  /** The Camp bar, chips and Chronicle: on the art's top, or just above the art on a phone (ui/headseat.ts seats it). */
  readonly head = el("div", "scene-head");
  private readonly chips = el("div", "chips");
  private readonly aimLine: AimLine;
  private readonly lines = el("ol", "lines");
  private readonly roomCell = el("div", "strip-room");
  /** The Feedback button: Screen seats it at the panel's foot. */
  readonly feedbackButton: HTMLButtonElement;
  private readonly camp: CampBar;
  private readonly chronicle: ChronicleSheet;
  /** The rule entries already in the chronicle, by id (game/rulerows.ts). */
  private readonly ruled = new Set<string>();
  private readonly journal: Journal;
  private readonly chronicleOpen: HTMLButtonElement;
  /** The bottom bar's Book on a phone (ui/tabs.ts seats it): the Chronicle button's twin there. */
  readonly book = el("button", "tab");
  /** When the player last touched the page (performance.now()). */
  private touchedAt = -Infinity;
  private chipRows = new Map<string, { node: HTMLElement }>();
  /** Chips whose mark the player touched this page session. */
  private readonly touchedChips = new Set<string>();
  /** The game second of the latest view or line: what a line the page words itself is stamped with. */
  private nowAt = 0;
  /** When each line in the strip was first seen shown (performance.now()); a line drawn still, not new, has no entry. */
  private readonly shownAt = new WeakMap<Element, number>();
  /** The lines written so far with their game seconds, oldest first (KEEP at most): what a redrawn screen restores. */
  readonly keys: Past[] = [];

  /** `showAsks`: what the chronicle's count of waiting asks opens (ui/asks.ts). */
  constructor(private readonly ctx: PartContext, showAsks: () => void = () => undefined) {
    this.camp = new CampBar(ctx);
    this.aimLine = new AimLine(ctx);
    this.chronicle = new ChronicleSheet(ctx.catalog, ctx.keeps, showAsks);
    this.journal = new Journal(ctx);
    this.lines.setAttribute("aria-live", "polite");
    const open = el("button", "chron-open", ctx.catalog.text.get(UI.chronicle));
    this.book.textContent = ctx.catalog.text.get(UI.tabBook);
    this.book.dataset.tab = "book";
    for (const b of [open, this.book]) {
      b.type = "button";
      b.addEventListener("click", () => { tapFeedback(); unmark(open); unmark(this.book); this.chronicle.show(); });
    }
    this.chronicleOpen = open;
    for (const t of TOUCHES) document.addEventListener(t, () => { this.touchedAt = performance.now(); }, { capture: true });
    const feedback = new FeedbackSheet(ctx);
    this.feedbackButton = feedback.button;
    this.head.append(this.camp.root, this.chips, open);
    this.root.append(this.room(), this.lines, this.chronicle.root, this.journal.root, feedback.root);
  }

  /** Every story line the content can write, unseen in the strip's one cell with the shown line: the cell is as tall as
   * the tallest of them at the strip's width, so no line is cut and none arriving changes the strip's height. */
  private room(): HTMLElement {
    const room = this.roomCell;
    room.setAttribute("aria-hidden", "true");
    const texts = new Set(this.ctx.catalog.content.line_infos.filter((l) => inStrip(l.kind)).map((l) => this.ctx.catalog.text.get(l.key)).filter((t) => t));
    room.append(...[...texts].map((t) => el("span", "", t)));
    return room;
  }

  update(view: View, prev: View | null): void {
    const { catalog } = this.ctx;
    this.nowAt = Math.max(this.nowAt, view.at);
    this.chronicle.seen(this.nowAt);
    this.chronicle.waiting(view.offers.filter((o) => o.answer === null).length);
    const carried = catalog.content.feature_infos.filter((f) => f.label_key && catalog.unlocked(view, "feature", f.feature));
    this.journal.update(view);
    const book = (f: string): string => (this.journal.shown && f === catalog.content.journal?.feature ? "journal" : "keep");
    const items = [...shownChips(catalog, view).map((c) => `chip:${c}`), ...carried.map((f) => `${book(f.feature)}:${f.feature}`)];
    this.chipRows = keyed(this.chips, items, (k) => k, this.chipRows, (k) => ({ node: this.item(k) }));
    this.hintChips(view);
    this.camp.update(view);
    this.aimLine.update(view);
    this.fightLines(view, prev);
    this.topLines(view, prev);
    this.ruleLines();
  }

  /** Each rule's latest start and let-go the chronicle does not hold yet (game/rulerows.ts). */
  private ruleLines(): void {
    for (const { id, entry } of ruleEntries(this.ctx.catalog, this.ctx.ruleRuns())) {
      if (this.ruled.has(id)) continue;
      this.ruled.add(id);
      this.chronicle.add(entry);
    }
  }

  /** A skill that reached its phase's top since the last view: one line, saying how long ago when that was a return
   * (CONTRACT.txt, "PRESTIGE PHASES"), never what the wait missed. It takes its turn like the step's other lines. */
  private topLines(view: View, prev: View | null): void {
    const { text, format } = this.ctx.catalog;
    for (const { skill, at } of toppedSince(prev, view)) {
      const name = this.ctx.catalog.skillLabel(skill);
      this.say(view.at - at >= 60 ? text.fill(UI.prestigeReached, { skill: name, d: format.duration(view.at - at) })
        : text.fill(UI.prestigeReachedNow, { skill: name }), `top:${skill}:${at}`, "level", null);
    }
  }

  /** What fights happened since the last view, as chronicle entries under their runner: each fight of a window its own entry
   * (the shuffle-bag labels, each worded from its runner's pool when it has one), a long window one summary line
   * (game/fights.ts). They take their turns in the arrival queue with the step's other lines. */
  private fightLines(view: View, prev: View | null): void {
    const { catalog } = this.ctx;
    const { text } = catalog;
    const save = this.ctx.saveId();
    const standing = (runner: string) => catalog.content.standing_infos.find((a) => a.action === runner);
    const name = (runner: string): string => catalog.cards.has(runner) ? catalog.cardLabel(runner) : catalog.label(standing(runner)?.label_key);
    const fight = (runner: string) => catalog.cards.get(runner)?.fight ?? standing(runner)?.fight ?? null;
    const causes: Array<string | null> = [];   // each entry's cause, in the order entries() words them: a pool's line
    const one = (runner: string, kind: "won" | "lost", k: number): string => {   // names no runner, ui.fight.* does
      const pool = (kind === "won" ? fight(runner)?.won_line_keys : fight(runner)?.lost_line_keys) ?? [];
      causes.push(pool.length > 0 ? name(runner) : null);
      if (pool.length > 0) return text.get(poolLine(save, runner, kind, pool, k));
      return text.fill(kind === "won" ? UI.fightWon : UI.fightLost, { runner: name(runner) });
    };
    const words = {
      won: (runner: string, k: number) => one(runner, "won", k),
      lost: (runner: string, k: number) => one(runner, "lost", k),
      since: (w: Window) => { causes.push(null); return text.fill(UI.fightSince,
        { fought: String(w.fought), won: String(w.fought - w.lost), lost: String(w.lost), runner: name(w.runner) }); },
    };
    entries(save, prev, view, words).forEach((said, i) => this.say(said, `fight:${view.at}:${i}`, "fight", causes[i] ?? null));
  }

  /** A line the page words itself, in the chronicle, and in the strip when its kind is story, taking its turn there in
   * the arrival queue. */
  private say(said: string, id: string, kind: EntryKind, cause: string | null): void {
    this.chronicle.add({ text: said, at: this.nowAt, kind, cause });
    if (!inStrip(kind)) return;
    const item = el("li", "", said);
    this.lines.append(item);
    this.ctx.arrivals.line([item], id, readingMs(said));
  }

  /** A page of the Book beside the chronicle (ui/chroniclesheet.ts, page): Screen's Done. */
  bookPage(label: string, node: HTMLElement): HTMLButtonElement {
    return this.chronicle.page(label, node);
  }

  /** The aim's line: Screen seats it above the art. */
  get aim(): HTMLElement {
    return this.aimLine.root;
  }

  tick(t: number): void {
    this.camp.tick(t);
    this.trim();
  }

  /** Each line's node in the strip, in order (null: a key with no text, or a line not for the strip). `queued`: the
   * arrival queue paces them. `away`: a return's lines, placed by game/awaylines.ts. */
  append(lines: LogLine[], queued = false, away: { view: View; prev: View | null } | null = null): Array<HTMLElement | null> {
    const where = away ? awayLines(this.ctx.catalog, lines, away.view, away.prev) : lines.map((): Placement => "band");
    return this.place(lines.map((l) => l.key), true, queued, where, lines.map((l) => l.at));
  }

  appendKeys(keys: string[], animate = true, queued = false): Array<HTMLElement | null> {
    return this.place(keys, animate, queued, keys.map((): Placement => "band"), keys.map(() => this.nowAt));
  }

  /** Lines drawn still before the first view, each at the second it landed at (a save opened, a screen redrawn). */
  restore(past: Past[]): void {
    this.place(past.map((p) => p.key), false, false, past.map((): Placement => "band"), past.map((p) => p.at));
  }

  private place(keys: string[], animate: boolean, queued: boolean, where: Placement[], ats: number[]): Array<HTMLElement | null> {
    const nodes = keys.map((key, i) => {
      const text = this.ctx.catalog.text.get(key);
      if (!text || where[i] === "none") return null;
      const at = ats[i]!;
      const kind = this.ctx.catalog.lineKind(key);
      this.chronicle.add({ text, at, kind, cause: causeWords(this.ctx.catalog, this.ctx.catalog.lineCause(key)) });
      this.keys.push({ key, at });
      if (where[i] === "chronicle" || !inStrip(kind)) return null;
      const item = el("li", animate ? "" : "still", text);
      this.lines.append(item);
      return item;
    });
    if (!queued) this.trim();   // queued lines are not held yet: the trim waits for tick()
    if (this.keys.length > KEEP) this.keys.splice(0, this.keys.length - KEEP);
    return nodes;
  }

  /** The strip shows the newest lines that have shown, as many as fit its room whole: a line that no longer fits goes
   * (the arrival queue held each back for the reading time of the one before); lines still waiting their turn stay. A
   * line that goes with no touch from the player since it showed may not have been read: the Chronicle gets its dot. */
  private trim(): void {
    const now = performance.now();
    const shown = [...this.lines.children].filter((n) => !n.classList.contains("held"));
    for (const n of shown) if (!this.shownAt.has(n) && !n.classList.contains("still")) this.shownAt.set(n, now);
    const spans = shown.map((n) => n.getBoundingClientRect());
    const keep = fitting(spans, this.roomCell.getBoundingClientRect().height);
    for (const gone of shown.slice(0, shown.length - keep)) {
      const since = this.shownAt.get(gone);
      if (since !== undefined && this.touchedAt < since && !this.chronicle.root.open) for (const b of [this.chronicleOpen, this.book]) markNew(b, () => {});
      gone.remove();
    }
  }

  /** A quiet mark on the chip a rule could answer (game/hints.ts), until it is touched: a switch's, once for the account; a
   * chip card's, once a page session. */
  private hintChips(view: View): void {
    const { catalog, keeps } = this.ctx;
    const hints = chipHints(catalog, view, keeps, this.ctx.lesson(), this.ctx.repeats().switches, this.ctx.endBehind());
    for (const [key, row] of this.chipRows) {
      if (!key.startsWith("chip:")) continue;   // the book's own dot is the journal's
      const hint = hints.find((h) => `chip:${h.chip}` === key);
      const chip = key.slice("chip:".length);
      if (hint && !this.touchedChips.has(chip)) markNew(row.node, () => { this.touchedChips.add(chip); if (hint.switch) keeps.keepSwitchOffered(hint.switch); });
      else unmark(row.node);
    }
  }

  private item(key: string): HTMLElement {
    const [kind, id = ""] = key.split(":");
    const { catalog } = this.ctx;
    if (kind === "chip") {
      const info = catalog.chips.get(id);
      const node = el("span", "chip", catalog.label(info?.label_key));
      if (info?.cost_key) node.append(el("span", "chip-cost", catalog.text.fill(info.cost_key, catalog.format.figures(info.change_bp))));
      node.dataset["tone"] = info?.tone ?? "";
      this.ctx.arrivals.arrive(node, "chip", id);
      return node;
    }
    if (kind === "journal") {   // the book once an entry is written: a button, in the place of the plain word
      this.ctx.arrivals.arrive(this.journal.button, "feature", id);
      return this.journal.button;
    }
    const node = el("span", "chip keep", catalog.label(catalog.content.feature_infos.find((f) => f.feature === id)?.label_key));
    node.dataset["keep"] = id;
    this.ctx.arrivals.arrive(node, "feature", id);
    return node;
  }
}
