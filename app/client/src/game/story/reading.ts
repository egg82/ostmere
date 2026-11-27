// How long a story line needs on screen to be read (docs/design/opening-screen/one-thing-at-a-time.md, "One thing at a time"): the queue
// holds the next line for it, and the band keeps a line that long before a newer one pushes it out.

/** `wpm`: 150, below the slow end of adult silent reading (Brysbaert 2019) and the BBC's 160-180 for text read beside a
 * picture (docs/research/human-player.md#### 1. Reading speed and decision latency), since a story line is read while
 * the eye also takes in the art. `floorMs`: no line is held for less, however short, since the eye has to get there
 * first: a design choice. `returnFirst`: the multiple of its reading time that the first story line of a return is
 * held for, since the player is still arriving. */
export const READING = { wpm: 150, floorMs: 3500, returnFirst: 1.75 } as const;

/** How long `text` is held on the strip; `firstOfReturn`: it is the first story line of a return. */
export function readingMs(text: string, firstOfReturn = false): number {
  const words = text.split(/\s+/).filter((w) => w.length > 0).length;
  const ms = Math.max(READING.floorMs, Math.round((words / READING.wpm) * 60_000));
  return firstOfReturn ? Math.round(ms * READING.returnFirst) : ms;
}
