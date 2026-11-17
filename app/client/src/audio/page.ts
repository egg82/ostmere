// Wires the player to the page: silent while the page is hidden or the device's switch says off.
import type { Player } from "./player";
import type { SoundSwitch } from "./mute";

export interface PageLike {
  hidden: boolean;
  addEventListener(type: "visibilitychange", fn: () => void): void;
}

/** Returns `refresh`, to call after the switch changes; the page's own visibility changes call it already. */
export function bindSilence(player: Player, page: PageLike, mute: SoundSwitch): () => void {
  const refresh = () => player.setSilent(page.hidden || !mute.get());
  page.addEventListener("visibilitychange", refresh);
  refresh();
  return refresh;
}
