// The small pictures of camps on the front page: one scene manifest, fetched once, and a still of any View drawn by the
// game's own Scene into a box that clips it. A picture draws nothing the View does not hold.
import type { View } from "../api/types";
import { daylight, hoursNow } from "../scene/light";
import type { SceneManifest } from "../scene/manifest";
import { Scene, SCENE_MANIFEST } from "../scene/scene";
import { el } from "./dom";

export class Pictures {
  private constructor(private readonly found: { manifest: SceneManifest; base: string }, readonly quantityPerItem: number) {}

  /** Null when the scene art cannot be had: the front page then has dark frames where pictures would be. */
  static async open(quantityPerItem: number): Promise<Pictures | null> {
    const found = await Scene.manifest(SCENE_MANIFEST);
    return found ? new Pictures(found, quantityPerItem) : null;
  }

  /** The game's Scene in `box`, which clips it: the caller crops it and hands it Views. */
  scene(box: HTMLElement): Scene {
    const inner = el("div", "pic-in");
    const canvas = el("canvas", "pic-art");
    inner.append(canvas);
    box.append(inner);
    const scene = new Scene(canvas, this.found.manifest, this.found.base, this.quantityPerItem);
    scene.setLight(daylight(hoursNow()));
    return scene;
  }

  /** `box` shows a window of the view's camp, held still: drawn once its art has loaded. */
  still(box: HTMLElement, view: View, window: [number, number]): void {
    const scene = this.scene(box);
    scene.update(view);
    scene.cropTo({ hold: [0.5, 0.5], window });
    void scene.loaded.then(() => scene.draw(view.at, Infinity));
  }
}
