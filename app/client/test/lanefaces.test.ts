// A ruled lane's tasks wear the card face (ui/cardpick.ts, from cardrow.ts and cardneeds.ts) in its editor, Plan names a
// lane task's lane, and a lane's Town row carries a quiet dot while a task of it has not been in front of the player.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { TAUGHT, testContext } from "./context";
import { dayTwoStep } from "../fixtures/daytwo";
import type { View } from "../src/api/types";
import { keepsOf } from "./kept";
import { el } from "../src/ui/dom";
import { LaneRows } from "../src/ui/lanerows";
import { RulesTab } from "../src/ui/rules";
import { StintPlan } from "../src/ui/stintplan";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

const base = dayTwoStep("ruled", 100).view;
const line = base.ledger[0]!;
const need = { store: line.store, quantity: 3000, segment: line.segment, gate: null, makers: [], spent: false };   // authored: the fixture's lane cards take nothing
const ruled: View = { ...base, cards: base.cards.map((c) => (c.card === "chop" ? { ...c, needs: [need] } : c)) };
const laneCards = ruled.cards.filter((c) => c.card === "chop" || c.card === "haul");

{  // the Do list: each task is the card's face, with its time, and its needs where it has them
  const { ctx } = testContext();
  const tab = new RulesTab(ctx);
  const root = mounted(tab.root);
  tab.update(ruled);
  tab.open(ruled, { lane: "helper", rule: 4 });
  const faces = root.querySelectorAll(".pick");
  expect("a face per task", faces.map((f) => f.dataset.card), ["chop", "haul"]);
  for (const f of faces) {
    const card = laneCards.find((c) => c.card === f.dataset.card);
    if (!card || card.tap_s === null) throw new Error("fixture card without a time");
    expect(`${f.dataset.card}: title`, f.querySelector(".card-title")?.textContent, ctx.catalog.cardLabel(card.card));
    expect(`${f.dataset.card}: time`, f.querySelector(".card-foot")?.textContent, ctx.catalog.format.duration(card.tap_s));
    expect(`${f.dataset.card}: needs drawn as the card's`, f.querySelectorAll(".card-need").length > 0 || card.needs.length === 0, true);
  }
  expect("one needs row at least among the tasks", faces.some((f) => f.querySelectorAll(".card-need").length > 0), true);
  expect("the open rule's task is pressed", root.querySelector(".pick[data-card=\"chop\"] .card-tap")?.getAttribute("aria-pressed"), "true");
}

{  // Plan: a lane task names its lane; the player's own task does not
  const { ctx: bare } = testContext();
  const ctx = { ...bare, keeps: keepsOf({ ...TAUGHT, rule_seen: true }) };
  const plan = new StintPlan(ctx, () => undefined);
  const info = ctx.catalog.cards.get("chop");
  if (!info) throw new Error("fixture has no chop");
  const was = info.presentation;
  info.presentation = "craft";   // the fixture's lane tasks are actions, which Plan leaves to the mix; a craft is offered
  const view: View = { ...ruled, queue: [], ended_at: 1 };
  const open = (): FakeEl => {
    (plan as unknown as { step: unknown }).step = { mix: null, after: null };
    const box = el("div");
    box.append(...plan.rows(view));
    return mounted(box);
  };
  const rows = open().querySelectorAll(".plan-card");
  const lane = (card: string): string | undefined => rows.find((r) => r.querySelector(".selector-name")?.textContent === ctx.catalog.cardLabel(card))?.querySelector(".plan-lane")?.textContent;
  const laned = ruled.cards.filter((c) => ctx.catalog.ruled(c.card));
  const own = ruled.cards.filter((c) => !ctx.catalog.ruled(c.card));
  const shown = rows.map((r) => r.querySelector(".selector-name")?.textContent);
  const lanedShown = laned.filter((c) => shown.includes(ctx.catalog.cardLabel(c.card)));
  const ownShown = own.filter((c) => shown.includes(ctx.catalog.cardLabel(c.card)));
  expect("a lane task is offered in Plan (control)", lanedShown.length > 0, true);
  expect("a lane task names its lane", lanedShown.map((c) => lane(c.card)), lanedShown.map((c) => ctx.catalog.laneLabel(ctx.catalog.laneOf(c.card), view)));
  expect("a player task is offered too (control)", ownShown.length > 0, true);
  expect("the player's own task names none", ownShown.map((c) => lane(c.card)), ownShown.map(() => undefined));
  info.presentation = was;
}

{  // the dot: on Change while a task of the lane has not been seen; Change's press (or the editor opening) clears it
  const { ctx } = testContext();
  const rows = new LaneRows(ctx);
  const root = mounted(rows.root);
  rows.update(ruled);
  expect("a new task: the dot", root.querySelectorAll(".lane-change .new-dot").length, 1);
  rows.update(ruled);
  expect("not drawn twice", root.querySelectorAll(".lane-change .new-dot").length, 1);
  root.querySelector(".lane-change")?.click();
  expect("the editor's opening keeps the tasks seen", laneCards.every((c) => ctx.keeps.laneTaskSeen(c.card)), false);
  const tab = new RulesTab(ctx);
  mounted(tab.root);
  tab.update(ruled);
  tab.open(ruled, { lane: "helper", rule: 4 });
  expect("the lane's tasks are kept seen", laneCards.every((c) => ctx.keeps.laneTaskSeen(c.card)), true);
  rows.update(ruled);
  expect("the dot is gone", root.querySelectorAll(".lane-change .new-dot").length, 0);
}
