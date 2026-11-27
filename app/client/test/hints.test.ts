// Hints (game/hints.ts): the detection behind today's marks, from the view alone. A card the player keeps tapping by hand that
// the mix could take is marked until it is touched (once, kept); nothing is marked during a lesson or before the first mix's
// is behind; a chip is marked for a switch the player keeps making and for the order card the strip would have offered.
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Order, View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { chipCards } from "../src/game/ledger/cues";
import { cardHints, chipHints, hintedCards, secondMixCard } from "../src/game/hands/hints";
import { FIRST_MIX, FIRST_RULE, SECOND_MIX } from "../src/game/lessons/lessons";
import { keepsOf, NEW_FLAT } from "./kept";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const view = fixtureStep("mid", 100).view;
const everyCard = view.cards.map((c) => ({ card: c.card, count: 3 }));
const [card = ""] = hintedCards(catalog, view, () => false, everyCard);   // a card outside the mix that it could take
const taps = [{ card, count: 3 }];
expect("control: the fixture has such a card", card !== "", true);
const taught = keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX, FIRST_RULE] });

expect("a hand-tapped card the mix could take", hintedCards(catalog, view, () => false, taps), [card]);
expect("control: no repeated taps, no mark", hintedCards(catalog, view, () => false, []), []);
expect("once marked, never again", hintedCards(catalog, view, (c) => c === card, taps), []);
expect("a greyed mix is not hinted at", hintedCards(catalog, { ...view, greyed_mix_ids: [view.active_mix_id as string] }, () => false, taps), []);
expect("no mark while a lesson runs", cardHints(catalog, view, taught, "journal", taps), []);
expect("none before the first mix's lesson is behind", cardHints(catalog, { ...view, mixes: [] }, keepsOf(NEW_FLAT), null, taps), []);
expect("marked once the lessons are behind", cardHints(catalog, view, taught, null, taps), [card]);

// The second mix's lesson starts from the first card a mark would go on, while that lesson may (after the first rule's).
expect("the second mix's card", secondMixCard(catalog, view, taught, taps), card);
expect("a mark touched before the lesson still counts", secondMixCard(catalog, view, keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX, FIRST_RULE], mix_offered: [card] }), taps), card);
expect("control: no repeated taps, no card", secondMixCard(catalog, view, taught, []), null);
expect("none before the first rule's lesson is behind", secondMixCard(catalog, view, keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX] }), taps), null);
expect("none once kept", secondMixCard(catalog, view, keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX, FIRST_RULE, SECOND_MIX] }), taps), null);
const full = { ...view, mixes: Array.from({ length: catalog.content.limits.max_mixes }, (_, i) => ({ ...view.mixes[0]!, id: `m${i}` })) };
expect("none when no new mix can be saved", secondMixCard(catalog, { ...full, active_mix_id: "m0" }, taught, taps), null);
expect("control: the same mixes one short of full", secondMixCard(catalog, { ...full, mixes: full.mixes.slice(1), active_mix_id: "m1" }, taught, taps), card);

const rest = { ...fixtureStep("restoffer", 100).view, orders: [], orders_on: [] };
expect("a chip card's chip is marked once the first rule's lesson is behind", chipHints(catalog, rest, taught, null, [], true).map((h) => h.chip), ["tired"]);
expect("none while the lesson may start (its row is the entry)", chipHints(catalog, rest, keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX] }), null, [], true), []);
expect("none during a lesson", chipHints(catalog, rest, taught, "journal", [], true), []);

// A season's chore with no order card (week-four-plan item 4): its chip carries the mark from its first showing with no card
// offered, until a rule is set on its store and test; an ordinary chip with no card is not marked.
const choreContent = { ...fixtureContent, chip_infos: fixtureContent.chip_infos.map((c) => (c.chip === "tired" ? { ...c, chore: true } : c)),
  order_cards: fixtureContent.order_cards.filter((c) => c.chip !== "tired") };
const chore = new Catalog(choreContent);
const shown = (c: Catalog, v: View) => chipHints(c, v, taught, null, [], true).map((h) => h.chip);
expect("control: the chore's chip shows with no card offered", [rest.chips.includes("tired"), chipCards(chore, rest, true)], [true, []]);
expect("a chore with no order card is marked", shown(chore, rest), ["tired"]);
expect("control: the same chip, no chore, no card: not marked", shown(new Catalog({ ...choreContent, chip_infos: fixtureContent.chip_infos }), rest), []);
expect("not marked before it shows", shown(chore, { ...rest, chips: rest.chips.filter((c) => c !== "tired") }), []);
const tiredRule: Order = { when: chore.chips.get("tired")!.when, then: { kind: "tap_card", card: "rest" }, unless: [], or_else: [], below_next: false };
expect("not marked once a rule is set on its store and test", shown(chore, { ...rest, orders: [tiredRule], orders_on: [false] }), []);
const fullRules: Order[] = Array.from({ length: chore.content.limits.max_orders }, () => ({ ...tiredRule, when: { kind: "after_time", at: 0 } }));
expect("not marked while no rule can be added", shown(chore, { ...rest, orders: fullRules, orders_on: fullRules.map(() => false) }), []);

// Lessons off (AccountSettings.lessons): no lesson-only hint (the second mix's card), and the ordinary marks no longer wait on
// lessons that will not run.
const off = keepsOf(NEW_FLAT, null, { lessons: false });
expect("lessons off: no second mix's card", secondMixCard(catalog, view, keepsOf({ ...NEW_FLAT, lessons: [FIRST_MIX, FIRST_RULE] }, null, { lessons: false }), taps), null);
expect("lessons off: a card is marked with no lesson behind", cardHints(catalog, view, off, null, taps), [card]);
expect("lessons off: a chip is marked with no lesson behind", chipHints(catalog, rest, off, null, [], true).map((h) => h.chip), ["tired"]);
