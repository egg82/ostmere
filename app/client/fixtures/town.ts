// FIXTURE, never shipped: day three's town (CONTRACT.txt, "The town's mix") over the day-two page. The lanes, cards, mixes,
// rules and joins are the engine's own (townwire.ts, served over the wire); the content is fixtures/content.ts's, whose
// helper and mason lanes and chop, haul, hew and carve cards the wire names.
//   town:     both people joined: the helper tapping Haul by a rule (their shares yielded), the mason on shares;
//   towngrey: "town" with its card Haul retired: the engine's greyed shape applied to the captured view (the mix greyed, its
//             rule passed over, nobody running shares, the card gone from the cards);
//   townone:  the helper alone has joined; the mason's lane keeps its own row, run by its always rule.
import type { Step, View } from "../src/api/types";
import { fixtureStep, type Kept } from "./steps";
import { TOWN_WIRE } from "./townwire";

export type TownPhase = "town" | "townone" | "towngrey";
export const TOWN: readonly TownPhase[] = ["town", "townone", "towngrey"];

export function isTown(phase: string): phase is TownPhase {
  return (TOWN as readonly string[]).includes(phase);
}

/** The hands' own rules, mixes and cards stand as the day-two page has them; the wire's follow them, its rule indexes moved. */
function town(phase: TownPhase, v: View): View {
  const { joined, ...wire } = TOWN_WIRE[phase === "town" ? "two" : "one"];
  const shift = v.orders.length;
  const lanes = wire.lanes.filter((l) => l.lane !== "hands").map((l) => ({ ...l, order: l.order === null ? null : l.order + shift }));
  return {
    ...v, at: wire.at, lanes: [...v.lanes, ...lanes], cards: [...v.cards, ...wire.cards], mixes: [...v.mixes, ...wire.mixes],
    orders: [...v.orders, ...wire.orders], orders_on: [...v.orders_on, ...wire.orders_on], order_states: [...v.order_states, ...wire.order_states],
    running_town_mix_id: wire.running_town_mix_id, town_mix_order: wire.town_mix_order === null ? null : wire.town_mix_order + shift,
    unlocked: [...v.unlocked, ...joined, ...["chop", "haul", "hew", "carve"].map((id) => ({ category: "card" as const, id }))],
  };
}

function greyed(v: View): View {
  const at = v.orders.findIndex((o) => o.then.kind === "switch_mix" && o.then.mix_id === "town:main");
  return {
    ...v, running_town_mix_id: null, town_mix_order: null, greyed_mix_ids: ["town:main"],
    orders_on: v.orders_on.map((on, i) => on && i !== at), order_states: v.order_states.map((s, i) => (i === at ? "passed_over" : s)),
    cards: v.cards.filter((c) => c.card !== "haul").map((c) => ({ ...c, share_bp: 0 })),
  };
}

export function townStep(phase: TownPhase, kept: Kept = {}, decisions = 0): Step {
  const wire = TOWN_WIRE[phase === "townone" ? "one" : "two"];
  const base = fixtureStep("restrule", wire.at, { ...kept, orders: undefined }, decisions);
  const view = town(phase, base.view);
  return { ...base, view: phase === "towngrey" ? greyed(view) : view, lines: [] };
}
