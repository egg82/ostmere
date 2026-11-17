// The bed under the scene (docs/design/sound.md, "The bed under the scene"): the wind fades in from the page's first
// tap, and the fire's gain is the alpha the scene draws its firelight layer at. Both go through the locator, so the Null
// default plays nothing.
import { sound, type Loop } from "./locator";

/** The wind's fade-in from the first tap, and the fire's when it is already built at that tap. */
export const WIND_FADE_MS = 2500;
export const FIRE_CATCH_MS = 800;

export interface Bed {
  /** The page's first tap: the wind begins to fade in. Later calls change nothing. */
  firstTap(): void;
  /** Each frame, with the alpha the scene now draws the fire's layer at (0 where it is not built). Silent before the first tap. */
  follow(fireAlpha: number): void;
}

export function createBed(): Bed {
  let fire: Loop | null = null;
  let last = 0;
  let caught = false;
  return {
    firstTap() {
      if (fire) return;
      sound().loop("wind").setLevel(1, WIND_FADE_MS);
      fire = sound().loop("fire");
    },
    follow(alpha) {
      if (!fire || (caught && alpha === last)) return;
      // Built before the first tap: it catches in sound over the time it catches in light. Otherwise the scene's own
      // fade is the ramp, so each frame's alpha is set at once.
      fire.setLevel(alpha, !caught && alpha === 1 ? FIRE_CATCH_MS : 0);
      caught = true;
      last = alpha;
    },
  };
}
