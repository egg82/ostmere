// What the page points the player at (CONTRACT.txt), read off the view and the content only: a red ledger line's
// answer (its order card once offered, else what draws on it most, unless that is the hands' passing tap); the card
// in play that makes a short need's store; a step need's count; the card the one glow goes to, and the card an idle
// player is nudged toward; and, after the end, a chip's first-rule lesson entry in the hands strip.
import type { Card, LedgerLine, OrderCard, View } from "../api/types";
import type { Catalog } from "./catalog";
import { sample } from "./clock";
import { ruleFor, rulesFull } from "./orders";

/** The store's order card on offer: the last in content order whose offered_after view.unlocked holds (or that names
 * none), so a later card (a re-tune of a rule, a rule for a new need) supersedes an earlier one once it is offered. */
export function offeredCard(catalog: Catalog, view: View, store: string): OrderCard | undefined {
  return catalog.orderCardsFor(store).filter((c) => !c.offered_after || catalog.unlocked(view, c.offered_after.category, c.offered_after.id)).pop();
}

/** A card for a rising line: its `when` is an at_least and its task takes from the store. It is offered
 * while the line is full or rising, never once a rule on its store and test is set (docs/design/opening-screen.md,
 * "Ledger and rules"). */
export function risingCard(catalog: Catalog, card: OrderCard): boolean {
  const info = card.then.kind === "tap_card" ? catalog.cards.get(card.then.card) : undefined;
  return card.when.kind === "at_least" && info !== undefined && info.inputs.some((i) => i.store === card.store);
}

/** The line is full or rising at the view's time. */
export function risingLine(line: LedgerLine, at: number): boolean {
  return line.net_per_hour > 0 || (line.cap > 0 && sample(line.segment, at) >= line.cap);
}

/** A chip's card may be on show (CONTRACT.txt): one that waits for the end (after_end) has the end recorded and its
 * lines read (`endBehind`), and no rule is set on its store and test. Once shown, it stays while this holds. */
export function chipCardOpen(view: View, card: OrderCard, endBehind: boolean): boolean {
  return (!card.after_end || (view.ended_at !== null && endBehind)) && ruleFor(view, card) < 0;
}

/** The chip's cards the hands strip offers now: those of the first chip in view.chips that has any open, in content
 * order, each one that may be on show whose offered_after, if any, view.unlocked holds (its task is open to run). Cards
 * of one chip share its store and test, so a rule set on either closes them all. */
export function chipCards(catalog: Catalog, view: View, endBehind: boolean): OrderCard[] {
  if (rulesFull(catalog, view)) return [];
  const due = catalog.chipCards.filter((c) => c.chip !== null && view.chips.includes(c.chip) && chipCardOpen(view, c, endBehind)
    && (!c.offered_after || catalog.unlocked(view, c.offered_after.category, c.offered_after.id)));
  return due.filter((c) => c.chip === due[0]?.chip);
}

/** The runner drawing on the line most, or null when nothing draws on it or that is the hands' tap (it ends). */
export function largestDrain(line: LedgerLine, view: View): string | null {
  let most: { runner: string; per_hour: number } | null = null;
  for (const c of line.contributions) if (c.per_hour < 0 && (most === null || c.per_hour < most.per_hour)) most = c;
  const tapped = view.lanes.find((l) => l.lane === "hands")?.running_card ?? null;
  return most && most.runner !== tapped ? most.runner : null;
}

/** A card's completions, in play or completed; none when it is in neither. */
export function completionsOf(view: View, card: string): number {
  return [...view.cards, ...view.completed].find((c) => c.card === card)?.completions ?? 0;
}

/** The card the one glow goes to now: the first marked one (CardInfo.glows) not glowed yet, ready, its lane free or
 * cutting in (Card.cuts_in). */
export function glowTarget(catalog: Catalog, view: View, glowed: ReadonlySet<string>): string | null {
  const busy = new Set(view.lanes.filter((l) => l.running_card !== null).map((l) => l.lane));
  const card = view.cards.find((c) => {
    const info = catalog.cards.get(c.card);
    return info?.glows === true && !glowed.has(c.card) && c.blocker === null && (c.cuts_in || !busy.has(info.lane));
  });
  return card?.card ?? null;
}

/** How far out the next timer card must be (seconds) before the nudge points at its countdown. */
const TIMER_FAR_S = 600;

/** The card the idle nudge points at: the first one ready with its lane free that has never completed, while no mix
 * runs (the player has not yet put the work in motion); else, with nothing ready at all and the next thing a timer
 * card more than TIMER_FAR_S out, that card, so the eye lands on its countdown. */
export function nudgeTarget(catalog: Catalog, view: View): string | null {
  if (view.running_mix_id === null) {
    const busy = new Set(view.lanes.filter((l) => l.running_card !== null).map((l) => l.lane));
    const card = view.cards.find((c) => c.blocker === null && c.completions === 0 && !busy.has(catalog.cards.get(c.card)?.lane ?? ""));
    if (card) return card.card;
  }
  return timerTarget(view);
}

function timerTarget(view: View): string | null {
  if (view.cards.some((c) => c.blocker === null && (c.cap === null || c.completions < c.cap))) return null;
  const next = view.cards
    .filter((c) => c.blocker?.ready_at != null)
    .reduce<Card | null>((a, c) => (a === null || (c.blocker?.ready_at ?? 0) < (a.blocker?.ready_at ?? 0) ? c : a), null);
  const far = next?.blocker?.condition.kind === "after_time" && (next.blocker.ready_at ?? 0) - view.at > TIMER_FAR_S;
  return far ? next.card : null;
}
