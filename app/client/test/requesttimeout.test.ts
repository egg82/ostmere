// A request no server answers is given up after REQUEST_TIMEOUT_MS and shown as reconnecting (src/api/api.ts).
import { httpApi, REQUEST_TIMEOUT_MS } from "../src/api/api";
import { Session, type SessionEvents } from "../src/game/session";

const noop = (): void => undefined;
const seen: boolean[] = [];
const events: SessionEvents = {
  started: noop, stepped: noop, build: noop, refused: noop, lost: noop, limited: noop, catchingUp: noop,
  connected: (ok) => { seen.push(ok); },
};

const delays: number[] = [];
const realSetTimeout = globalThis.setTimeout;
const realFetch = globalThis.fetch;
Object.assign(globalThis, {
  setTimeout: (fn: () => void, ms: number) => {
    delays.push(ms);
    if (ms === REQUEST_TIMEOUT_MS) queueMicrotask(fn);
    return 0;
  },
});
Object.assign(globalThis, {
  fetch: (_path: string, init: RequestInit) => new Promise((_res, rej) => {
    init.signal?.addEventListener("abort", () => rej(new Error("aborted")));
  }),
});

const stalled = new Promise<void>(() => undefined);
const session = new Session(httpApi, events, undefined, () => stalled);
void session.resume(1);
const guard = new Promise<void>((_r, rej) => realSetTimeout(() => rej(new Error("no reconnecting state shown")), 2000));
try {
  await Promise.race([guard, new Promise<void>((r) => { const t = setInterval(() => { if (seen.length) { clearInterval(t); r(); } }, 5); })]);
} finally {
  Object.assign(globalThis, { setTimeout: realSetTimeout, fetch: realFetch });
}
if (seen[0] !== false) throw new Error(`connected(false) expected, got ${JSON.stringify(seen)}`);
if (!delays.includes(REQUEST_TIMEOUT_MS)) throw new Error("no request timer set");
