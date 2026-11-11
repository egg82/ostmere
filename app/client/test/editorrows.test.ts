// The mix editor's entry rows and its drag-in (ui/editor.ts): what each row shows and does, and how a card joins by tap
// or by being dragged onto the bar. Pins the code before it moves out of editor.ts.
import { fakeDocument, FakeEl, FakeEvent, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { MixEditor } from "../src/ui/editor";
import type { PartContext } from "../src/ui/part";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const settle = (): Promise<void> => new Promise((done) => setTimeout(done, 200));   // past the editor's 150ms preview delay
const q = (root: FakeEl, sel: string): FakeEl[] => root.querySelectorAll(sel);
const one = (root: FakeEl, sel: string): FakeEl => {
  const found = q(root, sel)[0];
  if (!found) throw new Error(`no ${sel}`);
  return found;
};

const base = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const MIX = "Morning <b>fire</b> & wood";   // gather 60%, tend 40%
const SOLO = "Gather by hand";

function open(view: View, mixId: string, after: View = view): { editor: MixEditor; root: FakeEl } {
  const { ctx } = testContext();
  ctx.actions.dryRun = () => Promise.resolve(after);
  const editor = new MixEditor(ctx as PartContext, () => undefined, new NewMarks());
  document.body.replaceChildren(editor.root);
  const root = fakeDocument.body.firstElementChild;
  if (!root) throw new Error("nothing mounted");
  editor.update(view);
  editor.show(view, mixId);
  return { editor, root };
}
const shares = (root: FakeEl): string[] => q(root, ".entry-share").map((n) => n.textContent);
const names = (root: FakeEl): string[] => q(root, ".entry-name").map((n) => n.textContent);

// rows: label, share, the hue class, a remove button per row
{
  const { root } = open(base, MIX);
  expect("two rows", q(root, ".editor-entry").length, 2);
  expect("a name per row", names(root).map((s) => s.length > 0), [true, true]);
  expect("the shares", shares(root), ["60%", "40%"]);
  expect("hue classes", q(root, ".editor-entry").map((r) => r.className.match(/hue-\d/)?.[0]), ["hue-2", "hue-5"]);
  expect("remove buttons labelled with the card", q(root, ".entry-remove").map((b) => b.getAttribute("aria-label")?.endsWith(names(root)[0]!) ?? false), [true, false]);
  expect("removable while there are two", q(root, ".entry-remove").map((b) => b.disabled), [false, false]);
  expect("nothing struck", q(root, ".struck").length, 0);
}

// removing a row gives its share to the rest; the last row cannot go
{
  const { root } = open(base, MIX);
  const before = names(root);
  q(root, ".entry-remove")[1]!.click();
  expect("the second row's button removes the second: the first stays", names(root), [before[0]]);
}
{
  const { root } = open(base, MIX);
  const first = names(root)[0];
  one(root, ".entry-remove").click();
  expect("the first row's button removes the first", names(root).includes(first!), false);
  expect("one row left", q(root, ".editor-entry").length, 1);
  expect("it takes the whole bar", shares(root), ["100%"]);
  expect("the last cannot be removed", one(root, ".entry-remove").disabled, true);
  one(root, ".entry-remove").click();
  expect("still one", q(root, ".editor-entry").length, 1);
}

// "does": the engine's own per-hour numbers for that row's card, from the dry run; zero rates and other cards left out
{
  const { root } = open(base, MIX);
  await settle();
  const does = q(root, ".entry-does").map((n) => n.textContent);
  const gather = base.ledger.filter((l) => l.contributions.some((k) => k.runner === "gather" && k.per_hour !== 0));
  const tend = base.ledger.filter((l) => l.contributions.some((k) => k.runner === "tend" && k.per_hour !== 0));
  expect("gather's stores", (does[0] ?? "").split(" · ").length, gather.length);
  expect("tend's stores", (does[1] ?? "").split(" · ").length, tend.length);
  expect("a zero rate is left out", (does[1] ?? "").includes("stone"), false);
  const none = open(base, MIX, { ...base, ledger: [] });
  await settle();
  expect("no contributions, no text", q(none.root, ".entry-does").map((n) => n.textContent), ["", ""]);
}

// a card no longer in play: its row is struck and says retired
{
  const gone: View = { ...base, cards: base.cards.filter((c) => c.card !== "tend"), unlocked: [...base.unlocked, { category: "retired", id: "tend" }] };
  const { root } = open(gone, MIX);
  expect("only the gone row is struck", q(root, ".editor-entry").map((r) => r.classList.contains("struck")), [false, true]);
  expect("it says retired", q(root, ".entry-note").length, 1);
  const done: View = { ...base, cards: base.cards.filter((c) => c.card !== "tend") };
  expect("a struck row not retired has no note", q(open(done, MIX).root, ".entry-note").length, 0);
}


// drag-in: the cards that can join are the ones in play but not in the edit
const barOf = (root: FakeEl): FakeEl => {
  const bar = root.children[1];
  if (!bar) throw new Error("no bar");
  return bar;
};
function dragged(moves: [number, number][], up: [number, number]): { entries: number; transformDuring: string | undefined; transformAfter: string | undefined } {
  const { root } = open(base, SOLO);
  barOf(root).rect = { left: 100, top: 100, width: 200, height: 20, right: 300, bottom: 120 };
  const add = one(root, ".add-card");
  add.dispatchEvent(pointer("pointerdown", 0, 0));
  let transformDuring: string | undefined;
  for (const [x, y] of moves) { add.dispatchEvent(pointer("pointermove", x, y)); transformDuring = add.style["transform"]; }
  add.dispatchEvent(pointer("pointerup", up[0], up[1]));
  return { entries: q(root, ".editor-entry").length, transformDuring, transformAfter: add.style["transform"] };
}
const idle = (r: ReturnType<typeof dragged>) => r.entries;

expect("a tap joins", idle(dragged([], [0, 0])), 2);
expect("a jitter under 6px still counts as a tap", idle(dragged([[3, 3]], [500, 500])), 2);
expect("a drag dropped on the bar joins", idle(dragged([[150, 110]], [150, 110])), 2);
expect("a drag dropped off the bar does not", idle(dragged([[150, 400]], [150, 400])), 1);
expect("a drop just inside the margin above the bar joins", idle(dragged([[150, 80]], [150, 80])), 2);
expect("a drop beyond the margin above does not", idle(dragged([[150, 70]], [150, 70])), 1);
expect("a drop just inside the margin below joins", idle(dragged([[150, 140]], [150, 140])), 2);
expect("a drop beyond the margin below does not", idle(dragged([[150, 150]], [150, 150])), 1);
expect("just inside the left edge joins", idle(dragged([[103, 110]], [103, 110])), 2);
expect("just inside the right edge joins", idle(dragged([[298, 110]], [298, 110])), 2);
expect("left of the bar does not", idle(dragged([[99, 110]], [99, 110])), 1);
expect("right of the bar does not", idle(dragged([[301, 110]], [301, 110])), 1);
expect("the card follows the finger", dragged([[40, 30]], [40, 30]).transformDuring, "translate(40px, 30px)");
expect("and is put back on release", dragged([[40, 30]], [40, 30]).transformAfter, "");
expect("a small move does not move the card", dragged([[3, 3]], [0, 0]).transformDuring, undefined);

// a cancelled drag puts the card back and joins nothing
{
  const { root } = open(base, SOLO);
  const add = one(root, ".add-card");
  add.dispatchEvent(pointer("pointerdown", 0, 0));
  add.dispatchEvent(pointer("pointermove", 40, 30));
  add.dispatchEvent(new FakeEvent("pointercancel"));
  expect("put back", add.style["transform"], "");
  expect("nothing joined", q(root, ".editor-entry").length, 1);
  add.dispatchEvent(pointer("pointermove", 80, 60));
  expect("moves no longer followed", add.style["transform"], "");
}

// after the drop, later moves are not followed; the pointer is captured while it lasts
{
  const { root } = open(base, SOLO);
  const add = one(root, ".add-card");
  let captured = 0;
  add.setPointerCapture = () => { captured++; };
  add.dispatchEvent(pointer("pointerdown", 0, 0));
  expect("the pointer is captured", captured, 1);
  add.dispatchEvent(pointer("pointermove", 40, 30));
  add.dispatchEvent(pointer("pointerup", 40, 30));
  add.dispatchEvent(pointer("pointermove", 90, 90));
  expect("a move after the drop is ignored", add.style["transform"], "");
}

// the order: head, bar, results, run-until, rows, the folded Add, foot
{
  const { root } = open(base, SOLO);
  expect("the parts, top to bottom", root.children.map((c) => c.className.split(" ")[0]).slice(2, 7), ["editor-totals", "editor-stint", "editor-entries", "editor-adds", "editor-foot"]);
}

// Add is one control: the chips wait folded, a tap opens the list in place, a pick leaves it open, a second tap closes
{
  const { root } = open(base, SOLO);
  const fold = one(root, ".add-fold");
  const list = one(root, ".add-list");
  expect("folded at first", [list.hidden, fold.getAttribute("aria-expanded")], [true, "false"]);
  fold.click();
  expect("a tap opens it", [list.hidden, fold.getAttribute("aria-expanded")], [false, "true"]);
  one(root, ".add-card").dispatchEvent(new FakeEvent("click", { detail: 0 }));
  expect("a pick joins the card", q(root, ".editor-entry").length, 2);
  expect("and leaves the list open", one(root, ".add-list").hidden, false);
  one(root, ".add-fold").click();
  expect("a second tap closes it", one(root, ".add-list").hidden, true);
}

// a lesson pointing at a chip opens the fold
{
  const { root } = open(base, SOLO);
  one(root, ".editor-adds").dispatchEvent(new FakeEvent("unfold"));
  expect("unfold opens it", one(root, ".add-list").hidden, false);
}
