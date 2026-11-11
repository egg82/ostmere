// FIXTURE, never shipped: a scene manifest of plain coloured rectangles in the real manifest's shape (layers with
// when/until/blend, grades), standing in for the art until the assets volume serves /assets/art/scene/. One layer
// per condition kind the scene maps.
import type { SceneManifest } from "../src/scene/manifest";

function rect(w: number, h: number, fill: string): string {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><rect width="${w}" height="${h}" fill="${fill}"/></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

export const fixtureManifest: SceneManifest = {
  size: [480, 288],
  pixelated: true,
  layers: [
    { id: "sky", src: rect(480, 288, "#26232b"), x: 0, y: 0, when: "always" },
    { id: "ground", src: rect(480, 70, "#3a332d"), x: 0, y: 218, when: "always" },
    { id: "lying", src: rect(40, 12, "#8a7f73"), x: 40, y: 206, when: "always", until: "pushes:stand@1" },
    { id: "standing", src: rect(12, 36, "#8a7f73"), x: 60, y: 182, when: "pushes:stand@1" },
    { id: "lean-to", src: rect(70, 40, "#5a4a36"), x: 320, y: 178, when: "pushes:shelter@1" },
    { id: "bench-work", src: rect(30, 12, "#8f9a6a"), x: 360, y: 206, when: "running:shelter" },
    { id: "woodpile", src: rect(26, 14, "#7a5a3a"), x: 150, y: 204, when: "store:wood" },
    { id: "woodpile-high", src: rect(20, 10, "#7a5a3a"), x: 153, y: 194, when: "store:wood@10" },
    { id: "figure-away", src: rect(12, 36, "#8a7f73"), x: 400, y: 182, when: "running:shelter|running:hatchet" },
    { id: "seated", src: rect(12, 30, "#9a8f83"), x: 200, y: 188, when: "always", until: "running:far_hunt|mix:far_hunt" },
    { id: "fire", src: rect(16, 16, "#e0954f"), x: 232, y: 202, when: "store:warmth" },
    { id: "glow", src: rect(120, 80, "#6a3a1a"), x: 180, y: 160, when: "store:warmth", blend: "screen" },
    { id: "frost", src: rect(480, 6, "#a9bfd8"), x: 0, y: 216, when: "chip:cold" },
    { id: "ledger-mark", src: rect(10, 10, "#c9a35c"), x: 460, y: 10, when: "feature:ledger" },
    { id: "hatchet", src: rect(10, 6, "#b9b0a3"), x: 100, y: 212, when: "project:hatchet" },
  ],
  grades: {
    cold: { when: null, filter: "brightness(0.86) saturate(0.85)", overlay: "rgba(84,62,40,0.14)" },
    warm: { when: "chip:warm", filter: "brightness(0.98) saturate(0.95)", overlay: "rgba(255,140,60,0.07)" },
    night: { when: "feature:night", filter: "brightness(0.64) saturate(0.65) contrast(1.12)", overlay: "rgba(14,18,40,0.28)" },
    day: { when: "feature:morning", filter: "brightness(0.98) saturate(0.95)", overlay: "rgba(255,140,60,0.07)" },
  },
};

export function fixtureManifestUrl(): string {
  return URL.createObjectURL(new Blob([JSON.stringify(fixtureManifest)], { type: "application/json" }));
}
