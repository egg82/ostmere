// A return's figures (game/chapter.ts) and their words (game/chronwords.ts, chapterRows): what the return found
// against what the player left, kept with the visit in one write and joined by the later return; and the session takes
// them as a return lands.
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { GameApi } from "../src/api/api";
import type { Chapter, LedgerLine, NewSave, RuleRun, SavePresentation, Step, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { chapterOf } from "../src/game/chapter";
import { chapterRows } from "../src/game/chronwords";
import { Keeps, NEW_SAVE } from "../src/game/keeps";
import { mergeSavePresentation, sendableSave } from "../src/game/presentation";
import { ruleText } from "../src/game/rulerows";
import { Session } from "../src/game/session";
import { UI } from "../src/game/text";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const { text } = catalog;
const LEFT = 10_000, BACK = LEFT + 3600;
const still = (line: LedgerLine, items: number): LedgerLine => ({ ...line, segment: { start: 0, start_value: items * Q, rate: 0, limit: null } });
const base = fixtureStep("rulestab", LEFT);

function viewAt(at: number, stores: Record<string, number>, levels: Record<string, number>, unlockedStores = ["wood", "warmth", "stone", "camp"]): View {
  return {
    ...base.view, at,
    ledger: base.view.ledger.map((l) => still(l, stores[l.store] ?? 0)),
    skills: base.view.skills.map((s) => ({ ...s, level: levels[s.skill] ?? s.level })),
    unlocked: [...base.view.unlocked.filter((u) => u.category !== "store"), ...unlockedStores.map((id) => ({ category: "store" as const, id }))],
  };
}

const [wood, , tired, shelter] = base.view.orders;
if (!wood || !tired || !shelter) throw new Error("rulestab's rules moved");
const run = (order: typeof wood, starts: number, on: number | null, off: number | null): RuleRun =>
  ({ order, starts, on_at: on, on_level: null, off_at: off, off_level: null, ended: null, made: [] });

{
  const prev = viewAt(LEFT, { wood: 14.5, warmth: 38, stone: 3, camp: 60 }, { foraging: 2, firecraft: 3 });
  const next = viewAt(BACK, { wood: 340, warmth: 12, stone: 3.9, camp: 230 }, { foraging: 4, firecraft: 1 }, ["wood", "warmth", "stone", "camp"]);
  const before = [run(wood, 3, LEFT - 500, LEFT - 100), run(tired, 1, LEFT - 900, null), run(shelter, 7, LEFT - 50, null)];
  const after = [run(wood, 5, BACK - 1500, BACK - 900), run(tired, 1, LEFT - 900, BACK - 60), run(shelter, 7, LEFT - 50, null)];
  const camp = { ...fixtureContent, camp: { ...fixtureContent.camp!, camp_levels: fixtureContent.camp!.camp_levels.map((l) => ({ ...l, held: false })) } };
  const c = chapterOf(camp, prev, before, next, after);
  expect("the return's seconds", [c.left, c.back], [LEFT, BACK]);
  expect("each met store whose whole items moved, in quantity units; one that moved less than an item is not",
    c.stores, [{ id: "wood", was: 14.5 * Q, now: 340 * Q }, { id: "warmth", was: 38 * Q, now: 12 * Q }]);
  expect("each skill that rose, not one that fell (a prestige)", c.levels, [{ id: "foraging", was: 2, now: 4 }]);
  expect("the Camp's level, as its bar counts it", c.camp, { id: "camp", was: 1, now: 2 });
  expect("a rule that came on while away, with the starts since the Step before; one that only let go; none that ran before",
    c.rules, [{ order: wood, came_on: true, times: 2 }, { order: tired, came_on: false, times: 1 }]);
  const same = chapterOf(fixtureContent, prev, after, next, after);
  expect("with no Step before to count from, a rule that came on counts once", same.rules[0]?.times, 1);
  const unmet = chapterOf(fixtureContent, prev, [], viewAt(BACK, { wood: 14, warmth: 38, stone: 9, camp: 60 }, {}, ["wood", "warmth", "camp"]), []);
  expect("a store the player has not met is left out", unmet.stores, []);
  expect("a held Camp level is not counted", chapterOf(fixtureContent, prev, [], next, []).camp, null);

  const store = (id: string) => catalog.storeLabel(id);
  const rows = chapterRows(catalog, c, 2);
  expect("rows: stores gained then lost, the Camp before the skills, each rule, the asks waiting", rows, [
    ["stores", [`+326 ${store("wood")}`, `−26 ${store("warmth")}`]],
    ["levels", [`${store("camp")} 1 → 2`, `${catalog.skillLabel("foraging")} 2 → 4`]],
    ["rules", [text.fill(UI.chapterTimes, { rule: ruleText(catalog, wood)!, n: "2" }), text.fill(UI.chronRuleOff, { rule: ruleText(catalog, tired)! })]],
    ["waiting", ["2 asks"]],
  ]);
  expect("a rule that came on once says so without a count", chapterRows(catalog, { ...c, rules: [{ order: wood, came_on: true, times: 1 }] }, 0)[2],
    ["rules", [text.fill(UI.chronRuleOn, { rule: ruleText(catalog, wood)! })]]);
  expect("only what has something; one ask", chapterRows(catalog, { left: 0, back: 1, stores: [], levels: [], camp: null, rules: [] }, 1), [["waiting", ["1 ask"]]]);
  expect("no figures kept: only what waits", chapterRows(catalog, null, 0), []);
}
{
  const chapter: Chapter = { left: 100, back: 4000, stores: [], levels: [], camp: null, rules: [] };
  const keeps = new Keeps();
  keeps.keepReturn(100, 1000, { ...chapter, back: 1000 });
  expect("a return too short to be a visit keeps no chapter", [keeps.visits(), keeps.chapter()], [[], null]);
  keeps.keepReturn(100, 4000, chapter);
  expect("a visit keeps its chapter", [keeps.visits(), keeps.chapter()], [[{ left: 100, back: 4000 }], chapter]);
  const later = { ...chapter, left: 9000, back: 13000 };
  expect("of two copies the later return's chapter wins, either way round", [
    mergeSavePresentation({ ...NEW_SAVE, chapter }, { ...NEW_SAVE, chapter: later }).chapter,
    mergeSavePresentation({ ...NEW_SAVE, chapter: later }, { ...NEW_SAVE, chapter }).chapter,
    mergeSavePresentation({ ...NEW_SAVE, chapter }, NEW_SAVE).chapter], [later, later, chapter]);
  expect("a write names no chapter until one is kept", ["chapter" in sendableSave(NEW_SAVE), sendableSave({ ...NEW_SAVE, chapter }).chapter], [false, chapter]);
}
{  // a session's return: the visit and its figures in one write
  const none = (): Promise<never> => Promise.reject(new Error("not in this test"));
  const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };
  const first: Step = { ...base, save_id: 7, lines: [], view: viewAt(LEFT, { wood: 14 }, {}) };
  const back: Step = { ...first, view: viewAt(BACK, { wood: 90 }, {}) };
  const saves: SavePresentation[] = [];
  const api: GameApi = {
    content: () => Promise.resolve(fixtureContent), me: none, begin: () => Promise.resolve<NewSave>({ save, presentation: NEW_SAVE, step: first }), open: none,
    savedView: none, advance: () => Promise.resolve(back), forecast: none, decide: none, dryRun: none, sendFeedback: none, makeCode: none, makeWords: none,
    join: none, games: none, deleteGame: none, restoreGame: none, devices: none, removeDevice: none, putMePresentation: none, putMeSettings: none,
    putSavePresentation: (_id, p) => { saves.push(p); return Promise.resolve(p); },
  };
  const session = new Session(api, {
    started() { /* drawn */ }, stepped() { /* drawn */ }, build() { /* self-update */ }, refused() { /* none */ },
    connected() { /* none */ }, lost() { /* none */ }, limited() { /* none */ }, catchingUp() { /* none */ },
  });
  await session.begin();
  await session.advance(true);
  expect("one write holds the visit and the figures", saves.map((p) => [p.visits, p.chapter?.stores]),
    [[[{ left: LEFT, back: BACK }], [{ id: "wood", was: 14 * Q, now: 90 * Q }]]]);
}
