// Where the scene's canvas sits inside a box that shows only part of the art, at a whole number of device pixels per
// art pixel (so the pixels stay square at any pixel ratio). Pure: the Scene hands it the box and gets a placement.

/** What part of the art shows: `focus` (art pixels) is held at `hold` (0 to 1 across the box). With a `window` (art
 * pixels) the scale makes that window fill the box's width; with `cover`, the scale is the smallest that covers the box,
 * unrounded (a phone's stage: the art across its width at any size); otherwise it is the smallest whole one that covers
 * the box and is at least MIN_SCALE. */
export interface Crop {
  focus: [number, number];
  hold: [number, number];
  window?: [number, number];
  cover?: true;
}

/** The canvas's CSS size and its offset in the box, in CSS px, and the scale in device pixels per art pixel. */
export interface Placed {
  scale: number;
  width: number;
  height: number;
  left: number;
  top: number;
}

const MIN_SCALE = 2;

/** A covered box: what the view shows (focus.ts) held at its middle. */
export const COVER: Pick<Crop, "hold" | "cover"> = { hold: [0.5, 0.5], cover: true };

export function place(box: [number, number], dpr: number, art: [number, number], crop: Crop): Placed {
  const [bw, bh] = [box[0] * dpr, box[1] * dpr];
  const scale = crop.cover ? Math.max(bw / art[0], bh / art[1])
    : crop.window ? Math.max(1, Math.floor(bw / crop.window[0]))
    : Math.max(MIN_SCALE, Math.ceil(Math.max(bw / art[0], bh / art[1])));
  const [cw, ch] = [art[0] * scale, art[1] * scale];
  const at = (room: number, size: number, hold: number, focus: number): number =>
    Math.round(Math.min(0, Math.max(room - size, room * hold - focus * scale)));
  return {
    scale, width: cw / dpr, height: ch / dpr,
    left: at(bw, cw, crop.hold[0], crop.focus[0]) / dpr,
    top: at(bh, ch, crop.hold[1], crop.focus[1]) / dpr,
  };
}
