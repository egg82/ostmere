// FIXTURE, never shipped: hand-built Steps in the shape of models.py, each drawn at a given `at` so the page's clock
// and sampling run against them. Phases: start (one narrative card), standing (that card being tapped), firstmix (the
// first-mix offer), mid (a running mix, a bench lane, crafts, a red ledger line, a chip, the Camp bar, and the end
// feature already unlocked, so the end must wait), covered (the wood rule set: every line white, so the end comes: ended_at is that step's time),
// orderlist (covered plus a second hands rule and a bench task rule), rulemix (orderlist with the warmth rule on, so its
// mix runs over the player's), written (rules the player wrote: an old wood rule with no band, a warmth rule on
// "reaches" whose mix runs, and a saved mix no rule runs), redrule (mid with the wood rule set and its line still red),
// away (the first-mix screen; any later step lands in mid with no decision, so a reload or a return brings several
// things at once), restoffer (covered, the end ten minutes back, tired, no rule on energy: the strip's rest offer is
// due once the end is behind), restrule (restoffer with the rest rule set and on: Rest runs "while tired"),
// restaway (restoffer before its chips came; any later step lands in restoffer with no decision, a return mid-reveal),
// rulestab (restrule with three hands rules, the tired one on, and the bench task rule: the Rules tab full),
// ruleoffer (mid, for the rule lesson: the first set_orders moves it to ruleon), ruleon (the rules the page set, all at work),
// capfull (full with the bench's stone rule set, so this game's Rules tab is drawn: the cap rule's lesson may start),
// drystore (a one-card mix of stool stopped on dry wood, gather in play and not in it: the dry store's lesson may start),
// fullpause (dry's shape, but the mix's first card stopped because wood, which it fills, is full: Card.full_store).
import type { Card, LedgerLine, LogLine, Mix, Need, Order, OrderState, QueueEntry, RuleRun, Step, View } from "../src/api/types";
import { BP, fixtureContent, Q, R, TIRED } from "./content";
import type { DayOnePhase } from "./dayone";
import type { DayTwoPhase } from "./daytwo";
import type { FightsPhase } from "./fights";
import type { ChroniclePhase } from "./chronicle";
import type { SincePhase } from "./since";
import type { AsksPhase } from "./asks";
import type { LedgerPhase } from "./ledgerrules";
import type { GuardsPhase } from "./guards";
import type { FeelPhase } from "./feel";
import type { JournalPhase } from "./journal";
import type { PrestigePhase } from "./prestige";
import type { GroupsPhase } from "./groups";
import type { TownPhase } from "./town";

export type Phase = "start" | "standing" | "mid" | "covered" | "firstmix" | "greyed" | "full" | "capfull" | "orderlist" | "rulemix" | "written" | "redrule" | "away"
  | "restoffer" | "restrule" | "restaway" | "rulestab" | "ruleoffer" | "ruleon" | "repeattap" | "repeatswitch" | "alone" | "aloneDone" | "dry" | "drystore" | "fullpause" | "trip" | "tripmix" | "goals" | "goalsearly" | "held" | "heldstint" | DayOnePhase | DayTwoPhase | FightsPhase | JournalPhase | TownPhase | GroupsPhase | PrestigePhase | ChroniclePhase | SincePhase | AsksPhase | LedgerPhase | GuardsPhase | FeelPhase;

export const PHASES: readonly Phase[] = ["start", "standing", "mid", "covered", "firstmix", "greyed", "full", "capfull", "orderlist", "rulemix", "written", "redrule", "away",
  "restoffer", "restrule", "restaway", "rulestab", "ruleoffer", "ruleon", "repeattap", "repeatswitch", "alone", "aloneDone", "dry", "drystore"];

/** What the fixture API keeps from the decisions it was sent: the player's main mix, other saved mixes, the rules. */
export interface Kept {
  mix?: Mix;
  extra?: Mix[];
  orders?: Order[];
  queue?: QueueEntry[];
  /** Answers given, as "offer:answer" (asks.ts). */
  answered?: string[];
}

