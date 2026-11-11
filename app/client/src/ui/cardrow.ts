// One card's row in the card panel (cards.ts): its nodes and what the panel keeps about it between views.
import type { Card } from "../api/types";
import { CardNeeds } from "./cardneeds";
import { el, pulse, tapFeedback } from "./dom";
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
  /** A line on the card: shown when the arrival queue un-holds it, then kept `ms`; `failed`: a failed tap's. */
  lines: Array<{ node: HTMLElement; ms: number; shownAt: number; failed: boolean }>;
  /** False while a finished card's done look waits its turn in the arrival queue. */
  doneShown?: boolean;
  /** The finished card still in this row's slot, until this card's turn to arrive. */
  stand?: HTMLElement;
  /** The odds under a fight card (fightpanel.ts), else null. */
  fight: FightPanel | null;
  /** A rule started its running tap (ui/fires.ts), as of the last restyle. */
  byOrder?: boolean;
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
    fill: el("span", "card-fill"), foot: el("span", "card-foot"), card, done: false, doneAt: 0, lines: [],
    fight: info?.fight ? new FightPanel(catalog, info.fight) : null,
  };
  const head = el("span", "card-head");
  head.append(el("span", "card-title", catalog.label(info?.label_key)), row.count);
  tap.append(head);
  if (info?.upside_key) tap.append(el("span", "card-upside", catalog.text.fill(info.upside_key, catalog.format.figures(info.change_bp))));
  const track = el("span", "card-track");
  track.append(row.fill);
  tap.append(row.needs.root, track, row.foot);
  tap.addEventListener("click", () => {
    tapFeedback();
    pulse(node, "press");
    ctx.actions.decide({ kind: "tap_card", card: card.card });
  });
  if (row.fight) seatFight(node, tap, row.ready, row.fight);
  else node.append(tap, row.ready);
  return row;
}
