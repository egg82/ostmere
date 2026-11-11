// The front page's list of games, a save-select screen: every game newest first, each with a small picture of its own
// camp, then New game. One component with two placements (a rail over the scene on a desktop, a sheet on a phone); the
// caller moves its root. Where it is a picker (the rail) a tap selects a game and the page shows it, and a tap on the
// selected game opens it; where a tap opens (the sheet) it opens that game. Drawing a picture reads the save's view (GET), and never opens the save.
import type { GameApi } from "../api/api";
import type { SaveInfo, View } from "../api/types";
import { UI, type Text } from "../game/text";
import { el } from "./dom";
import { gameRefusal } from "./games";
import { DELETE_WORDS, START_OVER_WORDS, deleteParts, startOver } from "./gamedelete";
import { campLine, gameName, playedLine } from "./gamenames";

/** Draws a view's camp into a box. */
export type Paint = (box: HTMLElement, view: View) => void;

export interface PlacesIn {
  api: Pick<GameApi, "savedView" | "deleteGame" | "begin">;
  /** How long a deleted game is held (Me.kept_days), for the question before a delete. */
  keptDays: number;
  text: Text;
  /** Every live game, newest first. */
  saves: SaveInfo[];
  /** The most live games an account holds (Me.max_saves): a full list has no New game row, which could only be refused. */
  max: number;
  /** Null when the scene art cannot be had: every picture is then a dark frame. */
  paint: Promise<Paint | null>;
  /** The camp of a game not yet played, for New game's picture. */
  empty: View;
  now: () => number;
  /** A game was opened from a row (where a tap opens). */
  open(saveId: number): void;
  /** A game, or null for New game, was selected (where a tap selects). */
  picked(save: SaveInfo | null): void;
  /** New game: resolves once the game is made and opened, rejects with the refusal. */
  begin(): Promise<void>;
}

export class Places {
  readonly root = el("div", "places");
  private readonly list = el("ul", "places-list");
  private rows = new Map<number, HTMLButtonElement>();
  private fresh: HTMLButtonElement | null = null;
  private saves: SaveInfo[];
  private asking: number | null = null;   // the game whose Delete asks once more (where a tap opens)
  private readonly note = el("p", "places-note");
  private readonly views = new Map<number, Promise<View | null>>();
  private selected: SaveInfo | null;   // null: New game
  private direct = false;
  private busy = false;

  constructor(private readonly p: PlacesIn) {
    const [newest] = p.saves;
    if (!newest) throw new Error("the list of games needs a game");
    this.selected = newest;
    this.saves = p.saves;
    this.note.setAttribute("role", "status");
    for (const s of p.saves) this.views.set(s.save_id, p.api.savedView(s.save_id).catch(() => null));   // all at once
    this.root.append(el("h2", "places-heading", p.text.get(UI.gamesHeading)), this.list, this.note);
    this.fill();
  }

  /** The games still live; the list redraws from these after a delete. */
  get count(): number {
    return this.saves.length;
  }

  /** Deletes a game and redraws: the newest left is selected, and New game is back if the list was full. Refused:
   * one line, and the list stays. */
  async remove(saveId: number): Promise<void> {
    this.asking = null;
    try {
      this.saves = (await this.p.api.deleteGame(saveId)).saves;
    } catch (e) {
      this.note.textContent = gameRefusal(this.p.text, e, this.p.max);
      this.fill();
      return;
    }
    this.note.textContent = "";
    this.selected = this.saves[0] ?? null;
    this.fill();
    if (this.selected) this.p.picked(this.selected);
  }

  private fill(): void {
    this.rows = new Map();
    this.fresh = null;
    this.list.replaceChildren(...this.saves.map((s) => this.row(s)));
    if (this.saves.length < this.p.max) this.list.append(this.newRow());
    this.mark();
  }

  /** The selected game; null while New game is. */
  get current(): SaveInfo | null {
    return this.selected;
  }

