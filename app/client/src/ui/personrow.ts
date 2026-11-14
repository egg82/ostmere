// A person's row in the Town view (docs/design/opening-screen.md, "The Town view"), the one form for everyone there: their
// face and who they are, what they work now and the bar of that card. A person who has joined adds their split
// (ui/townstrip.ts); a lane run by rules adds its Change (ui/lanerows.ts), each before the bar.
import type { View } from "../api/types";
import { sample } from "../game/clock";
import { UI } from "../game/text";
import { face } from "./asknode";
import { el, setText } from "./dom";
import type { PartContext } from "./part";

export interface PersonRow {
  node: HTMLElement;
  /** Where the caller's own parts go: just before the bar. */
  track: HTMLElement;
  faceSlot: HTMLElement;
  name: HTMLElement;
  doing: HTMLElement;
  fill: HTMLElement;
}

/** An empty row; `kind` is the row's own class beside `person-row`. */
export function personRow(kind: string, lane: string): PersonRow {
  const node = el("div", `person-row ${kind}`);
  node.dataset.lane = lane;
  const faceSlot = el("span", "town-face");
  const name = el("span", "town-name");
  const doing = el("span", "hands-text town-doing");
  const who = el("div", "town-who");
  who.append(name, doing);
  const track = el("div", "card-track lane-bar");   // the card's own bar, as the card panel draws it
  const fill = el("span", "card-fill lane-fill");
  track.append(fill);
  node.append(faceSlot, who, track);
  return { node, track, faceSlot, name, doing, fill };
}

/** Who the row is (`label`, the lane's) and the card they work now, or idle. */
export function drawWho(ctx: PartContext, row: PersonRow, lane: string, label: string, running: string | null): void {
  setText(row.name, label);
  row.faceSlot.replaceChildren(face(ctx, lane, label));
  setText(row.doing, running ? ctx.catalog.cardLabel(running) : ctx.catalog.text.get(UI.laneIdle));
  row.doing.classList.toggle("idle", running === null);
}

/** The bar of the card worked now (`running`), sampled at `t` as the card panel samples it. */
export function drawBar(row: PersonRow, view: View, running: string | null, t: number): void {
  const card = view.cards.find((c) => c.card === running);
  const span = card?.bar_total ?? 0;
  const v = card ? sample(card.bar, t) : 0;
  row.fill.style.transform = `scaleX(${span > 0 ? (((v % span) + span) % span) / span : 0})`;
}
