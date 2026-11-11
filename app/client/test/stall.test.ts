// The stall offer: two hand-starts in a row of the card an order would start, and no other count.
import { fixtureContent } from "../fixtures/content";
import { HandStreak, stalled } from "../src/game/stall";

const card = fixtureContent.order_cards[0]!;   // taps "gather"

function expect(label: string, got: unknown, want: unknown): void {
  if (got !== want) throw new Error(`${label}: got ${String(got)}, want ${String(want)}`);
}

const s = new HandStreak();
expect("no taps", stalled(s, card), false);
s.tap("gather");
expect("one tap", stalled(s, card), false);
s.tap("gather");
expect("two in a row", stalled(s, card), true);
s.tap("tend");
expect("another card in between", stalled(s, card), false);
s.tap("gather");
expect("one again", stalled(s, card), false);
s.tap("gather");
s.tap("gather");
expect("three in a row", stalled(s, card), true);
const other = new HandStreak();
other.tap("tend");
other.tap("tend");
expect("a different card twice", stalled(other, card), false);
expect("an order that taps no card", stalled(s, { ...card, then: { kind: "switch_mix", mix: "Main" } as never }), false);
