// Where the lesson's note stands (ui/lessons/lessons.ts, place): the geometry, apart from the page.
export interface Spot { left: number; top: number }
type Box = Pick<DOMRect, "left" | "top" | "right" | "bottom" | "width" | "height">;

export interface Surroundings {
  target: Box;
  /** The card the target sits in, when it does. */
  card: Box | undefined;
  /** The note's own size and the window's. */
  w: number; h: number; vw: number; vh: number;
  /** What the note must not hide (the control's siblings, the tabs, names), and the controls the player can tap. */
  covered: Box[];
  taps: Box[];
}

const GAP_PX = 8;
const GUTTER_PX = 16;

  /** The note under its control; else beside it (left, then right); else above it: the first of those inside the
   * window's gutters that covers no sibling of the control, not the card it sits in (then above or below that card), not the panel's tabs,
   * not the next step's control when it is already on show, and no control the player can tap. When every one of those covers
   * a control (a short window under an open editor), the note docks at a corner of the window (top or bottom, at the control's left,
   * the left gutter or the right one): the nearest that covers none and not its own control. With none clear, the one that takes
   * fewest taps, then covers least. */
export function pickSpot({ target: r, card, w, h, vw, vh, covered, taps }: Surroundings): Spot {
  const across = Math.max(GUTTER_PX, Math.min(r.left, vw - w - GUTTER_PX));
  const middle = r.top + (r.height - h) / 2;
  const spots: Spot[] = [
    { left: across, top: r.bottom + GAP_PX },
    { left: r.left - GAP_PX - w, top: middle },
    { left: r.right + GAP_PX, top: middle },
    { left: across, top: r.top - GAP_PX - h },
  ];
  if (card) spots.push({ left: across, top: card.bottom + GAP_PX }, { left: across, top: card.top - GAP_PX - h });
  const fits = (s: Spot): boolean => s.left >= GUTTER_PX && s.left + w <= vw - GUTTER_PX && s.top >= 0 && s.top + h <= vh;
  const meets = (s: Spot, c: Box): boolean => Math.min(s.left + w, c.right) > Math.max(s.left, c.left) && Math.min(s.top + h, c.bottom) > Math.max(s.top, c.top);
  const hidden = (s: Spot): number => covered.reduce((sum, c) => sum + Math.max(0, Math.min(s.left + w, c.right) - Math.max(s.left, c.left)) * Math.max(0, Math.min(s.top + h, c.bottom) - Math.max(s.top, c.top)), 0);
  const pressed = (s: Spot): number => taps.filter((c) => meets(s, c)).length;   // taps the note would take from the player
  const clear = (s: Spot): boolean => hidden(s) === 0 && pressed(s) === 0;
  const room = spots.filter(fits);
  const corners: Spot[] = [across, GUTTER_PX, vw - w - GUTTER_PX].flatMap((left) => [{ left, top: GAP_PX }, { left, top: vh - GAP_PX - h }]);
  const away = (s: Spot): number => Math.hypot(s.left + w / 2 - r.left - r.width / 2, s.top + h / 2 - r.top - r.height / 2);
  const docks = corners.filter((s) => fits(s) && !meets(s, r)).sort((a, b) => away(a) - away(b));
  return room.find(clear) ?? (room.every((s) => pressed(s) > 0) ? docks.find(clear) : undefined) ?? room.find((s) => hidden(s) === 0)
    ?? room.sort((a, b) => pressed(a) - pressed(b) || hidden(a) - hidden(b))[0] ?? { left: across, top: Math.max(GUTTER_PX, r.top - GAP_PX - h) };
}
