// FIXTURE, never shipped: places on the world map (CONTRACT.txt, "MAP") with placeholder ids and names, for the Map page's
// screenshots (the shipped game has no places yet). #places=N reveals the first N (all with a bare #places); #map opens
// the Book on its Map. Each place is revealed by a feature of its own id. The stamps are served from /assets/art/map/
// by a screenshot run that made them with tools/mapstamps.py; without them the sheet draws its labels alone.
//   The set: a named village beside the town, neighbours on adjacent cells with long names (labels that must find room),
//   an unnamed forest and range, and a fort at the map's reach.
import type { Content, View } from "../src/api/types";

type Place = Content["places"][number];
const PLACES: Place[] = ([
  { place: "pl_mill", stamp: "village", east: 1, north: 1, label_key: "pl.mill" },
  { place: "pl_woods", stamp: "forest", east: -1, north: 0, label_key: null },
  { place: "pl_ford", stamp: "crossing", east: 2, north: 1, label_key: "pl.ford" },
  { place: "pl_hold", stamp: "stronghold", east: 2, north: 2, label_key: "pl.hold" },
  { place: "pl_peaks", stamp: "range", east: -2, north: 3, label_key: null },
  { place: "pl_watch", stamp: "fort", east: 5, north: -4, label_key: "pl.watch" },
  { place: "pl_hamlet", stamp: "hill_village", east: -3, north: -2, label_key: "pl.hamlet" },
] satisfies Omit<Place, "reveal">[]).map((p) => ({ ...p, reveal: { category: "feature" as const, id: p.place } }));

const NAMES: Record<string, string> = {
  "pl.mill": "The Old Mill", "pl.ford": "Ford of the Long Shallows", "pl.hold": "Greyhold", "pl.watch": "The Far Watchtower",
  "pl.hamlet": "Hillside Hamlet",
};

export function withPlaces(content: Content): Content {
  return {
    ...content,
    places: PLACES,
    feature_infos: [...content.feature_infos, ...PLACES.map((p) => ({ feature: p.place, hint_key: null, label_key: null, effect_key: null, change_bp: [], feature_card: null }))],
    text_entries: [...content.text_entries, ...Object.entries(NAMES).map(([key, text]) => ({ key, text }))],
  };
}

/** `view` with the first `n` places revealed. */
export function placesView(view: View, n = PLACES.length): View {
  return { ...view, unlocked: [...view.unlocked, ...PLACES.slice(0, n).map((p) => ({ category: "feature" as const, id: p.place }))] };
}
