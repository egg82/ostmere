// Where a page load goes (src/begin.ts entry): a browser with no saves sees the front page and Begin; with saves it
// sees Continue unless the address names a live save, a join link came, or the device's choice is on. The choice
// (src/app/straight.ts) is off when storage throws, and the Games sheet's checkbox sets it and shows what was kept.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureGames } from "../fixtures/games";
import type { GameApi } from "../src/api/api";
import type { SaveInfo } from "../src/api/types";
import { browserStraight } from "../src/app/straight";
import { entry } from "../src/begin";
import { Text } from "../src/game/text";
import { GamesSheet } from "../src/ui/games";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const save = (id: number): SaveInfo => ({ save_id: id, number: id, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 });
const saves = [save(5), save(8)];   // newest first
const ids = (e: { open?: SaveInfo; carryOn?: SaveInfo }) => ({ open: e.open?.save_id, carryOn: e.carryOn?.save_id });

expect("first visit", ids(entry([], "", false)), {});
expect("first visit, setting on", ids(entry([], "", true)), {});
expect("first visit, a #game that is no save", ids(entry([], "#game=8", false)), {});
expect("saves, setting off: Continue", ids(entry(saves, "", false)), { carryOn: 5 });
expect("saves, setting off: Continue follows the address's other fragments", ids(entry(saves, "#x=1", false)), { carryOn: 5 });
expect("saves, setting on: straight in", ids(entry(saves, "", true)), { open: 5 });
expect("#game= names a live save, setting off", ids(entry(saves, "#game=8", false)), { open: 8 });
expect("#game= names a live save, setting on", ids(entry(saves, "#game=8", true)), { open: 8 });
expect("#game= names a gone save, setting off: Continue", ids(entry(saves, "#game=3", false)), { carryOn: 5 });
expect("#game= names a gone save, setting on: the newest", ids(entry(saves, "#game=3", true)), { open: 5 });

const blocked = (): never => { throw new Error("blocked"); };
const no = (): Promise<never> => Promise.reject(new Error("not in these tests"));

/** An api that knows only the games list. */
function api(): GameApi {
  const games = fixtureGames();
  return {
    content: no, me: no, begin: no, open: no, savedView: no, advance: no, forecast: no, decide: no, dryRun: no, putMePresentation: no, putMeSettings: no, putSavePresentation: no,
    sendFeedback: no, makeCode: no, makeWords: no, join: no, devices: no, removeDevice: no,
    games: () => games.games(), deleteGame: no, restoreGame: no,
  };
}

function memory(): Storage {
  const m = new Map<string, string>();
  return { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => { m.set(k, v); }, removeItem: (k) => { m.delete(k); } } as Storage;
}
{  // the choice: off at first, kept once set, off again when cleared; a second Straight on the same storage sees it
  const store = memory();
  const a = browserStraight(() => store);
  expect("off by default", a.get(), false);
  a.set(true);
  expect("kept", browserStraight(() => store).get(), true);
  a.set(false);
  expect("cleared", a.get(), false);
}
{  // storage that throws, on naming it, reading or writing: the page works, and the choice reads as off
  const naming = browserStraight(() => { throw new Error("blocked"); });
  const hostile = Object.assign(memory(), { getItem: blocked, setItem: blocked, removeItem: blocked });
  for (const [label, s] of [["naming", naming], ["reading and writing", browserStraight(() => hostile)]] as const) {
    s.set(true);
    s.set(false);
    expect(`${label}: off`, s.get(), false);
  }
}
{  // the sheet's checkbox shows the choice on opening, sets it on a change, and shows off when nothing was kept
  const store = memory();
  const keeps = (): boolean => browserStraight(() => store).get();
  const sheet = new GamesSheet(api(), new Text(fixtureContent), { playing: () => null, open: () => undefined, begun: () => undefined, straight: browserStraight(() => store), skipLessons: { get: () => false, set: () => undefined } });
  document.body.replaceChildren(sheet.button, sheet.root);
  const box = fakeDocument.querySelector("input.games-straight");
  if (!box) throw new Error("no checkbox on the sheet");
  sheet.open();
  expect("opens unchecked", box.checked, false);
  box.checked = true;
  box.dispatchEvent(new FakeEvent("change"));
  expect("a change keeps it", keeps(), true);
  sheet.root.close();
  box.checked = false;
  sheet.open();
  expect("opens as kept", box.checked, true);
  box.checked = false;
  box.dispatchEvent(new FakeEvent("change"));
  expect("unticking clears it", keeps(), false);
}
{  // storage that keeps nothing: the box ticked by the player reads as off again
  const none = browserStraight(() => { throw new Error("blocked"); });
  const sheet = new GamesSheet(api(), new Text(fixtureContent), { playing: () => null, open: () => undefined, begun: () => undefined, straight: none, skipLessons: { get: () => false, set: () => undefined } });
  document.body.replaceChildren(sheet.button, sheet.root);
  const box = fakeDocument.querySelector("input.games-straight");
  if (!box) throw new Error("no checkbox on the sheet");
  box.checked = true;
  box.dispatchEvent(new FakeEvent("change"));
  expect("nothing kept, shown off", box.checked, false);
}
