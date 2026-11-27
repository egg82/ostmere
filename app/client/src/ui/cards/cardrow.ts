// One card's row in the card panel (cards.ts): its nodes and what the panel keeps about it between views.
import type { Card, View } from "../../api/types";
import type { Catalog } from "../../game/catalog";
import { sample } from "../../game/clock";
import { keptReadyAt } from "../../game/ready";
import { Bonus } from "./bonus";
import { CardNeeds } from "./cardneeds";
import { UI } from "../../game/text";
import { el, tapFeedback } from "../dom";
import { FightPanel, seatFight } from "../ledger/fightpanel";
import type { PartContext } from "../part";
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
  /** The upside line of a card that feeds no side, else null. */
  upside: HTMLElement | null;
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

/** The card's upside line, null when it names none. A card that holds an entry while it runs words it at its share of the
 * mix (Card.share_bp; 0: no share, the full figure), as the town editor does at the person's share. */
export function upsideWords(catalog: Catalog, card: Card): string | null {
  const info = catalog.cards.get(card.card);
  if (!info?.upside_key) return null;
  return catalog.text.fill(info.upside_key, card.share_bp > 0 ? catalog.format.figuresAt(info, card.share_bp) : catalog.format.figures(info.change_bp));
}

/** A new row for `card`: its nodes, wired to tap it, or to `onTap` (a choice among cards: no When ready, no fight).
 * `strengthOpen`: the cards whose upside line has its strength sheet open, kept by a page that redraws its rows. */
export function makeRow(ctx: PartContext, whenReady: WhenReady, card: Card, onTap?: () => void, strengthOpen?: Set<string>): Row {
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
    fight: info?.fight ? new FightPanel(catalog, info.fight) : null, bonus: null, upside: null,
  };
  const head = el("span", "card-head");
  head.append(el("span", "card-title", catalog.label(info?.label_key)), row.count);
  tap.append(head);
  const side = info?.kept.find((k) => k.side !== null)?.side;
  const words = upsideWords(catalog, card);
  if (words !== null) {
    if (side) {   // beside the tap, never inside the button: a button holds no button
      row.bonus = new Bonus(catalog, side, "card-upside", (open) => { if (open) strengthOpen?.add(card.card); else strengthOpen?.delete(card.card); }, strengthOpen?.has(card.card));
      row.bonus.draw(words, null);
    } else tap.append(row.upside = el("span", "card-upside", words));
  }
  const track = el("span", "card-track");
  track.append(row.fill);
  tap.append(row.needs.root, track, row.foot);
  tap.addEventListener("click", () => {
    tapFeedback();
    if (onTap) onTap();
    else ctx.actions.decide({ kind: "tap_card", card: card.card });
  });
  pressable(tap, node);
  if (onTap) node.append(tap, ...(row.bonus ? [row.bonus.line] : []));   // a choice among cards: the upside line beside the tap, as seatFight seats it
  else if (row.fight) seatFight(node, tap, row.ready, row.fight, row.bonus);
  else if (row.bonus) seatFight(node, tap, row.ready, null, row.bonus);
  else node.append(tap, row.ready);
  return row;
}

/** How far `card`'s one bar is through its span at `t` (Card.bar modulo bar_total), 0 to 1. */
export function barFraction(card: Card, t: number): number {
  const span = card.bar_total;
  const v = sample(card.bar, t);
  return span > 0 ? (((v % span) + span) % span) / span : 0;
}

/** When the card's foot counts down to: a running tap's landing, else when it turns ready by itself; null for none. */
export function waitAt(ctx: PartContext, view: View | null, card: Card): number | null {
  return card.by === "tap" ? card.completes_at : view ? keptReadyAt(view, card, ctx.catalog.content.scales.quantity_per_item) : null;
}

/** The card's foot at `t`: a running tap's timer bare; a card waiting to open, "Opens in" and the time (never the same
 * words as a timer); else its tap time. */
export function footWords(ctx: PartContext, wait: number | null, card: Card, t: number): string {
  const { format, text } = ctx.catalog;
  if (wait === null) return card.tap_s !== null ? format.duration(card.tap_s) : "";
  const left = format.duration(wait - t);
  return card.by === "tap" ? left : text.fill(UI.opensIn, { d: left });
}
