// What the page tells the telemetry after each Step lands (src/telemetry).
import type { Content, View } from "../api/types";
import { noteProgress } from "../telemetry";

/** Tells the telemetry the game clock and which one-off (narrative) cards have completed. */
export function progressed(content: Content, view: View): void {
  const oneOffs = new Set(content.card_infos.filter((c) => c.presentation === "narrative").map((c) => c.card));
  const done = [...view.cards, ...view.completed].filter((c) => oneOffs.has(c.card) && c.completions > 0);
  noteProgress(view.at, done.map((c) => c.card));
}
