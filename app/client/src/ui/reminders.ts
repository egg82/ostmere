// Reminders for this device, a row of the Settings sheet (docs/design/reminders.md, "What the player sees" and "The
// hands-free notice"): two choices, each off at first and either on alone, sharing the browser's one subscription:
// the absence reminder (its choices, the window slider and "Any time") and the hands-free notice. Turning either on
// asks the browser's permission with the purpose already on screen. A server from before reminders offers no row; one without a VAPID key, or a
// browser that cannot push, says so and offers nothing. On open the row checks the browser's subscription against
// the server's, so it never shows on when either side has let go.
import { httpReminders, type Reminder, type ReminderWindow, type RemindersApi } from "../api/reminders";
import { remindersConfig, type RemindersConfig } from "../app/pageconfig";
import { browserEnv, current, pushCap, subscribe, zone, type PushCap, type Subscribed } from "../app/push";
import { awayKey, REMINDER_KEYS as K } from "../game/reminderkeys";
import type { Text } from "../game/text";
import { el } from "./dom";
import { clock12, clock24, HourSlider, type HourWindow } from "./hourslider";

/** The window in words: `template`'s {from} and {until} become the 24-hour time with the 12-hour time beside it, so
 * a window that wraps past midnight reads in the order it runs. */
export function windowPhrase(template: string, w: HourWindow): HTMLElement[] {
  return template.split(/(\{from\}|\{until\})/).map((part) => {
    if (part !== "{from}" && part !== "{until}") return el("span", "", part);
    const h = part === "{from}" ? w.from : w.until;
    const time = el("span", "hour-time", `${clock24(h)} `);
    time.append(el("span", "hour-12", clock12(h)));
    return time;
  });
}

export type RowState = "hidden" | "unavailable" | PushCap;

export function rowState(cfg: RemindersConfig | null | undefined, cap: PushCap): RowState {
  if (cfg === undefined) return "hidden";
  return cfg === null ? "unavailable" : cap;
}

export interface ReminderDeps {
  api: RemindersApi;
  config: () => Promise<RemindersConfig | null | undefined>;
  cap: () => PushCap;
  current: () => Promise<{ sub: PushSubscription; keys: Subscribed } | null>;
  subscribe: (publicKey: string) => Promise<{ sub: PushSubscription; keys: Subscribed } | null>;
  zone: () => string;
}

const BROWSER: ReminderDeps = { api: httpReminders, config: remindersConfig, cap: () => pushCap(browserEnv()), current, subscribe, zone };
const SAID: Partial<Record<RowState, string>> = {
  unavailable: K.remindersUnavailable, "ios-install": K.remindersInstall, denied: K.remindersDenied, none: K.remindersNone,
};
const START: HourWindow = { from: 9, until: 21 };   // where the setting starts, not a rule
const START_AWAY = 24;
const SEND_AFTER_MS = 600;   // a dragged handle settles before its window is sent

export class ReminderRow {
  readonly root = el("section", "reminders-part");
  private readonly said = el("p", "reminders-said");
  private readonly controls = el("div", "reminders-controls");
  private readonly choices = el("fieldset", "reminders-away");
  private readonly anyTime = el("input");
  private readonly slider: HourSlider;
  private readonly windowSaid = el("p", "reminders-window-said");
  private readonly button = el("button");
  private readonly handsBox = el("input");
  private away = START_AWAY;
  private on: { sub: PushSubscription; keys: Subscribed } | null = null;   // the server holds a row for it
  private absence = false;
  private handsFree = false;
  private key = "";
  private timer: ReturnType<typeof setTimeout> | null = null;

  constructor(private readonly text: Text, private readonly deps: ReminderDeps = BROWSER) {
    this.said.setAttribute("aria-live", "polite");
    this.slider = new HourSlider({ from: text.get(K.remindersFrom), until: text.get(K.remindersUntil) }, START,
      () => { this.sayWindow(); this.changed(true); });
    this.anyTime.type = "checkbox";
    this.anyTime.addEventListener("change", () => { this.slider.disabled = this.anyTime.checked; this.sayWindow(); this.changed(false); });
    const any = el("label", "reminders-any");
    any.append(this.anyTime, text.get(K.remindersAnyTime));
    const windowBox = el("fieldset", "reminders-window");
    windowBox.append(el("legend", "", text.get(K.remindersWindow)), this.slider.root, this.windowSaid, any);
    this.button.type = "button";
    this.button.addEventListener("click", () => void this.keep(!this.absence, this.handsFree, true));
    this.handsBox.type = "checkbox";
    this.handsBox.addEventListener("change", () => void this.keep(this.absence, this.handsBox.checked, false));
    const hands = el("label", "settings-choice reminders-hands");
    hands.append(this.handsBox, el("span", "", text.get(K.remindersHandsFree)));
    const handsPart = el("div", "reminders-hands-part");
    handsPart.append(hands, el("p", "reminders-hands-said", text.get(K.remindersHandsFreeSaid)));
    this.controls.append(this.choices, windowBox, this.button, handsPart);
    this.root.append(el("h3", "part-heading", text.get(K.remindersHeading)), this.said, this.controls);
    this.root.hidden = true;
    this.sayWindow();
  }

