// A deploy between the slices of a long absence's open (CONTRACT.txt, "CATCHING UP"): the Step the open lands on carries
// the new rules digest, so the page fetches the new content as it does for any Step (src/game/session.ts).
import type { GameApi } from "../src/api/api";
import type { Step } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session, type SessionEvents } from "../src/game/session";
import { NEW_SAVE } from "../src/game/keeps";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const slice = (at: number, to: number | null, rules_digest: string): Step =>
  ({ ...fixtureStep("mid", at, {}, 0), save_id: 7, rules_digest, catching_up_to: to });
const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };
const unused = () => Promise.reject(new Error("not in this test"));
let fetched = 0;
const api: GameApi = {
  content: () => { fetched += 1; return Promise.resolve({ ...fixtureContent, rules_digest: fetched === 1 ? fixtureContent.rules_digest : "new" }); },
  me: unused, begin: unused,
  open: () => Promise.resolve({ save, was: fixtureStep("mid", 40).view, history: [], presentation: NEW_SAVE, step: slice(100, 500, fixtureContent.rules_digest) }),
  savedView: () => Promise.reject(new Error("unused")),
  advance: () => Promise.resolve(slice(500, null, "new")),
  forecast: unused, decide: unused, dryRun: unused, putMePresentation: unused, putMeSettings: unused, putSavePresentation: unused, sendFeedback: unused, makeCode: unused,
  makeWords: unused, games: unused, deleteGame: unused, restoreGame: unused, join: unused, devices: unused, removeDevice: unused,
};
const started: string[] = [];
const none = (): void => undefined;
const events: SessionEvents = {
  started(content) { started.push(content.rules_digest); },
  stepped: none, build: none, refused: none, connected: none, lost: none, limited: none, catchingUp: none,
};
const session = new Session(api, events, undefined, () => Promise.resolve(), () => 0);
await session.resume(7);
check(fetched === 2, `the content is fetched again for the new digest: ${fetched}`);
check(started.join() === `${fixtureContent.rules_digest},new`, `the page is drawn with the new content: ${started.join()}`);
