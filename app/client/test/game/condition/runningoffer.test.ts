// The When row offers "while {card} is running" exactly where set_orders takes it (contract/endpoints.txt, "Decisions"): on a
// rule tapping a person's lane, every card of another lane in play, the hands' included, and none of its own lane; on a
// hands tap, a mix switch or no action yet, none. Each offer builds the one Running shape and reads back as itself.
import { fixtureContent } from "../../../fixtures/content";
import { townStep } from "../../../fixtures/town";
import { Catalog } from "../../../src/game/page/catalog";
import { subjectChoices } from "../../../src/game/condition/ruleoffers";
import { buildSubject, readSubject, subjectKey, subjectWords } from "../../../src/game/condition/subjectrule";

const catalog = new Catalog(fixtureContent);
const view = townStep("town").view;
const failures: string[] = [];
const persons = view.cards.filter((c) => catalog.laneOf(c.card) !== "hands");
if (persons.length < 2 || !view.cards.some((c) => catalog.laneOf(c.card) === "hands")) throw new Error("the town fixture has no person's or hands card: the check looked at nothing");

for (const { card } of persons) {
  const lane = catalog.laneOf(card);
  const offered = subjectChoices(catalog, view, [{ kind: "tap_card", card }]).running;
  const want = view.cards.filter((c) => catalog.laneOf(c.card) !== lane).map((c) => c.card).sort();
  const got = offered.map((r) => (r.kind === "running" ? r.card : `not running: ${r.kind}`)).sort();
  if (JSON.stringify(got) !== JSON.stringify(want)) failures.push(`${card}: offered ${got.join(",")}, want ${want.join(",")}`);
  for (const rule of offered) {
    const when = buildSubject(catalog, rule);
    const back = readSubject(catalog, when);
    if (when.kind === "after_time" || when.watched.kind !== "running" || when.kind !== "at_least" || when.value !== 1 || when.release !== 1) failures.push(`${subjectKey(rule)} builds ${JSON.stringify(when)}`);
    if (!back || subjectKey(back) !== subjectKey(rule)) failures.push(`${subjectKey(rule)} reads back as ${back ? subjectKey(back) : "nothing"}`);
    if (rule.kind === "running" && !subjectWords(catalog, view, rule).includes(catalog.cardLabel(rule.card))) failures.push(`${subjectKey(rule)} words: ${subjectWords(catalog, view, rule)}`);
  }
}
const hands = view.cards.find((c) => catalog.laneOf(c.card) === "hands")?.card ?? "";
for (const [name, then] of [["a hands tap", { kind: "tap_card" as const, card: hands }], ["a mix switch", { kind: "switch_mix" as const, mix_id: view.mixes[0]?.id ?? "" }], ["no action", null]] as const) {
  const n = subjectChoices(catalog, view, [then]).running.length;
  if (n !== 0) failures.push(`${name} is offered ${n} running cards`);
}
const [first, other] = [persons[0]!.card, persons.find((c) => catalog.laneOf(c.card) !== catalog.laneOf(persons[0]!.card))!.card];
const taps = (...cards: string[]) => cards.map((card) => ({ kind: "tap_card" as const, card }));
if (subjectChoices(catalog, view, taps(first, other)).running.length !== 0) failures.push("a fallback on another lane is offered running");
if (subjectChoices(catalog, view, [...taps(first), { kind: "switch_mix", mix_id: view.mixes[0]!.id }]).running.length !== 0) failures.push("a mix-switch fallback is offered running");
if (subjectChoices(catalog, view, taps(first, first)).running.length === 0) failures.push("a fallback on the same lane lost the offer");
if (failures.length > 0) throw new Error(failures.slice(0, 5).join("; "));
