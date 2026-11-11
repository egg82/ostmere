// Next's Plan and a popped stint in Lately (ui/stintplan.ts, ui/stintlately.ts; CONTRACT.txt, "Goal stints", "Rule runs"):
// Plan lists the saved mixes, then the goals the picked mix would run to, and the pick queues the stint; an ended stint
// reads as its mix and goal with how long it ran and when its goal landed.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { fixtureContent, Q } from "../fixtures/content";
import type { GoalRow, Mix, RuleRun, View } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";
import { StintPlan } from "../src/ui/stintplan";
import { keepsOf } from "./kept";
import { TAUGHT, testContext } from "./context";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const R = fixtureContent.scales.rate_per_item_hour;
const H = 3600;
const base = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const woodUntil = { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "wood" }, value: 30 * Q, release: 30 * Q };
const wood = (lands: number): GoalRow => ({ kind: "store", store: "wood", skill: null, target: 30 * Q, lands_at: lands, per_hour: 60 * R, limit: null, until: woodUntil });
const mix = (id: string): Mix => ({ id, components: [] });
const planning = (over: Partial<View>): View => ({ ...base, mixes: [mix("a"), mix("b"), mix("town:camp")], active_mix_id: "a", running_mix_id: "a", greyed_mix_ids: [], queue: [], ...over });

async function plan(view: View, after: View | null, seeRules = true) {
  const { ctx, got } = testContext();
  const c = { ...ctx, keeps: keepsOf({ ...TAUGHT, rule_seen: seeRules }), actions: { ...ctx.actions, dryRun: () => Promise.resolve(after) } };
  let rows: HTMLElement[] = [];
  const p: StintPlan = new StintPlan(c, () => { rows = p.rows(view); });
  rows = p.rows(view);
  return { got, p, rows: () => rows };
}

{
  const { rows } = await plan(planning({}), null, false);
  expect("closed to a player who has not met rules", rows(), []);
  const none = await plan(planning({ mixes: [mix("a")], greyed_mix_ids: ["a"] }), null);
  expect("no mix to run", none.rows(), []);
  const full = await plan(planning({ queue: Array.from({ length: fixtureContent.limits.max_queue }, () => ({ verb: { kind: "switch_mix" as const, mix_id: "a" }, until: woodUntil })) }), null);
  expect("a full Next offers nothing", full.rows(), []);
}

// Plan, a mix, a goal: the dry run of switching to a mix that does not run now lists the goals; the pick queues the stint
{
  const view = planning({});
  const after = { ...view, running_mix_id: "b", goal_rows: [wood(base.at + 2 * H)] };
  const { rows, got } = await plan(view, after);
  expect("the button", rows().map((r) => r.textContent), ["+ Plan"]);
  rows()[0]?.click();
  expect("the saved mixes", rows().map((r) => r.textContent), ["Plan✕", "a", "b"]);
  rows()[2]?.click();
  await Promise.resolve();
  await Promise.resolve();
  expect("the mix named, its goals listed", rows().map((r) => r.textContent), ["b until…✕", "Dead wood 302 h"]);
  rows()[1]?.querySelector<HTMLElement>(".stint-goal")?.click();
  expect("queued at the end", got.decided, [{ kind: "set_queue", entries: [{ verb: { kind: "switch_mix", mix_id: "b" }, until: woodUntil }] }]);
  expect("closed again", rows().map((r) => r.textContent), ["+ Plan"]);
}

// A mix that already runs lists the live goals, no dry run
{
  const view = planning({ goal_rows: [wood(base.at + H)] });
  const { rows } = await plan(view, null);
  rows()[0]?.click();
  rows()[1]?.click();
  expect("the live view's goals", rows().map((r) => r.textContent), ["a until…✕", "Dead wood 301 h"]);
}

// Lately: an ended stint reads as its mix and goal, then what it ran and when its goal landed; one never seen starting only the landing
{
  const at = base.at;
  const run = (on: number | null): RuleRun => ({ order: { when: woodUntil, then: { kind: "switch_mix", mix_id: "b" } }, starts: on === null ? 0 : 1,
    on_at: on, on_level: null, off_at: at - 4 * H, off_level: null, ended: "stint", made: [] });
  const lately = (runs: RuleRun[]): string[] => {
    const tab = new RulesTab({ ...testContext().ctx, ruleRuns: () => runs });
    document.body.replaceChildren(tab.root);
    tab.update(planning({}));
    return [...tab.root.querySelectorAll<HTMLElement>(".lately-line")].map((n) => n.textContent ?? "");
  };
  expect("ran and landed", lately([run(at - 52 * H - 4 * H)]), ["Lately", "b until Dead wood 30", "ran 2 d 4 h · goal landed 4 h ago"]);
  expect("start unseen", lately([run(null)]), ["Lately", "b until Dead wood 30", "goal landed 4 h ago"]);
}
