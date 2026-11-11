// The two quiet marks (decisions.md, "Shown in the design, not claimed"). A dot on what is new, small and still, until
// the player interacts with it (a tap, a drag, a key); never a count. The glow on the one obvious next step, at most one
// control at a time, until it is used; which control gets it is the screen's rule (screen.ts).
import { el } from "./dom";
import type { Arrivals } from "./reveal";

const TOUCHES = ["pointerdown", "keydown"] as const;

/** A dot on a control `node` until the player touches it (`touched` runs then). The dot takes no room, so nothing moves. */
export function markNew(node: HTMLElement, touched: () => void): void {
  if (node.querySelector(":scope > .new-dot")) return;
  const dot = el("i", "new-dot");
  dot.setAttribute("aria-hidden", "true");
  node.append(dot);
  const clear = (): void => {
    dot.remove();
    for (const t of TOUCHES) node.removeEventListener(t, clear);
    touched();
  };
  for (const t of TOUCHES) node.addEventListener(t, clear);
}

/** Drops `node`'s dot, if it has one (its card went to work). */
export function unmark(node: HTMLElement): void {
  node.querySelector(":scope > .new-dot")?.remove();
}

/** The one glow on the page. It comes on at its turn in the arrival queue, so it never lands while a line is read. */
export class Glow {
  private node: HTMLElement | null = null;
  private waiting: HTMLElement | null = null;

  constructor(private readonly arrivals: Arrivals | null = null) {}

  get busy(): boolean {
    return (this.node !== null && this.node.isConnected) || this.waiting !== null;
  }

  /** Puts the glow on `node` unless another control has it (or is about to); it goes when `node` is used. */
  offer(node: HTMLElement): boolean {
    if (this.busy) return this.node === node || this.waiting === node;
    if (this.arrivals?.busy) {
      this.waiting = node;
      this.arrivals.effect(node, "card", () => {   // its turn: it takes the glow (offering again could queue it again)
        this.waiting = null;
        if (!this.busy) this.place(node);
      });
      return true;
    }
    this.place(node);
    return true;
  }

  private place(node: HTMLElement): void {
    this.node = node;
    node.classList.add("glow");
    const clear = (): void => this.clear(node);
    node.addEventListener("click", clear, { once: true });
  }

  clear(node?: HTMLElement): void {
    if (!this.node || (node && node !== this.node)) return;
    this.node.classList.remove("glow");
    this.node = null;
  }
}

/** The one glow on `node` from each time `want` turns true until the node is used (`used`, or its click) or `want`
 * turns false. It waits while another control has the glow, and while the reveal holds the node back. */
export class GlowWhile {
  private pending = false;
  private was = false;

  constructor(private readonly glow: Glow, private readonly node: HTMLElement) {}

  update(want: boolean): void {
    if (want && !this.was) this.pending = true;
    if (!want) this.used();
    this.was = want;
    this.tick();
  }

  /** Every frame: offer it once nothing holds it back. */
  tick(): void {
    if (!this.pending || this.node.closest(".held")) return;
    if (this.glow.offer(this.node)) this.pending = false;
  }

  used(): void {
    this.pending = false;
    this.glow.clear(this.node);
  }
}
