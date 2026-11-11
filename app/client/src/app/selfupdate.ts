// The page updates itself: each Step names the server's build, and /page-config.json is asked again every few minutes
// while nothing is sent. When the build is not the one this page booted with, the page reloads at a quiet moment
// behind a short fade to its background, and the kept game resumes (the server rebases it: engine DESIGN.txt,
// "Rebase"). Ported from habits' app/src/app/selfupdate.js: the pure decide() first (test/selfupdate.test.ts), then
// the browser wiring.
import { reducedMotion } from "../ui/dom";

export const QUIET_MS = 20_000;   // no pointer, touch or key for this long, once the page has been touched at all
export const BACKOFF_MS = [10 * 60_000, 60 * 60_000];   // a build reloaded for and served again waits this long; then never
export const POLL_MS = 5 * 60_000;
const FADE_MS = 450;
const DOWN_MS = 30_000;   // the page itself did not answer: ask again after this long
const TRIES = "ashfall.update.tries";
const BACK = "ashfall.update.back";   // set just before a self-reload: the page that comes back fades in

export type Decision = "current" | "wait" | "backoff" | "gave-up" | "reload";
export interface Try { at: number; count: number }
export type Tries = Record<string, Try>;

export interface Moment {
  booted: string | null;
  served: string | null;
  tries: Tries;
  now: number;
  idleMs: number;
  interacted: boolean;
  held: boolean;
}

/** `tries` maps a build to the reloads already made for it. */
export function decide({ booted, served, tries, now, idleMs, interacted, held }: Moment): Decision {
  if (!booted || !served || served === booted) return "current";
  const t = tries[served];
  if (t) {   // reloaded for this build before and still not on it (another pod still serving the old one, a stale proxy)
    if (t.count > BACKOFF_MS.length) return "gave-up";
    if (now - t.at < (BACKOFF_MS[t.count - 1] ?? 0)) return "backoff";
  }
  if (held) return "wait";
  if (interacted && idleMs < QUIET_MS) return "wait";
  return "reload";
}

/** The tries with one more for `served`, keeping the eight most recent builds. */
export function counted(tries: Tries, served: string, now: number): Tries {
  const prev = tries[served];
  const next: Tries = { ...tries, [served]: { at: now, count: prev ? prev.count + 1 : 1 } };
  const keep = Object.keys(next).sort((a, b) => (next[b]?.at ?? 0) - (next[a]?.at ?? 0)).slice(0, 8);
  return Object.fromEntries(keep.map((k) => [k, next[k] as Try]));
}

// ---------- the browser ----------

function read<T>(key: string, fallback: T): T {
  try { return (JSON.parse(sessionStorage.getItem(key) ?? "null") as T | null) ?? fallback; } catch { return fallback; }
}

function write(key: string, value: unknown): void {
  try {
    if (value === null) sessionStorage.removeItem(key);
    else sessionStorage.setItem(key, JSON.stringify(value));
  } catch { /* no storage: no memory */ }
}

/** Whether the page is being served this moment: a reload into an error page would leave a tab with no script. */
async function servable(): Promise<boolean> {
  try {
    const r = await fetch(location.href, { cache: "no-store", redirect: "manual", signal: AbortSignal.timeout(10_000) });
    return r.ok || r.type === "opaqueredirect";
  } catch {
    return false;
  }
}

async function servedBuild(): Promise<string | null> {
  try {
    const r = await fetch("/page-config.json", { cache: "no-store" });
    return r.ok ? ((await r.json()) as { version: string }).version : null;
  } catch {
    return null;
  }
}

export class SelfUpdate {
  private booted: string | null = null;
  private served: string | null = null;
  private lastInput = 0;
  private interacted = false;
  private going = false;
  private downUntil = 0;
  private lastSeen = Date.now();

  /** held(): something a reload would cut (an open sheet or editor). */
  constructor(private readonly held: () => boolean) {
    const touch = (): void => { this.lastInput = Date.now(); this.interacted = true; };
    for (const n of ["pointerdown", "pointermove", "keydown", "wheel", "touchstart"]) addEventListener(n, touch, { capture: true, passive: true });
    if (read(BACK, false)) { write(BACK, null); uncover(cover(1)); }
    void servedBuild().then((b) => { this.booted ??= b; this.served ??= b; });
    setInterval(() => this.check(), 5000);   // a quiet moment can come between polls
  }

  /** The build a Step names. */
  seen(build: string): void {
    this.booted ??= build;
    this.served = build;
    this.lastSeen = Date.now();
    this.check();
  }

  private check(): void {
    const now = Date.now();
    if (now - this.lastSeen > POLL_MS) {
      this.lastSeen = now;
      void servedBuild().then((b) => { if (b) this.served = b; });
    }
    if (this.going || now < this.downUntil) return;
    const d = decide({ booted: this.booted, served: this.served, tries: read<Tries>(TRIES, {}), now,
                       idleMs: now - this.lastInput, interacted: this.interacted, held: this.held() });
    if (d === "reload") void this.reload();
  }

  private async reload(): Promise<void> {
    this.going = true;
    if (!(await servable())) { this.going = false; this.downUntil = Date.now() + DOWN_MS; return; }
    const go = (): void => {
      if (this.served) write(TRIES, counted(read<Tries>(TRIES, {}), this.served, Date.now()));
      write(BACK, true);
      location.reload();
    };
    if (reducedMotion() || document.visibilityState !== "visible") { go(); return; }
    const o = cover(0);
    requestAnimationFrame(() => requestAnimationFrame(() => { o.style.opacity = "1"; }));
    setTimeout(() => {   // something opened under the fade: it stays, and the reload waits for the next quiet
      if (this.held()) { uncover(o); this.going = false; } else go();
    }, FADE_MS + 50);
  }
}

/** A sheet of the page's own background over everything: faded in before a self-reload, and out once it is back. */
function cover(opacity: number): HTMLDivElement {
  const o = document.createElement("div");
  const b = getComputedStyle(document.body);
  o.className = "updatecover";
  o.style.cssText = `position:fixed;inset:0;z-index:2147483647;pointer-events:none;transition:opacity ${FADE_MS}ms ease;opacity:${opacity}`;
  o.style.background = b.background || b.backgroundColor;
  document.body.appendChild(o);
  return o;
}

function uncover(o: HTMLDivElement): void {
  requestAnimationFrame(() => requestAnimationFrame(() => { o.style.opacity = "0"; }));
  setTimeout(() => o.remove(), FADE_MS + 50);
}
