// The fire's light varying as it burns: the scene's one animation path. A layer with `flicker` (its strength, 0 to 1) is
// drawn at an alpha scaled by a level that wanders, each frame drawn only while such a layer is showing and motion is
// allowed (scene.ts). A later animation (a walk) takes its own clock from Clock the same way. Pure: nothing here draws.

/** Light changes per second: the level is held between steps, so a frame is drawn at this rate, not the display's. */
export const FLICKER_HZ = 15;

/** A value in [0, 1) fixed by the integer `n` and the seed (an integer hash). */
function hashed(n: number, seed: number): number {
  let h = Math.imul(n ^ Math.imul(seed + 1, 0x9e3779b1), 0x85ebca6b);
  h ^= h >>> 13;
  h = Math.imul(h, 0xc2b2ae35);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}

/** Smooth noise at `rate` random values a second: each is held at its own second and eased into the next. */
function noise(seconds: number, rate: number, seed: number): number {
  const x = seconds * rate;
  const i = Math.floor(x);
  const f = x - i;
  const s = f * f * (3 - 2 * f);
  const a = hashed(i, seed);
  return a + (hashed(i + 1, seed) - a) * s;
}

/** The light's level at `seconds`, from 1 - strength (at its dimmest) to 1: slow swells under quick, uneven jitter, so
 * it never repeats and has no beat to see. `seed` keeps two fires out of step. */
export function flickerLevel(seconds: number, seed: number, strength: number): number {
  const slow = noise(seconds, 2.3, seed);
  const quick = noise(seconds, 11, seed + 101);
  const n = 0.6 * slow + 0.4 * quick;
  return 1 - strength * Math.min(1, Math.max(0, (n - 0.2) / 0.6));
}

/** The levels of the layers that flicker, stepped by the frame: steady (1) under reduced motion, else new at FLICKER_HZ. */
export class Clock {
  private seconds = 0;
  private step = -1;

  /** Advances by dt; true when the level should be read again (a step passed, or reduced motion has just ended or begun). */
  advance(dt: number, reduced: boolean): boolean {
    this.seconds += dt;
    const step = reduced ? -2 : Math.floor(this.seconds * FLICKER_HZ);
    const moved = step !== this.step;
    this.step = step;
    return moved;
  }

  level(seed: number, strength: number, reduced: boolean): number {
    return reduced ? 1 : flickerLevel(Math.floor(this.seconds * FLICKER_HZ) / FLICKER_HZ, seed, strength);
  }
}
