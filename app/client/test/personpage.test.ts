// A person's page (ui/personpage.ts), opened by Change on their Town row: their cards in full, their mix (once joined),
// and the rules that run them. A ruled lane before the join and the town's people after it.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { dayTwoStep } from "../fixtures/daytwo";
import { townStep } from "../fixtures/town";
import type { Decision, Mix, View } from "../src/api/types";
import { ruledLaneOf } from "../src/game/lanes";
import { taskRules } from "../src/game/orders";
import { NewMarks } from "../src/game/marks";
import { Cards } from "../src/ui/cards";
import { pickRow } from "../src/ui/cardpick";
import { LaneRows } from "../src/ui/lanerows";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  return fakeDocument.body.firstElementChild as FakeEl;
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
const { ctx: dayCtx } = testContext();
const CHOP = 4;

{  // a lane before the join: its cards in full, no mix, the rules that run it, each opening the Rules tab
  const { root, page, got, ctx } = rig(ruled);
  expect("closed until Change", page.hidden, true);
  root.querySelector(".lane-change")?.click();
  expect("Change opens the page", page.hidden, false);
  expect("it is the person's", page.querySelector(".town-title")?.textContent, "Helper");
  expect("a face per task", page.querySelectorAll(".person-cards .card").map((c) => c.dataset.card), ["chop", "haul"]);
  expect("a face only: no tap", page.querySelectorAll(".person-cards .card-tap").every((b) => b.disabled === true), true);
  expect("no mix before the join", page.querySelector(".person-mix")?.hidden, true);
  const want = taskRules(ruled).filter((i) => ruledLaneOf(ctx.catalog, ruled.orders[i]!) === "helper");
  expect("a row per rule that taps their cards", want.length > 1 && page.querySelectorAll(".person-rules .task-rule").length, want.length);
  page.querySelectorAll(".person-rules .rule-cond").find((b) => b.textContent?.includes("Chop"))?.click();
  expect("a rule opens in the Rules tab", got.opened[0], { lane: "helper", rule: CHOP });
}

{  // a joined person: their cards, their split and nothing of the others'; a change keeps the rest of the mix, with no Save
  const both = townStep("town").view;
  const { root, page, got } = rig(both);
  const changes = root.querySelectorAll(".person-change");
  expect("a Change per person", changes.length, 2);
  changes[0]!.click();
  expect("the page opens", page.hidden, false);
  expect("their cards", page.querySelectorAll(".person-cards .card").map((c) => c.dataset.card), ["chop", "haul"]);
  expect("only their split", texts(page.querySelectorAll(".person-mix .share-key-item")), ["Chop logs 60%", "Haul water 30%", "Helper, idle 10%"]);
  expect("no Save", page.querySelectorAll(".editor-buttons .primary").length, 0);
  page.querySelectorAll(".person-cards .card-tap")[1]?.click();
  const mix = saved(got.decided[0]);
  expect("the whole mix is sent, the mason's shares in it", mix?.components.map((c) => (c.kind === "card_share" ? c.card : null)), ["chop", "hew", "carve"]);
  expect("the page stays open", page.hidden, false);
}

{  // a person with no task rule: before the join their page offers Change (it sets the lane's task); once joined it does not, their split is the bar
  const noRules = (v: View): View => {
    const keep = v.orders.map((o) => o.then.kind !== "tap_card");
    return { ...v, orders: v.orders.filter((_, i) => keep[i]), orders_on: v.orders_on.filter((_, i) => keep[i]), order_states: v.order_states.filter((_, i) => keep[i]), order_guards: v.order_guards.filter((_, i) => keep[i]), order_doing: v.order_doing.filter((_, i) => keep[i]) };
  };
  const labels = (page: FakeEl): string[] => texts(page.querySelectorAll(".person-rules > button"));
  const before = rig(noRules(ruled));
  before.root.querySelector(".lane-change")?.click();
  expect("before the join: Change sets the lane's task", labels(before.page).includes("Change"), true);
  const joined = rig(noRules(townStep("town").view));
  joined.root.querySelectorAll(".person-change")[0]!.click();
  expect("joined: no second Change, the rule button stays", [labels(joined.page).includes("Change"), labels(joined.page).some((t) => t.includes("New rule"))], [false, true]);
}

{  // the dot on a joined person's Change clears once their page is opened
  const both = townStep("town").view;
  const { root, ctx } = rig(both);
  expect("dotted", root.querySelectorAll(".person-change .new-dot").length > 0, true);
  root.querySelectorAll(".person-change")[0]!.click();
  const mine = both.cards.filter((c) => ctx.catalog.laneOf(c.card) === "helper");
  expect("their tasks are seen", mine.every((c) => ctx.keeps.laneTaskSeen(c.card)), true);
}

{  // the page is the one editor: a phone seats `.editor` over the screen, so a part inside it that is one too covers the cards
  const { root, page } = rig(townStep("town").view);
  root.querySelectorAll(".person-change")[0]!.click();
  expect("the page is the editor", page.querySelector(".person-page")?.classList.contains("editor") ?? page.classList.contains("editor"), true);
  expect("nothing inside it is another", page.querySelectorAll(".editor").length, 0);
}

{  // a card's face reads as the Tasks page draws it: the same card, as the panel and as the page's face
  const line = ruled.ledger[0]!;
  const need = { store: line.store, quantity: 3000, segment: line.segment, gate: null, makers: [], spent: false };
  const hands = ruled.cards.find((c) => !dayCtx.catalog.ruled(c.card) && c.tap_s !== null);
  if (!hands) throw new Error("fixture has no hands card");
  const view: View = { ...ruled, cards: ruled.cards.map((c) => (c.card === hands.card ? { ...c, needs: [need] } : c)) };
  const panel = new Cards(dayCtx, new NewMarks());
  const panelRoot = mounted(panel.root);
  panel.update(view, null);
  panel.tick(view.at);
  const shown = panelRoot.querySelector(`.card[data-card="${hands.card}"]`);
  const page = mounted(pickRow(dayCtx, view.cards.find((c) => c.card === hands.card)!, view));
  const needs = (n: FakeEl | null): string[] => (n?.querySelectorAll(".card-need") ?? []).map((x) => x.textContent ?? "");
  expect("the panel draws the need (control)", needs(shown).length, 1);
  expect("the face draws the same need", needs(page), needs(shown));
  expect("and its time", page.querySelector(".card-foot")?.textContent, shown?.querySelector(".card-foot")?.textContent);
}
