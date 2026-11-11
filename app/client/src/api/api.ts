// The game API (app/ashfall_app/api/CONTRACT.txt) behind one narrow interface, so the page runs against the real
// server or a fixture (fixtures/fixture-api.ts) without knowing which. The server holds the game; the browser's
// session cookie names the account, so nothing here carries a state.
import { reportError, stepHeaders } from "../telemetry";
import type {
  Account, AccountPresentation, AccountSettings, ApiError, Content, Decision, Devices, ErrorCode, FeedbackRequest, ForecastAnswer, Games, JoinWay, Joined,
  MergeSummary, Me, NewSave, Opened, RecoveryWords, SavePresentation, Step, TransferCode, View,
} from "./types";

export interface GameApi {
  content(): Promise<Content>;
  /** Who this browser is, with its saves (the most recently played first). Never makes an account. */
  me(): Promise<Me>;
  /** A new save (and the account, for a browser with none). */
  begin(): Promise<NewSave>;
  /** The save as last seen, its last lines, and the save advanced to now. */
  open(saveId: number): Promise<Opened>;
  advance(saveId: number): Promise<Step>;
  /** The save as last written, at its own time, not advanced; nothing is written (the front page's picture of a save's camp). */
  savedView(saveId: number): Promise<View>;
  /** The save advanced to now and what lands from there if the player changes nothing (CONTRACT.txt, "Forecast"). */
  forecast(saveId: number): Promise<ForecastAnswer>;
  /** `after`: the Step.decisions the page last saw (409 stale when another page decided since). */
  decide(saveId: number, decision: Decision, after: number): Promise<Step>;
  /** The view after these decisions, applied now; nothing is written (the mix editor's "after" totals). */
  dryRun(saveId: number, decisions: Decision[]): Promise<View>;
  putMePresentation(presentation: AccountPresentation): Promise<Account>;
  /** Replaces the player's settings for every game of the account. */
  putMeSettings(settings: AccountSettings): Promise<Account>;
  /** Adds to what the save keeps about its teaching; answers what it keeps now. */
  putSavePresentation(saveId: number, presentation: SavePresentation): Promise<SavePresentation>;
  /** A tester's words, with the save they were playing (null: none). Resolves once the server has kept them. */
  sendFeedback(text: string, saveId: number | null): Promise<void>;
  /** A code (and its QR) that joins another browser to this account, once, for ten minutes. */
  makeCode(): Promise<TransferCode>;
  /** New recovery words; the old ones stop working. */
  makeWords(): Promise<RecoveryWords>;
  /** This browser joins the account a code or words name (CONTRACT.txt, "Moving to another device"); `way`, other than
   * plain only after the player chose it: "move" moves this browser's own games into that account, "keep" leaves them
   * on their old one. */
  join(typed: string, way: JoinWay): Promise<Joined>;
  /** The account's saves, live and deleted (CONTRACT.txt, "Games on one account"). */
  games(): Promise<Games>;
  /** Deletes a live save that is not the account's only one; it is held and can be restored. */
  deleteGame(saveId: number): Promise<Games>;
  restoreGame(saveId: number): Promise<Games>;
  /** The account's browsers, this one first (CONTRACT.txt, "Your devices"). */
  devices(): Promise<Devices>;
  /** Signs one browser out; the answer lists what is left. Removing this browser ends its session too. */
  removeDevice(deviceId: number): Promise<Devices>;
}

/** A request the server answered with an ApiError body, or one that never got an answer (code "network"). "server_error":
 * the app itself answered a 5xx with no ApiError body (its unhandled error), as the X-Ashfall-Server header says. `step`:
 * the save now, with stale. `retryAfterS`: a 503's Retry-After. `merge`: what a join would bring together. */
export class ApiFailure extends Error {
  constructor(
    readonly code: ErrorCode | "network" | "server_error", message: string, readonly step: Step | null = null,
    readonly retryAfterS: number | null = null, readonly merge: MergeSummary | null = null,
  ) {
    super(message);
  }
}

/** Worth asking again: the server or the network will likely answer later (a deploy, a pod restarting). */
export function retryable(e: unknown): e is ApiFailure {
  return e instanceof ApiFailure && (e.code === "network" || e.code === "save_unavailable");
}

/** The app answered, and failed: worth asking again only a few times, since it may fail the same way every time. */
export function appFault(e: unknown): e is ApiFailure {
  return e instanceof ApiFailure && e.code === "server_error";
}

