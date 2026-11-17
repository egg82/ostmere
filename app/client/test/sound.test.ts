const assert = {
  equal(got: unknown, want: unknown) { if (got !== want) throw new Error(`got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`); },
  deepEqual(got: unknown, want: unknown) {
    if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
  },
  ok(v: unknown) { if (!v) throw new Error("not ok"); },
};
import { createPlayer, CUT_MS, type ContextLike } from "../src/audio/player";
import { registerSound, resetSound, sound } from "../src/audio/locator";
import { browserSoundSwitch } from "../src/audio/mute";
import { bindSilence } from "../src/audio/page";
import type { Slot, SlotName } from "../src/audio/slots";

interface Log { ramps: [number, number][]; sources: { rate: number; started: boolean; when?: number }[]; calls: string[]; time: number }

function fakeContext(log: Log): ContextLike {
  const param = () => ({
    value: 1,
    cancelScheduledValues() {},
    setValueAtTime() {},
    linearRampToValueAtTime(v: number, t: number) { log.ramps.push([v, Math.round((t - log.time) * 1000)]); },
  });
  return {
    get currentTime() { return log.time; },
    destination: {},
    createGain: () => ({ gain: param(), connect() {} }),
    createBufferSource() {
      const s: Log["sources"][number] = { rate: 1, started: false };
      log.sources.push(s);
      return {
        buffer: null, loop: false, connect() {}, start(when?: number) { s.started = true; s.when = when; },
        playbackRate: { set value(v: number) { s.rate = v; }, get value() { return s.rate; } },
      };
    },
    async decodeAudioData() { return {}; },
    async resume() { log.calls.push("resume"); },
    async suspend() { log.calls.push("suspend"); },
  };
}

const slot = (asset: string | null, pitch = 1): Slot => ({ asset, gain: 1, pitch });
const table = (over: Partial<Record<SlotName, Slot>>) => ({
  tap: slot(null), tick: slot(null), first: slot(null), level: slot(null), strike: slot(null), story: slot(null),
  failed: slot(null), page: slot(null), settle: slot(null), ...over,
});

async function rig(over: Partial<Record<SlotName, Slot>>) {
  const log: Log = { ramps: [], sources: [], calls: [], time: 10 };
  const timers: [() => void, number][] = [];
  const player = createPlayer({
    makeContext: () => fakeContext(log),
    fetchBytes: async () => new ArrayBuffer(1),
    after: (fn, ms) => { timers.push([fn, ms]); },
    slots: table(over),
  });
  await player.start();
  return { log, timers, player };
}

// A slot with no asset is skipped; one with an asset plays
{
  const { log, player } = await rig({ tap: slot("sound/tap.ogg") });
  player.play("first");
  assert.equal(log.sources.length, 0);
  player.play("tap");
  assert.equal(log.sources.length, 1);
  assert.ok(log.sources[0]!.started);
}

// A slot whose asset fails to load is skipped, never late
{
  const log: Log = { ramps: [], sources: [], calls: [], time: 0 };
  const player = createPlayer({
    makeContext: () => fakeContext(log),
    fetchBytes: async () => { throw new Error("404"); },
    slots: table({ tap: slot("sound/tap.ogg") }),
  });
  await player.start();
  player.play("tap");
  assert.equal(log.sources.length, 0);
}

// Pitch is a playback-rate ratio: the slot's own ratio times the call's
{
  const { log, player } = await rig({ tick: slot("sound/tick.ogg", 1.25) });
  player.play("tick");
  player.play("tick", 6 / 5);
  assert.equal(log.sources[0]!.rate, 1.25);
  assert.equal(log.sources[1]!.rate, 1.25 * 6 / 5);
}

// A delayed sound starts on the audio clock that far on; its cut fades it over CUT_MS
{
  const { log, player } = await rig({ tick: slot("sound/tick.ogg") });
  const cut = player.play("tick", 1, 270);
  assert.equal(log.sources.length, 1);
  assert.equal(log.sources[0]!.when, 10.27);
  cut();
  assert.deepEqual(log.ramps.at(-1), [0, 50]);
}

// Silent ramps to zero in 50 ms, then suspends; waiting sounds are dropped; unsilencing resumes
{
  const { log, timers, player } = await rig({ tap: slot("sound/tap.ogg") });
  player.setSilent(true);
  assert.equal(CUT_MS, 50);
  assert.deepEqual(log.ramps.at(-1), [0, 50]);
  assert.deepEqual(timers.map((t) => t[1]), [50]);
  assert.deepEqual(log.calls, []);
  timers[0]![0]();
  assert.deepEqual(log.calls, ["suspend"]);
  player.play("tap");
  assert.equal(log.sources.length, 0);
  player.setSilent(false);
  assert.deepEqual(log.calls, ["suspend", "resume"]);
  assert.deepEqual(log.ramps.at(-1)![0], 1);
  player.play("tap");
  assert.equal(log.sources.length, 1);
}

// A cut undone before its suspend runs does not suspend
{
  const { log, timers, player } = await rig({});
  player.setSilent(true);
  player.setSilent(false);
  timers[0]![0]();
  assert.deepEqual(log.calls, ["resume"]);
}

// Hidden page or a muted device is silent; shown and unmuted is not
{
  const { log, player } = await rig({ tap: slot("sound/tap.ogg") });
  let on = true;
  const page = { hidden: false, listener: () => {}, addEventListener(_: "visibilitychange", fn: () => void) { this.listener = fn; } };
  const refresh = bindSilence(player, page, { get: () => on, set() {} });
  player.play("tap");
  assert.equal(log.sources.length, 1);
  page.hidden = true; page.listener();
  player.play("tap");
  assert.equal(log.sources.length, 1);
  page.hidden = false; on = false; refresh();
  player.play("tap");
  assert.equal(log.sources.length, 1);
  on = true; refresh();
  player.play("tap");
  assert.equal(log.sources.length, 2);
}

// The Null default plays nothing and throws nothing; a registered sound replaces it
{
  resetSound();
  sound().play("tap");
  sound().play("tick", 1.5);
  const played: string[] = [];
  registerSound({ play: (s) => { played.push(s); return () => undefined; }, loop: () => ({ setLevel: () => undefined }), piece: () => ({ setLevel: () => undefined, stop: () => undefined, onEnd: () => undefined }) });
  sound().play("first");
  assert.deepEqual(played, ["first"]);
  resetSound();
}

// The mute accessor: on by default, keeps an off, and survives a throwing localStorage
{
  const data = new Map<string, string>();
  const store = { getItem: (k: string) => data.get(k) ?? null, setItem: (k: string, v: string) => { data.set(k, v); }, removeItem: (k: string) => { data.delete(k); } } as Storage;
  const sw = browserSoundSwitch(() => store);
  assert.equal(sw.get(), true);
  sw.set(false);
  assert.equal(sw.get(), false);
  sw.set(true);
  assert.equal(sw.get(), true);
  const broken = browserSoundSwitch(() => { throw new Error("blocked"); });
  broken.set(false);
  assert.equal(broken.get(), true);
}
