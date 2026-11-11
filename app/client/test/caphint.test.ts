// The first full store (docs/design/opening-screen.md, the hands strip, "Hint: the first full store"; game/caphint.ts):
// a store the hands still make sits at its cap while another hands task could take the time, and no rule watches it reach
// a level. Written from that row: each case changes one fact of the full fixture and expects the mark to come or go.
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Order, View } from "../src/api/types";
import { capStore } from "../src/game/caphint";
import { Catalog } from "../src/game/catalog";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const full = fixtureStep("full", 100).view;
const wood = full.ledger.find((l) => l.store === "wood");
const withWood = (view: View, change: (l: View["ledger"][number]) => View["ledger"][number]): View =>
  ({ ...view, ledger: view.ledger.map((l) => (l.store === "wood" ? change(l) : l)) });
const watching = (kind: "at_least" | "at_most", store: string): Order => ({
  when: { kind, watched: { kind: "store_value", store }, value: 10, release: kind === "at_least" ? 5 : 20 },
  then: { kind: "tap_card", card: "tend" },
});

expect("control: the fixture's wood is at its cap and fed by gather, a hands card", wood !== undefined && wood.segment.start_value === wood.cap
  && wood.contributions.some((c) => c.runner === "gather" && c.per_hour > 0) && catalog.mixable("gather"), true);
expect("a full store the hands make is marked", capStore(catalog, full), "wood");
expect("control: mid's wood is below its cap, nothing marked", capStore(catalog, fixtureStep("mid", 100).view), null);

expect("one below the cap is not full", capStore(catalog, withWood(full, (l) => ({ ...l, segment: { ...l.segment, start_value: l.cap - 1, rate: 0 } }))), null);
expect("full with nothing feeding it loses nothing", capStore(catalog, withWood(full, (l) => ({ ...l, contributions: [] }))), null);
expect("control: chop is a ruled lane's task, not the hands'", catalog.mixable("chop"), false);
expect("full, fed only by another lane: not the hands' time",
  capStore(catalog, withWood(full, (l) => ({ ...l, contributions: [{ runner: "chop", per_hour: l.net_per_hour }] }))), null);
expect("no other hands task in play: nothing else could use the time",
  capStore(catalog, { ...full, cards: full.cards.filter((c) => c.card === "gather" || !catalog.mixable(c.card)) }), null);
expect("a rule on reaching a level of the store answers it", capStore(catalog, { ...full, orders: [watching("at_least", "wood")], orders_on: [false] }), null);
expect("a rule on falling below a level does not", capStore(catalog, { ...full, orders: [watching("at_most", "wood")], orders_on: [false] }), "wood");
expect("a reaching rule on another store does not", capStore(catalog, { ...full, orders: [watching("at_least", "stone")], orders_on: [false] }), "wood");
const max = fixtureContent.limits.max_orders;
expect("no room for another rule: nothing to teach", capStore(catalog, { ...full, orders: Array.from({ length: max }, () => watching("at_most", "stone")), orders_on: Array<boolean>(max).fill(false) }), null);
const camp = fixtureContent.camp;
expect("the Camp store is never marked", camp ? capStore(new Catalog({ ...fixtureContent, camp: { ...camp, store: "wood" } }), full) : "no camp", null);