const solo = (id: string, card: string): Mix => ({ id, components: [{ kind: "card_share", card, share_bp: BP }] });
const GATHER = solo("Gather by hand", "gather");
const REST = solo("Rest by the fire", "tend");
const low = (store: string, value: number, release: number): Order["when"] =>
  ({ kind: "at_most", watched: { kind: "store_value", store }, value: value * Q, release: release * Q, value_of_cap: false, release_of_cap: false });
const WOOD_RULE: Order = { when: low("wood", 10, 20), then: { kind: "switch_mix", mix_id: GATHER.id }, unless: [], or_else: [], below_next: false };
const WARMTH_RULE: Order = { when: low("warmth", 40, 60), then: { kind: "switch_mix", mix_id: REST.id }, unless: [], or_else: [], below_next: false };
const SHELTER_RULE: Order = { when: low("stone", 2, 6), then: { kind: "tap_card", card: "shelter" }, unless: [], or_else: [], below_next: false };
const OLD_WOOD_RULE: Order = { when: low("wood", 10, 10), then: { kind: "switch_mix", mix_id: GATHER.id }, unless: [], or_else: [], below_next: false };
const WARM_RULE: Order = {
  when: { kind: "at_least", watched: { kind: "store_value", store: "warmth" }, value: 80 * Q, release: 40 * Q, value_of_cap: false, release_of_cap: false },
  then: { kind: "switch_mix", mix_id: REST.id }, unless: [], or_else: [], below_next: false,
};
const REST_MIX = solo("Rest", "rest");
const STOOLS = solo("Stools", "stool");
const TIRED_RULE: Order = { when: TIRED, then: { kind: "switch_mix", mix_id: REST_MIX.id }, unless: [], or_else: [], below_next: false };
/** The end, this long before a rest phase's view: an older end, so a fresh page never replays its card. */
const ENDED_AGO = 600;
const EVENING: Mix = { id: "Evening", components: [{ kind: "card_share", card: "gather", share_bp: 5_000 }, { kind: "card_share", card: "tend", share_bp: 5_000 }] };

const MIX: Mix = {
  id: "Morning <b>fire</b> & wood",
  components: [
    { kind: "card_share", card: "gather", share_bp: 6_000 },
    { kind: "card_share", card: "tend", share_bp: 4_000 },
  ],
};

function lines(at: number, ...keys: string[]): LogLine[] {
  return keys.map((key, seq) => ({ at, seq, key, card: null, opens_beat: false }));
}

const still = (at: number, value = 0) => ({ start: at, start_value: value, rate: 0, limit: null });

function card(at: number, id: string, over: Partial<Card> = {}): Card {
  return {
    card: id, completions: 0, cap: null, bar: still(at), bar_total: 5 * BP, by: null, completes_at: null, share_bp: 0, run: null,
    blocker: null, cuts_in: false, spent_store: null, full_store: null, gained: [], crew: null, tap_s: 5, speed: BP, needs: [], ...over,
  };
}

const freeHands = { lane: "hands", running_card: null, completes_at: null, order: null, own_split: null };

function base(at: number): View {
  return {
    at, next_event_at: null, ledger: [], skills: [], standing: [], lanes: [freeHands],
    cards: [card(at, "stand", { cap: 3 })], completed: [], greyed_mix_ids: [],
    chips: [], chips_seen: [], unlocked: [{ category: "card", id: "stand" }], all_covered: true, ended_at: null, mixes: [], active_mix_id: null, runs_out_at: null,
    running_mix_id: null, mix_order: null, running_town_mix_id: null, town_mix_order: null, orders_on: [], order_states: [], order_guards: [], order_doing: [], order_dry: [], orders: [], queue: [], offers: [], fights: [], goals: [], goal_rows: [], store_rows: [], levels: [], forecast: { horizon_at: at + 6 * 3600, level_ups: [], tops_out: [], fills: [], empties: [] },
  };
}

function standing(at: number): View {
  return {
    ...base(at),
    next_event_at: at + 6,
    cards: [card(at, "stand", { cap: 3, completions: 1, by: "tap", bar: { start: at, start_value: 0, rate: BP, limit: 6 * BP }, bar_total: 6 * BP, completes_at: at + 6 })],
    lanes: [{ lane: "hands", running_card: "stand", completes_at: at + 6, order: null, own_split: null }],
  };
}

