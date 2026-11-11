// The scene manifest's shape (fetched at runtime from the assets volume) and the fades and grade choice it drives.
// Pure: nothing here draws (scene.ts does).

export interface SceneLayer {
  id: string;
  src: string;
  x: number;
  y: number;
  when: string | null;
  until?: string | null;
  /** A canvas composite / CSS mix-blend-mode name, e.g. "screen". */
  blend?: string | null;
  /** Drawn over the grade, not under it: a light that is the player's (the fire) is never dimmed by dusk. */
  ungraded?: boolean;
  /** Stands in front of the lights: drawn on the second canvas, graded like the base, over the ungraded pass. */
  front?: boolean;
  /** The y of the art's ground contact (its feet): layers that have one are drawn in order of it (see depthOrder). */
  base?: number;
}

export interface SceneGrade {
  when: string | null;
  filter: string;
  overlay: string;
  /** Seconds the scene takes to move into this grade (default GRADE_S): a slow one is light going as it is watched. */
  ease_s?: number;
}

export interface SceneManifest {
  size: [number, number];
  pixelated?: boolean;
  layers: SceneLayer[];
  /** In order: the first is the default; a later one whose `when` holds replaces it. */
  grades?: Record<string, SceneGrade>;
}

export function isManifest(m: unknown): m is SceneManifest {
  const o = m as Partial<SceneManifest> | null;
  return !!o && Array.isArray(o.size) && o.size.length === 2 && Array.isArray(o.layers)
    && o.layers.every((l) => typeof l.src === "string" && typeof l.x === "number" && typeof l.y === "number"
      && (l.base === undefined || typeof l.base === "number"));
}

export type Pass = "base" | "ungraded" | "front";

/** The pass a layer is drawn in: the base (graded), the lights over it, or the front canvas over both. */
export function passOf(layer: SceneLayer): Pass {
  return layer.front ? "front" : layer.ungraded ? "ungraded" : "base";
}

/** A glow laid over the scene (an ungraded layer with a blend): it lights figures in front of the fire too. */
export function isGlow(layer: SceneLayer): boolean {
  return layer.ungraded === true && !!layer.blend;
}

/** The draw order: layers with a `base` sorted by it (equal bases keep manifest order), each into a slot a based layer
 * held, so a layer with no base (flat ground, lights, fog) never moves and a manifest with no bases is drawn as listed.
 * What stands lower on the ground is nearer: a figure whose feet are above a prop's base is drawn behind it. */
export function depthOrder(layers: readonly SceneLayer[]): SceneLayer[] {
  const based = layers.filter((l) => l.base !== undefined);
  based.sort((a, b) => (a.base ?? 0) - (b.base ?? 0));
  let next = 0;
  return layers.map((l) => (l.base === undefined ? l : (based[next++] ?? l)));
}

/** How far a frame of dt seconds moves a fade of `seconds` (0 to 1); under reduced motion the fade is one frame. */
export function fadeStep(dt: number, seconds: number, reduced: boolean): number {
  return reduced ? 1 : dt / seconds;
}

/** How far a frame of dt seconds moves the fade into `to` (0 to 1 over its ease_s, else GRADE_S). */
export function gradeStep(to: SceneGrade | null, dt: number, reduced = false): number {
  return fadeStep(dt, to?.ease_s ?? GRADE_S, reduced);
}

/** The grade shown: the first, unless a later one's `when` holds, and the last of those wins (tools/scene/grades.py,
 * pick): the end's dusk stays on its own record (ended_at), so the night and then the day are later grades. */
export function pickGrade(grades: Record<string, SceneGrade>, holds: (when: string) => boolean): [string, SceneGrade] | undefined {
  const entries = Object.entries(grades);
  let chosen = entries[0];
  for (const entry of entries.slice(1)) if (entry[1].when && holds(entry[1].when)) chosen = entry;
  return chosen;
}

const GRADE_S = 2.5;