/** A request with no answer by now is given up as "network", which the session asks again behind the reconnecting
 * state (a tunnel or proxy with no ready app can hold a connection open without answering). The slowest call answers in
 * well under a second; this is wide of that. */
export const REQUEST_TIMEOUT_MS = 10_000;

async function call<T>(path: string, init: RequestInit): Promise<T> {
  return (await request(path, init)).json() as Promise<T>;
}

/** The answer to a request that succeeded; an ApiFailure for any other. */
export async function request(path: string, init: RequestInit): Promise<Response> {
  let response: Response;
  const abort = new AbortController();
  const timer = setTimeout(() => abort.abort(), REQUEST_TIMEOUT_MS);
  try {
    response = await fetch(path, { credentials: "same-origin", signal: abort.signal, ...init });
  } catch (e) {
    reportRequest(path, init, "no answer: " + String(e));
    throw new ApiFailure("network", String(e));
  } finally {
    clearTimeout(timer);
  }
  if (response.ok) return response;
  if (response.status >= 500 && response.status !== 503) reportRequest(path, init, `status ${response.status}`);
  const body = (await response.json().catch(() => null)) as Partial<ApiError> | null;
  const retry = Number(response.headers.get("Retry-After") ?? "NaN");
  const unanswered = response.status >= 500 && response.headers.get("X-Ashfall-Server") === "app" ? "server_error" : "network";
  throw new ApiFailure(body?.code ?? unanswered, `${response.status} ${body?.message ?? response.statusText}`,
    body?.step ?? null, Number.isFinite(retry) ? retry : null, body?.merge ?? null);
}

/** A request that failed to send or came back 5xx, with the route and the decision's kind (never its content). */
function reportRequest(path: string, init: RequestInit, message: string): void {
  let decision = "none";
  try {
    const sent = JSON.parse(String(init.body ?? "null")) as { decision?: { kind?: string } | null } | null;
    decision = sent?.decision?.kind ?? "none";
  } catch { /* no body */ }
  reportError("request", message, "", { route: path.replace(/\/\d+(\/|$)/, "/{id}$1"), decision });
}

const JSON_HEADERS = { "Content-Type": "application/json" } as const;
const post = (body?: unknown, headers: Record<string, string> = {}): RequestInit => ({
  method: "POST", headers: { ...JSON_HEADERS, ...headers }, body: body === undefined ? undefined : JSON.stringify(body),
});
const put = (body: unknown): RequestInit => ({ method: "PUT", headers: JSON_HEADERS, body: JSON.stringify(body) });
const save = (id: number, what: string): string => `/api/saves/${id}/${what}`;

export const httpApi: GameApi = {
  content: () => call<Content>("/api/content", { method: "GET" }),
  me: () => call<Me>("/api/me", { method: "GET" }),
  begin: () => call<NewSave>("/api/saves", post()),
  open: (id) => call<Opened>(save(id, "open"), post(undefined, stepHeaders(null))),
  advance: (id) => call<Step>(save(id, "advance"), post(undefined, stepHeaders(null))),
  forecast: (id) => call<ForecastAnswer>(save(id, "forecast"), post()),
  decide: (id, decision, after) => call<Step>(save(id, "decisions"), post({ decision, after }, stepHeaders(decision))),
  savedView: (id) => call<View>(save(id, "view"), { method: "GET" }),
  dryRun: (id, decisions) => call<View>(save(id, "dry-run"), post({ decisions })),
  putMePresentation: (presentation) => call<Account>("/api/me/presentation", put(presentation)),
  putMeSettings: (settings) => call<Account>("/api/me/settings", put(settings)),
  putSavePresentation: (id, presentation) => call<SavePresentation>(save(id, "presentation"), put(presentation)),
  sendFeedback: async (text, saveId) => { await request("/api/feedback", post({ text, save_id: saveId } satisfies FeedbackRequest)); },
  makeCode: () => call<TransferCode>("/api/me/transfer-code", post()),
  makeWords: () => call<RecoveryWords>("/api/me/words", post()),
  join: (typed, way) => call<Joined>("/api/join", post({ typed, merge: way === "move", keep: way === "keep" })),
  games: () => call<Games>("/api/saves", { method: "GET" }),
  deleteGame: (id) => call<Games>(save(id, "delete"), post()),
  restoreGame: (id) => call<Games>(save(id, "restore"), post()),
  devices: () => call<Devices>("/api/me/devices", { method: "GET" }),
  removeDevice: (id) => call<Devices>(`/api/me/devices/${id}`, { method: "DELETE" }),
};
