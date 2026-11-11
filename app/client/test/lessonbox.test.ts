// The lesson note keeps its own box inside the gutters ui/lessons.ts places it by (docs/design/opening-screen.md,
// "Lessons"): the placement code measures the note's offsetWidth, so a width cap that excludes padding and border (the
// content box) lets the box pass the window's edge at a narrow width or a larger text size, where no spot fits and
// the fallback lays the note over the content it teaches. The layout is CSS, so this reads the rule.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const rule = [...css.matchAll(/(?:^|\n)(\.lesson-note)\s*\{([^}]*)\}/g)].map((m) => m[2] ?? "")[0] ?? "";
expect("the note's rule exists to check", rule.includes("position: fixed"), true);
expect("the width cap bounds the whole box", /box-sizing: border-box/.test(rule), true);
expect("and never passes the window less its gutters", /100vw - 32px/.test(rule), true);
