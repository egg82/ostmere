// The sound locator: callers ask for `sound()` and never learn whether audio exists. The default plays nothing, so a
// page without audio (tests, a browser that refuses it, sound not started yet) is silent, not broken.
import type { SlotName } from "./slots";

export interface Sound {
  /** Play a slot's one-shot now. `pitch` multiplies the slot's own ratio (a chain's rising ticks). Never throws. */
  play(slot: SlotName, pitch?: number): void;
}

const NULL_SOUND: Sound = { play() { /* silence */ } };

let current: Sound = NULL_SOUND;

export function registerSound(sound: Sound): void { current = sound; }

/** Back to the Null default. */
export function resetSound(): void { current = NULL_SOUND; }

export function sound(): Sound { return current; }
