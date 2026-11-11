// A one-shot animation class goes once it has played (ui/dom.ts pulse): left on, the Tasks tab shown again replays
// every card's arrival.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { pulse } from "../src/ui/dom";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const card = document.createElement("div");
card.append(document.createElement("span"));
document.body.replaceChildren(card);
const fakeCard = fakeDocument.querySelector("div");
const fakeChild = fakeDocument.querySelector("span");
if (!fakeCard || !fakeChild) throw new Error("the fake DOM holds the card and its child");
pulse(card, "arrive");
expect("on while it plays", card.classList.contains("arrive"), true);
fakeChild.dispatchEvent(new FakeEvent("animationend"));
expect("a child's animation ending leaves it on", card.classList.contains("arrive"), true);
fakeCard.dispatchEvent(new FakeEvent("animationend"));
expect("off once its own has played", card.classList.contains("arrive"), false);
pulse(card, "arrive");
expect("a second pulse plays again", card.classList.contains("arrive"), true);
