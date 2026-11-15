// The mix bar shows what the hands are doing (docs/design/opening-screen.md, "The hands strip"; issue 104): while a
// queued step runs on the hands over the player's mix, the bar is that card, one full segment in its hue, its legend
// naming it with its time left, and the mix's name slot says what the hands go back to. When it lands, the mix returns.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { goalLabel } from "../src/ui/goaltimes";
import { Hands } from "../src/ui/hands";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const LEFT = 130;
const { ctx } = testContext();
const { catalog } = ctx;
const mid = fixtureStep("mid", AT).view;
const mixId = mid.running_mix_id ?? "";

/** mid, with a When ready step of stool running on the hands: the queue's head, the mix's cards yielded to it. */
const held: View = {
  ...mid,
  lanes: mid.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: "stool", completes_at: AT + LEFT } : l)),
  queue: [{ verb: { kind: "tap_card", card: "stool" }, until: { kind: "at_least", watched: { kind: "card_count", card: "stool" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false } }],
  cards: mid.cards.map((c) => (c.card === "stool" ? { ...c, by: "tap" as const, completes_at: AT + LEFT, bar: { start: AT, start_value: 0, rate: 10_000, limit: 25 * 10_000 } }
    : c.by === "mix" ? { ...c, run: "yielded" as const, completes_at: null } : c)),
};

const hands = new Hands(ctx);
const segments = (): string[] => Array.from(hands.root.querySelectorAll(".share-seg"), (n) => `${n.className}|${(n as HTMLElement).style.width}`);
const legend = (): string[] => Array.from(hands.root.querySelectorAll(".share-key-item"), (n) => (n as HTMLElement).textContent ?? "");
const nameSlot = (): string => (hands.root.querySelector(".hands-mix-name") as HTMLElement | null)?.textContent ?? "";

hands.update(held);
hands.tick(AT);
expect("held: one full segment, in the step's hue", segments(), [`share-seg hue-${catalog.rank("stool") % 6}|100%`]);
expect("held: the legend names the step and its time left", legend(), [`${catalog.cardLabel("stool")} ${catalog.format.duration(LEFT)}`]);
expect("held: the name slot says what the hands go back to", nameSlot(), `then ${mixId}`);
expect("held: no paused label", (hands.root.textContent ?? "").includes("paused"), false);
expect("held: next does not name the step that runs", (hands.root.querySelector(".hands-next") as HTMLElement | null)?.hidden ?? true, true);

hands.update(fixtureStep("mid", AT + LEFT).view);
expect("landed: the mix's split returns", segments().map((s) => s.split("|")[1]), ["60%", "40%"]);
expect("landed: the name slot is the mix again", nameSlot(), mixId);

// Every other holder. The strip's words read off the meta row: where the holder lets go, and what comes back after.
/** The text of the first of `sel` under `root` that is not hidden ("" when none is). */
const shownIn = (root: HTMLElement, sel: string): string =>
  (Array.from(root.querySelectorAll(sel), (n) => n as HTMLElement).find((n) => !n.hidden)?.textContent ?? "");
const meta = (): { until: string; then: string; runs: boolean } =>
  ({ until: shownIn(hands.root, ".hands-rule"), then: shownIn(hands.root, ".hands-then"), runs: shownIn(hands.root, ".hands-runs") !== "" });

{  // a goal stint: its mix's split, where it lets go, and the player's mix after it
  const stint = fixtureStep("heldstint", AT).view;
  const row = stint.goal_rows[0];
  hands.update(stint);
  hands.tick(AT);
  expect("stint: the stint's mix is the bar", legend(), [`${catalog.cardLabel("gather")} 100%`]);
  expect("stint: where it lets go, its goal row's words", meta().until, row ? `until ${goalLabel(catalog, row)}` : "no row");
  expect("stint: the player's mix comes back after", meta().then, `then ${stint.active_mix_id}`);
  expect("stint: its own name in the name slot", nameSlot(), stint.running_mix_id);
  expect("stint: no runs while it says where it lets go", meta().runs, false);
}

{  // a rule's mix: as before, plus the player's mix after it
  const rule = fixtureStep("rulemix", AT).view;
  hands.update(rule);
  hands.tick(AT);
  const m = meta();
  expect("rule's mix: where it lets go", m.until.length > 0 && !m.runs, true);
  expect("rule's mix: the player's mix after it", m.then, `then ${rule.active_mix_id}`);
  expect("rule's mix: its name in the name slot", nameSlot(), rule.running_mix_id);

  // with a goal stint queued, the stint's mix is what the rule gives the hands back to
  const gather = rule.mixes.find((x) => x.id !== rule.running_mix_id && x.id !== rule.active_mix_id)?.id ?? "";
  hands.update({ ...rule, queue: [{ verb: { kind: "switch_mix", mix_id: gather }, until: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 30_000, release: 30_000, value_of_cap: false, release_of_cap: false } }] });
  hands.tick(AT);
  expect("rule's mix over a stint: the stint's mix after it", meta().then, `then ${gather}`);

  // a tap over the rule's mix: the tap is the bar, and the rule's mix, which runs, is what comes back
  const tapped: View = { ...rule, lanes: rule.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: "stool", completes_at: AT + LEFT } : l)) };
  hands.update(tapped);
  hands.tick(AT + 10);
  expect("tap over a rule's mix: the tap's bar, its time counting down", legend(), [`${catalog.cardLabel("stool")} ${catalog.format.duration(LEFT - 10)}`]);
  expect("tap over a rule's mix: the rule's mix comes back", nameSlot(), `then ${rule.running_mix_id}`);
  expect("tap over a rule's mix: no until for a tap no rule makes", meta().until, "");
}

{  // a rule's tap on the hands, repeating (no end): the card, no time, and where the rule lets go
  const order = { when: { kind: "at_most" as const, watched: { kind: "store_value" as const, store: "wood" }, value: 10_000, release: 20_000, value_of_cap: false, release_of_cap: false },
    then: { kind: "tap_card" as const, card: "gather" } };
  const ruled: View = { ...mid, orders: [order], orders_on: [true], order_states: ["on"],
    lanes: mid.lanes.map((l) => (l.lane === "hands" ? { ...l, running_card: "gather", completes_at: null, order: 0 } : l)) };
  hands.update(ruled);
  hands.tick(AT);
  expect("rule's tap: the card alone, no time while it repeats", legend(), [`${catalog.cardLabel("gather")} 100%`]);
  expect("rule's tap: where the rule lets go", meta().until.length > 0, true);
  expect("rule's tap: the mix comes back", nameSlot(), `then ${mixId}`);
}
