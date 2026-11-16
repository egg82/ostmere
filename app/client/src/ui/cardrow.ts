// One card's row in the card panel (cards.ts): its nodes and what the panel keeps about it between views.
import type { Card } from "../api/types";
import { Bonus } from "./bonus";
import { CardNeeds } from "./cardneeds";
import { el, tapFeedback } from "./dom";
import { FightPanel, seatFight } from "./fightpanel";
import type { PartContext } from "./part";
import type { WhenReady } from "./whenready";

export interface Row {
  id: string;
  node: HTMLElement;
  tap: HTMLButtonElement;
  count: HTMLElement;
  needs: CardNeeds;
  /** "When ready": queues a step that will turn ready by itself (whenready.ts). */
  ready: HTMLButtonElement;
  fill: HTMLElement;
  foot: HTMLElement;
  card: Card;
  done: boolean;
  /** performance.now() when the card finished (so the hold is measured from the finish); 0 while live. */
  doneAt: number;
  /** False while a finished card's done look waits its turn in the arrival queue. */
  doneShown?: boolean;
  /** The odds under a fight card (fightpanel.ts), else null. */
  fight: FightPanel | null;
  /** The upside line of a card that feeds a side's strength, which leads to it (bonus.ts), else null. */
  bonus: Bonus | null;
  /** A rule started its running tap (ui/fires.ts), as of the last restyle. */
  byOrder?: boolean;
  /** performance.now() until which a level shows on the card (cardlevel.ts); undefined: none. */
  levelUntil?: number;
}

/** The card sinks while a pointer holds `tap` down and settles when it lets go (game.css, .card.pressed). Refused or
 * not, a tap that can be made goes down; a disabled one stays put. */
function pressable(tap: HTMLButtonElement, node: HTMLElement): void {
  tap.addEventListener("pointerdown", () => { if (!tap.disabled) node.classList.add("pressed"); });
  for (const type of ["pointerup", "pointercancel", "pointerleave"]) tap.addEventListener(type, () => node.classList.remove("pressed"));
}

/** A new row for `card`: its nodes, wired to tap it. */
export function makeRow(ctx: PartContext, whenReady: WhenReady, card: Card): Row {
  const { catalog } = ctx;
  const info = catalog.cards.get(card.card);
  const node = el("div", `card card-${info?.presentation ?? "action"} hue-${catalog.rank(card.card) % 6}`);
  node.dataset.lane = info?.lane ?? "hands";
  node.dataset.card = card.card;
  const tap = el("button", "card-tap");
  tap.type = "button";
  const row: Row = {
    id: card.card, node, tap, count: el("span", "card-count"), needs: new CardNeeds(ctx, card.card), ready: whenReady.make(card.card, node),
    fill: el("span", "card-fill"), foot: el("span", "card-foot"), card, done: false, doneAt: 0,
    fight: info?.fight ? new FightPanel(catalog, info.fight) : null, bonus: null,
  };
  const head = el("span", "card-head");
  head.append(el("span", "card-title", catalog.label(info?.label_key)), row.count);
  tap.append(head);
  const side = info?.kept.find((k) => k.side !== null)?.side;
  if (info?.upside_key) {
    const words = catalog.text.fill(info.upside_key, catalog.format.figures(info.change_bp));
    if (side) {   // beside the tap, never inside the button: a button holds no button
      row.bonus = new Bonus(catalog, side, "card-upside");
      row.bonus.draw(words, null);
    } else tap.append(el("span", "card-upside", words));
  }
  const track = el("span", "card-track");
  track.append(row.fill);
  tap.append(row.needs.root, track, row.foot);
  tap.addEventListener("click", () => {
    tapFeedback();
    ctx.actions.decide({ kind: "tap_card", card: card.card });
  });
  pressable(tap, node);
  if (row.fight) seatFight(node, tap, row.ready, row.fight, row.bonus);
  else if (row.bonus) seatFight(node, tap, row.ready, null, row.bonus);
  else node.append(tap, row.ready);
  return row;
}
