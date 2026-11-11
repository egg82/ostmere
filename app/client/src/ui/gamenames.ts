// How a save is named on the front page: "Game 3", "Camp level 4", "Last played 3 hours ago".
import type { SaveInfo } from "../api/types";
import { agoWords } from "../game/ago";
import { UI, type Text } from "../game/text";

export function gameName(text: Text, s: SaveInfo): string {
  return s.number === null ? text.get(UI.gameUnnumbered) : text.fill(UI.gameName, { number: String(s.number) });
}

/** How far the game is; null for a game with no camp level yet (it says nothing). */
export function campLine(text: Text, s: SaveInfo): string | null {
  return s.camp_level === null ? null : text.fill(UI.gameCamp, { level: String(s.camp_level) });
}

export function playedLine(text: Text, s: SaveInfo, now: number): string {
  return text.fill(UI.gamesPlayed, { when: agoWords(text, Date.parse(s.played_at), now) });
}

/** The panel's line for the selected game: its name, how far it is and when it was last played. */
export function savedLine(text: Text, s: SaveInfo, now: number): string {
  return [gameName(text, s), campLine(text, s), playedLine(text, s, now)].filter((part) => part !== null).join(" · ");
}
