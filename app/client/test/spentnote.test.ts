// A spent card on the strip (CONTRACT.txt, "SPENT"): while a card of the running mix is stopped on a store nothing
// can make again, the strip's status names the store, whether or not others gain its share (the split that runs now
// shows the gains: runningnow.test.ts); a mix with no spent card carries no note.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { Hands } from "../src/ui/hands";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const hands = new Hands(testContext().ctx);
const status = (): string => hands.root.querySelector(".hands-status")?.textContent ?? "";
const base = fixtureStep("mid", 100).view;
const [spent, other] = base.cards;
if (!spent || !other) throw new Error("fixture: the page holds fewer than two cards");

const withSpent = (gains: boolean): View => ({
  ...base,
  cards: base.cards.map((c) => (c.card === spent.card ? { ...c, run: "spent" as const, spent_store: "wood" }
    : c.card === other.card && gains ? { ...c, gained: [{ card: spent.card, share_bp: 1000 }] } : c)),
});

hands.update(base);
expect("control: no spent card, no note", status(), "");
hands.update(withSpent(false));
expect("spent, nobody gains: names the store", status(), "Dead wood is used up");
hands.update(withSpent(true));
expect("spent, another card gains: still names the store", status(), "Dead wood is used up");
hands.update(base);
expect("refilled: the note goes", status(), "");
