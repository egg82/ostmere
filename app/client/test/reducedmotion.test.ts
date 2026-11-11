// Under prefers-reduced-motion the scene's fades are instant: the grade and a layer reach their end in one frame
// (scene/scene.ts, fadeStep and gradeStep), and the helper that says so (ui/dom.ts, reducedMotion) reads the OS query.
import { fadeStep, gradeStep } from "../src/scene/manifest";
import { reducedMotion } from "../src/ui/dom";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

expect("a fade with motion: dt over its seconds", fadeStep(0.1, 0.8, false), 0.125);
expect("a fade under reduce: the whole way in one frame", fadeStep(0.016, 0.8, true), 1);
expect("a slow grade under reduce: the whole way in one frame", gradeStep({ when: null, filter: "", overlay: "", ease_s: 20 }, 0.016, true), 1);
expect("a grade with motion is unchanged", gradeStep(null, 1, false), 1 / 2.5);

const g = globalThis as { window?: unknown };
const real = g.window;
for (const matches of [true, false]) {
  const asked: string[] = [];
  g.window = { matchMedia: (q: string) => { asked.push(q); return { matches }; } };
  expect(`the helper reports the OS preference (${matches})`, reducedMotion(), matches);
  expect("it asks for the reduce query", asked, ["(prefers-reduced-motion: reduce)"]);
}
g.window = {};
expect("with no matchMedia (a bare runtime) motion is allowed", reducedMotion(), false);
g.window = real;
console.log("reducedmotion ok");
