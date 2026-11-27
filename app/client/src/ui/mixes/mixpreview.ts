// The mix editor's forecast requests (editor.ts): at most one in flight and one per PREVIEW_MS, so a drag that never
// pauses still sees its numbers move. An answer is shown when it lands and the next is asked for if the edit moved on;
// a null answer (a failed or refused request) is shown as unknown and asked again after RETRY_MS.
import type { Decision, View } from "../../api/types";

const PREVIEW_MS = 150;
const RETRY_MS = 2000;

export class MixPreview {
  /** The last request got no answer: the totals say so. */
  unknown = false;
  /** Counts openings, so an answer for an edit that has since been closed or replaced is dropped. */
  private seq = 0;
  private timer = 0;
  private flying = false;
  private stale = false;

  /** `decisions` is the edit as it stands, null when there is nothing to preview; `shown` draws an answer. */
  constructor(
    private readonly decisions: () => Decision[] | null,
    private readonly dryRun: (decisions: Decision[]) => Promise<View | null>,
    private readonly shown: (after: View | null) => void,
  ) {}

  /** A new edit opened, or the editor closed: answers still on their way are dropped. */
  reset(): void {
    this.seq++;
    this.unknown = false;
  }

  schedule(): void {
    this.stale = true;
    if (this.timer || this.flying) return;
    this.timer = window.setTimeout(() => { this.timer = 0; void this.ask(); }, PREVIEW_MS);
  }

  private async ask(): Promise<void> {
    const decisions = this.decisions();
    if (!decisions) return;
    this.stale = false;
    this.flying = true;
    const seq = this.seq;
    const after = await this.dryRun(decisions);
    this.flying = false;
    if (seq !== this.seq) return;
    this.unknown = after === null;
    this.shown(after);
    if (this.unknown) this.timer = window.setTimeout(() => { this.timer = 0; void this.ask(); }, RETRY_MS);
    else if (this.stale) this.schedule();
  }
}
