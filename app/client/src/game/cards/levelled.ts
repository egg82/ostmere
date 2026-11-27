// A level shown on the card it speeds up (docs/design/redesign.md, "Feel"; contract/, "Skills"), read from two
// views and the content alone: the cards a level passed names in LevelPays.speeds whose Card.speed rose, with one whole
// completion's time at each speed. Pure.
import type { View } from "../../api/types";
import type { Catalog } from "../page/catalog";
import { shownLevel } from "../skills/prestige";

export interface Speedup {
  card: string;
  skill: string;
  /** The level reached (the one counted across phases). */
  level: number;
  beforeS: number;
  afterS: number;
}

export function speedups(catalog: Catalog, prev: View, view: View): Speedup[] {
  const out: Speedup[] = [];
  for (const bar of view.skills) {
    const was = prev.skills.find((s) => s.skill === bar.skill);
    if (!was) continue;
    const from = shownLevel(was), to = shownLevel(bar);
    const named = new Set((catalog.skills.get(bar.skill)?.levels ?? []).filter((l) => l.level > from && l.level <= to).flatMap((l) => l.speeds));
    for (const card of named) {
      const old = prev.cards.find((c) => c.card === card), now = view.cards.find((c) => c.card === card);
      if (!old || !now || old.speed <= 0 || now.speed <= old.speed || out.some((s) => s.card === card)) continue;
      out.push({ card, skill: bar.skill, level: to, beforeS: old.bar_total / old.speed, afterS: now.bar_total / now.speed });
    }
  }
  return out;
}
