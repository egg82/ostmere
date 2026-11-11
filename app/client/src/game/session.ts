// The page's side of one save the server holds: its id, the latest Step (whose `decisions` the next decision sends as
// `after`), and one request in flight at a time. A decision is sent as it is; whether it fits is the server's call. A
// request the server or the network cannot answer now (a deploy, a pod restarting) is asked again with backoff while
// the page shows it is reconnecting; another page's decision (409 stale) hands back the save as it is, drawn at once,
// and so does an answer refused because the offer was answered since (a rule may have): the page asks advance. A long
// absence comes back in slices (Step.catching_up_to): the page asks advance again at once until one reaches now, holding
// its decisions and the forecast until then, and draws the slices as one return.
import { ApiFailure, type GameApi } from "../api/api";
import type { Content, Decision, NewSave, PastLine, SavePresentation, Step, View } from "../api/types";
import { Asking } from "./asking";
import { Clock } from "./clock";
import { ForecastHold } from "./forecasthold";
import { Keeps, NEW_SAVE, type Kept } from "./keeps";
import { progressed } from "./progressed";
import { sendable, sendableSave } from "./presentation";

export interface SessionEvents {
  /** A game began or opened, or the content changed under it (a deploy: the server rebased the save). `history`: the
   * save's last lines before it opened, each with its game second ([] for a new game; null for a redraw of the same save). */
  started(content: Content, step: Step, keeps: Keeps, history: PastLine[] | null): void;
  /** A later Step: draw `step.view`, append `step.lines`. `prev` is the view it replaces. `away`: it answers the
   * player's return (an open, or the page shown again), so what it brings arrived while they were gone. */
  stepped(step: Step, prev: View, away: boolean): void;
  /** A Step names the server's build (the self-update reloads the page for a new one). */
  build(build: string): void;
  /** A decision the server refused: redraw from the view you have. */
  refused(decision: Decision | null): void;
  /** False while a request is being asked again; true once one is answered after that. */
  connected(ok: boolean): void;
  /** The account or the save is gone (no live session, or no such save): back to the front page. `fresh`: the game was
   * begun on this page and no answer has come since (the browser may not be keeping its cookie). */
  lost(fresh: boolean): void;
  /** Too many new games from here just now (Begin's 429): the front page says so, and Begin can be tried later. */
  limited(): void;
  /** A slice of the time away answered short of now: the save is at game time `at` of `to`, and more is being asked
   * for. The view in hand stays until one `stepped` brings every slice's lines at once. */
  catchingUp(at: number, to: number): void;
}

export class Session {
  readonly clock = new Clock();
  private saveId: number | null = null;
  private step: Step | null = null;
  private content: Content | null = null;
  private readonly forecast: ForecastHold;
  private keeps: Keeps;
  private queue: Promise<void> = Promise.resolve();
  private busy = 0;
  private readonly asking: Asking;
  private fresh = false;

  constructor(
    private readonly api: GameApi, private readonly events: SessionEvents, player: Partial<Kept> = {},
    wait: (ms: number) => Promise<void> = (ms) => new Promise((r) => setTimeout(r, ms)),
    nowMs: () => number = () => performance.now(),
  ) {
    this.keeps = new Keeps(player);
    this.forecast = new ForecastHold(nowMs);
    this.asking = new Asking((ok) => this.events.connected(ok), wait);
  }

  /** Resolves once every call queued so far has been answered. */
  settled(): Promise<void> {
    return this.queue;
  }

  get view(): View | null {
    return this.step?.view ?? null;
  }

  /** A new save (Begin): the account comes with it on a browser with none. `made`: one the Games sheet already made. */
  begin(made: NewSave | null = null): Promise<void> {
    return this.enqueue(() => this.newGame(made));
  }

  /** The save as the player last saw it, then the time away as a return (also switching to another save). */
  resume(saveId: number): Promise<void> {
    return this.enqueue(() => this.open(saveId));
  }

  decide(decision: Decision): Promise<void> {
    return this.enqueue(() => this.send(decision));
  }

  /** A tester's words to the server, once and outside the save's queue: whether they were kept. */
  async feedback(text: string): Promise<boolean> {
    try {
      await this.api.sendFeedback(text, this.saveId);
      return true;
    } catch (e) {
      console.warn("ashfall: feedback not sent", e instanceof ApiFailure ? e.code : "network");
      return false;
    }
  }

