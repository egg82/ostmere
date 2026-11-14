// The scene above the game: graded art layers listed by a manifest that is fetched at runtime (licensed art and its
// manifest live on the assets volume, never in git or the bundle). Each layer shows while its `when` holds and its
// `until` does not, fading in and out; a grade (a filter plus an overlay colour) is chosen the same way. This
// module draws; what is true comes from SceneFacts. With no manifest, the game plays with no scene drawn.
// The canvas is the art's own size (manifest.size) and CSS scales it up, pixelated, so the cost of a frame does not
// grow with the window; a frame is drawn only when a layer's fade or the grade's fade is moving.
import type { View } from "../api/types";
import { SceneFacts } from "./conditions";
import { depthOrder, fadeStep, isGlow, isManifest, passOf, pickGrade, gradeStep, type Pass, type SceneLayer, type SceneGrade, type SceneManifest } from "./manifest";
import { COVER, place, type Crop } from "./crop";
import { focusOf } from "./focus";
import { duskWash, lightFilter } from "./light";
import { reducedMotion } from "../ui/dom";

/** Where licensed assets are served; the scene's manifest and layers sit under it. */
export const SCENE_BASE = "/assets/art/scene/";
export const SCENE_MANIFEST = `${SCENE_BASE}manifest.json`;

const FADE_S = 0.8;
/** The frame around the canvas (.scene-frame in game.css): its padding and border, both sides, in CSS px. */
const FRAME_PX = 10;

interface Drawn {
  layer: SceneLayer;
  image: HTMLImageElement;
  alpha: number;
}

export class Scene {
  private readonly facts: SceneFacts;
  private readonly layers: Drawn[];
  private readonly ctx: CanvasRenderingContext2D | null;
  /** The layers composed with no grade; a grade is applied when this is copied to the visible canvas. */
  private readonly base: HTMLCanvasElement;
  private readonly baseCtx: CanvasRenderingContext2D | null;
  private readonly canFilter: boolean;
  /** A second canvas laid over the first, the same size, for the layers that stand in front of the lights (`front`):
   * composed in its own base and graded the same way. */
  private readonly front: HTMLCanvasElement;
  private readonly frontCtx: CanvasRenderingContext2D | null;
  private readonly frontBase: HTMLCanvasElement;
  private readonly frontBaseCtx: CanvasRenderingContext2D | null;
  /** Resolves once every layer's image has loaded (or failed): a still picture is drawn after it. */
  readonly loaded: Promise<void>;
  private crop: Pick<Crop, "hold" | "window"> | null = null;
  private cover = false;   // the box asks to be covered (game.css's --cover: a phone's stage)
  private fixed: [number, number] | null = null;
  private day = 1;
  private gradeId = "";
  private from: SceneGrade | null = null;
  private to: SceneGrade | null = null;
  private fade = 1;
  private baseDirty = true;
  private shownDirty = true;

  constructor(
    private readonly canvas: HTMLCanvasElement,
    private readonly manifest: SceneManifest, base: string, private readonly quantityPerItem: number,
  ) {
    this.facts = new SceneFacts();
    const [w, h] = manifest.size;
    const arrived: Promise<void>[] = [];
    this.layers = depthOrder(manifest.layers).map((layer) => {
      const image = new Image();
      image.decoding = "async";
      arrived.push(new Promise((resolve) => {
        image.onload = () => { this.baseDirty = true; resolve(); };
        image.onerror = () => resolve();
      }));
      image.src = new URL(layer.src, base).href;
      return { layer, image, alpha: 0 };
    });
    this.loaded = Promise.all(arrived).then(() => undefined);
    canvas.width = w;
    canvas.height = h;
    canvas.style.imageRendering = manifest.pixelated === false ? "auto" : "pixelated";
    this.ctx = canvas.getContext("2d");
    this.base = document.createElement("canvas");
    this.base.width = w;
    this.base.height = h;
    this.baseCtx = this.base.getContext("2d");
    this.canFilter = this.ctx !== null && "filter" in this.ctx;
    this.frontBase = document.createElement("canvas");
    this.frontBase.width = w;
    this.frontBase.height = h;
    this.frontBaseCtx = this.frontBase.getContext("2d");
    this.front = document.createElement("canvas");
    this.front.width = w;
    this.front.height = h;
    this.front.className = canvas.className;
    this.front.setAttribute("aria-hidden", "true");
    this.front.style.cssText = "position: absolute; left: 0; top: 0; pointer-events: none;";
    this.front.style.imageRendering = canvas.style.imageRendering;
    this.frontCtx = this.front.getContext("2d");
    canvas.after(this.front);
    const box = canvas.parentElement?.parentElement;
    // Fitting resizes the canvas inside the observed box, so it runs after the observer's pass (in the same pass the
    // browser reports "ResizeObserver loop completed with undelivered notifications").
    const watch = new ResizeObserver(() => requestAnimationFrame(() => this.fit()));
    if (box) watch.observe(box);
    const left = box?.closest(".left");   // the strip's and the head's heights are the art's to give up (roomAbove)
    for (const part of [left?.querySelector(".strip"), left?.querySelector(".scene-head")]) if (part) watch.observe(part);
    this.fit();
  }

