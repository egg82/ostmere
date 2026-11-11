// What the rules did lately (docs/design/opening-screen.md, "Lately"; ui/rulelately.ts): the Rules tab's last block,
// from Step.rule_runs, one entry per rule the view still has, in the server's order: the rule's words, then how many
// times it came on, its last start and (once it has let go since) its last let-go, with the store's level at each and
// how long ago by the frame's clock. A chip's rule shows no levels. No entries, no block.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { Q } from "../fixtures/content";
import type { RuleRun, View } from "../src/api/types";
import { RulesTab } from "../src/ui/rules";
import { testContext } from "./context";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureStep("rulestab", 100).view;   // wood (0), warmth (1), tired (2, its mix runs), bench task (3)
const at = base.at;
const [wood, , tired] = base.orders;

function draw(view: View, runs: RuleRun[]): { tab: RulesTab; lately: () => string[] } {
  const { ctx } = testContext();
  const tab = new RulesTab({ ...ctx, ruleRuns: () => runs });
  document.body.replaceChildren(tab.root);
  tab.update(view);
  const lately = () => [...tab.root.querySelectorAll<HTMLElement>(".lately-line")].map((n) => n.textContent ?? "");
  return { tab, lately };
}

const woodRun: RuleRun = { order: wood!, starts: 4, on_at: at - 3 * 3600, on_level: 2 * Q, off_at: at - 2 * 3600, off_level: 20 * Q, ended: null, made: [] };
const tiredRun: RuleRun = { order: tired!, starts: 1, on_at: at - 65, on_level: 7 * Q, off_at: null, off_level: null, ended: null, made: [] };

// Two entries, newest first as served: the store rule with levels, the chip's rule without, still on so no let-go.
{
  const { lately } = draw(base, [tiredRun, woodRun]);
  expect("the block", lately(), [
    "Lately",
    "While tired → Rest", "ran once · came on 1 m 5 s ago",
    "Under 10 Dead wood, until 20 → Gather by hand", "ran 4 times · came on at 2 Dead wood, 3 h ago · let go at 20 Dead wood, 2 h ago",
  ]);
}

// A rule that let go in an earlier run and has come on again shows only the start; the ago follows the clock.
{
  const again: RuleRun = { ...woodRun, starts: 5, on_at: at - 10 };
  const { tab, lately } = draw(base, [again]);
  expect("on again", lately()[2], "ran 5 times · came on at 2 Dead wood, 10 s ago");
  tab.tick(at + 5);
  expect("the ago moves with the frame", lately()[2], "ran 5 times · came on at 2 Dead wood, 15 s ago");
}

// An entry for a rule the view no longer has is not drawn; with nothing to draw there is no block.
{
  const gone: RuleRun = { ...woodRun, order: { ...wood!, then: { kind: "switch_mix", mix_id: "Somewhere else" } } };
  expect("a rule the view lacks", draw(base, [gone]).lately(), []);
  expect("no entries", draw(base, []).lately(), []);
}
