// A person's name slot ({<lane>}, CONTRACT.txt "Text and numbers") is filled in every text from the lane's name_key:
// as written in a label, lowercased in a line; a slot naming no named lane is left for fill().
import { fixtureContent } from "../fixtures/content";
import { Text } from "../src/game/text";

function expect(label: string, got: unknown, want: unknown): void {
  if (got !== want) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content = {
  ...fixtureContent,
  lane_infos: fixtureContent.lane_infos.map((l) => (l.lane === "helper" ? { ...l, name_key: "name.helper" } : l)),
  text_entries: [
    ...fixtureContent.text_entries.filter((e) => e.key !== "line.1" && e.key !== "lane.helper.later"),
    { key: "name.helper", text: "Agnes" },
    { key: "lane.helper.later", text: "{helper}" },
    { key: "line.1", text: "{helper} looks at the {mason} and the {store}." },
  ],
};
const text = new Text(content);
expect("a label holds the name as written", text.get("lane.helper.later"), "Agnes");
expect("a line holds it lowercased, an unnamed lane's slot and other slots kept", text.get("line.1"), "agnes looks at the {mason} and the {store}.");
expect("fill() still fills the slots left", text.fill("line.1", { store: "wood" }), "agnes looks at the  and the wood.");
expect("content with no name_key is as written", new Text(fixtureContent).get("lane.helper.later"), "Helper, settled");
