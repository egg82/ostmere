// FIXTURE, never shipped: the fights shapes (CONTRACT.txt, "FIGHTS"), with placeholder ids, built on the fire's `mid`
// phase (the shipped game has no fights yet).
//   fight:   the `combat` feature on; one fight card (Hunt the ridge, 2 in 5 lost; yours 8 against 9, with gear and
//            a skill behind the 8) and one standing fight (raiders at the stores, 7.5% lost, 31 fought and 2 lost).
//   fightnew, fightfirst: the same fights with none fought yet, and with one fought (odds unknown, then served).
//   fightlater: the same fights 5 and 1 fights later (a window the arrival queue writes entries for), then a long one.
import type { Fight, Step, Strength, View } from "../src/api/types";
import { fixtureStep, type Kept } from "./steps";

export type FightsPhase = "fight" | "fightlater" | "fightmany" | "fightnew" | "fightfirst";
export const FIGHTS: readonly FightsPhase[] = ["fight", "fightlater", "fightmany", "fightnew", "fightfirst"];

export function isFights(phase: string): phase is FightsPhase {
  return (FIGHTS as readonly string[]).includes(phase);
}

const power: Strength = {
  value: 8, sources: [
    { source: null, form: "base", amount_bp: 6, share_bp: null }, { source: "hatchet", form: "add_bp", amount_bp: 5000, share_bp: null },
    { source: "foraging", form: "add_bp", amount_bp: 2500, share_bp: null }, { source: "stool", form: "add_bp", amount_bp: 1250, share_bp: 5000 },
    { source: "cold", form: "mul_bp", amount_bp: 8000, share_bp: null },
  ],
};
const wolves: Strength = { value: 9, sources: [{ source: null, form: "base", amount_bp: 9, share_bp: null }] };
const raiders: Strength = { value: 40, sources: [{ source: null, form: "base", amount_bp: 20, share_bp: null }, { source: "dusk_ramp", form: "mul_bp", amount_bp: 20000, share_bp: null }] };

/** Both fights at a fixed fought count (none lost) when `only` is given, else at their usual counts plus `extra`. */
function fights(extra: number, lostExtra: number, only?: number): Fight[] {
  if (only !== undefined) return fights(0, 0).map((f) => ({ ...f, fought: only, lost: 0 }));
  return [
    { runner: "hunt", side: "hands", threat: "wolves", power, threat_strength: wolves, loss_bp: 4000, fought: 4 + extra, lost: 1 + lostExtra },
    { runner: "raiders", side: "hands", threat: "raiders", power, threat_strength: raiders, loss_bp: 750, fought: 31 + extra, lost: 2 + lostExtra },
  ];
}

export function fightsStep(phase: FightsPhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("mid", at, kept, decisions);
  const extra = phase === "fight" ? 0 : phase === "fightlater" ? 3 : 40;
  const view: View = {
    ...base.view, fights: fights(extra, phase === "fight" ? 0 : phase === "fightlater" ? 1 : 5, phase === "fightnew" ? 0 : phase === "fightfirst" ? 1 : undefined),
    cards: [...base.view.cards, { ...base.view.cards[0], card: "hunt", completions: 0, cap: null, by: null, tap_s: 5, bar_total: 5 * 10_000 } as View["cards"][number]],
    unlocked: [...base.view.unlocked, { category: "card", id: "hunt" }, { category: "feature", id: "combat" }],
  };
  return { ...base, view, lines: [] };
}
