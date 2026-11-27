// A completion's "+1" (docs/design/opening-screen/feedback.md, "The feedback ladder") never covers a card's title or its need
// rows, on any frame of its rise: it sits in the room the card's head keeps clear at its right, and rises 12px from
// there, staying in the head's row. The geometry is CSS, so this computes the boxes from the rules, at a phone's card
// width (390 wide: two columns of about 170px) and a desktop's.
import { readGameCss } from "./gamecss";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readGameCss();
const rule = (selector: string): string => {
  const start = css.indexOf(`\n${selector} {`);
  if (start < 0) throw new Error(`no rule for ${selector}`);
  return css.slice(start, css.indexOf("}", start));
};
const rem = (decl: string, prop: string): number => {
  const m = new RegExp(`(?:^|[;{\\s])${prop}: ([\\d.]+)rem`).exec(decl);
  if (!m) throw new Error(`no ${prop} in rem: ${decl}`);
  return Number(m[1]);
};
const padding = (decl: string): number[] => {
  const m = /padding: ([\d.]+)rem ([\d.]+)rem ([\d.]+)rem ([\d.]+)rem/.exec(decl);
  if (!m) throw new Error(`no four-sided padding: ${decl}`);
  return m.slice(1).map(Number);
};

const ROOT = 16;   // a phone's root size (game.css: html font-size); the boxes scale with it
const POP_W = 1.5 * ROOT;   // "+1" in bold at the card's body size, with room to spare
const POP_H = 1.4 * ROOT;
const pop = rule(".pop");
const tap = padding(rule(".card-tap"));
const headRight = rem(rule(".card-head"), "padding-right");
const keyframes = css.slice(css.indexOf("@keyframes pop "), css.indexOf("\n", css.indexOf("@keyframes pop ")));   // one line
const lifts = [...keyframes.matchAll(/translateY\((-?[\d.]+)rem\)/g)].map((m) => Number(m[1]) * ROOT);

type Box = { left: number; right: number; top: number; bottom: number };
const meets = (a: Box, b: Box): boolean => a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;

for (const cardW of [170, 230]) {
  const right = rem(pop, "right") * ROOT, top = rem(pop, "top") * ROOT;
  const title: Box = { left: (tap[3] ?? 0) * ROOT, right: cardW - ((tap[1] ?? 0) + headRight) * ROOT, top: (tap[0] ?? 0) * ROOT, bottom: 400 };   // the head's text, however many lines it wraps to
  for (const dy of [0, ...lifts]) {
    const box: Box = { left: cardW - right - POP_W, right: cardW - right, top: top + dy, bottom: top + dy + POP_H };
    expect(`card ${cardW}px, the "+1" lifted ${dy}px: clear of the title and the needs under it`, meets(box, title), false);
  }
}
expect("it rises 12px, as the design's tap result does", Math.min(...lifts), -12);
console.log("cardpop: ok");
