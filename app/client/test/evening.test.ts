// The evening piece (audio/evening.ts, docs/design/sound.md "Music: the evening piece") on fake clocks: it waits for its
// moment, plays once, ducks under the story cue and the strike, ends on its own, is cut by mute, and under the Null
// locator does nothing.
import { createEvening, DUCK_BACK_MS, DUCK_HOLD_MS, DUCK_MS, ENTRY_AFTER_END_MS, type EveningFrame } from "../src/audio/evening";
import { hasSound, registerSound, resetSound, type Piece, type Sound } from "../src/audio/locator";
import { createPlayer, CUT_MS, type ContextLike, type GainLike } from "../src/audio/player";
import { RESUME_MS } from "../src/audio/piece";
import { GRADE_S } from "../src/scene/manifest";
import { BEDS, PIECES, SLOTS } from "../src/audio/slots";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
function near(label: string, got: number, want: number): void {
  if (Math.abs(got - want) > 1e-6) throw new Error(`${label}: got ${got}, want ${want}`);
}

// ---- a recording locator: each piece keeps what it was told
interface Made { calls: [string, number, number][]; ended: boolean; ends: (() => void)[] }
let made: Made[] = [];
function recording(): Sound {
  return {
    play: () => () => undefined,
    loop: () => ({ setLevel: () => undefined }),
    piece(): Piece {
      const m: Made = { calls: [], ended: false, ends: [] };
      made.push(m);
      return {
        setLevel: (level, ms) => { m.calls.push(["level", level, ms]); },
        stop: (ms) => { m.calls.push(["stop", 0, ms]); m.ended = true; },
        onEnd: (fn) => { m.ends.push(fn); },
      };
    },
  };
}
const DAY: EveningFrame = { shown: false, grade: "warm", easeS: 2.5, endShowing: false };
const EVE: EveningFrame = { ...DAY, shown: true, grade: "dusk", easeS: 40 };
const END: EveningFrame = { ...EVE, endShowing: true };   // the opening's end: its lines are queued or showing
const last = (m: Made) => m.calls[m.calls.length - 1];
function fresh() { made = []; registerSound(recording()); return createEvening(); }

// the piece never plays before its moment
{
  const e = fresh();
  e.frame(DAY, 0);
  e.frame(DAY, 100);
  expect("by day: nothing", made.length, 0);
  // a reload into the evening: the first frame only resets
  const r = fresh();
  r.frame(EVE, 0);
  r.frame(EVE, 100);
  expect("an evening already showing at the first frame: nothing", made.length, 0);
  // an evening that began while the page was hidden
  const h = fresh();
  h.frame(DAY, 0);
  h.away();
  h.frame(EVE, 5000);
  h.frame(EVE, 5100);
  expect("an evening that began while hidden: nothing", made.length, 0);
  // begun in view: it starts with the layer, fading in over the grade ease
  const v = fresh();
  v.frame(DAY, 0);
  v.frame(EVE, 100);
  expect("it starts with the layer", made.length, 1);
  expect("silent, then fading in over GRADE_S", made[0]!.calls, [["level", 0, 0], ["level", 1, GRADE_S * 1000]]);
  // the opening's end: the strike first, the piece 4 s on
  const s1 = fresh();
  s1.frame(DAY, 0);
  s1.cue("end", 1000);
  s1.frame(END, 1000);
  s1.frame(END, 1000 + ENTRY_AFTER_END_MS - 1);
  expect("before the strike is over: nothing", made.length, 0);
  s1.frame(END, 1000 + ENTRY_AFTER_END_MS);
  expect("4 s after the strike", made.length, 1);
  // the layer wanted while the end's line is still queued: the strike owns the first hearing
  const l = fresh();
  l.frame(DAY, 0);
  l.frame(END, 1000);
  for (let t = 1100; t < 15000; t += 100) l.frame(END, t);
  expect("wanted while the end's line is queued: nothing before the strike", made.length, 0);
  l.cue("end", 15000);
  l.frame(END, 15000 + ENTRY_AFTER_END_MS - 1);
  expect("not before 4 s after the strike", made.length, 0);
  l.frame(END, 15000 + ENTRY_AFTER_END_MS);
  expect("first enters 4 s after the end cue", made.length, 1);
  // the end's lines over with no strike ever sung: the piece is no longer held
  const q = fresh();
  q.frame(DAY, 0);
  q.frame(END, 1000);
  q.frame(EVE, 21000);
  expect("lines over, no strike: it enters", made.length, 1);
  // a strike after it has begun (a later evening's end) ducks it
  const k = fresh();
  k.frame(DAY, 0);
  k.frame(EVE, 1000);
  k.cue("end", 2000);
  expect("a strike over a playing piece ducks it", last(made[0]!)![1] < 1, true);
  // hidden while it waits: dropped
  const d = fresh();
  d.frame(DAY, 0);
  d.cue("end", 0);
  d.frame(END, 0);
  d.away();
  d.frame(EVE, 9000);
  d.frame(EVE, 9100);
  expect("hidden while it waits: dropped", made.length, 0);
}

