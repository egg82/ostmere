// The feedback ladder (docs/design/opening-screen/feedback.md, "The feedback ladder"): one fixed effect per kind of event, sized
// by how much it matters and never grown by repeats. The sizes are keyframes in game.css; the Big rung (the end, a
// feature's card) is drawn by its own parts and has no one-shot effect here.
import type { Card } from "../api/types";
import { sing, type Voice } from "../audio/cues";
import { popOne, pulse } from "./dom";

export type Rung = "background" | "tap" | "first" | "level";

/** Lowest first. */
export const RUNGS: readonly Rung[] = ["background", "tap", "first", "level"];

interface Effect {
  /** The one-shot animation class put on the event's node, if any. */
  readonly pulse: string | null;
  /** A "+1" rising off the node. */
  readonly pop: boolean;
  /** Its sound, fixed like the effect (docs/design/sound.md, "The ladder"); null is silence. A cue (new, level) is one
   * per arrival batch; the knock is the player's own tap. */
  readonly sound: Voice | null;
}

export const LADDER: Readonly<Record<Rung, Effect>> = {
  background: { pulse: null, pop: true, sound: null },
  tap: { pulse: "landed", pop: true, sound: "knock" },
  first: { pulse: "arrive", pop: false, sound: "new" },
  level: { pulse: "burst", pop: false, sound: "level" },
};

/** A completion's rung: a tap's, unless a rule started that tap (`byOrder`); the mix's, and one seen with nobody running
 * it, sit a rung below. */
export function completionRung(by: Card["by"], byOrder: boolean): Rung {
  return by === "tap" && !byOrder ? "tap" : "background";
}

/** Play `rung`'s effect on `node`, and its sound unless `quiet` (a batch's lower cues, what is out of sight). */
export function play(node: HTMLElement, rung: Rung, quiet = false): void {
  const effect = LADDER[rung];
  if (effect.sound && !quiet) sing(effect.sound);
  if (effect.pulse) pulse(node, effect.pulse);
  if (effect.pop) popOne(node);
}
