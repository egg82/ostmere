// A layer as the scene draws it, and what the sound bed reads from it (docs/design/sound.md).
import { passOf, soundLayer, type Pass, type SceneLayer } from "./manifest";

export interface Drawn {
  layer: SceneLayer;
  image: HTMLImageElement;
  alpha: number;
  /** Wanted this frame: its `when` holds and its `until` does not (alpha is where its fade has got to). */
  shown: boolean;
  /** The flicker's level this frame (1 where the layer is steady), scaling alpha when drawn. */
  glow: number;
}

/** The alpha of the first of `layers` (manifest order) that sounds as `sound`, by its field alone; 0 where none does. */
export function soundAlphaOf(drawn: readonly Drawn[], layers: readonly SceneLayer[], sound: NonNullable<SceneLayer["sound"]>): number {
  const layer = soundLayer(layers, sound);
  return drawn.find((d) => d.layer === layer)?.alpha ?? 0;
}

/** Whether the first of `layers` that sounds as `sound` is wanted now, by its field alone. */
export function soundShownOf(drawn: readonly Drawn[], layers: readonly SceneLayer[], sound: NonNullable<SceneLayer["sound"]>): boolean {
  const layer = soundLayer(layers, sound);
  return drawn.find((d) => d.layer === layer)?.shown ?? false;
}

/** The layers of one pass, each at its fade's alpha and flicker, in the blend it names, onto `ctx`. */
export function drawLayers(ctx: CanvasRenderingContext2D, drawn: readonly Drawn[], pass: Pass, only: (layer: SceneLayer) => boolean = () => true): void {
  for (const { layer, image, alpha, glow } of drawn) {
    if (passOf(layer) !== pass || !only(layer)) continue;
    if (alpha <= 0 || !image.complete || image.naturalWidth === 0) continue;
    ctx.globalAlpha = alpha * glow;
    ctx.globalCompositeOperation = (layer.blend ?? "source-over") as GlobalCompositeOperation;
    ctx.drawImage(image, layer.x, layer.y);
  }
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = "source-over";
}
