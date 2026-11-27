// Where the world map's stamps and labels go on a sheet (contract/map.txt, "MAP"): the frame fitted to the cells shown, each
// stamp as large as it may be without crossing another (inside its own cell at worst, where none can cross), and each
// label at the first spot beside its place that crosses no stamp, no other label and not the sheet's edge. Pure: the page
// measures the labels and hands their sizes in.
import type { StampArt } from "./mapsheet";

export interface Box { x: number; y: number; w: number; h: number }
export interface Cell { east: number; north: number }

/** The fewest cells shown each way from the town. */
export const MIN_REACH = 2;
/** A cell's side at which a stamp is drawn at its base size. */
export const BASE_CELL = 72;
/** The most a stamp is scaled up from its base size. */
export const MAX_SCALE = 2.2;
/** The share of its cell a stamp's longer side takes where a neighbour's is near: the rest keeps the two apart. */
export const FILL = 0.9;
/** The most cells a stamp's longer side spans where it crosses no other stamp. */
export const ROOMY = 1.8;
/** The share of a cell a stamp drawn over another's takes along its longer side, and how far toward the cell's upper right
 * it sits, in cells: small, so it reads as a mark on the stamp beneath. */
export const OVER_SPAN = 0.55;
export const OVER_LIFT = 0.17;

/** A cell's side in pixels and the pixel centre of cell (0, 0), the town's. */
export interface Frame { cell: number; x0: number; y0: number }

/** The frame holding `cells` and the town with a cell of margin, at least MIN_REACH each way, centred on a sheet of
 * `w` by `h` and so widened along its longer side; a cell at most `maxCell`. */
export function frameOf(cells: readonly Cell[], w: number, h: number, maxCell: number): Frame {
  const east = cells.map((c) => c.east), north = cells.map((c) => c.north);
  const e0 = Math.min(-MIN_REACH, ...east.map((v) => v - 1)), e1 = Math.max(MIN_REACH, ...east.map((v) => v + 1));
  const n0 = Math.min(-MIN_REACH, ...north.map((v) => v - 1)), n1 = Math.max(MIN_REACH, ...north.map((v) => v + 1));
  const cell = Math.min(w / (e1 - e0 + 1), h / (n1 - n0 + 1), maxCell);
  return { cell, x0: w / 2 - ((e0 + e1) / 2) * cell, y0: h / 2 + ((n0 + n1) / 2) * cell };
}

/** A stamp to box: its art, its cell, and, for a stamp drawn on another's, that other's id (the one pair allowed to cross). */
export interface Stamped { art: StampArt; at: Cell; over?: string | null }

/** Each stamp's box, by id: at its roomy size where that crosses no other's box, else inside its cell; a stamp over another
 * is always the small box on its cell's upper right and crosses only the one it is over. Shrinking only ever turns a roomy
 * box into its cell's, so this ends, and two cell boxes never cross. */
export function stampBoxes(stamps: ReadonlyMap<string, Stamped>, f: Frame): Map<string, Box> {
  const boxes = new Map([...stamps].map(([id, s]) => [id, s.over ? overBox(s.art, s.at, f) : stampBox(s.art, s.at, f, ROOMY)]));
  const paired = (a: string, b: string): boolean => stamps.get(a)?.over === b || stamps.get(b)?.over === a;
  for (let changed = true; changed;) {
    changed = false;
    for (const [id, s] of stamps) {
      const box = boxes.get(id)!;
      if (s.over || ![...boxes].some(([other, b]) => other !== id && !paired(id, other) && crosses(box, b))) continue;
      const tight = stampBox(s.art, s.at, f, FILL);
      if (tight.w < box.w) { boxes.set(id, tight); changed = true; }
    }
  }
  return boxes;
}

/** The box of a stamp drawn over another: OVER_SPAN of a cell, lifted toward the cell's upper right. */
export function overBox(art: StampArt, at: Cell, f: Frame): Box {
  const b = stampBox(art, at, f, OVER_SPAN);
  return { ...b, x: b.x + OVER_LIFT * f.cell, y: b.y - OVER_LIFT * f.cell };
}

/** The box `art` is drawn in at `at`: its base size scaled with the cell (at most MAX_SCALE), its longer side at most
 * `span` cells, centred on the cell. */
export function stampBox(art: StampArt, at: Cell, f: Frame, span = FILL): Box {
  const k = Math.min(f.cell / BASE_CELL, MAX_SCALE, (span * f.cell) / Math.max(art.w, art.h));
  const w = art.w * k, h = art.h * k;
  return { x: f.x0 + at.east * f.cell - w / 2, y: f.y0 - at.north * f.cell - h / 2, w, h };
}

/** A label to place: whose it is, its stamp's box (what it sits beside), and its measured size. */
export interface Wanted { id: string; beside: Box; w: number; h: number }

export function crosses(a: Box, b: Box): boolean {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

function inside(a: Box, w: number, h: number): boolean {
  return a.x >= 0 && a.y >= 0 && a.x + a.w <= w && a.y + a.h <= h;
}

/** The spots tried for a label beside `b`, in order: right, left, below, above, at each of `gaps` out from it. */
function spots(b: Box, w: number, h: number, gaps: readonly number[]): Box[] {
  const cx = b.x + b.w / 2, cy = b.y + b.h / 2;
  return gaps.flatMap((d) => [
    { x: b.x + b.w + d, y: cy - h / 2, w, h }, { x: b.x - d - w, y: cy - h / 2, w, h },
    { x: cx - w / 2, y: b.y + b.h + d, w, h }, { x: cx - w / 2, y: b.y - d - h, w, h },
  ]);
}

/** Each wanted label's box, in order, or null where no spot is clear: none crosses a box of `stamps`, an earlier label or
 * the sheet's edge (`w` by `h`). */
export function placeLabels(wanted: readonly Wanted[], stamps: readonly Box[], w: number, h: number,
  gaps: readonly number[]): Map<string, Box | null> {
  const placed: Box[] = [];
  const out = new Map<string, Box | null>();
  for (const l of wanted) {
    const spot = spots(l.beside, l.w, l.h, gaps).find((s) => inside(s, w, h) && !stamps.some((b) => crosses(s, b)) && !placed.some((b) => crosses(s, b)));
    if (spot) placed.push(spot);
    out.set(l.id, spot ?? null);
  }
  return out;
}
