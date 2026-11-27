// A person's lane heading in a rule editor's task list is the label the save holds: descriptive until the game says the
// name (a later label's unlock), the person's name after. The fixture's helper lane takes its later label with `yard`.
import { fixtureStep } from "../fixtures/steps";
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/page/catalog";
import { sectioned } from "../src/game/cards/cardsections";
import type { View } from "../src/api/types";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const base = fixtureStep("mid", 1_000).view;
const told: View = { ...base, unlocked: [...base.unlocked, { category: "feature", id: "yard" }] };
const headingOf = (view: View | undefined): string[] => sectioned(catalog, ["chop"], (c) => c, view).map((g) => g.heading);

expect("control: the lane's own label stands before the name is told", headingOf(base), ["Helper"]);
expect("control: no view, the first label", headingOf(undefined), ["Helper"]);
expect("the heading after the telling is the later label", headingOf(told), ["Helper, settled"]);
