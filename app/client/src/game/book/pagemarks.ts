// The marks on the journal's pages (docs/design/journal.md, "Marks on the page"; contract/journal.txt, "JOURNAL"): a page's wear
// and its days' event marks, which art each draws and where. Pure: every draw is seeded by the save and the page or
// day, and a place is chosen against the boxes the page measured, so a page is marked the same each time it is drawn
// at one size, and no mark is kept over the words.
import type { JournalDay } from "../../api/types";
import { seeded } from "../ledger/fights";
import type { Page } from "./journal";

export type MarkKind = JournalDay["marks"][number] | "wear";

/** One image of a kind, as /assets/journal/marks/manifest.json lists it (tools/pagemarks.py). */
export interface MarkArt { src: string; w: number; h: number }
export type MarkManifest = Partial<Record<MarkKind, MarkArt[]>>;

/** A box in the page's own pixels, its top left at (0, 0). */
export interface Box { x: number; y: number; w: number; h: number }

/** A mark the page asks for: its kind and the key every draw for it is seeded by. */
export interface Wanted { kind: MarkKind; key: string }

/** A mark as drawn: its art turned by `angle` degrees about its centre, mirrored on either axis, scaled, at `opacity`.
 * `box` is the bounding box of the art as drawn, in the page's pixels; the art's own unturned size is `w` by `h`,
 * centred in it. */
export interface Placed { kind: MarkKind; src: string; box: Box; w: number; h: number; angle: number; flipX: boolean;
                          flipY: boolean; scale: number; opacity: number }

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
/** A mark's scale about its own size: [least, most]. */
const SCALE: [number, number] = [0.85, 1.2];
/** A second copy of one art on a page (only once every art of its kind is on it) lies at least this share of the page's
 * diagonal from the first, and is turned at least this far from it, as well as mirrored on one axis. */
export const REPEAT_APART = 0.4;
export const REPEAT_TURN = 90;
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
 * TRIES, or with no art, is left off. Each mark is turned (any angle), mirrored and scaled by its own seeded draw. An art
 * already on the page is not drawn again while one of its kind is not; when it must be, the copy is mirrored and turned
 * differently and lies far from the first. */
export function placeMarks(wanted: readonly Wanted[], art: MarkManifest, page: { w: number; h: number },
                           blocked: readonly Box[]): Placed[] {
  const walls = blocked.map((b) => grow(b, CLEAR_PX));
  const placed: Placed[] = [];
  for (const want of wanted) {
    const all = art[want.kind] ?? [];
    if (all.length === 0 || page.w <= 0 || page.h <= 0) continue;
    const draw = seeded(want.key);
    const fresh = all.filter((a) => !placed.some((p) => p.src === a.src));
    const options = fresh.length > 0 ? fresh : all;
    const pick = options[Math.floor(draw() * options.length)]!;
    const first = fresh.length > 0 ? undefined : placed.find((p) => p.src === pick.src);
    const tier = want.kind === "wear" ? "wear" : "event";
    const look = lookOf(draw, tier, pick, page.w, first);
    for (let i = 0; i < TRIES; i++) {
      const off = BLEED[tier];
      const [w, h] = [look.box.w, look.box.h];
      const box = { x: -off * w + draw() * (page.w - (1 - 2 * off) * w), y: -off * h + draw() * (page.h - (1 - 2 * off) * h), w, h };
      const core = shrink(box, SOFT_EDGE);
      if (walls.some((b) => crosses(core, b)) || placed.some((p) => crosses(box, p.box))) continue;
      if (first !== undefined && distance(box, first.box) < REPEAT_APART * Math.hypot(page.w, page.h)) continue;
      placed.push({ ...look, kind: want.kind, src: pick.src, box });
      break;
    }
  }
  return placed;
}

/** One mark's seeded transform and the size of its bounding box (its place is the caller's). A repeat of `first` is
 * turned REPEAT_TURN or more from it and mirrored on the x axis against it. */
function lookOf(draw: () => number, tier: "wear" | "event", pick: MarkArt, pageW: number, first: Placed | undefined):
  Omit<Placed, "kind" | "src" | "box"> & { box: Box } {
  let angle = draw() * 360 - 180;
  let flipX = draw() < 0.5;
  const flipY = draw() < 0.5;
  if (first !== undefined) {
    angle = first.angle + REPEAT_TURN + draw() * (360 - 2 * REPEAT_TURN);
    flipX = !first.flipX;
  }
  angle = ((angle + 180) % 360 + 360) % 360 - 180;
  const opacity = between(OPACITY[tier], draw());
  const scale = between(SCALE, draw());
  const unit = between(SIZE[tier], draw()) * pageW / Math.max(pick.w, pick.h);
  const [w, h] = [pick.w * unit, pick.h * unit];
  const rad = (angle * Math.PI) / 180;
  const [c, s] = [Math.abs(Math.cos(rad)), Math.abs(Math.sin(rad))];
  const box = { x: 0, y: 0, w: (w * c + h * s) * scale, h: (w * s + h * c) * scale };
  return { box, w, h, angle, flipX, flipY, scale, opacity };
}

function distance(a: Box, b: Box): number {
  return Math.hypot(a.x + a.w / 2 - b.x - b.w / 2, a.y + a.h / 2 - b.y - b.h / 2);
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
