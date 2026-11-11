// "Another device" (CONTRACT.txt, "Moving to another device"): a quiet text button at the panel's foot opening a sheet
// of four parts, a code to join another device to this game (devicecode.ts), recovery words for when every device is
// gone (devicewords.ts), joining this device to another (devicejoin.ts), and the account's browsers with a Remove on
// each (devicelist.ts), then this device's reminders (reminders.ts). A join that left this device's games behind replaces the four with the step that shows their
// words (devicekept.ts), and the sheet cannot be closed until its Continue reloads. The button carries the quiet dot while recovery words are due and the sheet has never been
// opened; opening it clears the dot for good (Keeps).
import type { GameApi } from "../api/api";
import type { Account, KeptGames } from "../api/types";
import type { Format } from "../game/format";
import { refusal, refusalLine, type JoinRefusal } from "../game/joining";
import type { Keeps } from "../game/keeps";
import { UI, type Text } from "../game/text";
import { CodePart } from "./devicecode";
import { DeviceList } from "./devicelist";
import { KeptPart } from "./devicekept";
import { ReminderRow } from "./reminders";
import { JoinPart } from "./devicejoin";
import { WordsPart } from "./devicewords";
import { el } from "./dom";

export interface DevicesContext {
  api: GameApi;
  text: Text;
  format: Format;
  /** The line for a refusal: a join's (with MergeSummary.max_saves when it came), or any failed request's. */
  refusalLine(why: JoinRefusal | unknown, max?: number | null): string;
}
const WORDS_LABEL = "Ostmere";   // RecoveryWords.label

export class Devices {
  readonly button = el("button", "devices-open");
  readonly root = el("dialog", "sheet devices-sheet");
  private readonly dot = el("span", "new-dot");
  private readonly code: CodePart;
  private readonly words: WordsPart;
  private readonly joining: JoinPart;
  private readonly list: DeviceList;
  private readonly kept: KeptPart;
  readonly reminders: ReminderRow;
  private readonly actions = el("div", "sheet-actions");
  private held = false;

  constructor(api: GameApi, text: Text, format: Format, codeS: number, private readonly keeps: Keeps,
    account: Account | null) {
    const ctx: DevicesContext = {
      api, text, format,
      refusalLine: (why, max = null) =>
        refusalLine(text, codeS, typeof why === "string" ? (why as JoinRefusal) : refusal(why), max),
    };
    this.code = new CodePart(ctx);
    this.words = new WordsPart(ctx, account?.has_words ?? false);
    this.kept = new KeptPart(ctx);
    this.joining = new JoinPart(ctx, WORDS_LABEL, (kept) => this.leave(kept));
    this.list = new DeviceList(ctx);
    this.reminders = new ReminderRow(text);
    this.button.type = "button";
    this.button.append(text.get(UI.devicesOpen));
    this.dot.setAttribute("aria-hidden", "true");
    this.dot.hidden = !(account?.words_due ?? false) || keeps.devicesOpened();
    this.button.append(this.dot);
    this.button.addEventListener("click", () => this.open(null));
    const close = el("button", "quiet", text.get(UI.close));
    close.type = "button";
    close.addEventListener("click", () => this.root.close());
    this.actions.append(close);
    this.root.append(el("h2", "panel-heading", text.get(UI.devicesHeading)), this.code.root, this.words.root,
      this.joining.root, this.list.root, this.reminders.root, this.kept.root, this.actions);
    this.root.addEventListener("click", (e) => { if (e.target === this.root && !this.held) this.root.close(); });
    this.root.addEventListener("cancel", (e) => { if (this.held) e.preventDefault(); });
    this.root.addEventListener("close", () => this.code.stop());
  }

  /** The join left this device's games on their old account: only their words are left to show. */
  private leave(kept: KeptGames): void {
    this.held = true;
    for (const part of [this.code.root, this.words.root, this.joining.root, this.list.root, this.reminders.root, this.actions]) part.hidden = true;
    this.code.stop();
    this.kept.show(kept);
  }

  /** The sheet; with `join` (a join link's code), its code waits in the join box and no code of this account is made. */
  open(join: string | null): void {
    this.dot.hidden = true;
    this.keeps.keepDevicesOpened();
    this.words.reset();
    this.list.open();
    void this.reminders.open();
    if (!this.root.open) this.root.showModal();
    if (join === null) void this.code.make();
    else this.joining.fill(join);
  }
}
