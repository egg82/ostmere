// The Views the front page hands the game's Scene when it has no save's own to draw: the camp at one canned moment (the
// fire lit, the stool and fireback built, stores stocked), and the camp of a game just begun. The ids are the
// opening's card and store ids; the Scene's manifest decides what they show.
import type { Card, View } from "../api/types";

const DONE: [string, number][] = [
  ["stand_up", 3], ["look_around", 1], ["clear_spot", 2], ["lay_to_dry", 1], ["ring_it", 1], ["strike_fire", 1], ["build_fireback", 1],
  ["woodcutting", 1],   // the fireback needs woodcutting level 2, so the felled birch is already down
];
const STORES: [string, number][] = [["damp_wood", 9], ["dry_wood", 4], ["stones", 1]];

/** A view holding only what a camp shows: the cards done, the stores' items, the card the hands are on. */
function campView(running: string | null, done: [string, number][], stores: [string, number][], quantityPerItem: number): View {
  const still = { start: 0, start_value: 0, rate: 0, limit: null };
  const completed = done.map(([card, completions]) => ({ card, completions }));
  const cards: Card[] = [];
  return {
    at: 0, next_event_at: null, skills: [], standing: [], cards, completed, greyed_mix_ids: [], chips: [], chips_seen: [],
    lanes: [{ lane: "hands", running_card: running, completes_at: null, order: null }],
    ledger: stores.map(([store, items]) => ({
      store, segment: { ...still, start_value: items * quantityPerItem }, net_per_hour: 0, contributions: [], empties_at: null,
      fills_at: null, falling: false, covered: true, starved: false, cap: 12 * quantityPerItem,
    })),
    unlocked: done.length > 0 ? [{ category: "feature", id: "stool" }] : [], all_covered: true, ended_at: null, mixes: [], active_mix_id: null, runs_out_at: null,
    running_mix_id: null, mix_order: null, running_town_mix_id: null, town_mix_order: null, orders_on: [], order_states: [], order_dry: [], orders: [], queue: [], offers: [], fights: [], goals: [], goal_rows: [], forecast: { horizon_at: 0, level_ups: [], tops_out: [], fills: [], empties: [] },
  };
}

export function cannedView(running: string, quantityPerItem: number): View {
  return campView(running, DONE, STORES, quantityPerItem);
}

/** The ruin and the person lying in it: the camp of a game that has not been played. */
export function emptyView(quantityPerItem: number): View {
  return campView(null, [], [], quantityPerItem);
}
