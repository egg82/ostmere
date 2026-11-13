// No text sits inside a share bar (docs/design/redesign.md, "Phone frame"; ui/sharebar.ts): the segments are hue alone,
// and a legend beneath names each one with its share, in the bar's order, following a divider as it moves.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { ShareBar } from "../src/ui/sharebar";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const sent: number[][] = [];
const bar = new ShareBar("slim", 10000, (bp) => `${bp / 100}%`, { commit: (s) => sent.push(s) });
document.body.append(bar.root);
const seg = (key: string, label: string, struck = false) => ({ key, label, hue: 0, struck });
const segText = (): string[] => Array.from(bar.root.querySelectorAll(".share-seg"), (n) => n.textContent ?? "");
const legend = (): string[] => Array.from(bar.root.querySelectorAll(".share-key-item"), (n) => n.textContent ?? "");

bar.set([seg("a", "Alpha"), seg("b", "Beta", true)], [6000, 4000]);
expect("a segment per share", segText().length, 2);
expect("and no text in any of them", segText().every((t) => t === ""), true);
expect("the legend names each, name then share, in order", legend(), ["Alpha 60%", "Beta 40%"]);
expect("a struck segment is struck in the legend too", Array.from(bar.root.querySelectorAll(".share-key-item.struck"), (n) => n.textContent), ["Beta 40%"]);

fakeDocument.querySelector(".share-divider")?.dispatchEvent(new FakeEvent("keydown", { key: "ArrowRight" }));
expect("a divider moved by a key is sent", sent, [[6100, 3900]]);
expect("and the legend follows it", legend(), ["Alpha 61%", "Beta 39%"]);
