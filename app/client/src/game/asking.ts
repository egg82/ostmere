// Asking the server until it answers: backoff while it cannot (a deploy, a pod restarting), and the page told it is
// reconnecting for as long as that lasts.
import { appFault, retryable } from "../api/api";

const BACKOFF_MS = [1000, 2000, 4000, 8000, 15000, 30000];
const APP_RETRIES = 3;   // the app's own 5xx is asked again this many times; anything else it cannot answer, without bound

export class Asking {
  private failing = false;

  /** `connected(false)` while a request is being asked again; `connected(true)` once one is answered after that. */
  constructor(private readonly connected: (ok: boolean) => void, private readonly wait: (ms: number) => Promise<void>) {}

  /** `ask` until it is answered, waiting longer each time it cannot be (Retry-After when the server says); the app's
   * own 5xx, which may repeat for ever, is given up after APP_RETRIES. */
  async answered<T>(ask: () => Promise<T>): Promise<T> {
    let appFaults = 0;
    for (let tries = 0; ; tries += 1) {
      try {
        const got = await ask();
        this.reached();
        return got;
      } catch (e) {
        if (appFault(e)) {
          this.reached();
          appFaults += 1;
          if (appFaults > APP_RETRIES) throw e;
        } else {
          if (!retryable(e)) throw e;
          if (!this.failing) this.connected(false);
          this.failing = true;
        }
        const backoff = BACKOFF_MS[Math.min(tries, BACKOFF_MS.length - 1)] ?? 30000;
        await this.wait(Math.max(backoff, (e.retryAfterS ?? 0) * 1000));
      }
    }
  }

  /** The server answered, so the page is no longer reconnecting. */
  private reached(): void {
    if (this.failing) this.connected(true);
    this.failing = false;
  }
}
