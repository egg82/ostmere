// The Another device sheet's list of browsers (src/ui/devicelist.ts): one row per served device with its label and last
// use, the asking browser marked, Remove sending DELETE for that row's id and redrawing from the answer, and removing
// this browser asking first and then starting the page again.
import { fakeDocument, install, type FakeEl } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureDevices } from "../fixtures/devices";
import { ApiFailure, type GameApi } from "../src/api/api";
import { dateOf } from "../src/game/format";
import { Text } from "../src/game/text";
import { DeviceList } from "../src/ui/devicelist";
import type { DevicesContext } from "../src/ui/devices";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const text = new Text(fixtureContent);
const later = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 5));
const no = (): Promise<never> => Promise.reject(new Error("not in these tests"));

function rig(fail: ApiFailure | null = null) {
  const served = fixtureDevices();
  const calls: string[] = [];
  const api = {
    devices: () => { calls.push("devices"); return served.devices(); },
    removeDevice: (id: number) => { calls.push(`remove ${id}`); return fail ? Promise.reject(fail) : served.removeDevice(id); },
  } as Partial<GameApi> as GameApi;
  const ctx: DevicesContext = { api, text, format: no as never, refusalLine: () => "" };
  let reloads = 0;
  const list = new DeviceList(ctx, () => { reloads += 1; });
  document.body.replaceChildren(list.root);
  return { list, calls, reloads: () => reloads };
}

const rows = (): FakeEl[] => fakeDocument.querySelectorAll(".devices-list .games-row");
const button = (row: FakeEl, key: string): FakeEl => {
  const found = row.querySelectorAll("button").find((b) => b.textContent === text.get(key));
  if (!found) throw new Error(`no ${key} button in the row`);
  return found;
};
const labels = (): string[] => rows().map((r) => r.querySelector(".games-name")?.textContent ?? "");

{  // rows: label, last use, this device marked, a Remove on every row
  const r = rig();
  r.list.open();
  await later();
  expect("asked once", r.calls, ["devices"]);
  expect("one row per browser, this one first", labels(), ["Firefox on Linux", "Safari on iPhone", "Chrome on Android", "A browser"]);
  const [here, other] = rows();
  expect("this device is marked", [here!.querySelector(".games-playing")?.textContent, other!.querySelector(".games-playing")], [text.get("ui.devices.list_this"), null]);
  const lastUsed = text.fill("ui.devices.list_seen", { seen: dateOf(new Date(Date.now() - 2 * 86_400_000).toISOString()) });
  expect("last use as a date", other!.querySelector(".games-dates")?.textContent, lastUsed);
  expect("Remove on every row", rows().map((row) => row.querySelectorAll("button").length), [1, 1, 1, 1]);
}
{  // removing another browser sends its id and redraws from the answer, without asking
  const r = rig();
  r.list.open();
  await later();
  button(rows()[1]!, "ui.devices.list_remove").click();
  await later();
  expect("DELETE for that row's id", r.calls, ["devices", "remove 9"]);
  expect("redrawn from the answer", labels(), ["Firefox on Linux", "Chrome on Android", "A browser"]);
  expect("the page stays", r.reloads(), 0);
}
{  // removing this browser asks first; Cancel takes it back; the yes sends and restarts the page
  const r = rig();
  r.list.open();
  await later();
  button(rows()[0]!, "ui.devices.list_remove").click();
  expect("the question", rows()[0]!.querySelector(".games-ask")?.textContent, text.get("ui.devices.list_remove_ask"));
  expect("nothing sent on the first tap", r.calls, ["devices"]);
  button(rows()[0]!, "ui.devices.list_remove_no").click();
  expect("Cancel takes it back", [rows()[0]!.querySelector(".games-ask"), r.calls], [null, ["devices"]]);
  button(rows()[0]!, "ui.devices.list_remove").click();
  button(rows()[0]!, "ui.devices.list_remove_yes").click();
  await later();
  expect("DELETE for this browser's id", r.calls, ["devices", "remove 7"]);
  expect("the page starts again", r.reloads(), 1);
}
{  // a refusal is one line and the list is asked for again; a gone row (not_found) says nothing
  const away = rig(new ApiFailure("network", "x"));
  away.list.open();
  await later();
  button(rows()[1]!, "ui.devices.list_remove").click();
  await later();
  expect("no answer", [fakeDocument.querySelector(".devices-note")?.textContent, labels().length], [text.get("ui.devices.away"), 4]);
  const gone = rig(new ApiFailure("not_found", "x"));
  gone.list.open();
  await later();
  button(rows()[2]!, "ui.devices.list_remove").click();
  await later();
  expect("gone already", [fakeDocument.querySelector(".devices-note")?.textContent ?? "", gone.calls.at(-1)], ["", "devices"]);
}
