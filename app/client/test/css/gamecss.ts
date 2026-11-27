import { readFileSync } from "node:fs";

/** The game screen's stylesheet as one text: src/game.css with each `@import` replaced by the file it names, in order. */
export function readGameCss(): string {
  return readFileSync("src/game.css", "utf8").replace(/^@import "\.\/([^"]+)";\n/gm, (_m, path: string) => readFileSync(`src/${path}`, "utf8"));
}
