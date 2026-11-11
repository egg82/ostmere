// FIXTURE, never shipped: day one's phases (content/team/day-one.md's shapes, with the fixture's placeholder ids),
// built on the rest rule's ended camp (steps.ts, restrule): the end long behind, a mix running, the rules set.
//   whenready: two builds in view, the larder waiting on flint the mix makes (a ready time: When ready, with the glow)
//              and the lean-to on wood nothing makes now (no ready time); queued: the larder in the queue (Next, the
//              strip's note, the card's "in Next"); rising: the smoke lane open, catch rising (its rule offered) and
//              Take stock waiting on smoked and roots; night and morning: the night after the end (its first step, waiting on the night's clock,
//              counting down; the clock lesson), then the morning (the scene's grades); returned: the morning before a planned moment, which lands while the page is shut
//              or hidden (landed: its lines, played in turn on the return, and its feature).
import type { Card, LedgerLine, LogLine, QueueEntry, Step, View } from "../src/api/types";
import { BP, Q, R } from "./content";
import { fixtureStep, type Kept } from "./steps";

export type DayOnePhase = "whenready" | "queued" | "rising" | "night" | "morning" | "returned" | "landed";
export const DAY_ONE: readonly DayOnePhase[] = ["whenready", "queued", "rising", "night", "morning", "returned", "landed"];

export function isDayOne(phase: string): phase is DayOnePhase {
  return (DAY_ONE as readonly string[]).includes(phase);
}

const still = (at: number, value = 0) => ({ start: at, start_value: value, rate: 0, limit: null });

function card(at: number, id: string, over: Partial<Card> = {}): Card {
  return {
    card: id, completions: 0, cap: 1, bar: still(at), bar_total: 20 * BP, by: null, completes_at: null, share_bp: 0, run: null,
    blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20, needs: [], ...over,
  };
}

/** A card short of `store`: has `have` of `need` items, ready at `readyAt` (null: not by itself). */
function short(at: number, id: string, store: string, need: number, have: number, readyAt: number | null, over: Partial<Card> = {}): Card {
  const watched = { kind: "store_value" as const, store };
  return card(at, id, {
    blocker: { condition: { kind: "at_least", watched, value: need * Q, release: need * Q }, ready_at: readyAt },
    needs: [{ store, quantity: need * Q, segment: { start: at, start_value: have * Q, rate: readyAt === null ? 0 : Math.ceil(((need - have) * Q) / (readyAt - at)), limit: null }, gate: null, makers: [], spent: false }],
    ...over,
  });
}

function line(at: number, store: string, items: number, perHour: number, cap: number): LedgerLine {
  const rate = perHour * R;
  return {
    store, segment: { start: at, start_value: items * Q, rate, limit: rate > 0 ? cap * Q : rate < 0 ? 0 : null }, net_per_hour: rate,
    contributions: [{ runner: "smoke_catch", per_hour: rate }], empties_at: null, fills_at: rate > 0 ? at + Math.ceil(((cap - items) * Q) / rate) : null,
    falling: rate < 0, covered: false, starved: false, cap: cap * Q,
  };
}

const queued = (id: string): QueueEntry => ({ verb: { kind: "tap_card", card: id }, until: { kind: "at_least", watched: { kind: "card_count", card: id }, value: 1, release: 1 } });
const feature = (id: string) => ({ category: "feature" as const, id });

function builds(at: number, view: View, queue: QueueEntry[]): View {
  return {
    ...view, queue,
    cards: [...view.cards, short(at, "larder", "stone", 12, 3, at + 540), short(at, "lean_to", "wood", 10, 2, null)],
    unlocked: [...view.unlocked, { category: "card", id: "larder" }, { category: "card", id: "lean_to" }, feature("morning")],
  };
}

function rising(at: number, view: View): View {
  return {
    ...view,
    ledger: [...view.ledger, line(at, "catch", 2, 3, 6), line(at, "smoked", 2, 0, 12), line(at, "roots", 6, 0, 24)],
    lanes: [...view.lanes, { lane: "smoke", running_card: null, completes_at: null, order: null }],
    cards: [...view.cards, card(at, "smoke_catch", { cap: null }), card(at, "smoke_roots", { cap: null }),
      short(at, "take_stock", "smoked", 6, 2, null, { needs: [{ store: "smoked", quantity: 6 * Q, segment: still(at, 2 * Q), gate: null, makers: ["smoke_catch", "smoke_roots"], spent: false }, { store: "roots", quantity: 15 * Q, segment: still(at, 6 * Q), gate: null, makers: [], spent: false }] })],
    unlocked: [...view.unlocked, { category: "card", id: "smoke_catch" }, { category: "card", id: "smoke_roots" }, { category: "store", id: "catch" },
      { category: "store", id: "smoked" }, { category: "store", id: "roots" }, feature("morning")],   // the ledger lists only unlocked stores
  };
}

/** The lines of a moment that landed while the page was shut, played in turn on the return. */
function returnLines(at: number): LogLine[] {
  return ["line.1", "line.2", "line.4"].map((key, seq) => ({ at: at - 600, seq, key, card: null }));
}

export function dayOneStep(phase: DayOnePhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("restrule", at, kept, decisions);
  const v = base.view;
  const queue = kept.queue ?? (phase === "queued" ? [queued("larder")] : []);
  const view = phase === "whenready" || phase === "queued" ? builds(at, v, queue)
    : phase === "rising" ? rising(at, v)
      : phase === "night" ? { ...v, cards: [...v.cards, short(at, "look_out", "night", 20, 1, at + 3400, { tap_s: null })], unlocked: [...v.unlocked, feature("night")] }
        : phase === "morning" || phase === "returned" ? { ...v, unlocked: [...v.unlocked, feature("night"), feature("morning")] }
          : { ...v, unlocked: [...v.unlocked, feature("night"), feature("morning"), feature("prints")] };
  return { ...base, view, lines: phase === "landed" ? returnLines(at) : [] };
}
