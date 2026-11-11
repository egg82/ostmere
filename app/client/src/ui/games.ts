// Games (CONTRACT.txt, "Games on one account"): a quiet text button at the panel's foot opening a sheet that lists the
// account's games, asked for afresh each time it opens. The game this page plays is marked; each other has Open and
// Delete, which asks once more before the game goes. New game starts another beside them, and the deleted games still
// held come last, each with Restore. What a tap does to the page (switch, a new game) is the caller's (GamesActions).
import { ApiFailure, type GameApi } from "../api/api";
import type { DeletedSave, Games, NewSave, SaveInfo } from "../api/types";
import type { Straight } from "../app/straight";
import { dateOf } from "../game/format";
import { DELETE_WORDS, START_OVER_WORDS, deleteParts, startOver } from "./gamedelete";
import { UI, type Text } from "../game/text";
import { noteGame } from "../telemetry";
import { el } from "./dom";
import { checkChoice, straightChoice, type StraightChoice } from "./straightchoice";

export interface GamesActions {
  /** The save this page plays now. */
  playing(): number | null;
  /** Play another of the account's saves. */
  open(saveId: number): void;
  /** Play a save just made by New game. */
  begun(made: NewSave): void;
  /** This device's choice to open straight into a game, shown as a checkbox. */
  straight: Straight;
  /** The account's choice to skip lessons in every game, shown as a checkbox (checked: lessons off). */
  skipLessons: Straight;
}

export class GamesSheet {
  readonly button = el("button", "games-open");
  readonly root = el("dialog", "sheet games-sheet");
  private readonly list = el("ul", "games-list");
  private readonly held = el("section", "games-held");
  private readonly note = el("p", "games-note");
  private readonly make = el("button", "primary");
  private readonly straight: StraightChoice;
  private readonly skipLessons: StraightChoice;
  private games: Games | null = null;
  private asking: number | null = null;   // the game whose Delete asks once more
  private busy = false;

  constructor(private readonly api: GameApi, private readonly text: Text, private readonly actions: GamesActions) {
    this.button.type = "button";
    this.button.textContent = text.get(UI.gamesOpen);
    this.button.addEventListener("click", () => this.open());
    this.note.setAttribute("role", "status");
    this.make.type = "button";
    this.make.textContent = text.get(UI.gameNew);
    this.make.addEventListener("click", () => void this.begin());
    this.straight = straightChoice(text, actions.straight, "games-choice", "games-straight");
    this.skipLessons = checkChoice(text.get(UI.gameSkipLessons), actions.skipLessons, "games-choice", "games-lessons");
    const close = el("button", "quiet", text.get(UI.close));
    close.type = "button";
    close.addEventListener("click", () => this.root.close());
    const foot = el("div", "sheet-actions");
    foot.append(close, this.make);
    this.root.append(el("h2", "panel-heading", text.get(UI.gamesHeading)), this.list, this.note, this.held, this.straight.root,
      this.skipLessons.root, foot);
    this.root.addEventListener("click", (e) => { if (e.target === this.root) this.root.close(); });
  }

  open(): void {
    this.asking = null;
    this.note.textContent = "";
    this.straight.show();
    this.skipLessons.show();
    if (!this.root.open) this.root.showModal();
    void this.run(() => this.api.games());
  }

