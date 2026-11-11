// The end's moment on the screen: its lines, and when what waits on it may come.
import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { noteEnd } from "../telemetry";

const READ_MS = 20000;   // what waits on the end comes this long after its lines
const RECENT_S = 30;   // an end the page had shown, reloaded within this many game seconds, is replayed; an older one is not

/**
 * The end (CONTRACT.txt, "The end"), keyed on view.ended_at, which the server records once: the end lines go to the
 * log, the scene is at dusk (scene conditions read the same field), and what waits on the end (an after_end order
 * card) comes once the lines have had READ_MS to be read. An end the page had already shown before a reload (set in
 * the first view, which is the kept game at its own time) is replayed the same way only if it happened under RECENT_S
 * game seconds ago; an older one is behind at once. An end that happened while the page was shut or hidden was never
 * shown, so it plays like a live one, whenever it was.
 */
export class TheEnd {
  private handled = false;
  private shownBefore = false;
  /** The end lines are still having their READ_MS. */
  private reading = false;

  constructor(
    private readonly catalog: Catalog, private readonly lines: (keys: string[]) => void,
    private readonly read: () => void = () => undefined,
  ) {}

  /** The end is recorded and its lines have been read, or it is an older end a reopened page does not replay. */
  get behind(): boolean {
    return this.handled && !this.reading;
  }

  update(view: View, first: boolean): void {
    const ended = view.ended_at;
    if (this.handled || ended === null) return;
    if (first) {   // the save as last drawn: the end was shown before. The return's step says how long ago.
      this.shownBefore = true;
      return;
    }
    this.handled = true;
    if (this.shownBefore && view.at - ended > RECENT_S) return;
    if (!this.shownBefore) noteEnd();
    this.lines(this.catalog.content.end_line_keys);
    this.reading = true;
    window.setTimeout(() => { this.reading = false; this.read(); }, READ_MS);
  }
}
