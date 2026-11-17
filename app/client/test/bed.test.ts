// The bed under the scene (audio/bed.ts, docs/design/sound.md "The bed under the scene"), on a fake audio clock: the wind
// fades in over 2.5 s from the first tap, the fire's gain is its layer's alpha, mute cuts both, the Null locator is silent.
import { createBed, WIND_FADE_MS } from "../src/audio/bed";
import { hasSound, registerSound, resetSound, sound } from "../src/audio/locator";
import { createPlayer, CUT_MS, type ContextLike, type GainLike } from "../src/audio/player";
import { BEDS, SLOTS, type Slot } from "../src/audio/slots";
import { Scene } from "../src/scene/scene";
import type { SceneManifest } from "../src/scene/manifest";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
function near(label: string, got: number, want: number): void {
  if (Math.abs(got - want) > 1e-6) throw new Error(`${label}: got ${got}, want ${want}`);
}

// ---- a fake audio clock whose gain nodes keep their automation, so a gain can be read at any time
const clock = { now: 0 };
interface Ev { t: number; v: number; ramp: boolean }
class FakeGain implements GainLike {
  evs: Ev[] = [];
  to: FakeGain | null = null;
  at(t: number): number {
    let v = 1, pt = -Infinity;
    for (const e of this.evs) {
      if (e.t > t) { if (e.ramp && pt > -Infinity) return v + ((e.v - v) * (t - pt)) / (e.t - pt); break; }
      v = e.v; pt = e.t;
    }
    return v;
  }
  gain = (() => {
    const node = this;
    return {
      get value(): number { return node.at(clock.now); },
      set value(v: number) { node.evs.push({ t: clock.now, v, ramp: false }); },
      cancelScheduledValues: (t: number) => { node.evs = node.evs.filter((e) => e.t < t); },
      setValueAtTime: (v: number, t: number) => { node.evs.push({ t, v, ramp: false }); },
      linearRampToValueAtTime: (v: number, t: number) => { node.evs.push({ t, v, ramp: true }); },
    };
  })();
  connect(to: unknown): void { this.to = to instanceof FakeGain ? to : null; }
}
interface Source { gain: FakeGain | null; loop: boolean; started: boolean }
const sources: Source[] = [];
const suspends: number[] = [];

function makeContext(): ContextLike {
  return {
    get currentTime() { return clock.now; },
    destination: {},
    createGain() { return new FakeGain(); },
    createBufferSource() {
      const s: Source = { gain: null, loop: false, started: false };
      sources.push(s);
      return { buffer: null, playbackRate: { value: 1 }, connect(to: unknown) { s.gain = to as FakeGain; }, start() { s.started = true; }, set loop(v: boolean) { s.loop = v; }, get loop() { return s.loop; } };
    },
    async decodeAudioData() { return {}; },
    async resume() {},
    async suspend() { suspends.push(clock.now); },
  };
}
/** What reaches the speaker from a source: its own gain times every gain after it. */
function heard(s: Source): number {
  let v = 1;
  for (let g = s.gain; g; g = g.to) v *= g.at(clock.now);
  return v;
}
const WIND = BEDS.wind.gain, FIRE = BEDS.fire.gain;
const bedSlot = (gain: number): Slot => ({ asset: "bed.ogg", gain, pitch: 1 });
const timers: [() => void, number][] = [];
const player = createPlayer({
  makeContext, fetchBytes: async () => new ArrayBuffer(1), after: (fn, ms) => { timers.push([fn, ms]); },
  slots: SLOTS, beds: { wind: bedSlot(WIND), fire: bedSlot(FIRE) },
});
registerSound(player);
await player.start();
const wind = () => sources[0];
const fire = () => sources[1];

