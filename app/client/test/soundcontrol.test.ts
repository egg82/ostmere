// The speaker button and the Settings row (src/ui/soundcontrol.ts): drawn only once a sound is registered, one switch
// behind both, and the cut taken at once.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { registerSound, resetSound } from "../src/audio/locator";
import { browserSoundSwitch } from "../src/audio/mute";
import { browserStraight } from "../src/app/straight";
import { Text, UI } from "../src/game/text";
import { ReminderRow, type ReminderDeps } from "../src/ui/settings/reminders";
import { SettingsSheet } from "../src/ui/settings/settings";
import { soundControl } from "../src/ui/settings/soundcontrol";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const text = new Text(fixtureContent);
const store = new Map<string, string>();
const storage = { getItem: (k: string) => store.get(k) ?? null, setItem: (k: string, v: string) => { store.set(k, v); }, removeItem: (k: string) => { store.delete(k); } } as Storage;
const deps: ReminderDeps = {
  api: { put: () => Promise.resolve(null), off: () => Promise.resolve() },
  config: () => Promise.resolve({ public_key: "k", after_hours: [12] }), cap: () => "ok", current: () => Promise.resolve(null),
  subscribe: () => Promise.resolve(null), zone: () => "UTC",
};
const sheet = (sound = soundControl(text, browserSoundSwitch(() => storage))) =>
  new SettingsSheet(text, new ReminderRow(text, deps), browserStraight(() => storage), { get: () => false, set: () => undefined }, sound);

{  // only the Null default: no control, and no row in Settings
  resetSound();
  expect("no control", soundControl(text, browserSoundSwitch(() => storage)) === null, true);
  const s = sheet();
  document.body.replaceChildren(s.root);
  s.button.click();
  expect("no Sound row", s.root.querySelectorAll(".settings-sound").length, 0);
}

{  // a sound registered: both appear, each flips the shared switch and the other follows
  let refreshes = 0;
  registerSound({ play: () => () => undefined, loop: () => ({ setLevel: () => undefined }), piece: () => ({ setLevel: () => undefined, stop: () => undefined, onEnd: () => undefined }) }, () => { refreshes++; });
  const mute = browserSoundSwitch(() => storage);
  const control = soundControl(text, mute)!;
  const s = sheet(control);
  document.body.replaceChildren(s.root);
  s.button.click();
  const input = fakeDocument.querySelector(".settings-sound")!;
  expect("the row is in Settings, on", [s.root.querySelectorAll(".settings-sound").length, input.checked], [1, true]);
  expect("the button says on", control.button.getAttribute("aria-label"), text.get(UI.soundOn));
  control.button.click();
  expect("the button turned it off", [mute.get(), input.checked, control.button.getAttribute("aria-label"), refreshes],
    [false, false, text.get(UI.soundOff), 1]);
  input.checked = true;
  input.dispatchEvent(new FakeEvent("change"));
  expect("the row turned it on", [mute.get(), control.button.getAttribute("aria-label"), refreshes], [true, text.get(UI.soundOn), 2]);
  resetSound();
}

{  // storage that throws: the control still draws, on, and a tap cannot keep an off
  registerSound({ play: () => () => undefined, loop: () => ({ setLevel: () => undefined }), piece: () => ({ setLevel: () => undefined, stop: () => undefined, onEnd: () => undefined }) });
  const broken = browserSoundSwitch(() => { throw new Error("blocked"); });
  const control = soundControl(text, broken)!;
  control.button.click();
  expect("falls back to on", [broken.get(), control.button.getAttribute("aria-label")], [true, text.get(UI.soundOn)]);
  resetSound();
}
