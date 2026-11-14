// The press (docs/design/redesign.md, "Feel"): on pointer-down a card sinks 2px onto its shadow, a step lighter, and on
// release it settles back in 160ms with a little overshoot. A refused card goes down too: a control that does not move
// reads as a bug. A card that cannot be tapped (its lane busy, or done) stays put. Reduced motion keeps the colour and
// drops the sink. The sink and the settle are CSS, so this reads the rules for them.
import { readFileSync } from "node:fs";
import { fakeDocument, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import { makeRow } from "../src/ui/cardrow";
import { WhenReady } from "../src/ui/whenready";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const { ctx } = testContext();
const card = fixtureStep("mid", 100).view.cards[0];
if (!card) throw new Error("the fixture has no card");
const row = makeRow(ctx, new WhenReady(ctx), card);
const held = (): boolean => row.node.classList.contains("pressed");
document.body.replaceChildren(row.node);
const tap = fakeDocument.body.querySelector(".card-tap");
if (!tap) throw new Error("no tap target");

tap.dispatchEvent(pointer("pointerdown", 5, 5));
expect("down: it sinks", held(), true);
tap.dispatchEvent(pointer("pointerup", 5, 5));
expect("up: it settles back", held(), false);
tap.dispatchEvent(pointer("pointerdown", 5, 5));
tap.dispatchEvent(pointer("pointercancel", 5, 5));
expect("a cancelled press settles back too", held(), false);
tap.dispatchEvent(pointer("pointerdown", 5, 5));
tap.dispatchEvent(pointer("pointerleave", 5, 5));
expect("and one dragged off the card", held(), false);

row.tap.click();
expect("the click plays no second press of its own", row.node.classList.contains("press"), false);

row.tap.disabled = true;
tap.dispatchEvent(pointer("pointerdown", 5, 5));
expect("a card that cannot be tapped stays put", held(), false);

const css = readFileSync("src/game.css", "utf8");
const rule = (selector: string, from = 0): string => {
  const start = css.indexOf(`${selector} {`, from);
  if (start < 0) throw new Error(`no rule for ${selector}`);
  return css.slice(start, css.indexOf("}", start));
};
const tokens = rule(":root");
expect("the timings are the design's tokens", [/--press-ms: 60ms/.test(tokens), /--settle-ms: 160ms/.test(tokens), /--settle-ease: cubic-bezier\(\.3, ?1\.5, ?\.5, ?1\)/.test(tokens)], [true, true, true]);
const pressed = rule(".card.pressed");
expect("held down: 2px onto its shadow, a step lighter, at the press's pace", [/translateY\(2px\)/.test(pressed), /var\(--press\)/.test(pressed), /var\(--press-ms\)/.test(pressed)], [true, true, true]);
expect("released: it settles at the settle's pace and ease", /transform var\(--settle-ms\) var\(--settle-ease\)/.test(rule("\n.card")), true);
const reduce = css.indexOf("@media (prefers-reduced-motion: reduce)");
const still = rule(".game .card.pressed", reduce);
expect("reduced motion: no sink, the colour kept", [/transform: none/.test(still), /background/.test(still)], [true, false]);
console.log("cardpress: ok");
