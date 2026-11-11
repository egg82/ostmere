// The feedback ladder (docs/design/opening-screen.md, "The feedback ladder"): one fixed effect per kind of event, sized
// by how much it matters and never grown by repeats. The sizes are keyframes in game.css; the Big rung (the end, a
// feature's card) is drawn by its own parts and has no one-shot effect here.
import type { Card } from "../api/types";
import { popOne, pulse } from "./dom";

export type Rung = "background" | "tap" | "first" | "level";

/** Lowest first. */
export const RUNGS: readonly Rung[] = ["background", "tap", "first", "level"];

interface Effect {
  /** The one-shot animation class put on the event's node, if any. */
  readonly pulse: string | null;
  /** A "+1" rising off the node. */
  readonly pop: boolean;
}

export const LADDER: Readonly<Record<Rung, Effect>> = {
  background: { pulse: null, pop: true },
  tap: { pulse: "landed", pop: true },
  first: { pulse: "arrive", pop: false },
  level: { pulse: "burst", pop: false },
};

/** A completion's rung: a tap's, unless a rule started that tap (`byOrder`); the mix's, and one seen with nobody running
 * it, sit a rung below. */
export function completionRung(by: Card["by"], byOrder: boolean): Rung {
  return by === "tap" && !byOrder ? "tap" : "background";
}

/** Play `rung`'s effect on `node`. */
export function play(node: HTMLElement, rung: Rung): void {
  const effect = LADDER[rung];
  if (effect.pulse) pulse(node, effect.pulse);
  if (effect.pop) popOne(node);
}
