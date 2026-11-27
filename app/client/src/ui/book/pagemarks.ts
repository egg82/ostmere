// The marks layer over a journal page (docs/design/journal.md, "Marks on the page"): it loads the marks' manifest
// once, when the journal is made (so turning to a page sends nothing, as contract/'s JOURNAL asks), measures the
// words, headings and drawings the page shows, and draws each mark game/pagemarks.ts places. It is redrawn when the page
// is, when the fonts arrive and when its size changes, since a place depends on where the words lie. A manifest or an
// image that fails to load draws no marks and is reported once.
import { placeMarks, type Box, type MarkManifest, type Wanted } from "../../game/book/pagemarks";
import { reportError } from "../../telemetry";
import { el } from "../dom";

const MARKS = "/assets/journal/marks/";
/** What a mark keeps clear of; the words are measured line by line, so the room beside a short line stays open. */
const BLOCKS = ".journal-day, .journal-sketch, .journal-note-sketch, .journal-numbers:not([hidden])";

export class PageMarks {
  readonly layer = el("div", "journal-marks");
  private manifest: MarkManifest | null = null;
  private reported = false;
  private wanted: readonly Wanted[] = [];

  /** `page`: the element whose words, headings and drawings the marks keep clear of. */
  constructor(private readonly page: HTMLElement) {
    this.layer.setAttribute("aria-hidden", "true");
    new ResizeObserver(() => this.draw()).observe(this.layer);
    document.fonts?.addEventListener("loadingdone", () => this.draw());   // the hand's face arriving moves every line
    // a drawing arriving moves the words beside and below it; a mark's own image moves nothing
    page.addEventListener("load", (e) => { if (!this.layer.contains(e.target as Node)) this.draw(); }, true);
    this.load();
  }

  /** Marks the page with `wanted`, once the manifest is in. */
  show(wanted: readonly Wanted[]): void {
    this.wanted = wanted;
    this.draw();
  }

  private load(): void {
    fetch(`${MARKS}manifest.json`)
      .then((r) => (r.ok ? r.json() as Promise<MarkManifest> : Promise.reject(new Error(`status ${r.status}`))))
      .then((m) => { this.manifest = m; this.draw(); })
      .catch((e: unknown) => this.report(`journal marks manifest failed to load: ${String(e)}`));
  }

  private draw(): void {
    const at = this.layer.getBoundingClientRect();
    if (this.manifest === null || at.width === 0 || at.height === 0) return;
    const placed = placeMarks(this.wanted, this.manifest, { w: at.width, h: at.height }, this.blocked(at));
    this.layer.replaceChildren(...placed.map((p) => {
      const img = el("img", `journal-mark mark-${p.kind}`);
      img.alt = "";
      img.addEventListener("error", () => this.report(`journal mark failed to load: ${p.src}`));
      img.src = `${MARKS}${p.src}`;
      const s = img.style;
      // sized unturned and centred in its bounding box, then turned, mirrored and scaled about its centre
      s.width = `${p.w}px`;
      s.height = `${p.h}px`;
      s.left = `${p.box.x + (p.box.w - p.w) / 2}px`;
      s.top = `${p.box.y + (p.box.h - p.h) / 2}px`;
      s.transform = `rotate(${p.angle.toFixed(1)}deg) scale(${p.flipX ? -p.scale : p.scale}, ${p.flipY ? -p.scale : p.scale})`;
      s.opacity = p.opacity.toFixed(2);
      return img;
    }));
  }

  /** The boxes the marks keep clear of, in the layer's own pixels: each line of words, and every heading and drawing. */
  private blocked(at: DOMRect): Box[] {
    const rects: DOMRect[] = [];
    for (const words of Array.from(this.page.querySelectorAll(".journal-words"))) {
      const range = document.createRange();
      range.selectNodeContents(words);
      rects.push(...Array.from(range.getClientRects()));
    }
    for (const b of Array.from(this.page.querySelectorAll(BLOCKS))) rects.push(b.getBoundingClientRect());
    return rects.filter((r) => r.width > 0 && r.height > 0)
      .map((r) => ({ x: r.left - at.left, y: r.top - at.top, w: r.width, h: r.height }));
  }

  private report(message: string): void {
    this.layer.replaceChildren();
    this.manifest = null;
    if (this.reported) return;
    this.reported = true;
    reportError("error", message, "journal");
  }
}
