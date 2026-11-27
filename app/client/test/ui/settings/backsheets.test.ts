// Back from each kind of sheet the player opens closes that sheet and nothing else; closing one by its own button or the
// backdrop gives its history entry back, so the next back is the player's, not a stale one; with nothing open back is not
// held (ui/back.ts holds no entry).
import { install } from "../../fake-dom";
import { dayTwoStep } from "../../../fixtures/daytwo";
import { fixtureContent } from "../../../fixtures/content";
import { Catalog } from "../../../src/game/page/catalog";
import { Keeps } from "../../../src/game/account/keeps";
import { fixtureGames } from "../../../fixtures/games";
import { Screen } from "../../../src/ui/screen";
import { browserStraight } from "../../../src/app/straight";
import { Text } from "../../../src/game/page/text";
import type { GameApi } from "../../../src/api/api";
import { Devices } from "../../../src/ui/devices/devices";
import { GamesSheet } from "../../../src/ui/front/games";
import { ReminderRow } from "../../../src/ui/settings/reminders";
import { SettingsSheet } from "../../../src/ui/settings/settings";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
// The sheets game.ts seats beside the screen, built as it builds them.
const text = new Text(fixtureContent);
const no = (): Promise<never> => Promise.reject(new Error("not in these tests"));
const api = { games: () => fixtureGames().games(), devices: no, mixRows: () => new Promise<never>(() => undefined) } satisfies Partial<GameApi> as Partial<GameApi> as GameApi;
const settings = new SettingsSheet(text, new ReminderRow(text), browserStraight(), { get: () => false, set: () => undefined });
const games = new GamesSheet(api, text, { playing: () => 1, open: () => undefined, begun: () => undefined });
const devices = new Devices(api, text, null as never, 600, { devicesOpened: () => true, keepDevicesOpened: () => undefined } as Partial<Keeps> as Keeps, null);
const beside = document.createElement("div");
beside.append(settings.button, settings.root, games.button, games.root, devices.button, devices.root);
document.body.replaceChildren(screen.root, beside);
screen.show(dayTwoStep("ruled", 100));

const all = (s: string): HTMLElement[] => [...document.body.querySelectorAll<HTMLElement>(s)];
const depth = (): number => (history.state as { ostmere?: number } | null)?.ostmere ?? 0;
const openSheets = (): HTMLDialogElement[] => all("dialog").filter((d) => (d as HTMLDialogElement).open) as HTMLDialogElement[];
const settle = (): Promise<void> => new Promise((done) => setTimeout(done, 0));
async function back(): Promise<void> {
  history.back();
  await settle();
}

/** The buttons that open a sheet from the panel: each opens exactly one dialog. */
const openers = [".settings-open", ".games-open", ".devices-open", ".feedback-open", ".hands-name"];
const found = openers.filter((s) => all(s).length > 0);
expect("every kind of sheet has its opener on the page", found, openers);

for (const selector of openers) {
  const opener = all(selector)[0]!;
  expect(`${selector}: nothing open to start`, [openSheets().length, depth()], [0, 0]);

  opener.click();
  await settle();
  const sheet = openSheets()[0];
  expect(`${selector}: opens one sheet holding one entry`, [openSheets().length, depth()], [1, 1]);
  if (!sheet) throw new Error(`${selector}: no sheet opened`);

  await back();
  expect(`${selector}: back closes the sheet`, [sheet.open, depth()], [false, 0]);

  opener.click();
  await settle();
  sheet.dispatchEvent(Object.assign(new Event("click"), { target: sheet }));   // the backdrop
  sheet.close();
  await settle();
  expect(`${selector}: closed by hand, the entry is given back`, [sheet.open, depth()], [false, 0]);
  await back();
  expect(`${selector}: back after a hand close reopens nothing`, [openSheets().length, depth()], [0, 0]);
}

{  // a sheet over a tab: back closes the sheet, then the tab; a hand close in between skips nothing
  all(`.tabs [data-tab="town"]`)[0]!.click();
  await settle();
  all(".settings-open")[0]!.click();
  await settle();
  expect("a sheet over the Town tab", [openSheets().length, depth(), screen.root.dataset["tab"]], [1, 2, "town"]);
  openSheets()[0]!.close();
  await settle();
  expect("closed by hand: the tab's entry stays", [openSheets().length, depth(), screen.root.dataset["tab"]], [0, 1, "town"]);
  await back();
  expect("back leaves the tab for Tasks", [depth(), screen.root.dataset["tab"]], [0, "cards"]);
  const before = history.state;
  all(".settings-open")[0]!.click();
  await settle();
  await back();
  expect("at the top level nothing is left held", [depth(), history.state], [0, before]);
}
