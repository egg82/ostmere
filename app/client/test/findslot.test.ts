// A find's amount ({found}, CONTRACT.txt "Text and numbers") is filled in the line its FindInfo names, from the served
// quantity in whole items; the same slot in any other text is left as written.
import { fixtureContent } from "../fixtures/content";
import { Text } from "../src/game/text";

function expect(label: string, got: unknown, want: unknown): void {
  if (got !== want) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const text = new Text(fixtureContent);
const q = fixtureContent.scales.quantity_per_item;
expect("the find's line holds its amount", text.get("line.find"), "[fixture] a find: 12 of them, dry.");

const served = { ...fixtureContent, find_infos: [{ line_key: "line.find", store: "wood", quantity: 7 * q + 3 }] };
expect("a part of an item is not counted", new Text(served).get("line.find"), "[fixture] a find: 7 of them, dry.");

const other = { ...fixtureContent, text_entries: [...fixtureContent.text_entries, { key: "line.other", text: "{found} here." }] };
expect("the slot in another text is left", new Text(other).get("line.other"), "{found} here.");
