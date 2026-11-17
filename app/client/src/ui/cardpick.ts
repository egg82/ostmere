// A card as a choice (the lane editor's Do list): the Tasks page's card face (cardrow.ts makeRow, its needs drawn by
// cardneeds.ts), read-only, its tap picking the card instead of tapping it. Drawn at the view's own moment.
import type { Card, View } from "../api/types";
import { makeRow } from "./cardrow";
import { setText } from "./dom";
import type { PartContext } from "./part";
import { WhenReady } from "./whenready";

/** The face of `card` as of `view`: title, completions, needs, and its time; the tap button carries aria-pressed. */
export function pickRow(ctx: PartContext, card: Card, view: View, pick: () => void): HTMLElement {
  const { catalog } = ctx;
  const row = makeRow(ctx, new WhenReady(ctx), card, pick);
  row.node.classList.add("pick", card.blocker === null ? "ready" : "unready");
  setText(row.count, card.cap !== null || card.completions > 0 ? catalog.format.completions(card.completions, card.cap) : "");
  row.needs.draw(card, view, false);
  row.needs.tick(card, view, view.at);
  if (card.tap_s !== null) setText(row.foot, catalog.format.duration(card.tap_s));
  return row.node;
}
