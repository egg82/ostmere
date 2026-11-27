// The rendered journal on the fixture pages (fixtures/journal.ts), shared by the journal tests: the Book's journal page on
// a real Screen (a phone's sheet unless `phone: false`, the desktop's view), the sent requests and the account writes.
// NOTES_D stand for the fixture's written day: in `notes` they write DAY_D on the step instead of unlocking anything, and
// in `read` they mean its day was turned to (the save's newest_day_read).
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { BOOK, DAY_D, journalStep, journalView, NOTE_B, NOTES_A, NOTES_D, withJournal } from "../fixtures/journal";
import type { JournalDay, Step } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { FIRST_MIX, FIRST_RULE, JOURNAL, JOURNAL_NUMBERS } from "../src/game/lessons/lessons";
import { PHONE } from "../src/ui/layout";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800 });
export const requests: string[] = [];
Object.assign(globalThis, { fetch: (url: string, init?: { body?: string }) => { requests.push(`${url} ${init?.body ?? ""}`); return Promise.resolve({}); } });

/** Sends `type` to `node`; install() makes the global Event the fake DOM's own. */
export function fire(node: HTMLElement, type: string): void {
  node.dispatchEvent(new Event(type));
}

const shown = (x: unknown): string => JSON.stringify(x, (_k, v: unknown) => (v !== null && typeof v === "object" && "tagName" in v ? `<${String((v as { tagName: string }).tagName)}>` : v));

export function expect(label: string, got: unknown, want: unknown): void {
  if (shown(got) !== shown(want)) throw new Error(`${label}: got ${shown(got)}, want ${shown(want)}`);
}

export const catalog = new Catalog(withJournal(fixtureContent));
export const text = (key: string): string => catalog.text.get(key);
export const KEPT = [FIRST_MIX, FIRST_RULE];
export const ALL = [...NOTES_A, NOTE_B];

/** The step with `notes` written and `days` served (NOTES_D among the notes serve DAY_D too). */
export function stepWith(notes: string[], at: number, fought = true, days: JournalDay[] = []): Step {
  const base = journalStep("journal", at);
  const book = notes.filter((n) => !NOTES_D.includes(n));
  const served = notes.some((n) => NOTES_D.includes(n)) ? [DAY_D, ...days] : days;
  const view = journalView({ ...base.view, unlocked: base.view.unlocked.filter((u) => !(u.category === "entry" || u.category === "note" || u.id === BOOK)) }, book);
  return { ...base, view: fought ? view : { ...view, fights: [] }, journal_days: served };
}

export function rig(opts: { read?: string[]; notes?: string[]; lessons?: string[]; phone?: boolean; days?: JournalDay[]; newestDay?: number | null } = {}) {
  const phone = opts.phone ?? true;
  Object.assign(window, { matchMedia: (q: string) => ({ matches: phone && q === PHONE, addEventListener: () => {} }) });
  const sent: Flat[] = [];
  const asked = { decided: 0, dry: 0 };
  const read = opts.read ?? [];
  const kept: Flat = { ...NEW_FLAT, lessons: opts.lessons ?? [...KEPT, JOURNAL, JOURNAL_NUMBERS], journal_read: read.filter((n) => !NOTES_D.includes(n)),
    newest_day_read: opts.newestDay ?? (read.some((n) => NOTES_D.includes(n)) ? DAY_D.day : null) };
  const keeps = keepsOf(kept, sent);
  const screen = new Screen(catalog, () => { asked.decided += 1; }, () => { asked.dry += 1; return Promise.resolve(null); }, keeps);
  document.body.replaceChildren(screen.root);
  let at = 100;
  const show = (notes: string[], days: JournalDay[] = []): void => { at += 10; screen.show(stepWith(notes, at, true, days)); };
  show(opts.notes ?? ALL, opts.days ?? []);
  const q = <T extends HTMLElement = HTMLElement>(sel: string): T | null => screen.root.querySelector<T>(sel);
  const tab = (): HTMLElement => q('.tabs [data-tab="book"]')!;
  /** The Journal's button in the Book, while it is offered. */
  const button = (): HTMLElement | null => { const b = q('.book [data-page="journal"]'); return b && !b.hidden ? b : null; };
  /** Book, then Journal: the one way in. */
  const open = (): void => { tab().click(); button()!.click(); };
  const dotShows = (): boolean => button()?.querySelector(".new-dot") != null;
  const tabDot = (): boolean => tab().querySelector(".new-dot") != null;
  const sheet = (): HTMLElement => q(".book")!;
  const actions = (): HTMLButtonElement[] => [...sheet().querySelectorAll<HTMLButtonElement>(".sheet-actions button")];
  const [contents, prev, next] = [1, 2, 3].map((i) => () => actions()[i]!);
  /** Out of the journal: the sheet's Close on a phone, the Tasks tab on a desktop. */
  const close = (): HTMLElement => (phone ? actions()[0]! : q('.tabs [data-tab="cards"]')!);
  const words = (): string[] => [...sheet().querySelectorAll<HTMLElement>(".journal-words")].map((n) => n.textContent ?? "");
  /** The open page's day headings and words, in page order. */
  const written = (): string[] => [...sheet().querySelectorAll<HTMLElement>(".journal-day, .journal-words")].map((n) => n.textContent ?? "");
  const numbers = (): HTMLElement => sheet().querySelector<HTMLElement>(".journal-numbers")!;
  return { screen, keeps, sent, asked, show, q, tab, button, open, dotShows, tabDot, sheet, close, contents: contents!, prev: prev!, next: next!, words, written, numbers };
}

