// A mix drawn as one bar split into its shares, with a legend beneath it naming each segment and its share: no text sits
// inside the bar. Used by the hands strip (slim) and the mix editor (large). Dividers drag share between their two neighbours, snapping to whole percents and
// never below MIN_SHARE_BP, so no divider ever reaches 0%; in the editor a segment dragged off the bar is removed.
// The bar only reports what the player did; the owner decides what to send.
import { MIN_SHARE_BP } from "../game/mix";
import { el, pulse, setText, tapFeedback } from "./dom";

const SNAP_BP = 100;
const OFF_PX = 40;   // a segment dragged this far off the bar's line leaves the mix

export interface SegmentSpec {
  key: string;
  label: string;
  hue: number;
  /** Struck through: a retired or completed card the mix still holds. */
  struck?: boolean;
}

export interface ShareBarHooks {
  /** Shares as they move, before letting go (the editor's live totals). */
  moving?(shares: number[], divider: number): void;
  /** Let go after a change. */
  commit(shares: number[]): void;
  /** A segment dragged off the bar (editor only). */
  remove?(index: number): void;
}

export class ShareBar {
  readonly root: HTMLElement;
  private readonly bar = el("div", "share-track");
  private readonly key = el("div", "share-key");
  private specs: SegmentSpec[] = [];
  private local: number[] = [];
  private segs: { seg: HTMLElement; name: HTMLElement; pct: HTMLElement }[] = [];
  private dividers: HTMLElement[] = [];
  private shape = "";

  constructor(className: string, private readonly bp: number, private readonly format: (bp: number) => string, private readonly hooks: ShareBarHooks) {
    this.root = el("div", `share-bar ${className}`);
    this.root.append(this.bar, this.key);
  }

  get shares(): number[] {
    return [...this.local];
  }

  set(specs: SegmentSpec[], shares: number[]): void {
    const shape = specs.map((s) => `${s.key}:${s.struck ? 1 : 0}:${s.label}`).join("|");
    this.specs = specs;
    if (shape !== this.shape) this.build(specs);
    this.shape = shape;
    this.local = [...shares];
    this.layout();
  }

  private build(specs: SegmentSpec[]): void {
    this.bar.replaceChildren();
    this.key.replaceChildren();
    this.segs = specs.map((s, i) => {
      const seg = el("div", `share-seg hue-${s.hue % 6}`);
      const item = el("span", `share-key-item hue-${s.hue % 6}`);
      for (const n of [seg, item]) n.classList.toggle("struck", s.struck === true);
      const name = el("span", "share-name");
      const pct = el("b", "share-pct");
      item.append(name, " ", pct);
      if (this.hooks.remove) seg.addEventListener("pointerdown", (e) => this.dragOff(e, i, seg));
      this.bar.append(seg);
      this.key.append(item);
      return { seg, name, pct };
    });
    this.dividers = specs.slice(1).map((_, i) => this.divider(i));
    this.bar.append(...this.dividers);
  }

  private layout(): void {
    let left = 0;
    this.local.forEach((share, i) => {
      const seg = this.segs[i];
      if (seg) {
        seg.seg.style.left = `${(left / this.bp) * 100}%`;
        seg.seg.style.width = `${(share / this.bp) * 100}%`;
        setText(seg.name, this.specs[i]?.label ?? "");
        setText(seg.pct, this.format(share));
      }
      left += share;
      const div = this.dividers[i];
      if (div) {
        div.style.left = `${(left / this.bp) * 100}%`;
        div.setAttribute("aria-valuenow", String(Math.round(share / SNAP_BP)));
      }
    });
  }

  /** Divider i sits after segment i: it trades share between segment i and i+1. */
  private divider(i: number): HTMLElement {
    const node = el("div", "share-divider");
    node.setAttribute("role", "slider");
    node.setAttribute("aria-label", this.specs[i]?.label ?? "");
    node.tabIndex = 0;
    node.addEventListener("pointerdown", (e) => this.drag(e, i, node));
    node.addEventListener("keydown", (e) => {
      const step = e.key === "ArrowRight" ? SNAP_BP : e.key === "ArrowLeft" ? -SNAP_BP : 0;
      if (!step) return;
      e.preventDefault();
      const before = this.local.slice(0, i + 1).reduce((a, b) => a + b, 0);
      if (this.move(i, before + step)) this.hooks.commit(this.shares);
    });
    return node;
  }

  private move(i: number, bpAt: number): boolean {
    const before = this.local.slice(0, i).reduce((a, b) => a + b, 0);
    const pair = (this.local[i] ?? 0) + (this.local[i + 1] ?? 0);
    const raw = Math.round((bpAt - before) / SNAP_BP) * SNAP_BP;
    const mine = Math.min(pair - MIN_SHARE_BP, Math.max(MIN_SHARE_BP, raw));
    if (mine === this.local[i] || pair < 2 * MIN_SHARE_BP) return false;
    this.local[i] = mine;
    this.local[i + 1] = pair - mine;
    this.layout();
    this.hooks.moving?.(this.shares, i);
    return true;
  }

  private drag(e: PointerEvent, i: number, node: HTMLElement): void {
    e.preventDefault();
    e.stopPropagation();
    node.setPointerCapture(e.pointerId);
    node.classList.add("held");
    this.root.classList.add("dragging");
    const rect = this.bar.getBoundingClientRect();
    const start = this.shares.join();
    this.hooks.moving?.(this.shares, i);
    const onMove = (ev: PointerEvent) => { if (this.move(i, ((ev.clientX - rect.left) / rect.width) * this.bp)) tapFeedback(); };
    const onUp = () => {
      node.removeEventListener("pointermove", onMove);
      node.classList.remove("held");
      this.root.classList.remove("dragging");
      pulse(node, "settle");
      if (this.shares.join() !== start) this.hooks.commit(this.shares);
      else this.hooks.moving?.(this.shares, -1);
    };
    node.addEventListener("pointermove", onMove);
    node.addEventListener("pointerup", onUp, { once: true });
    node.addEventListener("pointercancel", onUp, { once: true });
  }

  /** A segment pulled up or down off the bar, past OFF_PX, leaves the mix when let go. */
  private dragOff(e: PointerEvent, i: number, node: HTMLElement): void {
    if (this.segs.length < 2) return;
    node.setPointerCapture(e.pointerId);
    const y0 = e.clientY;
    let off = false;
    const onMove = (ev: PointerEvent) => {
      const dy = ev.clientY - y0;
      off = Math.abs(dy) > OFF_PX;
      node.style.transform = `translateY(${dy}px)`;
      node.classList.toggle("leaving", off);
    };
    const onUp = () => {
      node.removeEventListener("pointermove", onMove);
      node.style.transform = "";
      node.classList.remove("leaving");
      if (off) this.hooks.remove?.(i);
    };
    node.addEventListener("pointermove", onMove);
    node.addEventListener("pointerup", onUp, { once: true });
    node.addEventListener("pointercancel", onUp, { once: true });
  }
}
