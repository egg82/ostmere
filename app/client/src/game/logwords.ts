// The words a Log stretch wears: how long the player was away, and how many lines of a kind it holds. Pure.
import type { LineKind } from "./loggroups";
import { UI, type Text } from "./text";

const COUNT: Record<LineKind, string> = {
  story: UI.logNStory, find: UI.logNFind, tap: UI.logNTap, level: UI.logNLevel, body: UI.logNBody, fight: UI.logNFight,
};

/** "Away 54m", "Away 5h 3m", "Away 2d": the time between leaving and returning, to the minute and under a day to the hour. */
export function awayTitle(text: Text, seconds: number): string {
  const minutes = Math.round(seconds / 60);
  const h = Math.floor(minutes / 60), m = minutes % 60;
  if (minutes < 60) return text.fill(UI.logAwayM, { m: String(minutes) });
  if (h < 24) return m === 0 ? text.fill(UI.logAwayH, { h: String(h) }) : text.fill(UI.logAwayHm, { h: String(h), m: String(m) });
  return text.fill(UI.logAwayD, { d: String(Math.floor(h / 24)) });
}

/** "Finds 3": a kind's label and how many lines of it. */
export function kindCount(text: Text, kind: LineKind, n: number): string {
  return text.fill(COUNT[kind], { n: String(n) });
}
