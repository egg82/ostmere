// FIXTURE, never shipped: the fights shapes (CONTRACT.txt, "FIGHTS"), with placeholder ids, built on the fire's `mid`
// phase (the shipped game has no fights yet).
//   fight:   the `combat` feature on; one fight card (Hunt the ridge, 2 in 5 lost; yours 8 against 9, with gear and
//            a skill behind the 8) and one standing fight (raiders at the stores, 7.5% lost, 31 fought and 2 lost).
//   fightnew, fightfirst: the same fights with none fought yet, and with one fought (odds unknown, then served).
//            A poultice drains the hurt the hunt wounds, which is at 0: its tap starts all the same.
//   fighthurt: the fight phase with 1.5 hurt (the chip and its level), under withHurtChip's content.
//   fightlater: the same fights 5 and 1 fights later (a window the arrival queue writes entries for), then a long one.
import type { Card, ChipInfo, Content, Fight, Need, Step, Strength, View } from "../src/api/types";
import { Q } from "./content";
import { fixtureStep, type Kept } from "./steps";

export type FightsPhase = "fight" | "fightlater" | "fightmany" | "fightnew" | "fightfirst" | "fighthurt";
export const FIGHTS: readonly FightsPhase[] = ["fight", "fightlater", "fightmany", "fightnew", "fightfirst", "fighthurt"];

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

/** A poultice with its roots in hand and nothing hurt: ready, a drain asking nothing. */
function poultice(card: Card, at: number): Card {
  const need = (store: string, quantity: number, has: number): Need => ({
    store, quantity, segment: { start: at, start_value: has, rate: 0, limit: null }, gate: null, makers: [], spent: false,
  });
  return {
    ...card, card: "poultice", completions: 0, cap: null, by: null, run: null, share_bp: 0, tap_s: 60, bar_total: 60 * 10_000,
    blocker: null, needs: [need("roots", 6 * Q, 20 * Q)],
  };
}

/** The content with the hurt chip, which shows from a quarter hurt (the shipped chip's `when`). */
export function withHurtChip(content: Content): Content {
  const when = { kind: "at_least", watched: { kind: "store_value", store: "hurt" }, value: Q / 4, release: Q / 4, value_of_cap: false, release_of_cap: false } as const;
  const chip: ChipInfo = { chip: "hurt", label_key: "chip.hurt", tone: "hurt", when, cost_key: null, change_bp: [], on_line_key: null, off_line_key: null, offered_after: null, chore: false };
  return { ...content, chip_infos: [...content.chip_infos, chip], text_entries: [...content.text_entries, { key: "chip.hurt", text: "hurt" }] };
}

export function fightsStep(phase: FightsPhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("mid", at, kept, decisions);
  const extra = phase === "fight" ? 0 : phase === "fightlater" ? 3 : 40;
  const view: View = {
    ...base.view, fights: fights(extra, phase === "fight" ? 0 : phase === "fightlater" ? 1 : 5, phase === "fightnew" ? 0 : phase === "fightfirst" ? 1 : undefined),
    cards: [...base.view.cards, { ...base.view.cards[0], card: "hunt", completions: 0, cap: null, by: null, tap_s: 5, bar_total: 5 * 10_000 } as View["cards"][number],
      poultice(base.view.cards[0]!, at)],
    unlocked: [...base.view.unlocked, { category: "card", id: "hunt" }, { category: "card", id: "poultice" }, { category: "feature", id: "combat" }],
  };
  if (phase !== "fighthurt") return { ...base, view, lines: [] };
  const hurt = 1.5 * Q;
  return { ...base, view: { ...view, chips: [...view.chips, "hurt"], chips_seen: [...view.chips_seen, "hurt"], levels: [{ store: "hurt", segment: { start: at, start_value: hurt, rate: 0, limit: null } }] }, lines: [] };
}
