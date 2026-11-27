// The map's stamp choices and layout (contract/map.txt, "MAP", acceptance 5 and 6): a place's variant is the save's and its
// kind's shuffle bag, walked over every place of the kind, so it is stable as places are revealed and repeats only once
// the pool is used; on every fixed sheet no two stamps cross, every stamp lies inside the sheet, and no label crosses a
// stamp, another label or the edge, a label with no clear spot being left off.
import { crosses, frameOf, placeLabels, stampBoxes, type Box } from "../src/game/book/maplayout";
import { HOME, stampPicks, type Place, type StampManifest } from "../src/game/book/mapsheet";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const place = (id: string, stamp: Place["stamp"], east: number, north: number, label = true): Place =>
  ({ place: id, stamp, east, north, reveal: { category: "feature", id }, label_key: label ? `k.${id}` : null });
const arts = (kind: string, n: number, w: number, h: number) => Array.from({ length: n }, (_, i) => ({ src: `${kind}-${i + 1}.png`, w, h }));
const MANIFEST: StampManifest = { village: arts("village", 5, 46, 43), fort: arts("fort", 3, 51, 44), range: arts("range", 4, 273, 133),
  forest: arts("forest", 4, 64, 82) };

// ---------- 5: the picks ----------

const villages = Array.from({ length: 12 }, (_, i) => place(`v${i}`, "village", i - 6, 3));
const all: Place[] = [...villages, place("f1", "fort", 1, -1), place("r1", "range", -2, -2)];
const picks = stampPicks(7, all, MANIFEST);
expect("the same save draws the same art", [...stampPicks(7, all, MANIFEST)].map(([k, a]) => [k, a.src]), [...picks].map(([k, a]) => [k, a.src]));
expect("another save draws differently somewhere", [...stampPicks(8, all, MANIFEST)].some(([k, a]) => picks.get(k)!.src !== a.src), true);
expect("the town is a village: the bag's first draw", picks.has(HOME) && picks.get(HOME)!.src.startsWith("village-"), true);
const firstRound = [HOME, ...villages.slice(0, 4).map((p) => p.place)].map((k) => picks.get(k)!.src);
expect("no two share a variant while the pool lasts", new Set(firstRound).size, 5);
const secondRound = villages.slice(4, 9).map((p) => picks.get(p.place)!.src);
expect("the second round uses every variant again before any repeats", new Set(secondRound).size, 5);
// the content order is what is walked, not what is revealed: a place's art is the same whichever others are revealed
const later = [...all, place("v_late", "village", 4, 4)];
expect("a place keeps its art when another of its kind is added after it", villages.map((p) => stampPicks(7, later, MANIFEST).get(p.place)!.src),
  villages.map((p) => picks.get(p.place)!.src));
expect("a kind with no art draws nothing", stampPicks(7, [place("t1", "tree", 1, 1)], MANIFEST).has("t1"), false);

// ---------- 6: the layout on fixed sheets ----------

const SHEETS = [{ w: 356, h: 490 }, { w: 2300, h: 1950 }, { w: 1040, h: 650 }];
const LAYOUTS: Record<string, Place[]> = {
  neighbours: [place("a", "village", 1, 0), place("b", "fort", 1, 1), place("c", "range", 0, 1, false), place("d", "forest", -1, 0, false),
    place("e", "village", 2, 1), place("f", "village", 2, 0)],
  reach: [place("n", "fort", 0, 8), place("s", "village", 0, -8), place("e", "range", 8, 0), place("w", "forest", -8, -8)],
  lone: [place("only", "village", 1, 1)],
};
const LONG = "A very long name for a place that runs on";
let dropped = 0;
for (const [name, places] of Object.entries(LAYOUTS)) {
  for (const s of SHEETS) {
    const spots = [{ id: HOME, east: 0, north: 0 }, ...places.map((p) => ({ id: p.place, east: p.east, north: p.north }))];
    const frame = frameOf(spots, s.w, s.h, 160);
    const chosen = stampPicks(1, places, MANIFEST);
    const boxes = stampBoxes(new Map(spots.map((p) => [p.id, { art: chosen.get(p.id)!, at: p }])), frame);
    const stamps = [...boxes.values()];
    const at = `${name} at ${s.w}x${s.h}`;
    expect(`${at}: no two stamps cross`, stamps.some((a, i) => stamps.some((b, j) => i < j && crosses(a, b))), false);
    expect(`${at}: every stamp is inside the sheet`, stamps.every((b) => b.x >= 0 && b.y >= 0 && b.x + b.w <= s.w && b.y + b.h <= s.h), true);
    const wanted = spots.map((p, i) => ({ id: p.id, beside: boxes.get(p.id)!, w: (i % 2 ? LONG.length : 8) * 8, h: 18 }));
    const labels = placeLabels(wanted, stamps, s.w, s.h, [4, 14, 30]);
    const drawn = [...labels.values()].filter((b): b is Box => b !== null);
    dropped += labels.size - drawn.length;
    expect(`${at}: no label crosses a stamp`, drawn.some((l) => stamps.some((b) => crosses(l, b))), false);
    expect(`${at}: no two labels cross`, drawn.some((a, i) => drawn.some((b, j) => i < j && crosses(a, b))), false);
    expect(`${at}: every label is inside the sheet`, drawn.every((b) => b.x >= 0 && b.y >= 0 && b.x + b.w <= s.w && b.y + b.h <= s.h), true);
    expect(`${at}: the town's label is drawn`, labels.get(HOME) !== null, true);
  }
}
expect("the crowded phone sheet leaves some label off (the check can see a drop)", dropped > 0, true);
// control: the check above sees a crossing when there is one
expect("crosses sees an overlap", crosses({ x: 0, y: 0, w: 10, h: 10 }, { x: 9, y: 9, w: 5, h: 5 }), true);
expect("and not boxes that only touch", crosses({ x: 0, y: 0, w: 10, h: 10 }, { x: 10, y: 0, w: 5, h: 5 }), false);
const noRoom = placeLabels([{ id: "x", beside: { x: 40, y: 40, w: 20, h: 20 }, w: 500, h: 20 }], [], 100, 100, [4]);
expect("a label with no clear spot is left off", noRoom.get("x"), null);