  /** The manifest at `url`, or null when it cannot be fetched or is not one (the game plays without a scene). */
  static async load(canvas: HTMLCanvasElement, url: string, quantityPerItem: number): Promise<Scene | null> {
    const found = await Scene.manifest(url);
    return found ? new Scene(canvas, found.manifest, found.base, quantityPerItem) : null;
  }

  /** A manifest fetched once, for any number of scenes drawn from it (the front page's pictures). */
  static async manifest(url: string): Promise<{ manifest: SceneManifest; base: string } | null> {
    try {
      // Revalidated every time: a copy cached under an old policy (assets were once immutable for a year) is never used.
      const response = await fetch(url, { cache: "no-cache" });
      if (!response.ok) return null;
      const manifest: unknown = await response.json();
      if (!isManifest(manifest)) throw new Error("not a scene manifest");
      return { manifest, base: new URL(url, location.href).href };
    } catch (e) {
      console.warn("ashfall: no scene", e);
      return null;
    }
  }

  /** Shows part of the art in a box that clips it (the front page): `focus` of the art held at `hold` of the box. With
   * no focus the part follows what the view shows (focusOf). */
  cropTo(crop: Pick<Crop, "hold" | "window"> & { focus?: [number, number] }): void {
    this.crop = crop;
    this.fixed = crop.focus ?? null;
    this.fit();
  }

  /** How much of the day's light there is (1 is full day, the game's own state): the front page's follows the clock. */
  setLight(day: number): void {
    this.day = day;
    this.shownDirty = true;
  }

  update(view: View): void {
    this.facts.observe(view);
  }

  /** One frame at game time t; dt in seconds since the last frame. Draws only when something moved. */
  draw(t: number, dt: number): void {
    const { ctx, baseCtx, frontCtx, frontBaseCtx } = this;
    if (!ctx || !baseCtx || !frontCtx || !frontBaseCtx) return;
    const q = this.quantityPerItem;
    const reduced = reducedMotion();
    const step = fadeStep(dt, FADE_S, reduced);
    for (const drawn of this.layers) {
      const { layer } = drawn;
      const shown = this.facts.holds(layer.when, t, q) && !(layer.until && this.facts.holds(layer.until, t, q));
      const alpha = shown ? Math.min(1, drawn.alpha + step) : Math.max(0, drawn.alpha - step);
      if (alpha !== drawn.alpha) {
        drawn.alpha = alpha;
        this.baseDirty = true;
      }
    }
    if (this.baseDirty) {
      this.composeBase(baseCtx, frontBaseCtx);
      this.baseDirty = false;
      this.shownDirty = true;
      if ((this.crop || this.cover) && !this.fixed) this.fit();
    }
    this.chooseGrade(t);
    if (this.fade < 1) {
      this.fade = Math.min(1, this.fade + gradeStep(this.to, dt, reduced));
      this.shownDirty = true;
    }
    if (this.shownDirty) {
      this.present(ctx, frontCtx);
      this.shownDirty = false;
    }
  }

  private composeBase(ctx: CanvasRenderingContext2D, frontCtx: CanvasRenderingContext2D): void {
    const [w, h] = this.manifest.size;
    ctx.clearRect(0, 0, w, h);
    frontCtx.clearRect(0, 0, w, h);
    this.drawLayers(ctx, "base");
    this.drawLayers(frontCtx, "front");
  }

  private drawLayers(ctx: CanvasRenderingContext2D, pass: Pass, only: (layer: SceneLayer) => boolean = () => true): void {
    for (const { layer, image, alpha } of this.layers) {
      if (passOf(layer) !== pass || !only(layer)) continue;
      if (alpha <= 0 || !image.complete || image.naturalWidth === 0) continue;
      ctx.globalAlpha = alpha;
      ctx.globalCompositeOperation = (layer.blend ?? "source-over") as GlobalCompositeOperation;
      ctx.drawImage(image, layer.x, layer.y);
    }
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = "source-over";
  }

  /** The base with the grade over it, easing from the previous grade to the current one. */
  private present(ctx: CanvasRenderingContext2D, frontCtx: CanvasRenderingContext2D): void {
    const [w, h] = this.manifest.size;
    ctx.clearRect(0, 0, w, h);
    frontCtx.clearRect(0, 0, w, h);
    for (const [target, source, op] of [[ctx, this.base, "source-over"], [frontCtx, this.frontBase, "source-atop"]] as const) {
      if (this.fade < 1 && this.from) this.paintGraded(target, source, op, this.from, 1);
      this.paintGraded(target, source, op, this.to, this.fade);
      target.globalAlpha = 1;
    }
    this.drawLayers(ctx, "ungraded");
    this.drawLayers(frontCtx, "ungraded", isGlow);
    frontCtx.globalCompositeOperation = "destination-in";   // the glows were drawn on clear canvas too: keep them on the figures only
    frontCtx.drawImage(this.frontBase, 0, 0);
    frontCtx.globalCompositeOperation = "source-over";
  }

