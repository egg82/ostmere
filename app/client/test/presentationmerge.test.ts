// What the page keeps about the player only grows, so a keep sends the page's copy and adopts the merged copy the
// server answers (api/CONTRACT.txt, AccountPresentation and SavePresentation): another page's keep is seen from the next
// keep on, and a keep made while a send was in flight is not lost to its answer. A lesson's keeps go to the save's.
import type { Account, AccountPresentation, NewSave, SavePresentation } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { GameApi } from "../src/api/api";
import { NEW_ACCOUNT, NEW_SAVE, NEW_SETTINGS, type Keeps } from "../src/game/keeps";
import { Session } from "../src/game/session";

const none = (): Promise<never> => Promise.reject(new Error("not in this test"));
const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };
const first = { ...fixtureStep("standing", 100, {}, 0), save_id: 7, rules_digest: fixtureContent.rules_digest, lines: [] };
const account = (presentation: AccountPresentation): Account => ({ presentation, settings: NEW_SETTINGS, has_words: false, words_due: false });

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

async function rig(answer: (sent: AccountPresentation) => Promise<Account>, answerSave = (s: SavePresentation) => Promise.resolve(s)) {
  const sent: AccountPresentation[] = [];
  const saves: [number, SavePresentation][] = [];
  const api: GameApi = {
    content: () => Promise.resolve(fixtureContent), me: none, begin: () => Promise.resolve<NewSave>({ save, presentation: NEW_SAVE, step: first }), open: none,
    savedView: none, advance: none, forecast: none, decide: none, dryRun: none, sendFeedback: none, makeCode: none, makeWords: none, join: none,
    games: none, deleteGame: none, restoreGame: none, devices: none, removeDevice: none,
    putMePresentation: (p) => { sent.push(p); return answer(p); },
    putMeSettings: none,
    putSavePresentation: (id, p) => { saves.push([id, p]); return answerSave(p); },
  };
  let keeps: Keeps | null = null;
  const session = new Session(api, {
    started(_content, _step, k) { keeps = k; }, stepped() { /* drawn */ }, build() { /* self-update */ }, refused() { /* none */ },
    connected() { /* none */ }, lost() { /* none */ }, limited() { /* none */ }, catchingUp() { /* none */ },
  });
  await session.begin();
  if (!keeps) throw new Error("the session never started");
  return { keeps: keeps as Keeps, sent, saves };
}

const settled = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 5));

{  // another page's keep, in the answer, is the page's from then on and is sent with its next keep
  const theirs: AccountPresentation = { ...NEW_ACCOUNT, ledger_lines: ["wood"] };
  const run = await rig((p) => Promise.resolve(account({ ...p, ledger_lines: [...new Set([...(p.ledger_lines ?? []), ...(theirs.ledger_lines ?? [])])] })));
  run.keeps.keepRulesOpened();
  await settled();
  check(run.keeps.ledgerShown("wood"), "the merged copy was not adopted");
  run.keeps.keepDevicesOpened();
  await settled();
  check(JSON.stringify(run.sent[1]?.ledger_lines) === '["wood"]', `the next keep sent ${JSON.stringify(run.sent[1]?.ledger_lines)}`);
}
{  // a keep made while a send is in flight survives the earlier send's answer, which cannot hold it
  let release: (a: Account) => void = () => undefined;
  const run = await rig((p) => (p.rules_opened ? new Promise<Account>((r) => { release = r; }) : Promise.resolve(account(p))));
  run.keeps.keepRulesOpened();
  run.keeps.keepDevicesOpened();
  release(account({ ...NEW_ACCOUNT, rules_opened: true }));
  await settled();
  check(run.keeps.devicesOpened() && run.keeps.rulesOpened(), "a keep made in flight was lost to an older answer");
}
{  // a lesson kept goes to the save it was played in, not the account, and the save's answer is adopted the same way
  const run = await rig(() => Promise.resolve(account(NEW_ACCOUNT)), (p) => Promise.resolve({ ...p, mix_offered: ["look"] }));
  run.keeps.keepLesson({ lesson: "first_mix", skipped: false, step: 6, longest_wait_s: 3 });
  await settled();
  check(run.sent.length === 0, `a lesson wrote the account: ${JSON.stringify(run.sent)}`);
  check(JSON.stringify(run.saves.map(([id, p]) => [id, p.lessons])) === '[[7,["first_mix"]]]', `the save got ${JSON.stringify(run.saves)}`);
  check(run.keeps.mixOffered("look"), "the save's merged copy was not adopted");
}
