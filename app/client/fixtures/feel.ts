// FIXTURE, never shipped: the feel (docs/design/redesign.md, "Feel") on the mid phase. Each tap of a card lands a
// completion of Gather by hand; every odd tap also levels Foraging 2 → 3, which speeds Gather up by a tenth (a level on
// its card), and covers the red wood line (it settles), so the step is a chain of four links; an even tap puts both
// back, a lone landing. For screenshots of the press, the level on its card and a cascade, and the 4K check's cascade.
import type { Step, View } from "../src/api/types";
import { BP } from "./content";
import { fixtureStep, type Kept } from "./steps";

export type FeelPhase = "feel";
export const isFeel = (phase: string): phase is FeelPhase => phase === "feel";

export function feelStep(at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("mid", at, kept, decisions);
  const odd = decisions % 2 === 1;
  const view: View = {
    ...base.view,
    skills: base.view.skills.map((s) => (s.skill === "foraging" ? { ...s, level: odd ? 3 : 2 } : s)),
    cards: base.view.cards.map((c) => (c.card === "gather" ? { ...c, completions: c.completions + decisions, speed: odd ? (BP * 11) / 10 : BP } : c)),
    ledger: base.view.ledger.map((l) => (l.store === "wood" ? { ...l, covered: odd } : l)),
  };
  return { ...base, view, lines: [] };
}
