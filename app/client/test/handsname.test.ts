// The hands strip's meta row gives way in an order (game.css): the queue's head first, then the status text, and the mix's
// name last, by shrink factors far enough apart that the name loses not even a sub-pixel, since a name short of its own
// width by a hair is drawn "M..". A covered status is hidden but keeps its width, so it must not squeeze the name.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const shrink = (selector: string): number => {
  const body = [...css.matchAll(/(?:^|\n)(\.[^\n{}]*?)\s*\{([^}]*)\}/g)].find((m) => m[1] === selector)?.[2] ?? "";
  const flex = /flex:\s*([\d.]+)\s+([\d.]+)/.exec(body);
  if (!flex) throw new Error(`no flex on ${selector}`);
  return Number(flex[2]);
};

const name = shrink(".hands-mix-name");
const status = shrink(".hands-status");
const next = shrink(".hands-next");
expect("the name's own shrink factor is the base", name, 1);
expect("the status text gives way long before the name", status / name >= 100_000, true);
expect("the queue's head gives way before the status", next / status >= 100, true);
