// The Town view's groups and a group's page (contract/groups.txt, "GROUPS"; ui/town/townstrip.ts, ui/town/personpage.ts, ui/town/groupmembers.ts):
// a row per person who runs their own split and one per group with a member; a group of one draws as that person; a group of
// two takes its label, a count and one bar; a member mid one-off drops the crew; a marked person who names the group is not in it.
// The views are fixtures/groups.ts's: four marked people, a pooled lane "crew" and its members nan and ole.
import { type FakeEl, install } from "./fake-dom";
import { groupsView, withGroups } from "../fixtures/groups";
import { Catalog } from "../src/game/catalog";
import { pageRig, savedMix, shareOf, texts } from "./personrig";
import type { View } from "../src/api/types";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(withGroups());
const rig = (view: View, c = catalog) => pageRig(view, c);
const names = (root: FakeEl): string[] => texts(root.querySelectorAll(".town-person .town-name"));
const bar = (row: FakeEl): number => row.querySelectorAll(".town-seg").reduce((n, s) => n + Number(s.style.flexGrow), 0);
/** The view with `lane` set as the mark says (LaneBar.own_split). */
const marked = (view: View, lane: string, own: boolean): View => ({ ...view, lanes: view.lanes.map((l) => (l.lane === lane ? { ...l, own_split: own } : l)) });

{  // a group of two: the group's label, both faces, the count, one bar of the whole of each member's time; four marked people keep their rows
  const { root } = rig(groupsView());
  expect("rows: the marked people, then the group", names(root), ["Helper", "Mason", "Smith", "Scribe", "Workers"]);
  const row = root.querySelectorAll(".town-person").find((r) => r.dataset.lane === "crew") as FakeEl;
  expect("the count", row.querySelector(".town-count")?.textContent, "2 people");
  expect("the members' faces", texts(row.querySelectorAll(".ask-face")), ["N", "O"]);
  expect("one split: the group's shares, each of each member's time, and the idle rest", texts(row.querySelectorAll(".town-key-item")), ["Dig ditches 60%", "Sweep paths 30%", "Workers, idle 10%"]);
  expect("the bar is one whole", bar(row), 10000);
  expect("no count on a person", root.querySelectorAll(".town-person").filter((r) => r.dataset.lane !== "crew").map((r) => r.querySelector(".town-count")?.textContent), ["", "", "", ""]);
  expect("no lane-run-by-rules row for the group or its members", root.querySelectorAll(".lane-row").length, 0);
}

{  // a group of one draws as that person: their name, face and no count; a second member changes the name and adds the count, not the split
  const one = groupsView();
  const alone: View = { ...one, unlocked: one.unlocked.filter((u) => !(u.category === "joined" && u.id === "ole")) };
  const a = rig(alone).root.querySelectorAll(".town-person").find((r) => r.dataset.lane === "crew") as FakeEl;
  expect("the member's name", a.querySelector(".town-name")?.textContent, "Nan");
  expect("the member's face", texts(a.querySelectorAll(".ask-face")), ["N"]);
  expect("no count", a.querySelector(".town-count")?.textContent, "");
  expect("the idle part is the member's", texts(a.querySelectorAll(".town-key-item")), ["Dig ditches 60%", "Sweep paths 30%", "Nan, idle 10%"]);
  const { rows, root } = rig(alone);
  const bars = (): number[] => (root.querySelectorAll(".town-person").find((r) => r.dataset.lane === "crew") as FakeEl).querySelectorAll(".town-seg").map((s) => Number(s.style.flexGrow));
  const before = bars();
  rows.update(one);
  expect("the second member: the group's label", names(root).at(-1), "Workers");
  expect("the split does not move", bars(), before);
}

{  // a group of one's page is titled with the member's name; a group of two's with the group's
  const one = groupsView();
  const alone: View = { ...one, unlocked: one.unlocked.filter((u) => !(u.category === "joined" && u.id === "ole")) };
  expect("titled with the member", texts(rig(alone).open(4).querySelectorAll(".editor-head .town-title")), ["Nan"]);
  expect("titled with the group", texts(rig(one).open(4).querySelectorAll(".editor-head .town-title")), ["Workers"]);
}

{  // the group's page: its split as the one bar, "each of 2" beside it, its tasks as faces with the saved shares, a line a member
  const { open, face } = rig(groupsView());
  const page = open(4);
  expect("the split is the group's, per member", texts((page.querySelector(".person-mix") as FakeEl).querySelectorAll(".share-key-item")), ["Dig ditches 60%", "Sweep paths 30%", "Workers, idle 10%"]);
  expect("each of the crew", page.querySelector(".person-each")?.textContent, "each of 2");
  expect("the group's tasks, not the members'", page.querySelectorAll(".person-cards .card").map((c) => c.dataset.card), ["dig", "sweep"]);
  expect("the faces carry the per-member share", [shareOf(face("dig")), shareOf(face("sweep"))], ["60%", "30%"]);
  expect("a line per member", texts(page.querySelectorAll(".group-line .town-name")), ["Nan", "Ole"]);
  expect("each is on the split", texts(page.querySelectorAll(".group-doing")), ["Dig ditches 60%, Sweep paths 30%", "Dig ditches 60%, Sweep paths 30%"]);
  expect("no rules on a group's page", (page.querySelector(".person-rules") as FakeEl).children.length, 0);
}

