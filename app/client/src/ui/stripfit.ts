// How many of the story strip's newest lines fit whole in its room (ui/story.ts).
/** A line's top and bottom edge, in the same units as the room's height. */
export interface Span { top: number; bottom: number }

const SLACK = 0.5;   // sub-pixel layout rounding

/** The most newest lines (spans oldest first, stacked in flow) whose run from the oldest's top to the newest's bottom
 * fits `room`, and at least one: the newest always shows, and a room not laid out (height 0) holds just that. */
export function fitting(spans: Span[], room: number): number {
  const last = spans.at(-1);
  if (!last || room <= 0) return Math.min(1, spans.length);
  let n = 1;
  while (n < spans.length && last.bottom - (spans[spans.length - 1 - n] as Span).top <= room + SLACK) n++;
  return n;
}
