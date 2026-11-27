// The town's mix on the page (contract/the-towns-mix.txt, "The town's mix"; game/town/town.ts, ui/town/townstrip.ts, ui/town/personpage.ts): in the Town
// tab, once people have joined, one block per person: their face and who, their shares and the idle rest, the card they are on;
// each person's Change opens their page, where their tasks join or leave their split; before the join the page is day two's lane row. The views are the
// engine's own (fixtures/townwire.ts: helper tapping Haul by a rule, shares yielded; mason on shares).
import { type FakeEl, install } from "../../fake-dom";
import { dayTwoStep } from "../../../fixtures/daytwo";
import { townStep } from "../../../fixtures/town";
import type { Card, Mix, View } from "../../../src/api/types";
import { panelView } from "../../../src/game/town/lanes";
import { Catalog } from "../../../src/game/page/catalog";
import { fixtureContent } from "../../../fixtures/content";
import { pageRig, savedMix, shareOf, texts } from "../../ui/town/personrig";
import { isTownMix, townMixToEdit } from "../../../src/game/town/town";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const both = townStep("town").view;
const helperOnly = townStep("townone").view;
const before = dayTwoStep("ruled", 100).view;

const rig = (view: View) => pageRig(view);

{  // before the first join: day two's row, no strip
  const { root } = rig(before);
  expect("no town strip before the join", root.querySelectorAll(".town").length, 0);
  expect("the lane row is day two's", root.querySelectorAll(".lane-row").length, 1);
}

{  // two people: a block each, their shares and idle rest as the engine served them, the card each is on
  const { root } = rig(both);
  expect("each person's face", texts(root.querySelectorAll(".town-person .ask-face")), ["H", "M"]);
  expect("a block per person", texts(root.querySelectorAll(".town-person .town-name")), ["Helper", "Mason"]);
  expect("the helper taps by a rule", texts(root.querySelectorAll(".town-person .town-doing")), ["Haul water", "Hew stone"]);
  expect("shares, idle last", root.querySelectorAll(".town-person").map((p) => texts(p.querySelectorAll(".town-key-item"))), [
    ["Chop logs 60%", "Haul water 30%", "Helper, idle 10%"], ["Hew stone 70%", "Carve beams 20%", "Mason, idle 10%"]]);
  expect("joined people have no row of their own", root.querySelectorAll(".lane-row").length, 0);
  const grow = root.querySelectorAll(".town-person").map((p) => p.querySelectorAll(".town-seg").reduce((n, s) => n + Number(s.style.flexGrow), 0));
  expect("each person's parts total their whole time", grow, [10000, 10000]);
}

{  // one person: the other's lane keeps its own row
  const { root } = rig(helperOnly);
  expect("one block", texts(root.querySelectorAll(".town-person .town-name")), ["Helper"]);
  expect("the mason's lane keeps its row", root.querySelectorAll(".lane-row").map((r) => r.dataset.lane), ["mason"]);
}

{  // ruled-lane cards are not in the card panel
  const cards = panelView(catalog, both).cards.map((c: Card) => c.card);
  expect("no ruled-lane card in the panel", cards.filter((c) => ["chop", "haul", "hew", "carve"].includes(c)), []);
}

{  // every person's Change opens their page; the camp has none of its own
  const { root, page, open } = rig(both);
  expect("no camp-wide Change", root.querySelectorAll(".town-change").length, 0);
  expect("a Change per person", root.querySelectorAll(".person-change").length, 2);
  open(1);
  expect("the second person's page is open", [page.hidden, texts(page.querySelectorAll(".editor-head .town-title"))], [false, ["Mason"]]);
  expect("their split is its bar, theirs alone", texts((page.querySelector(".person-mix") as FakeEl).querySelectorAll(".share-key-item")), ["Hew stone 70%", "Carve beams 20%", "Mason, idle 10%"]);
}

{  // the page offers every task of the person's lane, a share on those the mix holds
  const { open, face } = rig(both);
  const page = open(0);
  expect("the helper's tasks", page.querySelectorAll(".person-cards .card").map((c) => c.dataset.card), ["chop", "haul"]);
  expect("shares on the faces", [shareOf(face("chop")), shareOf(face("haul"))], ["60%", "30%"]);
}

{  // a task the mix does not hold joins by a tap on its face and leaves by another; each is sent as it is made
  const { open, face, got, settle } = rig(helperOnly);
  const page = open(0);
  const { cards } = helperOnly;
  const lone = { ...helperOnly, mixes: helperOnly.mixes.map((m) => ({ ...m, components: m.components.filter((c) => c.kind !== "card_share" || c.card !== "haul") })) };
  expect("fixture: haul is a task of the helper", cards.some((c) => c.card === "haul"), true);
  const next = settle(lone);
  face("haul").querySelector(".card-tap")?.click();
  expect("one decision, the mix with haul in it", got.decided.length, 1);
  expect("haul joined with what was free", savedMix(got.decided[0])?.components.flatMap((c) => (c.kind === "card_share" && c.card === "haul" ? [c.share_bp] : [])), [4000]);
  const after = settle(next);
  expect("it is on the face, and the page was not closed", [shareOf(face("haul")), page.hidden], ["40%", false]);
  face("haul").querySelector(".card-tap")?.click();
  expect("a second tap takes it out", savedMix(got.decided[0])?.components.some((c) => c.kind === "card_share" && c.card === "haul"), false);
  expect("and the view's cards are as they were", after.cards.length, next.cards.length);
}

