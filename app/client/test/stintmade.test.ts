// What an ended stint made, in Lately's facts (ui/stintlately.ts; CONTRACT.txt, "RULE RUNS", "Made"): the made fact
// comes last, after how long the stint ran and when its goal landed: one gain, two, none, whole items rounded down.
import { Catalog } from "../src/game/catalog";
import { fixtureContent, Q } from "../fixtures/content";
import type { RuleRun } from "../src/api/types";
import { stintFacts } from "../src/ui/stintlately";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

type Amount = RuleRun["made"][number];
const H = 3600;
const catalog = new Catalog(fixtureContent);
const now = 1_000_000;
const run = (made: Amount[], on: number | null = now - 6 * H): RuleRun => ({
  order: { when: { kind: "at_least", watched: { kind: "skill_level", skill: "k" }, value: 2, release: 2 }, then: { kind: "switch_mix", mix_id: "b" } },
  starts: on === null ? 0 : 1, on_at: on, on_level: null, off_at: now - 4 * H, off_level: null, ended: "stint", made,
});
const facts = (made: Amount[], on: number | null = now - 6 * H): string => stintFacts(catalog, run(made, on), now);

expect("nothing made", facts([]), "ran 2 h · goal landed 4 h ago");
expect("one gain", facts([{ store: "wood", quantity: 12 * Q }]), "ran 2 h · goal landed 4 h ago · made 12 Dead wood");
expect("two gains", facts([{ store: "wood", quantity: 12 * Q }, { store: "stone", quantity: 3 * Q }]),
  "ran 2 h · goal landed 4 h ago · made 12 Dead wood and 3 Flint");
expect("whole items rounded down", facts([{ store: "wood", quantity: 5 * Q + Math.floor(Q * 0.9) }, { store: "stone", quantity: 2 * Q + 1 }]),
  "ran 2 h · goal landed 4 h ago · made 5 Dead wood and 2 Flint");
expect("made after the landing, with no start seen", facts([{ store: "stone", quantity: 7 * Q }], null), "goal landed 4 h ago · made 7 Flint");
