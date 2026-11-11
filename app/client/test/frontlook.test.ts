// The front page wears the game's look (src/front.css; static/index.html): square notched frames,
// grooves, the slate panel colours, ember only on Begin, and the join links plain. Reads the rules, as the look is CSS.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const front = readFileSync("src/front.css", "utf8");
const page = readFileSync("../ashfall_app/static/index.html", "utf8");

expect("no rounded corners on the front page", [front, page].map((s) => /border-radius/.test(s)), [false, false]);
expect("Begin has the ember frame", /#begin \{[^}]*border-image: var\(--px-ember\) 1/.test(front), true);
expect("the list of games has the panel's frame", /#rail \{[^}]*border-image: var\(--px2-dim\) 2/.test(front), true);
expect("the selected game has the ember frame", /\.place:hover, \.place:focus-visible, \.place\[aria-pressed="true"\] \{[^}]*border-image: var\(--px-ember\) 1/.test(front), true);
expect("the join links are plain links", /#have summary \{[^}]*text-decoration: underline/.test(front), true);
expect("a link lights to the plain bright ink, not ember", /#have summary:hover[^}]*color: var\(--ink-bright\)/.test(front), true);
expect("Join is not ember until used", /\.have-form button \{[^}]*border-image: var\(--px-stone\) 1/.test(front), true);
expect("the dev panel's divider is a groove", /#dev \.commits \{[^}]*box-shadow: inset 0 2px 0 var\(--rim-dim\)/.test(front), true);