  /** Called every frame: ask the server again once the clock passes next_event_at. */
  tick(): void {
    const view = this.view;
    if (!view || this.busy > 0) return;
    if (this.clock.due(view)) void this.advance();
    else if (this.forecastDue()) void this.enqueue(() => this.askForecast());
  }

  /** A plain advance: when the clock passes next_event_at, or on the page being shown again (`away`). */
  advance(away = false): Promise<void> {
    return this.enqueue(() => this.send(null, away));
  }

  /** The view the save would show after these decisions, without keeping it: the mix editor's "after" totals. Null
   * when there is no game or the server refuses one of them (the editor then shows no after column). */
  async dryRun(decisions: Decision[]): Promise<View | null> {
    if (this.saveId === null || decisions.length === 0) return null;
    try {
      return await this.api.dryRun(this.saveId, decisions);
    } catch {
      return null;
    }
  }

  private enqueue(job: () => Promise<void>): Promise<void> {
    this.busy += 1;
    const run = this.queue.then(job).finally(() => { this.busy -= 1; });
    this.queue = run.catch(() => undefined);
    return run;
  }

  private async newGame(given: NewSave | null): Promise<void> {
    this.fresh = true;
    try {
      const early = this.contentAlongside();
      const made = given ?? await this.asking.answered(() => this.api.begin());
      this.begun(await this.contentFor(made.step, early), made.step, made.save.save_id, [], made.presentation ?? NEW_SAVE);
    } catch (e) {
      this.failed(e, null);
    }
  }

  private async open(saveId: number): Promise<void> {
    try {
      const early = this.contentAlongside();
      const opened = await this.asking.answered(() => this.api.open(saveId));
      const content = await this.contentFor(opened.step, early);
      const was: Step = { ...opened.step, view: opened.was, lines: [], failed_tap: null, catching_up_to: null };
      this.begun(content, was, saveId, opened.history, opened.presentation ?? NEW_SAVE);   // an older pod answers none: none kept, never the last save's
      await this.took(await this.caughtUp(opened.step, saveId), opened.was, true);
    } catch (e) {
      this.failed(e, null);
    }
  }

  /** `first`, or, while it stops short of now, the Step advance answers once one reaches it, with every slice's lines
   * in order (each slice's (at, seq) follow the last's). */
  private async caughtUp(first: Step, id: number): Promise<Step> {
    let next = first;
    const lines = [...first.lines];
    while (next.catching_up_to !== null) {
      this.events.catchingUp(next.view.at, next.catching_up_to);
      next = await this.asking.answered(() => this.api.advance(id));
      lines.push(...next.lines);
    }
    return next === first ? first : { ...next, lines };
  }

  /** The content asked for while the save's own call is out: one try, null when the page holds it already or it failed
   * (`contentFor` then asks as usual). Always settled, so a save call that fails first leaves nothing unhandled. */
  private contentAlongside(): Promise<Content | null> {
    if (this.content !== null) return Promise.resolve(null);
    return this.api.content().catch(() => null);
  }

  /** The content for the rules `step` was made under: the one held, or the one asked for alongside when its digest
   * matches (a deploy between the two calls changes it), or asked for now. */
  private async contentFor(step: Step, early: Promise<Content | null> = Promise.resolve(null)): Promise<Content> {
    if (this.content?.rules_digest === step.rules_digest) return this.content;
    const got = await early;
    if (got?.rules_digest === step.rules_digest) return got;
    return this.asking.answered(() => this.api.content());
  }

  /** The forecast, asked for by its own call (CONTRACT.txt, "Forecast"), drawn at once on the view the page holds. */
  private async askForecast(): Promise<void> {
    const id = this.saveId;
    if (id === null || !this.forecastDue()) return;
    this.forecast.asked();
    try {
      const got = await this.api.forecast(id);
      this.forecast.got(got.forecast, got.decisions, this.clock.now());
      const held = this.step;
      if (!held) return;
      const next = this.forecast.withForecast({ ...held, lines: [], failed_tap: null });   // the same view, now with the times; the clock runs on
      this.step = next;
      this.events.stepped(next, held.view, false);
    } catch (e) {
      if (e instanceof ApiFailure && e.code === "no_account") {
        this.events.lost(this.fresh);
        return;
      }
      if (e instanceof ApiFailure && e.code === "catching_up") {
        await this.send(null);   // the forecast wrote nothing: the save is behind, so catch it up
        return;
      }
      console.warn("ashfall: no forecast", e instanceof Error ? e.message : e);   // times wait for the next ask
    }
  }

