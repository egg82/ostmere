// The front page's selection (begin.ts, ui/frontdress.ts) with the real wiring and a spy for the game: the main button
// opens the selected game, and while New game is selected it is Begin and starts a new game instead of opening a save.
// Drawing a game's picture reads its view and never opens the save (api.open stays uncalled until a tap opens one).
import { FakeEl, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { ApiFailure, type GameApi } from "../src/api/api";
import { Text as Words } from "../src/game/text";
import type { SaveInfo } from "../src/api/types";
import { wireBegin, type PlayGame } from "../src/begin";
import { NEW_SAVE } from "../src/game/keeps";

install();
const text = new Words(fixtureContent);
Object.assign(globalThis, { HTMLButtonElement: FakeEl, fetch: () => Promise.resolve(new Response("", { status: 404 })) });   // no scene art: the pictures are dark frames

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const later = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 10));
const view = fixtureStep("standing", 100, {}, 0).view;
const at = new Date(Date.now() - 3 * 3_600_000).toISOString();
const save = (id: number): SaveInfo => ({ save_id: id, number: id, decisions: 0, game_time: 0, ended_at: null, started_at: at, played_at: at, camp_level: id });
const no = (): Promise<never> => Promise.reject(new Error("not in these tests"));

function page(): Record<string, FakeEl> {
  document.body.replaceChildren();
  const made: Record<string, FakeEl> = {};
  for (const id of ["stage", "ledger", "sub", "begin", "rail", "keep", "limited", "have", "framed"]) {
    const node = fakeDocument.createElement(id === "begin" ? "button" : "div");
    node.setAttribute("id", id);
    fakeDocument.body.append(node);
    made[id] = node;
  }
  made["begin"]!.hidden = true;
  made["rail"]!.hidden = true;
  return made;
}

async function rig(ids: number[], beginRefusal?: ApiFailure) {
  const nodes = page();
  let live = ids.map(save);
  const calls: string[] = [];
  const api: GameApi = {
    content: () => Promise.resolve(fixtureContent), me: () => Promise.resolve({ account: null, saves: live, max_saves: 5, kept_days: 30 }),
    savedView: (id) => { calls.push(`view ${id}`); return Promise.resolve(view); },
    open: (id) => { calls.push(`open ${id}`); return no(); },
    begin: () => { calls.push("begin"); return beginRefusal ? Promise.reject(beginRefusal) : Promise.resolve({ save: save(99), presentation: NEW_SAVE, step: fixtureStep("standing", 100, {}, 0) }); },
    advance: no, forecast: no, decide: no, dryRun: no, putMePresentation: no, putMeSettings: no, putSavePresentation: no, sendFeedback: no, makeCode: no, makeWords: no,
    join: no, devices: no, removeDevice: no, games: no, restoreGame: no,
    deleteGame: (id) => { calls.push(`delete ${id}`); live = live.filter((x) => x.save_id !== id); return Promise.resolve({ saves: live, deleted: [], max_saves: 5, kept_days: 30 }); },
  };
  const started: (number | null)[] = [];
  const spy: PlayGame = (_api, _root, opts) => {
    started.push(opts.resume);
    return { begin: () => Promise.resolve() };
  };
  wireBegin(api, undefined, null, { get: () => false, set: () => undefined }, spy);
  await later();
  const rows = (): FakeEl[] => fakeDocument.querySelectorAll("button.place");
  return { nodes, calls, started, rows };
}

