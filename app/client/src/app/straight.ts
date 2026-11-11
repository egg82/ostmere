// "Skip the front page on this device": a per-device choice, kept in this browser's local storage. Off by default,
// and off again whenever storage cannot be read or written (a private window, blocked site data).

export interface Straight {
  get(): boolean;
  set(on: boolean): void;
}

const KEY = "ashfall.straight";

/** `storage` is asked for on each use: even naming `localStorage` can throw. */
export function browserStraight(storage: () => Storage = () => localStorage): Straight {
  return {
    get() {
      try { return storage().getItem(KEY) === "1"; } catch { return false; }
    },
    set(on) {
      try {
        if (on) storage().setItem(KEY, "1");
        else storage().removeItem(KEY);
      } catch { /* no storage: the choice is not kept, and get() says so */ }
    },
  };
}
