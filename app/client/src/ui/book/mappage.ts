// The Book's Map page (contract/map.txt, "MAP"; docs/decisions.md, "A world map"): the town and the places found so far on
// one sheet, north up, each an engraved stamp (the town's warm, the rest cool) with its name in clear space beside it, and
// the named places listed beside the sheet (under it on a phone), so no name needs a hover. Offered only once a place is
// revealed. The stamps' manifest is fetched when the page is first offered; the layout is game/book/maplayout.ts's, redrawn
// when the sheet's size changes. Nothing here sends anything.
import type { View } from "../../api/types";
import { frameOf, placeLabels, stampBoxes, type Box, type Cell, type Frame } from "../../game/book/maplayout";
import { HOME, labelKey, revealed, stampPicks, type StampArt, type StampManifest } from "../../game/book/mapsheet";
import { UI } from "../../game/page/text";
import { reportError } from "../../telemetry";
import type { Book } from "./book";
import { el } from "../dom";
import { markNew } from "../feedback/fresh";
import type { Part, PartContext } from "../part";

const STAMPS = "/assets/art/map/";
/** A cell's largest side, in root ems: a big screen shows more of the world, not bigger stamps. */
const MAX_CELL_EM = 6;
/** The room a spot with no art keeps for its label to sit beside. */
const UNDRAWN: StampArt = { src: "", w: 24, h: 24 };
/** How far out a label is tried from its stamp, in root ems, nearest first. */
const GAPS_EM = [0.3, 1, 2];

/** One spot on the sheet: the town (id HOME) or a revealed place. */
interface Spot { id: string; at: Cell; label: string; over: string | null }

export class MapPage implements Part {
  readonly id = "map";
  readonly label: string;
  readonly root = el("section", "map-page");
  private readonly sheet = el("div", "map-sheet");
  private readonly stamps = el("div", "map-stamps");
  private readonly labels = el("div", "map-labels");
  private readonly list = el("ol", "map-list");
  private readonly button: HTMLButtonElement;
  private manifest: StampManifest | null = null;
  private loading = false;
  private reported = false;
  private readonly loaded = new Set<string>();
  private spots: Spot[] = [];
  private marked: string | null = null;
  /** The ring round the marked place, and each spot's box from the last draw. */
  private readonly ring = el("i", "map-ring");
  private boxes = new Map<string, Box>();

  constructor(private readonly ctx: PartContext, private readonly book: Book) {
    this.label = ctx.catalog.text.get(UI.bookMap);
    this.stamps.setAttribute("aria-hidden", "true");
    this.labels.setAttribute("aria-hidden", "true");   // the list says the same, as text a reader reaches
    this.sheet.append(this.stamps, this.labels);
    const places = el("div", "map-places");
    places.append(el("h3", "map-heading", ctx.catalog.text.get(UI.mapHeading)), this.list);
    this.root.append(this.sheet, places);
    this.button = book.page(this);
    this.button.hidden = true;
    new ResizeObserver(() => this.draw()).observe(this.sheet);
  }

  update(view: View, prev: View | null): void {
    const { catalog } = this.ctx;
    const shown = revealed(catalog, view);
    this.button.hidden = shown.length === 0;
    if (shown.length === 0) { delete this.button.dataset["teach"]; return; }
    this.button.dataset["teach"] = "map";   // the map's lesson starts on it (game/lessons/lessons.ts)
    if (!this.loading) this.load();
    if (prev !== null && revealed(catalog, prev).length < shown.length) markNew(this.book.tab, () => undefined);
    const spots = [{ id: HOME, at: { east: 0, north: 0 }, label: catalog.townTitle(view), over: null },
      ...shown.map((p) => { const key = labelKey(catalog, view, p); return { id: p.place, at: { east: p.east, north: p.north }, label: key ? catalog.text.get(key) : "", over: p.over }; })];
    if (JSON.stringify(spots) === JSON.stringify(this.spots)) return;
    this.spots = spots;
    this.fillList();
    this.draw();
  }

  tick(): void {}

  turnedTo(): void {
    this.draw();
  }

  turnedFrom(): void {
    this.mark(null);
  }

  private load(): void {
    this.loading = true;
    fetch(`${STAMPS}manifest.json`)
      .then((r) => (r.ok ? r.json() as Promise<StampManifest> : Promise.reject(new Error(`status ${r.status}`))))
      .then((m) => { this.manifest = m; this.draw(); })
      .catch((e: unknown) => this.report(`map stamps manifest failed to load: ${String(e)}`));
  }

  private report(message: string): void {
    if (this.reported) return;
    this.reported = true;
    reportError("error", message, "map");
  }

