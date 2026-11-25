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

/** How a control takes the glow: one that `yields` gives it up to a control that `outranks` it (a story step the content
 * marks takes it from the shown ask, which keeps its outline). */
export interface GlowRank {
  yields?: boolean;
  outranks?: boolean;
}

/** The one glow on the page. It comes on at its turn in the arrival queue, so it never lands while a line is read. */
export class Glow {
  private node: HTMLElement | null = null;
  private waiting: HTMLElement | null = null;
  private yields = false;

  constructor(private readonly arrivals: Arrivals | null = null) {}

  get busy(): boolean {
    return (this.node !== null && this.node.isConnected) || this.waiting !== null;
  }

  /** Puts the glow on `node` unless another control has it (or is about to) and does not yield to `node`; it goes when
   * `node` is used. */
  offer(node: HTMLElement, rank: GlowRank = {}): boolean {
    if (rank.outranks === true && this.yields && this.busy && this.node !== node && this.waiting !== node) {
      this.waiting = null;   // a yielding control still waiting for its turn gives up that turn
      this.clear();
    }
    if (this.busy) return this.node === node || this.waiting === node;
    if (this.arrivals?.busy) {
      this.waiting = node;
      this.yields = rank.yields === true;
      this.arrivals.effect(node, "card", () => {   // its turn: it takes the glow (offering again could queue it again)
        if (this.waiting !== node) return;   // outranked while it waited
        this.waiting = null;
        if (!this.busy) this.place(node, rank);
      });
      return true;
    }
    this.place(node, rank);
    return true;
  }

  private place(node: HTMLElement, rank: GlowRank): void {
    this.node = node;
    this.yields = rank.yields === true;
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

  constructor(private readonly glow: Glow, private readonly node: HTMLElement, private readonly rank: GlowRank = {}) {}

  update(want: boolean): void {
    if (want && !this.was) this.pending = true;
    if (!want) this.used();
    this.was = want;
    this.tick();
  }

  /** Every frame: offer it once nothing holds it back. */
  tick(): void {
    if (!this.pending || this.node.closest(".held")) return;
    if (this.glow.offer(this.node, this.rank)) this.pending = false;
  }

  used(): void {
    this.pending = false;
    this.glow.clear(this.node);
  }
}
