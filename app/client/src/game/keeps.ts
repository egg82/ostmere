// What the server keeps for the page that is not game state (CONTRACT.txt): about the player across saves
// (AccountPresentation: the Rules tab opened, the "Another device" sheet opened, the ledger lines shown, the journal
// notes read, the repeated-switch rules answered), about this save's teaching (SavePresentation: the lessons done or
// skipped, a rule seen on then off, the mix-hint dots touched), and the player's settings (AccountSettings: lessons on
// or off). Read when the game begins or opens; each change is sent at once with the page's whole copy, and the
// server's answer, which holds what other pages kept, is adopted (presentation.ts). A send that fails is only logged
// (the page goes on as if it was kept).
import type { GameApi } from "../api/api";
import type { AccountPresentation, AccountSettings, Chapter, LessonEnd, OfferedSwitch, SavePresentation, Visit } from "../api/types";
import { AWAY_MIN_S, MAX_VISITS } from "./chronicle";
import { mergePresentation, mergeSavePresentation, sendable, sendableSave } from "./presentation";

export interface KeepsSink {
  account?(presentation: AccountPresentation): void;
  save?(presentation: SavePresentation): void;
  settings?(settings: AccountSettings): void;
}

/** Everything a page keeps: the account's, this save's, and the player's settings. */
export interface Kept {
  account: AccountPresentation;
  save: SavePresentation;
  settings: AccountSettings;
}

const NOWHERE: KeepsSink = {};
export const NEW_ACCOUNT: AccountPresentation = { rules_opened: false, devices_opened: false, reminder_mentioned: false, ledger_lines: [], mix_stopped: [], switch_offered: [], journal_read: [] };
export const NEW_SAVE: SavePresentation = { rule_seen: false, mix_offered: [], lessons: [], lesson_ends: [], visits: [] };
export const NEW_SETTINGS: AccountSettings = { lessons: true };

export class Keeps {
  private account: AccountPresentation;
  private save: SavePresentation;
  private settings: AccountSettings;

  constructor(kept: Partial<Kept> = {}, private readonly sink: KeepsSink = NOWHERE) {
    this.account = kept.account ?? NEW_ACCOUNT;
    this.save = kept.save ?? NEW_SAVE;
    this.settings = kept.settings ?? NEW_SETTINGS;
  }

  private keepAccount(account: AccountPresentation): void {
    this.account = account;
    this.sink.account?.(account);
  }

  private keepSave(save: SavePresentation): void {
    this.save = save;
    this.sink.save?.(save);
  }

  /** A rule has been seen on and then off in this save: writing rules is open. */
  ruleSeen(): boolean {
    return this.save.rule_seen ?? false;
  }

  keepRuleSeen(): void {
    if (this.save.rule_seen) return;
    this.keepSave({ ...this.save, rule_seen: true });
  }

  /** The player has opened the Rules tab: its label needs no glow. */
  rulesOpened(): boolean {
    return this.account.rules_opened ?? false;
  }

  keepRulesOpened(): void {
    if (this.account.rules_opened) return;
    this.keepAccount({ ...this.account, rules_opened: true });
  }

  /** The player has opened the "Another device" sheet: its button needs no dot. */
  devicesOpened(): boolean {
    return this.account.devices_opened ?? false;
  }

  keepDevicesOpened(): void {
    if (this.account.devices_opened) return;
    this.keepAccount({ ...this.account, devices_opened: true });
  }

  /** The one mention of reminders has been drawn: it is never drawn again (ui/remindermention.ts). */
  reminderMentioned(): boolean {
    return this.account.reminder_mentioned ?? false;
  }

  keepReminderMentioned(): void {
    if (this.account.reminder_mentioned) return;
    this.keepAccount({ ...this.account, reminder_mentioned: true });
  }

  /** The store's ledger line has been shown: it stays. */
  ledgerShown(store: string): boolean {
    return (this.account.ledger_lines ?? []).includes(store);
  }

  keepLedgerLine(store: string): void {
    if (this.ledgerShown(store)) return;
    this.keepAccount({ ...this.account, ledger_lines: [...(this.account.ledger_lines ?? []), store] });
  }

  /** The card's "your mix could take it" dot has been touched in this save: it is not marked again. */
  mixOffered(card: string): boolean {
    return (this.save.mix_offered ?? []).includes(card);
  }

  keepMixOffered(card: string): void {
    if (this.mixOffered(card)) return;
    this.keepSave({ ...this.save, mix_offered: [...(this.save.mix_offered ?? []), card] });
  }

