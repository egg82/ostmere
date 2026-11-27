// Settings: a quiet text button at the panel's foot opening a sheet of the player's choices, beside Games and "Another
// device" (which holds only what moves a game between devices). Each group is headed by what its choices are bound to,
// this device or every game; each choice is shown as the sheet opens.
import type { Straight } from "../../app/straight";
import { UI, type Text } from "../../game/text";
import { el } from "../dom";
import { openSheet } from "../back";
import type { ReminderRow } from "./reminders";
import type { SoundControl } from "./soundcontrol";
import { checkChoice, straightChoice } from "../front/straightchoice";

export class SettingsSheet {
  readonly button = el("button", "settings-open");
  readonly root = el("dialog", "sheet settings-sheet");
  private readonly opens: (() => void | Promise<void>)[];

  /** `straight` is this device's choice to open straight into a game; `skipLessons` the account's, checked: lessons off;
   * `sound` is the device's sound switch, there once a sound is registered. */
  constructor(text: Text, readonly reminders: ReminderRow, straight: Straight, skipLessons: Straight, sound: SoundControl | null = null) {
    const open = straightChoice(text, straight, "settings-choice", "settings-straight");
    const lessons = checkChoice(text.get(UI.gameSkipLessons), skipLessons, "settings-choice", "settings-lessons");
    const device = group(text.get(UI.settingsDevice), reminders.root, ...(sound ? [sound.row] : []), open.root);
    const every = group(text.get(UI.settingsEvery), lessons.root);
    this.opens = [() => reminders.open(), ...(sound ? [sound.show] : []), open.show, lessons.show];
    this.button.type = "button";
    this.button.textContent = text.get(UI.settingsOpen);
    this.button.addEventListener("click", () => void this.open());
    const close = el("button", "quiet", text.get(UI.close));
    close.type = "button";
    close.addEventListener("click", () => this.root.close());
    const foot = el("div", "sheet-actions");
    foot.append(close);
    this.root.append(el("h2", "panel-heading", text.get(UI.settingsHeading)), device, every, foot);
    this.root.addEventListener("click", (e) => { if (e.target === this.root) this.root.close(); });
  }

  /** Shows the sheet; resolves once every part has drawn what it offers. */
  async open(): Promise<void> {
    const drawn = this.opens.map((show) => show());
    if (!this.root.open) openSheet(this.root);
    await Promise.all(drawn);
  }

  /** The reminders mention's way in: the sheet, with the reminders row focused once it is drawn. */
  async showReminders(): Promise<void> {
    await this.open();
    this.reminders.focus();
  }
}

/** A group of choices under a heading naming what they are bound to, ruled like the parts of "Another device". */
function group(heading: string, ...rows: HTMLElement[]): HTMLElement {
  const box = el("section", "devices-part");
  box.append(el("h3", "lane-tag", heading), ...rows);
  return box;
}