  private forecastDue(): boolean {
    return this.forecast.due(this.step, () => this.clock.now());
  }

  /** `kept`: what the save keeps about its teaching, as answered; null for a redraw of the same save (its copy stays). */
  private begun(content: Content, step0: Step, saveId: number, history: PastLine[] | null, kept: SavePresentation | null): void {
    if (saveId !== this.saveId) this.forecast.drop();   // another save's future
    const step = this.forecast.withForecast(step0);
    this.content = content;
    this.saveId = saveId;
    this.step = step;
    this.keeps = this.keepsFor(saveId, kept);
    this.events.build(step.build);
    this.clock.start(step.view.at);
    this.events.started(content, step, this.keeps, history);
    progressed(content, step.view);
  }

  /** The keeps for save `saveId`: the account's and the settings carried on; each change sent, the answer adopted. */
  private keepsFor(saveId: number, kept: SavePresentation | null): Keeps {
    const notKept = (e: unknown): void => console.warn("ashfall: not kept", e);
    const was = this.keeps.kept;
    const keeps: Keeps = new Keeps({ ...was, save: kept ?? was.save }, {
      account: (p) => void this.api.putMePresentation(sendable(p)).then((a) => keeps.adopt(a.presentation)).catch(notKept),
      save: (p) => void this.api.putSavePresentation(saveId, sendableSave(p)).then((s) => keeps.adoptSave(s)).catch(notKept),
      settings: (s) => void this.api.putMeSettings(s).then((a) => keeps.adoptSettings(a.settings)).catch(notKept),
    });
    return keeps;
  }

  private async send(decision: Decision | null, away = false): Promise<void> {
    const held = this.step;
    const id = this.saveId;
    if (!held || id === null) return;
    try {
      if (decision !== null) this.forecast.decided();
      const next = await this.asking.answered(() => (decision === null ? this.api.advance(id) : this.api.decide(id, decision, held.decisions)));
      await this.took(await this.caughtUp(next, id), held.view, away);
    } catch (e) {
      await this.refusedWith(e, decision, held.view, id).catch((e2: unknown) => { this.failed(e2, decision); });
    }
  }

  /** A refusal the page carries on from: another page's decision (stale) or time still to catch up (catching_up) hands
   * back the save as it is, drawn once caught up, and a decision held back by catching up is then sent; an answer
   * refused because the offer was answered since asks advance. Anything else fails. */
  private async refusedWith(e: unknown, decision: Decision | null, prev: View, id: number): Promise<void> {
    if (e instanceof ApiFailure && (e.code === "stale" || e.code === "catching_up") && e.step) {
      await this.took(await this.caughtUp(e.step, id), prev, false);
      if (e.code === "catching_up" && decision !== null) await this.send(decision);
      return;
    }
    if (e instanceof ApiFailure && e.code === "invalid_decision" && decision?.kind === "answer_offer") {
      await this.send(null);   // answered since the page's last view (a rule may have): draw the save as it is
      return;
    }
    this.failed(e, decision);
  }

  /** A Step answered: a new digest means a deploy (fetch the content and redraw), else it lands. */
  private async took(next: Step, prev: View, away: boolean): Promise<void> {
    if (this.content && next.rules_digest !== this.content.rules_digest && this.saveId !== null) {
      this.content = null;
      this.forecast.drop();   // made under other rules
      this.begun(await this.contentFor(next), next, this.saveId, null, null);
      return;
    }
    this.landed(next, prev, away);
  }

  private landed(next0: Step, prev: View, away: boolean): void {
    const next = this.forecast.withForecast(next0);
    this.fresh = false;
    this.step = next;
    this.events.build(next.build);
    this.clock.start(next.view.at);
    if (away) this.keeps.keepReturn(prev.at, next.view.at);
    this.events.stepped(next, prev, away);
    if (this.content) progressed(this.content, next.view);
  }

  private failed(e: unknown, decision: Decision | null): void {
    const code = e instanceof ApiFailure ? e.code : "network";
    console.error("ashfall: request failed", code, e instanceof Error ? e.message : e);
    if (code === "no_account" || code === "not_found") {
      this.events.lost(this.fresh);
      return;
    }
    if (code === "rate_limited" && decision === null) {   // Begin's; a decision past its save's limit is refused and redrawn
      this.events.limited();
      return;
    }
    this.events.refused(decision);
  }
}
