// What the page tells the server and Umami about itself, and nothing else: pageviews, five kinds of event, client
// errors, and where the player left. Ids, counts and durations only; never the state string or any text the player
// sees. Every call is a silent no-op when the config is missing, the tracker is blocked, or a report fails to send.
// Server side: ashfall_app/page_config.py (the config) and client_errors.py (the reports).

import type { Decision } from "./api/types";

interface UmamiConfig { script_url: string; website_id: string }
interface PageConfig { version: string; umami: UmamiConfig | null }
type Umami = { track(event: string | ((p: Record<string, unknown>) => Record<string, unknown>), data?: Record<string, unknown>): void };
declare global { interface Window { umami?: Umami } }   // set by the tracker script once it loads
type Kind = "error" | "rejection" | "request" | "leave";

const REPORT_URL = "/api/client-errors";
const MAX_REPORTS = 10;   // per page load, errors; the leave beacon has its own count
const MAX_LEAVES = 10;
const CUT = 300;

let version = "";
let beganAt: number | null = null;
let lastDecisionAt: number | null = null;
let decisions = 0;
let gameTime = 0;
let lastCard: string | null = null;
let reachedEnd = 0;
let reports = 0;
let leaves = 0;
let leftSent = false;   // this leave has been reported; the page coming back to the front re-arms it
const milestones = new Set<string>();

const seconds = (from: number | null): number | null => (from === null ? null : Math.max(0, Math.round((performance.now() - from) / 1000)));
const umami = (): Umami | undefined => window.umami;

function send(body: object, beacon: boolean): void {
  try {
    const json = JSON.stringify(body);
    if (beacon && navigator.sendBeacon) {
      navigator.sendBeacon(REPORT_URL, new Blob([json], { type: "application/json" }));
    } else {
      void fetch(REPORT_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: json, keepalive: true }).catch(() => undefined);
    }
  } catch { /* a failed report is dropped */ }
}

export function reportError(kind: Exclude<Kind, "leave">, message: string, source: string, request?: { route: string; decision: string }): void {
  if (reports >= MAX_REPORTS) return;
  reports += 1;
  send({
    kind, message: message.slice(0, CUT), source: source.slice(0, CUT), version,
    route: request?.route, decision: request?.decision, since_begin_s: seconds(beganAt),
  }, false);
}

function topFrame(e: unknown): string {
  const frame = e instanceof Error ? /\(?([^\s()]+:\d+):\d+\)?\s*$/m.exec((e.stack ?? "").split("\n").slice(1).join("\n")) : null;
  return frame?.[1] ?? "";
}

/** A close fires visibilitychange (hidden) and then pagehide: one report per leave, re-armed when the page is shown again. */
function sendLeave(): void {
  if (beganAt === null || leaves >= MAX_LEAVES || leftSent) return;
  leftSent = true;
  leaves += 1;
  send({
    kind: "leave", version, since_begin_s: seconds(beganAt), game_time: Math.round(gameTime), last_project: lastCard,   // the server's field name; it holds a card id
    decisions, reached_end: reachedEnd,
  }, true);
}

function trackPageview(): void {
  try {
    umami()?.track((p) => ({ ...p, url: "/" }));   // one view; the path is fixed, the query and fragment never leave
  } catch { /* tracking never breaks the page */ }
}

function loadTracker(cfg: UmamiConfig | null): void {
  if (!cfg?.script_url || !cfg.website_id) return;   // off means off
  const script = document.createElement("script");
  script.src = cfg.script_url;
  script.async = true;
  script.setAttribute("data-website-id", cfg.website_id);
  script.setAttribute("data-auto-track", "false");
  script.setAttribute("data-do-not-track", "true");
  script.setAttribute("data-exclude-hash", "true");
  script.setAttribute("data-exclude-search", "true");
  script.addEventListener("load", trackPageview);
  document.head.appendChild(script);
}

/** Once, from main.ts: handlers first (they need no config), then the config for the version and the tracker. */
export function initTelemetry(): void {
  window.addEventListener("error", (ev) => {
    reportError("error", ev.message, ev.filename ? `${ev.filename.split("/").pop()}:${ev.lineno}` : topFrame(ev.error));
  });
  window.addEventListener("unhandledrejection", (ev) => {
    const reason: unknown = ev.reason;
    reportError("rejection", reason instanceof Error ? reason.message : String(reason), topFrame(reason));
  });
  window.addEventListener("pagehide", sendLeave);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") sendLeave();
    else leftSent = false;
  });
  void fetch("/page-config.json").then((r) => (r.ok ? (r.json() as Promise<PageConfig>) : null)).then((cfg) => {
    if (!cfg) return;
    version = cfg.version;
    loadTracker(cfg.umami);
  }).catch(() => undefined);
}

function event(name: string, data?: Record<string, unknown>): void {
  try {
    umami()?.track(name, data);
  } catch { /* tracking never breaks the page */ }
}

export function noteBegin(): void {
  beganAt = performance.now();
  event("preview_begin");
}

const ordersShown = new Set<string>();

/** True the first time (per page load) this store's inline order card is shown; sends the event then. */
export function noteOrderShown(store: string): boolean {
  if (ordersShown.has(store)) return false;
  ordersShown.add(store);
  event("preview_order_shown");
  return true;
}

export function noteOrderSet(): void {
  event("preview_order_set");
}

export function noteOrderRemoved(): void {
  event("preview_order_removed");
}

/** A rule reordered or pointed at another mix. */
export function noteRuleChanged(): void {
  event("preview_rule_changed");
}

/** A Games sheet action: a new game, a switch, a delete or a restore, with the save's id. */
export function noteGame(action: "new" | "switch" | "delete" | "restore", saveId: number): void {
  event(`game_${action}`, { save: saveId });
}

export function noteEnd(): void {
  reachedEnd = 1;
  event("preview_end");
}

/** Called when a decision is about to be sent; the headers carry the timing the server logs. */
export function stepHeaders(decision: Decision | null): Record<string, string> {
  const isDecision = decision !== null;
  const headers: Record<string, string> = {};
  const wall = seconds(beganAt);
  if (wall !== null) headers["X-Ashfall-Wall"] = String(wall);
  if (isDecision) {
    const gap = seconds(lastDecisionAt);
    if (gap !== null) headers["X-Ashfall-Gap"] = String(gap);
    lastDecisionAt = performance.now();
    decisions += 1;
    if (decision.kind === "tap_card") lastCard = decision.card;   // the last card actually tapped
  }
  return headers;
}

/** After each step: the game clock for the leave beacon, and any one-off card that has just first completed. */
export function noteProgress(at: number, completed: readonly string[]): void {
  gameTime = at;
  for (const id of completed) {
    if (milestones.has(id)) continue;
    milestones.add(id);
    event("preview_step", { milestone: id });
  }
}
