// The page's first steps, in the order that matters: a join link's code is taken off the address bar (joinlink.ts)
// before the analytics load (telemetry.ts), then the front page or the game starts with it.
import { httpApi } from "../api/api";
import { wireBegin } from "../begin";
import { initTelemetry } from "../telemetry";
import { takeJoinLink } from "./joinlink";

export interface BootSteps {
  takeJoin(): string | null;
  telemetry(): void;
  begin(join: string | null): void;
}

const REAL: BootSteps = { takeJoin: takeJoinLink, telemetry: initTelemetry, begin: (join) => wireBegin(httpApi, undefined, join) };

export function boot(steps: BootSteps = REAL): void {
  const join = steps.takeJoin();
  steps.telemetry();
  steps.begin(join);
}
