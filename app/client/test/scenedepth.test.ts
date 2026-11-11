// The scene draws layers lower on the ground over higher ones (a figure whose feet are above a prop's base stands behind
// it), and never moves a layer that has no base.
import { depthOrder, type SceneLayer } from "../src/scene/manifest";

const layer = (id: string, base?: number): SceneLayer => ({ id, src: `${id}.png`, x: 0, y: 0, when: "always", ...(base === undefined ? {} : { base }) });
const ids = (layers: SceneLayer[]) => layers.map((l) => l.id).join(" ");
function expectOrder(got: SceneLayer[], want: string): void {
  if (ids(got) !== want) throw new Error(`draw order "${ids(got)}", want "${want}"`);
}

// The reported case: the figure comes in at the gap (feet 171) behind the fireback (base 190), though it is listed after it.
const camp = [layer("ruin"), layer("fireback", 190), layer("figure_gathering", 171), layer("firelight")];
expectOrder(depthOrder(camp), "ruin figure_gathering fireback firelight");

// A figure in front of the prop (feet below its base) keeps its place over it.
expectOrder(depthOrder([layer("ruin"), layer("fireback", 190), layer("figure_by_fire", 235)]), "ruin fireback figure_by_fire");

// Layers with no base keep their slots: ground first, lights last, whatever the based layers do between them.
expectOrder(depthOrder([layer("ruin"), layer("cleared"), layer("b", 200), layer("a", 100), layer("glow")]), "ruin cleared a b glow");

// Equal bases keep manifest order (a layer drawn on another's art takes its parent's base).
expectOrder(depthOrder([layer("lean_to", 246), layer("roof_ash", 246), layer("pelt", 246)]), "lean_to roof_ash pelt");

// A manifest with no bases is drawn as listed, and the input is not reordered.
const plain = [layer("c"), layer("a"), layer("b")];
expectOrder(depthOrder(plain), "c a b");
expectOrder(plain, "c a b");

// Control: the check can fail. The listed order puts the figure over the fireback, which the sort must not leave.
if (ids(camp) === ids(depthOrder(camp))) throw new Error("control: the sort left the camp as listed");
