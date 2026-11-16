// The fire's light varies as it burns, irregularly and within its strength, and holds steady under prefers-reduced-motion
// (scene/flicker.ts: the Clock the scene steps each frame).
import { Clock, FLICKER_HZ, flickerLevel } from "../src/scene/flicker";

const STRENGTH = 0.22;
const STEPS = 600;   // 40 seconds at the flicker's pace

function levels(reduced: boolean, seed = 0): number[] {
  const clock = new Clock();
  const out: number[] = [];
  for (let i = 0; i < STEPS; i++) {
    clock.advance(1 / FLICKER_HZ, reduced);
    out.push(clock.level(seed, STRENGTH, reduced));
  }
  return out;
}
function fail(label: string, detail: unknown): never { throw new Error(`${label}: ${JSON.stringify(detail)}`); }

// Under reduced motion every level is exactly steady, and the clock asks for no redraw after the first.
const still = levels(true);
if (still.some((v) => v !== 1)) fail("reduced motion flickers", still.filter((v) => v !== 1).slice(0, 3));
const settled = new Clock();
settled.advance(0.1, true);
if (settled.advance(0.1, true)) fail("reduced motion keeps asking for a frame", true);

// Control (the checks below can fail): the same run with motion allowed does move.
const moving = levels(false);
const lo = Math.min(...moving);
const hi = Math.max(...moving);
if (hi - lo < STRENGTH * 0.5) fail("the flicker barely moves", { lo, hi });
if (lo < 1 - STRENGTH - 1e-9 || hi > 1 + 1e-9) fail("the level leaves its range", { lo, hi });

// Not a pulse: its steps change in size and sign, and a half-second window does not repeat on the next.
const steps = moving.slice(1).map((v, i) => v - (moving[i] ?? v));
const distinct = new Set(steps.map((d) => d.toFixed(4))).size;
if (distinct < STEPS / 2) fail("the steps repeat", distinct);
const win = (from: number) => moving.slice(from, from + 8).map((v) => v.toFixed(3)).join();
if (win(10) === win(10 + 8) || win(10) === win(10 + 16)) fail("a window repeats", win(10));
// No beat: the lag-correlation at any period between 0.5 s and 5 s stays well short of a sine's 1.
const mean = moving.reduce((a, b) => a + b, 0) / moving.length;
const dev = moving.map((v) => v - mean);
const energy = dev.reduce((a, b) => a + b * b, 0);
for (let lag = Math.round(FLICKER_HZ / 2); lag <= FLICKER_HZ * 5; lag++) {
  const r = dev.slice(lag).reduce((a, b, i) => a + b * (dev[i] ?? 0), 0) / energy;
  if (r > 0.6) fail("the light beats", { lag, r });
}

// Deterministic for a time and seed; two fires with different seeds are out of step.
if (flickerLevel(3.2, 4, STRENGTH) !== flickerLevel(3.2, 4, STRENGTH)) fail("not deterministic", 0);
const apart = Array.from({ length: 40 }, (_, i) => flickerLevel(i / 5, 0, STRENGTH) !== flickerLevel(i / 5, 1, STRENGTH)).filter(Boolean).length;
if (apart < 30) fail("two fires move together", apart);
console.log("fireflicker ok");
