// The forecast the page holds (CONTRACT.txt, "Forecast"): every level-up, fill and emptying that lands if the player
// changes nothing, orders and the queue played out. It holds until the save's next decision, so a plain advance that
// brings none keeps the one before (game/session.ts). The page draws those times only from here, the first after
// now, so each comes true by itself; nothing listed by the horizon gets no time, never an estimate.
import type { View } from "../api/types";

const first = (times: Iterable<number>, t: number): number | null => {
  let found: number | null = null;
  for (const at of times) if (at > t && (found === null || at < found)) found = at;
  return found;
};

/** When `skill` next levels up after `t`, or null when not by the forecast's horizon. */
export function levelAt(view: View, skill: string, t: number): number | null {
  return first((view.forecast?.level_ups ?? []).filter((f) => f.skill === skill).map((f) => f.at), t);
}

/** When `skill` reaches its phase's top after `t` ("tops out in"), or null when not by the forecast's horizon. */
export function topAt(view: View, skill: string, t: number): number | null {
  return first((view.forecast?.tops_out ?? []).filter((f) => f.skill === skill).map((f) => f.at), t);
}

/** When `store` next reaches its cap after `t`, or null when not by the forecast's horizon. */
export function fullAt(view: View, store: string, t: number): number | null {
  return first((view.forecast?.fills ?? []).filter((f) => f.store === store).map((f) => f.at), t);
}

/** When `store` next runs to 0 after `t`, or null when not by the forecast's horizon. */
export function emptyAt(view: View, store: string, t: number): number | null {
  return first((view.forecast?.empties ?? []).filter((f) => f.store === store).map((f) => f.at), t);
}
