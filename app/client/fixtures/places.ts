// FIXTURE, never shipped: places on the world map (contract/map.txt, "MAP") with placeholder ids and names, for the Map page's
// screenshots (the shipped game has no places yet). #places=N reveals the first N (all with a bare #places); #map opens
// the Book on its Map. Each place is revealed by a feature of its own id. The stamps are served from /assets/art/map/
// by a screenshot run that made them with tools/mapstamps.py; without them the sheet draws its labels alone.
//   The set: a named village beside the town, neighbours on adjacent cells with long names (labels that must find room),
//   an unnamed forest and range, and a fort at the map's reach. Then the week-five shapes: a place shown unnamed until the
//   feature `pl_bridge` is held (#bridge adds it), and two places revealed together by `pl_dusk`, one of them a stamp
//   drawn over the village's.
import type { Content, View } from "../src/api/types";

type Place = Content["places"][number];
const NO: Pick<Place, "labelled_after" | "over"> = { labelled_after: null, over: null };
const PLACES: Place[] = ([
  { place: "pl_mill", stamp: "village", east: 1, north: 1, label_key: "pl.mill" },
  { place: "pl_woods", stamp: "forest", east: -1, north: 0, label_key: null },
  { place: "pl_ford", stamp: "crossing", east: 2, north: 1, label_key: "pl.ford" },
  { place: "pl_hold", stamp: "stronghold", east: 2, north: 2, label_key: "pl.hold" },
  { place: "pl_peaks", stamp: "range", east: -2, north: 3, label_key: null },
  { place: "pl_watch", stamp: "fort", east: 5, north: -4, label_key: "pl.watch" },
  { place: "pl_hamlet", stamp: "hill_village", east: -3, north: -2, label_key: "pl.hamlet" },
] satisfies Omit<Place, "reveal" | "labelled_after" | "over">[]).map((p) => ({ ...p, ...NO, reveal: { category: "feature" as const, id: p.place } }));
const DUSK = { category: "feature" as const, id: "pl_dusk" };
PLACES[2] = { ...PLACES[2]!, labelled_after: { category: "feature", id: "pl_bridge" } };
PLACES.push(
  { place: "pl_beacon", stamp: "mountain", east: -4, north: -3, label_key: "pl.beacon", ...NO, reveal: DUSK },
  { place: "pl_cairn", stamp: "tree", east: 1, north: 1, label_key: null, ...NO, over: "pl_mill", reveal: DUSK },
);

const NAMES: Record<string, string> = {
  "pl.mill": "The Old Mill", "pl.ford": "Ford of the Long Shallows", "pl.hold": "Greyhold", "pl.watch": "The Far Watchtower",
  "pl.hamlet": "Hillside Hamlet", "pl.beacon": "The Beacon",
};

export function withPlaces(content: Content): Content {
  return {
    ...content,
    places: PLACES,
    feature_infos: [...content.feature_infos, ...[...new Set(PLACES.map((p) => p.reveal.id))].map((feature) => ({ feature, hint_key: null, label_key: null, effect_key: null, change_bp: [], feature_card: null }))],
    text_entries: [...content.text_entries, ...Object.entries(NAMES).map(([key, text]) => ({ key, text }))],
  };
}

/** `view` with the first `n` places revealed, and the features `also` held. */
export function placesView(view: View, n = PLACES.length, also: string[] = []): View {
  const features = [...PLACES.slice(0, n).map((p) => p.reveal.id), ...also];
  return { ...view, unlocked: [...view.unlocked, ...features.map((id) => ({ category: "feature" as const, id }))] };
}