  /** `source` with the grade over it; `op` keeps the overlay and the wash on the source's own pixels (the front canvas is mostly clear). */
  private paintGraded(ctx: CanvasRenderingContext2D, source: HTMLCanvasElement, op: GlobalCompositeOperation, grade: SceneGrade | null, alpha: number): void {
    const [w, h] = this.manifest.size;
    ctx.globalAlpha = alpha;
    if (this.canFilter) ctx.filter = lightFilter(grade?.filter ?? "none", this.day);
    ctx.drawImage(source, 0, 0);
    if (this.canFilter) ctx.filter = "none";
    ctx.globalCompositeOperation = op;
    if (grade) {
      ctx.fillStyle = grade.overlay;
      ctx.fillRect(0, 0, w, h);
    }
    const wash = duskWash(this.day);
    if (wash) {
      ctx.fillStyle = wash;
      ctx.fillRect(0, 0, w, h);
    }
    ctx.globalCompositeOperation = "source-over";
  }

  private chooseGrade(t: number): void {
    const chosen = pickGrade(this.manifest.grades ?? {}, (when) => this.facts.holds(when, t, this.quantityPerItem));
    if (!chosen || chosen[0] === this.gradeId) return;
    const first = this.gradeId === "";
    this.gradeId = chosen[0];
    this.from = this.to;
    this.to = chosen[1];
    this.fade = first ? 1 : 0;
    this.shownDirty = true;
    // Without canvas filters the grade is the element's, applied at once.
    if (!this.canFilter) this.canvas.style.filter = this.front.style.filter = chosen[1].filter;
  }

  /** The height a width-sized box may take: its column's height less the panel and the story strip under it and the head
   * and the aim over it (a phone has no column: no cap). */
  private roomAbove(box: HTMLElement): number {
    const left = box.closest<HTMLElement>(".left");
    if (!left || left.clientHeight === 0) return Infinity;
    const low = left.querySelector<HTMLElement>(".low");
    const aim = (left.querySelector<HTMLElement>(".aim")?.offsetHeight ?? 0) + (left.querySelector<HTMLElement>(".scene-head")?.offsetHeight ?? 0);
    const strip = left.querySelector<HTMLElement>(".strip")?.offsetHeight ?? 0;
    const style = getComputedStyle(box);
    return left.clientHeight - (low ? parseFloat(getComputedStyle(low).minHeight) || 0 : 0) - aim - strip - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom) - FRAME_PX;
  }

  /** Size the canvas, in CSS px, to the largest scale of the art that fits the box: whole device pixels once that is 2x or more. */
  private fit(): void {
    const box = this.canvas.parentElement?.parentElement;
    const [w, h] = this.manifest.size;
    if (!box) return;
    const dpr = window.devicePixelRatio || 1;
    const style = getComputedStyle(box);
    this.cover = style.getPropertyValue("--cover").trim() === "1";
    if (this.crop || this.cover) { this.fitCropped(box, dpr, this.crop ?? COVER); return; }
    Object.assign(this.canvas.style, { left: "", top: "" });
    const bw = box.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight) - FRAME_PX;
    // A box that takes the art's own height (the phone stage) sets only its width.
    const byWidth = style.getPropertyValue("--by-width").trim() === "1";
    const bh = byWidth ? this.roomAbove(box) : box.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom) - FRAME_PX;
    const fit = Math.min((bw * dpr) / w, (bh * dpr) / h);
    if (!(fit > 0)) return;
    const k = fit >= 2 && style.getPropertyValue("--fill").trim() !== "1" ? Math.floor(fit) : fit;
    this.canvas.style.width = `${(w * k) / dpr}px`;
    this.canvas.style.height = `${(h * k) / dpr}px`;
    this.followCanvas();
  }

  /** The front canvas lies exactly over the first: its size and, in a crop, its place. */
  private followCanvas(): void {
    const { width, height, left, top } = this.canvas.style;
    Object.assign(this.front.style, { width, height, left: left || "0px", top: top || "0px" });
  }

  /** Place the canvas so the box shows the cropped part of the art: at whole device pixels per art pixel, or covering it. */
  private fitCropped(box: HTMLElement, dpr: number, crop: Pick<Crop, "hold" | "window" | "cover">): void {
    if (box.clientWidth === 0) return;
    const shown = this.layers.filter((d) => d.alpha > 0 && d.image.complete).map(({ layer, image }) => ({
      id: layer.id, x: layer.x, y: layer.y, w: image.naturalWidth, h: image.naturalHeight,
    }));
    const placed = place([box.clientWidth, box.clientHeight], dpr, this.manifest.size, { ...crop, focus: this.fixed ?? focusOf(shown) });
    Object.assign(this.canvas.style, {
      width: `${placed.width}px`, height: `${placed.height}px`, left: `${placed.left}px`, top: `${placed.top}px`,
    });
    this.followCanvas();
  }
}
