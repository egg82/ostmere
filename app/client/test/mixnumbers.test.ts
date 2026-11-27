// The Mixes list shows each saved mix's own numbers, separately, and the player's earlier best for a goal with the mix
// that set it, worded "earlier" and never as a verdict (contract/mix-rows.txt, "Mix rows"; ui/mixes/selector.ts).
import { fakeDocument, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { GoalRow, MixRows } from "../src/api/types";
import type { PartContext } from "../src/ui/part";
import { MixSelector } from "../src/ui/mixes/selector";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const view = fixtureStep("rulestab", 100).view;
const goal: GoalRow = {
  kind: "store", store: "wood", skill: null, target: 20_000, lands_at: view.at + 3600, per_hour: 40_000, limit: null,
  until: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 20_000, release: 20_000 } as GoalRow["until"],
};
const own = view.mixes.filter((m) => !m.id.startsWith("town:"));
const [a, b] = [own[0]!, own[1]!];
const key = `${goal.kind}|${goal.store}||${goal.target}`;
const numbers: MixRows = {
  at: view.at,
  rows: [a, b].map((m, i) => ({
    id: m.id, runs_out_at: null, nets: [{ store: "wood", per_hour: goal.per_hour + i * 600 }],
    goals: [{ ...goal, lands_at: view.at + 3600 * (i + 1) }],
  })),
  best: [{ goal: key, mix_id: a.id, lands_at: view.at + 1800, saved_at: view.at - 60 }],
};
const { ctx } = testContext();
ctx.actions.mixRows = () => Promise.resolve(numbers);
const list = new MixSelector(ctx as PartContext);
list.show(view);
await new Promise((r) => setTimeout(r, 0));
document.body.replaceChildren(list.root);
const rowOf = (id: string) => Array.from(fakeDocument.body.querySelectorAll(".selector-row")).find((r) => r.querySelector(".selector-name")?.textContent === id)!;
const goalsOf = (id: string) => Array.from(rowOf(id).querySelectorAll(".mix-goal"), (n) => n.textContent);
expect("two saved mixes show a goal line each", [goalsOf(a.id).length, goalsOf(b.id).length], [1, 1]);
expect("on separate numbers", goalsOf(a.id)[0] !== goalsOf(b.id)[0], true);
const earlier = (id: string) => Array.from(rowOf(id).querySelectorAll(".goal-binds"), (n) => n.textContent ?? "").filter((t) => t.startsWith("earlier"));
expect("the kept best names the mix that set it", earlier(a.id).every((t) => t.includes(a.id)) && earlier(a.id).length === 1, true);
expect("under each mix, since the goal is the same", earlier(b.id).length, 1);
expect("worded earlier, never as a verdict", /best|better|worse|optimal/i.test(fakeDocument.body.textContent ?? ""), false);
