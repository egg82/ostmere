// FIXTURE, never shipped: the journal's shapes (CONTRACT.txt, "JOURNAL") with placeholder ids and words, on the fights
// fixture (the shipped game has no entries yet). The sketches are placeholders too: assets/journal/*.png, ink on
// transparent, which a screenshot run serves at /assets/journal/ (the real ones come from docs/research/sketch-test).
//   journal:       the book on, combat on, two entries written. The first (creatures) has three notes (one pencil with
//                  a drawing beside it) and names the fight card, fought 4 times; the second (places) has one pencil
//                  note and names the standing fight, never fought. All four notes are unread.
//   More pages, written when `journalView` is handed their notes: PAGE_C (a second creatures page, no numbers). Content
//   order is B, A, C, so page order (days, creatures, places) is the days pages, A, C, B.
//   DAY_D: a written day (game day 0) of two notes, the step's journal_days on the phases below that have days.
//   journallesson: the same as journal, with the journal's lesson still to run.
//   journaldays:   the book with one written day: one days page.
//   journalall:    every page written: one days page, two creatures pages and a places page.
//   journalweeks:  WEEKS' written days and nothing else: several days pages, the newest day turned to READ_TO. Its
//                  days are a short day, days that fill a page and break, a long gap then a day of catch-up notes, a
//                  late addition, and a misremembering whose correction is pages later.
//   journaltoday:  WEEKS' days 0 to 4, then day 5 still being written: its first note so far (TODAY), turned to day 4.
import type { Content, JournalDay, Step, View } from "../src/api/types";
import { fightsStep } from "./fights";
import type { Kept } from "./steps";

//   journalbook:   a synthetic long book, far past anything shipped: LONG_DAYS days of placeholder notes (many days pages),
//                  LONG_CREATURES creatures pages and LONG_PLACES places pages, some read: for the contents and the turns at length.
export type JournalPhase = "journal" | "journallesson" | "journaldays" | "journalall" | "journalweeks" | "journaltoday" | "journalbook";
export const JOURNAL_PHASES: readonly JournalPhase[] = ["journal", "journallesson", "journaldays", "journalall", "journalweeks", "journaltoday", "journalbook"];

export function isJournal(phase: string): phase is JournalPhase {
  return (JOURNAL_PHASES as readonly string[]).includes(phase);
}

export const BOOK = "book";
export const PAGE_A = "page_a";
export const PAGE_B = "page_b";
export const NOTES_A = ["note_a1", "note_a2", "note_a3"];
export const NOTE_B = "note_b1";
export const PAGE_C = "page_c";
export const NOTE_C = "note_c1";
export const NOTES_D = ["note_d1", "note_d2"];
export const DAY_D: JournalDay = { day: 0, day_notes: NOTES_D.map((key) => ({ subject: "s_first_night", slot: "first" as const, key, hand: "ink" as const, sketch: null, count: null })), marks: [] };

/** Placeholder words for WEEKS, in a diarist's voice (never shipped). */
const WEEK_WORDS: Record<string, string> = {
  rain: "Rain all day. Stayed in.",
  roof: "Patched the roof over the north end with the last of the bark. It held through the night, mostly.",
  roof2: "The roof again.",
  well: "Found the old well past the birches. The water is cold and tastes of iron, but it is water and it is close.",
  well2: "The well is good.",
  fox: "A fox at the edge of the clearing at dusk. It watched the fire a long while before it went.",
  fox_late: "Forgot to say: the fox had a white tip to its tail.",
  count: "Counted the sacks in the store. Eleven, I think, and one half gone to damp.",
  count_fix: "It was nine sacks, not eleven. I counted twice in the light.",
  sick: "The cough is worse. Kept the fire high and slept by it.",
  better: "Woke without the cough for the first time.",
  catch_roof: "The roof came down in the wind and we put it up again.",
  catch_well: "Lost the bucket down the well. Made another.",
  catch_fox: "The fox took two of the hens.",
  walk: "Walked the whole ridge to the far stones and back before dark, and saw nobody the whole way, not even smoke.",
  frost: "First frost. The ground rang under the axe.",
  gone: "couldn't find the word for it.",
};

