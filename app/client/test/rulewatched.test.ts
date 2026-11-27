// A new store rule on a phone (issue 467; ui/condition/conditiondraft.ts keepOffered, ui/condition/condstore.ts): a task picked on a rule with
// no condition yet starts on the first store it makes, as a tap on that store would, so Rules, + New rule, the task and
// Add rule is the whole rule (4 taps, from 6); and the foot shows the watched store as it stands (held / cap, net per
// minute, where it heads) over the sentence while the levels are set. A chip's rule shows no number.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { RulesTab } from "../src/ui/rules/rules";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const base = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const wood = base.ledger.find((l) => l.store === "wood");
if (!wood) throw new Error("fixture: no wood ledger line");
const view: View = { ...base, store_rows: [{ store: "wood", per_hour: -60 * fixtureContent.scales.rate_per_item_hour, heading: "empties", at: base.at + 600, mixed: false }] };

const { ctx, got } = testContext(undefined, catalog);
ctx.keeps.keepRuleSeen();
const tab = new RulesTab(ctx);
document.body.replaceChildren(tab.root);
const root = fakeDocument.body.firstElementChild as FakeEl;
tab.update(view);
root.querySelector(".rules-new")?.click();
const cond = root.querySelector(".cond") as FakeEl;
const watched = (): FakeEl => cond.querySelector(".cond-watched") as FakeEl;
const add = (): FakeEl => cond.querySelector(".cond-actions .primary") as FakeEl;

expect("control: nothing chosen, nothing watched, Add rule off", [watched().hidden, add().disabled], [true, true]);
cond.querySelector('.cond-task[data-card="gather"]')?.click();   // gather makes wood
expect("the task's store is chosen with it", cond.querySelectorAll(".cond-store").filter((b) => b.getAttribute("aria-pressed") === "true").map((b) => b.dataset.store), ["wood"]);
const held = catalog.format.amount(wood.segment.start_value, wood.cap);
expect("the foot shows wood as it stands", [watched().hidden, watched().textContent], [false, `${catalog.storeTitle("wood")} · ${held} · ${catalog.format.perMinute(-60 * fixtureContent.scales.rate_per_item_hour)} · ${catalog.text.fill("ui.ledger.empties", { d: catalog.format.duration(600) })}`]);
expect("Add rule is on", add().disabled, false);
add().click();
const sent = got.decided.find((d): d is Extract<Decision, { kind: "set_orders" }> => d.kind === "set_orders");
const when = sent?.orders.at(-1)?.when;
expect("the rule watches wood, made more as it runs low", when && when.kind !== "after_time" ? [when.kind, when.watched] : when, ["at_most", { kind: "store_value", store: "wood" }]);
