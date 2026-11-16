// Two pieces of the scene's page plumbing, apart from drawing: the manifest fetch and the room the art is given.
import { isManifest, type SceneManifest } from "./manifest";

/** The manifest at `url` and the base its layers resolve against, or null when it cannot be fetched or is not one (the
 * game plays without a scene). */
export async function fetchManifest(url: string): Promise<{ manifest: SceneManifest; base: string } | null> {
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

/** The height a width-sized box may take: its column's height less the panel and the story strip under it and the head
 * and the aim over it, and the frame `framePx` (a phone has no column: no cap). */
export function roomAbove(box: HTMLElement, framePx: number): number {
  const left = box.closest<HTMLElement>(".left");
  if (!left || left.clientHeight === 0) return Infinity;
  const low = left.querySelector<HTMLElement>(".low");
  const aim = (left.querySelector<HTMLElement>(".aim")?.offsetHeight ?? 0) + (left.querySelector<HTMLElement>(".scene-head")?.offsetHeight ?? 0);
  const strip = left.querySelector<HTMLElement>(".strip")?.offsetHeight ?? 0;
  const style = getComputedStyle(box);
  return left.clientHeight - (low ? parseFloat(getComputedStyle(low).minHeight) || 0 : 0) - aim - strip - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom) - framePx;
}
