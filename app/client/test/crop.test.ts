// The front page's crop of the scene (scene/crop.ts, focus.ts, light.ts): whole device pixels per art pixel at any pixel
// ratio, the box covered, the focus held, and the hour's light that leaves the game's own scene (full day) untouched.
import { place } from "../src/scene/crop";
import { focusOf, CAMP } from "../src/scene/focus";
import { daylight, duskWash, lightFilter } from "../src/scene/light";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const ART: [number, number] = [480, 288];
const FIRE: [number, number] = [270, 222];

for (const [dpr, bw, bh] of [[1, 1920, 800], [2, 1920, 800], [1, 3840, 1900], [2, 390, 460], [1.5, 1366, 480]] as const) {
  const p = place([bw, bh], dpr, ART, { focus: FIRE, hold: [0.5, 0.58] });
  expect(`whole device pixels at ${bw}x${bh}@${dpr}`, [Number.isInteger(p.scale), p.scale >= 2], [true, true]);
  expect(`the box is covered at ${bw}x${bh}@${dpr}`, [p.left <= 0, p.top <= 0, p.left + p.width >= bw - 1 / dpr, p.top + p.height >= bh - 1 / dpr], [true, true, true, true]);
  expect(`the canvas is the art at the scale at ${bw}x${bh}@${dpr}`, [p.width * dpr, p.height * dpr], [ART[0] * p.scale, ART[1] * p.scale]);
}
{  // the focus sits where it is held, when the art has room on every side
  const p = place([600, 300], 1, [4000, 3000], { focus: [2000, 1500], hold: [0.5, 0.58] });
  expect("focus held across", p.left + 2000 * p.scale, 300);
  expect("focus held down", p.top + 1500 * p.scale, 174);
}
{  // a window: the scale makes it fill the box's width in whole steps, never below 1
  expect("a window of 112 in 224", place([224, 144], 1, ART, { focus: [270, 196], hold: [0.5, 0.5], window: [112, 72] }).scale, 2);
  expect("a window of 112 in 157", place([157, 100], 1, ART, { focus: [270, 196], hold: [0.5, 0.5], window: [112, 72] }).scale, 1);
  expect("a window wider than the box", place([60, 40], 1, ART, { focus: [270, 196], hold: [0.5, 0.5], window: [112, 72] }).scale, 1);
}
{  // what a small picture centres on
  const at = (id: string) => ({ id, x: 10, y: 20, w: 34, h: 52 });
  expect("a camp centres on the camp", focusOf([at("ruin"), at("ring")]), CAMP);
  expect("a person alone centres on the person", focusOf([at("ruin"), at("figure_up")]), [10 + 17 + 40, 20 + 26]);
  expect("the bare ruin", focusOf([at("ruin")]), [120, 130]);
}
{  // the hour's light: nothing at full day, dimmer and cooler towards night
  expect("1pm is full day", daylight(13), 1);
  expect("1am is dark", daylight(1), 0);
  expect("full day changes no filter", lightFilter("brightness(0.95)", 1), "brightness(0.95)");
  expect("night appends to the grade's filter", lightFilter("brightness(0.95)", 0), "brightness(0.95) brightness(0.66) saturate(0.78)");
  expect("night with no grade filter", lightFilter("none", 0), "brightness(0.66) saturate(0.78)");
  expect("no wash by day", duskWash(1), null);
  expect("a wash at night", duskWash(0), "rgba(16, 22, 44, 0.26)");
}
