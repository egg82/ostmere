// A layer as the scene draws it, and what the sound bed reads from it (docs/design/sound.md).
import { soundLayer, type SceneLayer } from "./manifest";

export interface Drawn {
  layer: SceneLayer;
  image: HTMLImageElement;
  alpha: number;
  /** The flicker's level this frame (1 where the layer is steady), scaling alpha when drawn. */
  glow: number;
}

/** The alpha of the first of `layers` (manifest order) that sounds as `sound`, by its field alone; 0 where none does. */
export function soundAlphaOf(drawn: readonly Drawn[], layers: readonly SceneLayer[], sound: NonNullable<SceneLayer["sound"]>): number {
  const layer = soundLayer(layers, sound);
  return drawn.find((d) => d.layer === layer)?.alpha ?? 0;
}
