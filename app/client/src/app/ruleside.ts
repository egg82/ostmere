// The side of the Rules page this device last showed, Mine or Camp: kept in this browser's local storage, Mine when
// storage cannot be read or written (a private window, blocked site data).
import type { RuleSide } from "../game/rules/ruleside";

export interface SideKept {
  get(): RuleSide;
  set(side: RuleSide): void;
}

const KEY = "ashfall.ruleside";

/** `storage` is asked for on each use: even naming `localStorage` can throw. */
export function browserSide(storage: () => Storage = () => localStorage): SideKept {
  return {
    get() {
      try { return storage().getItem(KEY) === "camp" ? "camp" : "mine"; } catch { return "mine"; }
    },
    set(side) {
      try { storage().setItem(KEY, side); } catch { /* no storage: the side is not kept, and get() says so */ }
    },
  };
}
