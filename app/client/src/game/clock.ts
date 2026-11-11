// The page's clock and the one sampling rule CONTRACT.txt allows. Nothing here knows a game rule: a segment is read
// at a time, and never past view.next_event_at, where the server has to be asked again.
import type { Segment, View } from "../api/types";

/** value = start_value + rate * (t - start), held at limit once reached (from either side). */
export function sample(segment: Segment, t: number): number {
  const v = segment.start_value + segment.rate * (t - segment.start);
  const limit = segment.limit;
  if (limit === null) return v;
  if (segment.rate > 0) return Math.min(v, limit);
  if (segment.rate < 0) return Math.max(v, limit);
  return v;
}

/** Game seconds, continuous across Steps: started at a new game's view.at, then the page's monotonic clock. */
export class Clock {
  private originMs = 0;
  private originAt = 0;

  constructor(private readonly nowMs: () => number = () => performance.now()) {}

  start(at: number): void {
    this.originMs = this.nowMs();
    this.originAt = at;
  }

  now(): number {
    return this.originAt + (this.nowMs() - this.originMs) / 1000;
  }

  /** The `at` to send: whole seconds, never before the view the state was drawn at. */
  at(view: View): number {
    return Math.max(view.at, Math.floor(this.now()));
  }

  /** The time to sample the view at: now, held at next_event_at until the next Step arrives. */
  sampleTime(view: View): number {
    const t = Math.max(view.at, this.now());
    return view.next_event_at === null ? t : Math.min(t, view.next_event_at);
  }

  due(view: View): boolean {
    return view.next_event_at !== null && this.now() >= view.next_event_at;
  }
}
