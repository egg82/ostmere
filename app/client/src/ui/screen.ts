// The game screen (docs/design/opening-screen/index.md): on a desktop the left rail, the scene with the story strip under it,
// and the panel beside it (under it on a phone): the hands strip, the asks, then the open tab's panel, Tasks, Town
// (ui/townview.ts) or Rules once the first rule exists (ui/tabs.ts; each part's seat by frame: ui/partseat.ts). The mix
// and town editors take the card area's place while open. It owns no game state: it draws each View it is handed and
// samples it every frame. The one glow on a card is placed here (CardInfo.glows, the first time it is ready with its lane
// free); the strip places its offers' glows, the Rules tab's label takes it once a rule has come on and let go until the
// tab is opened, and a running lesson's step takes it (lessons.ts).
import type { Decision, JournalDay, MixRows, Step, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { NewMarks } from "../game/marks";
import type { Keeps } from "../game/keeps";
import type { Past } from "../game/chronicle";
import { mixRules, ruleLetGo, ruleRunLetGo, rulesTabDrawn, taskRules } from "../game/orders";
import { readingMs } from "../game/reading";
import { HandStreak } from "../game/stall";
import { Banner } from "./banner";
import { CardGlow } from "./cardglow";
import { Cards } from "./cards";
import { bookPages } from "./bookpages";
import { el } from "./dom";
import { MixEditor } from "./editor";
import { TheEnd } from "./end";
import { FeatureCard } from "./featurecard";
import { OrderFires } from "./fires";
import { Flight } from "./flight";
import { Glow, GlowWhile, markNew } from "./fresh";
import { IdleNudge, nudgeNode } from "./nudge";
import { Lessons } from "./lessons";
import { Hands } from "./hands";
import { Asks } from "./asks";
import { seatHead } from "./headseat";
import { PHONE } from "./layout";
import { seatParts } from "./partseat";
import { Ledger } from "./ledger";
import type { Actions, Part } from "./part";
import type { Moment } from "./remindermention";
import { Reveal } from "./reveal";
import { RulesTab } from "./rules";
import { MixSelector } from "./selector";
import { Skills } from "./skills";
import { Story } from "./story";
import { StripGlow } from "./stripglow";
import { MoreCue } from "./morecue";
import { PanelNav } from "./panelnav";
import { PanelTabs } from "./tabs";
import { TownView } from "./townview";

export class Screen {
  readonly root = el("div", "game");
  readonly sceneBox = el("div", "scene-box");
  readonly sceneCanvas = el("canvas", "scene-art");
  /** The panel's last row: quiet text buttons (Feedback, and others that sit beside it). */
  readonly foot = el("div", "panel-foot");
  private readonly left = el("div", "left");
  private readonly low = el("div", "low");
  private readonly rail = el("aside", "rail");
  private readonly area = el("div", "card-area");
  private readonly panel: HTMLElement;
  private readonly fires = new OrderFires();
  private readonly reveal = new Reveal();
  private readonly glow = new Glow(this.reveal);   // the reveal first: the glow waits its turn there
  private readonly nudge = new IdleNudge(this.glow, () => this.view && nudgeNode(this.catalog, this.view, (c) => this.cards.node(c)));
  private readonly streak = new HandStreak();
  private readonly parts: Part[];
  private readonly story: Story;
  private readonly cards: Cards;
  private readonly bookPages: Part[];
  private readonly skills: Skills;
  private readonly town: TownView;
  private readonly ledger: Ledger;
  private readonly hands: Hands;
  private readonly asks: Asks;
  private readonly flight = new Flight(this.reveal);
  private lineIds = 0;
  private readonly stripGlow: StripGlow;
  private drawing = false;
  private readonly editor: MixEditor;
  private readonly selector: MixSelector;
  private readonly banner: Banner;
  private readonly end: TheEnd;
  private readonly tabs: PanelTabs;
  /** The hands strip's band, pinned under the scene on a phone. */
  private readonly pinned = el("div", "panel-top");
  private readonly rules: RulesTab;
  private readonly rulesGlow: GlowWhile;
  /** The Rules tab has been shown this page session: it stays, even with every rule removed. */
  private rulesShown = false;
  private readonly nav: PanelNav;
  private view: View | null = null;
  private latest: Pick<Step, "repeats" | "rule_runs" | "lines" | "save_id"> = { repeats: { taps: [], switches: [] }, rule_runs: [], lines: [], save_id: 0 };
  private lessons: Lessons | null = null;
  private readonly cardGlow: CardGlow;

  constructor(
    private readonly catalog: Catalog, decide: (decision: Decision) => void,
    dryRun: (decisions: Decision[]) => Promise<View | null>, private readonly keeps: Keeps,
    sendFeedback: (text: string) => Promise<boolean> = () => Promise.resolve(false),
    mixRows: () => Promise<MixRows | null> = () => Promise.resolve(null),
  ) {
    const actions: Actions = {
      decide: (d) => {
        if (d.kind === "tap_card") {
          this.fires.tap(d.card);
          this.streak.tap(d.card);
        }
        decide(d);
      },
      dryRun,
      mixRows,
      editMix: (id) => this.nav.openEditor(id),
      newMix: (rule) => this.nav.openEditor(null, true, rule),
      openSelector: () => { if (this.view) this.selector.show(this.view); },
      openRules: (rule, offered) => this.nav.openRules(rule, offered),
      orderSent: (card) => this.flight.launch(card),
      highlight: (cards) => this.ledger.highlight(cards),
      sendFeedback,
    };
    const ctx = {
      catalog, actions, fires: this.fires, glow: this.glow, streak: this.streak, arrivals: this.reveal,
      endBehind: () => this.end.behind, keeps, repeats: () => this.latest.repeats, ruleRuns: () => this.latest.rule_runs,
      lines: () => this.latest.lines, saveId: () => this.latest.save_id, lesson: () => this.lessons?.holding ?? null, lessonSubject: () => this.lessons?.subject ?? null,
    };
    this.story = new Story(ctx, () => this.asks.show(), () => this.nav.pick("cards"));
    this.stripGlow = new StripGlow(this.story.root);
    this.tabs = new PanelTabs(catalog, this.story.book.tab, (tab) => this.nav.pick(tab));
    const marks = new NewMarks();
    this.cardGlow = new CardGlow(catalog, this.glow, (card) => this.cards.node(card));
    this.cards = new Cards(ctx, marks, () => { if (this.tabs.on !== "cards" || this.editor.open) markNew(this.tabs.cards, () => undefined); });
    this.bookPages = bookPages(ctx, this.story.book);
    this.ledger = new Ledger(ctx);
    this.editor = new MixEditor(ctx, () => this.nav.showTab(), marks);
    this.selector = new MixSelector(ctx);
    this.banner = new Banner(catalog, this.reveal);
    this.end = new TheEnd(catalog, (keys) => this.endLines(keys), () => this.redraw());
    this.hands = new Hands(ctx, () => this.nav.showTab());
    this.asks = new Asks(ctx);
    this.skills = new Skills(ctx);
    this.rules = new RulesTab(ctx, undefined, () => this.nav.returnToOpener());
    this.rulesGlow = new GlowWhile(this.glow, this.tabs.rules);
    this.town = new TownView(catalog, this.hands.lanes, this.tabs.town);
    this.area.append(this.cards.root, this.town.root, this.rules.root, this.story.book.view, this.editor.root, this.hands.lanes.page.root);
    this.pinned.append(this.hands.root);
    const panel = el("section", "panel");
    this.foot.append(this.story.feedbackButton);
    panel.append(this.banner.root, this.pinned, this.hands.rows, this.ledger.asks, this.asks.root, this.area);   // under the strip, unpinned: a phone's mix controls, then the red and full ledger lines beside the mix that feeds them, then the asks
    this.parts = [this.story, this.hands, this.asks, this.cards, ...this.bookPages, this.rules, this.skills, this.ledger,
      new FeatureCard(catalog, this.reveal, this.root), new MoreCue(panel, this.area), (this.lessons = new Lessons(ctx, this.root, () => this.redraw()))];

    const frame = el("div", "scene-frame");
    this.sceneCanvas.setAttribute("aria-hidden", "true");
    frame.append(this.sceneCanvas);
    this.sceneBox.append(frame);
    const stage = el("section", "stage");
    stage.append(this.sceneBox);
    this.left.append(stage, this.low);
    seatHead(this.root, stage, this.story.head, this.story.aim, this.story.root);

    this.low.hidden = true;
    this.panel = panel;
    this.root.append(this.rail, this.left, panel, this.selector.root);
    seatParts({ tabs: this.tabs.root, ledger: this.ledger.root, skills: this.skills.root, foot: this.foot, book: this.story.book },
      { low: this.low, rail: this.rail, panel, area: this.area, town: this.town.root }, (wide) => this.ledger.setSplit(!wide));
    this.nav = new PanelNav({
      tabs: this.tabs, rules: this.rules, editor: this.editor, hands: this.hands, book: this.story.book, keeps, rulesGlow: this.rulesGlow,
      panels: { cards: this.cards.root, town: this.town.root }, root: this.root, panel, area: this.area, pinned: this.pinned,
      view: () => this.view, rulesShown: () => { this.rulesShown = true; },
    });
    this.nav.showTab();
  }

  /** The story's last lines and written days, drawn at once before the first view (a save opened, a screen redrawn). */
  restore(past: Past[], days: readonly JournalDay[] = []): void {
    this.story.restore(past, days);
  }

  /** What a screen redrawn for a deploy restores (Story.carried). */
  get carried(): { past: Past[]; days: JournalDay[] } {
    return this.story.carried;
  }

  /** `away`: the first view after the player was away, whose new things are revealed in turn. A step's lines, live or
   * on a return, are revealed first, each held for its reading time before what came with it. */
  show(step: Step, away = false): void {
    const first = this.view === null;
    this.latest = step;
    const lines = step.lines;
    const lead = lines.length > 0;   // live, first or on a return alike: each line in turn, a planned moment in full
    if ((away && !first) || lead) this.reveal.collect();
    else if (first) this.reveal.hush();   // the page's first draw is silent
    else this.reveal.cascade();   // a live step's consequences light link by link
    if (away && !first) this.root.scrollTop = 0;   // a return opens at the top: no card row under the pinned strip
    const nodes = this.story.append(lines, lead, away && !first ? { view: step.view, prev: this.view } : null);
    this.story.written(step.journal_days);
    if (lead) this.stripGlow.lead(this.reveal, nodes, away && !first, () => String(++this.lineIds), lines.map((l) => l.opens_beat));
    this.drawing = true;   // the end's lines join this batch rather than start one
    this.end.update(step.view, first);   // first, so the parts drawn next know whether the end is behind
    try {
      this.draw(step.view);
      if (!first && step.failed_tap !== null) this.cards.failed(step.failed_tap, step.view);
    } finally {
      this.drawing = false;
      this.reveal.start(performance.now());
    }
  }

  /** The end's lines (live or replayed on a return): strip only, each taking its turn in the queue like any line. */
  private endLines(keys: string[]): void {
    this.reveal.collect();
    this.story.appendKeys(keys, true, true).forEach((shown) => {
      if (!shown) return;
      this.lineIds += 1;
      this.reveal.line([shown], String(this.lineIds), readingMs(shown.textContent ?? ""), "end");   // one strike per batch: the first of these
    });
    if (!this.drawing) this.reveal.start(performance.now());
  }

  get endShowing(): boolean { return this.end.showing; }   // TheEnd.showing
  /** Something is still waiting its turn or a line is being read: not a moment to reload the page. */
  get revealing(): boolean {
    return this.reveal.busy;
  }

  /** What the reminders mention waits on: the end read, and nothing holding the glow or still being revealed. */
  get moment(): Moment {
    return { endRead: this.end.behind, busy: this.glow.busy || this.reveal.busy };
  }

  tick(t: number): void {
    this.reveal.tick(performance.now());
    this.stripGlow.tick(performance.now(), this.reveal.busy);
    this.rulesGlow.tick();
    this.nudge.tick();
    for (const part of this.parts) part.tick(t);
  }

  /** Put back what a refused decision changed on screen (a dragged share): redraw the view as it stands. */
  redraw(): void {
    if (this.view) this.draw(this.view);
  }

  private draw(view: View): void {
    const prev = this.view;
    this.view = view;
    if ((prev && ruleLetGo(prev, view)) || ruleRunLetGo(this.latest.rule_runs)) this.keeps.keepRuleSeen();
    this.fires.observe(view, prev);
    for (const part of this.parts) part.update(view, prev);
    this.banner.update(view, prev);
    this.editor.update(view);
    this.selector.update(view);
    const rules = mixRules(view).length + taskRules(view).length;
    this.rulesShown ||= rulesTabDrawn(view, this.keeps.ruleSeen());   // Next lives there too
    this.tabs.rules.style.visibility = this.rulesShown ? "" : "hidden";   // its room is kept: nothing moves
    this.rulesGlow.update(rules > 0 && this.keeps.ruleSeen() && !this.keeps.rulesOpened());
    if (prev && (view.orders.length > prev.orders.length || view.queue.length > prev.queue.length)) this.flight.landed(this.tabs.rules, this.tabs.on === "rules");
    this.low.hidden = this.ledger.root.hidden;   // nothing under the strip until the ledger has something to show
    const more = window.matchMedia(PHONE).matches && !(this.ledger.root.hidden && this.skills.root.hidden);
    if (!this.town.draw(view, more, prev !== null && this.tabs.on !== "town") && this.tabs.on === "town") this.nav.pick("cards");
    this.cardGlow.place(view);
  }
}
