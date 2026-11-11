// The scene's manifest is always revalidated, so a browser holding an old immutable copy cannot keep using it.
import { Scene } from "../src/scene/scene";

let seen: RequestInit | undefined;
globalThis.fetch = ((_url: unknown, init?: RequestInit) => {
  seen = init;
  return Promise.resolve(new Response("{}", { status: 200 }));
}) as typeof fetch;
const warn = console.warn;
console.warn = () => {};
const scene = await Scene.load({} as HTMLCanvasElement, "/assets/art/scene/manifest.json", 1);
console.warn = warn;

if (scene !== null) throw new Error("a non-manifest should load no scene");
if (seen?.cache !== "no-cache") throw new Error(`manifest fetched with cache=${String(seen?.cache)}, want no-cache`);
