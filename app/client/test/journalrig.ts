// The rendered journal on the fixture pages (fixtures/journal.ts), shared by the journal tests: the strip and sheet on a
// real Screen, the sent requests and the account writes.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { BOOK, journalStep, journalView, NOTE_B, NOTES_A, withJournal } from "../fixtures/journal";
import type { Step } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { FIRST_MIX, FIRST_RULE, JOURNAL, JOURNAL_NUMBERS } from "../src/game/lessons";
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

export function stepWith(notes: string[], at: number, fought = true): Step {
  const base = journalStep("journal", at);
  const view = journalView({ ...base.view, unlocked: base.view.unlocked.filter((u) => !(u.category === "entry" || u.category === "note" || u.id === BOOK)) }, notes);
  return { ...base, view: fought ? view : { ...view, fights: [] } };
}

export function rig(opts: { read?: string[]; notes?: string[]; lessons?: string[] } = {}) {
  const sent: Flat[] = [];
  const asked = { decided: 0, dry: 0 };
  const kept: Flat = { ...NEW_FLAT, lessons: opts.lessons ?? [...KEPT, JOURNAL, JOURNAL_NUMBERS], journal_read: opts.read ?? [] };
  const keeps = keepsOf(kept, sent);
  const screen = new Screen(catalog, () => { asked.decided += 1; }, () => { asked.dry += 1; return Promise.resolve(null); }, keeps);
  document.body.replaceChildren(screen.root);
  let at = 100;
  const show = (notes: string[]): void => { at += 10; screen.show(stepWith(notes, at)); };
  show(opts.notes ?? ALL);
  const q = <T extends HTMLElement = HTMLElement>(sel: string): T | null => screen.root.querySelector<T>(sel);
  const button = (): HTMLElement | null => q(".journal-open");
  const dotShows = (): boolean => { const d = button()?.querySelector(".new-dot"); return d !== null && d !== undefined && !(d as HTMLElement).hidden; };
  const sheet = (): HTMLElement => q(".journal-sheet")!;
  const actions = (): HTMLButtonElement[] => [...sheet().querySelectorAll<HTMLButtonElement>(".sheet-actions button")];
  const [close, prev, next] = [0, 1, 2].map((i) => () => actions()[i]!);
  const words = (): string[] => [...sheet().querySelectorAll<HTMLElement>(".journal-words")].map((n) => n.textContent ?? "");
  const numbers = (): HTMLElement => sheet().querySelector<HTMLElement>(".journal-numbers")!;
  return { screen, keeps, sent, asked, show, q, button, dotShows, sheet, close: close!, prev: prev!, next: next!, words, numbers };
}

