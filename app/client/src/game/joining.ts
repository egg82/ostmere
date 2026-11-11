// A join, as the page tells it (CONTRACT.txt, "Moving to another device"): what to say when the server refuses, and a
// reload into GET /api/me when it does not. Shared by the game's sheet and the front page.
import { ApiFailure, type GameApi } from "../api/api";
import type { JoinWay, KeptGames } from "../api/types";
import { UI, type Text } from "./text";

/** none: nothing matched; limited: too many tries; full: both devices' games together pass the cap; ask: this device
 * has games of its own, to move only once the player says so; away: the server did not answer. */
export type JoinRefusal = "none" | "limited" | "full" | "ask" | "away";

/** A join that did not go through; `max` is MergeSummary.max_saves when the server sent one, `wordsReplaced` its
 * words_replaced (false without one). */
export interface Refused { why: JoinRefusal; max: number | null; wordsReplaced: boolean }

/** `onKept`: where a join that left this browser's games behind goes (its words are to be seen first); without it the
 * page reloads as after any join. */
export async function joinWith(api: GameApi, typed: string, way: JoinWay = "plain",
  reload: () => void = () => location.reload(), onKept?: (kept: KeptGames) => void): Promise<Refused | null> {
  let joined;
  try {
    joined = await api.join(typed, way);
  } catch (e) {
    const merge = e instanceof ApiFailure ? e.merge : null;
    return { why: refusal(e), max: merge?.max_saves ?? null, wordsReplaced: merge?.words_replaced ?? false };
  }
  if (joined.kept && onKept) onKept(joined.kept);
  else reload();
  return null;
}

export function refusal(e: unknown): JoinRefusal {
  if (!(e instanceof ApiFailure)) return "away";
  if (e.code === "no_such_code" || e.code === "invalid_decision") return "none";
  if (e.code === "rate_limited") return "limited";
  if (e.code === "confirm_merge") return "ask";
  if (e.code === "too_many_saves") return "full";
  return "away";
}

const LINES: Record<JoinRefusal, string> = {
  none: UI.joinNone, limited: UI.joinLimited, full: UI.joinFull, ask: UI.mergeAsk, away: UI.devicesAway,
};

/** The merge question; when this device's recovery words will stop working (MergeSummary.words_replaced), it says so. */
export function askLine(text: Text, wordsReplaced: boolean): string {
  return wordsReplaced ? `${text.get(UI.mergeAsk)} ${text.get(UI.mergeWords)}` : text.get(UI.mergeAsk);
}

/** The line a refusal shows, the same on the game's sheet and the front page; `codeS` is Content.transfer_code_s and
 * `max` MergeSummary.max_saves. */
export function refusalLine(text: Text, codeS: number, why: JoinRefusal, max: number | null = null): string {
  return text.fill(LINES[why], { minutes: String(Math.floor(codeS / 60)), max: max === null ? "" : String(max) });
}