// ---- the scene: a decoy layer named for the fire that does not sound as it, and the layer that does
const g = globalThis as Record<string, unknown>;
const canvas = (): HTMLCanvasElement => {
  const ctx = new Proxy({ globalAlpha: 1 } as Record<string, unknown>, { get: (o, k) => (k in o ? o[k as string] : () => undefined), set: (o, k, v) => { o[k as string] = v; return true; } });
  return Object.assign({} as HTMLCanvasElement, { width: 0, height: 0, style: {}, className: "", parentElement: null, after: () => {}, setAttribute: () => {}, getContext: () => ctx });
};
g.document = { createElement: canvas };
g.window = { matchMedia: () => ({ matches: false }), devicePixelRatio: 1 };
g.ResizeObserver = class { observe(): void {} };
g.Image = class { complete = true; naturalWidth = 4; decoding = ""; onload: (() => void) | null = null; set src(_: string) { queueMicrotask(() => this.onload?.()); } };
const manifest: SceneManifest = {
  size: [8, 8],
  layers: [
    { id: "fire", src: "d.png", x: 0, y: 0, when: "project:nothing", blend: "screen", ungraded: true },
    { id: "hearth", src: "f.png", x: 0, y: 0, when: "always", blend: "screen", ungraded: true, flicker: 0.4, sound: "fire" },
  ],
};
const DT = 1 / 60;
function newScene(): Promise<Scene> { const s = new Scene(canvas(), manifest, "http://x/", 1); return s.loaded.then(() => s); }
function frame(scene: Scene, bed: ReturnType<typeof createBed>, i: number): void {
  clock.now = i * DT;
  scene.draw(clock.now, DT);
  bed.follow(scene.soundAlpha("fire"));
}

// the wind: nothing before the first tap, then 2.5 s
{
  const scene = await newScene();
  const bed = createBed();
  for (let i = 0; i < 120; i++) frame(scene, bed, i);
  expect("no source before the first tap", sources.length, 0);
  clock.now = 2;
  bed.firstTap();
  bed.firstTap();
  expect("the wind and the fire start, once", sources.length, 2);
  expect("the wind loops", wind()!.loop, true);
  near("silent at the tap", heard(wind()!), 0);
  clock.now = 2 + WIND_FADE_MS / 2000;
  near("halfway", heard(wind()!), WIND / 2);
  clock.now = 2 + WIND_FADE_MS / 1000;
  near("faded in", heard(wind()!), WIND);
  clock.now = 60;
  near("then fixed", heard(wind()!), WIND);
  expect("the fade is the spec's 2.5 s", WIND_FADE_MS, 2500);

  // the fire was built before the tap: it catches over 0.8 s
  clock.now = 2;
  frame(scene, bed, 120);
  near("fire silent at the tap", heard(fire()!), 0);
  clock.now = 2.4;
  near("fire half caught", heard(fire()!), FIRE / 2);
  clock.now = 2.8;
  near("fire caught", heard(fire()!), FIRE);
}

// the fire follows its layer's alpha frame by frame, flicker aside, and not a layer called "fire"
{
  sources.length = 0;
  const scene = await newScene();
  const bed = createBed();
  clock.now = 0;
  bed.firstTap();
  const seen: number[] = [];
  for (let i = 0; i < 120; i++) {
    frame(scene, bed, i);
    near(`frame ${i}: gain is the layer's alpha`, heard(fire()!), scene.soundAlpha("fire") * FIRE);
    seen.push(scene.soundAlpha("fire"));
  }
  if (seen[10]! <= 0 || seen[10]! >= 1) throw new Error(`the fade should be under way at frame 10: ${seen[10]}`);
  expect("alpha is 1 by 0.8 s", seen[50], 1);
  near("flicker does not move it", heard(fire()!), FIRE);
}

// mute cuts both beds inside the mute's time
{
  sources.length = 0;
  const scene = await newScene();
  const bed = createBed();
  clock.now = 0;
  bed.firstTap();
  for (let i = 0; i < 200; i++) frame(scene, bed, i);
  const T = clock.now;
  near("wind in", heard(wind()!), WIND);
  player.setSilent(true);
  clock.now = T + CUT_MS / 2000;
  const mid = heard(wind()!);
  if (mid <= 0 || mid >= WIND) throw new Error(`mid-cut should be between: ${mid}`);
  clock.now = T + CUT_MS / 1000;
  near("wind cut", heard(wind()!), 0);
  near("fire cut", heard(fire()!), 0);
  timers.forEach(([fn]) => fn());
  expect("the context suspends", suspends.length, 1);
}

// the Null locator plays nothing and changes nothing seen
{
  resetSound();
  sources.length = 0;
  expect("the Null is not a sound", hasSound(), false);
  const seen: number[][] = [];
  for (const withBed of [false, true]) {
    const scene = await newScene();
    const bed = createBed();
    const run: number[] = [];
    if (withBed) bed.firstTap();
    for (let i = 0; i < 100; i++) {
      scene.draw(i * DT, DT);
      if (withBed) bed.follow(scene.soundAlpha("fire"));
      run.push(scene.soundAlpha("fire"));
    }
    seen.push(run);
  }
  expect("the scene is the same with the bed", seen[1], seen[0]);
  expect("no source was made", sources.length, 0);
  sound().loop("wind").setLevel(1, 0);
}
console.log("bed ok");