{  // a task joins the group's split and leaves it by a tap, sent as the town's mix with the group's shares changed
  const { open, face, got } = rig(groupsView());
  open(4);
  face("sweep").querySelector(".card-tap")?.click();
  const sent = savedMix(got.decided[0]);
  expect("sweep leaves the group's split", sent?.components.filter((c) => c.kind === "card_share").map((c) => (c.kind === "card_share" ? c.card : "")), ["chop", "haul", "hew", "carve", "forge", "copy", "dig"]);
}

{  // a member mid one-off: the crew drops to 1, the member's line is the one-off with its time left and "then {split}", the split stays
  const base = groupsView(1);
  const busy: View = { ...base, lanes: base.lanes.map((l) => (l.lane === "ole" ? { ...l, running_card: "errand_o", completes_at: base.at + 30 } : l)) };
  const { open, root } = rig(busy);
  const page = open(4);
  expect("the crew drops", page.querySelector(".person-each")?.textContent, "each of 1");
  expect("the split stays", texts((page.querySelector(".person-mix") as FakeEl).querySelectorAll(".share-key-item")), ["Dig ditches 60%", "Sweep paths 30%", "Workers, idle 10%"]);
  const lines = page.querySelectorAll(".group-line");
  expect("the other member is on the split", lines[0]?.querySelector(".group-doing")?.textContent, "Dig ditches 60%, Sweep paths 30%");
  expect("the member on a one-off: it with its time left", lines[1]?.querySelector(".group-doing")?.textContent, "Fetch a load 30 s");
  expect("and the split they go back to", lines[1]?.querySelector(".group-then")?.textContent, "then Dig ditches 60%, Sweep paths 30%");
  expect("the row still counts both", (root.querySelectorAll(".town-person").find((r) => r.dataset.lane === "crew") as FakeEl).querySelector(".town-count")?.textContent, "2 people");
  expect("their one-off is not tappable while one is held", lines[1]?.querySelector(".group-task")?.disabled, true);
}

{  // a member's own one-off is tapped from their line
  const { open, got } = rig(groupsView());
  open(4).querySelectorAll(".group-line").find((l) => l.dataset.lane === "nan")?.querySelector(".group-task")?.click();
  expect("tap_card of the member's own card", got.decided, [{ kind: "tap_card", card: "errand_n" }]);
}

{  // a marked person who names the group is not a member: they keep their own row and are not counted
  const { root } = rig(marked(groupsView(), "nan", true));
  expect("nan has a row of their own, the group is ole alone", names(root), ["Helper", "Mason", "Smith", "Scribe", "Nan", "Ole"]);
  const row = root.querySelectorAll(".town-person").find((r) => r.dataset.lane === "crew") as FakeEl;
  expect("no count: a group of one", row.querySelector(".town-count")?.textContent, "");
  const nan = root.querySelectorAll(".town-person").find((r) => r.dataset.lane === "nan") as FakeEl;
  expect("nan's split is their own, not the group's", texts(nan.querySelectorAll(".town-key-item")), ["Nan, idle 100%"]);
}

{  // a big group: the head count, its names a tap away
  const big = new Catalog({ ...withGroups(), lane_infos: withGroups().lane_infos.map((l) => (l.lane === "smith" || l.lane === "scribe" ? { ...l, group: "crew" } : l)) });
  const { open } = rig(marked(marked(groupsView(4), "smith", false), "scribe", false), big);
  const page = open(2);
  expect("the count is on the page", page.querySelector(".group-count")?.textContent, "4 people");
  expect("names are a tap away", page.querySelector(".group-lines")?.hidden, true);
  page.querySelector(".group-count")?.click();
  expect("a tap shows them", [page.querySelector(".group-lines")?.hidden, texts(page.querySelectorAll(".group-line .town-name"))], [false, ["Smith", "Scribe", "Nan", "Ole"]]);
}

{  // the person a group is tied to: one line on its page naming them, only once they are in the town, never when none is set
  const tiedLine = (view: View, c = catalog): string[] => texts(rig(view, c).open(4).querySelectorAll(".group-tied").filter((n) => !n.hidden));
  expect("set and met: the line", tiedLine(groupsView()), ["With Nan"]);
  const none = new Catalog({ ...withGroups(), lane_infos: withGroups().lane_infos.map((l) => (l.lane === "crew" ? { ...l, tied: null } : l)) });
  expect("unset: no line", tiedLine(groupsView(), none), []);
  const view = groupsView();
  const unmet: View = { ...view, unlocked: view.unlocked.filter((u) => !(u.category === "joined" && u.id === "nan")) };
  expect("set, not yet met: no line", tiedLine(unmet), []);
  const apart = new Catalog({ ...withGroups(), lane_infos: withGroups().lane_infos.map((l) => (l.lane === "crew" ? { ...l, tied: "smith" } : l)) });
  expect("tied to a person who is not a member: still named", tiedLine(groupsView(), apart), ["With Smith"]);
}
