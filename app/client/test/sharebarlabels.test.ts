// A share bar's dividers are named for the segment before them, from the mix drawn now, on the first draw and after a
// change of mix (src/ui/sharebar.ts).
import { install } from "./fake-dom";
import { ShareBar } from "../src/ui/sharebar";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const bar = new ShareBar("t", 10000, (bp) => String(bp), { commit: () => undefined });
const names = (): (string | null)[] => Array.from(bar.root.querySelectorAll(".share-divider"), (n) => n.getAttribute("aria-label"));
const seg = (key: string, label: string) => ({ key, label, hue: 0, struck: false });

bar.set([seg("a", "Alpha"), seg("b", "Beta"), seg("c", "Gamma")], [5000, 3000, 2000]);
expect("first draw", names(), ["Alpha", "Beta"]);
bar.set([seg("x", "Xi"), seg("y", "Psi")], [6000, 4000]);
expect("a new mix", names(), ["Xi"]);
