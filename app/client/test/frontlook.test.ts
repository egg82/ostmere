// The front page wears the game's look (src/front.css; static/index.html; docs/design/redesign.md, "Look"): no frame but
// a game's picture, controls lifted onto the raised surface, ember filled only on Begin, and the join links plain.
// Reads the rules, as the look is CSS.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const front = readFileSync("src/front.css", "utf8");
const page = readFileSync("../ashfall_app/static/index.html", "utf8");
const rule = (selector: string): string => {
  const start = front.indexOf(`\n${selector} {`);
  if (start < 0) throw new Error(`no rule ${selector}`);
  return front.slice(start, front.indexOf("}", start));
};

expect("no 9-slice frame on the front page", [front, page].map((s) => /border-image/.test(s)), [false, false]);
expect("Begin is ember filled", /background: var\(--ember\)/.test(rule("#begin")), true);
expect("only Begin and the primary button fill with ember", [...front.matchAll(/background: var\(--ember\)/g)].length, 2);
expect("the list of games is raised, not framed", /border-radius: 2px/.test(rule("#rail")) && !/border:/.test(rule("#rail")), true);
expect("the selected game is marked in ink at its edge", /\.place:hover, \.place:focus-visible, \.place\[aria-pressed="true"\] \{[^}]*box-shadow: inset 2px 0 0 var\(--ink-hi\)/.test(front), true);
expect("the join links are plain links", /#have summary \{[^}]*text-decoration: underline/.test(front), true);
expect("a link lights to the bright ink, not ember", /#have summary:hover[^}]*color: var\(--ink-hi\)/.test(front), true);
expect("Join is a raised control, not ember", /background: var\(--raise\)/.test(rule(".have-form button")), true);
expect("the dev panel's divider is a hairline", /border-top: 1px solid var\(--rule\)/.test(rule("#dev .commits")), true);