  /** The game's camp as last written, or null when it could not be had. */
  view(saveId: number): Promise<View | null> {
    return this.views.get(saveId) ?? Promise.resolve(null);
  }

  /** Where a tap opens the game (the phone's sheet) rather than selecting it. */
  opensDirectly(direct: boolean): void {
    this.direct = direct;
    this.fill();
  }

  private row(s: SaveInfo): HTMLLIElement {
    const button = this.button(gameName(this.p.text, s), [campLine(this.p.text, s), playedLine(this.p.text, s, this.p.now())]);
    button.addEventListener("click", () => {
      if (this.direct || s === this.selected) { this.p.open(s.save_id); return; }   // the selected game's tap is Continue's
      this.selected = s;
      this.mark();
      this.p.picked(s);
    });
    this.rows.set(s.save_id, button);
    void Promise.all([this.p.paint, this.views.get(s.save_id)]).then(([paint, view]) => this.show(button, paint, view ?? null));
    const li = this.item(button);
    if (this.direct) li.append(this.trash(s));
    return li;
  }

  private trash(s: SaveInfo): HTMLElement {
    const parts = deleteParts(this.p.text, this.p.keptDays, this.asking === s.save_id, {
      ask: () => { this.asking = s.save_id; this.fill(); },
      cancel: () => { this.asking = null; this.fill(); },
      confirm: () => (this.saves.length > 1 ? void this.remove(s.save_id) : void this.startOver(s.save_id)),
    }, undefined, this.saves.length > 1 ? DELETE_WORDS : START_OVER_WORDS);
    const box = el("div", "places-trash");
    if (parts.question) box.append(parts.question);
    const actions = el("div", "games-actions");
    actions.append(...parts.buttons);
    box.append(actions);
    return box;
  }

  private newRow(): HTMLLIElement {
    const button = this.button(this.p.text.get(UI.gameNew), []);
    button.classList.add("new");
    button.addEventListener("click", () => {
      if (this.direct || this.selected === null) { void this.begin(); return; }
      this.selected = null;
      this.mark();
      this.p.picked(null);
    });
    this.fresh = button;
    void this.p.paint.then((paint) => this.show(button, paint, this.p.empty));
    return this.item(button);
  }

  /** Start over for the only game (gamedelete.ts); a refusal is the note's line. */
  startOver(oldId: number): Promise<void> {
    return this.guarded(async () => this.p.open((await startOver(this.p.api, oldId)).save.save_id));
  }

  private begin(): Promise<void> {
    return this.guarded(() => this.p.begin());
  }

  private async guarded(make: () => Promise<void>): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    this.asking = null;
    this.note.textContent = "";
    try {
      await make();
    } catch (e) {
      this.note.textContent = gameRefusal(this.p.text, e, this.p.max);
    } finally {
      this.busy = false;
    }
  }

  private button(name: string, lines: (string | null)[]): HTMLButtonElement {
    const button = el("button", "place");
    button.type = "button";
    const words = el("span", "ptext");
    words.append(el("span", "pname", name), ...lines.filter((l) => l !== null).map((l) => el("span", "pmeta", l)));
    button.append(el("span", "pic"), words);
    return button;
  }

  private item(button: HTMLButtonElement): HTMLLIElement {
    const li = el("li");
    li.append(button);
    return li;
  }

  /** A picture is drawn from a view, or is a plain dark frame: an unknown camp must not look like a real one. */
  private show(button: HTMLButtonElement, paint: Paint | null, view: View | null): void {
    const box = button.querySelector<HTMLElement>(".pic");
    if (!box) return;
    if (paint && view) paint(box, view);
    else box.classList.add("failed");
  }

  private mark(): void {
    const pressed = (button: HTMLButtonElement, on: boolean): void => {
      if (this.direct) button.removeAttribute("aria-pressed");
      else button.setAttribute("aria-pressed", String(on));
    };
    for (const [id, button] of this.rows) pressed(button, id === this.selected?.save_id);
    if (this.fresh) pressed(this.fresh, this.selected === null);
  }
}