const WORDS: Record<string, string> = {
  "feature.book": "Journal",
  note_a1: "Seen at the water just after dusk. Quick, and it does not like noise.",
  note_a2: "Might be hurt on the left side. Not sure yet.",
  note_a3: "Leaves the stores alone when the fire is high.",
  note_b1: "Only ever heard, never seen. Count the nights it comes.",
  note_c1: "Smaller than the first, and shyer.",
  note_d1: "The first night was the long one.",
  note_d2: "We kept the fire up until it was light.",
  ...Object.fromEntries(Object.entries(WEEK_WORDS).map(([k, t]) => [`wk_${k}`, t])),
};

/** The fixture content with the book (a feature with a label) and a journal of two entries. */
export function withJournal(content: Content): Content {
  return {
    ...content,
    feature_infos: [...content.feature_infos, { feature: BOOK, hint_key: null, label_key: "feature.book", effect_key: null, change_bp: [], feature_card: null }],
    text_entries: [...content.text_entries, ...Object.entries(WORDS).map(([key, text]) => ({ key, text }))],
    journal: {
      feature: BOOK,
      entries: [
        { entry: PAGE_B, section: "places", sketch: "sketch_b", runners: ["raiders"], notes: [{ note: NOTE_B, hand: "pencil", sketch: null }] },
        { entry: PAGE_A, section: "creatures", sketch: "sketch_a", runners: ["hunt"], notes: [
          { note: "note_a1", hand: "ink", sketch: null }, { note: "note_a2", hand: "pencil", sketch: "note_sketch" }, { note: "note_a3", hand: "ink", sketch: null }] },
        { entry: PAGE_C, section: "creatures", sketch: "sketch_c", runners: [], notes: [{ note: NOTE_C, hand: "ink", sketch: null }] },
      ],
    },
  };
}

/** The view with the journal written: the book on, entries and notes unlocked (`notes` of them; an entry with one of its notes). */
export function journalView(base: View, notes: string[] = [...NOTES_A, NOTE_B]): View {
  const holds = (page: string[]): boolean => notes.some((n) => page.includes(n));
  const entries = [[PAGE_A, NOTES_A], [PAGE_B, [NOTE_B]], [PAGE_C, [NOTE_C]]].flatMap(([id, page]) => (holds(page as string[]) ? [id as string] : []));
  return {
    ...base,
    fights: base.fights.map((f) => (f.runner === "raiders" ? { ...f, fought: 0, lost: 0 } : f)),
    unlocked: [...base.unlocked, { category: "feature", id: BOOK },
      ...entries.map((id) => ({ category: "entry" as const, id })), ...notes.map((id) => ({ category: "note" as const, id }))],
  };
}

export function journalStep(phase: JournalPhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fightsStep("fight", at, kept, decisions);
  if (phase === "journalbook") return { ...base, view: longView(journalView(base.view, [])), journal_days: LONG_DAYS };
  const notes = phase === "journaldays" || phase === "journalweeks" || phase === "journaltoday" ? [] : phase === "journalall" ? [...NOTES_A, NOTE_C, NOTE_B] : undefined;
  const days = phase === "journalweeks" ? WEEKS : phase === "journaltoday" ? [...WEEKS.slice(0, 5), TODAY] : phase === "journaldays" || phase === "journalall" ? [DAY_D] : [];
  return { ...base, view: journalView(base.view, notes), journal_days: days };
}

/** journalweeks' newest day turned to: the days after it are unread. */
export const READ_TO = 4;


const note = (key: string, slot: JournalDay["day_notes"][number]["slot"] = "first", hand: "ink" | "pencil" = "ink", sketch: string | null = null) =>
  ({ subject: `s_${key}`, slot, key: `wk_${key}`, hand, sketch, count: null });

/** Days 0 to 15 with gaps: a short day (1), days that fill the first page, a late addition (day 6 for day 5), a
 * misremembering (day 7) corrected on day 14, a gap from day 9 to 12 caught up on day 13; a loss note and a fold of
 * three (day 16, LOSS LINES); every kind of mark on some day. */
