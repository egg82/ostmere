// The condition editor's simple view and the mixes' door (docs/design/opening-screen.md, "The condition editor", "The
// hands strip", "The Mixes list"): a chip's rule written in two taps from the task that answers it; a task chosen
// clears a condition it does not answer; More options keeps the full editor's choices one tap away; the strip's way
// into the mixes reads "Mixes", the name beside it as text; the Mixes list says which mix runs and which it would run.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, TIRED } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, View } from "../src/api/types";
import { doChoices, whenChoices } from "../src/game/ruleoffers";
import { Hands } from "../src/ui/hands";
import { RulesTab } from "../src/ui/rules";
import { MixSelector } from "../src/ui/selector";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const offer = fixtureStep("restoffer", 100).view;   // tired, the rest task in play, no rule on energy, no Rest mix saved

/** A context whose player has seen a rule come on and let go: writing rules is open. */
function context(): { ctx: ReturnType<typeof testContext>["ctx"]; decided: Decision[] } {
  const { ctx, got } = testContext();
  ctx.keeps.keepRuleSeen();
  return { ctx, decided: got.decided };
}
const { catalog } = context().ctx;

const q = (root: ParentNode, sel: string): HTMLButtonElement[] => Array.from(root.querySelectorAll<HTMLButtonElement>(sel));
const one = (root: ParentNode, sel: string): HTMLButtonElement => {
  const found = q(root, sel)[0];
  if (!found) throw new Error(`no ${sel}`);
  return found;
};

function newRule(view: View): { cond: HTMLElement; decided: Decision[] } {
  const { ctx, decided } = context();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  one(tab.root, ".rules-new").click();
  return { cond: one(tab.root, ".cond"), decided };
}

// "Rest while tired" from scratch: the task, then the chip it answers; the rule reads as the chip and saves the
// chip's own condition, the task as a mix of itself alone.
{
  const { cond, decided } = newRule(offer);
  expect("simple: the heading names a new rule", one(cond, ".cond-heading").textContent, "New rule");
  expect("More options is offered", one(cond, ".cond-more").hidden, false);
  one(cond, ".cond-task[data-card=\"rest\"]").click();
  expect("the rest task answers tired: the chip is offered, no store", q(cond, ".cond-stores button").map((b) => b.dataset.chip ?? b.dataset.store), ["tired"]);
  one(cond, ".cond-chip[data-chip=\"tired\"]").click();
  expect("the sentence reads as the chip", one(cond, ".cond-sentence").textContent, "While tired → Rest");
  expect("no number shown for the chip", /\d/.test(one(cond, ".cond-sentence").textContent ?? ""), false);
  one(cond, ".cond-actions .primary").click();
  expect("saved: the task's solo mix, then the rule on the chip's condition", decided.map((d) => d.kind), ["save_mix", "set_orders"]);
  const set = decided[1];
  const added = set?.kind === "set_orders" ? set.orders.at(-1) : undefined;
  expect("the chip's condition, running that mix", added, { when: TIRED, then: { kind: "switch_mix", mix_id: "Rest" } });
}

// A task chosen after another clears a condition it does not answer; More options offers every chip and store.
{
  const { cond } = newRule(offer);
  one(cond, ".cond-task[data-card=\"rest\"]").click();
  one(cond, ".cond-chip[data-chip=\"tired\"]").click();
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  expect("gather does not answer tired: nothing pressed in When", q(cond, ".cond-stores button").filter((b) => b.getAttribute("aria-pressed") === "true").length, 0);
  expect("and Add rule is off", one(cond, ".cond-actions .primary").disabled, true);
  one(cond, ".cond-more").click();
  expect("More options: gone once open", one(cond, ".cond-more").hidden, true);
  const full = whenChoices(catalog, offer, true, null, null);
  expect("full: every chip a task in play answers, then every store", q(cond, ".cond-stores .cond-store").map((b) => b.dataset.chip ?? b.dataset.store),
    [...full.chips.map((c) => c.chip), ...full.stores]);
}

// The offers themselves: a saved solo mix is its task, offered once; the simple view offers no mixes.
{
  const simple = doChoices(catalog, offer, false, null);
  expect("simple: tasks only", simple.every((c) => c.kind === "task"), true);
  const full = doChoices(catalog, offer, true, null);
  expect("full: the gather mix shows as the gather task, not twice", full.filter((c) => (c.kind === "mix" && c.mix === "Gather by hand") || (c.kind === "task" && c.card === "gather")),
    [{ kind: "task", card: "gather" }]);
  expect("a store too small for a band is never offered", whenChoices(catalog, offer, true, null, null).stores.every((s) => (catalog.stores.get(s)?.cap ?? 0) >= 2 * fixtureContent.scales.quantity_per_item), true);
}

// The strip's way into the mixes says what it is; the name is plain text beside it.
{
  const mid = fixtureStep("mid", 100).view;
  const hands = new Hands(context().ctx);
  const root = hands.root;
  document.body.replaceChildren(root);
  hands.update(mid);
  expect("the door reads Mixes", one(root, ".hands-meta .hands-name").textContent, "Mixes ▾");
  expect("the running mix's name, as text", one(root, ".hands-meta .hands-mix-name").textContent, mid.running_mix_id);
}

// The Mixes list: the running mix says so; another runnable mix says Run.
{
  const tab = fixtureStep("rulestab", 100).view;
  const sel = new MixSelector(context().ctx);
  sel.show(tab);
  const root = sel.root;
  const notes = Object.fromEntries(q(root, ".selector-row").map((row) => [one(row, ".selector-name").textContent, one(row, ".selector-note").textContent]));
  expect("running, Run, and none on the default under a rule", notes, { [tab.active_mix_id!]: "", "Gather by hand": "Run", "Rest by the fire": "Run", Rest: "running" });
}
