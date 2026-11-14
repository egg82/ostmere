// A ruled lane's cards stay out of the card panel and the Completed tab (CONTRACT.txt, "A lane run by rules"): such
// cards are offered only as that lane's tasks (its row's Change, the rule editor).
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { dayTwoStep } from "../fixtures/daytwo";
import { NewMarks } from "../src/game/marks";
import { Cards } from "../src/ui/cards";
import { Completed } from "../src/ui/completed";
import { Story } from "../src/ui/story";

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

const ruled = dayTwoStep("ruled", 100).view;

{  // the lane's cards stay out of the card panel and the Completed tab
  const { ctx } = testContext();
  const cards = new Cards(ctx, new NewMarks());
  const done = new Completed(ctx, new Story(ctx).book);
  cards.update(ruled, null);
  done.update(ruled);
  expect("no card on the ruled lane in Tasks", ["chop", "haul"].map((c) => cards.node(c) !== undefined), [false, false]);
  expect("other cards still drawn", cards.node("gather") !== undefined, true);
  const completed = mounted(done.root).querySelectorAll(".card-title").map((n) => n.textContent);
  expect("a ruled lane's done one-off not in Completed", completed.includes("Fetch once"), false);
  expect("other done cards still there", completed.includes("Stand up"), true);
}
