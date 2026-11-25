// FIXTURE, never shipped: a camp with groups (CONTRACT.txt, "GROUPS"), as the engine serves it (no content uses groups yet).
// On day three's town (townwire.ts: helper and mason, split in town:main) four people run their own split, helper, mason, smith
// and scribe, and a pooled lane, crew ("Workers"), holds the split of its two members, nan and ole, whose marks are off:
// dig 60% and sweep 30% of each member's time, served as totals over the crew of two. Each member also has a one-off of their own.
// withGroups adds the lanes, cards and words to the content; groupsStep is the view.
import type { Content, Step, View } from "../src/api/types";
import { fixtureContent } from "./content";
import { townStep } from "./town";

export type GroupsPhase = "groups";
export const GROUPS: readonly GroupsPhase[] = ["groups"];

export function isGroups(phase: string): phase is GroupsPhase {
  return (GROUPS as readonly string[]).includes(phase);
}

const LABELS: Record<string, string> = {
  "lane.smith": "Smith", "lane.scribe": "Scribe", "lane.nan": "Nan", "lane.ole": "Ole", "lane.crew": "Workers",
  "card.forge": "Forge tools", "card.copy": "Copy pages", "card.dig": "Dig ditches", "card.sweep": "Sweep paths", "card.errand_n": "Run an errand", "card.errand_o": "Fetch a load",
};

const LANES: { lane: string; group: string | null; pooled: boolean }[] = [
  { lane: "smith", group: null, pooled: false }, { lane: "scribe", group: null, pooled: false },
  { lane: "nan", group: "crew", pooled: false }, { lane: "ole", group: "crew", pooled: false }, { lane: "crew", group: null, pooled: true },
];

const CARDS: { card: string; lane: string }[] = [
  { card: "forge", lane: "smith" }, { card: "copy", lane: "scribe" }, { card: "dig", lane: "crew" }, { card: "sweep", lane: "crew" },
  { card: "errand_n", lane: "nan" }, { card: "errand_o", lane: "ole" },
];

/** The fixture's content with the four marked people's lanes, the group's, its two members' and their cards. */
export function withGroups(content: Content = fixtureContent): Content {
  const chop = content.card_infos.find((c) => c.card === "chop") as Content["card_infos"][number];
  return {
    ...content,
    text_entries: [...content.text_entries, ...Object.entries(LABELS).map(([key, text]) => ({ key, text }))],
    lane_infos: [...content.lane_infos, ...LANES.map((l) => ({ lane: l.lane, label_key: `lane.${l.lane}`, ruled: true, station: false, later_labels: [], name_key: null, told: l.pooled ? null : ("mention" as const), pooled: l.pooled, group: l.group, tied: l.lane === "crew" ? "nan" : null }))],
    card_infos: [...content.card_infos, ...CARDS.map((c) => ({ ...chop, card: c.card, lane: c.lane, label_key: `card.${c.card}` }))],
  };
}

const SPLIT = { forge: 5000, copy: 4000, dig: 6000, sweep: 3000 };

/** The groups view: the town's, with the new lanes joined, the crew's free members counted (`crew`, 2 when both are free). */
export function groupsView(crew = 2): View {
  const base = townStep("town").view;
  const chop = base.cards.find((c) => c.card === "chop") as View["cards"][number];
  const card = (id: string, share: number, patch: Partial<View["cards"][number]> = {}): View["cards"][number] =>
    ({ ...chop, card: id, share_bp: share, run: "full", by: "mix", completions: 0, ...patch });
  const total = (bp: number): number => bp * Math.max(crew, 1);
  const cards = [
    card("forge", SPLIT.forge), card("copy", SPLIT.copy),
    card("dig", total(SPLIT.dig), { crew }), card("sweep", total(SPLIT.sweep), { crew }),
    card("errand_n", 0, { cap: 1, by: null, run: "yielded" }), card("errand_o", 0, { cap: 1, by: null, run: "yielded" }),
  ];
  const mix = base.mixes.find((m) => m.id === "town:main") as View["mixes"][number];
  const shared = { ...mix, components: [...mix.components, ...Object.entries(SPLIT).map(([id, bp]) => ({ kind: "card_share" as const, card: id, share_bp: bp }))] };
  const bar = (lane: string, own_split: boolean | null) => ({ lane, running_card: null, completes_at: null, order: null, own_split });
  return {
    ...base,
    lanes: [...base.lanes, bar("smith", true), bar("scribe", true), bar("nan", false), bar("ole", false), bar("crew", null)],
    cards: [...base.cards, ...cards],
    mixes: base.mixes.map((m) => (m.id === "town:main" ? shared : m)),
    unlocked: [...base.unlocked, ...["smith", "scribe", "nan", "ole"].map((id) => ({ category: "joined" as const, id })), ...CARDS.map((c) => ({ category: "card" as const, id: c.card }))],
  };
}

export function groupsStep(): Step {
  const base = townStep("town");
  return { ...base, view: groupsView() };
}
