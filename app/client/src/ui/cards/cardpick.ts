// A ruled lane's card: the Tasks page's card face (cardrow.ts makeRow, its needs drawn by cardneeds.ts). In the lane
// editor's Do list its tap picks the card; on a person's page (personpage.ts) its tap joins it to their time, else it has
// none. Its upside leads to the strength it feeds, as the Tasks page's does. Drawn at the view's own moment; a page that
// keeps the Row (pickFace) moves its bar and countdown on with tickFace, as the card panel does; a picker's face keeps
// the card's tap time.
import type { Card, View } from "../../api/types";
import { barFraction, footWords, makeRow, upsideWords, waitAt, type Row } from "./cardrow";
import { setText } from "../dom";
import type { PartContext } from "../part";
import { sideStrength } from "../ledger/strength";
import { WhenReady } from "./whenready";

/** The face of `card` as of `view`: title, completions, needs, and its time; the tap button carries aria-pressed.
 * Without `pick` the face only shows. `strengthOpen`: see makeRow. */
export function pickRow(ctx: PartContext, card: Card, view: View, pick?: () => void, strengthOpen?: Set<string>): HTMLElement {
  return pickFace(ctx, card, view, pick, strengthOpen).node;
}

/** pickRow's face with its Row, for a page that ticks it. */
export function pickFace(ctx: PartContext, card: Card, view: View, pick?: () => void, strengthOpen?: Set<string>): Row {
  const { catalog } = ctx;
  const row = makeRow(ctx, new WhenReady(ctx), card, pick ?? (() => undefined), strengthOpen);
  const side = catalog.cards.get(card.card)?.kept.find((k) => k.side !== null)?.side;
  const words = upsideWords(catalog, card);
  if (row.bonus && side && words !== null) row.bonus.draw(words, sideStrength(catalog, view, side));
  if (!pick) row.tap.disabled = true;
  row.node.classList.add("pick", card.blocker === null ? "ready" : "unready");
  setText(row.count, card.cap !== null || card.completions > 0 ? catalog.format.completions(card.completions, card.cap) : "");
  row.needs.draw(card, view, false);
  row.needs.tick(card, view, view.at);
  if (card.tap_s !== null) setText(row.foot, catalog.format.duration(card.tap_s));
  return row;
}

/** The face at `t`: its bar's fill, its countdown (a running tap's landing, else when it turns ready), its needs. */
export function tickFace(ctx: PartContext, row: Row, view: View, t: number): void {
  row.fill.style.transform = `scaleX(${barFraction(row.card, t)})`;
  setText(row.foot, footWords(ctx, waitAt(ctx, view, row.card), row.card, t));
  row.needs.tick(row.card, view, t);
}
