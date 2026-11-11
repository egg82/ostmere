// What a small picture of a camp centres on: the camp once it has one, else its person, else the ruin's walls.
// Ids and places are the scene manifest's (assets volume), so this names the layers it reads.

export interface Shown {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export const CAMP: [number, number] = [270, 196];
const CAMP_LAYERS = ["ring", "fire_lit", "cleared"];
const RUIN: [number, number] = [120, 130];

export function focusOf(shown: Shown[]): [number, number] {
  if (shown.some((s) => CAMP_LAYERS.includes(s.id))) return CAMP;
  const who = shown.find((s) => s.id.startsWith("figure_"));
  return who ? [who.x + who.w / 2 + 40, who.y + who.h / 2] : RUIN;
}
