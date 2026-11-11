// How long a story line needs on screen to be read (docs/design/opening-screen.md, "One thing at a time"): the queue
// holds the next line for it, and the band keeps a line that long before a newer one pushes it out.

/** `wpm`: 175, the slow end of adult silent reading (Brysbaert 2019) and the BBC's 160-180 for text read beside a
 * picture, which a line on the art is (docs/research/human-player.md#### 1. Reading speed and decision latency).
 * `floorMs`: no line is held for less, however short, since the eye has to get there first: a design choice. */
export const READING = { wpm: 175, floorMs: 3000 } as const;

export function readingMs(text: string): number {
  const words = text.split(/\s+/).filter((w) => w.length > 0).length;
  return Math.max(READING.floorMs, Math.round((words / READING.wpm) * 60_000));
}
