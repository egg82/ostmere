// The scene draws the fire's light at a varying alpha, and under prefers-reduced-motion at one steady alpha with no
// frame spent on it (Scene.draw, scene/flicker.ts).
import { Scene } from "../src/scene/scene";
import type { SceneManifest } from "../src/scene/manifest";

let reduced = false;
const alphas: number[] = [];   // the alpha of each glow drawn, in order
let presents = 0;               // frames drawn onto the visible canvas

function fakeCanvas(visible: boolean): HTMLCanvasElement {
  const ctx = new Proxy({ globalAlpha: 1 } as Record<string, unknown>, {
    get: (o, k) => (k in o ? o[k as string] : () => { if (k === "clearRect" && visible) presents++; }),
    set: (o, k, v) => { o[k as string] = v; return true; },
  });
  const drawImage = (): void => { if (visible && (ctx as { globalCompositeOperation?: string }).globalCompositeOperation === "screen") alphas.push(ctx.globalAlpha as number); };
  (ctx as Record<string, unknown>).drawImage = drawImage;
  return Object.assign({} as HTMLCanvasElement, { width: 0, height: 0, style: {}, className: "", parentElement: null, after: () => {}, setAttribute: () => {}, getContext: () => ctx });
}
const g = globalThis as Record<string, unknown>;
g.document = { createElement: () => fakeCanvas(false) };
g.window = { matchMedia: () => ({ matches: reduced }), devicePixelRatio: 1 };
g.ResizeObserver = class { observe(): void {} };
g.Image = class { complete = true; naturalWidth = 4; decoding = ""; onload: (() => void) | null = null; set src(_: string) { queueMicrotask(() => this.onload?.()); } };

const manifest: SceneManifest = {
  size: [8, 8],
  layers: [{ id: "firelight", src: "f.png", x: 0, y: 0, when: "always", blend: "screen", ungraded: true, flicker: 0.3 }],
};
const visible = fakeCanvas(true);
const scene = new Scene(visible, manifest, "http://x/", 1);
await scene.loaded;

function run(seconds: number): { alphas: number[]; presents: number } {
  alphas.length = 0;
  presents = 0;
  for (let i = 0; i < seconds * 60; i++) scene.draw(i / 60, 1 / 60);
  return { alphas: [...alphas], presents };
}
function fail(label: string, detail: unknown): never { throw new Error(`${label}: ${JSON.stringify(detail)}`); }

run(2);   // the fade in, and the first frames
const moving = run(10);
const distinct = new Set(moving.alphas.map((a) => a.toFixed(3))).size;
if (distinct < 20) fail("the fire's light barely varies on screen", distinct);
if (Math.min(...moving.alphas) < 0.7 - 1e-9 || Math.max(...moving.alphas) > 1 + 1e-9) fail("alpha outside its range", [Math.min(...moving.alphas), Math.max(...moving.alphas)]);
if (moving.presents > 10 * 16) fail("frames drawn faster than the flicker's pace", moving.presents);

reduced = true;
run(1);   // the frame that settles it
const still = run(10);
if (still.presents !== 0) fail("reduced motion still draws frames", still.presents);
reduced = true;
scene.setLight(1);
const steady = run(1);
if (steady.alphas.length === 0) fail("the control frame drew no glow", 0);
if (steady.alphas.some((a) => a !== 1)) fail("reduced motion draws the fire at a varying alpha", steady.alphas.slice(0, 3));
console.log("scenefire ok");
