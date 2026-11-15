// How long a story line is held (game/reading.ts): the floor, the words rate, and the first line of a return's multiple.
import { READING, readingMs } from "../src/game/reading";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const words = (n: number): string => Array.from({ length: n }, () => "word").join(" ");
const long = words(100);
const plain = Math.round((100 / READING.wpm) * 60_000);

expect("a short line is held for the floor", readingMs("Short."), READING.floorMs);
expect("an empty line is held for the floor", readingMs(""), READING.floorMs);
expect("a long line is held for its words at the rate", readingMs(long), plain);
expect("the rate is above the floor for the long line", plain > READING.floorMs, true);
expect("the first line of a return is held the multiple of its plain time", readingMs(long, true), Math.round(plain * READING.returnFirst));
expect("a short first line of a return is held the multiple of the floor", readingMs("Short.", true), Math.round(READING.floorMs * READING.returnFirst));
expect("not first of a return is plain", readingMs(long, false), plain);
expect("the multiple slows the first line", READING.returnFirst > 1, true);
expect("pinned numbers", [READING.wpm, READING.floorMs, READING.returnFirst], [150, 3500, 1.75]);