{  // at load: the newest game is selected, Continue opens it, and its picture read nothing but views
  const r = await rig([5, 3, 1]);
  expect("four rows", r.rows().length, 4);
  expect("the button is Continue", r.nodes["begin"]?.textContent, "Continue");
  expect("the line is the newest game's", r.nodes["sub"]?.textContent, "Game 5 · Camp level 5 · Last played 3 hours ago");
  expect("every game's view was read once, none opened", r.calls.sort(), ["view 1", "view 3", "view 5"]);
  r.nodes["begin"]?.click();
  expect("Continue opens the newest", r.started, [5]);
  expect("opening is the game's own, never the front page's api.open", r.calls.some((c) => c.startsWith("open")), false);
}
{  // selecting another game changes what Continue opens, and the line
  const r = await rig([5, 3, 1]);
  r.rows()[2]?.click();
  expect("nothing opened by a tap that selects", r.started, []);
  expect("the line follows", r.nodes["sub"]?.textContent, "Game 1 · Camp level 1 · Last played 3 hours ago");
  expect("still Continue", r.nodes["begin"]?.textContent, "Continue");
  r.nodes["begin"]?.click();
  expect("Continue opens the selected game", r.started, [1]);
}
{  // New game selected: Begin, the first visit's line, no skip box, and the button begins a new game
  const r = await rig([5, 3]);
  r.rows()[2]?.click();
  expect("the button reads Begin", r.nodes["begin"]?.textContent, "Begin");
  expect("the first visit's line", r.nodes["sub"]?.textContent, fixtureContent.text_entries.find((e) => e.key === "ui.front.first")?.text);
  expect("the skip box is hidden", r.nodes["keep"]?.querySelector("label")?.hidden, true);
  r.nodes["begin"]?.click();
  expect("pressing it starts a new game, not a save", r.started, [null]);
}
{  // choosing a game again turns the button back to Continue
  const r = await rig([5, 3]);
  r.rows()[2]?.click();
  r.rows()[1]?.click();
  expect("back to Continue", r.nodes["begin"]?.textContent, "Continue");
  expect("the skip box is back", r.nodes["keep"]?.querySelector("label")?.hidden, false);
  r.nodes["begin"]?.click();
  expect("it opens the chosen game", r.started, [3]);
}

{  // the canned ledger line shows for New game (and on a first visit, which selects nothing), never over a saved game's camp
  const r = await rig([5, 3]);
  expect("a game is selected: the line is hidden", r.nodes["ledger"]?.hidden, true);
  r.rows()[2]?.click();
  expect("New game: the line is back", r.nodes["ledger"]?.hidden, false);
  r.rows()[1]?.click();
  expect("another game: hidden again", r.nodes["ledger"]?.hidden, true);
}

{  // the panel's Delete: it asks first, deletes on the second tap, and the newest left is selected
  const r = await rig([5, 3, 1]);
  const panel = (): FakeEl[] => r.nodes["begin"]?.parent?.querySelectorAll("button.front-quiet, button.front-primary").filter((b) => !b.className.includes("phone-only")) ?? [];
  const named = (label: string): FakeEl | undefined => panel().find((b) => b.textContent === label);
  r.rows()[1]?.click();   // select Game 3
  named("Delete")?.click();
  expect("one tap deletes nothing", r.calls.some((c) => c.startsWith("delete")), false);
  expect("it asks, with Cancel", [named("Cancel") !== undefined, fakeDocument.body.textContent.includes("Delete this game?")], [true, true]);
  named("Delete")?.click();
  await later();
  expect("the second tap deletes the selected game", r.calls.filter((c) => c.startsWith("delete")), ["delete 3"]);
  expect("two games left, newest selected", [r.rows().length, r.nodes["sub"]?.textContent?.startsWith("Game 5")], [3, true]);
}
{  // New game selected: no Delete; the only game: Start over in Delete's place, which begins a new game, then deletes
  const r = await rig([5, 3]);
  const deletes = (): number => (r.nodes["begin"]?.parent?.querySelectorAll("button.front-quiet") ?? []).filter((b) => b.textContent === "Delete").length;
  expect("a Delete beside Continue", deletes(), 1);
  r.rows()[2]?.click();
  expect("none while New game is selected", deletes(), 0);
  const one = await rig([5]);
  const lone = (label: string): FakeEl[] => (one.nodes["begin"]?.parent?.querySelectorAll("button.front-quiet, button.front-primary") ?? []).filter((b) => b.textContent === label);
  expect("the only game: Start over, no Delete", [lone("Delete").length, lone("Start over").length], [0, 1]);
  lone("Start over")[0]?.click();
  expect("it asks first, and calls nothing", [fakeDocument.body.textContent.includes("Start a new game and delete this one?"), one.calls.includes("begin")], [true, false]);
  lone("Start over")[0]?.click();
  await later();
  expect("a begin, then the old game's delete, then the new game opens", [one.calls.filter((c) => c === "begin" || c.startsWith("delete")), one.started.at(-1)], [["begin", "delete 5"], 99]);
  const refused = await rig([5], new ApiFailure("rate_limited", "429"));
  const again = (label: string): FakeEl[] => (refused.nodes["begin"]?.parent?.querySelectorAll("button.front-quiet, button.front-primary") ?? []).filter((b) => b.textContent === label);
  again("Start over")[0]?.click();
  again("Start over")[0]?.click();
  await later();
  expect("a refused begin deletes nothing and says why", [refused.calls.filter((c) => c === "begin" || c.startsWith("delete")), fakeDocument.body.textContent.includes(text.get("ui.games.limited"))], [["begin"], true]);
}
