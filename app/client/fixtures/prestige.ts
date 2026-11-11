// FIXTURE, never shipped: a skill's prestige shapes (CONTRACT.txt, "PRESTIGE PHASES") with placeholder ids and words, on
// the fire's `mid` phase (the shipped game has no prestige yet). withPrestige adds a third skill and four nodes.
//   prestige:        foraging below its top, the forecast topping it out in 2 h; firecraft at its top in phase 1, six
//                    levels waiting, three nodes on its menu; carving at its top in phase 3, mastered.
//   prestigeclicked: firecraft's click landed: phase 2 at level 7, the pick still undoable.
//   prestigeowed:    firecraft's pick taken back: phase 2, a pick owed from the same menu.
//   prestigeparked:  firecraft's only pick moved: phase 2, a rank parked on the second node, back in two pushes.
//   prestigeaway:    firecraft still below its top; the next step (an advance) is `prestige`, firecraft having topped
//                    out five hours before it: the return's line.
import type { Content, MenuNode, SkillBar, SkillPrestige, Step } from "../src/api/types";
import { BP, Q, R } from "./content";
import { fixtureStep, type Kept } from "./steps";

export type PrestigePhase = "prestige" | "prestigeclicked" | "prestigeowed" | "prestigeparked" | "prestigeaway";
export const PRESTIGE_PHASES: readonly PrestigePhase[] = ["prestige", "prestigeclicked", "prestigeowed", "prestigeparked", "prestigeaway"];

export function isPrestige(phase: string): phase is PrestigePhase {
  return (PRESTIGE_PHASES as readonly string[]).includes(phase);
}

const H = 3600;
const LABELS: Record<string, string> = {
  "skill.carving": "Carving", "node.one": "First bonus", "node.two": "Second bonus", "node.three": "Third bonus",
  "node.four": "Fourth bonus",
};

/** The fixture's content with prestige on: carving, and four nodes (three on firecraft's track, one on foraging's). */
export function withPrestige(content: Content): Content {
  const node = (id: string, skill: string, change: Content["node_infos"][number]["change"]) => ({ node: id, skill, label_key: `node.${id}`, change });
  return {
    ...content,
    text_entries: [...content.text_entries, ...Object.entries(LABELS).map(([key, text]) => ({ key, text }))],
    skill_infos: [...content.skill_infos, { skill: "carving", label_key: "skill.carving", levels: [] }],
    node_infos: [
      node("one", "firecraft", { target: "cap", id: "wood", store: null }),
      node("two", "firecraft", { target: "make", id: "tend", store: "warmth" }),
      node("three", "firecraft", { target: "work", id: "gather", store: null }),
      node("four", "foraging", { target: "cap", id: "stone", store: null }),
    ],
  };
}

const MENU: MenuNode[] = [
  { node: "one", ranks_taken: 1, ranks: 5, before_value: 44 * Q, after_value: 48 * Q },
  { node: "two", ranks_taken: 0, ranks: 3, before_value: 300 * R, after_value: 330 * R },
  { node: "three", ranks_taken: 2, ranks: 4, before_value: 12 * BP / 10, after_value: 13 * BP / 10 },
];

const phase = (over: Partial<SkillPrestige>): SkillPrestige => ({
  phase: 1, level_counted: 1, at_top: false, waiting_levels: 0, menu_nodes: [], undo_open: false, mastered: false,
  pick_owed: false, topped_at: null, picked: [], parked: [], ...over,
});

const row = (at: number, skill: string, level: number, top: boolean, p: SkillPrestige): SkillBar => ({
  skill, xp: { start: at, start_value: top ? 1_000 : 150, rate: top ? 0 : 1, limit: null }, level,
  level_xp: top ? 1_000 : 100, next_level_xp: top ? null : 200, next_level_at: top ? null : at + 50, prestige: p,
});

function firecraft(at: number, state: PrestigePhase): SkillBar {
  if (state === "prestigeclicked") return row(at, "firecraft", 7, false, phase({ phase: 2, level_counted: 17, menu_nodes: MENU.map((n) => (n.node === "one" ? { ...n, ranks_taken: 2 } : n)), undo_open: true, picked: ["one"] }));
  if (state === "prestigeowed") return row(at, "firecraft", 7, false, phase({ phase: 2, level_counted: 17, menu_nodes: MENU, pick_owed: true }));
  if (state === "prestigeparked") return row(at, "firecraft", 7, false, phase({ phase: 2, level_counted: 17, menu_nodes: MENU, parked: [{ node: "two", due: 4 }] }));
  if (state === "prestigeaway") return row(at, "firecraft", 9, false, phase({ level_counted: 9, menu_nodes: MENU }));
  return row(at, "firecraft", 10, true, phase({ level_counted: 10, at_top: true, waiting_levels: 6, menu_nodes: MENU, topped_at: at - 5 * H }));
}

export function prestigeStep(state: PrestigePhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("mid", at, kept, decisions);
  const foraging = base.view.skills.find((s) => s.skill === "foraging");
  const skills: SkillBar[] = [
    ...(foraging ? [{ ...foraging, prestige: phase({ level_counted: foraging.level, menu_nodes: [{ node: "four", ranks_taken: 0, ranks: 2, before_value: 20 * Q, after_value: 22 * Q }] }) }] : []),
    firecraft(at, state),
    row(at, "carving", 10, true, phase({ phase: 3, level_counted: 30, at_top: true, mastered: true, topped_at: at - 40 * H })),
  ];
  const forecast = { ...base.view.forecast!, tops_out: [{ skill: "foraging", at: at + 2 * H + 15 * 60 }] };
  const view = { ...base.view, skills, forecast, unlocked: [...base.view.unlocked, { category: "skill" as const, id: "carving" }] };
  return { ...base, view, lines: [] };
}