// at most once per evening, again on a new one
{
  const e = fresh();
  e.frame(DAY, 0);
  e.frame(EVE, 100);
  for (let t = 200; t < 5000; t += 100) e.frame(EVE, t);
  made[0]!.ends.forEach((fn) => fn());
  for (let t = 5000; t < 9000; t += 100) e.frame(EVE, t);
  expect("one piece however long the evening", made.length, 1);
  e.frame(DAY, 9100);
  e.frame(EVE, 9200);
  expect("the next evening has its own", made.length, 2);
  // a flicker of the layer inside one evening does not restart it
  const f = fresh();
  f.frame(DAY, 0);
  f.frame(EVE, 100);
  f.frame(EVE, 200);
  expect("still one while it plays", made.length, 1);
}

// ducking: the story cue and the strike drop it 9 dB over 0.2 s and it comes back over 2.5 s; shorter cues play over it
{
  const e = fresh();
  e.frame(DAY, 0);
  e.frame(EVE, 100);
  const m = made[0]!;
  const DUCKED = 10 ** (-9 / 20);
  e.cue("level", 1000);
  e.cue("new", 1000);
  e.cue("knock", 1000);
  expect("shorter cues play over it", m.calls.length, 2);
  e.cue("beat", 2000);
  expect("the story cue ducks it", last(m), ["level", DUCKED, DUCK_MS]);
  e.frame(EVE, 2000 + DUCK_HOLD_MS.beat! - 1);
  expect("held for the cue", last(m)![1], DUCKED);
  e.frame(EVE, 2000 + DUCK_HOLD_MS.beat!);
  expect("then back over 2.5 s", last(m), ["level", 1, DUCK_BACK_MS]);
  e.cue("end", 20000);
  expect("the strike ducks it", last(m), ["level", DUCKED, DUCK_MS]);
  e.cue("beat", 20500);
  const n = m.calls.length;
  e.frame(EVE, 20000 + DUCK_HOLD_MS.end! - 1);
  expect("a second cue while down does not duck twice, and holds for the later one", m.calls.length, n);
  e.frame(EVE, Math.max(20000 + DUCK_HOLD_MS.end!, 20500 + DUCK_HOLD_MS.beat!));
  expect("back after the last one", last(m), ["level", 1, DUCK_BACK_MS]);
}

// it ends on its own; night falling fades it over that grade's ease and nothing restarts it
{
  const e = fresh();
  e.frame(DAY, 0);
  e.frame(EVE, 100);
  made[0]!.ends.forEach((fn) => fn());
  e.cue("beat", 500);
  expect("a cue after its end touches nothing", made[0]!.calls.length, 2);
  const g = fresh();
  g.frame(DAY, 0);
  g.frame(EVE, 100);
  g.frame({ ...EVE, grade: "night", easeS: 12 }, 200);
  expect("the grade changes first: fades over its ease", last(made[0]!), ["stop", 0, 12000]);
  g.frame({ ...EVE, grade: "night", easeS: 12 }, 300);
  expect("and is not begun again", made.length, 1);
  // night falls while it still waits on the strike
  const w = fresh();
  w.frame(DAY, 0);
  w.cue("end", 0);
  w.frame(END, 0);
  w.frame({ ...EVE, grade: "night" }, 1000);
  w.frame({ ...EVE, grade: "night" }, 6000);
  expect("never in the night's grade", made.length, 0);
}

