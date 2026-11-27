// An order card offered once (OrderCard.offered_until): once view.unlocked holds the unlock the season's turn that
// retired its rule gives, the page offers the card no more, at the chip's next showing or under a line, and the chip
// comes back as a chore with its hint dot alone. A copy with no field is offered as before.
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Unlock, View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { chipCards, offeredCard } from "../src/game/ledger/cues";
import { choreChips } from "../src/game/hands/hints";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const TURN: Unlock = { category: "feature", id: "turned" };
const rest = { ...fixtureStep("restoffer", 100).view, orders: [], orders_on: [] };
const turned: View = { ...rest, unlocked: [...rest.unlocked, TURN] };

const once = (until: Unlock | null) => new Catalog({
  ...fixtureContent,
  chip_infos: fixtureContent.chip_infos.map((c) => (c.chip === "tired" ? { ...c, chore: true } : c)),
  order_cards: fixtureContent.order_cards.map((c) => (c.chip === "tired" || c.store === "wood" ? { ...c, offered_until: until } : c)),
});
const retired = once(TURN);
const fieldless = once(null);
const names = (c: Catalog, v: View) => chipCards(c, v, true).map((x) => x.store);

expect("control: the chip shows", rest.chips.includes("tired"), true);
expect("before the turn the card is offered", names(retired, rest), ["energy"]);
expect("after the turn it is not offered at the chip's next showing", names(retired, turned), []);
expect("a planted field-less copy is offered after the turn", names(fieldless, turned), ["energy"]);

expect("a retired card is not offered under its line either", offeredCard(retired, turned, "wood"), undefined);
expect("control: the same line before the turn", offeredCard(retired, rest, "wood")?.store, "wood");
expect("a field-less copy under its line is offered after the turn", offeredCard(fieldless, turned, "wood")?.store, "wood");

expect("the chip is a chore with its hint dot alone once its card is over", choreChips(retired, turned), ["tired"]);
expect("control: not before the turn, while its card is on offer", choreChips(retired, rest), []);
expect("a field-less copy is no chore", choreChips(fieldless, turned), []);
