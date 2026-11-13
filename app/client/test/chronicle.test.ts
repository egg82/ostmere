// The chronicle's routing (game/chronicle.ts): one filter per kind, the strip holding the story filter's kinds alone,
// entries placed by time and capped per filter; which stretch an entry belongs to; and the words (game/chronwords.ts).
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import { KEEP, ROUTES, added, filtersOf, held, inStrip, stretches, tally, type Entry, type EntryKind } from "../src/game/chronicle";
import { awayTitle, causeWords, filterCount } from "../src/game/chronwords";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const l = (at: number, kind: EntryKind = "story"): Entry => ({ text: String(at), at, kind, cause: null });
const lines = [l(10), l(20, "tap"), l(30), l(40, "find"), l(50)];
const shape = (v: Array<{ left: number; back: number }>): Array<[number | null, number[]]> =>
  stretches(lines, v).map((s) => [s.visit?.left ?? null, s.lines.map((x) => x.at)]);

const kinds: EntryKind[] = ["story", "tap", "body", "find", "level", "rule", "fight", "talk"];
expect("the strip holds story, taps and the body alone", kinds.filter(inStrip), ["story", "tap", "body"]);
expect("town talk has its own filter, never the strip", [ROUTES.talk, inStrip("talk")], ["talk", false]);
expect("every kind has a filter", kinds.map((k) => ROUTES[k]), ["story", "story", "story", "finds", "levels", "rules", "fights", "talk"]);

expect("no visit: one stretch", shape([]), [[null, [10, 20, 30, 40, 50]]]);
expect("a line at the second the player left is before the visit", shape([{ left: 20, back: 35 }]), [[null, [10, 20]], [20, [30, 40, 50]]]);
expect("visits split in order, whatever order they are kept in", shape([{ left: 40, back: 45 }, { left: 10, back: 15 }]),
  [[null, [10]], [10, [20, 30, 40]], [40, [50]]]);
expect("a visit past the last line opens nothing", shape([{ left: 90, back: 99 }]), [[null, [10, 20, 30, 40, 50]]]);
expect("a chronicle with no lines has no stretch", stretches([], [{ left: 1, back: 2 }]), []);
expect("the tally counts filters in their order", tally([...lines, l(5, "rule")].reverse()), [["story", 4], ["finds", 1], ["rules", 1]]);
expect("a filter holds its kinds", held(lines, "story").map((e) => e.at), [10, 20, 30, 50]);
expect("the filters offered are those with an entry", filtersOf([l(1, "rule"), l(2, "body")]), ["story", "rules"]);

{
  let es: Entry[] = [];
  for (const e of [l(10), l(30), l(20, "rule"), l(30, "find")]) es = added(es, e);
  expect("an entry from the past takes its place by time, a tie goes after", es.map((e) => `${e.kind}${e.at}`), ["story10", "rule20", "story30", "find30"]);
  for (let i = 0; i < KEEP; i += 1) es = added(es, l(100 + i, "talk"));
  expect("a busy filter fills to its cap", held(es, "talk").length, KEEP);
  es = added(es, l(9999, "talk"));
  expect("past it, its own oldest goes", [held(es, "talk").length, held(es, "talk")[0]?.at], [KEEP, 101]);
  expect("and no other filter loses an entry", held(es, "story").length + held(es, "finds").length + held(es, "rules").length, 4);
}

const catalog = new Catalog(fixtureContent);
const { text } = catalog;
expect("minutes", awayTitle(text, 54 * 60 + 20), "Away 54m");
expect("an hour and some", awayTitle(text, 5 * 3600 + 3 * 60), "Away 5h 3m");
expect("whole hours", awayTitle(text, 5 * 3600), "Away 5h");
expect("a day or more is days", awayTitle(text, 50 * 3600), "Away 2d");
expect("a filter's count", filterCount(text, "finds", 3), "Finds 3");

const Q = fixtureContent.scales.quantity_per_item;
const cause = (key: string): string | null => causeWords(catalog, catalog.lineCause(key));
expect("no cause, no words", cause("line.1"), null);
expect("the clock", cause("line.2"), "time");
expect("a runner by its label", cause("line.3"), catalog.runnerLabel("stand"));
expect("a level", cause("line.6"), `${catalog.skillLabel("foraging")} 2`);
expect("a Camp level", cause("line.7"), "Camp level 1");
expect("a store reached, in whole items", cause("line.offer"), `10 ${catalog.storeLabel("wood")}`);
expect("a store fallen to", causeWords(catalog, { kind: "when", when: { kind: "at_most", watched: { kind: "store_value", store: "wood" }, value: 0, release: Q } }),
  `down to 0 ${catalog.storeLabel("wood")}`);
expect("one of a skill's levels", causeWords(catalog, { kind: "skill", skill: "foraging" }), `${catalog.skillLabel("foraging")} level up`);
expect("a card's count", causeWords(catalog, { kind: "when", when: { kind: "at_least", watched: { kind: "card_count", card: "look" }, value: 3, release: 3 } }),
  `${catalog.cardLabel("look")} ×3`);
expect("an answer", causeWords(catalog, { kind: "answer", offer: "ask" }), "your answer");
expect("a card unlocked", causeWords(catalog, { kind: "when", when: { kind: "at_least", watched: { kind: "unlocked", unlock: { category: "card", id: "look" } }, value: 1, release: 1 } }),
  catalog.cardLabel("look"));
