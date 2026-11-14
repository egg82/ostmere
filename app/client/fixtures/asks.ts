// FIXTURE, never shipped: the Asks list (CONTRACT.txt, "OFFERS"), on day two's bank phase (daytwo.ts). asksone: the
// bank offer open alone, with every optional field; asksmany: all three fixture offers open, the bare one shown first and
// "2 more" behind it. An answer the page sends is kept (the ask leaves the list), and a dry run of one shows what it
// moves: hers the wood's rate and Rest's time, his the wood's cap, keep Rest's time.
import type { Offer, Step, View } from "../src/api/types";
import { dayTwoStep } from "./daytwo";
import type { Kept } from "./steps";

export type AsksPhase = "asksone" | "asksmany";
export const isAsks = (phase: string): phase is AsksPhase => phase === "asksone" || phase === "asksmany";

const open = (offer: string, takes: Record<string, [string | null, number | null]>): Offer => ({
  offer, answer: null, answers: Object.entries(takes).map(([answer, [card, takes_s]]) => ({ answer, card, takes_s })),
});
const ASK = open("ask", { wait: [null, null], go: ["haul", 750] });
const BANK = open("bank", { hers: [null, null], his: [null, null] });
const TRADE = open("trade", { keep: [null, null], swap: [null, null] });

/** What a given answer moves, as the engine's view would show it after. */
function moved(view: View, answer: string): View {
  const rest = (s: number): View["cards"] => view.cards.map((c) => (c.card === "rest" ? { ...c, tap_s: s } : c));
  if (answer === "bank:hers") return { ...view, ledger: view.ledger.map((l) => (l.store === "wood" ? { ...l, net_per_hour: Math.trunc(l.net_per_hour * 0.9) } : l)), cards: rest(4) };
  if (answer === "bank:his") return { ...view, ledger: view.ledger.map((l) => (l.store === "wood" ? { ...l, cap: Math.trunc(l.cap * 1.25) } : l)) };
  if (answer === "trade:keep") return { ...view, cards: rest(4) };
  return view;
}

export function asksStep(phase: AsksPhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = dayTwoStep("bank", at, kept, decisions);
  const given = kept.answered ?? [];
  const answer = (o: Offer): Offer => ({ ...o, answer: given.find((g) => g.startsWith(`${o.offer}:`))?.split(":")[1] ?? null });
  const offers = (phase === "asksone" ? [BANK] : [ASK, BANK, TRADE]).map(answer);
  const view = given.reduce(moved, { ...base.view, offers });
  return { ...base, view, lines: [] };
}
