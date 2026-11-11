// A layer marked `front` is drawn in the front pass, over the lights; `ungraded` stays the lights' pass, and front wins
// when both are set.
import { isGlow, passOf, type SceneLayer } from "../src/scene/manifest";

const layer = (id: string, extra: Partial<SceneLayer> = {}): SceneLayer => ({ id, src: `${id}.png`, x: 0, y: 0, when: "always", ...extra });
function expectPass(l: SceneLayer, want: string): void {
  if (passOf(l) !== want) throw new Error(`${l.id} drawn in "${passOf(l)}", want "${want}"`);
}

expectPass(layer("ground"), "base");
expectPass(layer("fire_lit", { ungraded: true }), "ungraded");
expectPass(layer("figure_n3_at_edge", { front: true }), "front");
expectPass(layer("both", { front: true, ungraded: true }), "front");

// Control: the check can fail. A front layer must not be left in the lights' pass.
if (passOf(layer("figure", { front: true })) === passOf(layer("fire_lit", { ungraded: true }))) throw new Error("control: front and ungraded share a pass");

// The glows over the scene (ungraded, blended) are the lights figures in front still get; the lit pieces are not.
if (!isGlow(layer("firelight", { ungraded: true, blend: "screen" }))) throw new Error("a blended ungraded layer is a glow");
if (isGlow(layer("fire_lit", { ungraded: true }))) throw new Error("an unblended ungraded layer is not a glow");
if (isGlow(layer("frost", { blend: "screen" }))) throw new Error("a graded layer is not a glow");
