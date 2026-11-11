// Reminders on the page: the window slider (shading past midnight, keys, labels), what the row offers in each state
// of the server and browser (pushCap), the one mention drawn once and kept when drawn, and a presentation write that
// an older build still accepts.
import { install, FakeEvent, fakeDocument } from "./fake-dom";
import type { AccountPresentation } from "../src/api/types";
import { pushCap, type PushEnv } from "../src/app/push";
import { awayKey } from "../src/game/reminderkeys";
import { Keeps, NEW_ACCOUNT } from "../src/game/keeps";
import { sendable } from "../src/game/presentation";
import { Text } from "../src/game/text";
import { fixtureContent } from "../fixtures/content";
import { el } from "../src/ui/dom";
import { clock12, clock24, HourSlider, keyed, shaded } from "../src/ui/hourslider";
import { mentionDue, ReminderMention } from "../src/ui/remindermention";
import { rowState, windowPhrase } from "../src/ui/reminders";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}
const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);

install();

// the shaded span: inside the day, wrapped past midnight, and the whole day when the ends are equal
check(same(shaded({ from: 9, until: 21 }), [[9, 21]]), "9 until 21 shades one span");
check(same(shaded({ from: 22, until: 7 }), [[22, 24], [0, 7]]), "22 until 7 wraps past midnight");
check(same(shaded({ from: 5, until: 5 }), [[0, 24]]), "equal ends are any hour");
check(clock24(21) === "21:00" && clock12(21) === "9 PM", "21:00 over 9 PM");
check(clock24(0) === "00:00" && clock12(0) === "12 AM" && clock12(12) === "12 PM" && clock12(9) === "9 AM", "midnight and noon");
const said = (w: { from: number; until: number }) => windowPhrase("From {from} until {until}", w).map((n) => n.textContent).join("");
check(said({ from: 9, until: 21 }) === "From 09:00 9 AM until 21:00 9 PM", "an unwrapped window reads from, then until");
check(said({ from: 22, until: 7 }) === "From 22:00 10 PM until 07:00 7 AM", "a wrapped window names which end is which");
check(keyed("ArrowRight", 9) === 10 && keyed("ArrowDown", 9) === 8 && keyed("PageUp", 22) === 23, "keys step and clamp");
check(keyed("Home", 9) === 0 && keyed("End", 9) === 23 && keyed("a", 9) === null, "Home, End, and a key it does not take");

// the slider by keyboard: a handle is an ARIA slider whose value and text follow the keys
const seen: string[] = [];
const slider = new HourSlider({ from: "From", until: "Until" }, { from: 9, until: 21 }, (w) => seen.push(`${w.from}-${w.until}`));
document.body.append(slider.root);
const handles = fakeDocument.body.querySelectorAll(".hour-handle");
check(handles.length === 2 && handles[0]?.getAttribute("role") === "slider", "two slider handles");
const press = (i: number, key: string) => handles[i]?.dispatchEvent(Object.assign(new FakeEvent("keydown"), { key }));
press(1, "End");
press(0, "End");
check(same(seen, ["9-23", "23-23"]), `keys move the handle they are pressed on: ${seen.join()}`);
check(handles[0]?.getAttribute("aria-valuetext") === "23:00 (11 PM)", "the value text says both clocks");
slider.disabled = true;
press(0, "Home");
check(seen.length === 2, "a disabled slider takes no key");

// the row's state: a server from before reminders offers nothing, no key says so, then the browser's four
const cfg = { public_key: "k", after_hours: [12, 24, 72, 168] };
check(rowState(undefined, "ok") === "hidden", "no reminders key: no row");
check(rowState(null, "ok") === "unavailable", "a null key: not available here");
const env: PushEnv = { userAgent: "Mozilla/5.0 (X11; Linux x86_64) Firefox/140.0", maxTouchPoints: 0, platform: "Linux x86_64",
  standalone: false, hasPush: true, permission: "default" };
check(pushCap(env) === "ok", "a desktop browser can push");
check(pushCap({ ...env, permission: "denied" }) === "denied", "blocked notifications");
check(pushCap({ ...env, hasPush: false }) === "none", "no Web Push");
const iphone = { ...env, userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) Safari/604.1" };
check(pushCap(iphone) === "ios-install", "iOS in a Safari tab must be installed first");
check(pushCap({ ...iphone, standalone: true }) === "ok", "iOS from the Home Screen can push");
check(pushCap({ ...env, platform: "MacIntel", maxTouchPoints: 5 }) === "ios-install", "an iPad asking for the desktop site");
check(rowState(cfg, pushCap(iphone)) === "ios-install", "the row tells iOS to install");
check(same(awayKey(72), { key: "ui.reminders.h72", n: 3 }) && same(awayKey(12), { key: "ui.reminders.h12", n: 12 }), "absences in days when whole");

// the mention: due only once the end is read and nothing holds the glow, where reminders are offered
const quiet = { endRead: true, busy: false };
check(mentionDue(quiet, false, cfg, "ok"), "due when quiet");
check(!mentionDue({ ...quiet, busy: true }, false, cfg, "ok") && !mentionDue({ ...quiet, endRead: false }, false, cfg, "ok"), "not while busy or before the end");
check(!mentionDue(quiet, true, cfg, "ok") && !mentionDue(quiet, false, null, "ok") && !mentionDue(quiet, false, cfg, "none"), "not twice, not unoffered");

const sent: AccountPresentation[] = [];
const keeps = new Keeps({ account: { ...NEW_ACCOUNT } }, { account: (p) => sent.push(p) });
const text = new Text(fixtureContent);
let opened = 0;
const mention = new ReminderMention(keeps, text, () => { opened += 1; }, () => Promise.resolve(cfg), () => "ok");
const foot = el("div");
const panel = el("div");
panel.append(foot);
await mention.check({ endRead: true, busy: true }, foot);
check(sent.length === 0, "nothing drawn or kept while busy");
await mention.check(quiet, foot);
check(panel.querySelectorAll(".reminder-mention").length === 1, "drawn once quiet");
check(sent.length === 1 && sent[0]?.reminder_mentioned === true, "kept as shown when drawn, before any tap");
await mention.check(quiet, foot);
const again = new ReminderMention(keeps, text, () => undefined, () => Promise.resolve(cfg), () => "ok");
await again.check(quiet, foot);
check(panel.querySelectorAll(".reminder-mention").length === 1 && sent.length === 1, "never drawn again, a new screen included");
panel.querySelector<HTMLButtonElement>(".reminder-mention button")?.click();
check(opened === 1 && panel.querySelectorAll(".reminder-mention").length === 0, "its button opens the setting and the row goes");
const reloaded = new Keeps({ account: { ...NEW_ACCOUNT, reminder_mentioned: true } }, { account: (p) => sent.push(p) });
const fresh = el("div");
const box = el("div");
box.append(fresh);
await new ReminderMention(reloaded, text, () => undefined, () => Promise.resolve(cfg), () => "ok").check(quiet, fresh);
check(box.querySelectorAll(".reminder-mention").length === 0, "a reload or a second device, given the kept flag, draws nothing");

// a write leaves the field out until it is set, so a build from before reminders still takes it
check(!("reminder_mentioned" in sendable({ ...NEW_ACCOUNT })), "unset: not sent");
check(sendable({ ...NEW_ACCOUNT, reminder_mentioned: true }).reminder_mentioned === true, "set: sent");
