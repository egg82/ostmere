// The Settings sheet (src/ui/settings.ts): this device's reminders live in it and not in "Another device", and the
// reminders mention opens it with the row focused.
import { fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import type { GameApi } from "../src/api/api";
import { Keeps, NEW_ACCOUNT } from "../src/game/keeps";
import { Text, UI } from "../src/game/text";
import { Devices } from "../src/ui/devices";
import { el } from "../src/ui/dom";
import { ReminderMention } from "../src/ui/remindermention";
import { ReminderRow, type ReminderDeps } from "../src/ui/reminders";
import { SettingsSheet } from "../src/ui/settings";

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
const settings = new SettingsSheet(text, new ReminderRow(text, deps));
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
