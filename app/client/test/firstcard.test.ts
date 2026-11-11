// The first card before its first tap (docs/design/opening-screen.md, "Cards"): the lone card on the screen, never
// completed and not under way, is marked `untapped` (only its verb shows, the rest keeps its room); once tapped, or
// once it is not alone, it is not.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { Card, View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { Cards } from "../src/ui/cards";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const start = fixtureStep("start", 100).view;
const lone = start.cards[0];
if (start.cards.length !== 1 || !lone) throw new Error("the fixture's start should hold one card");

function classes(view: View): string[][] {
  const { ctx } = testContext();
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  cards.update(view, null);
  return Array.from(cards.root.querySelectorAll(".card"), (n) => ["first", "untapped"].filter((c) => n.classList.contains(c)));
}
const as = (over: Partial<Card>): View => ({ ...start, cards: [{ ...lone, ...over }] });

expect("the lone card, never tapped", classes(start), [["first", "untapped"]]);
expect("under way by a tap", classes(fixtureStep("standing", 100).view), [["first"]]);
expect("tapped and running, none done yet", classes(as({ by: "tap" })), [["first"]]);
expect("completed once, idle", classes(as({ completions: 1 })), [["first"]]);
expect("not alone", classes({ ...start, cards: [lone, { ...lone, card: "look" }] }), [[], []]);
