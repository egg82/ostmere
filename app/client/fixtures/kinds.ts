// FIXTURE, never shipped: kinds of one card and one store, and a station lane with two tasks (#473), for screenshots.
// #kinds: the two smoke cards are kinds of one card (a picker on the Tasks page), catch and smoked fold into one ledger
// row, and "the pot" is a station whose always rule taps its first task.
import type { Card, Content, LedgerLine, Order, View } from "../src/api/types";
import { Q } from "./content";

export function withKinds(c: Content): Content {
  const pot = c.card_infos.find((x) => x.card === "gather");
  return {
    ...c,
    card_infos: [
      ...c.card_infos.map((x) => (x.card === "smoke_catch" || x.card === "smoke_roots" ? { ...x, variant_of: "smoke_catch" } : x)),
      ...(pot ? ["pot_a", "pot_b"].map((id) => ({ ...pot, card: id, lane: "pot", label_key: `card.${id}`, upside_key: `card.${id}.up`, makes: [], takes: ["roots"], replaced_by: null, glows: false })) : []),
    ],
    store_infos: c.store_infos.map((s) => (s.store === "catch" || s.store === "smoked" ? { ...s, group_key: "store.larder" } : s)),
    lane_infos: [...c.lane_infos, { lane: "pot", label_key: "lane.pot", ruled: true, station: true, later_labels: [], name_key: null, told: null, pooled: false, group: null, tied: null }],
    text_entries: [...c.text_entries, ...Object.entries({
      "store.larder": "Larder", "lane.pot": "The pot", "card.pot_a": "Root stew", "card.pot_b": "Fungus stew",
      "card.pot_a.up": "+15% work speed for anyone who eats", "card.pot_b.up": "+10% work speed for anyone who eats, at half the stew",
      ...Object.fromEntries(["ui.lesson.pot_change", "ui.lesson.pot_pick", "ui.lesson.pot_rule"].map((k) => [k, `[fixture] ${k}`])),
    }).map(([key, text]) => ({ key, text }))],
  };
}

function line(at: number, store: string, items: number, cap: number): LedgerLine {
  return { store, segment: { start: at, start_value: items * Q, rate: -60, limit: null }, net_per_hour: -60_000, contributions: [], empties_at: null, fills_at: null, falling: true, covered: true, starved: false, cap: cap * Q };   // falling and covered: drawn, white
}

export function kindsView(v: View): View {
  const like = v.cards[0];
  if (!like) return v;
  const card = (id: string, over: Partial<Card> = {}): Card => ({ ...like, card: id, completions: 0, cap: null, by: null, completes_at: null, share_bp: 0, run: null, blocker: null, needs: [], ...over });
  const always: Order = { when: { kind: "after_time", at: 0 }, then: { kind: "tap_card", card: "pot_a" }, unless: [], or_else: [], below_next: false };
  const at = v.orders.length;
  return {
    ...v,
    cards: [...v.cards.filter((c) => !["smoke_catch", "smoke_roots", "pot_a", "pot_b"].includes(c.card)), card("smoke_catch"), card("smoke_roots", { by: "tap" }), card("pot_a", { by: "tap" }), card("pot_b")],
    unlocked: [...v.unlocked, ...["smoke_catch", "smoke_roots", "pot_a", "pot_b"].map((id) => ({ category: "card" as const, id })), ...["catch", "smoked", "roots"].map((id) => ({ category: "store" as const, id }))],
    ledger: [...v.ledger.filter((l) => !["catch", "smoked", "roots"].includes(l.store)), line(v.at, "catch", 4, 6), line(v.at, "smoked", 7, 12), line(v.at, "roots", 6, 24)],
    lanes: [...v.lanes.filter((l) => l.lane !== "smoke" && l.lane !== "pot"), { lane: "smoke", running_card: "smoke_roots", completes_at: v.at + 40, order: null, own_split: null },
      { lane: "pot", running_card: "pot_a", completes_at: null, order: at, own_split: null }],
    orders: [...v.orders, always], orders_on: [...v.orders_on, true], order_states: [...v.order_states, "on"],
    order_guards: [...v.order_guards, []], order_doing: [...v.order_doing, null], order_dry: [...v.order_dry, null],
  };
}
