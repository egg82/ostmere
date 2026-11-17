// The sound map's slots as data (`docs/design/sound.md`). A slot with no `asset` is skipped, never late: assets live
// on the assets volume (served at /assets/) and are picked by the owner's ear, so none is named yet.

export type SlotName = "tap" | "tick" | "first" | "level" | "strike" | "story" | "failed" | "page" | "settle";

export interface Slot {
  /** Path under /assets/, or null while no recording is picked. */
  asset: string | null;
  /** Linear gain, 1 being the tap's level. */
  gain: number;
  /** Playback-rate ratio against the recording; pitch is set by rate, in exact ratios. */
  pitch: number;
}

export type BedName = "wind" | "fire";

const none = (gain: number): Slot => ({ asset: null, gain, pitch: 1 });

// Loudness steps from the map: soft is the tap's level, medium 4 dB above it, full 8 dB above it.
const MEDIUM = 10 ** (4 / 20);
const FULL = 10 ** (8 / 20);

export const SLOTS: Readonly<Record<SlotName, Slot>> = {
  tap: none(1),
  tick: none(1),
  first: none(1),
  level: none(MEDIUM),
  strike: none(FULL),
  story: none(MEDIUM),
  failed: none(10 ** (-4 / 20)),
  page: none(1),
  settle: none(1),
};

// The bed sits under the tap, felt more than heard; the owner's ear sets these.
const UNDER = 10 ** (-12 / 20);

/** The looping beds, each at its fixed gain; the fire's is scaled by its layer's alpha. */
export const BEDS: Readonly<Record<BedName, Slot>> = {
  wind: none(UNDER),
  fire: none(UNDER),
};
