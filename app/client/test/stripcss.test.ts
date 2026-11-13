// The story strip's layout (src/game.css; docs/design/opening-screen.md, "One column of attention"): the shown line and
// the room of every line share one grid cell and one type size, so the strip is the tallest line's height and no line
// is cut; the lines before the newest are dimmer, none faded or clipped. The Camp bar's next-marker wraps by word rather
// than truncating, and the first card keeps its hidden parts' room. The layout is CSS, so this reads the rules.
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

expect("the strip is a grid", /display: grid/.test(rule(".strip")), true);
const cell = rule(".strip > .lines, .strip > .strip-room");
expect("the line and the room share one cell", /grid-area: 1 \/ 1/.test(cell), true);
expect("in one type size", /font-size: var\(--t-story\)/.test(cell) && /line-height: 1\.35/.test(cell), true);
expect("the room is unseen", /visibility: hidden/.test(rule(".strip-room")), true);
expect("each line in the room shares the cell", /grid-area: 1 \/ 1/.test(rule(".strip-room > span")), true);
expect("only a line waiting its turn is hidden by CSS; the strip's script keeps the ones that fit", /display: none/.test(rule(".lines li.held")), true);
expect("the lines before the newest are dimmer", /color: var\(--ink-dim\)/.test(rule(".lines li:not(:nth-last-child(1 of :not(.held)))")), true);
expect("the room measures its own height, not the cell's", /align-self: start/.test(rule(".strip-room")), true);

// Nothing else sizes a story line, so a line and its room twin always wrap alike; nothing fades or clips one.
const sized = [...css.matchAll(/([^{}]*\.(?:lines|strip-room)[^{}]*)\{([^}]*)\}/g)]
  .filter((m) => /font-size|line-height|font:/.test(m[2] ?? "")).map((m) => (m[1] ?? "").trim());
expect("one rule sizes the line and its room", sized, [".strip > .lines, .strip > .strip-room"]);
const clipped = [...css.matchAll(/([^{}]*\.(?:lines|strip)\b[^{}]*)\{([^}]*)\}/g)]
  .filter((m) => /mask-image|overflow: hidden|max-height|text-overflow/.test(m[2] ?? "")).map((m) => (m[1] ?? "").trim());
expect("no rule fades or clips the strip or its line", clipped, []);

// On a desktop the head leaves the art while it holds nothing, except a dotted Log, which must stay reachable.
expect("a dotted Log keeps the head on the art", /\.scene-head:not\(:has\([^{}]*\.new-dot\)\) \{ display: none; \}/.test(css), true);

// On a desktop the strip sits between the stage and the skills and ledger: the stage still sees the ledger's absence.
expect("the art does not take the hidden ledger block's room, so its arrival resizes nothing", /\.stage:has\(~ \.low\[hidden\]\)/.test(css), false);

const next = rule(".camp-next");
expect("the marker does not truncate", /text-overflow|nowrap/.test(next), false);
expect("the marker's row may wrap", /\.camp-head \{[^}]*flex-wrap: wrap/.test(css), true);
const untapped = /\n\.card\.first\.untapped :is\(([^)]*)\) \{ ([^}]*)\}/.exec(css);
expect("the first card's count, bar and time hide until its first tap", untapped?.[1], ".card-count, .card-track, .card-foot");
expect("hidden, their room kept", untapped?.[2]?.trim(), "visibility: hidden;");