export const WEEKS: JournalDay[] = [
  { day: 0, day_notes: [note("roof"), note("well", "first", "ink", "note_sketch")], marks: ["mud"] },
  { day: 1, day_notes: [note("rain")], marks: ["water"] },
  { day: 2, day_notes: [note("roof2", "repeat"), note("well2", "repeat", "pencil")], marks: [] },
  { day: 3, day_notes: [note("walk")], marks: ["mud"] },
  { day: 4, day_notes: [note("sick")], marks: ["blood"] },
  { day: 5, day_notes: [note("fox"), note("better")], marks: ["blood", "mud"] },
  { day: 6, day_notes: [note("fox_late", "late", "pencil")], marks: [] },
  { day: 7, day_notes: [note("count", "misremember")], marks: [] },
  { day: 8, day_notes: [note("walk", "repeat"), note("rain", "repeat")], marks: ["soot"] },
  { day: 13, day_notes: [note("catch_roof", "catchup"), note("catch_well", "catchup"), note("catch_fox", "catchup"), note("frost")], marks: ["smudge"] },
  { day: 14, day_notes: [note("count_fix", "correction", "pencil")], marks: [] },
  { day: 15, day_notes: [note("rain", "repeat")], marks: ["soot"] },
  { day: 16, day_notes: [note("walk", "repeat"), note("gone", "loss", "pencil"),
    { subject: "hunt", slot: "fold", key: "ui.journal.fold", hand: "pencil", sketch: null, count: 3 }], marks: [] },
];

/** journaltoday's day still being written: WEEKS' day 5 with its first note so far. */
export const TODAY: JournalDay = { ...WEEKS[5]!, day_notes: WEEKS[5]!.day_notes.slice(0, 1), marks: ["blood"] };

export const LONG_DAYS_N = 90;
export const LONG_CREATURES = 18;
export const LONG_PLACES = 13;
const SEEN = ["by the water", "past the birches", "under the ridge", "at the far stones", "near the old wall", "in the long grass"];
const ENTRY_SECTIONS = [["creatures", LONG_CREATURES], ["places", LONG_PLACES]] as const;
const longId = (section: string, i: number): string => `long_${section}_${i}`;
const longNotes = (section: string, i: number): string[] => [`${longId(section, i)}_n0`, `${longId(section, i)}_n1`];

/** The synthetic long book's days: three placeholder notes of about a sentence each for every day (never shipped). */
export const LONG_DAYS: JournalDay[] = Array.from({ length: LONG_DAYS_N }, (_, d) => ({
  day: d, marks: [],
  day_notes: [0, 1, 2].map((n) => ({ subject: `s_long_${d}_${n}`, slot: "first" as const, key: `long_day_${d}_${n}`, hand: n === 1 ? "pencil" as const : "ink" as const, sketch: null, count: null })),
}));

/** The account's book notes read in journalbook: the first two thirds of each section's pages. */
export const LONG_READ: string[] = ENTRY_SECTIONS.flatMap(([section, n]) =>
  Array.from({ length: Math.floor(n * 2 / 3) }, (_, i) => longNotes(section, i)).flat());

/** The newest day turned to in journalbook: the last third of the days are unread. */
export const LONG_READ_TO = Math.floor(LONG_DAYS_N * 2 / 3);

/** The content with the synthetic long book's entries and words, beside withJournal's. */
export function withLongBook(content: Content): Content {
  const entries = ENTRY_SECTIONS.flatMap(([section, n]) => Array.from({ length: n }, (_, i) => ({
    entry: longId(section, i), section, sketch: null, runners: [],
    notes: longNotes(section, i).map((note, k) => ({ note, hand: k === 1 ? "pencil" as const : "ink" as const, sketch: null })) })));
  const words = [
    ...ENTRY_SECTIONS.flatMap(([section, n]) => Array.from({ length: n }, (_, i) => longNotes(section, i).map((key, k) =>
      ({ key, text: k === 0 ? `Placeholder ${section} page ${i + 1}, ${SEEN[i % SEEN.length]}.` : `A second placeholder note on page ${i + 1}.` }))).flat()),
    ...LONG_DAYS.flatMap((d) => d.day_notes.map((n) => ({ key: n.key, text: `Placeholder note for day ${d.day + 1}, written ${SEEN[d.day % SEEN.length]} and long enough to take a row or two of the page.` }))),
  ];
  const base = content.journal!;
  return { ...content, text_entries: [...content.text_entries, ...words], journal: { ...base, entries: [...base.entries, ...entries] } };
}

/** `view` with the long book's entries and notes unlocked. */
function longView(view: View): View {
  const unlocked = ENTRY_SECTIONS.flatMap(([section, n]) => Array.from({ length: n }, (_, i) =>
    [{ category: "entry" as const, id: longId(section, i) }, ...longNotes(section, i).map((id) => ({ category: "note" as const, id }))]).flat());
  return { ...view, unlocked: [...view.unlocked, ...unlocked] };
}
