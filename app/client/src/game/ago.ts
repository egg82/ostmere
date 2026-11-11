// How long ago a game was last played, as the words of ui.time.* ("3 hours ago"). Pure: the caller names the clock.
import { UI, type Text } from "./text";

const MINUTE = 60_000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

export function agoWords(text: Text, playedAt: number, now: number): string {
  const since = Math.max(0, now - playedAt);
  if (since < 2 * MINUTE) return text.get(UI.timeNow);
  if (since < HOUR) return text.fill(UI.timeMinutes, { n: String(Math.floor(since / MINUTE)) });
  if (since < 2 * HOUR) return text.get(UI.timeHour);
  if (since < DAY) return text.fill(UI.timeHours, { n: String(Math.floor(since / HOUR)) });
  if (since < 2 * DAY) return text.get(UI.timeYesterday);
  return text.fill(UI.timeDays, { n: String(Math.floor(since / DAY)) });
}
