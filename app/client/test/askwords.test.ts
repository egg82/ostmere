// What an ask says of itself (game/asks.ts; CONTRACT.txt, "OFFERS"): who asks by name (a lane's name text, else its
// label as it reads now), what led to it (a line's cause, an earlier answer by its label), and the figures an answer
// moves, read off a dry run against the view (rates, then caps, then card times, never the Camp's store).
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { asksStep } from "../fixtures/asks";
import type { Content, OfferInfo, View } from "../src/api/types";
import { answerFigures, askCause, askedBy, openAsks } from "../src/game/asks";
import { Catalog } from "../src/game/catalog";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const view = asksStep("asksmany", 100).view;
const info = (offer: string): OfferInfo => {
  const got = fixtureContent.offer_infos.find((o) => o.offer === offer);
  if (!got) throw new Error(`no offer ${offer}`);
  return got;
};

{  // the open asks, in content order
  expect("all three open", openAsks(view), ["ask", "bank", "trade"]);
  expect("an answered one leaves", openAsks(asksStep("asksmany", 100, { answered: ["bank:his"] }).view), ["ask", "trade"]);
}

{  // who asks: the label as it reads now, a name text over it, joined as a list
  expect("two by label, the later label once its unlock holds", askedBy(catalog, view, info("bank")), "Helper, settled and Mason");
  const early: View = { ...view, unlocked: view.unlocked.filter((u) => u.id !== "yard") };
  expect("the first label before it", askedBy(catalog, early, info("bank")), "Helper and Mason");
  const named: Content = { ...fixtureContent, lane_infos: fixtureContent.lane_infos.map((l) => (l.lane === "mason" ? { ...l, name_key: "answer.keep" } : l)) };
  expect("a name text wins", askedBy(new Catalog(named), view, info("bank")), "Helper, settled and Keep it");
  expect("no one", askedBy(catalog, view, info("ask")), "");
}

{  // what led to it
  expect("a gate, as a line's cause", askCause(catalog, view, info("bank")), "Tend the fire ×3");
  expect("an earlier answer, by its label", askCause(catalog, asksStep("asksmany", 100, { answered: ["bank:his"] }).view, info("trade")), "your answer: His");
  expect("an earlier offer not answered in the view: the plain cause", askCause(catalog, view, info("trade")), "your answer");
  expect("none", askCause(catalog, view, info("ask")), null);
}

{  // the figures an answer moves
  const after = (answer: string): View => asksStep("asksmany", 100, { answered: [answer] }).view;
  expect("a rate and a card's time", answerFigures(catalog, view, after("bank:hers")), ["Dead wood -2/min → -1.8/min", "Rest 5 s → 4 s"]);
  expect("a cap", answerFigures(catalog, view, after("bank:his")), ["Dead wood holds 40 → 50"]);
  expect("nothing moved", answerFigures(catalog, view, view), []);
  const camp: View = { ...view, ledger: [...view.ledger, { ...view.ledger[0]!, store: "camp" }] };
  const campAfter: View = { ...camp, ledger: camp.ledger.map((l) => (l.store === "camp" ? { ...l, net_per_hour: l.net_per_hour + 3600 } : l)) };
  expect("never the Camp's store", answerFigures(catalog, camp, campAfter), []);
}
