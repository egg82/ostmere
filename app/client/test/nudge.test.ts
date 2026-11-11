// The idle nudge (ui/nudge.ts): after NUDGE_IDLE_S without a touch, the card the pick gives takes the one glow, unless
// something else has it; any touch starts the wait again.
import { install } from "./fake-dom";
import { Glow } from "../src/ui/fresh";
import { NUDGE_IDLE_S, IdleNudge } from "../src/ui/nudge";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

let now = 0;
Object.assign(globalThis, { performance: { now: () => now } });
const touches = new Map<string, () => void>();
Object.assign(document, {
  addEventListener: (t: string, f: () => void) => void touches.set(t, f),
});

const card = document.createElement("div");
const glow = new Glow();
const nudge = new IdleNudge(glow, () => card);
const glowing = (): boolean => card.classList.contains("glow");

now = NUDGE_IDLE_S * 1000 - 1;
nudge.tick();
expect("not before the wait", glowing(), false);
now = NUDGE_IDLE_S * 1000;
nudge.tick();
expect("after the wait: the glow", glowing(), true);

glow.clear(card);
touches.get("pointerdown")?.();
now += NUDGE_IDLE_S * 1000 - 1;
nudge.tick();
expect("a touch starts the wait again", glowing(), false);
now += 1;
nudge.tick();
expect("and it comes round again", glowing(), true);

const other = new Glow();
const taken = document.createElement("div");
document.body.append(taken);
other.offer(taken);
const held = new IdleNudge(other, () => card);
card.classList.remove("glow");
now += NUDGE_IDLE_S * 1000;
held.tick();
expect("not while another control has the glow", glowing(), false);
