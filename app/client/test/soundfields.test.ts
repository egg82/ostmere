// The fields the sound wiring reads (docs/design/sound.md, "What wiring needs"): a served line says whether it opens a
// beat, and a scene layer says what it sounds as; neither is taken from a key or a layer id.
import type { LogLine } from "../src/api/types";
import { beatOpeners } from "../src/game/story/beats";
import { isManifest, soundLayer, type SceneLayer } from "../src/scene/manifest";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

{  // the field decides, whatever the key says
  const lines: LogLine[] = [
    { at: 1, seq: 0, key: "l_b3_1", card: null, opens_beat: false },
    { at: 2, seq: 1, key: "l_anything", card: null, opens_beat: true },
    { at: 3, seq: 2, key: "l_b3_2", card: "take_stock", opens_beat: false },
  ];
  expect("only the flagged line opens a beat", beatOpeners(lines).map((l) => l.key), ["l_anything"]);
  expect("a batch with none opens none", beatOpeners(lines.filter((l) => !l.opens_beat)), []);
}

{  // the layer's field decides, whatever its id says
  const layer = (id: string, sound?: SceneLayer["sound"]): SceneLayer => ({ id, src: `${id}.png`, x: 0, y: 0, when: null, ...(sound ? { sound } : {}) });
  const layers = [layer("firelight"), layer("hearth_glow", "fire"), layer("firelight_dusk"), layer("late_light", "evening")];
  const manifest = { size: [10, 10], layers };
  expect("the manifest still reads", isManifest(manifest), true);
  expect("the fire is the layer that says so", soundLayer(layers, "fire")?.id, "hearth_glow");
  expect("the evening is the layer that says so", soundLayer(layers, "evening")?.id, "late_light");
  expect("none says so: none", soundLayer([layer("firelight")], "fire"), undefined);
}
