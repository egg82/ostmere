// FIXTURE, never shipped: an account's games for the Games sheet (fixture-api.ts), the game being played (save 1, as the
// fixture's NewSave names it) and two others, with one deleted game held. Delete and restore move them between the
// lists as the server would; the cap and the last live save answer as the contract says.
import { ApiFailure } from "../src/api/api";
import type { DeletedSave, Games, SaveInfo } from "../src/api/types";

const DAY_MS = 86_400_000;
const MAX_SAVES = 5;
const KEPT_DAYS = 30;

function game(saveId: number, number: number, campLevel: number, startedDaysAgo: number, playedDaysAgo: number): SaveInfo {
  const at = (days: number): string => new Date(Date.now() - days * DAY_MS).toISOString();
  return {
    save_id: saveId, number, decisions: 12 * number, game_time: 3600 * number, ended_at: null,
    started_at: at(startedDaysAgo), played_at: at(playedDaysAgo), camp_level: campLevel,
  };
}

export interface FixtureGames {
  games(): Promise<Games>;
  deleteGame(saveId: number): Promise<Games>;
  restoreGame(saveId: number): Promise<Games>;
}

export function fixtureGames(): FixtureGames {
  let live: SaveInfo[] = [game(1, 3, 2, 1, 0), game(2, 1, 4, 9, 2), game(3, 2, 0, 5, 5)];
  let held: DeletedSave[] = [{ save: game(4, 4, 1, 3, 3), deleted_at: new Date(Date.now() - 2 * DAY_MS).toISOString(),
    purge_at: new Date(Date.now() + (KEPT_DAYS - 2) * DAY_MS).toISOString() }];
  const answer = (): Promise<Games> => Promise.resolve({ saves: live, deleted: held, max_saves: MAX_SAVES, kept_days: KEPT_DAYS });
  return {
    games: answer,
    deleteGame: (saveId) => {
      const found = live.find((s) => s.save_id === saveId);
      if (!found) return Promise.reject(new ApiFailure("not_found", "fixture: no such game"));
      if (live.length === 1) return Promise.reject(new ApiFailure("last_save", "fixture: the only game"));
      live = live.filter((s) => s !== found);
      const now = Date.now();
      held = [{ save: found, deleted_at: new Date(now).toISOString(), purge_at: new Date(now + KEPT_DAYS * DAY_MS).toISOString() }, ...held];
      return answer();
    },
    restoreGame: (saveId) => {
      const found = held.find((d) => d.save.save_id === saveId);
      if (!found) return Promise.reject(new ApiFailure("not_found", "fixture: no such deleted game"));
      if (live.length >= MAX_SAVES) return Promise.reject(new ApiFailure("too_many_saves", "fixture: at the cap"));
      held = held.filter((d) => d !== found);
      live = [...live, found.save];
      return answer();
    },
  };
}
