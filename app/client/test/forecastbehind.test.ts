// A forecast refused as catching_up (the save is behind: CONTRACT.txt, "CATCHING UP") is a read that wrote nothing, so the
// page asks a plain advance, which catches the save up (src/game/session.ts).
import { ApiFailure, type GameApi } from "../src/api/api";
import type { Step } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session, type SessionEvents } from "../src/game/session";
import { NEW_SAVE } from "../src/game/keeps";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const AT = 100;
const step = (at: number, to: number | null): Step =>
  ({ ...fixtureStep("mid", at, {}, 0), save_id: 7, rules_digest: fixtureContent.rules_digest, catching_up_to: to });
const unused = () => Promise.reject(new Error("not in this test"));
const calls: string[] = [];
const api: GameApi = {
  content: () => Promise.resolve(fixtureContent),
  me: unused,
  begin: () => Promise.resolve({ save: { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 }, presentation: NEW_SAVE, step: step(AT, null) }),
  open: unused,
  savedView: () => Promise.reject(new Error("unused")),
  advance: () => { calls.push("advance"); return Promise.resolve(step(AT + 500, null)); },
  forecast: () => { calls.push("forecast"); return Promise.reject(new ApiFailure("catching_up", "behind", step(AT, AT + 500))); },
  decide: unused, dryRun: unused, putMePresentation: unused, putMeSettings: unused, putSavePresentation: unused, sendFeedback: unused, makeCode: unused, makeWords: unused,
  games: unused, deleteGame: unused, restoreGame: unused, join: unused, devices: unused, removeDevice: unused,
};
const none = (): void => undefined;
const events: SessionEvents = { started: none, stepped: none, build: none, refused: none, connected: none, lost: none, limited: none, catchingUp: none };
const session = new Session(api, events, undefined, () => Promise.resolve(), () => 0);
await session.begin();
session.tick();
await session.settled();
check(calls.join() === "forecast,advance", `a forecast refused as behind asks a plain advance: ${calls.join()}`);
check(session.view?.at === AT + 500, "and the save it answers is drawn");