function store(at: number, id: string, items: number, perHour: number, cap: number, covered: boolean): LedgerLine {
  const rate = perHour * R;
  const value = items * Q;
  return {
    store: id, segment: { start: at, start_value: value, rate, limit: rate < 0 ? 0 : rate > 0 ? cap * Q : null },
    net_per_hour: rate, contributions: rate > 0 ? [{ runner: "gather", per_hour: rate }] : [{ runner: "tend", per_hour: rate }],
    empties_at: rate < 0 ? at + Math.ceil(value / -rate) : null,
    fills_at: rate > 0 ? at + Math.ceil((cap * Q - value) / rate) : null,
    falling: rate < 0, covered, starved: false, cap: cap * Q,
  };
}

/** A card's need of `items` from a store holding `has` items, flat. */
function need(at: number, s: string, items: number, has: number): Need {
  return { store: s, quantity: items * Q, segment: still(at, has * Q), gate: null, makers: [], spent: false };
}

function firstMix(at: number): View {
  return {
    ...base(at),
    cards: [card(at, "gather"), card(at, "tend")],
    completed: [{ card: "stand", completions: 3 }],
    unlocked: [{ category: "feature", id: "mix" }, { category: "card", id: "gather" }, { category: "card", id: "tend" }],
  };
}

function mid(at: number, mix: Mix, covered: boolean, plan: Plan): View {
  const runs = plan.mixes.find((m) => m.id === plan.running) ?? mix;
  const shareOf = (id: string) => runs.components.find((c) => c.kind === "card_share" && c.card === id)?.share_bp ?? 0;
  const mixed = (id: string, s: number): Card => card(at, id, { share_bp: shareOf(id), run: "full", by: "mix", bar: { start: at, start_value: 0, rate: Math.round((BP * shareOf(id)) / BP), limit: null }, bar_total: s * BP });
  return {
    at, next_event_at: at + 12,
    ledger: [store(at, "wood", 14, -120, 40, covered), store(at, "warmth", 38, 300, 100, false), store(at, "stone", 3, 0, 20, false), store(at, "camp", 80, 600, 1000, false)],
    skills: [
      { skill: "foraging", xp: { start: at, start_value: 130, rate: 1, limit: null }, level: 2, level_xp: 100, next_level_xp: 200, next_level_at: at + 70, prestige: null },
      { skill: "firecraft", xp: { start: at, start_value: 40, rate: 1, limit: null }, level: 1, level_xp: 0, next_level_xp: 100, next_level_at: at + 60, prestige: null },
    ],
    standing: [],
    lanes: [freeHands, { lane: "bench", running_card: "shelter", completes_at: at + 12, order: null, own_split: null }],
    cards: [
      card(at, "look", { blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store: "stone" }, value: 4 * Q, release: 4 * Q, value_of_cap: false, release_of_cap: false }, ready_at: null }, needs: [need(at, "stone", 4, 3)] }),
      mixed("gather", 5),
      mixed("tend", 7),
      card(at, "hatchet", { blocker: { condition: { kind: "at_least", watched: { kind: "skill_level", skill: "foraging" }, value: 3, release: 3, value_of_cap: false, release_of_cap: false }, ready_at: null }, needs: [need(at, "wood", 2, 14)], tap_s: 30 }),
      card(at, "stool", { needs: [need(at, "wood", 3, 14)], tap_s: 25, cap: 1 }),
      card(at, "shelter", { by: "tap", bar: { start: at, start_value: 8 * BP, rate: BP, limit: 20 * BP }, bar_total: 20 * BP, completes_at: at + 12, cap: 3, completions: 1 }),
    ],
    completed: [{ card: "stand", completions: 3 }],
    greyed_mix_ids: [],
    chips: covered ? ["warm"] : ["cold"],
    chips_seen: covered ? ["cold", "warm"] : ["cold"],
    unlocked: [
      { category: "feature", id: "mix" }, { category: "store", id: "wood" }, { category: "store", id: "camp" },
      { category: "store", id: "warmth" }, { category: "store", id: "stone" },
      { category: "skill", id: "foraging" }, { category: "skill", id: "firecraft" },
      { category: "feature", id: "leave_it_running" },   // the end feature: the end waits for all_covered
      { category: "feature", id: "ledger" },
    ],
    all_covered: covered, ended_at: covered ? at : null, mixes: [mix, ...plan.mixes.filter((m) => m.id !== mix.id)], active_mix_id: mix.id,
    runs_out_at: covered ? null : at + 5_400, running_mix_id: plan.running ?? mix.id, mix_order: plan.order, running_town_mix_id: null, town_mix_order: null,
    orders_on: plan.on, order_states: statesOf(plan), order_guards: plan.orders.map(() => []), order_doing: plan.orders.map(() => null), order_dry: [], orders: plan.orders, queue: [], offers: [], fights: [], goals: [], goal_rows: [], store_rows: [], levels: [],
    // foraging's next level lands as its bar says; firecraft's is pushed back by the rule that takes the hands first
    forecast: { horizon_at: at + 6 * 3600, level_ups: [{ skill: "foraging", at: at + 70 }, { skill: "firecraft", at: at + 1_500 }], tops_out: [], fills: [{ store: "warmth", at: at + 744 }], empties: [{ store: "wood", at: at + 420 }] },
  };
}

