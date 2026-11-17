// The sound locator: callers ask for `sound()` and never learn whether audio exists. The default plays nothing, so a
// page without audio (tests, a browser that refuses it, sound not started yet) is silent, not broken.
import type { BedName, PieceName, SlotName } from "./slots";

export interface Sound {
  /** Play a slot's one-shot `delayMs` from now, on the audio clock. `pitch` multiplies the slot's own ratio (a chain's
   * rising ticks). Never throws. Returns a cut: it fades the sound over CUT_MS, so one not yet begun never sounds. */
  play(slot: SlotName, pitch?: number, delayMs?: number): () => void;
  /** A looping bed, silent until `setLevel`. Never throws. */
  loop(bed: BedName): Loop;
  /** A piece of music, begun now and silent until `setLevel`; it plays once and ends on its own. Never throws. */
  piece(name: PieceName): Piece;
}

export interface Piece {
  /** Ramp the piece to `level` (0 to 1, against its slot's gain) over `rampMs`; 0 ms is at once. */
  setLevel(level: number, rampMs: number): void;
  /** Fade out over `rampMs`, then end. */
  stop(rampMs: number): void;
  /** `fn` runs once when the piece is over, by its last note or by `stop`. A piece that never began is over at once. */
  onEnd(fn: () => void): void;
}

export interface Loop {
  /** Ramp the bed to `level` (0 to 1, against its slot's gain) over `rampMs`; 0 ms is at once. */
  setLevel(level: number, rampMs: number): void;
}

const NOTHING = (): void => undefined;
const NULL_PIECE: Piece = { setLevel: NOTHING, stop: NOTHING, onEnd: NOTHING };
const NULL_SOUND: Sound = { play: () => NOTHING, loop: () => ({ setLevel: NOTHING }), piece: () => NULL_PIECE };
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