  /** Asks the server, and draws the list it answers; a refusal is one line, and the list is asked for again. */
  private async run(ask: () => Promise<Games>): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    this.sync();
    try {
      this.games = await ask();
      this.asking = null;
      this.note.textContent = "";
    } catch (e) {
      this.note.textContent = this.refusal(e);
      if (e instanceof ApiFailure && e.code !== "network") this.games = await this.api.games().catch(() => this.games);
    } finally {
      this.busy = false;
      this.draw();
    }
  }

  private async begin(): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    this.sync();
    try {
      const made = await this.api.begin();
      this.root.close();
      this.actions.begun(made);
    } catch (e) {
      this.note.textContent = this.refusal(e);
    } finally {
      this.busy = false;
      this.sync();
    }
  }

  /** Start over (gamedelete.ts), then switch to the new game as New game does; a refusal is the note's line. */
  private async startOver(oldId: number): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    this.asking = null;
    this.sync();
    try {
      const made = await startOver(this.api, oldId);
      this.root.close();
      this.actions.begun(made);
    } catch (e) {
      this.note.textContent = this.refusal(e);
    } finally {
      this.busy = false;
      this.draw();
    }
  }

  private refusal(e: unknown): string {
    return gameRefusal(this.text, e, this.games?.max_saves ?? null);
  }

  private draw(): void {
    const g = this.games;
    this.list.replaceChildren(...(g?.saves ?? []).map((s) => this.row(s, g?.saves.length ?? 0)));
    this.held.replaceChildren();
    if (g && g.deleted.length > 0) {
      const rows = el("ul", "games-list");
      rows.append(...g.deleted.map((d) => this.heldRow(d)));
      this.held.append(el("h3", "devices-heading", this.text.get(UI.gamesDeleted)), rows);
    }
    const full = g !== null && g.saves.length >= g.max_saves;
    if (full && this.note.textContent === "") this.note.textContent = this.text.fill(UI.gamesFull, { max: String(g.max_saves) });
    this.sync();
  }

  private sync(): void {
    const g = this.games;
    this.make.disabled = this.busy || g === null || g.saves.length >= g.max_saves;
    for (const b of this.root.querySelectorAll<HTMLButtonElement>(".games-row button")) b.disabled = this.busy;
  }

  private row(s: SaveInfo, live: number): HTMLLIElement {
    const playing = s.save_id === this.actions.playing();
    const li = this.describe(s, playing ? "games-row playing" : "games-row");
    const act = el("div", "games-actions");
    li.append(act);
    const asking = this.asking === s.save_id;
    if (playing && !asking) act.append(el("span", "games-playing", this.text.get(UI.gamePlaying)));
    if (!playing && !asking) act.append(this.tap("quiet", UI.gameSwitch, () => { this.root.close(); this.actions.open(s.save_id); }));
    const only = live <= 1;   // the only game is never deleted, only replaced
    if (playing && !only) return li;
    const parts = deleteParts(this.text, this.games?.kept_days ?? 0, asking, {
      ask: () => { this.asking = s.save_id; this.draw(); },
      cancel: () => { this.asking = null; this.draw(); },
      confirm: () => void (only ? this.startOver(s.save_id) : this.run(() => this.api.deleteGame(s.save_id).then(noted("delete", s.save_id)))),
    }, undefined, only ? START_OVER_WORDS : DELETE_WORDS);
    if (parts.question) act.before(parts.question);
    act.append(...parts.buttons);
    return li;
  }

  private heldRow(d: DeletedSave): HTMLLIElement {
    const li = this.describe(d.save, "games-row");
    li.append(el("p", "games-dates", this.text.fill(UI.gameKept, { until: dateOf(d.purge_at) })));
    const act = el("div", "games-actions");
    act.append(this.tap("quiet", UI.gameRestore, () => void this.run(() => this.api.restoreGame(d.save.save_id).then(noted("restore", d.save.save_id)))));
    li.append(act);
    return li;
  }

  /** A game's name, how far it is (its camp level, once it has one), and when it began and was last played. */
  private describe(s: SaveInfo, className: string): HTMLLIElement {
    const t = this.text;
    const li = el("li", className);
    const what = el("p", "games-what");
    what.append(el("span", "games-name", s.number === null ? t.get(UI.gameUnnumbered) : t.fill(UI.gameName, { number: String(s.number) })));
    if (s.camp_level !== null && s.camp_level > 0) what.append(el("span", "games-camp", t.fill(UI.gameCamp, { level: String(s.camp_level) })));
    li.append(what, el("p", "games-dates", t.fill(UI.gameDates, { started: dateOf(s.started_at), played: dateOf(s.played_at) })));
    return li;
  }

  private tap(className: string, key: string, then: () => void): HTMLButtonElement {
    const b = el("button", className, this.text.get(key));
    b.type = "button";
    b.addEventListener("click", then);
    return b;
  }
}

const noted = (action: "delete" | "restore", saveId: number) => (games: Games): Games => {
  noteGame(action, saveId);
  return games;
};

/** The one line for a refused games call; `max` is the cap on live games, when it is known. */
export function gameRefusal(text: Text, e: unknown, max: number | null): string {
  const code = e instanceof ApiFailure ? e.code : "network";
  if (code === "too_many_saves") return text.fill(UI.gamesFull, { max: String(max ?? "") });
  if (code === "rate_limited") return text.get(UI.gamesLimited);
  if (code === "not_found") return "";   // gone already (another page): the list redrawn says so
  return text.get(UI.devicesAway);
}
