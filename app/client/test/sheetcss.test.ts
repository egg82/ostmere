// A sheet taller than the viewport scrolls its body inside a max-height of the viewport, its heading and its actions
// (Close) staying in sight (src/game.css, .sheet). The layout is CSS, so this reads the rules.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const rule = (selector: string): string => {
  const start = css.indexOf(`\n${selector} {`);
  if (start < 0) throw new Error(`no rule for ${selector}`);
  return css.slice(start, css.indexOf("}", start));
};

const sheet = rule(".sheet");
expect("the sheet is no taller than the viewport", /max-height: calc\(100dvh - [\d.]+rem\)/.test(sheet), true);
expect("and scrolls its own body", /overflow-y: auto/.test(sheet), true);
expect("the heading stays", /position: sticky; top: /.test(rule(".sheet > .panel-heading")), true);
expect("the actions stay", /position: sticky; bottom: /.test(rule(".sheet > .sheet-actions")), true);
