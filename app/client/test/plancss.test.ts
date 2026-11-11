// Next's "+ Plan" lists the saved mixes as Mixes-list rows (.selector-run, ui/stintplan.ts) straight in the Rules tab's
// list, a flex column: there the row's flex basis (18rem, sized for a row of rows) would be its height, so each row
// takes its content's height instead (src/game.css), as the rule picker's do. The layout is CSS, so this reads the rules.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
/** The body of the first rule whose selector list names `selector`. */
const ruleFor = (selector: string): string => {
  const found = [...css.matchAll(/^([^{}\n]+)\{([^}]*)\}/gm)].find((m) => (m[1] ?? "").split(",").some((s) => s.trim() === selector));
  if (!found) throw new Error(`no rule for ${selector}`);
  return found[2] ?? "";
};

expect("the Rules tab's list is a column", /flex-direction: column/.test(ruleFor(".rules-list")), true);
expect("a Mixes-list row's basis is a width", /flex: 1 1 18rem/.test(ruleFor(".selector-run")), true);
expect("a Plan row in that column takes its content's height", /flex: none/.test(ruleFor(".rules-list > .selector-run")), true);
expect("as a rule picker's row does", /flex: none/.test(ruleFor(".rule-picker .selector-run")), true);
