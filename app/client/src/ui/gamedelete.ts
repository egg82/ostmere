// Deleting a game asks once more first: one tap asks, in a line beside Cancel, and a second confirms. The words are the
// Games sheet's (ui.games.delete, delete_ask, cancel). Shared by that sheet, the front page's panel and its phone sheet.
import type { GameApi } from "../api/api";
import type { NewSave } from "../api/types";
import { UI, type Text } from "../game/text";
import { el } from "./dom";

export interface DeleteSteps {
  ask(): void;
  cancel(): void;
  confirm(): void;
}

/** What shows for one game's delete: a Delete that asks, or (once asked) the question with Cancel and a Delete that confirms. */
export interface DeleteStyles {
  quiet: string;
  primary: string;
}

/** The words on the two taps and the question: Delete's, or (for a browser's only game) Start over's. */
export interface DeleteWords {
  tap: string;
  ask: string;
}

export const DELETE_WORDS: DeleteWords = { tap: UI.gameDelete, ask: UI.gameDeleteAsk };
export const START_OVER_WORDS: DeleteWords = { tap: UI.gameStartOver, ask: UI.gameStartOverAsk };

export function deleteParts(text: Text, keptDays: number, asking: boolean, on: DeleteSteps, styles: DeleteStyles = { quiet: "quiet", primary: "primary" }, words: DeleteWords = DELETE_WORDS): { question: HTMLElement | null; buttons: HTMLButtonElement[] } {
  const tap = (className: string, key: string, then: () => void): HTMLButtonElement => {
    const b = el("button", className, text.get(key));
    b.type = "button";
    b.addEventListener("click", then);
    return b;
  };
  if (!asking) return { question: null, buttons: [tap(styles.quiet, words.tap, on.ask)] };
  return {
    question: el("p", "games-ask", text.fill(words.ask, { days: String(keptDays) })),
    buttons: [tap(styles.quiet, UI.gameCancel, on.cancel), tap(styles.primary, words.tap, on.confirm)],
  };
}

/** Start over, for a browser's only game: the new game is made first, and only once it is the old one is deleted (the
 * server refuses a last game's delete, and a refused make leaves the old game alone). A failed delete is not a failure:
 * the old game stays in the Games sheet. Rejects with the refusal of making the game. */
export async function startOver(api: Pick<GameApi, "begin" | "deleteGame">, oldId: number): Promise<NewSave> {
  const made = await api.begin();
  await api.deleteGame(oldId).catch(() => undefined);
  return made;
}
