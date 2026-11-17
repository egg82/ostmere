// The rule editors' pickers list cards under the Tasks page's sections, in the page's order, each section by shown name,
// with the mixes after the cards (docs/decisions/mixes.md, "the rule editors"). The page's own section of a card is read
// off ui/cardgroups.ts, so a picker that puts a card elsewhere than the page does fails here.
import { fakeDocument, FakeEl, install } from "./fake-dom";
import { Catalog } from "../src/game/catalog";
import { testContext } from "./context";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { CardGroups } from "../src/ui/cardgroups";
import { UI } from "../src/game/text";
import { RulesTab } from "../src/ui/rules";

install();

const failures: string[] = [];
function check(name: string, run: () => void): void {
  try { run(); } catch (e) { failures.push(`${name}: ${e instanceof Error ? e.message : String(e)}`); }
}
function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const q = (root: FakeEl, sel: string): FakeEl[] => root.querySelectorAll(sel);
const one = (root: FakeEl, sel: string): FakeEl => {
  const found = q(root, sel)[0];
  if (!found) throw new Error(`no ${sel}`);
  return found;
};

const catalog = new Catalog(fixtureContent);
const base = fixtureStep("rulestab", 100).view;
const gatherCard = base.cards.find((c) => c.card === "gather")!;
const OTHER = ["shelter", "smoke_catch", "smoke_roots", "hew", "carve", "chop", "haul", "hatchet", "stool", "rest", "forage"];
const view: View = { ...base, cards: [...base.cards, ...OTHER.filter((c) => !base.cards.some((b) => b.card === c)).map((card) => ({ ...gatherCard, card }))] };

interface Seen { card: string | null; mix: string | null; section: string }

/** The one node mounted on the page: a real-typed root seen as the fake element it is. */
function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

/** The Tasks page's section of `card`, as its own lane group draws it: the lane and the heading under it. */
const pageGroups = new CardGroups(document.createElement("div"), catalog);
function pageSection(card: string): { lane: string; heading: string } {
  const node = mounted(pageGroups.of(card).node);
  return { lane: node.dataset.lane ?? "", heading: q(node, ".lane-tag")[0]?.textContent ?? "" };
}
/** The page's order of sections: the hands first, then the lanes as the content lists them, a lane's crafts last. */
const pageRank = (card: string): number => {
  const s = pageSection(card);
  return ["hands", ...catalog.lanes.keys()].indexOf(s.lane) * 2 + Number(s.heading === catalog.text.get(UI.craftHeading));
};

/** A picker's children as the choices it lists, each with the heading row last above it. */
function walk(box: FakeEl): Seen[] {
  let section = "";
  const out: Seen[] = [];
  for (const k of box.children) {
    if (k.classList.contains("cond-subhead")) section = k.textContent ?? "";
    else if (k.dataset.card !== undefined || k.dataset.mix !== undefined) out.push({ card: k.dataset.card ?? null, mix: k.dataset.mix ?? null, section });
  }
  return out;
}

function mount(v: View, c = catalog): { tab: RulesTab; root: FakeEl } {
  const { ctx } = testContext(undefined, c);
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  const root = mounted(tab.root);
  tab.update(v);
  return { tab, root };
}

function holdsOrder(name: string, seen: Seen[]): void {
  const cards = seen.flatMap((s) => (s.card === null ? [] : [s.card]));
  expect(`${name}: sections in the page's order`, cards.map(pageRank), [...cards.map(pageRank)].sort((a, b) => a - b));
  for (const s of seen) if (s.card !== null) expect(`${name}: ${s.card} under the page's heading for it`, s.section, pageSection(s.card).heading);
  for (const rank of new Set(cards.map(pageRank))) {
    const names = cards.filter((c) => pageRank(c) === rank).map((c) => catalog.cardLabel(c));
    expect(`${name}: section ${rank} by name`, names, [...names].sort((a, b) => a.localeCompare(b)));
  }
  const lastCard = seen.map((s) => s.card !== null).lastIndexOf(true);
  const firstMix = seen.findIndex((s) => s.mix !== null);
  if (firstMix >= 0) expect(`${name}: mixes after every card`, firstMix > lastCard, true);
}

check("the Do picker: the page's sections, by name, the mixes last", () => {
  const { tab, root } = mount(view);
  tab.open(view, 0);
  const seen = walk(one(root, ".cond .cond-mixes"));
  expect("a card from each lane is offered", seen.filter((s) => s.card !== null).length >= OTHER.length, true);
  expect("sections drawn", new Set(seen.map((s) => s.section)).size > 2, true);
  expect("some mix is offered", seen.some((s) => s.mix !== null), true);
  expect("the mixes sit under the Mixes heading", seen.filter((s) => s.mix !== null).map((s) => s.section), seen.filter((s) => s.mix !== null).map(() => catalog.text.get(UI.mixesHeading)));
  holdsOrder("do", seen);
});

check("the Or else picker lists the same way", () => {
  const { tab, root } = mount(view);
  tab.open(view, 0);
  one(root, ".cond-else-add").click();
  const seen = walk(one(root, ".cond-else-pick"));
  expect("cards offered", seen.filter((s) => s.card !== null).length > 3, true);
  expect("mixes offered", seen.some((s) => s.mix !== null), true);
  expect("the mixes sit under the Mixes heading", seen.filter((s) => s.mix !== null).every((s) => s.section === catalog.text.get(UI.mixesHeading)), true);
  holdsOrder("else", seen);
});

check("the quick add's action choice lists the same way", () => {
  const rising = dayOneStep("rising", 100).view;
  const { root } = mount(rising, new Catalog(fixtureContent));
  one(root, ".rules-new").click();
  one(root, ".cond-task[data-card=\"smoke_catch\"]").click();
  one(root, ".cond-store[data-store=\"smoked\"]").click();
  const select = one(root, ".cond-sentence .quick-action select");
  const seen: Seen[] = [];
  for (const g of select.children) for (const o of g.children) seen.push({ card: o.value, mix: null, section: g.getAttribute("label") ?? "" });
  expect("cards offered", seen.length > 3, true);
  expect("sections drawn", new Set(seen.map((x) => x.section)).size > 1, true);
  holdsOrder("quick", seen);
});

check("the full editor's tasks to count (When) list the same way", () => {
  const capped: View = { ...view, cards: view.cards.map((c) => ({ ...c, cap: c.cap ?? c.completions + 5 })) };   // only a capped task is counted
  const { tab, root } = mount(capped);
  tab.open(capped, 0);
  const seen = walk(one(root, ".cond .cond-stores"));
  const counted = q(root, ".cond-subject").flatMap((b) => (b.dataset.subject?.startsWith("task:") ? [b.dataset.subject.slice(5)] : []));
  expect("tasks offered", counted.length > 3, true);
  expect("sections drawn", seen.length, 0);
  expect("sections in the page's order", counted.map(pageRank), [...counted.map(pageRank)].sort((a, b) => a - b));
  const names = counted.filter((c) => pageRank(c) === pageRank("gather")).map((c) => catalog.cardLabel(c));
  expect("the hands' by name", names, [...names].sort((a, b) => a.localeCompare(b)));
});

if (failures.length > 0) throw new Error(failures.join("\n"));
console.log("rulepickerorder: ok");
