// A role's slot ({<role>}, contract/casting.txt "CASTING") is the cast lane's name, read from the view's unlocked features at each
// draw: it stays as written while no feature of the role is held, follows the one held, and is lowercased in a line.
import { fixtureContent } from "../../../fixtures/content";
import { Text } from "../../../src/game/page/text";

function expect(label: string, got: unknown, want: unknown): void {
  if (got !== want) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const lane = (id: string, name_key: string) => ({ lane: id, label_key: `lane.${id}`, ruled: true, station: false, later_labels: [], name_key, told: "mention" as const, pooled: false, group: null, tied: null });
const content = {
  ...fixtureContent,
  lane_infos: [...fixtureContent.lane_infos, lane("n1", "name_n1"), lane("n2", "name_n2")],
  cast_infos: [{ role: "scout", label_key: "role.scout", lanes: [{ lane: "n1", feature: "scout_n1" }, { lane: "n2", feature: "scout_n2" }] }],
  text_entries: [...fixtureContent.text_entries,
    { key: "name_n1", text: "Ada" }, { key: "name_n2", text: "Bram" },
    { key: "label.scout", text: "{scout}'s watch" }, { key: "line.scout", text: "{scout} comes back." },
    { key: "label.plain", text: "{n1}'s watch" }, { key: "role.scout", text: "Scout" }],
  line_infos: [...fixtureContent.line_infos, { key: "line.scout", kind: "story" as const, cause: null, person: false, mention: null }],
};
const feature = (id: string) => ({ category: "feature" as const, id });
const text = new Text(content);

expect("before the cast the slot is as written", text.get("label.scout"), "{scout}'s watch");
text.cast([feature("other")]);
expect("a feature of no role casts no one", text.get("label.scout"), "{scout}'s watch");
text.cast([feature("scout_n2")]);
expect("the cast lane's name fills it", text.get("label.scout"), "Bram's watch");
expect("in a line it is lowercased", text.get("line.scout"), "bram comes back.");
expect("a lane's own slot is unchanged", text.get("label.plain"), "Ada's watch");
text.cast([]);
expect("a view without it takes the name back", text.get("label.scout"), "{scout}'s watch");
