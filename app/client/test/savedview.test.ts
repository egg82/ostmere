// savedView asks for a save's stored view with a GET, which writes nothing; it must not be a POST (api/CONTRACT.txt, ENDPOINTS).
import { httpApi } from "../src/api/api";
import { fixtureStep } from "../fixtures/steps";

const view = fixtureStep("standing", 100, {}, 0).view;
const calls: { path: string; method: string | undefined }[] = [];
const realFetch = globalThis.fetch;
Object.assign(globalThis, {
  fetch: (path: string, init: RequestInit) => {
    calls.push({ path, method: init.method });
    return Promise.resolve(new Response(JSON.stringify(view), { status: 200, headers: { "content-type": "application/json" } }));
  },
});
try {
  const got = await httpApi.savedView(7);
  if (JSON.stringify(got) !== JSON.stringify(view)) throw new Error("the view was not passed through");
} finally {
  Object.assign(globalThis, { fetch: realFetch });
}
const only = calls[0];
if (calls.length !== 1 || only?.path !== "/api/saves/7/view" || only.method !== "GET") throw new Error(`unexpected call ${JSON.stringify(calls)}`);
