// A game lost right after Begin inside another site's frame (src/game.ts, src/game/session.ts): the forecast asked
// after Begin is the first request to find the session gone and says so; any other forecast failure only waits for the
// next ask; and the page takes the game's screen down so the front page's message, not a dead screen, is in view.
import { ApiFailure, type GameApi } from "../src/api/api";
import type { Step } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { play } from "../src/game";
import { Session, type SessionEvents } from "../src/game/session";
import { fakeDocument, install } from "./fake-dom";
import { NEW_SAVE, NEW_ACCOUNT, NEW_SETTINGS } from "../src/game/keeps";

install();
const realInterval = globalThis.setInterval;   // the page's self-update polls forever; this run clears it to end
const polls: number[] = [];
Object.assign(globalThis, { setInterval: (f: () => void, ms: number) => { const id = realInterval(f, ms); polls.push(id); return id; } });
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } }, requestAnimationFrame: () => 0, addEventListener: () => undefined });
Object.assign(window, { top: {}, self: {} });   // inside a frame

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const step = (): Step => ({ ...fixtureStep("mid", 100, {}, 0), save_id: 7, rules_digest: fixtureContent.rules_digest });
const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };

function apiWhose(forecast: () => Promise<never>, advance: () => Promise<Step> = () => Promise.resolve(step())): GameApi {
  const away = (): Promise<never> => Promise.reject(new Error("not in these tests"));
  return {
    content: () => Promise.resolve(fixtureContent),
    me: () => Promise.resolve({ account: null, saves: [], max_saves: 5, kept_days: 30 }),
    begin: () => Promise.resolve({ save, presentation: NEW_SAVE, step: step() }),
    open: away, advance, savedView: away, forecast, decide: away, dryRun: away,
    putMePresentation: (p) => Promise.resolve({ presentation: p, settings: NEW_SETTINGS, has_words: false, words_due: false }),
    putMeSettings: (settings) => Promise.resolve({ presentation: NEW_ACCOUNT, settings, has_words: false, words_due: false }),
    putSavePresentation: (_id, p) => Promise.resolve(p),
    sendFeedback: () => Promise.resolve(),
    makeCode: away, makeWords: away, games: away, deleteGame: away, restoreGame: away, join: away, devices: away, removeDevice: away,
  };
}

const gone = (): Promise<never> => Promise.reject(new ApiFailure("no_account", "401"));
const broken = (): Promise<never> => Promise.reject(new ApiFailure("network", "500 Internal Server Error"));

/** A Session just begun, its quiet spell over, and one tick past it: the forecast's ask has been made and answered. */
async function afterForecast(forecast: () => Promise<never>): Promise<boolean[]> {
  const lost: boolean[] = [];
  const none = (): void => undefined;
  const events: SessionEvents = { started: none, stepped: none, build: none, refused: none, connected: none, lost: (fresh) => { lost.push(fresh); }, limited: none, catchingUp: none };
  let ms = 0;
  const session = new Session(apiWhose(forecast), events, undefined, () => Promise.resolve(), () => ms);
  await session.begin();
  ms += 120_000;
  session.tick();
  await session.settled();
  return lost;
}

{  // the forecast is the first request to find the session gone
  const lost = await afterForecast(gone);
  check(lost.join() === "true", `a forecast 401 right after Begin is a fresh loss: ${lost.join()}`);
}
{  // anything else only waits for the next ask
  const warn = console.warn;
  const warned: unknown[][] = [];
  console.warn = (...a: unknown[]) => { warned.push(a); };
  const lost = await afterForecast(broken);
  console.warn = warn;
  check(lost.length === 0 && warned.length === 1, `a forecast 500 only warns: lost ${lost.length}, warned ${warned.length}`);
}
{  // a loss in a frame takes the game down, whatever was mounted, and tells the page
  let unkept = 0;
  const session = play(apiWhose(broken, gone), document.body, { resume: null, unkept: () => { unkept += 1; } }, "");
  await session.settled();
  check(fakeDocument.querySelector(".game") !== null, "the game is on screen after Begin");
  await session.advance();
  check(unkept === 1, `the page is told once: ${unkept}`);
  check(fakeDocument.querySelector(".game") === null, "no game screen is left over the front page");
  check(fakeDocument.body.kids.length === 0, "nor any of its sheets");
}
globalThis.setInterval = realInterval;
for (const id of polls) clearInterval(id);