/** The rules in play: the orders, which are on, and the mix a rule runs (none: the player's own runs). */
interface Plan {
  orders: Order[];
  on: boolean[];
  mixes: Mix[];
  running: string | null;
  order: number | null;
}

/** Where each rule stands, as the server says it: off while its condition does not hold, outranked while another
 * rule's mix runs. No fixture plan holds a greyed mix's rule. */
function statesOf(plan: Plan): OrderState[] {
  return plan.orders.map((o, i) => (!plan.on[i] ? "waiting" : o.then.kind === "switch_mix" && plan.order !== i ? "outranked" : "on"));
}

function planOf(phase: Phase, kept: Kept): Plan {
  const extra = kept.extra ?? [];
  const known = (ms: Mix[]) => [...ms, ...extra.filter((e) => !ms.some((m) => m.id === e.id))];
  if (phase === "restrule") {   // the tired rule on, whether the fixture's or the one the page just set
    const orders = kept.orders ?? [WOOD_RULE, TIRED_RULE];
    const i = orders.findIndex((o) => JSON.stringify(o.when) === JSON.stringify(TIRED));
    const then = orders[i]?.then;
    return { orders, on: orders.map((_, j) => j === i), mixes: known([GATHER, REST_MIX]), running: then?.kind === "switch_mix" ? then.mix_id : null, order: i >= 0 ? i : null };
  }
  if (phase === "ruleon") {   // the rule the page just set (the rule lesson's offer), at work
    const orders = kept.orders ?? [];
    return { orders, on: orders.map(() => true), mixes: known([GATHER, REST]), running: null, order: null };
  }
  if (phase === "rulestab") {
    const orders = kept.orders ?? [WOOD_RULE, WARMTH_RULE, TIRED_RULE, SHELTER_RULE];
    const i = orders.findIndex((o) => JSON.stringify(o.when) === JSON.stringify(TIRED));
    const then = orders[i]?.then;
    return { orders, on: orders.map((o, j) => j === i || o.then.kind === "tap_card"), mixes: known([GATHER, REST, REST_MIX]), running: then?.kind === "switch_mix" ? then.mix_id : null, order: i >= 0 ? i : null };
  }
  if (kept.orders) return { orders: kept.orders, on: kept.orders.map(() => false), mixes: known([GATHER, REST]), running: null, order: null };
  if (phase === "covered") return { orders: [WOOD_RULE], on: [false], mixes: known([GATHER]), running: null, order: null };
  if (phase === "capfull") return { orders: [SHELTER_RULE], on: [false], mixes: known([]), running: null, order: null };
  if (phase === "orderlist") return { orders: [WOOD_RULE, WARMTH_RULE, SHELTER_RULE], on: [false, false, true], mixes: known([GATHER, REST]), running: null, order: null };
  if (phase === "written") return { orders: [OLD_WOOD_RULE, WARM_RULE, SHELTER_RULE], on: [false, true, true], mixes: known([GATHER, REST, EVENING]), running: REST.id, order: 1 };
  if (phase === "redrule") return { orders: [WOOD_RULE], on: [false], mixes: known([GATHER]), running: null, order: null };
  if (phase === "restoffer" || phase === "restaway") return { orders: [WOOD_RULE], on: [false], mixes: known([GATHER]), running: null, order: null };
  if (phase === "rulemix") return { orders: [WOOD_RULE, WARMTH_RULE, SHELTER_RULE], on: [false, true, true], mixes: known([GATHER, REST]), running: REST.id, order: 1 };
  return { orders: [], on: [], mixes: known([]), running: null, order: null };
}

