// The idle nudge (docs/design/opening-screen.md, "Dots and the one glow"): a player who has not touched anything for a
// while is pointed at the card to tap, with the one glow, unless something else has it. Which card is the screen's
// pick (game/cues.ts, nudgeTarget); any touch starts the wait again.
import type { Glow } from "./fresh";

/** Seconds without a touch before the glow comes: a design choice, long enough that a player reading or deciding is
 * not interrupted, short enough that a stranger who is lost is not left waiting. */
export const NUDGE_IDLE_S = 20;

const TOUCHES = ["pointerdown", "keydown"] as const;

export class IdleNudge {
  private last = performance.now();

  /** `pick`: the node to glow now, or null when there is none. */
  constructor(private readonly glow: Glow, private readonly pick: () => HTMLElement | null) {
    for (const t of TOUCHES) document.addEventListener(t, () => { this.last = performance.now(); }, { capture: true });
  }

  tick(): void {
    if (performance.now() - this.last < NUDGE_IDLE_S * 1000) return;
    const node = this.pick();
    if (node) this.glow.offer(node);
  }
}
