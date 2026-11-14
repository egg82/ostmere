// The town's mix on the page (CONTRACT.txt, "The town's mix"; game/town.ts, ui/townstrip.ts, ui/townedit.ts): in the Town
// tab, once people have joined, one block per person: their face and who, their shares and the idle rest, the card they are on;
// Change opens the town editor, one split per person; before the join the page is day two's lane row. The views are the
// engine's own (fixtures/townwire.ts: helper tapping Haul by a rule, shares yielded; mason on shares).
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { dayTwoStep } from "../fixtures/daytwo";
import { townStep } from "../fixtures/town";
import type { Card, Decision, Mix, View } from "../src/api/types";
import { panelView } from "../src/game/lanes";
import { Catalog } from "../src/game/catalog";
import { fixtureContent } from "../fixtures/content";
import { LaneRows } from "../src/ui/lanerows";
import { isTownMix, townMixToEdit } from "../src/game/town";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const both = townStep("town").view;
const helperOnly = townStep("townone").view;
const before = dayTwoStep("ruled", 100).view;

function rig(view: View) {
  const { ctx, got } = testContext();
  const rows = new LaneRows(ctx);
  document.body.replaceChildren(rows.root, rows.town.root);
  const root = fakeDocument.body.firstElementChild as FakeEl;
  rows.update(view);
  return { rows, root, got, editor: fakeDocument.body.children[1] as FakeEl };
}
const texts = (nodes: FakeEl[]): string[] => nodes.map((n) => n.textContent ?? "");
const saved = (d: Decision | undefined): Mix | null => (d?.kind === "save_mix" ? d.mix : null);

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

/** Change, then the editor's state. */
function opened(view: View) {
  const r = rig(view);
  r.root.querySelector(".town-change")?.click();
  return r;
}

{  // Change opens the town's mix: a split per person, only that person's own uncapped cards to add
  const { editor } = opened(both);
  expect("the editor is open", editor.hidden, false);
  expect("a split per person", texts(editor.querySelectorAll(".town-person .town-name")), ["Helper", "Mason"]);
  expect("the first person's rows", texts((editor.querySelectorAll(".town-person")[0] as FakeEl).querySelectorAll(".town-card-name")), ["Chop logs", "Haul water"]);
  const capped = { ...both, cards: both.cards.map((c) => (c.card === "carve" ? { ...c, cap: 3 } : c)) };
  const { editor: ed2 } = opened({ ...capped, mixes: capped.mixes.map((m) => ({ ...m, components: m.components.filter((c) => c.kind !== "card_share" || (c.card !== "hew" && c.card !== "carve")) })) });
  expect("a capped card is not offered; hew is, carve is not", ed2.querySelectorAll(".town-add").map((b) => b.dataset.card), ["hew"]);
}

{  // + and - move a share in steps within the person's whole time; Save sends that mix
  const { editor, got } = opened(both);
  const helper = (): FakeEl => editor.querySelectorAll(".town-person")[0] as FakeEl;
  helper().querySelector(".town-card .town-minus")?.click();   // chop 60% -> 55%
  expect("a step down", texts(helper().querySelectorAll(".town-card-share")), ["55%", "30%"]);
  helper().querySelectorAll(".town-card .town-plus")[1]?.click();   // haul 30% -> 35%
  helper().querySelectorAll(".town-card .town-plus")[1]?.click();   // 40%
  helper().querySelector(".town-card .town-plus")?.click();   // chop back to 60%: the person's whole time is given
  expect("the rest is gone", texts(helper().querySelectorAll(".town-key-item")), ["Chop logs 60%", "Haul water 40%"]);
  expect("no step past the whole", helper().querySelectorAll(".town-card .town-plus").map((b) => b.disabled), [true, true]);
  editor.querySelector(".editor-head .primary")?.click();
  const mix = saved(got.decided[0]);
  expect("the town's mix is saved", mix?.id, "town:main");
  expect("its shares", mix?.components.map((c) => (c.kind === "card_share" ? [c.card, c.share_bp] : null)), [["chop", 6000], ["haul", 4000], ["hew", 7000], ["carve", 2000]]);
  expect("the editor closes", editor.hidden, true);
  expect("one decision", got.decided.length, 1);
}

{  // no town mix yet: a new one, and the town's always rule pointed at it (saved, then the rules)
  const none = { ...both, mixes: both.mixes.filter((m) => m.id !== "town:main"), running_town_mix_id: null, town_mix_order: null, orders: both.orders.filter((o) => o.then.kind !== "switch_mix" || o.then.mix_id !== "town:main") };
  const { editor, got } = opened(none);
  editor.querySelector('.town-add[data-card="chop"]')?.click();
  editor.querySelector(".editor-head .primary")?.click();
  const mix = saved(got.decided[0]);
  expect("a new mix, not named for the game's", mix?.id.startsWith("town:"), false);
  expect("with the card at half", mix?.components.map((c) => (c.kind === "card_share" ? c.share_bp : 0)), [5000]);
  const orders = got.decided[1]?.kind === "set_orders" ? got.decided[1].orders : [];
  expect("then the always rule", orders.at(-1), { when: { kind: "after_time", at: 0 }, then: { kind: "switch_mix", mix_id: mix?.id } });
}

{  // a town mix a leave emptied is still the town's: Change opens it, and it is not offered as a hands mix
  const emptied = { ...both, mixes: both.mixes.map((m) => (m.id === "town:main" ? { ...m, components: [] } : m)) };
  const town = emptied.mixes.find((m) => m.id === "town:main") as Mix;
  expect("an emptied town:main is a town mix", isTownMix(catalog, emptied, town), true);
  expect("an empty mix the player named is a hands mix", isTownMix(catalog, emptied, { id: "mine", components: [] }), false);
  expect("Change opens it", townMixToEdit(catalog, emptied)?.id, "town:main");
}
