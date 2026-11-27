// From a person's page, the way to a rule that watches another lane's task running: "+ New rule" on the page opens the
// condition editor for that person (the Rules tab's New rule, scoped to their lane), whose full view's When row offers
// "while <task> is running" for a person's task, and offers none for a hands rule or when the rule's task is on the
// watched card's own lane (contract/endpoints.txt, "Decisions": the one Running shape set_orders takes).
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { Decision } from "../src/api/types";
import { LaneRows } from "../src/ui/town/lanerows";
import { RulesTab } from "../src/ui/rules/rules";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const view = townStep("town").view;

{  // the page's New rule opens the Rules tab on a new rule for that person
  const { ctx, got } = testContext();
  const rows = new LaneRows(ctx);
  document.body.replaceChildren(rows.root, rows.page.root);
  rows.update(view);
  (fakeDocument.body.firstElementChild as FakeEl).querySelectorAll(".person-change")[0]!.click();
  const page = fakeDocument.body.children[1] as FakeEl;
  const add = page.querySelectorAll(".person-rules .quiet").find((b) => b.textContent?.startsWith("+"));
  if (!add) throw new Error("no New rule on the person's page");
  add.click();
  expect("the page asks for a new rule for the helper", got.opened.at(-1), { newFor: "helper" });
}

function editor(): { cond: FakeEl; decided: Decision[] } {
  const { ctx, got } = testContext();
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  tab.open(view, { newFor: "helper" });
  const cond = (fakeDocument.body.firstElementChild as FakeEl).querySelector(".cond");
  if (!cond) throw new Error("the condition editor did not open");
  cond.querySelector(".cond-more")?.click();
  return { cond, decided: got.decided };
}
const running = (cond: FakeEl): string[] => cond.querySelectorAll(".cond-subject").map((b) => b.dataset.subject ?? "").filter((k) => k.startsWith("running:"));

{  // a person's task: the other lane's cards are offered under Running, none of their own lane's
  const { cond, decided } = editor();
  cond.querySelector('.cond-task[data-card="chop"]')?.click();
  expect("the helper's rule is offered the mason's and the hands' cards running", running(cond).length > 0 && running(cond).every((k) => !["running:chop", "running:haul"].includes(k)), true);
  expect("the mason's card is among them", running(cond).includes("running:hew"), true);
  cond.querySelector('.cond-subject[data-subject="running:hew"]')?.click();
  cond.querySelector(".cond-actions .primary")?.click();
  const set = decided.at(-1);
  expect("saved as the one Running shape on the helper's tap", set?.kind === "set_orders" ? set.orders.at(-1) : set,
    { when: { kind: "at_least", watched: { kind: "running", runner: "hew" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false }, then: { kind: "tap_card", card: "chop" }, unless: [], or_else: [], below_next: false });
}

{  // a hands rule, a mix, or a person's rule with a fallback on another lane: none
  const hands = view.cards.find((c) => c.card !== "chop" && c.card !== "haul" && c.card !== "hew" && c.card !== "carve")?.card ?? "";
  const { ctx } = testContext();
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  tab.open(view, "new");
  const open = (fakeDocument.body.firstElementChild as FakeEl).querySelector(".cond") as FakeEl;
  open.querySelector(".cond-more")?.click();
  expect("before a task is chosen, none", running(open), []);
  if (!open.querySelector(`.cond-task[data-card="${hands}"]`)) throw new Error(`no hands task ${hands} to pick: the check looked at nothing`);
  open.querySelector(`.cond-task[data-card="${hands}"]`)?.click();
  expect("a hands task: none", running(open), []);
  open.querySelector(".cond-task[data-card=\"chop\"]")?.click();
  expect("control: the same editor offers running once a person's task is chosen", running(open).length > 0, true);
}
