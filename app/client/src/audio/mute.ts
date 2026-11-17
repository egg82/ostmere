// "Sound on this device": a per-device choice in this browser's local storage. On by default, and on whenever
// storage cannot be read or written (a private window, blocked site data); only an explicit off is kept.

export interface SoundSwitch {
  /** True when sound is allowed on this device. */
  get(): boolean;
  set(on: boolean): void;
}

const KEY = "ashfall.sound";

/** `storage` is asked for on each use: even naming `localStorage` can throw. */
export function browserSoundSwitch(storage: () => Storage = () => localStorage): SoundSwitch {
  return {
    get() {
      try { return storage().getItem(KEY) !== "0"; } catch { return true; }
    },
    set(on) {
      try {
        if (on) storage().removeItem(KEY);
        else storage().setItem(KEY, "0");
      } catch { /* no storage: the choice is not kept, and get() says so */ }
    },
  };
}