/** trip: the hands are out on far_hunt, an uncapped trip, tapped; tripmix: the mix gives it a quarter of the hands' time,
 * taken from gather's share. Its bar and work_s are the page's to draw, so they are a long trip's (an hour at full speed). */
function tripVariant(phase: Phase, view: View, at: number): View {
  const work = 3600;
  const tapped = phase === "trip";
  const trip = card(at, "far_hunt", {
    by: tapped ? "tap" : "mix", share_bp: tapped ? BP : 2500, run: tapped ? null : "full", tap_s: work, bar_total: work * BP,
    bar: { start: at, start_value: 0, rate: tapped ? BP : 2500, limit: work * BP }, completes_at: tapped ? at + work : null,
  });
  const cards = tapped ? view.cards : view.cards.map((c) => (c.card === "gather" && c.share_bp >= 2500 ? { ...c, share_bp: c.share_bp - 2500 } : c));
  return {
    ...view, cards: [...cards, trip], unlocked: [...view.unlocked, { category: "card", id: "far_hunt" }],
    lanes: view.lanes.map((l) => (tapped && l.lane === "hands" ? { ...l, running_card: "far_hunt", completes_at: at + work } : l)),
  };
}

/** drystore: the running mix is stool alone, stopped on wood, which ran dry with nothing covering it; gather makes wood
 * and is in play, outside the mix, so its time has nowhere to go. far_hunt is in play so the strip's Edit has come. */
function dryStore(view: View, at: number): View {
  const wood = { ...store(at, "wood", 0, 0, 40, false), contributions: [], starved: true };
  const cards = view.cards.map((c): Card => {
    if (c.card === "stool") return { ...c, share_bp: BP, run: "paused", by: null, needs: [{ ...need(at, "wood", 3, 0), makers: ["gather"] }] };
    if (c.card === "gather" || c.card === "tend") return { ...c, share_bp: 0, run: null, by: null, bar: still(at) };
    return c;
  });
  return { ...view, cards: [...cards, card(at, "far_hunt", { needs: [need(at, "wood", 2, 0)] })], unlocked: [...view.unlocked, { category: "card", id: "far_hunt" }], ledger: view.ledger.map((l) => (l.store === "wood" ? wood : l)), mixes: [...view.mixes, STOOLS], active_mix_id: STOOLS.id, running_mix_id: STOOLS.id, all_covered: false };
}

/** When held lands: the step a held phase taps runs this long from Begin. */
const HELD_S = 8;

/** held: a When ready step of stool runs on the hands over the player's Rest mix until HELD_S, then lands and the mix
 * returns; heldstint: a goal stint runs Gather by hand over the player's Rest mix until wood reaches 30. */
