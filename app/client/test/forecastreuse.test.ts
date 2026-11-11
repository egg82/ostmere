// The page holds the forecast (CONTRACT.txt, "Forecast"; src/game/session.ts): asked for by its own call, it is drawn on
// every view while the save has had no decision since; a decision since (the page's or another's) leaves the view
// without one until the page asks again, which it does after a quiet spell, at most once a minute; one near its
// horizon, or half its span if that is less, is asked for afresh.
import type { GameApi } from "../src/api/api";
import type { Forecast, Step } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session, type SessionEvents } from "../src/game/session";
import { NEW_SAVE, NEW_ACCOUNT, NEW_SETTINGS } from "../src/game/keeps";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const AT = 100;
const FORECAST: Forecast = { horizon_at: AT + 6 * 3600, level_ups: [{ skill: "foraging", at: AT + 70 }], tops_out: [], fills: [], empties: [] };

function harness(steps: { decisions: number; at?: number }[], answers: { decisions: number; forecast: Forecast }[]) {
  const asked: number[] = [];
  const step = (decisions: number, at = AT): Step => {
    const s = fixtureStep("mid", at, {}, decisions);
    return { ...s, save_id: 7, rules_digest: fixtureContent.rules_digest };
  };
  let i = 0;
  let j = 0;
  const api: GameApi = {
    content: () => Promise.resolve(fixtureContent),
    me: () => Promise.resolve({ account: null, saves: [], max_saves: 5, kept_days: 30 }),
    begin: () => Promise.resolve({ save: { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 }, presentation: NEW_SAVE, step: step(0) }),
    open: () => Promise.reject(new Error("not here")),
    savedView: () => Promise.reject(new Error("unused")),
    advance: () => {
      const a = steps[i++] ?? { decisions: 0 };
      return Promise.resolve(step(a.decisions, a.at));
    },
    forecast: () => {
      asked.push(j);
      return Promise.resolve(answers[j++] ?? { decisions: 0, forecast: FORECAST });
    },
    decide: () => Promise.reject(new Error("not here")),
    dryRun: () => Promise.resolve(fixtureStep("mid", AT).view),
    putMePresentation: (p) => Promise.resolve({ presentation: p, settings: NEW_SETTINGS, has_words: false, words_due: false }),
    putMeSettings: (settings) => Promise.resolve({ presentation: NEW_ACCOUNT, settings, has_words: false, words_due: false }),
    putSavePresentation: (_id, p) => Promise.resolve(p),
    sendFeedback: () => Promise.resolve(),
    makeCode: () => Promise.reject(new Error("not in these tests")),
    makeWords: () => Promise.reject(new Error("not in these tests")),
    games: () => Promise.reject(new Error("not in these tests")),
    deleteGame: () => Promise.reject(new Error("not in these tests")),
    restoreGame: () => Promise.reject(new Error("not in these tests")),
    devices: () => Promise.reject(new Error("not in these tests")),
    removeDevice: () => Promise.reject(new Error("not in these tests")),
    join: () => Promise.reject(new Error("not in these tests")),
  };
  const none = (): void => undefined;
  const events: SessionEvents = { started: none, stepped: none, build: none, refused: none, connected: none, lost: none, limited: none, catchingUp: none };
  let ms = 0;
  const session = new Session(api, events, undefined, () => Promise.resolve(), () => ms);
  return { session, asked, later: (by: number) => { ms += by; } };
}

{  // the control: after Begin the page asks once, and the answer is drawn on the views that follow
  const h = harness([{ decisions: 0 }], [{ decisions: 0, forecast: FORECAST }]);
  await h.session.begin();
  h.session.tick();
  await h.session.settled();
  check(h.asked.length === 1, `one ask after Begin: ${h.asked.length}`);
  check(JSON.stringify(h.session.view?.forecast) === JSON.stringify(FORECAST), "the answer is drawn at once");
  await h.session.advance();
  check(JSON.stringify(h.session.view?.forecast) === JSON.stringify(FORECAST), "a plain advance keeps drawing it");
  h.later(120_000);
  h.session.tick();
  await h.session.settled();
  check(h.asked.length === 1, `a forecast that holds is not asked for again: ${h.asked.length}`);
}
{  // another page decided: nothing drawn from the held one, then the page asks again
  const h = harness([{ decisions: 2 }], [{ decisions: 0, forecast: FORECAST }, { decisions: 2, forecast: FORECAST }]);
  await h.session.begin();
  h.session.tick();
  await h.session.settled();
  await h.session.advance();
  check(h.session.view?.forecast === null, "a held forecast is not drawn on a save with other decisions");
  h.later(120_000);
  h.session.tick();
  await h.session.settled();
  check(h.asked.length === 2 && JSON.stringify(h.session.view?.forecast) === JSON.stringify(FORECAST), "then the page asks, and draws it");
}
{  // near its horizon the page asks afresh
  const h = harness([{ decisions: 0, at: FORECAST.horizon_at - 600 }], [{ decisions: 0, forecast: FORECAST }]);
  await h.session.begin();
  h.session.tick();
  await h.session.settled();
  await h.session.advance();
  h.later(120_000);
  h.session.tick();
  await h.session.settled();
  check(h.asked.length === 2, `within an hour of the horizon the page asks afresh: ${h.asked.length}`);
}
{  // a 20-minute horizon: held until half of it has passed
  const short: Forecast = { ...FORECAST, horizon_at: AT + 1200 };
  const h = harness([{ decisions: 0, at: AT + 500 }, { decisions: 0, at: AT + 700 }], [{ decisions: 0, forecast: short }, { decisions: 0, forecast: short }]);
  await h.session.begin();
  h.session.tick();
  await h.session.settled();
  await h.session.advance();
  h.later(120_000);
  h.session.tick();
  await h.session.settled();
  check(h.asked.length === 1, `700 s of 1200 left is more than half: not asked again: ${h.asked.length}`);
  await h.session.advance();
  h.later(120_000);
  h.session.tick();
  await h.session.settled();
  check(h.asked.length === 2, `500 s of 1200 left is under half: asked afresh: ${h.asked.length}`);
}
