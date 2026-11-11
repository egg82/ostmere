// FIXTURE, never shipped: the journal's shapes (CONTRACT.txt, "JOURNAL") with placeholder ids and words, on the fights
// fixture (the shipped game has no entries yet). The sketches are placeholders too: assets/journal/*.png, ink on
// transparent, which a screenshot run serves at /assets/journal/ (the real ones come from docs/research/sketch-test).
//   journal:       the book on, combat on, two entries written. The first (creatures) has three notes (one pencil with
//                  a drawing beside it) and names the fight card, fought 4 times; the second (places) has one pencil
//                  note and names the standing fight, never fought. All four notes are unread.
//   More pages, written when `journalView` is handed their notes: PAGE_C (a second creatures page, no numbers) and
//   PAGE_D (a days page with no sketch and no numbers, two notes). Content order is B, A, C, D, so page order
//   (days, creatures, places) is D, A, C, B.
//   journallesson: the same, with the journal's lesson still to run.
//   journaldays:   the book with one days page written (no sketch, no numbers).
//   journalall:    every page written: days, two creatures pages and a places page.
import type { Content, Step, View } from "../src/api/types";
import { fightsStep } from "./fights";
import type { Kept } from "./steps";

export type JournalPhase = "journal" | "journallesson" | "journaldays" | "journalall";
export const JOURNAL_PHASES: readonly JournalPhase[] = ["journal", "journallesson", "journaldays", "journalall"];

export function isJournal(phase: string): phase is JournalPhase {
  return (JOURNAL_PHASES as readonly string[]).includes(phase);
}

export const BOOK = "book";
export const PAGE_A = "page_a";
export const PAGE_B = "page_b";
export const NOTES_A = ["note_a1", "note_a2", "note_a3"];
export const NOTE_B = "note_b1";
export const PAGE_C = "page_c";
export const PAGE_D = "page_d";
export const NOTE_C = "note_c1";
export const NOTES_D = ["note_d1", "note_d2"];

const WORDS: Record<string, string> = {
  "feature.book": "Journal",
  note_a1: "Seen at the water just after dusk. Quick, and it does not like noise.",
  note_a2: "Might be hurt on the left side. Not sure yet.",
  note_a3: "Leaves the stores alone when the fire is high.",
  note_b1: "Only ever heard, never seen. Count the nights it comes.",
  note_c1: "Smaller than the first, and shyer.",
  note_d1: "The first night was the long one.",
  note_d2: "We kept the fire up until it was light.",
};

/** The fixture content with the book (a feature with a label) and a journal of two entries. */
export function withJournal(content: Content): Content {
  return {
    ...content,
    feature_infos: [...content.feature_infos, { feature: BOOK, hint_key: null, label_key: "feature.book", feature_card: null }],
    text_entries: [...content.text_entries, ...Object.entries(WORDS).map(([key, text]) => ({ key, text }))],
    journal: {
      feature: BOOK,
      entries: [
        { entry: PAGE_B, section: "places", sketch: "sketch_b", runners: ["raiders"], notes: [{ note: NOTE_B, hand: "pencil", sketch: null }] },
        { entry: PAGE_A, section: "creatures", sketch: "sketch_a", runners: ["hunt"], notes: [
          { note: "note_a1", hand: "ink", sketch: null }, { note: "note_a2", hand: "pencil", sketch: "note_sketch" }, { note: "note_a3", hand: "ink", sketch: null }] },
        { entry: PAGE_C, section: "creatures", sketch: "sketch_c", runners: [], notes: [{ note: NOTE_C, hand: "ink", sketch: null }] },
        { entry: PAGE_D, section: "days", sketch: null, runners: [], notes: NOTES_D.map((note) => ({ note, hand: "ink" as const, sketch: null })) },
      ],
    },
  };
}

/** The view with the journal written: the book on, entries and notes unlocked (`notes` of them; an entry with one of its notes). */
export function journalView(base: View, notes: string[] = [...NOTES_A, NOTE_B]): View {
  const holds = (page: string[]): boolean => notes.some((n) => page.includes(n));
  const entries = [[PAGE_A, NOTES_A], [PAGE_B, [NOTE_B]], [PAGE_C, [NOTE_C]], [PAGE_D, NOTES_D]].flatMap(([id, page]) => (holds(page as string[]) ? [id as string] : []));
  return {
    ...base,
    fights: base.fights.map((f) => (f.runner === "raiders" ? { ...f, fought: 0, lost: 0 } : f)),
    unlocked: [...base.unlocked, { category: "feature", id: BOOK },
      ...entries.map((id) => ({ category: "entry" as const, id })), ...notes.map((id) => ({ category: "note" as const, id }))],
  };
}

export function journalStep(phase: JournalPhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fightsStep("fight", at, kept, decisions);
  const notes = phase === "journaldays" ? NOTES_D : phase === "journalall" ? [...NOTES_D, ...NOTES_A, NOTE_C, NOTE_B] : undefined;
  return { ...base, view: journalView(base.view, notes) };
}