function heldVariant(phase: Phase, view: View, at: number): View {
  const solo = (c: Card, mix: Mix): Card => {
    const first = mix.components[0];
    const mine = first?.kind === "card_share" && first.card === c.card;
    return c.card === "gather" || c.card === "tend" ? { ...c, share_bp: mine ? BP : 0, run: mine ? "full" : null, by: mine ? "mix" : null } : c;
  };
  if (phase === "heldstint") {
    const until = { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "wood" }, value: 30 * Q, release: 30 * Q, value_of_cap: false, release_of_cap: false };
    return { ...view, cards: view.cards.map((c) => solo(c, GATHER)), mixes: [REST, GATHER], active_mix_id: REST.id, running_mix_id: GATHER.id,
      queue: [{ verb: { kind: "switch_mix", mix_id: GATHER.id }, until }],
      goal_rows: [{ kind: "store", store: "wood", skill: null, target: 30 * Q, lands_at: at + 2 * 3600, per_hour: 60_000, limit: null, until }] };
  }
  const resting = { ...view, cards: view.cards.map((c) => solo(c, REST)), mixes: [REST], active_mix_id: REST.id, running_mix_id: REST.id };
  if (at >= HELD_S) return { ...resting, cards: resting.cards.filter((c) => c.card !== "stool"), completed: [...resting.completed, { card: "stool", completions: 1 }] };
  const once = { kind: "at_least" as const, watched: { kind: "card_count" as const, card: "stool" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false };
  return {
    ...resting, next_event_at: HELD_S,
    lanes: resting.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: "stool", completes_at: HELD_S } : l)),
    queue: [{ verb: { kind: "tap_card", card: "stool" }, until: once }],
    cards: resting.cards.map((c) => (c.card === "stool" ? { ...c, by: "tap" as const, completes_at: HELD_S, bar: { start: at, start_value: at * BP, rate: BP, limit: HELD_S * BP }, bar_total: HELD_S * BP }
      : c.by === "mix" ? { ...c, run: "yielded" as const, completes_at: null } : c)),
  };
}

/** greyed: the running mix holds a retired card; full: the wood store is at its cap with a maker still feeding it. */
function variant(phase: Phase, view: View, at: number): View {
  if (phase === "greyed" && view.active_mix_id !== null) {
    return {
      ...view, greyed_mix_ids: [view.active_mix_id], cards: view.cards.filter((c) => c.card !== "tend"),
      unlocked: [...view.unlocked, { category: "retired", id: "tend" }],
    };
  }
  if (phase === "dry" || phase === "fullpause") {   // the mix's first card paused on a dry store, or a full one (CONTRACT.txt, "FULL OUTPUT"), its share run by the rest
    const [stop, ...rest] = view.cards.filter((c) => c.share_bp > 0);
    const total = rest.reduce((n, c) => n + c.share_bp, 0);
    const gain = (c: Card): number => (stop && total > 0 ? Math.floor((stop.share_bp * c.share_bp) / total) : 0);
    const full = phase === "fullpause" ? "wood" : null;
    const ledger = full === null ? view.ledger : view.ledger.map((l) => (l.store === full ? store(at, full, 40, 0, 40, true) : l));
    return { ...view, ledger, cards: view.cards.map((c) => (c === stop ? { ...c, run: "paused" as const, by: null, full_store: full }
      : rest.includes(c) ? { ...c, gained: stop ? [{ card: stop.card, share_bp: gain(c) }] : [] } : c)) };
  }
  if (phase === "drystore") return dryStore(view, at);
  if (phase === "held" || phase === "heldstint") return heldVariant(phase, view, at);
  if (phase === "full" || phase === "capfull") return { ...view, ledger: view.ledger.map((l) => (l.store === "wood" ? store(at, "wood", 40, 300, 40, false) : l)) };
  if (phase === "trip" || phase === "tripmix") return tripVariant(phase, view, at);
  if (phase === "goals") return { ...view, goals: [   // a story beat's marks: a card, a line, a skill row; and the wait line (game/story.ts)
    { kind: "card", store: null, card: "look", skill: null, target: 1, value: null, at: null, feeds: [] },
    { kind: "store", store: "wood", card: null, skill: null, target: 30 * Q, value: { start: at, start_value: 14 * Q, rate: 0, limit: null }, at: null, feeds: [] },
    { kind: "level", store: null, card: null, skill: "foraging", target: 3, value: null, at: null, feeds: [] },
    { kind: "clock", store: null, card: null, skill: null, target: 0, value: null, at: at + 2 * 3600 + 10 * 60, feeds: ["wood"] }] };
  if (phase === "restoffer" || phase === "restrule" || phase === "restaway" || phase === "rulestab") {
    const tired = phase !== "restaway";
    const resting = phase === "restrule" || phase === "rulestab";
    return {
      ...view, ended_at: at - ENDED_AGO, chips: tired ? [...view.chips, "tired"] : [], chips_seen: tired ? [...view.chips_seen, "tired"] : view.chips_seen,   // restaway: the return brings two chips, so the offer waits a turn
      cards: [...view.cards, card(at, "rest", { share_bp: resting ? BP : 0, run: resting ? "full" : null, by: resting ? "mix" : null })],
      unlocked: [...view.unlocked, { category: "card", id: "rest" }, ...(tired ? [{ category: "chip" as const, id: "tired" }] : [])],
    };
  }
  return view;
}

