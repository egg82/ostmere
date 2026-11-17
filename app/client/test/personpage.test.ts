// A person's page (ui/personpage.ts), opened by Change on their Town row: their cards in full, their mix (once joined),
// and the rules that run them. A ruled lane before the join and the town's people after it.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { dayTwoStep } from "../fixtures/daytwo";
import { townStep } from "../fixtures/town";
import type { Decision, Mix, View } from "../src/api/types";
import { ruledLaneOf } from "../src/game/lanes";
import { taskRules } from "../src/game/orders";
import { LaneRows } from "../src/ui/lanerows";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
function rig(view: View) {
  const { ctx, got } = testContext();
  const rows = new LaneRows(ctx);
  document.body.replaceChildren(rows.root, rows.page.root);
  const root = fakeDocument.body.firstElementChild as FakeEl;
  const page = fakeDocument.body.children[1] as FakeEl;
  rows.update(view);
  return { rows, root, page, got, ctx };
}
const texts = (nodes: FakeEl[]): string[] => nodes.map((n) => n.textContent ?? "");
const saved = (d: Decision | undefined): Mix | null => (d?.kind === "save_mix" ? d.mix : null);

const ruled = dayTwoStep("ruled", 100).view;
const CHOP = 4;

{  // a lane before the join: its cards in full, no mix, the rules that run it, each opening the Rules tab
  const { root, page, got, ctx } = rig(ruled);
  expect("closed until Change", page.hidden, true);
  root.querySelector(".lane-change")?.click();
  expect("Change opens the page", page.hidden, false);
  expect("it is the person's", page.querySelector(".town-title")?.textContent, "Helper");
  expect("a face per task", page.querySelectorAll(".person-cards .card").map((c) => c.dataset.card), ["chop", "haul"]);
  expect("a face only: no tap", page.querySelectorAll(".person-cards .card-tap").every((b) => b.disabled === true), true);
  expect("no mix before the join", page.querySelector(".town-editor")?.hidden, true);
  const want = taskRules(ruled).filter((i) => ruledLaneOf(ctx.catalog, ruled.orders[i]!) === "helper");
  expect("a row per rule that taps their cards", want.length > 1 && page.querySelectorAll(".person-rules .task-rule").length, want.length);
  page.querySelectorAll(".person-rules .rule-cond").find((b) => b.textContent?.includes("Chop"))?.click();
  expect("a rule opens in the Rules tab", got.opened[0], { lane: "helper", rule: CHOP });
}

{  // a joined person: their cards, their part of the town's mix and nothing of the others'; Save keeps the rest of the mix
  const both = townStep("town").view;
  const { root, page, got } = rig(both);
  const changes = root.querySelectorAll(".person-change");
  expect("a Change per person", changes.length, 2);
  changes[0]!.click();
  expect("the page opens", page.hidden, false);
  expect("their cards", page.querySelectorAll(".person-cards .card").map((c) => c.dataset.card), ["chop", "haul"]);
  expect("only their split", texts(page.querySelectorAll(".town-person .town-name")), ["Helper"]);
  page.querySelector(".editor-buttons .primary")?.click();
  const mix = saved(got.decided[0]);
  expect("the whole mix is saved", mix?.components.map((c) => (c.kind === "card_share" ? c.card : null)), ["chop", "haul", "hew", "carve"]);
  expect("the page closes", page.hidden, true);
}

{  // the dot on a joined person's Change clears once their page is opened
  const both = townStep("town").view;
  const { root, ctx } = rig(both);
  expect("dotted", root.querySelectorAll(".person-change .new-dot").length > 0, true);
  root.querySelectorAll(".person-change")[0]!.click();
  const mine = both.cards.filter((c) => ctx.catalog.laneOf(c.card) === "helper");
  expect("their tasks are seen", mine.every((c) => ctx.keeps.laneTaskSeen(c.card)), true);
}
