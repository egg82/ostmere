// The part of the art the page shows (manifest.ts pickView): the first view by default, the last whose `when` holds,
// and the whole art for a manifest that lists none.
import { pickView, type SceneManifest } from "../src/scene/manifest";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const manifest: SceneManifest = {
  size: [600, 400],
  layers: [],
  views: [
    { id: "camp", size: [480, 288], when: null },
    { id: "wider", size: [540, 336], when: "feature:a" },
    { id: "widest", size: [600, 400], when: "feature:b" },
  ],
};
const holding = (...facts: string[]) => (when: string) => facts.includes(when);

expect("the first by default", pickView(manifest, holding()), [480, 288]);
expect("a later one when its fact holds", pickView(manifest, holding("feature:a")), [540, 336]);
expect("the last that holds wins", pickView(manifest, holding("feature:a", "feature:b")), [600, 400]);
expect("a later one holding alone", pickView(manifest, holding("feature:b")), [600, 400]);
expect("no views: the whole art", pickView({ size: [480, 288], layers: [] }, holding("feature:a")), [480, 288]);
