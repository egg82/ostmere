// The hands strip's offer rows on a phone sit under the pinned strip, not in it (docs/design/opening-screen.md, "The
// hands strip"): a prompt such as "this mix stopped" must not cost the cards their room, so on a phone Hands seats the
// mix offer, the asked-offer rows and the rule offer in `rows`, which the screen places after the pinned strip; wider
// screens keep them in the strip's body.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { Hands } from "../src/ui/hands";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const rowsOf = (matches: boolean): { rows: number; strip: number } => {
  Object.assign(window, { matchMedia: () => ({ matches, addEventListener: () => {} }) });
  const hands = new Hands(testContext().ctx);
  return { rows: hands.rows.querySelectorAll(".hands-mix-offer, .hands-rule-offer").length, strip: hands.root.querySelectorAll(".hands-mix-offer, .hands-rule-offer").length };
};
const wide = rowsOf(false);
const phone = rowsOf(true);
expect("wide: the offer rows are in the strip", wide.rows === 0 && wide.strip > 0, true);
expect("phone: the same rows are in `rows`, none in the strip", phone.rows === wide.strip && phone.strip === 0, true);