export function fixtureStep(phase: Phase, at: number, kept: Kept = {}, decisions = 0): Step {
  const mix = kept.mix ?? MIX;
  const covered = phase === "covered" || phase === "orderlist" || phase === "rulemix" || phase === "written" || phase === "restoffer" || phase === "restrule" || phase === "restaway" || phase === "rulestab";
  const view = phase === "goalsearly" ? { ...standing(at), goals: [   // a store with no line yet, and the wait stopped on a dry store
    { kind: "store" as const, store: "stone", card: null, skill: null, target: 3 * Q, value: { start: at, start_value: Q, rate: 0, limit: null }, at: null, feeds: [] },
    { kind: "clock" as const, store: null, card: null, skill: null, target: 0, value: null, at: null, feeds: ["wood"] }] }
    : phase === "aloneDone" ? { ...base(at), cards: [], completed: [{ card: "stand", completions: 1 }] } : phase === "firstmix" || phase === "away" ? firstMix(at) : phase === "start" || phase === "alone" ? base(at) : phase === "standing" ? standing(at) : variant(phase, mid(at, mix, covered, planOf(phase, kept)), at);
  // mid's first line is written by the first card ("stand"): on that card when the player's tap of it led here
  const midLines = lines(at, "line.3", "line.4").map((l, i) => (i === 0 ? { ...l, card: "stand" } : l));
  const said = phase === "aloneDone" ? lines(at, "line.3").map((l) => ({ ...l, card: "stand" })) : phase === "start" ? lines(at, "line.1", "line.2") : phase === "mid" || phase === "greyed" || phase === "full" ? midLines : covered ? lines(at, "line.5") : [];
  // repeattap, repeatswitch: mid, with a card tapped by hand again and again, or a switch made again and again while cold
  const repeats = phase === "repeattap" ? { taps: [{ card: "look", count: 5 }], switches: [] }
    : phase === "repeatswitch" ? { taps: [], switches: [{ chip: "cold", mix_id: mix.id, count: 3 }] } : { taps: [], switches: [] };
  return { save_id: 1, decisions, rules_digest: fixtureContent.rules_digest, build: "fixture", view, lines: said, failed_tap: null, repeats, rule_runs: ruleRuns(phase, view), catching_up_to: null, journal_days: [] };
}

/** rulestab: what its rules did lately, the tired rule on a minute ago, the wood rule's last full run before it, and a
 * goal stint that popped four hours ago. */
function ruleRuns(phase: Phase, view: View): RuleRun[] {
  if (phase !== "rulestab") return [];
  const [wood, , tired] = view.orders;
  if (!wood || !tired) return [];
  return [{ order: tired, starts: 1, on_at: view.at - 65, on_level: 7 * Q, off_at: null, off_level: null, ended: null, made: [] },
    { order: wood, starts: 4, on_at: view.at - 3 * 3600, on_level: 2 * Q, off_at: view.at - 2 * 3600, off_level: 20 * Q, ended: null, made: [] },
    { order: STINT_ORDER, starts: 1, on_at: view.at - 55 * 3600, on_level: null, off_at: view.at - 4 * 3600, off_level: null, ended: "stint",
      made: [{ store: "wood", quantity: 140 * Q }, { store: "stone", quantity: 12 * Q }] }];
}

/** rulestab's popped goal stint: gather until 30 wood. */
const STINT_ORDER: Order = { when: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 30 * Q, release: 30 * Q, value_of_cap: false, release_of_cap: false },
  then: { kind: "switch_mix", mix_id: GATHER.id }, unless: [], or_else: [], below_next: false };
