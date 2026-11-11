// The reminder window's slider (docs/design/reminders.md, "What the player sees"): two handles over the 24 hours,
// from and until, each labelled in 24-hour time with 12-hour time beneath. A start past the end wraps past midnight,
// and the shaded span shows it. Each handle is an ARIA slider: arrows move an hour, Page keys three, Home and End to
// the ends; a pointer or touch drags the nearer handle.
import { el } from "./dom";

export interface HourWindow {
  from: number;
  until: number;
}

const LAST = 23;

export function clock24(h: number): string {
  return `${String(h).padStart(2, "0")}:00`;
}

export function clock12(h: number): string {
  return `${h % 12 === 0 ? 12 : h % 12} ${h < 12 ? "AM" : "PM"}`;
}

/** The shaded spans as [start, end) hours over 0..24: one, or two when the window wraps past midnight. */
export function shaded(w: HourWindow): [number, number][] {
  if (w.from === w.until) return [[0, 24]];
  return w.from < w.until ? [[w.from, w.until]] : [[w.from, 24], [0, w.until]];
}

/** The hour a key moves a handle at `h` to, or null for a key the slider does not take. */
export function keyed(key: string, h: number): number | null {
  const step: Record<string, number> = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1, PageDown: -3, PageUp: 3 };
  if (key === "Home") return 0;
  if (key === "End") return LAST;
  const d = step[key];
  return d === undefined ? null : Math.max(0, Math.min(LAST, h + d));
}

type End = keyof HourWindow;

export class HourSlider {
  readonly root = el("div", "hour-slider");
  private readonly track = el("div", "hour-track");
  private readonly spans = [el("div", "hour-span"), el("div", "hour-span")];
  private readonly handles: Record<End, HTMLElement>;
  private readonly labels: Record<End, HTMLElement>;

  constructor(names: Record<End, string>, private w: HourWindow, private readonly changed: (w: HourWindow) => void) {
    this.track.append(...this.spans);
    this.handles = { from: this.handle(names.from, "from"), until: this.handle(names.until, "until") };
    this.labels = { from: el("div", "hour-label"), until: el("div", "hour-label") };
    const under = el("div", "hour-labels");
    under.append(this.labels.from, this.labels.until);
    this.root.append(this.track, under);
    this.track.addEventListener("pointerdown", (e) => this.grab(e));
    this.draw();
  }

  get window(): HourWindow {
    return { ...this.w };
  }

  set(w: HourWindow): void {
    this.w = { ...w };
    this.draw();
  }

  set disabled(off: boolean) {
    this.root.classList.toggle("off", off);
    for (const h of Object.values(this.handles)) {
      h.tabIndex = off ? -1 : 0;
      h.setAttribute("aria-disabled", String(off));
    }
  }

  private handle(name: string, end: End): HTMLElement {
    const h = el("div", `hour-handle hour-${end}`);
    h.setAttribute("role", "slider");
    h.setAttribute("aria-label", name);
    h.setAttribute("aria-valuemin", "0");
    h.setAttribute("aria-valuemax", String(LAST));
    h.tabIndex = 0;
    h.addEventListener("keydown", (e) => {
      const to = keyed(e.key, this.w[end]);
      if (to === null || this.root.classList.contains("off")) return;
      e.preventDefault();
      this.move(end, to);
    });
    this.track.append(h);
    return h;
  }

  private grab(e: PointerEvent): void {
    if (this.root.classList.contains("off")) return;
    e.preventDefault();
    const at = this.hourAt(e.clientX);
    const end: End = Math.abs(at - this.w.from) <= Math.abs(at - this.w.until) ? "from" : "until";
    this.handles[end].focus();
    this.track.setPointerCapture?.(e.pointerId);
    this.move(end, at);
    const drag = (m: PointerEvent) => this.move(end, this.hourAt(m.clientX));
    const done = () => {
      this.track.removeEventListener("pointermove", drag);
      this.track.removeEventListener("pointerup", done);
      this.track.removeEventListener("pointercancel", done);
    };
    this.track.addEventListener("pointermove", drag);
    this.track.addEventListener("pointerup", done);
    this.track.addEventListener("pointercancel", done);
  }

  private hourAt(x: number): number {
    const box = this.track.getBoundingClientRect();
    const share = box.width > 0 ? (x - box.left) / box.width : 0;
    return Math.max(0, Math.min(LAST, Math.round(share * 24)));
  }

  private move(end: End, h: number): void {
    if (this.w[end] === h) return;
    this.w = { ...this.w, [end]: h };
    this.draw();
    this.changed(this.window);
  }

  private draw(): void {
    const parts = shaded(this.w);
    this.spans.forEach((s, i) => {
      const part = parts[i];
      s.hidden = part === undefined;
      if (part) Object.assign(s.style, { left: `${(part[0] / 24) * 100}%`, width: `${((part[1] - part[0]) / 24) * 100}%` });
    });
    for (const end of ["from", "until"] as const) {
      const h = this.w[end];
      const node = this.handles[end];
      node.style.left = `${(h / 24) * 100}%`;
      node.setAttribute("aria-valuenow", String(h));
      node.setAttribute("aria-valuetext", `${clock24(h)} (${clock12(h)})`);
      this.labels[end].replaceChildren(el("span", "hour-24", clock24(h)), el("span", "hour-12", clock12(h)));
      this.labels[end].style.left = `${(h / 24) * 100}%`;
    }
  }
}
