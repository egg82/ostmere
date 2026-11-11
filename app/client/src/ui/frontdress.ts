// The front page once the content is in: the stage's scene, the panel's words, and, for a browser with games, the list
// of them (ui/places.ts) with the selected game's camp behind the panel and its line in it. begin.ts says who this
// browser is and what opening a game does; this draws.
import type { GameApi } from "../api/api";
import type { Content, SaveInfo } from "../api/types";
import type { Straight } from "../app/straight";
import { Text, UI } from "../game/text";
import { el } from "./dom";
import { emptyView } from "./camp-views";
import { DELETE_WORDS, START_OVER_WORDS, deleteParts } from "./gamedelete";
import { savedLine } from "./gamenames";
import { glimpse } from "./glimpse";
import { Pictures } from "./pictures";
import { Places } from "./places";
import { straightChoice } from "./straightchoice";

/** The size, in art pixels, of the window each row's picture shows of its camp. */
const WINDOW: [number, number] = [112, 72];
const PHONE = "(max-width: 760px)";

export interface DressIn {
  api: GameApi;
  content: Content;
  /** Every live game, newest first; none on a first visit. */
  saves: SaveInfo[];
  max: number;
  /** How long a deleted game is held (Me.kept_days). */
  keptDays: number;
  straight: Straight;
  /** What the main button opens from now on: a game, or (null) a new one. */
  carryOn(saveId: number | null): void;
  /** Open a game, or make one when null. */
  start(saveId: number | null): void;
}

function byId(id: string): HTMLElement | null {
  return document.getElementById(id);
}

export function dress(d: DressIn): void {
  const text = new Text(d.content);
  const stageBox = byId("stage");
  const chip = byId("ledger");
  const sub = byId("sub");
  if (!stageBox || !chip || !sub) return;
  const pictures = Pictures.open(d.content.scales.quantity_per_item);
  const stage = pictures.then((p) => glimpse(stageBox, chip, p, text, d.content));
  const main = byId("begin");
  if (main) main.textContent = text.get(UI.frontBegin);
  const [newest] = d.saves;
  if (!newest) {
    sub.textContent = text.get(UI.frontFirst);
    return;
  }
  const places = new Places({
    api: d.api, text, saves: d.saves, max: d.max, keptDays: d.keptDays,
    paint: pictures.then((p) => (p ? (box, view) => p.still(box, view, WINDOW) : null)),
    empty: emptyView(d.content.scales.quantity_per_item),
    now: Date.now,
    open: (id) => { sheet.dialog.close(); d.start(id); },
    picked: (s) => select(s),
    begin: async () => { sheet.dialog.close(); d.start((await d.api.begin()).save.save_id); },
  });
  const keep = straightChoice(text, d.straight, "front-keep", "front-keep-box");
  const trash = el("span", "desk-only");   // the panel's Delete, beside Continue (a phone deletes from the sheet's rows)
  const question = el("p", "games-ask desk-only");
  let asking = false;
  const showTrash = (): void => {
    const s = places.current;
    question.textContent = "";
    trash.replaceChildren();
    if (!s) return;   // New game is selected
    const only = places.count <= 1;   // the only game is never deleted, only replaced
    const parts = deleteParts(text, d.keptDays, asking, {
      ask: () => { asking = true; showTrash(); },
      cancel: () => { asking = false; showTrash(); },
      confirm: () => {
        asking = false;
        showTrash();
        if (only) void places.startOver(s.save_id);
        else void places.remove(s.save_id);
      },
    }, { quiet: "front-quiet", primary: "front-primary" }, only ? START_OVER_WORDS : DELETE_WORDS);
    question.textContent = parts.question?.textContent ?? "";
    trash.append(...parts.buttons);
  };
  const select = (s: SaveInfo | null): void => {   // a game: Continue opens it; New game: the first visit's page
    d.carryOn(s?.save_id ?? null);
    if (main) main.textContent = text.get(s ? UI.frontContinue : UI.frontBegin);
    sub.textContent = s ? savedLine(text, s, Date.now()) : text.get(UI.frontFirst);
    keep.root.hidden = s === null;
    chip.hidden = s !== null;   // the ledger line's figures are the canned moment's, never a save's
    asking = false;
    showTrash();
    const view = s ? places.view(s.save_id) : Promise.resolve(null);
    void Promise.all([view, stage]).then(([v, st]) => { if (places.current === s) st.show(v); });
  };
  const sheet = gamesSheet(text);
  const slot = sheet.slot;
  byId("begin")?.after(sheet.opener);
  byId("begin")?.after(trash);
  byId("keep")?.before(question);
  keep.show();
  byId("keep")?.append(keep.root);
  const rail = byId("rail");
  const narrow = window.matchMedia(PHONE);
  const placeIt = (): void => {
    places.opensDirectly(narrow.matches);
    (narrow.matches || !rail ? slot : rail).append(places.root);
    if (rail) rail.hidden = narrow.matches;
  };
  narrow.addEventListener("change", placeIt);
  placeIt();
  select(newest);
}

interface GamesSheet {
  dialog: HTMLDialogElement;
  /** Where the list sits on a phone. */
  slot: HTMLElement;
  /** The phone's button that opens the sheet. */
  opener: HTMLButtonElement;
}

function gamesSheet(text: Text): GamesSheet {
  const dialog = el("dialog", "sheet games-sheet");
  const slot = el("div", "places-slot");
  const close = el("button", "quiet", text.get(UI.close));
  close.type = "button";
  close.addEventListener("click", () => dialog.close());
  const foot = el("div", "sheet-actions");
  foot.append(close);
  dialog.append(slot, foot);
  dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
  document.body.append(dialog);
  const opener = el("button", "front-quiet phone-only", text.get(UI.gamesOpen));
  opener.type = "button";
  opener.addEventListener("click", () => dialog.showModal());
  return { dialog, slot, opener };
}
