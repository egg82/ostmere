// The story strip's turn in the queue: a step's lines first, and on a return the glow (game.css `.glow`) on the strip while
// the first is held, so the eye goes there as the lines start (docs/decisions/knowledge.md, "A story line stays until it can be read").
import { readingMs } from "../../game/reading";
import type { Arrivals } from "../feedback/reveal";

export class StripGlow {
  private until = 0;

  constructor(private readonly strip: HTMLElement) {}

  /** Each of `nodes` first in the queue, in the strip, held for its reading time (a null, or a node not in the strip, is
   * skipped: a return's chip or task line, game/awaylines.ts). `id` gives each a queue id. On a return the first is held
   * READING.returnFirst times longer and the strip glows for that hold. */
  lead(arrivals: Arrivals, nodes: Array<HTMLElement | null>, returned: boolean, id: () => string, opens: readonly boolean[] = []): void {
    let first = returned;
    for (const [i, shown] of nodes.entries()) {
      if (!shown?.isConnected) continue;
      const hold = readingMs(shown.textContent ?? "", first);
      if (first) this.light(performance.now(), hold);
      first = false;
      arrivals.line([shown], id(), hold, opens[i] ? "beat" : undefined);
    }
  }

  /** Lit now, for `ms`. */
  light(nowMs: number, ms: number): void {
    this.strip.classList.add("glow");
    this.until = nowMs + ms;
  }

  /** Out when the hold ends, or when nothing waits any more (a tap moved the lines on). */
  tick(nowMs: number, busy: boolean): void {
    if (this.until === 0 || (nowMs < this.until && busy)) return;
    this.strip.classList.remove("glow");
    this.until = 0;
  }
}