// ---- through the real player on a fake audio clock: it ends on its own, mute cuts it, and a long cut is over
const clock = { now: 0 };
let wall = 0;
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
      set value(v: number) { node.evs.push({ t: -Infinity, v, ramp: false }); },   // intrinsic: a cancel keeps it
      cancelScheduledValues: (t: number) => { node.evs = node.evs.filter((x) => x.t < t); },
      setValueAtTime: (v: number, t: number) => { node.evs.push({ t, v, ramp: false }); },
      linearRampToValueAtTime: (v: number, t: number) => { node.evs.push({ t, v, ramp: true }); },
    };
  })();
  connect(to: unknown): void { this.to = to instanceof FakeGain ? to : null; }
}
interface Src { gain: FakeGain | null; started: boolean; stopped: boolean; onended: (() => void) | null }
let srcs: Src[] = [];
let suspends = 0;
const ctx: ContextLike = {
  get currentTime() { return clock.now; },
  destination: {},
  createGain() { return new FakeGain(); },
  createBufferSource() {
    const s: Src = { gain: null, started: false, stopped: false, onended: null };
    srcs.push(s);
    return {
      buffer: null, loop: false, playbackRate: { value: 1 },
      connect(to: unknown) { s.gain = to as FakeGain; }, start() { s.started = true; }, stop() { s.stopped = true; },
      set onended(fn: (() => void) | null) { s.onended = fn; }, get onended() { return s.onended; },
    };
  },
  async decodeAudioData() { return {}; },
  async resume() {},
  async suspend() { suspends += 1; },
};
const timers: (() => void)[] = [];
const piece = { asset: "p.ogg", gain: PIECES.evening.gain, pitch: 1 };
const player = createPlayer({ makeContext: () => ctx, fetchBytes: async () => new ArrayBuffer(1), after: (fn) => { timers.push(fn); }, slots: SLOTS, beds: BEDS, pieces: { evening: piece }, now: () => wall });
await player.start();
const heard = (s: Src): number => { let v = 1; for (let g = s.gain; g; g = g.to) v *= g.at(clock.now); return v; };
function begun() { clock.now = 0; wall = 0; srcs = []; registerSound(player); const e = createEvening(); e.frame(DAY, 0); e.frame(EVE, 100); return e; }

{
  begun();
  const src = srcs[0]!;
  expect("the piece began", src.started, true);
  near("silent at its start", heard(src), 0);
  clock.now = 1 + GRADE_S;
  near("faded in over 2.5 s", heard(src), PIECES.evening.gain);
  clock.now = 90;
  near("steady for its length", heard(src), PIECES.evening.gain);
  const own = player.piece("evening");
  let over = 0;
  own.onEnd(() => { over += 1; });
  srcs[srcs.length - 1]!.onended?.();   // its last note
  expect("its last note ends it, once", over, 1);
  srcs[srcs.length - 1]!.onended?.();
  expect("and only once", over, 1);
}
{
  begun();
  const src = srcs[0]!;
  clock.now = 10;
  player.setSilent(true);
  clock.now = 10 + CUT_MS / 1000;
  near("mute cuts it in 50 ms", heard(src), 0);
  timers.splice(0).forEach((fn) => fn());
  expect("the context suspends", suspends > 0, true);
  clock.now = 10; wall = 10_000;
  player.setSilent(false);
  expect("cut off under 30 s ago, it carries on", src.stopped, false);
  clock.now = 10 + CUT_MS / 1000;
  near("and is heard again", heard(src), PIECES.evening.gain);
}
{
  begun();
  const src = srcs[0]!;
  clock.now = 10; wall = 10_000;
  player.setSilent(true);
  wall = 10_000 + RESUME_MS + 1;
  player.setSilent(false);
  expect("cut off for longer than 30 s, it is over", src.stopped, true);
}
{
  // hidden before the piece's moment: nothing is begun on a silent page
  srcs = [];
  player.setSilent(true);
  const e = createEvening();
  e.frame(DAY, 0);
  e.frame(EVE, 100);
  expect("nothing is begun while silent", srcs.length, 0);
  player.setSilent(false);
}

// the Null locator plays nothing and nothing seen changes
{
  resetSound();
  srcs = [];
  expect("the Null is not a sound", hasSound(), false);
  const e = createEvening();
  const seen: unknown[] = [];
  e.frame(DAY, 0);
  e.frame(EVE, 100);
  e.cue("end", 200);
  e.cue("beat", 300);
  e.frame(EVE, 5000);
  e.frame({ ...EVE, grade: "night" }, 6000);
  e.away();
  seen.push(srcs.length, made.length);
  expect("nothing was made", seen, [0, made.length]);
}
console.log("evening ok");
