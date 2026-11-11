// Joining without moving, on the Another device sheet (src/ui/devicejoin.ts, devicekept.ts, devices.ts): the ask a device
// with games of its own gets has three buttons (Move my games the primary one, Join without moving, Cancel), each
// sending its own request; a join that kept the games shows their words (or what to do when the account had some),
// and the sheet cannot be closed until Continue.
import { fakeDocument, FakeEvent, install, type FakeEl } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { ApiFailure, type GameApi } from "../src/api/api";
import type { JoinWay, Joined, KeptGames } from "../src/api/types";
import type { Keeps } from "../src/game/keeps";
import { Text, UI } from "../src/game/text";
import { Devices } from "../src/ui/devices";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const text = new Text(fixtureContent);
const later = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 5));
let reloads = 0;
Object.assign(globalThis, { location: { reload: () => { reloads += 1; } } });

const account = { presentation: { rules_opened: false, devices_opened: false, reminder_mentioned: false, ledger_lines: [], mix_stopped: [], switch_offered: [], journal_read: [] }, settings: { lessons: true }, has_words: false, words_due: false };
const summary = { here: 2, there: 1, there_newest_game_time: 0, max_saves: 5, words_replaced: false };

function rig(kept: KeptGames | null) {
  const sent: JoinWay[] = [];
  const api = {
    join: (_typed: string, way: JoinWay): Promise<Joined> => {
      sent.push(way);
      if (way === "plain") return Promise.reject(new ApiFailure("confirm_merge", "x", null, null, summary));
      return Promise.resolve({ moved: way === "move" ? 2 : 0, account, kept: way === "keep" ? kept : null });
    },
  } as Partial<GameApi> as GameApi;
  const keeps = { devicesOpened: () => true, keepDevicesOpened: () => undefined } as Partial<Keeps> as Keeps;
  const sheet = new Devices(api, text, null as never, 600, keeps, null);
  document.body.replaceChildren(sheet.root);
  return { sheet, sent };
}

const buttons = (): FakeEl[] => fakeDocument.querySelectorAll(".devices-ask .sheet-actions button");
const named = (key: string): FakeEl => {
  const found = buttons().find((b) => b.textContent === text.get(key));
  if (!found) throw new Error(`no ${key} button`);
  return found;
};

async function asked(r: ReturnType<typeof rig>): Promise<void> {
  const input = fakeDocument.querySelector(".devices-join .devices-input")!;
  input.value = "K7QM-4XRT";
  input.parent!.parent!.dispatchEvent(new FakeEvent("submit"));
  await later();
}

{  // the ask: three buttons, Move my games the only primary one, and the question names both ways
  const r = rig(null);
  await asked(r);
  expect("the three answers, Cancel first", buttons().map((b) => b.textContent), [text.get(UI.mergeCancel), text.get(UI.keep), text.get(UI.merge)]);
  expect("only Move my games is primary", buttons().map((b) => b.classList.contains("primary")), [false, false, true]);
  expect("the first join asked first", r.sent, ["plain"]);
  named(UI.mergeCancel).click();
  expect("Cancel sends nothing and closes the ask", [r.sent, fakeDocument.querySelector(".devices-ask")!.hidden], [["plain"], true]);
}
{  // Move my games sends move and reloads
  reloads = 0;
  const r = rig(null);
  await asked(r);
  named(UI.merge).click();
  await later();
  expect("move is sent, then the page reloads", [r.sent, reloads], [["plain", "move"], 1]);
}
{  // Join without moving sends keep, shows the new words and holds the sheet until Continue
  reloads = 0;
  const r = rig({ saves: 2, words: "ember-lantern-gravel-oyster", label: "Ostmere" });
  r.sheet.root.open = true;
  await asked(r);
  named(UI.keep).click();
  await later();
  expect("keep is sent and the page waits", [r.sent, reloads], [["plain", "keep"], 0]);
  const kept = fakeDocument.querySelector(".devices-kept")!;
  expect("the step is shown and says why", [kept.hidden, kept.textContent.includes(text.get(UI.keptNew))], [false, true]);
  expect("the words are listed", kept.querySelectorAll(".devices-words-list span").map((s) => s.textContent), ["ember", "lantern", "gravel", "oyster"]);
  expect("the rest of the sheet is gone", ["devices-code", "devices-words", "devices-join", "devices-list"].map((c) => fakeDocument.querySelector(`.${c}`)!.hidden), [true, true, true, true]);
  const cancel = new FakeEvent("cancel");
  const dialog = fakeDocument.querySelector(".devices-sheet")!;
  dialog.dispatchEvent(cancel);
  dialog.dispatchEvent(new FakeEvent("click"));
  expect("Escape and the backdrop do not close it", [cancel.defaultPrevented, r.sheet.root.open], [true, true]);
  fakeDocument.querySelectorAll(".devices-kept .sheet-actions button").find((b) => b.textContent === text.get(UI.keptDone))!.click();
  expect("Continue reloads", reloads, 1);
}
{  // an account that already had words: none shown, and the line says they are what brings the games back
  const r = rig({ saves: 2, words: null, label: "Ostmere" });
  await asked(r);
  named(UI.keep).click();
  await later();
  const kept = fakeDocument.querySelector(".devices-kept")!;
  expect("the had-words line, no words form", [kept.textContent.includes(text.get(UI.keptHad)), kept.querySelectorAll("form").length], [true, 0]);
}
