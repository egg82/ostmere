// The one mention of reminders (docs/design/reminders.md, "The single mention"): a quiet row with a button to the
// setting, drawn once per account once the end's lines have been read and nothing holds the glow, where this server
// offers reminders and this browser could take them. It is kept as shown when drawn, not when tapped
// (AccountPresentation.reminder_mentioned), so taking it, ignoring it and reloading all leave it gone.
import type { RemindersConfig } from "../app/pageconfig";
import type { PushCap } from "../app/push";
import type { Keeps } from "../game/keeps";
import { REMINDER_KEYS as K } from "../game/reminderkeys";
import type { Text } from "../game/text";
import { el } from "./dom";

export interface Moment {
  /** The end's lines have been read (TheEnd.behind). */
  endRead: boolean;
  /** Something holds the one glow, or a line is still being revealed. */
  busy: boolean;
}

export function mentionDue(m: Moment, mentioned: boolean, cfg: RemindersConfig | null | undefined, cap: PushCap): boolean {
  return m.endRead && !m.busy && !mentioned && cfg !== null && cfg !== undefined && cap !== "none";
}

export class ReminderMention {
  private row: HTMLElement | null = null;

  constructor(private readonly keeps: Keeps, private readonly text: Text, private readonly openSetting: () => void,
    private readonly config: () => Promise<RemindersConfig | null | undefined>, private readonly cap: () => PushCap) {}

  /** Draws the row before `foot` when it is due; at most once. */
  async check(m: Moment, foot: HTMLElement): Promise<void> {
    if (this.row || this.keeps.reminderMentioned() || !m.endRead || m.busy) return;
    if (!mentionDue(m, this.keeps.reminderMentioned(), await this.config(), this.cap()) || this.row) return;
    const row = el("div", "reminder-mention");
    const go = el("button", "quiet", this.text.get(K.remindersMentionOpen));
    go.type = "button";
    go.addEventListener("click", () => { row.remove(); this.openSetting(); });
    row.append(el("span", "", this.text.get(K.remindersMention)), go);
    foot.before(row);
    this.row = row;
    this.keeps.keepReminderMentioned();
  }
}
