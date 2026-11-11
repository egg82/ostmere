// A narrow share-bar segment cuts the task's name and keeps its share (ui/sharebar.ts, game.css): the share is its own
// element that does not shrink, and the name is the one that takes the ellipsis. Both stay in the segment's text, name
// then share, for anything reading it.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const body = (selector: string): string => [...css.matchAll(/(?:^|\n)(\.[^\n{}]*?)\s*\{([^}]*)\}/g)].find((m) => m[1] === selector)?.[2] ?? "";
expect("the share does not shrink", /flex: none/.test(body(".share-pct")), true);
expect("the name takes the ellipsis", /text-overflow: ellipsis/.test(body(".share-name")), true);
expect("and may shrink below its text", /min-width: 0/.test(body(".share-name")), true);
expect("the segment's text is no longer cut as a whole", /text-overflow/.test(body(".share-text")), false);
const src = readFileSync("src/ui/sharebar.ts", "utf8");
expect("the share has its own element, after the name", src.indexOf('"share-name"') > 0 && src.indexOf('"share-name"') < src.indexOf('"share-pct"'), true);
