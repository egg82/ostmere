// A new card that gets a new slot at the end of its group, out of sight on a phone below the mix's cards, is brought
// into view once (ui/cards.ts): scrolled to the nearest edge, unless a finger is on the page or just left it. A card
// taking a finished card's slot lands under the finger and needs no scroll.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { Card, View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { Cards } from "../src/ui/cards";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function check(label: string, block: () => void): void {
  try { block(); } catch (e) { throw new Error(`${label}: ${(e as Error).message}`); }
}

const scrolled: string[] = [];
const proto = Object.getPrototypeOf(document.createElement("div")) as { scrollIntoView?: () => void };
proto.scrollIntoView = function (this: HTMLElement): void { scrolled.push(this.textContent ?? ""); };

const AT = 100;
const base = fixtureStep("restrule", AT).view;
const step = (id: string): Card => ({
  card: id, completions: 0, cap: 1, bar: { start: AT, start_value: 0, rate: 0, limit: null }, bar_total: 20, by: null,
  completes_at: null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20, needs: [],
});
const withCards = (cards: Card[]): View => ({ ...base, cards: [...base.cards, ...cards] });

function drawn(): { cards: Cards; ctx: ReturnType<typeof testContext>["ctx"] } {
  const { ctx } = testContext();
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  cards.update(withCards([]), null);
  return { cards, ctx };
}

check("a new card at the end of its group is scrolled into view once", () => {
  scrolled.length = 0;
  const { cards } = drawn();
  const first = withCards([]);
  cards.update(withCards([step("take_stock")]), first);
  expect("one scroll", scrolled.length, 1);
});

// A finger on the page: no scroll (the list must not move under it).
{
  scrolled.length = 0;
  const { cards } = drawn();
  fakeDocument.body.dispatchEvent(new FakeEvent("pointerdown"));
  cards.update(withCards([step("take_stock")]), withCards([]));
  expect("no scroll under a finger", scrolled.length, 0);
}

// A card taking the slot of the one that just finished lands under the finger: no scroll.
{
  scrolled.length = 0;
  const { cards } = drawn();
  const before = withCards([step("larder")]);
  cards.update(before, withCards([]));
  scrolled.length = 0;
  cards.update(withCards([step("lean_to")]), before);   // both crafts: one group
  expect("no scroll into a finished card's slot", scrolled.length, 0);
}

// Two new cards at once: one scroll, to the first.
{
  scrolled.length = 0;
  const { cards, ctx } = drawn();
  cards.update(withCards([step("take_stock"), step("larder")]), withCards([]));
  expect("one scroll for the batch", scrolled.length, 1);
  const first = ctx.catalog.label(ctx.catalog.cards.get("take_stock")?.label_key);
  expect("to the first", scrolled[0]?.includes(first), true);
}