  /** The rule offer for this repeated switch has been answered: it is not offered again. */
  switchOffered(s: OfferedSwitch): boolean {
    return (this.account.switch_offered ?? []).some((o) => o.chip === s.chip && o.mix_id === s.mix_id);
  }

  keepSwitchOffered(s: OfferedSwitch): void {
    if (this.switchOffered(s)) return;
    this.keepAccount({ ...this.account, switch_offered: [...(this.account.switch_offered ?? []), { chip: s.chip, mix_id: s.mix_id }] });
  }

  /** Lessons run in this account's games: the player has not turned them off. */
  lessonsOn(): boolean {
    return this.settings.lessons ?? true;
  }

  /** The player turns lessons on or off for every game of the account. */
  keepLessonsOn(on: boolean): void {
    if (this.lessonsOn() === on) return;
    this.settings = { ...this.settings, lessons: on };
    this.sink.settings?.(this.settings);
  }

  /** The lesson has been done or skipped in this save: it never comes again in it (game/lessons.ts). */
  lessonKept(id: string): boolean {
    return (this.save.lessons ?? []).includes(id);
  }

  /** The lesson ended done in this save: finished, not skipped. */
  lessonDone(id: string): boolean {
    return (this.save.lesson_ends ?? []).some((e) => e.lesson === id && !e.skipped);
  }

  /** Kept with how it ended: the step it ended on and the longest wait on one step (the server logs it). */
  keepLesson(end: LessonEnd): void {
    if (this.lessonKept(end.lesson)) return;
    this.keepSave({ ...this.save, lessons: [...(this.save.lessons ?? []), end.lesson],
      lesson_ends: [...(this.save.lesson_ends ?? []), end] });
  }

  /** This save's returns after a long time away, oldest first: the chronicle's stretches begin at each one's `left`. */
  visits(): Visit[] {
    return this.save.visits ?? [];
  }

  /** A return from `left` to `back`, kept once per `left` when it was long enough to be a visit, with its figures
   * (game/chapter.ts) as the save's chapter in the same write. */
  keepReturn(left: number, back: number, chapter: Chapter | null = null): void {
    if (back - left < AWAY_MIN_S || this.visits().some((v) => v.left === left)) return;
    this.keepSave({ ...this.save, visits: [...this.visits(), { left, back }].slice(-MAX_VISITS), ...(chapter ? { chapter } : {}) });
  }

  /** The newest return's figures, null when none were kept (a return before they were, or none yet). */
  chapter(): Chapter | null {
    return this.save.chapter ?? null;
  }

  /** The note has been read: its page was turned to with the note on it (ui/journal.ts). Kept for the account. */
  journalRead(note: string): boolean {
    return (this.account.journal_read ?? []).includes(note);
  }

  /** The notes of the pages turned to, kept at once as one write; nothing is sent when none is new. */
  keepJournalRead(notes: Iterable<string>): void {
    const fresh = [...new Set(notes)].filter((n) => !this.journalRead(n));
    if (fresh.length === 0) return;
    this.keepAccount({ ...this.account, journal_read: [...(this.account.journal_read ?? []), ...fresh] });
  }

  /** The account's copy the server answered a send with, which holds what other pages kept: joined into the page's own. */
  adopt(kept: AccountPresentation): void {
    this.account = mergePresentation(this.account, kept);
  }

  /** The save's copy the server answered a send with: joined into the page's own. */
  adoptSave(kept: SavePresentation): void {
    this.save = mergeSavePresentation(this.save, kept);
  }

  /** The settings the server answered a settings write with. */
  adoptSettings(kept: AccountSettings): void {
    this.settings = kept;
  }

  /** What the page keeps: the account's and the settings carry into another save; the save's is this one's. */
  get kept(): Kept {
    return { account: this.account, save: this.save, settings: this.settings };
  }
}

/** The keeps for save `saveId` (`kept`: what it keeps, null for the save in `was`), `was`'s account and settings carried
 * on; each change sent, the answer adopted. */
export function sentKeeps(api: GameApi, saveId: number, was: Kept, kept: SavePresentation | null): Keeps {
  const notKept = (e: unknown): void => console.warn("ashfall: not kept", e);
  const keeps: Keeps = new Keeps({ ...was, save: kept ?? was.save }, {
    account: (p) => void api.putMePresentation(sendable(p)).then((a) => keeps.adopt(a.presentation)).catch(notKept),
    save: (p) => void api.putSavePresentation(saveId, sendableSave(p)).then((s) => keeps.adoptSave(s)).catch(notKept),
    settings: (s) => void api.putMeSettings(s).then((a) => keeps.adoptSettings(a.settings)).catch(notKept),
  });
  return keeps;
}
