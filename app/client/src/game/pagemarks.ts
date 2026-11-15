// The marks on the journal's pages (docs/design/journal.md, "Marks on the page"; CONTRACT.txt, "JOURNAL"): a page's wear
// and its days' event marks, which art each draws and where. Pure: every draw is seeded by the save and the page or
// day, and a place is chosen against the boxes the page measured, so a page is marked the same each time it is drawn
// at one size, and no mark is kept over the words.
import type { JournalDay } from "../api/types";
import { seeded } from "./fights";
import type { Page } from "./journal";

export type MarkKind = JournalDay["marks"][number] | "wear";

/** One image of a kind, as /assets/journal/marks/manifest.json lists it (tools/pagemarks.py). */
export interface MarkArt { src: string; w: number; h: number }
export type MarkManifest = Partial<Record<MarkKind, MarkArt[]>>;

/** A box in the page's own pixels, its top left at (0, 0). */
export interface Box { x: number; y: number; w: number; h: number }

/** A mark the page asks for: its kind and the key every draw for it is seeded by. */
export interface Wanted { kind: MarkKind; key: string }

export interface Placed { kind: MarkKind; src: string; box: Box; flip: boolean; turn: boolean; opacity: number }

/** The most event marks one page carries, besides its wear. */
export const PAGE_EVENT_MARKS = 2;
/** Places tried for one mark before it is left off. */
export const TRIES = 80;
/** The share of a mark's box that is its soft, near-clear edge, left out of the test against the words. */
export const SOFT_EDGE = 0.12;
/** The room kept between a mark's box and the words, in pixels. */
export const CLEAR_PX = 4;
/** The share of a mark that may lie off the page's edge: an event mark may lie mostly off it, so on a full page it can
 * still come in from the edge. */
export const BLEED: Record<"wear" | "event", number> = { wear: 0.45, event: 0.6 };
/** A mark's longer side as a share of the page's width: [least, most]. */
const SIZE: Record<"wear" | "event", [number, number]> = { wear: [0.16, 0.3], event: [0.2, 0.38] };
const OPACITY: Record<"wear" | "event", [number, number]> = { wear: [0.3, 0.42], event: [0.7, 0.9] };

/** What `page` asks for: one wear mark, now and then two, keyed by the save and the page, then the marks of the days on
 * it, in day order, at most PAGE_EVENT_MARKS, each keyed by the save, its day and its kind. */
export function wantedOf(saveId: number, page: Page, days: readonly JournalDay[]): Wanted[] {
  const at = `marks|${saveId}|${page.id}`;
  const wear = seeded(`${at}|wear`)() < 0.7 ? 1 : 2;
  const wanted: Wanted[] = Array.from({ length: wear }, (_, i) => ({ kind: "wear", key: `${at}|wear|${i}` }));
  const onPage = new Set(page.notes.map((n) => n.day));
  const events = days.filter((d) => onPage.has(d.day))
    .flatMap((d) => d.marks.map((kind): Wanted => ({ kind, key: `marks|${saveId}|${d.day}|${kind}` })));
  return [...wanted, ...events.slice(0, PAGE_EVENT_MARKS)];
}

/** Each wanted mark at the first of its seeded places where its box, less its soft edge, crosses no blocked box (grown
 * by CLEAR_PX), its whole box crosses no mark already placed (so marks never pile into one corner), and at most its BLEED lies off the page; one with no such place among
 * TRIES, or with no art, is left off. */
export function placeMarks(wanted: readonly Wanted[], art: MarkManifest, page: { w: number; h: number },
                           blocked: readonly Box[]): Placed[] {
  const walls = blocked.map((b) => grow(b, CLEAR_PX));
  const placed: Placed[] = [];
  for (const want of wanted) {
    const options = art[want.kind] ?? [];
    if (options.length === 0 || page.w <= 0 || page.h <= 0) continue;
    const draw = seeded(want.key);
    const pick = options[Math.floor(draw() * options.length)]!;
    const tier = want.kind === "wear" ? "wear" : "event";
    const turn = draw() < 0.5;
    const flip = draw() < 0.5;
    const opacity = between(OPACITY[tier], draw());
    const long = between(SIZE[tier], draw()) * page.w;
    const [aw, ah] = turn ? [pick.h, pick.w] : [pick.w, pick.h];
    const scale = long / Math.max(aw, ah);
    const [w, h] = [aw * scale, ah * scale];
    for (let i = 0; i < TRIES; i++) {
      const off = BLEED[tier];
      const box = { x: -off * w + draw() * (page.w - (1 - 2 * off) * w), y: -off * h + draw() * (page.h - (1 - 2 * off) * h), w, h };
      const core = shrink(box, SOFT_EDGE);
      if (walls.some((b) => crosses(core, b)) || placed.some((p) => crosses(box, p.box))) continue;
      placed.push({ kind: want.kind, src: pick.src, box, flip, turn, opacity });
      break;
    }
  }
  return placed;
}

function between([lo, hi]: [number, number], r: number): number {
  return lo + (hi - lo) * r;
}

function grow(b: Box, by: number): Box {
  return { x: b.x - by, y: b.y - by, w: b.w + 2 * by, h: b.h + 2 * by };
}

function shrink(b: Box, share: number): Box {
  return { x: b.x + b.w * share, y: b.y + b.h * share, w: b.w * (1 - 2 * share), h: b.h * (1 - 2 * share) };
}

export function crosses(a: Box, b: Box): boolean {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}
