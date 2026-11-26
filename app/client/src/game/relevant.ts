// The stores and cards a rule is about, read off the cards' served CardInfo (makes, takes, kept, fight) and nothing else
// (never words in a name): the condition editor offers these first (docs/design/opening-screen.md, "The condition editor").
import type { Catalog } from "./catalog";

/** The stores a rule doing some cards is about, in three tiers, each store once, in its first tier. */
export interface Relevant {
  /** The stores the cards make. */
  makes: string[];
  /** The stores they take. */
  takes: string[];
  /** One step out: the other stores of each card in play that makes what they take or takes what they make. */
  near: string[];
}

/** The relevant stores of a rule doing `cards` (a task, or the cards of a mix): each tier holds only stores in `stores`
 * (the ones the editor may offer), in that order; one step out looks only at the cards in `known` (the cards in play),
 * so a card the player has not met adds nothing. */
export function relevantStores(catalog: Catalog, cards: readonly string[], known: readonly string[], stores: readonly string[]): Relevant {
  const info = (c: string) => catalog.cards.get(c);
  const doing = new Set(cards);
  const makes = new Set(cards.flatMap((c) => info(c)?.makes ?? []));
  const takes = new Set(cards.flatMap((c) => info(c)?.takes ?? []));
  const neighbours = known.filter((k) => !doing.has(k)).map(info).filter((i) => i !== undefined)
    .filter((i) => i.makes.some((s) => takes.has(s)) || i.takes.some((s) => makes.has(s)));
  const near = new Set(neighbours.flatMap((i) => [...i.makes, ...i.takes]));
  const seen = new Set<string>();
  const tier = (from: Set<string>) => stores.filter((s) => from.has(s) && !seen.has(s)).map((s) => { seen.add(s); return s; });
  return { makes: tier(makes), takes: tier(takes), near: tier(near) };
}

/** The cards a rule doing `cards` is about, as what it might wait on running, best first, each once: the cards its
 * effect reaches (a `kept` entry on a lane, or on a side a fight card is on), then the cards that make what it takes,
 * then the cards that take what it makes. Only cards in `known` (the cards in play) and not `cards` themselves. */
export function relevantCards(catalog: Catalog, cards: readonly string[], known: readonly string[]): string[] {
  const info = (c: string) => catalog.cards.get(c);
  const doing = new Set(cards);
  const kept = cards.flatMap((c) => info(c)?.kept ?? []);
  const takes = new Set(cards.flatMap((c) => info(c)?.takes ?? []));
  const makes = new Set(cards.flatMap((c) => info(c)?.makes ?? []));
  const others = known.filter((k) => !doing.has(k));
  const reached = (c: string) => kept.some((k) => (k.lane !== null && k.lane === catalog.laneOf(c)) || (k.side !== null && k.side === info(c)?.fight?.side));
  const tiers = [reached, (c: string) => (info(c)?.makes ?? []).some((s) => takes.has(s)), (c: string) => (info(c)?.takes ?? []).some((s) => makes.has(s))];
  return [...new Set(tiers.flatMap((hit) => others.filter(hit)))];
}
