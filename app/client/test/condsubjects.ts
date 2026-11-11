// What a save holds that a condition can watch and see change (the wire's Subject union), read off a View, and the saves
// to read it from: every fixture phase, the fresh save included. Shared by condsubjects.test.ts and condeditor's tests.
import { PHASES, fixtureStep, type Phase } from "../fixtures/steps";
import type { Subject, View } from "../src/api/types";

const OTHER_PHASES: readonly Phase[] = ["ruled", "offered", "bank", "answered", "whenready", "queued", "rising", "night", "morning", "returned",
  "landed", "fight", "fightlater", "fightmany", "fightnew", "fightfirst", "town", "townone", "towngrey", "prestige", "prestigeclicked", "prestigeowed",
  "prestigeaway", "journal", "journallesson", "journaldays", "journalall", "trip", "tripmix"];

export const SAVES: readonly { phase: Phase; view: View }[] = [...PHASES, ...OTHER_PHASES].map((phase) => ({ phase, view: fixtureStep(phase, 1_000).view }));

export type Kind = Subject["kind"];

/** `kind:id` of a subject, one string per thing a rule could watch. */
export function keyOf(s: Subject): string {
  switch (s.kind) {
    case "store_value": return `store_value:${s.store}`;
    case "skill_level": return `skill_level:${s.skill}`;
    case "card_count": return `card_count:${s.card}`;
    case "unlocked": return `unlocked:${s.unlock.category}/${s.unlock.id}`;
    case "running": return `running:${s.runner}`;
  }
}

/** The kinds a rule is offered. Unlocked is not one: unlocks only grow, so a condition on one the save holds is always
 * true, and one on an unlock it does not hold would name what the story has not shown yet. Nor is Running: set_orders
 * refuses it (api/convert.py, `_page_built`: an order on what its own mix stops flips at every instant). */
export const KINDS: readonly Kind[] = ["store_value", "card_count", "skill_level"];

/** Every subject of KINDS the save holds whose value can still move: a store per ledger line, a skill per bar, a card
 * count per card in play (a done card's count is final). */
export function present(view: View): Subject[] {
  return [
    ...view.ledger.map((l): Subject => ({ kind: "store_value", store: l.store })),
    ...view.skills.map((s): Subject => ({ kind: "skill_level", skill: s.skill })),
    ...view.cards.map((c): Subject => ({ kind: "card_count", card: c.card })),
  ];
}

/** The saved subjects of `kind` the offered ones leave out, as keys. */
export function missing(view: View, offered: readonly Subject[], kind: Kind): string[] {
  const have = new Set(offered.map(keyOf));
  return present(view).filter((s) => s.kind === kind).map(keyOf).filter((k) => !have.has(k));
}
