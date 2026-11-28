// A job first offered to a person of the town is said once in the story (game/town/newjobs.ts): one line for a person's one
// card, one naming the job when it fans out over several people, one for a person's several jobs, one for the town's
// several; never one per lane; none for a card that arrives at work,
// for a person who joins in the same step, or on the first view.
import { townStep } from "../../../fixtures/town";
import { fixtureContent } from "../../../fixtures/content";
import type { Content, View } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { jobLine, newJobs } from "../../../src/game/town/newjobs";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const base = fixtureContent.card_infos.find((c) => c.card === "haul");
if (!base) throw new Error("the fixture should carry the helper's Haul card");
const extra = (id: string, lane: string, label_key = "card.haul") => ({ ...base, card: id, lane, label_key });
const content: Content = {
  ...fixtureContent,
  card_infos: [...fixtureContent.card_infos, extra("mend", "helper", "card.chop"), extra("mend2", "helper", "card.fetch"), extra("lay", "mason", "card.chop"), extra("chop2", "hands")],
};
const catalog = new Catalog(content);
const town = townStep("town").view;
const haul = town.cards.find((c) => c.card === "haul");
if (!haul) throw new Error("the town fixture should carry Haul");
const add = (v: View, ...ids: string[]): View => ({ ...v, cards: [...v.cards, ...ids.map((id) => ({ ...haul, card: id, share_bp: 0, run: null }))] });
const helper = catalog.laneLabel("helper", town);

expect("first view: nothing offered", newJobs(catalog, null, add(town, "mend")), []);
expect("nothing new", newJobs(catalog, town, town), []);

const one = add(town, "mend");
expect("one card: one job", newJobs(catalog, town, one), [{ label: "card.chop", card: "mend", lanes: ["helper"] }]);
expect("one card: its own line", jobLine(catalog, one, newJobs(catalog, town, one)), `${helper} has something new to try: Chop logs.`);

const fanned = add(town, "mend", "lay");
expect("one job on two lanes: one entry", newJobs(catalog, town, fanned).map((j) => [j.label, j.lanes]), [["card.chop", ["helper", "mason"]]]);
expect("one job on two lanes: one line naming the job", jobLine(catalog, fanned, newJobs(catalog, town, fanned)), "Something new for the town to try: Chop logs.");

const two = add(town, "mend", "mend2");
expect("two jobs for one person: one line, no job named", jobLine(catalog, two, newJobs(catalog, town, two)), `${helper} has a few new things to try.`);

const both = add(town, "mend2", "lay");
expect("two jobs for two people: one line for the town", jobLine(catalog, both, newJobs(catalog, town, both)), "The town has a few new things to try.");
expect("no job: no line", jobLine(catalog, town, newJobs(catalog, town, town)), null);

const installed: View = { ...one, mixes: [{ ...(one.mixes[0] ?? ({} as never)), components: [{ kind: "card_share", card: "mend", share_bp: 5000 }] }] };
expect("a card that arrives in a mix is no offer", newJobs(catalog, town, installed), []);

expect("a player's card is no offer", newJobs(catalog, town, { ...town, cards: [...town.cards, { ...haul, card: "chop2", share_bp: 0 }] }), []);

// A person with a name is named by it, never by their lane's label: a label titles a row ("…'s hands") and read as a
// sentence's subject it says a crew member still works a split of their own.
const namedContent: Content = {
  ...content,
  lane_infos: content.lane_infos.map((l) => (l.lane === "helper" ? { ...l, name_key: "name.helper" } : l)),
  text_entries: [...content.text_entries, { key: "name.helper", text: "Ada" }],
};
const namedCatalog = new Catalog(namedContent);
expect("a named person: their name, not the lane's label", jobLine(namedCatalog, one, newJobs(namedCatalog, town, one)), "Ada has something new to try: Chop logs.");
expect("a named person's several jobs: their name", jobLine(namedCatalog, two, newJobs(namedCatalog, town, two)), "Ada has a few new things to try.");
