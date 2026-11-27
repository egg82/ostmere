// A short window (docs/research/a11y-audit.md, §6): the condition editor keeps its Remove, Copy rule and Save row on
// screen and gives the choices the room the foot's lines took, and the lesson note is small enough to dock in the band above
// an open editor. Layout is CSS, which fake-dom cannot draw (no container or media queries), so this reads the rules; the
// measured result is in the branch's before/after renders (the pull request).
import { readGameCss } from "./gamecss";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readGameCss();
/** The text between the `{` that follows `head` and its matching `}`. */
function block(from: string, head: string): string {
  const at = from.indexOf(head);
  expect(`found ${head}`, at >= 0, true);
  let depth = 0;
  for (let i = from.indexOf("{", at); i < from.length; i += 1) {
    if (from[i] === "{") depth += 1;
    if (from[i] === "}" && (depth -= 1) === 0) return from.slice(from.indexOf("{", at) + 1, i);
  }
  throw new Error(`unclosed ${head}`);
}

const phone = block(css, "@media (max-width: 1023px) and (orientation: portrait), (max-width: 639px)");
expect("the rule editor scrolls as one and measures itself", /\.cond \{ container-type: size; overflow-y: auto; \}/.test(phone), true);
const short = block(phone, "@container (max-height: 16rem)");
expect("short: the choices stop scrolling on their own", /\.cond-body \{ flex: none; overflow-y: visible; \}/.test(short), true);
expect("short: the foot's lines scroll with them", /\.cond-foot \{ display: contents; \}/.test(short), true);
const actions = short.match(/\.cond-actions \{([^}]*)\}/)?.[1] ?? "";
expect("short: the action row is pinned to the editor's bottom", /position: sticky; bottom: 0;/.test(actions), true);
expect("short: and keeps a background, so rows scroll under it", /background: var\(--bg\)/.test(actions), true);

const note = block(css, "@media (max-height: 640px)");
expect("a short window: the note's tag, Skip and Got it share one row", /grid-template-columns: 1fr auto auto/.test(note) && /\.lesson-next \{ grid-column: 3; grid-row: 1;/.test(note), true);
