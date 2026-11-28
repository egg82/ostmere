// A person cast into a role is titled in the Town list by the role's display name (Content.cast_infos' label_key; contract/
// casting.txt, "CASTING"), their own name beside it; a person with no role keeps the lane's label, with no detail.
import { install } from "../../fake-dom";
import { Catalog } from "../../../src/game/page/catalog";
import { fixtureContent } from "../../../fixtures/content";
import { townStep } from "../../../fixtures/town";
import { pageRig } from "./personrig";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content = {
  ...fixtureContent,
  lane_infos: fixtureContent.lane_infos.map((l) => (l.lane === "helper" || l.lane === "mason" ? { ...l, name_key: `name.${l.lane}` } : l)),
  cast_infos: [{ role: "scout", label_key: "role.scout", lanes: [{ lane: "helper", feature: "scout_helper" }, { lane: "mason", feature: "scout_mason" }] }],
  text_entries: [...fixtureContent.text_entries, { key: "role.scout", text: "Scout" }, { key: "name.helper", text: "Ada" }, { key: "name.mason", text: "Bram" }],
};
const view = townStep("town").view;
const rows = (v: typeof view): string[][] => {
  const { root } = pageRig(v, new Catalog(content));
  return root.querySelectorAll(".person-row").map((r) => [r.querySelector(".town-name")?.textContent ?? "", r.querySelector(".town-detail")?.textContent ?? ""]);
};

const before = rows(view);
expect("before the cast each row is the lane's own label, with no detail", before.map((r) => r[1]), ["", ""]);
const cast = rows({ ...view, unlocked: [...view.unlocked, { category: "feature", id: "scout_mason" }] });
expect("the cast person's row is titled by the role, their own name beside it", cast[1], ["Scout", "Bram"]);
expect("the other row is unchanged", cast[0], before[0]);
