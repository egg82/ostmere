// The second offer kind (docs/design/day-three-plan.md, item 5; CONTRACT.txt, "Offers"): once an offer whose answers
// start nothing and install a modifier sits beside one that starts a card, the Rules tab lists the answer order (the
// always rules that answer offers, in list order, under the Answers heading), and the Asks list words each answer's
// effect where a time would be.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { dayTwoStep } from "../fixtures/daytwo";
import type { Offer, Order, View } from "../src/api/types";
import { Asks } from "../src/ui/asks";
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

const answer = (offer: string, a: string): Order => ({ when: { kind: "after_time", at: 0 }, then: { kind: "answer_offer", offer, answer: a } });
const bank: Offer = { offer: "bank", answer: null, answers: [{ answer: "hers", card: null, takes_s: null }, { answer: "his", card: null, takes_s: null }] };
const base = dayTwoStep("offered", 100).view;
const order: Order[] = [answer("bank", "his"), answer("ask", "go")];
const both: View = { ...base, offers: [...base.offers, bank], orders: [...base.orders, ...order], orders_on: [...base.orders_on, false, false], order_states: [...base.order_states, "on", "on"] };

{  // the answer order: both kinds' always rules under the Answers heading, in list order
  const tab = new RulesTab(testContext().ctx);
  const root = mounted(tab.root);
  tab.update(both);
  const section = root.querySelectorAll(".rules-lane").find((s) => s.querySelector(".panel-heading")?.textContent === "Answers");
  if (!section) throw new Error("no Answers section");
  expect("the answer order, in list order", section.querySelectorAll(".rules-row").map((r) => r.querySelector(".rule-cond-text")?.textContent), ["Answer: His", "Answer: Go now"]);
  expect("no arrow: the answer is in the words", section.querySelectorAll(".rule-arrow").length, 0);
}

{  // the modifier offer's ask: each answer's effect where a time would be; the card offer's keeps its time (both in the list)
  const { ctx } = testContext();
  ctx.lines = () => [];
  const asks = new Asks(ctx);
  const root = mounted(asks.root);
  asks.update(both);
  root.querySelector(".asks-more")?.click();
  const list = root.querySelector(".asks-sheet");
  const costs = (offer: string) => list?.querySelector(`[data-offer="${offer}"]`)?.querySelectorAll("button").map((b) => b.textContent);
  expect("the effects", costs("bank"), ["Hers[fixture] +10% a thing", "His[fixture] -10% another, 2 wood"]);
  expect("the card offer still names its time", costs("ask"), ["Wait", "Go nowtakes 12 m 30 s"]);
}
