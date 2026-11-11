// The answer rule's builder reads as a rule for later offers of the kind, not as the offer still waiting
// (CONTRACT.txt, "Offers"): it says which answer the offer it is worded by was given, and its lead says the buttons
// are for next time. The question no longer takes the open offer's look.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { dayTwoStep } from "../fixtures/daytwo";
import type { View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { RulesTab } from "../src/ui/rules";

install();
Object.assign(window, { innerWidth: 1440, innerHeight: 900 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const kinded = new Catalog({ ...fixtureContent, offer_infos: fixtureContent.offer_infos.map((o) => (o.offer !== "ask" ? o
  : { ...o, kind: "q", answers: o.answers.map((a) => ({ ...a, role: a.answer === "go" ? "yes" : "no" })) })) });
const open = dayTwoStep("offered", 100).view;
const answeredWith = (answer: string): View => ({ ...open, offers: open.offers.map((o) => (o.offer === "ask" ? { ...o, answer } : o)) });

function builder(view: View): FakeEl {
  const { ctx } = testContext(undefined, kinded);
  const tab = new RulesTab(ctx);
  document.body.replaceChildren(tab.root);
  tab.update(view);
  const row = fakeDocument.body.querySelector(".kind-rule");
  if (!row) throw new Error("no builder");
  return row;
}

for (const [answer, label] of [["go", "Go now"], ["wait", "Wait"]] as const) {
  const row = builder(answeredWith(answer));
  expect(`the answer given (${answer})`, row.querySelector(".kind-answered")?.textContent, `Answered: ${label}`);
  expect("the lead is about next time", row.querySelector(".kind-lead")?.textContent, "Next time someone asks:");
  expect("the question is not drawn as an open offer", row.querySelector(".offer-text"), null);
}
