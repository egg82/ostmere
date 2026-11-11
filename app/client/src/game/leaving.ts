// A person who leaves (CONTRACT.txt, "LEAVES"): the Step that holds the left unlock has already dropped their lane, their
// cards and their shares. The page's lists keep drawing them from the view they were last in until the moment's lines
// have been read, so a person does not vanish before the lines that say why.
import type { View } from "../api/types";
import type { Catalog } from "./catalog";

/** A lane whose person has left, with the view the page last drew them in. */
export interface Leaver {
  lane: string;
  from: View;
}

/** The people `view` has lost since `prev`: a left unlock `prev` lacked, for a lane `prev` still had. */
export function leaversOf(prev: View, view: View): Leaver[] {
  return view.unlocked.flatMap((u) => u.category === "left" && !prev.unlocked.some((p) => p.category === "left" && p.id === u.id)
    && prev.lanes.some((l) => l.lane === u.id) ? [{ lane: u.id, from: prev }] : []);
}

/** `view` with each leaver's lane, cards and shares put back as `from` had them: the lane where it was, its cards after
 * the others, and each mix that held one of its cards as it was. Whoever else's shares changed with it is unchanged. */
export function withLeavers(catalog: Catalog, view: View, leavers: readonly Leaver[]): View {
  if (leavers.length === 0) return view;
  const lanes = [...view.lanes];
  for (const { lane, from } of leavers) {
    const at = from.lanes.findIndex((l) => l.lane === lane);
    const bar = from.lanes[at];
    if (bar) lanes.splice(Math.min(at, lanes.length), 0, bar);
  }
  const mine = (card: string): boolean => leavers.some((l) => l.lane === catalog.laneOf(card));
  const was = new Map(leavers.flatMap((l) => l.from.mixes.map((m) => [m.id, m] as const)));
  return {
    ...view, lanes,
    cards: [...view.cards, ...leavers.flatMap((l) => l.from.cards.filter((c) => catalog.laneOf(c.card) === l.lane))],
    mixes: view.mixes.map((m) => {
      const old = was.get(m.id);
      return old && old.components.some((c) => c.kind === "card_share" && mine(c.card)) ? old : m;
    }),
  };
}
