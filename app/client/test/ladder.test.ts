// The feedback ladder (docs/design/opening-screen.md, "The feedback ladder"): a card's completion by the mix or by a
// rule plays a rung below the same completion from the player's tap, and a completion's effect never grows on repeats.
// Driven through the real card panel: what lands on a card's node when its completions go up.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { Card, View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { Cards } from "../src/ui/cards";
import { completionRung, LADDER, RUNGS, type Rung } from "../src/ui/ladder";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const base = fixtureStep("restrule", AT).view;
const ID = "take_stock";
const card = (completions: number, by: Card["by"]): Card => ({
  card: ID, completions, cap: null, bar: { start: AT, start_value: 0, rate: 0, limit: null }, bar_total: 20, by,
  completes_at: null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20, needs: [],
});
const viewOf = (c: Card): View => ({ ...base, cards: [...base.cards, c] });
const PULSES = RUNGS.flatMap((r) => (LADDER[r].pulse ? [LADDER[r].pulse] : []));

/** What one completion played on the card: the ladder's pulse classes now on it and the "+1"s it gained. */
interface Played { pulses: string[]; pops: number }

/** A card run `by` (and, when `rule`, started by a standing order), completing `times` times in a row. */
function completions(by: Card["by"], rule: boolean, times: number): Played[] {
  const { ctx } = testContext();
  const cards = new Cards(ctx, new NewMarks());
  document.body.replaceChildren(cards.root);
  if (rule) ctx.fires.running.add(ID);
  let prev = viewOf(card(0, by));
  cards.update(prev, null);
  cards.update(prev, prev);   // as running, so the panel knows who runs it
  const title = ctx.catalog.label(ctx.catalog.cards.get(ID)?.label_key);
  const ours = [...cards.root.querySelectorAll(".card")].find((n) => n.querySelector(".card-title")?.textContent === title);
  if (!ours) throw new Error("the card is drawn");
  expect("drawn as the rule's when a rule runs it", ours.classList.contains("by-order"), rule);
  const played: Played[] = [];
  for (let k = 1; k <= times; k += 1) {
    for (const p of PULSES) ours.classList.remove(p);   // the last effect has played out
    const before = ours.querySelectorAll(".pop").length;
    const next = viewOf(card(k, by));
    cards.update(next, prev);
    prev = next;
    played.push({ pulses: PULSES.filter((p) => ours.classList.contains(p)), pops: ours.querySelectorAll(".pop").length - before });
  }
  return played;
}

const rank = (r: Rung): number => RUNGS.indexOf(r);

// The mapping itself.
expect("a mix's completion sits below a tap's", rank(completionRung("mix", false)) < rank(completionRung("tap", false)), true);
expect("a rule's completion sits below a tap's", rank(completionRung("tap", true)) < rank(completionRung("tap", false)), true);
expect("a rule's sits with the mix's", completionRung("tap", true), completionRung("mix", false));

// On the card: a tap rings and pops; the mix and a rule only pop.
const tap = completions("tap", false, 3);
const mix = completions("mix", false, 3);
const rule = completions("tap", true, 3);
expect("a tap's completion", tap[0], { pulses: [LADDER.tap.pulse], pops: 1 });
expect("a mix's completion", mix[0], { pulses: [], pops: 1 });
expect("a rule's completion", rule[0], { pulses: [], pops: 1 });
expect("the mix's is not the tap's", JSON.stringify(mix[0]) === JSON.stringify(tap[0]), false);

// Repeats never grow: the third completion plays exactly what the first did.
for (const [label, run] of [["tap", tap], ["mix", mix], ["rule", rule]] as const) {
  for (const p of run) expect(`${label}: a repeat plays the first's effect`, p, run[0]);
}
