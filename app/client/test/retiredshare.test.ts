// A retired card's share in the hands strip (hands.ts; docs/design/opening-screen.md, "The hands strip"): the engine
// keeps it in the greyed mix (docs/decisions.md, "The mix"), but the strip draws the rest of the bar with the
// share divided among them in proportion, never a struck segment holding a share.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import { Hands } from "../src/ui/hands";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const hands = new Hands(testContext().ctx);
const segments = (): string[] => Array.from(hands.root.querySelectorAll(".share-seg"), (n) => `${n.className}|${(n as HTMLElement).style.width}`);

hands.update(fixtureStep("mid", 100).view);
expect("running: both cards, by their shares", segments().map((s) => s.split("|")[1]), ["60%", "40%"]);

hands.update(fixtureStep("greyed", 100).view);
expect("greyed: the retired card is gone, the rest take its share", segments().map((s) => s.split("|")[1]), ["100%"]);
expect("and nothing is struck", segments().some((s) => s.includes("struck")), false);
