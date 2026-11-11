// The forecast the page holds for its save (CONTRACT.txt, "Forecast"), with the Step.decisions it came with: it holds
// until the save's next decision. Also when a new one is due, so a run of taps costs one ask (game/session.ts).
import type { Forecast, Step } from "../api/types";

/** A held forecast within this of its horizon, or within half of its span if that is less, is asked for afresh. */
const HOUR_S = 3600;
/** A new forecast is asked for only after this long with no decision of the page's own: a run of taps costs one. */
const QUIET_MS = 3000;
/** At most one forecast asked for in this long, whatever the answers (a short horizon must not become a flood). */
const ASK_GAP_MS = 60_000;

export class ForecastHold {
  private forecast: Forecast | null = null;
  private forecastFor: number | null = null;
  private gotAt = 0;
  private lastDecisionMs = -Infinity;
  private lastAskMs = -Infinity;

  constructor(private readonly nowMs: () => number) {}

  /** Another save's future, or one made under other rules: no longer held. */
  drop(): void {
    this.forecast = null;
  }

  /** The page sent a decision of its own. */
  decided(): void {
    this.lastDecisionMs = this.nowMs();
  }

  /** A forecast is being asked for. */
  asked(): void {
    this.lastAskMs = this.nowMs();
  }

  /** The forecast answered, for the save at `decisions`, when the game clock read `at`. */
  got(forecast: Forecast, decisions: number, at: number): void {
    this.forecast = forecast;
    this.forecastFor = decisions;
    this.gotAt = at;
  }

  /** The Step with the forecast held for it, while the save has had no decision since (else none). */
  withForecast(step: Step): Step {
    const holds = this.forecast !== null && this.forecastFor === step.decisions;
    return { ...step, view: { ...step.view, forecast: holds ? this.forecast : null } };
  }

  /** A new forecast is wanted (none held for this plan, or its horizon under an hour or half its span away) and the page has had a
   * quiet few seconds since its own last decision. `clockNow`: the game clock. */
  due(held: Step | null, clockNow: () => number): boolean {
    const now = this.nowMs();
    if (held === null || now - this.lastDecisionMs < QUIET_MS || now - this.lastAskMs < ASK_GAP_MS) return false;
    const f = this.forecast;
    return f === null || this.forecastFor !== held.decisions
      || f.horizon_at - clockNow() < Math.min(HOUR_S, (f.horizon_at - this.gotAt) / 2);
  }
}
