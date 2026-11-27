// The Settings sheet (src/ui/settings/settings.ts): this device's reminders live in it and not in "Another device", and the
// reminders mention opens it with the row focused.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import type { GameApi } from "../src/api/api";
import { browserStraight } from "../src/app/straight";
import { Keeps, NEW_ACCOUNT } from "../src/game/account/keeps";
import { Text, UI } from "../src/game/page/text";
import { Devices } from "../src/ui/devices/devices";
import { el } from "../src/ui/dom";
import { ReminderMention } from "../src/ui/settings/remindermention";
import { ReminderRow, type ReminderDeps } from "../src/ui/settings/reminders";
import { SettingsSheet } from "../src/ui/settings/settings";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const text = new Text(fixtureContent);
const later = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 5));
const cfg = { public_key: "k", after_hours: [12, 24, 72, 168] };
const deps: ReminderDeps = {
  api: { put: () => Promise.resolve(null), off: () => Promise.resolve() },
  config: () => Promise.resolve(cfg), cap: () => "ok", current: () => Promise.resolve(null), subscribe: () => Promise.resolve(null), zone: () => "UTC",
};
const store = new Map<string, string>();
const storage = { getItem: (k: string) => store.get(k) ?? null, setItem: (k: string, v: string) => { store.set(k, v); }, removeItem: (k: string) => { store.delete(k); } } as Storage;
let lessonsOff = false;   // what the account keeps (the page's AccountSettings.lessons, inverted)
const settings = new SettingsSheet(text, new ReminderRow(text, deps), browserStraight(() => storage),
  { get: () => lessonsOff, set: (skip) => { lessonsOff = skip; } });
const devices = new Devices({ devices: () => Promise.resolve({ devices: [] }) } as Partial<GameApi> as GameApi, text, null as never, 600,
  { devicesOpened: () => true, keepDevicesOpened: () => undefined } as Partial<Keeps> as Keeps, null);
document.body.replaceChildren(settings.root, devices.root);

{  // Settings holds the reminders row, drawn on open; Another device holds none of it
  settings.button.click();
  await later();
  expect("Settings opens", settings.root.open, true);
  expect("the button's words", settings.button.textContent, text.get(UI.settingsOpen));
  expect("the reminders row is in Settings and shown", [settings.root.querySelectorAll(".reminders-part").length,
    fakeDocument.querySelector(".settings-sheet .reminders-part")!.hidden], [1, false]);
  devices.open(null);
  await later();
  expect("Another device holds no reminders", devices.root.querySelectorAll(".reminders-part").length, 0);
  expect("its transfer parts are still there", ["devices-code", "devices-words", "devices-join", "devices-list"]
    .map((c) => devices.root.querySelectorAll(`.${c}`).length), [1, 1, 1, 1]);
}

{  // the mention's button opens Settings and puts focus in the reminders row
  settings.root.close();
  devices.root.close();
  const keeps = new Keeps({ account: { ...NEW_ACCOUNT } }, { account: () => undefined });
  const mention = new ReminderMention(keeps, text, () => void settings.showReminders(), () => Promise.resolve(cfg), () => "ok");
  const foot = el("div");
  const panel = el("div");
  panel.append(foot);
  await mention.check({ endRead: true, busy: false }, foot);
  panel.querySelector<HTMLButtonElement>(".reminder-mention button")!.click();
  await later();
  expect("the mention opens Settings", settings.root.open, true);
  expect("and not Another device", devices.root.open, false);
    expect("focus is in the reminders row", fakeDocument.activeElement !== null && fakeDocument.querySelector(".settings-sheet")!.contains(fakeDocument.activeElement), true);
}

{  // each choice sits under the heading for what it is bound to, shows what is kept on opening, and keeps its change where it did before
  const groups = fakeDocument.querySelectorAll(".settings-sheet > .devices-part");
  expect("the groups, by what they are bound to", groups.map((g) => g.querySelector(".lane-tag")!.textContent),
    [text.get(UI.settingsDevice), text.get(UI.settingsEvery)]);
  expect("reminders and straight are this device's, lessons every game's", groups.map((g) => [".reminders-part", ".settings-straight", ".settings-lessons"]
    .map((c) => g.querySelectorAll(c).length)), [[1, 1, 0], [0, 0, 1]]);
  const straight = fakeDocument.querySelector("input.settings-straight")!;
  const lessons = fakeDocument.querySelector("input.settings-lessons")!;
  settings.root.close();
  await settings.open();
  expect("both open unchecked", [straight.checked, lessons.checked], [false, false]);
  straight.checked = true;
  straight.dispatchEvent(new FakeEvent("change"));
  lessons.checked = true;
  lessons.dispatchEvent(new FakeEvent("change"));
  expect("the front page's choice is kept in this browser", browserStraight(() => storage).get(), true);
  expect("skip lessons is the account's, checked meaning lessons off", lessonsOff, true);
  straight.checked = false;
  lessons.checked = false;
  await settings.open();
  expect("opening shows what is kept", [straight.checked, lessons.checked], [true, true]);
  lessons.checked = false;
  lessons.dispatchEvent(new FakeEvent("change"));
  expect("unticking turns lessons back on", lessonsOff, false);
}
{  // storage that keeps nothing: a ticked box reads as off again
  const none = browserStraight(() => { throw new Error("blocked"); });
  const sheet = new SettingsSheet(text, new ReminderRow(text, deps), none, { get: () => false, set: () => undefined });
  document.body.replaceChildren(sheet.root);
  const box = fakeDocument.querySelector("input.settings-straight")!;
  box.checked = true;
  box.dispatchEvent(new FakeEvent("change"));
  expect("nothing kept, shown off", box.checked, false);
}
