// A control whose only sign of life is a hover look is reachable by tap and by keyboard (docs/research/a11y-audit.md, §4):
// the panel foot's words read as buttons at rest, and every control whose focus look was a colour alone or nothing gets
// the ring the other controls use. The look is CSS, so this reads the rules.
import { readFileSync } from "node:fs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const css = readFileSync("src/game.css", "utf8");
const rules = [...css.matchAll(/(?:^|\n)\s*([^{}\n/@][^{}]*?)\s*\{([^}]*)\}/g)].map((m) => ({ selectors: (m[1] ?? "").split(/,(?![^(]*\))/).map((s) => s.trim()), body: m[2] ?? "" }));
/** Every declaration block applying to exactly `selector` (also through an `:is(...)` list), in file order. */
const bodies = (selector: string): string[] => rules.filter((r) => r.selectors.some((s) => s === selector
  || (s.startsWith(":is(") && s.endsWith("):focus-visible") && s.slice(4, -"):focus-visible".length).split(/,\s*/).includes(selector.replace(":focus-visible", ""))
    && selector.endsWith(":focus-visible")))).map((r) => r.body);

const controls = ["sound-button", "feedback-open", "devices-open", "games-open", "settings-open", "share-divider"];
for (const c of controls) {
  const focus = bodies(`.${c}:focus-visible`);
  expect(`.${c} has a focus rule`, focus.length > 0, true);
  expect(`.${c} has a focus rule that draws a ring`, focus.some((b) => /outline:\s*2px solid var\(--ink-hi\)/.test(b)), true);
  expect(`.${c} never turns its outline off`, bodies(`.${c}`).concat(focus).some((b) => /outline:\s*none/.test(b)), false);
}

for (const c of ["feedback-open", "devices-open", "games-open", "settings-open"]) {
  expect(`.${c} is underlined at rest, with no hover to show it presses`, bodies(`.${c}`).some((b) => /text-decoration:\s*underline/.test(b)), true);
}

expect("a line's rule mark rings its line, as its own mask would clip an outline",
  bodies(".line:has(.line-rule:focus-visible)").some((b) => /outline:\s*2px solid var\(--ink-hi\)/.test(b)), true);
expect(".line-rule never turns its outline off", bodies(".line-rule:focus-visible").concat(bodies(".line-rule")).some((b) => /outline:\s*none/.test(b)), false);
