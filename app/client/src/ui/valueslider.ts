// One value on a track: a pointer or touch drag sets it, the arrow keys step it, Home and End go to the ends. The value
// snaps to `step` from `min`. A rule's level uses it (condlevels.ts); a split of 100% across parts is sharebar.ts's.
import { el } from "./dom";

export interface SliderRange {
  min: number;
  max: number;
  step: number;
}

/** `v` snapped to the range's steps and held inside it. */
export function snap(range: SliderRange, v: number): number {
  const n = Math.round((v - range.min) / range.step);
  return Math.max(range.min, Math.min(range.max, range.min + n * range.step));
}

/** The value a key moves `v` to, or null for a key the slider does not take; Page keys move a tenth of the range. */
export function keyed(range: SliderRange, key: string, v: number): number | null {
  const page = Math.max(range.step, snap(range, (range.max - range.min) / 10 + range.min) - range.min);
  const move: Record<string, number> = { ArrowLeft: -range.step, ArrowDown: -range.step, ArrowRight: range.step, ArrowUp: range.step, PageDown: -page, PageUp: page };
  if (key === "Home") return range.min;
  if (key === "End") return range.max;
  const d = move[key];
  return d === undefined ? null : snap(range, v + d);
}

export class ValueSlider {
  readonly root = el("div", "value-slider");
  private readonly fill = el("div", "value-fill");
  private readonly handle = el("div", "value-handle");
  private range: SliderRange = { min: 0, max: 1, step: 1 };
  private at = 0;
  private ok: (v: number) => boolean = () => true;

  /** `picked` gets each new value a drag or key lands on. */
  constructor(label: string, private readonly picked: (v: number) => void) {
    const track = el("div", "value-track");
    this.handle.setAttribute("role", "slider");
    this.handle.setAttribute("aria-label", label);
    this.handle.tabIndex = 0;
    track.append(this.fill, this.handle);
    this.root.append(track);
    this.handle.addEventListener("keydown", (e) => {
      const to = keyed(this.range, e.key, this.at);
      if (to === null) return;
      e.preventDefault();
      this.move(to);
    });
    track.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      this.handle.focus();
      track.setPointerCapture?.(e.pointerId);
      this.move(this.valueAt(track, e.clientX));
      const drag = (m: PointerEvent) => this.move(this.valueAt(track, m.clientX));
      const done = () => {
        track.removeEventListener("pointermove", drag);
        track.removeEventListener("pointerup", done);
        track.removeEventListener("pointercancel", done);
      };
      track.addEventListener("pointermove", drag);
      track.addEventListener("pointerup", done);
      track.addEventListener("pointercancel", done);
    });
  }

  /** Shows `value` in `range`, read aloud as `text`; `can` says which values a drag or key may land on. */
  draw(range: SliderRange, value: number, text: string, can: (v: number) => boolean): void {
    this.range = range;
    this.at = value;
    this.ok = can;
    const share = range.max > range.min ? (value - range.min) / (range.max - range.min) : 0;
    this.handle.style.left = this.fill.style.width = `${share * 100}%`;
    this.handle.setAttribute("aria-valuemin", String(range.min));
    this.handle.setAttribute("aria-valuemax", String(range.max));
    this.handle.setAttribute("aria-valuenow", String(value));
    this.handle.setAttribute("aria-valuetext", text);
  }

  private valueAt(track: HTMLElement, x: number): number {
    const box = track.getBoundingClientRect();
    const share = box.width > 0 ? (x - box.left) / box.width : 0;
    return snap(this.range, this.range.min + share * (this.range.max - this.range.min));
  }

  private move(v: number): void {
    if (v === this.at || !this.ok(v)) return;
    this.picked(v);
  }
}