  /** The named spots, the town first, each a row whose tap marks its place on the sheet. */
  private fillList(): void {
    this.list.replaceChildren(...this.spots.filter((s) => s.label).map((s) => {
      const row = el("li");
      const pick = el("button", s.id === HOME ? "map-row home" : "map-row", s.label);
      pick.type = "button";
      pick.dataset["place"] = s.id;
      pick.addEventListener("click", () => this.mark(this.marked === s.id ? null : s.id));
      row.append(pick);
      return row;
    }));
    this.mark(this.spots.some((s) => s.id === this.marked) ? this.marked : null);
  }

  private mark(id: string | null): void {
    this.marked = id;
    for (const n of Array.from(this.root.querySelectorAll<HTMLElement>("[data-place]"))) {
      const on = n.dataset["place"] === id;
      n.classList.toggle("marked", on);
      if (n.matches("button")) n.setAttribute("aria-pressed", String(on));
    }
    const box = id === null ? undefined : this.boxes.get(id);
    this.ring.hidden = !box;
    if (box) {
      const r = Math.max(box.w, box.h) / 2 + 6;
      this.ring.style.cssText = `left:${box.x + box.w / 2 - r}px;top:${box.y + box.h / 2 - r}px;width:${2 * r}px;height:${2 * r}px`;
    }
  }

  private draw(): void {
    const w = this.sheet.clientWidth, h = this.sheet.clientHeight;
    if (this.root.hidden || this.spots.length === 0 || !(w > 0) || !(h > 0)) return;
    const rem = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
    const frame = frameOf(this.spots.map((s) => s.at), w, h, MAX_CELL_EM * rem);
    const boxes = this.drawStamps(frame);
    this.drawLabels(boxes, w, h, GAPS_EM.map((g) => g * rem));
    this.mark(this.marked);
  }

  /** Each spot's stamp (none until the manifest is in, or for a kind it has no art for), and the box its label sits
   * beside: the stamp's, else a small square on its cell. */
  private drawStamps(frame: Frame): Map<string, Box> {
    const places = this.ctx.catalog.content.places;
    const picks = this.manifest ? stampPicks(this.ctx.saveId(), places, this.manifest) : new Map();
    const boxes = stampBoxes(new Map(this.spots.map((s) => [s.id, { art: picks.get(s.id) ?? UNDRAWN, at: s.at, over: s.over }])), frame);
    const nodes: HTMLElement[] = [];
    for (const s of [...this.spots].sort((a, b) => Number(a.over !== null) - Number(b.over !== null))) {
      const art = picks.get(s.id), box = boxes.get(s.id)!;
      if (!art) continue;
      this.preload(art.src);
      if (s.over !== null) {   // a stamp on a stamp: its own patch of the ground beneath it keeps the two engravings apart
        const knock = el("i", "map-knock");
        const pad = Math.max(box.w, box.h) * 0.12;
        knock.style.cssText = `left:${box.x - pad}px;top:${box.y - pad}px;width:${box.w + 2 * pad}px;height:${box.h + 2 * pad}px`;
        nodes.push(knock);
      }
      const node = el("i", s.id === HOME ? "map-stamp home" : "map-stamp");
      node.dataset["place"] = s.id;
      node.style.cssText = `left:${box.x}px;top:${box.y}px;width:${box.w}px;height:${box.h}px;--art:url("${STAMPS}${art.src}")`;
      nodes.push(node);
    }
    this.stamps.replaceChildren(...nodes, this.ring);
    this.boxes = boxes;
    return boxes;
  }

  /** A stamp is drawn as a CSS mask, which says nothing when its image fails: the image is fetched once beside it. */
  private preload(src: string): void {
    if (this.loaded.has(src)) return;
    this.loaded.add(src);
    const img = new Image();
    img.addEventListener("error", () => this.report(`map stamp failed to load: ${src}`));
    img.src = `${STAMPS}${src}`;
  }

  /** Each named spot's label, measured and then put beside its stamp in clear space, or left off the sheet. */
  private drawLabels(boxes: Map<string, Box>, w: number, h: number, gaps: number[]): void {
    const named = this.spots.filter((s) => s.label);
    const nodes = named.map((s) => {
      const node = el("span", s.id === HOME ? "map-label home" : "map-label", s.label);
      node.dataset["place"] = s.id;
      return node;
    });
    this.labels.replaceChildren(...nodes);
    const spots = placeLabels(named.map((s, i) => ({ id: s.id, beside: boxes.get(s.id)!, w: nodes[i]!.offsetWidth + 1, h: nodes[i]!.offsetHeight })),
      [...boxes.values()], w, h, gaps);
    named.forEach((s, i) => {
      const at = spots.get(s.id), node = nodes[i]!;
      node.hidden = !at;
      if (at) node.style.cssText = `left:${at.x}px;top:${at.y}px`;
    });
  }
}
