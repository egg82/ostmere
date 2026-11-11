// A tap's line on its card never moves the layout (docs/decisions.md, "What can be tapped looks tappable"): the line is
// out of the card's flow, and no rule for a saying card sizes it, so no card or heading below shifts when a line comes
// or goes. The layout is CSS, so this reads the rules.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const rules = [...css.matchAll(/(?:^|\n)(\.[^\n{}]*?)\s*\{([^}]*)\}/g)].map((m) => ({ selector: m[1] ?? "", body: m[2] ?? "" }));
const about = rules.filter((r) => /\.saying\b|\.card-line\b/.test(r.selector));

const line = rules.find((r) => r.selector === ".card-line")?.body ?? "";
expect("the card's line is out of the card's flow", /position: absolute/.test(line), true);
expect("it hangs from the card's foot, over what is below", /top: 100%/.test(line), true);
expect("it takes no taps", /pointer-events: none/.test(line), true);

// What sizes a card or its line in flow: on a rule for a saying card, any of these would move the rows below.
const sizing = /^(flex-wrap|flex-basis|flex|padding[a-z-]*|margin[a-z-]*|height|min-height|gap|border-width)$/;
const sized = about.flatMap((r) => r.body.split(";").map((d) => d.split(":")[0]?.trim() ?? "")
  .filter((p) => sizing.test(p)).map((p) => `${r.selector} { ${p} }`));
expect("no rule for a saying card or its line sizes anything", sized.filter((s) => !s.startsWith(".card-line {")), []);
expect("rules for a saying card exist to check", about.length > 3, true);
