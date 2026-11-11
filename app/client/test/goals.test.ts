// What a story beat waits on, on screen (CONTRACT.txt, "Goals"; game/story.ts): the card, the ledger line and the skill
// row it waits on carry the story mark and nothing else does; a store with no line yet is a row of its own in the Camp
// bar's box; a wait on the clock is a plain line under them, with its time and the store that keeps it moving, or that
// store alone while it is dry.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Goal, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { storyMarks } from "../src/game/story";
import { UI } from "../src/game/text";
import { CampBar } from "../src/ui/camp";
import { WaitLine } from "../src/ui/waitline";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const catalog = new Catalog(fixtureContent);
const mid = fixtureStep("mid", AT).view;
const goal = (over: Partial<Goal>): Goal => ({ kind: "card", store: null, card: null, skill: null, target: 0, value: null, at: null, feeds: [], ...over });
const clock = goal({ kind: "clock", at: AT + 2 * 3600, feeds: ["wood"] });

{
  const marks = storyMarks(catalog, { ...mid, goals: [goal({ card: "look", target: 1 }), goal({ kind: "store", store: "wood", target: 30 * Q }), goal({ kind: "level", skill: "foraging", target: 3 }), clock] });
  expect("the card, the skill", [[...marks.cards], [...marks.skills]], [["look"], ["foraging"]]);
  expect("the store's line, once, though the clock waits on it too", [...marks.stores], ["wood"]);
  expect("nothing unlined", marks.unlined, []);
  const none = storyMarks(catalog, { ...mid, goals: [] });
  expect("no goals: nothing marked", [none.cards.size, none.stores.size, none.skills.size, none.clock], [0, 0, 0, null]);
}

function campRows(view: View): { hidden: boolean; rows: string[] } {
  const { ctx } = testContext(undefined, catalog);
  const b = new CampBar(ctx);
  b.update(view);
  b.tick(AT);
  return { hidden: b.root.hidden, rows: ([...b.root.querySelectorAll(".goal-what")] as HTMLElement[]).map((r) => r.textContent ?? "") };
}

{
  const start = fixtureStep("start", AT).view;   // nothing unlocked: no store has a line, no Camp level
  const stone = goal({ kind: "store", store: "stone", target: 3 * Q, value: { start: AT, start_value: Q, rate: 0, limit: null } });
  expect("no goals: the box is hidden", campRows({ ...start, goals: [] }).hidden, true);
  expect("a store with no line yet is a row of its own", campRows({ ...start, goals: [stone] }),
    { hidden: false, rows: [`${catalog.storeLabel("stone")} ${catalog.format.amount(Q, 3 * Q)}`] });
}

function wait(view: View): { hidden: boolean; tag: string; line: string; tabbable: number } {
  const { ctx } = testContext(undefined, catalog);
  const w = new WaitLine(ctx);
  w.update(view);
  w.tick(AT);
  return { hidden: w.root.hidden, tag: w.root.tagName.toLowerCase(), line: w.root.textContent ?? "", tabbable: w.root.querySelectorAll("button, a, input, [tabindex]").length };
}

{
  const t = catalog.text, f = catalog.format, wood = catalog.storeLabel("wood");
  const title = t.get(UI.nextUnnamed);
  const head = title.charAt(0).toUpperCase() + title.slice(1);
  const time = t.fill(UI.goalIn, { d: f.duration(2 * 3600) });
  expect("no clock: no wait line", wait({ ...mid, goals: [] }), { hidden: true, tag: "p", line: "", tabbable: 0 });
  expect("a clock: its time and what keeps it moving, plain text, nothing to tap", wait({ ...mid, goals: [clock] }),
    { hidden: false, tag: "p", line: `${head} · ${time} · ${t.fill(UI.goalWhile, { store: wood })}`, tabbable: 0 });
  expect("stopped on a dry store: that store alone", wait({ ...mid, goals: [{ ...clock, at: null }] }).line, `${head} · ${t.fill(UI.goalPaused, { store: wood })}`);
  expect("a clock nothing feeds: its time alone", wait({ ...mid, goals: [{ ...clock, feeds: [] }] }).line, `${head} · ${time}`);
}
