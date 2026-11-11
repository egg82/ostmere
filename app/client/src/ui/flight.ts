// A just-accepted rule offer flies to where rules live now: a copy of the offer waits above the page until the new
// rule shows up in a view, then flies to the Rules tab's label. Under prefers-reduced-motion, or with no
// copy waiting, the target only pulses. The flight answers the player's own tap, so it goes at once; the target's
// pulse is an arrival like any other and takes its turn behind a line (reveal.ts).
import { reducedMotion } from "./dom";
import { play } from "./ladder";
import { markNew } from "./fresh";
import type { Arrivals } from "./reveal";

const FLY_MS = 450;
const WAIT_MS = 4000;

export class Flight {
  private flying: HTMLElement | null = null;

  constructor(private readonly arrivals: Arrivals) {}

  launch(from: HTMLElement): void {
    this.drop();
    if (reducedMotion()) return;
    const rect = from.getBoundingClientRect();
    const copy = from.cloneNode(true) as HTMLElement;
    copy.classList.add("order-flight");
    Object.assign(copy.style, { left: `${rect.left}px`, top: `${rect.top}px`, width: `${rect.width}px`, height: `${rect.height}px` });
    document.body.append(copy);
    this.flying = copy;
    window.setTimeout(() => { if (this.flying === copy) this.drop(); }, WAIT_MS);
  }

  land(target: HTMLElement): void {
    const copy = this.flying;
    if (!copy) {
      this.arrive(target);
      return;
    }
    this.flying = null;
    const to = target.getBoundingClientRect();
    const from = copy.getBoundingClientRect();
    const dx = to.left - from.left, dy = to.top - from.top;
    const scale = Math.min(1, to.width / from.width);
    copy.animate(
      [{ transform: "none", opacity: 1 }, { transform: `translate(${dx}px, ${dy}px) scale(${scale})`, opacity: 0.3 }],
      { duration: FLY_MS, easing: "ease-in-out", fill: "forwards" },
    ).finished.then(() => { copy.remove(); this.arrive(target); }, () => copy.remove());
  }

  /** A rule or a queued tap went to the Rules tab: it lands there and, unless that tab is the one open, the tab keeps
   * a quiet dot until it is next touched, so the way to where it went stays marked (no text). */
  landed(tab: HTMLElement, onTab: boolean): void {
    this.land(tab);
    if (!onTab) markNew(tab, () => undefined);
  }

  private arrive(target: HTMLElement): void {
    this.arrivals.effect(target, "feature", () => play(target, "first"));
  }

  private drop(): void {
    this.flying?.remove();
    this.flying = null;
  }
}
