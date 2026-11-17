// The sound locator: callers ask for `sound()` and never learn whether audio exists. The default plays nothing, so a
// page without audio (tests, a browser that refuses it, sound not started yet) is silent, not broken.
import type { SlotName } from "./slots";

export interface Sound {
  /** Play a slot's one-shot now. `pitch` multiplies the slot's own ratio (a chain's rising ticks). Never throws. */
  play(slot: SlotName, pitch?: number): void;
}

const NULL_SOUND: Sound = { play() { /* silence */ } };
const NO_REFRESH = (): void => undefined;

let current: Sound = NULL_SOUND;
let refresh = NO_REFRESH;

/** `refreshSilence` is what `bindSilence` returned: the switch's controls call it after a change, so the cut is at once. */
export function registerSound(sound: Sound, refreshSilence: () => void = NO_REFRESH): void { current = sound; refresh = refreshSilence; }

/** Back to the Null default. */
export function resetSound(): void { current = NULL_SOUND; refresh = NO_REFRESH; }

/** True once something other than the Null default is registered: the UI draws sound's controls only then. */
export function hasSound(): boolean { return current !== NULL_SOUND; }

/** Re-reads the device's switch into the registered player. */
export function refreshSilence(): void { refresh(); }

export function sound(): Sound { return current; }
