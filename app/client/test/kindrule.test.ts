// The answer rule on the page (CONTRACT.txt, "Offers"): the Rules tab's answers section builds one rule per offer kind,
// and only once an offer of that kind has been answered; its buttons are the kind's roles worded by the answer that
// offer gave; a tap sets (or, with a rule set, changes in place) an answer_kind order; the page builds no answer_offer.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { dayTwoStep } from "../fixtures/daytwo";
import type { Decision, Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { RulesTab } from "../src/ui/rules";

install();
Object.assign(window, { innerWidth: 1440, innerHeight: 900 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

// The fixture's "ask" offer, made a kind of its own with roles on its two answers; "bank" stays unkinded.
const kinded = new Catalog({ ...fixtureContent, offer_infos: fixtureContent.offer_infos.map((o) => (o.offer !== "ask" ? o
  : { ...o, kind: "q", answers: o.answers.map((a) => ({ ...a, role: a.answer === "go" ? "yes" : "no" })) })) });
const open = dayTwoStep("offered", 100).view;
const answered: View = { ...open, offers: open.offers.map((o) => (o.offer === "ask" ? { ...o, answer: "go" } : o)) };
const rule: Order = { when: { kind: "after_time", at: 0 }, then: { kind: "answer_kind", offer_kind: "q", role: "yes" } };
const ruled: View = { ...answered, orders: [...answered.orders, rule], orders_on: [...answered.orders_on, false], order_states: [...answered.order_states, "on"] };

function draw(view: View): { root: FakeEl; decided: Decision[] } {
  const { ctx, got } = testContext(undefined, kinded);
  const tab = new RulesTab(ctx);
  const root = mounted(tab.root);
  tab.update(view);
  return { root, decided: got.decided };
}

const builders = (root: FakeEl) => root.querySelectorAll(".kind-rule");

{  // before any offer of the kind is answered the builder is absent, though the offer is open and shown
  expect("the offer is open", open.offers.some((o) => o.offer === "ask" && o.answer === null), true);
  expect("no builder", builders(draw(open).root).length, 0);
}

{  // once one is answered: a row under Answers, a button per role worded by that offer's answers
  const { root } = draw(answered);
  const rows = builders(root);
  expect("one builder", rows.length, 1);
  expect("in the answers section", rows[0]?.parentElement?.querySelector(".panel-heading")?.textContent, "Answers");
  expect("a button per role, by the answer's label", rows[0]?.querySelectorAll("button").map((b) => [b.dataset.role, b.textContent]), [["no", "Wait"], ["yes", "Go now"]]);
  expect("a line says the buttons set a standing answer", rows[0]?.querySelector(".kind-lead")?.textContent, "Next time someone asks:");
  expect("none pressed with no rule", rows[0]?.querySelectorAll("button").map((b) => b.getAttribute("aria-pressed")), ["false", "false"]);
}

{  // a tap sets the kind's rule, an always rule appended, an answer_kind and never an answer_offer
  const { root, decided } = draw(answered);
  root.querySelector("[data-role=\"yes\"]")?.click();
  expect("sets the rule", decided, [{ kind: "set_orders", orders: [...answered.orders, rule] }]);
}

{  // with the rule set: its row says what it does, the role is pressed; a tap on the other role changes it in place
  const { root, decided } = draw(ruled);
  expect("the rule's words", root.querySelectorAll(".task-rule").map((r) => r.querySelector(".rule-cond-text")?.textContent).filter((t) => t?.startsWith("Answer")), ["Answer: Go now"]);
  expect("the pressed role", builders(root)[0]?.querySelectorAll("button").map((b) => b.getAttribute("aria-pressed")), ["false", "true"]);
  root.querySelector("[data-role=\"no\"]")?.click();
  expect("changed in place", decided, [{ kind: "set_orders", orders: [...answered.orders, { ...rule, then: { ...rule.then, role: "no" } }] }]);
}

{  // remove takes the rule away
  const { root, decided } = draw(ruled);
  root.querySelectorAll(".task-rule").at(-1)?.querySelector(".quiet")?.click();
  expect("removed", decided, [{ kind: "set_orders", orders: answered.orders }]);
}
