// A standing action's label is the one the view has, as a lane's (Catalog.runnerLabel, StandingInfo.later_labels): the last
// later label whose unlock the view holds, else its own; its own without a view. A card's label is its own.
import { Catalog } from "../../../src/game/page/catalog";
import { fixtureContent } from "../../../fixtures/content";
import { fixtureStep } from "../../../fixtures/steps";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const feature = (id: string) => ({ category: "feature" as const, id });
const content = {
  ...fixtureContent,
  standing_infos: fixtureContent.standing_infos.map((s) => ({ ...s, later_labels: [
    { after: feature("named"), label_key: "standing.named" }, { after: feature("renamed"), label_key: "standing.renamed" }] })),
  text_entries: [...fixtureContent.text_entries, { key: "standing.named", text: "Named" }, { key: "standing.renamed", text: "Renamed" }],
};
const catalog = new Catalog(content);
const runner = content.standing_infos[0]!.action;
const own = catalog.label(content.standing_infos[0]!.label_key);
const before = fixtureStep("mid", 100).view;
const named = { ...before, unlocked: [...before.unlocked, feature("named")] };
const renamed = { ...named, unlocked: [...named.unlocked, feature("renamed")] };

expect("no view: its own label", catalog.runnerLabel(runner), own);
expect("nothing unlocked: its own label", catalog.runnerLabel(runner, before), own);
expect("one unlocked: that later label", catalog.runnerLabel(runner, named), "Named");
expect("both unlocked: the last", catalog.runnerLabel(runner, renamed), "Renamed");
const card = content.card_infos[0]!.card;
expect("a card: its own label, whatever the view", catalog.runnerLabel(card, renamed), catalog.cardLabel(card));
