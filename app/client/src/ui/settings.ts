// Settings: a quiet text button at the panel's foot opening a sheet of this device's own choices, beside Games and
// "Another device" (which holds only what moves a game between devices). The sheet's parts are listed in one array,
// each a root and an open() called as the sheet opens.
import { UI, type Text } from "../game/text";
import { el } from "./dom";
import type { ReminderRow } from "./reminders";

export interface SettingsPart {
  root: HTMLElement;
  open(): void | Promise<void>;
}

export class SettingsSheet {
  readonly button = el("button", "settings-open");
  readonly root = el("dialog", "sheet settings-sheet");
  private readonly parts: SettingsPart[];

  constructor(text: Text, readonly reminders: ReminderRow) {
    this.parts = [reminders];
    this.button.type = "button";
    this.button.textContent = text.get(UI.settingsOpen);
    this.button.addEventListener("click", () => void this.open());
    const close = el("button", "quiet", text.get(UI.close));
    close.type = "button";
    close.addEventListener("click", () => this.root.close());
    const foot = el("div", "sheet-actions");
    foot.append(close);
    this.root.append(el("h2", "panel-heading", text.get(UI.settingsHeading)), el("p", "devices-lead", text.get(UI.settingsDevice)),
      ...this.parts.map((p) => p.root), foot);
    this.root.addEventListener("click", (e) => { if (e.target === this.root) this.root.close(); });
  }

  /** Shows the sheet; resolves once every part has drawn what it offers. */
  async open(): Promise<void> {
    const drawn = this.parts.map((p) => p.open());
    if (!this.root.open) this.root.showModal();
    await Promise.all(drawn);
  }

  /** The reminders mention's way in: the sheet, with the reminders row focused once it is drawn. */
  async showReminders(): Promise<void> {
    await this.open();
    this.reminders.focus();
  }
}
