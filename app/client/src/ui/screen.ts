// The game screen (docs/design/opening-screen.md): the scene with the story strip under it, and the panel beside
// it (under it on a phone): the hands strip and a row per lane run by rules, Tasks · Completed · Rules, the skills and the ledger (the Rules tab shows once
// the first rule exists; the Mixes list opens from the strip). On a big desktop window the skills and ledger sit under the
// scene, so neither column has dead space. The mix editor takes the card area's place while open. It owns no game state:
// it draws each View it is handed and samples it every frame. The one glow on a card is placed here (CardInfo.glows, the
// first time it is ready with its lane free); the strip places its offers' glows, the Rules tab's label takes it once a
// rule has come on and let go until the tab is opened, and a running lesson's step takes it (lessons.ts).
import type { Condition, Decision, Step, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { nudgeTarget } from "../game/cues";
import { NewMarks } from "../game/marks";
import type { Keeps } from "../game/keeps";
import type { Past } from "../game/loggroups";
import { mixRules, ruleLetGo, ruleRunLetGo, rulesTabDrawn, taskRules } from "../game/orders";
import { readingMs } from "../game/reading";
import { HandStreak } from "../game/stall";
import { UI } from "../game/text";
import { Banner } from "./banner";
import { CardGlow } from "./cardglow";
import { Cards } from "./cards";
import { Completed } from "./completed";
import { el, revealBelow } from "./dom";
import { MixEditor } from "./editor";
import { TheEnd } from "./end";
import { FeatureCard } from "./featurecard";
import { OrderFires } from "./fires";
import { Flight } from "./flight";
import { Glow, GlowWhile, markNew } from "./fresh";
import { IdleNudge } from "./nudge";
import { Lessons } from "./lessons";
import { Hands } from "./hands";
import { seatHead } from "./headseat";
import { LOW_UNDER_SCENE } from "./layout";
import { Ledger } from "./ledger";
import type { Actions, Part, RuleTarget } from "./part";
import type { Moment } from "./remindermention";
import { Reveal } from "./reveal";
import { RulesTab } from "./rules";
import { MixSelector } from "./selector";
import { Skills } from "./skills";
import { Story } from "./story";
import { MoreCue } from "./morecue";
import { showTabs, wireTabs, type Tab } from "./tabs";

export class Screen {
  readonly root = el("div", "game");
  readonly sceneBox = el("div", "scene-box");
  readonly sceneCanvas = el("canvas", "scene-art");
  /** The panel's last row: quiet text buttons (Feedback, and others that sit beside it). */
  readonly foot = el("div", "panel-foot");
  private readonly left = el("div", "left");
  private readonly low = el("div", "low");
  private readonly state: HTMLElement[];
  private readonly panel: HTMLElement;
  private readonly fires = new OrderFires();
  private readonly reveal = new Reveal();
  private readonly glow = new Glow(this.reveal);   // the reveal first: the glow waits its turn there
  private readonly nudge = new IdleNudge(this.glow, () => {
    const card = this.view ? nudgeTarget(this.catalog, this.view) : null;
    return (card && this.cards.node(card)) || null;
  });
  private readonly streak = new HandStreak();
  private readonly parts: Part[];
  private readonly story: Story;
  private readonly cards: Cards;
  private readonly completed: Completed;
  private readonly ledger: Ledger;
  private readonly hands: Hands;
  private readonly flight = new Flight(this.reveal);
  private lineIds = 0;
  private drawing = false;
  private readonly editor: MixEditor;
  private readonly selector: MixSelector;
  private readonly banner: Banner;
  private readonly end: TheEnd;
  private readonly tabCards = el("button", "tab");
  private readonly tabCompleted = el("button", "tab");
  private readonly tabRules = el("button", "tab");
  private readonly tabs = el("div", "tabs");
  /** The hands strip's band, pinned under the scene on a phone. */
  private readonly pinned = el("div", "panel-top");
  private readonly rules: RulesTab;
  private readonly rulesGlow: GlowWhile;
  /** The Rules tab has been shown this page session: it stays, even with every rule removed. */
  private rulesShown = false;
  private view: View | null = null;
  private latest: Pick<Step, "repeats" | "rule_runs" | "lines" | "save_id"> = { repeats: { taps: [], switches: [] }, rule_runs: [], lines: [], save_id: 0 };
  private lessons: Lessons | null = null;
  private tab: Tab = "cards";
  private readonly cardGlow: CardGlow;

  constructor(
    private readonly catalog: Catalog, decide: (decision: Decision) => void,
    dryRun: (decisions: Decision[]) => Promise<View | null>, private readonly keeps: Keeps,
    sendFeedback: (text: string) => Promise<boolean> = () => Promise.resolve(false),
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
      editMix: (id) => this.openEditor(id),
      newMix: (rule) => this.openEditor(null, true, rule),
      openSelector: () => { if (this.view) this.selector.show(this.view); },
      openRules: (rule, offered) => this.openRules(rule, offered),
      orderSent: (card) => this.flight.launch(card),
      highlight: (cards) => this.ledger.highlight(cards),
      sendFeedback,
    };
    const ctx = {
      catalog, actions, fires: this.fires, glow: this.glow, streak: this.streak, arrivals: this.reveal,
      endBehind: () => this.end.behind, keeps, repeats: () => this.latest.repeats, ruleRuns: () => this.latest.rule_runs,
      lines: () => this.latest.lines, saveId: () => this.latest.save_id, lesson: () => this.lessons?.holding ?? null, lessonSubject: () => this.lessons?.subject ?? null,
    };
    this.story = new Story(ctx);
    const marks = new NewMarks();
    this.cardGlow = new CardGlow(catalog, this.glow, (card) => this.cards.node(card));
    this.cards = new Cards(ctx, marks, () => { if (this.tab !== "cards" || this.editor.open) markNew(this.tabCards, () => undefined); });
    this.completed = new Completed(ctx);
    this.ledger = new Ledger(ctx);
    this.editor = new MixEditor(ctx, () => this.showTab(), marks);
    this.selector = new MixSelector(ctx);
    this.banner = new Banner(catalog, this.reveal);
    this.end = new TheEnd(catalog, (keys) => this.endLines(keys), () => this.redraw());
    this.hands = new Hands(ctx, () => this.showTab());
    const skills = new Skills(ctx);
    this.rules = new RulesTab(ctx);
    this.rulesGlow = new GlowWhile(this.glow, this.tabRules);
    const area = el("div", "card-area");
    area.append(this.cards.root, this.completed.root, this.rules.root, this.editor.root, this.hands.lanes.town.root);
    this.pinned.append(this.hands.root);
    const panel = el("section", "panel");
    this.foot.append(this.story.feedbackButton);
    panel.append(this.banner.root, this.pinned, this.hands.rows, this.hands.lanes.root, this.ledger.asks, this.tabs, area, this.foot);   // the offer rows (a phone's) and the lane rows under the strip, unpinned; then a phone's red and full ledger lines
    this.parts = [this.story, this.hands, this.cards, this.completed, this.rules, skills, this.ledger,
      new FeatureCard(catalog, this.reveal, this.root), new MoreCue(panel, area), (this.lessons = new Lessons(ctx, this.root, () => this.redraw()))];

    const frame = el("div", "scene-frame");
    this.sceneCanvas.setAttribute("aria-hidden", "true");
    frame.append(this.sceneCanvas);
    this.sceneBox.append(frame);
    const stage = el("section", "stage");
    stage.append(this.sceneBox);
    this.left.append(stage, this.low);
    seatHead(this.root, stage, this.story.head, this.story.aim, this.story.root);

    wireTabs(catalog, [[this.tabCards, UI.tabCards, "cards"], [this.tabCompleted, UI.tabCompleted, "completed"], [this.tabRules, UI.ordersHeading, "rules"]], (tab) => {
      if (tab === "rules") { this.openRules(null); return; }
      this.tab = tab;
      this.showTab();
    });
    this.tabRules.style.visibility = "hidden";
    this.tabs.append(this.tabCards, this.tabCompleted, this.tabRules);
    this.state = [this.ledger.root, skills.root];   // on a phone the ledger comes first, nearest the cards
    this.low.hidden = true;
    this.panel = panel;
    this.root.append(this.left, panel, this.selector.root);
    const wide = window.matchMedia(LOW_UNDER_SCENE);
    const place = (): void => { if (wide.matches) this.low.append(...this.state); else this.foot.before(...this.state); this.ledger.setSplit(!wide.matches); };
    wide.addEventListener("change", place);
    place();
    this.showTab();
  }

  /** The story's last lines, drawn at once before the first view (a save opened, or a screen redrawn for a deploy). */
  restore(past: Past[]): void {
    this.story.restore(past);
  }

  /** The story's lines, oldest first: what a screen redrawn for a deploy restores. */
  get storyPast(): Past[] {
    return [...this.story.keys];
  }

  /** `away`: the first view after the player was away, whose new things are revealed in turn. A step's lines, live or
   * on a return, are revealed first, each held for its reading time before what came with it. */
  show(step: Step, away = false): void {
    const first = this.view === null;
    this.latest = step;
    const lines = step.lines;
    const lead = lines.length > 0;   // live, first or on a return alike: each line in turn, a planned moment in full
    if ((away && !first) || lead) this.reveal.collect();
    if (away && !first) this.root.scrollTop = 0;   // a return opens at the top: no card row under the pinned strip
    const nodes = this.story.append(lines, lead, away && !first ? { view: step.view, prev: this.view } : null);
    if (lead) this.lead(nodes);
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
      this.reveal.line([shown], String(this.lineIds), readingMs(shown.textContent ?? ""));
    });
    if (!this.drawing) this.reveal.start(performance.now());
  }

  /** Each line first in the queue, in the strip, held for its reading time. */
  private lead(nodes: Array<HTMLElement | null>): void {
    for (const shown of nodes) {
      if (!shown?.isConnected) continue;   // not for the strip (a return's chip or task line: game/awaylines.ts)
      this.lineIds += 1;   // (at, seq) is unique only within one Step
      this.reveal.line([shown], String(this.lineIds), readingMs(shown.textContent ?? ""));
    }
  }

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
    this.tabRules.style.visibility = this.rulesShown ? "" : "hidden";   // its room is kept: nothing moves
    this.rulesGlow.update(rules > 0 && this.keeps.ruleSeen() && !this.keeps.rulesOpened());
    if (prev && (view.orders.length > prev.orders.length || view.queue.length > prev.queue.length)) this.flight.landed(this.tabRules, this.tab === "rules");
    this.tabCompleted.style.visibility = view.completed.length > 0 ? "" : "hidden";   // its room is kept: nothing moves
    this.low.hidden = this.state.every((part) => part.hidden);   // nothing under the strip until the ledger or a skill has something to show
    this.cardGlow.place(view);
  }

  /** The Rules tab, on rule `rule`'s editor when given (the shortcuts from the strip and the ledger). */
  private openRules(rule: RuleTarget, offered?: Condition): void {
    const view = this.view;
    if (!view) return;
    if (this.editor.open) this.editor.close();
    this.keeps.keepRulesOpened();
    this.rulesGlow.used();
    this.rulesShown = true;
    this.tabRules.style.visibility = "";
    this.tab = "rules";
    this.rules.open(view, rule, offered);
    this.showTab();
    revealBelow(this.tabs, this.pinned, [this.root, this.panel]);
  }

  private openEditor(mixId: string | null, fresh = false, forRule: number | null = null): void {
    if (!this.view) return;
    if (fresh) this.editor.showNew(this.view, forRule);
    else this.editor.show(this.view, mixId);
    this.hands.editorOpened();
    this.showTab();
  }

  private showTab(): void {
    const editing = this.editor.open || this.hands.lanes.town.open;
    this.root.classList.toggle("editing", editing);
    this.tabs.style.visibility = editing ? "hidden" : "";
    showTabs(this.tab, editing, [[this.tabCards, this.cards.root, "cards"], [this.tabCompleted, this.completed.root, "completed"], [this.tabRules, this.rules.root, "rules"]]);
  }
}
