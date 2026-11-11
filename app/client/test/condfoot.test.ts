// A rule's editor on a phone (ui/condition.ts; src/game.css): the choices scroll in their own area and the pinned foot
// (the rule as a sentence, Remove, Save) sits outside it, so no chip is ever behind the foot.
import { readFileSync } from "node:fs";
import { install } from "./fake-dom";
import { testContext } from "./context";
import { ConditionEditor } from "../src/ui/condition";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const editor = new ConditionEditor(testContext().ctx, () => undefined);
expect("the editor is the scrolling choices, then the foot", Array.from(editor.root.children, (c) => c.className), ["cond-body", "cond-foot"]);

const css = readFileSync("src/game.css", "utf8");
const phone = css.slice(css.indexOf("@media (max-width: 1023px) and (orientation: portrait), (max-width: 639px) {"));
expect("the choices scroll above the foot", /\.cond-body \{[^}]*overflow-y: auto/.test(phone), true);
expect("the foot does not float over them", /\.cond-foot \{ position: static/.test(phone), true);
