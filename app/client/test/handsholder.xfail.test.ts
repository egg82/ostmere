// The mix bar shows what the hands are doing (docs/design/opening-screen.md, "The hands strip"; issue 104): while a
// queued step runs on the hands over the player's mix, the bar is that card, one full segment in its hue, its legend
// naming it with its time left, and the mix's name slot says what the hands go back to. When it lands, the mix returns.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
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
