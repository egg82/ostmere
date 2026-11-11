// The Camp bar past a held level (ui/camp.ts; CONTRACT.txt, the Camp bar): a held level a step lifts counts as
// reached once that step has finished and the bar has filled to it; one nothing lifts never counts.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { UI } from "../src/game/text";
import { CampBar } from "../src/ui/camp";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function check(label: string, block: () => void): void {
  try { block(); } catch (e) { throw new Error(`${label}: ${(e as Error).message}`); }
}

const AT = 100;
const camp = fixtureContent.camp!;
const lifted = (by: string[]): Catalog => new Catalog({
  ...fixtureContent, camp: { ...camp, camp_levels: camp.camp_levels.map((l) => (l.held ? { ...l, lifted_by: by } : l)) },
} satisfies Content);
const base = fixtureStep("restrule", AT).view;

/** The view with the camp store at `items` (a still line, so the sample is exact) and `done` completed. */
function at(items: number, done: string[]): View {
  const ledger = base.ledger.map((l) => (l.store === "camp" ? { ...l, segment: { start: AT, start_value: items * Q, rate: 0, limit: null }, cap: 1000 * Q } : l));
  return { ...base, ledger, completed: done.map((card) => ({ card, completions: 1 })) };
}

function bar(catalog: Catalog, view: View): { level: string; next: string | null } {
  const { ctx } = testContext(undefined, catalog);
  const b = new CampBar(ctx);
  b.update(view);
  b.tick(AT);
  const next = b.root.querySelector(".camp-next") as HTMLElement;
  return { level: b.root.querySelector(".camp-level")?.textContent ?? "", next: next.hidden ? null : next.textContent };
}
const levelText = (catalog: Catalog, n: number): string =>
  `${catalog.storeLabel("camp")} ${catalog.text.fill(UI.level, { n: catalog.format.count(n) })}`;

// The controls: below the held level it is level 1, the held marker next; a held level nothing lifts never counts.
{
  const c = lifted(["take_stock"]);
  expect("below the held level", bar(c, at(150, ["take_stock"])).level, levelText(c, 1));
  const none = lifted([]);
  const held = bar(none, at(200, []));
  expect("a held level nothing lifts, filled to: still level 1", held.level, levelText(none, 1));
  expect("its marker still showing", held.next !== null, true);
  expect("lifted by a step not yet finished: level 1", bar(c, at(200, [])).level, levelText(c, 1));
}

check("a lifted held level counts once its step has finished", () => {
  const c = lifted(["take_stock"]);
  const past = bar(c, at(200, ["take_stock"]));
  expect("level 2", past.level, levelText(c, 2));
  expect("no marker past the last level", past.next, null);
});

check("a held level two steps can lift counts once either has finished", () => {
  const c = lifted(["walk_a", "walk_b"]);
  expect("neither finished: level 1", bar(c, at(200, [])).level, levelText(c, 1));
  expect("the first finished: level 2", bar(c, at(200, ["walk_a"])).level, levelText(c, 2));
  expect("the second finished: level 2", bar(c, at(200, ["walk_b"])).level, levelText(c, 2));
});

// The marker is a sentence (decisions.md, "Two registers"): the level it names, then its pays words with their own
// {from} and {to} filled from pays_from and pays_to; never arrow notation. A level with no number keeps its words.
check("a marker with a number reads as a sentence naming its level", () => {
  const c = lifted(["take_stock"]);
  expect("level 1's marker", bar(c, at(10, [])).next, "level 1: wall dries 5 wood at a time, was 3");
  expect("the held level's marker", bar(c, at(60, [])).next, "level 2: something new");
});

// A marker never names what the player has not unlocked: level 1 pays something about the smoked store, so its words
// wait until that store is unlocked, and until then it reads UI.nextUnnamed: there is a next thing to reach, not yet named.
const naming = new Catalog({
  ...fixtureContent,
  camp: { ...camp, camp_levels: camp.camp_levels.map((l, i) => (i === 0 ? { ...l, names: [{ category: "store", id: "smoked" }] } : l)) },
} satisfies Content);
check("a marker naming a locked store shows no words, only that there is a next", () => {
  expect("before the store: ?", bar(naming, at(10, [])).next, naming.text.get(UI.nextUnnamed));
});
{
  const v = at(10, []);
  const open = { ...v, unlocked: [...v.unlocked, { category: "store" as const, id: "smoked" }] };
  expect("once unlocked: its words", bar(naming, open).next !== null, true);
}

// The store unlocks with no level change: the same bar words the marker at its next tick.
{
  const { ctx } = testContext(undefined, naming);
  const b = new CampBar(ctx);
  const v = at(10, []);
  b.update(v);
  b.tick(AT);
  const next = b.root.querySelector(".camp-next") as HTMLElement;
  expect("locked: ?", next.textContent, naming.text.get(UI.nextUnnamed));
  b.update({ ...v, unlocked: [...v.unlocked, { category: "store", id: "smoked" }] });
  b.tick(AT);
  expect("unlocked: its words", next.textContent === naming.text.get(UI.nextUnnamed), false);
}

// The bar arrives at its first level: hidden while no level is reached, drawn from the first one on, already pointing
// at the next. Reached live, it arrives (its turn in the queue) with its level burst; a page opened past it just draws it.
{
  const c = lifted(["take_stock"]);
  const { ctx } = testContext(undefined, c);
  const got: string[] = [];
  const b = new CampBar({ ...ctx, arrivals: { arrive: (_n, kind, id) => { got.push(`arrive:${kind}:${id}`); }, effect: (_n, _k, run) => { got.push("effect"); run(); }, line: () => undefined, busy: false } });
  b.update(at(10, []));
  b.tick(AT);
  expect("no level yet: not drawn", b.root.hidden, true);
  b.update(at(60, []));
  b.tick(AT);
  expect("its first level: drawn", b.root.hidden, false);
  expect("pointing at the next", (b.root.querySelector(".camp-next") as HTMLElement).hidden, false);
  expect("it arrived, with its level burst", got, ["arrive:chip:camp", "effect"]);
}
{
  const { ctx } = testContext(undefined, lifted(["take_stock"]));
  const got: string[] = [];
  const b = new CampBar({ ...ctx, arrivals: { arrive: () => { got.push("arrive"); }, effect: () => { got.push("effect"); }, line: () => undefined, busy: false } });
  b.update(at(60, []));
  b.tick(AT);
  expect("opened past level 1: drawn", b.root.hidden, false);
  expect("with no arrival or burst", got, []);
}
