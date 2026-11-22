// The world map's places and their art (CONTRACT.txt, "MAP"; docs/decisions.md, "A world map"): which places are
// revealed, and which variant of its stamp kind each is drawn with. Pure: a variant is a shuffle bag keyed by the save and
// the kind, walked over every place of the kind in content order, so a place keeps its art as others are revealed.
import type { Content, View } from "../api/types";
import type { Catalog } from "./catalog";
import { seeded } from "./fights";

export type Place = Content["places"][number];
export type Stamp = Place["stamp"];

/** One image of a kind, as /assets/art/map/manifest.json lists it (tools/mapstamps.py), w by h at the base scale. */
export interface StampArt { src: string; w: number; h: number }
export type StampManifest = Partial<Record<Stamp, StampArt[]>>;

/** The id the town is drawn under: a village, the first draw of that kind's bag. */
export const HOME = "";
const HOME_STAMP: Stamp = "village";

/** The places view.unlocked reveals, in content order. */
export function revealed(catalog: Catalog, view: View): Place[] {
  return catalog.content.places.filter((p) => catalog.unlocked(view, p.reveal.category, p.reveal.id));
}

/** Each place's art (HOME for the town), by place id; a kind the manifest has no art for draws nothing. Every place of
 * the content is walked, revealed or not: the i-th draw of a kind is its bag's (i mod n)-th, the bag shuffled afresh
 * each time it is used up. */
export function stampPicks(saveId: number, places: readonly Place[], manifest: StampManifest): Map<string, StampArt> {
  const picks = new Map<string, StampArt>();
  const drawn = new Map<Stamp, number>();
  for (const [id, stamp] of [[HOME, HOME_STAMP] as const, ...places.map((p) => [p.place, p.stamp] as const)]) {
    const art = manifest[stamp] ?? [];
    if (art.length === 0) continue;
    const i = drawn.get(stamp) ?? 0;
    drawn.set(stamp, i + 1);
    picks.set(id, art[bag(`map|${saveId}|${stamp}|${Math.floor(i / art.length)}`, art.length)[i % art.length]!]!);
  }
  return picks;
}

/** 0 to n - 1 in an order drawn from `key`. */
function bag(key: string, n: number): number[] {
  const draw = seeded(key);
  const order = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(draw() * (i + 1));
    [order[i], order[j]] = [order[j]!, order[i]!];
  }
  return order;
}