  /** Called as the sheet opens: what this server and browser can do, and whether this device is on. */
  async open(): Promise<void> {
    const cfg = await this.deps.config();
    const state = rowState(cfg, this.deps.cap());
    this.root.hidden = state === "hidden";
    this.controls.hidden = state !== "ok";
    if (state !== "ok" || !cfg) {
      this.said.textContent = SAID[state] ? this.text.get(SAID[state]) : "";
      return;
    }
    this.key = cfg.public_key;
    this.drawChoices(cfg.after_hours);
    await this.sync();
  }

  focus(): void {
    (this.controls.hidden ? this.root : this.choices.querySelector<HTMLInputElement>("input:checked") ?? this.root).focus();
  }

  private drawChoices(hours: number[]): void {
    this.choices.replaceChildren(el("legend", "", this.text.get(K.remindersAway)));
    if (!hours.includes(this.away)) this.away = hours[0] ?? START_AWAY;
    for (const h of hours) {
      const input = el("input");
      Object.assign(input, { type: "radio", name: "reminders-away", value: String(h), checked: h === this.away });
      input.addEventListener("change", () => { this.away = h; this.changed(false); });
      const label = el("label", "reminders-choice");
      const away = awayKey(h);
      label.append(input, this.text.fill(away.key, { n: String(away.n) }));
      this.choices.append(label);
    }
  }

  private async sync(): Promise<void> {
    const held = await this.deps.current().catch(() => null);
    const stored = held ? await this.deps.api.put(held.keys, this.deps.zone(), null).catch(() => undefined) : null;
    if (held && stored === null) await held.sub.unsubscribe().catch(() => false);
    this.on = held && stored ? held : null;
    this.absence = Boolean(this.on && stored?.window);
    this.handsFree = Boolean(this.on && stored?.hands_free);
    if (this.on && stored?.window) this.show(stored.window);
    this.drawState(false);
  }

  private show(w: ReminderWindow): void {
    this.away = w.after_hours;
    for (const input of this.choices.querySelectorAll<HTMLInputElement>("input")) input.checked = input.value === String(w.after_hours);
    const any = w.send_from_hour === w.send_until_hour;
    this.anyTime.checked = any;
    this.slider.disabled = any;
    if (!any) this.slider.set({ from: w.send_from_hour, until: w.send_until_hour });
    this.sayWindow();
  }

  private sayWindow(): void {
    this.windowSaid.hidden = this.anyTime.checked;
    this.windowSaid.replaceChildren(...windowPhrase(this.text.get(K.remindersWindowSaid), this.slider.window));
  }

  private picked(): ReminderWindow {
    const w = this.slider.window;
    return { after_hours: this.away, send_from_hour: w.from, send_until_hour: this.anyTime.checked ? w.from : w.until };
  }

  private choice(absence: boolean, handsFree: boolean): Reminder {
    return { window: absence ? this.picked() : null, hands_free: handsFree };
  }

  private drawState(changedNow: boolean): void {
    this.button.textContent = this.text.get(this.absence ? K.remindersOffButton : K.remindersOn);
    this.button.className = this.absence ? "quiet" : "primary";
    this.said.textContent = this.absence ? this.text.get(K.remindersIsOn)
      : this.text.get(changedNow ? K.remindersIsOff : K.remindersLead);
    this.handsBox.checked = this.handsFree;
  }

  private changed(settle: boolean): void {
    if (!this.on || !this.absence) return;
    if (this.timer !== null) clearTimeout(this.timer);
    this.timer = setTimeout(() => { this.timer = null; void this.send(); }, settle ? SEND_AFTER_MS : 0);
  }

  private async send(): Promise<void> {
    if (!this.on) return;
    try {
      await this.deps.api.put(this.on.keys, this.deps.zone(), this.choice(this.absence, this.handsFree));
    } catch {
      this.said.textContent = this.text.get(K.remindersFailed);
    }
  }

  /** This browser with the absence reminder and the hands-free notice as given: subscribed first when neither was on,
   * turned off and unsubscribed when neither is. `said`: the absence reminder is what changed, so the line says so. */
  private async keep(absence: boolean, handsFree: boolean, said: boolean): Promise<void> {
    if (!absence && !handsFree) return this.turnOff(said);
    const got = this.on ?? await this.deps.subscribe(this.key);
    if (!got) {
      this.drawState(false);
      if (this.deps.cap() === "denied") void this.open();
      return;
    }
    try {
      await this.deps.api.put(got.keys, this.deps.zone(), this.choice(absence, handsFree));
      this.on = got;
      this.absence = absence;
      this.handsFree = handsFree;
      this.drawState(said);
    } catch {
      this.drawState(false);
      this.said.textContent = this.text.get(K.remindersFailed);
    }
  }

  private async turnOff(said: boolean): Promise<void> {
    const was = this.on;
    if (was) {
      try {
        await this.deps.api.off(was.keys.endpoint);
      } catch {
        this.drawState(false);
        this.said.textContent = this.text.get(K.remindersFailed);
        return;
      }
      await was.sub.unsubscribe().catch(() => false);
    }
    this.on = null;
    this.absence = this.handsFree = false;
    this.drawState(said);
  }
}
