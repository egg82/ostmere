// A person with nothing to do (issue 467; game/stuck.ts, ui/stucknote.ts): when every card holding a share of their time is
// paused or spent and no tap holds their lane, their Town row reads "nothing to do" in place of "idle", says what each
// card is stopped on, and offers the tasks they could run now, each one tap that joins it to their time (their set
// shares kept); their page says the same with every offer. A spent card's face says which store nothing makes now.
// Nothing is chosen for the player: no decision is sent until an offer is tapped.
import { install, type FakeEl } from "./fake-dom";
import { pageRig, savedMix } from "./personrig";
import { townStep } from "../fixtures/town";
import { fixtureContent } from "../fixtures/content";
import type { Card, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { runnableFor, stuckOf } from "../src/game/stuck";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const base = townStep("town").view;
const chop = base.cards.find((c) => c.card === "chop") as Card;
const name = (card: string): string => catalog.cardLabel(card);
// the helper on shares alone (the fixture has them tapping Haul by a rule): Chop paused, Haul spent on wood, Fetch open
const stuck: View = {
  ...base,
  lanes: base.lanes.map((l) => (l.lane === "helper" ? { ...l, running_card: null } : l)),
  cards: [...base.cards.map((c) => (c.card === "chop" ? { ...c, run: "paused" as const, by: null }
    : c.card === "haul" ? { ...c, run: "spent" as const, by: null, spent_store: "wood" } : c)),
  { ...chop, card: "fetch", share_bp: 0, run: null, by: null }],
};

expect("control: the fixture's helper is tapping by a rule, not stuck", stuckOf(catalog, base, "helper"), null);
expect("control: the mason runs shares, not stuck", stuckOf(catalog, stuck, "mason"), null);
expect("every held card stopped: stuck, each with why", stuckOf(catalog, stuck, "helper"),
  [{ card: "chop", why: "dry", store: null }, { card: "haul", why: "spent", store: "wood" }]);
expect("offers: the open task holding no share", runnableFor(catalog, stuck, "helper"), ["fetch"]);
const capped = { ...stuck, cards: stuck.cards.map((c) => (c.card === "fetch" ? { ...c, cap: 1 } : c)) };
expect("a capped task is not offered (the town's mix holds none)", runnableFor(catalog, capped, "helper"), []);

const rowOf = (root: FakeEl, lane: string): FakeEl => root.querySelectorAll(".town-person").find((r) => r.dataset.lane === lane) as FakeEl;
const texts = (nodes: FakeEl[]): string[] => nodes.map((n) => n.textContent ?? "");

{  // the Town row
  const { root, got, settle } = pageRig(base);
  expect("control: a working person's row has no note", rowOf(root, "helper").querySelector(".stuck-note")?.hidden, true);
  settle(stuck, []);
  const row = rowOf(root, "helper");
  expect("the row reads nothing to do, not idle", row.querySelector(".town-doing")?.textContent, "nothing to do");
  expect("what each card is stopped on", texts(row.querySelectorAll(".stuck-line")),
    [`${name("chop")} is waiting`, `${name("haul")} needs ${catalog.storeLabel("wood")}, nothing makes it now`]);
  expect("the open task, one tap", texts(row.querySelectorAll(".stuck-offer")), [`+ ${name("fetch")}`]);
  expect("nothing is chosen for the player", got.decided.length, 0);
  row.querySelector(".stuck-offer")?.click();
  const mix = savedMix(got.decided[0]);
  const shares = Object.fromEntries((mix?.components ?? []).flatMap((c) => (c.kind === "card_share" ? [[c.card, c.share_bp]] : [])));
  expect("Fetch joins with the helper's free time; the shares the player set stay", shares, { chop: 6000, haul: 3000, hew: 7000, carve: 2000, fetch: 1000 });
}

{  // the page, and the spent card's face
  const { root, got, page, settle, face } = pageRig(base);
  settle(stuck, []);
  rowOf(root, "helper").querySelector(".person-change")?.click();
  expect("the page's note shows", page.querySelector(".stuck-note")?.hidden, false);
  expect("its offers", texts(page.querySelectorAll(".stuck-offer")), [`+ ${name("fetch")}`]);
  expect("the spent card's face names the store", face("haul").querySelector(".card-need.full.spent")?.textContent,
    `Needs ${catalog.storeLabel("wood")}, nothing makes it now`);
  page.querySelector(".stuck-offer")?.click();
  expect("a tap on the page joins it too", savedMix(got.decided[0])?.components.some((c) => c.kind === "card_share" && c.card === "fetch"), true);
}
