// Which served lines open a story beat (api/contract/endpoints.txt, "Beat lines"): the server says so on the line, so the page
// never takes a beat from a key or a line's words.
import type { LogLine } from "../api/types";

/** The first line of the beats in `lines`, in order. */
export function beatOpeners(lines: readonly LogLine[]): LogLine[] {
  return lines.filter((l) => l.opens_beat);
}
