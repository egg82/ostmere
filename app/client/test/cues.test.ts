// What the page points at (game/cues.ts): the glow on a marked card once ready with its lane free, once each; an
// order card held back until its offered_after; the largest drain unless it is the hands' tap; the maker in play.
import type { Card, LedgerLine, OrderCard, View } from "../src/api/types";
import { BP, fixtureContent, Q } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import { completionsOf, glowTarget, largestDrain, nudgeTarget, offeredCard } from "../src/game/cues";

function expect(label: string, got: unknown, want: unknown): void {
  if (got !== want) throw new Error(`${label}: got ${String(got)}, want ${String(want)}`);
}

const still = { start: 0, start_value: 0, rate: 0, limit: null };
const card = (id: string, over: Partial<Card> = {}): Card => ({
  card: id, completions: 0, cap: null, bar: still, bar_total: 5 * BP, by: null, completes_at: null, share_bp: 0, run: null,
  blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 5, needs: [], ...over,
});
const blocked = { condition: { kind: "after_time" as const, at: 99 }, ready_at: 99 };
const view = (over: Partial<View> = {}): View => ({
  at: 0, next_event_at: null, ledger: [], skills: [], standing: [], lanes: [{ lane: "hands", running_card: null, completes_at: null, order: null }],
  cards: [], completed: [], greyed_mix_ids: [], chips: [], chips_seen: [], unlocked: [], all_covered: true, ended_at: null, mixes: [], active_mix_id: null,
  runs_out_at: null, running_mix_id: null, mix_order: null, running_town_mix_id: null, town_mix_order: null, orders_on: [], order_states: [], order_dry: [], orders: [], queue: [], offers: [], fights: [], goals: [], goal_rows: [],
  forecast: { horizon_at: 0, level_ups: [], tops_out: [], fills: [], empties: [] }, ...over,
});

// The glow: "stand" is the fixture's one marked card.
const catalog = new Catalog(fixtureContent);
expect("marked and ready", glowTarget(catalog, view({ cards: [card("gather"), card("stand")] }), new Set()), "stand");
expect("unmarked cards never glow", glowTarget(catalog, view({ cards: [card("gather"), card("tend")] }), new Set()), null);
expect("not while unready", glowTarget(catalog, view({ cards: [card("stand", { blocker: blocked })] }), new Set()), null);
const busy = view({ cards: [card("stand")], lanes: [{ lane: "hands", running_card: "gather", completes_at: 5, order: null }] });
expect("not while its lane is busy", glowTarget(catalog, busy, new Set()), null);
expect("while it cuts in on the busy lane", glowTarget(catalog, { ...busy, cards: [card("stand", { cuts_in: true })] }, new Set()), "stand");
expect("once each", glowTarget(catalog, view({ cards: [card("stand")] }), new Set(["stand"])), null);

// The idle nudge: the first ready, never-completed card with its lane free, until a mix runs.
expect("nudge: the first ready card", nudgeTarget(catalog, view({ cards: [card("gather"), card("tend")] })), "gather");
expect("nudge: not an unready one", nudgeTarget(catalog, view({ cards: [card("gather", { blocker: blocked }), card("tend")] })), "tend");
expect("nudge: not one done before", nudgeTarget(catalog, view({ cards: [card("gather", { completions: 1 })] })), null);
expect("nudge: not while its lane is busy", nudgeTarget(catalog, { ...busy, cards: [card("tend")] }), null);
expect("nudge: not once a mix runs", nudgeTarget(catalog, view({ cards: [card("gather")], running_mix_id: "main" })), null);

// The end of the opening: nothing affordable, the next thing a timer card more than ten minutes out: it takes the nudge
// (the screen's countdown is what the eye should land on), mix or no mix.
const timer = (at: number): Card["blocker"] => ({ condition: { kind: "after_time", at }, ready_at: at });
const away = (id: string, at: number): Card => card(id, { blocker: timer(at) });
const idle = (cards: Card[], over: Partial<View> = {}): View => view({ cards, running_mix_id: "main", ...over });
expect("timer nudge: a timer card well out", nudgeTarget(catalog, idle([away("gather", 3000)])), "gather");
expect("timer nudge: the soonest of two", nudgeTarget(catalog, idle([away("gather", 3000), away("tend", 2000)])), "tend");
expect("timer nudge: a card at its cap is not affordable", nudgeTarget(catalog, idle([away("gather", 3000), card("tend", { cap: 1, completions: 1 })])), "gather");
expect("timer nudge: not within ten minutes", nudgeTarget(catalog, idle([away("gather", 600)])), null);
expect("timer nudge: not while a card is affordable", nudgeTarget(catalog, idle([away("gather", 3000), card("tend")])), null);
expect("timer nudge: not when something else is next", nudgeTarget(catalog,
  idle([away("gather", 3000), card("tend", { blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: Q, release: Q }, ready_at: 900 } })])), null);
expect("timer nudge: measured from now", nudgeTarget(catalog, idle([away("gather", 3000)], { at: 2500 })), null);

// The order card: the fixture's wood card, once with no offered_after and once waiting on a feature.
const wood = fixtureContent.order_cards[0]!;
expect("offered with no offered_after", offeredCard(catalog, view(), "wood"), wood);
const waiting: OrderCard = { ...wood, offered_after: { category: "feature", id: "mix" } };
const later = new Catalog({ ...fixtureContent, order_cards: [waiting] });
expect("held back before its unlock", offeredCard(later, view(), "wood"), undefined);
expect("offered once unlocked", offeredCard(later, view({ unlocked: [{ category: "feature", id: "mix" }] }), "wood"), waiting);

// The largest drain, unless it is the hands' tap.
const line: LedgerLine = {
  store: "wood", segment: still, net_per_hour: -9, contributions: [{ runner: "gather", per_hour: 3 }, { runner: "tend", per_hour: -2 },
    { runner: "shelter", per_hour: -10 }], empties_at: 10, fills_at: null, falling: true, covered: false, starved: false, cap: 40 * Q,
};
expect("the largest drain", largestDrain(line, view()), "shelter");
const tapping = view({ lanes: [{ lane: "hands", running_card: "shelter", completes_at: 5, order: null }] });
expect("not the hands' tap", largestDrain(line, tapping), null);
expect("nothing draws", largestDrain({ ...line, contributions: [{ runner: "gather", per_hour: 3 }] }, view()), null);

// A step's completions.
const done = view({ cards: [card("gather", { completions: 2 })], completed: [{ card: "stand", completions: 3 }] });
expect("completions in play", completionsOf(done, "gather"), 2);
expect("completions done", completionsOf(done, "stand"), 3);
expect("completions of a card in neither", completionsOf(done, "tend"), 0);
