// The hands-free notice in the reminders row (src/ui/reminders.ts): off at first, either choice on alone, the
// subscription made when the first goes on and dropped only when both are off, and what the server holds shown on open.
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

const box = () => fakeDocument.querySelector(".reminders-hands input")!;
const toggle = async (on: boolean) => {
  box().checked = on;
  box().dispatchEvent(new FakeEvent("change"));
  await new Promise((resolve) => setTimeout(resolve, 5));
};
const press = async () => {
  fakeDocument.querySelector(".reminders-controls > button")!.click();
  await new Promise((resolve) => setTimeout(resolve, 5));
};
const WINDOW = { after_hours: 24, send_from_hour: 9, send_until_hour: 21 };

{  // off at first, with its words on screen; on alone subscribes and sends no window; off again drops the browser
  const world: World = { calls: [], stored: null, held: false };
  const row = rowIn(world);
  await row.open();
  expect("drawn off", box().checked, false);
  expect("its words", [fakeDocument.querySelector(".reminders-hands span")!.textContent, fakeDocument.querySelector(".reminders-hands-said")!.textContent],
    [text.get("ui.reminders.hands_free"), text.get("ui.reminders.hands_free_said")]);
  await toggle(true);
  expect("on alone", world.calls, ["subscribe", `put ${JSON.stringify({ window: null, hands_free: true })}`]);
  expect("checked", box().checked, true);
  world.calls = [];
  await toggle(false);
  expect("off with nothing else on drops the browser", world.calls, ["off", "unsubscribe"]);
}

{  // with the absence reminder on, the notice rides the same subscription, and turning either off keeps the other
  const world: World = { calls: [], stored: null, held: false };
  const row = rowIn(world);
  await row.open();
  await press();
  await toggle(true);
  expect("one subscription for both", world.calls, ["subscribe", `put ${JSON.stringify({ window: WINDOW, hands_free: false })}`,
    `put ${JSON.stringify({ window: WINDOW, hands_free: true })}`]);
  world.calls = [];
  await press();
  expect("the absence reminder off keeps the notice", world.calls, [`put ${JSON.stringify({ window: null, hands_free: true })}`]);
  expect("and the button offers it again", fakeDocument.querySelector(".reminders-controls > button")!.textContent, text.get("ui.reminders.turn_on"));
  world.calls = [];
  await press();
  await toggle(false);
  expect("the notice off keeps the absence reminder", world.calls, [`put ${JSON.stringify({ window: WINDOW, hands_free: true })}`,
    `put ${JSON.stringify({ window: WINDOW, hands_free: false })}`]);
}

{  // opening shows what the server holds for this browser
  const world: World = { calls: [], stored: { window: null, hands_free: true }, held: true };
  const row = rowIn(world);
  await row.open();
  expect("the notice shows on", box().checked, true);
  expect("the absence reminder shows off", fakeDocument.querySelector(".reminders-controls > button")!.textContent, text.get("ui.reminders.turn_on"));
}
