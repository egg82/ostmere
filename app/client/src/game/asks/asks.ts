// What an ask says of itself (contract/offers.txt, "OFFERS"): which asks are open and in what order, who asks, what led to it,
// and each figure an answer moves, now → once given, read off a dry run of that answer, never computed here. Pure.
import type { AnswerShift, OfferInfo, View } from "../../api/types";
import type { Catalog } from "../page/catalog";
import { causeWords } from "../book/chronwords";
import { UI } from "../page/text";

const names = new Intl.ListFormat(undefined, { type: "conjunction" });

/** The open offers' ids in content order: the first is the one shown. */
export function openAsks(view: View): string[] {
  return view.offers.filter((o) => o.answer === null).map((o) => o.offer);
}

/** The people who ask, by name: a lane's name text, else its label as it reads now; "" when no one person asks. */
export function askedBy(catalog: Catalog, view: View, info: OfferInfo): string {
  const { text } = catalog;
  return names.format(info.askers.map((lane) => {
    const key = catalog.content.lane_infos.find((l) => l.lane === lane)?.name_key;
    return key ? text.get(key) : catalog.laneLabel(lane, view);
  }));
}

/** What led to the ask, worded as a chronicle line's cause. Null when the content gives none or the page cannot word it. */
export function askCause(catalog: Catalog, info: OfferInfo): string | null {
  return causeWords(catalog, info.cause);
}

/** An answer's {pct} and {pct_b} slots: each served change, or where the server read its target's total, that total now
 * → once given (OfferAnswer.shifts; the answer's own change when it names none, never computed here). */
export function answerPcts(catalog: Catalog, changesBp: readonly number[], shifts: readonly (AnswerShift | null)[]): Record<string, string> {
  const { text, format } = catalog;
  return Object.fromEntries(changesBp.slice(0, 2).map((bp, i) => {
    const s = shifts[i];
    return [i === 0 ? "pct" : "pct_b", s ? text.fill(UI.askShift, { before: format.change(s.now_bp), after: format.change(s.after_bp) }) : format.change(bp)];
  }));
}

/** Each figure that differs between the view and the dry run of an answer: a store's net rate, then its cap (the
 * Camp's store aside, which the Camp bar shows), then a card's time. In view order; none when nothing moves. */
export function answerFigures(catalog: Catalog, view: View, after: View): string[] {
  const { text, format } = catalog;
  const figure = (name: string, before: string, now: string): string => text.fill(UI.askFigure, { name, before, after: now });
  const lines = view.ledger.filter((l) => l.store !== catalog.campStore);
  const later = (store: string) => after.ledger.find((l) => l.store === store);
  const rates = lines.flatMap((l) => {
    const a = later(l.store);
    return a && a.net_per_hour !== l.net_per_hour ? [figure(catalog.storeTitle(l.store), format.perMinute(l.net_per_hour), format.perMinute(a.net_per_hour))] : [];
  });
  const caps = lines.flatMap((l) => {
    const a = later(l.store);
    return a && a.cap !== l.cap ? [text.fill(UI.prestigeCap, { store: catalog.storeTitle(l.store), before: format.items(l.cap), after: format.items(a.cap) })] : [];
  });
  const times = view.cards.flatMap((c) => {
    const a = after.cards.find((x) => x.card === c.card);
    return a && c.tap_s !== null && a.tap_s !== null && a.tap_s !== c.tap_s ? [figure(catalog.cardLabel(c.card), format.duration(c.tap_s), format.duration(a.tap_s))] : [];
  });
  return [...rates, ...caps, ...times];
}