{  // a capped card is never held by a town mix: its tap does its next completion, as a hands one-off, and makes no rule
  const capped = { ...both, cards: both.cards.map((c) => (c.card === "carve" ? { ...c, cap: 3, share_bp: 0 } : c)) };
  const noCarve = { ...capped, mixes: capped.mixes.map((m) => ({ ...m, components: m.components.filter((c) => c.kind !== "card_share" || c.card !== "carve") })) };
  const { open, face, got, settle, root, page, rows } = rig(noCarve);
  open(1);
  expect("the face carries no note of its own", face("carve").querySelector(".card-need.oneoff"), null);
  face("carve").querySelector(".card-tap")?.click();
  expect("one decision, a tap of it", got.decided, [{ kind: "tap_card", card: "carve" }]);
  const ends = noCarve.at + 600;
  const held: View = {   // as the engine serves the tap: the mason's lane holds carve until it lands
    ...noCarve,
    lanes: noCarve.lanes.map((l) => (l.lane === "mason" ? { ...l, running_card: "carve", completes_at: ends, order: null } : l)),
    cards: noCarve.cards.map((c) => (c.card === "carve" ? { ...c, by: "tap" as const, completes_at: ends, bar: { start: noCarve.at, start_value: 0, rate: 1, limit: 600 }, bar_total: 600 } : c)),
  };
  settle(held, []);
  const tap = face("carve").querySelector(".card-tap");
  expect("running, pressed, and not tapped again while it runs", [face("carve").classList.contains("running"), tap?.getAttribute("aria-pressed"), tap?.disabled], [true, "true", true]);
  const mason = root.querySelectorAll(".town-person")[1] as FakeEl;
  const left = (s: number): string => catalog.format.duration(s);
  expect("the Town row's split is the one-off alone, its time left, then their split", texts(mason.querySelectorAll(".town-key > span")), [`Carve beams ${left(600)}`, "then Hew stone 70%"]);
  const mix = page.querySelector(".person-mix") as FakeEl;
  expect("so is their bar on the page", [texts(mix.querySelectorAll(".share-key-item")), mix.querySelector(".person-then")?.textContent], [[`Carve beams ${left(600)}`], "then Hew stone 70%"]);
  rows.tick(noCarve.at + 150);
  expect("the row counts down", texts(mason.querySelectorAll(".town-key > span"))[0], `Carve beams ${left(450)}`);
  expect("and the page's bar", texts(mix.querySelectorAll(".share-key-item")), [`Carve beams ${left(450)}`]);
  expect("the card counts down and fills", [face("carve").querySelector(".card-foot")?.textContent, (face("carve").querySelector(".card-fill") as FakeEl).style.transform], [left(450), "scaleX(0.25)"]);
  settle(noCarve, []);
  expect("once it lands their split is back", texts(mason.querySelectorAll(".town-key > span")), ["Hew stone 70%", "Mason, idle 30%"]);
  expect("and the page's bar", mix.querySelector(".person-then")?.hidden, true);
}

{  // no town mix yet: a new one, and the town's always rule pointed at it (saved, then the rules)
  const none = { ...both, mixes: both.mixes.filter((m) => m.id !== "town:main"), running_town_mix_id: null, town_mix_order: null, orders: both.orders.filter((o) => o.then.kind !== "switch_mix" || o.then.mix_id !== "town:main") };
  const { open, face, got } = rig(none);
  open(0);
  face("chop").querySelector(".card-tap")?.click();
  const mix = savedMix(got.decided[0]);
  expect("a new mix, not named for the game's", mix?.id.startsWith("town:"), false);
  expect("their only card takes all their time", mix?.components.map((c) => (c.kind === "card_share" ? c.share_bp : 0)), [10000]);
  const orders = got.decided[1]?.kind === "set_orders" ? got.decided[1].orders : [];
  expect("then the always rule", orders.at(-1), { when: { kind: "after_time", at: 0 }, then: { kind: "switch_mix", mix_id: mix?.id }, unless: [], or_else: [], below_next: false });
}

{  // a greyed town mix is still the one mix holding everyone: a person's edit saves it, and the others' shares stay under the always rule
  const at = both.orders.findIndex((o) => o.then.kind === "switch_mix" && o.then.mix_id === "town:main");
  const grey: View = {   // as fixtures/town.ts greys the helper's town: the mix greyed, its rule passed over, Haul retired
    ...both, running_town_mix_id: null, town_mix_order: null, greyed_mix_ids: ["town:main"],
    order_states: both.order_states.map((st, i) => (i === at ? "passed_over" : st)), cards: both.cards.filter((c) => c.card !== "haul"),
  };
  const { open, face, got } = rig(grey);
  expect("fixture: the mix is greyed and its rule passed over", [grey.greyed_mix_ids, grey.running_town_mix_id], [["town:main"], null]);
  open(0);
  face("chop").querySelector(".card-tap")?.click();
  expect("one decision, the mix saved and no new always rule", [got.decided.length, got.decided[0]?.kind], [1, "save_mix"]);
  const mix = savedMix(got.decided[0]);
  expect("it is the town's mix, the mason's shares still in it", [mix?.id, mix?.components.flatMap((c) => (c.kind === "card_share" && (c.card === "hew" || c.card === "carve") ? [c.card, c.share_bp] : []))], ["town:main", ["hew", 7000, "carve", 2000]]);
}

{  // a town mix a leave emptied is still the town's: Change opens it, and it is not offered as a hands mix
  const emptied = { ...both, mixes: both.mixes.map((m) => (m.id === "town:main" ? { ...m, components: [] } : m)) };
  const town = emptied.mixes.find((m) => m.id === "town:main") as Mix;
  expect("an emptied town:main is a town mix", isTownMix(catalog, emptied, town), true);
  expect("an empty mix the player named is a hands mix", isTownMix(catalog, emptied, { id: "mine", components: [] }), false);
  expect("Change opens it", townMixToEdit(catalog, emptied)?.id, "town:main");
}
