// The Notifications section of Settings (src/ui/reminders.ts): the kinds off at first and on in any combination, the
// subscription made when the first goes on and dropped only when none is on, one window for all of them shown once
// any kind is on, and what the server holds shown on open.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import type { Reminder } from "../src/api/reminders";
import type { Subscribed } from "../src/app/push";
import { Text } from "../src/game/text";
import { ReminderRow, type ReminderDeps } from "../src/ui/reminders";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const text = new Text(fixtureContent);
const cfg = { public_key: "k", after_hours: [12, 24, 72, 168] };
const keys: Subscribed = { endpoint: "https://fcm.googleapis.com/fcm/send/x", p256dh: "p", auth: "a" };

interface World { calls: string[]; stored: Reminder | null; held: boolean }
const WINDOW = { send_from_hour: 9, send_until_hour: 21 };
const AWAY = { after_hours: 24, ...WINDOW };
const NOTICE = { after_hours: null, ...WINDOW };

function rowIn(world: World): ReminderRow {
  const sub = { unsubscribe: () => { world.calls.push("unsubscribe"); world.held = false; return Promise.resolve(true); } } as Partial<PushSubscription> as PushSubscription;
  const deps: ReminderDeps = {
    api: {
      put: (_k, _tz, choice) => {
        world.calls.push(`put ${JSON.stringify(choice)}`);
        if (choice !== null) world.stored = choice;
        return Promise.resolve(world.stored);
      },
      off: () => { world.calls.push("off"); world.stored = null; return Promise.resolve(); },
    },
    config: () => Promise.resolve(cfg), cap: () => "ok",
    current: () => Promise.resolve(world.held ? { sub, keys } : null),
    subscribe: () => { world.calls.push("subscribe"); world.held = true; return Promise.resolve({ sub, keys }); },
    zone: () => "UTC",
  };
  const row = new ReminderRow(text, deps);
  document.body.replaceChildren(row.root);
  return row;
}

const box = (kind: "away" | "hands") => fakeDocument.querySelector(`.reminders-${kind === "away" ? "away-kind" : "hands"} input`)!;
const shown = (cls: string) => !fakeDocument.querySelector(cls)!.hidden;
const settle = () => new Promise((resolve) => setTimeout(resolve, 5));
const toggle = async (kind: "away" | "hands", on: boolean) => {
  box(kind).checked = on;
  box(kind).dispatchEvent(new FakeEvent("change"));
  await settle();
};
const put = (r: Reminder) => `put ${JSON.stringify(r)}`;
const state = () => ({ away: box("away").checked, hands: box("hands").checked, lengths: shown(".reminders-away"), times: shown(".reminders-window") });

{  // none on at first: both kinds off with their words on screen, no lengths and no times until a kind is on
  const world: World = { calls: [], stored: null, held: false };
  await rowIn(world).open();
  expect("drawn off", state(), { away: false, hands: false, lengths: false, times: false });
  expect("their words", [fakeDocument.querySelector(".reminders-hands span")!.textContent, fakeDocument.querySelector(".reminders-away-kind span")!.textContent],
    [text.get("ui.reminders.hands_free"), text.get("ui.reminders.away_kind")]);
  expect("the lead says what it is for", fakeDocument.querySelector(".reminders-said")!.textContent, text.get("ui.reminders.lead"));
}

{  // the notice alone: subscribes, sends no absence, shows the times but not the lengths; off again drops the browser
  const world: World = { calls: [], stored: null, held: false };
  await rowIn(world).open();
  await toggle("hands", true);
  expect("on alone", world.calls, ["subscribe", put({ ...NOTICE, hands_free: true })]);
  expect("states", state(), { away: false, hands: true, lengths: false, times: true });
  world.calls = [];
  await toggle("hands", false);
  expect("off with nothing else on drops the browser", world.calls, ["off", "unsubscribe"]);
  expect("states after", state(), { away: false, hands: false, lengths: false, times: false });
  expect("says so", fakeDocument.querySelector(".reminders-said")!.textContent, text.get("ui.reminders.is_off"));
}

{  // the absence reminder alone: its lengths and the times show, the notice stays off
  const world: World = { calls: [], stored: null, held: false };
  await rowIn(world).open();
  await toggle("away", true);
  expect("on alone", world.calls, ["subscribe", put({ ...AWAY, hands_free: false })]);
  expect("states", state(), { away: true, hands: false, lengths: true, times: true });
}

{  // both ride one subscription; turning either off keeps the other and the times
  const world: World = { calls: [], stored: null, held: false };
  await rowIn(world).open();
  await toggle("away", true);
  await toggle("hands", true);
  expect("one subscription for both", world.calls, ["subscribe", put({ ...AWAY, hands_free: false }), put({ ...AWAY, hands_free: true })]);
  expect("states", state(), { away: true, hands: true, lengths: true, times: true });
  world.calls = [];
  await toggle("away", false);
  expect("the absence reminder off keeps the notice", world.calls, [put({ ...NOTICE, hands_free: true })]);
  expect("and the times stay", state(), { away: false, hands: true, lengths: false, times: true });
  world.calls = [];
  await toggle("away", true);
  await toggle("hands", false);
  expect("the notice off keeps the absence reminder", world.calls, [put({ ...AWAY, hands_free: true }), put({ ...AWAY, hands_free: false })]);
}

{  // one window for every kind: Any time with only the notice on is sent with equal ends
  const world: World = { calls: [], stored: null, held: false };
  await rowIn(world).open();
  await toggle("hands", true);
  world.calls = [];
  const any = fakeDocument.querySelector(".reminders-any input")!;
  any.checked = true;
  any.dispatchEvent(new FakeEvent("change"));
  await settle();
  expect("the notice's times are any time", world.calls, [put({ after_hours: null, send_from_hour: 9, send_until_hour: 9, hands_free: true })]);
}

{  // opening shows what the server holds for this browser, the times included
  const world: World = { calls: [], stored: { after_hours: null, send_from_hour: 22, send_until_hour: 7, hands_free: true }, held: true };
  await rowIn(world).open();
  expect("the notice shows on, the reminder off", state(), { away: false, hands: true, lengths: false, times: true });
  expect("with its times", fakeDocument.querySelector(".reminders-window-said")!.textContent.replace(/\s+/g, " ").trim().includes("22:00"), true);
}

{  // control: the checks above can fail (a notice-only world drawn as none on reads differently)
  const world: World = { calls: [], stored: null, held: false };
  await rowIn(world).open();
  let failed = false;
  try { expect("control", state(), { away: false, hands: true, lengths: false, times: true }); } catch { failed = true; }
  expect("the state check fails on a wrong state", failed, true);
}
