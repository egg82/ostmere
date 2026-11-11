// The offer row (CONTRACT.txt, "Offers"; docs/design/opening-screen.md, the hands strip's offer row): an open offer's
// text and one button per answer, each with its time cost from takes_s (left out while takes_s is null); revealed
// through the arrival queue after the last of its lines in this Step, or at once when the Step holds none of them; no
// dismiss, never gone until answered; a tap sends answer_offer. An offer that arrives already answered draws no row.
// A refused answer (422: answered since the page's last view) asks advance and draws that.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { dayTwoStep } from "../fixtures/daytwo";
import type { LogLine } from "../src/api/types";
import { OfferRows } from "../src/ui/offerrows";
import { Reveal } from "../src/ui/reveal";

install();
Object.assign(window, { innerWidth: 1440, innerHeight: 900 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

const offered = dayTwoStep("offered", 100);
const answered = dayTwoStep("answered", 100).view;
const LINE: LogLine = { at: 100, seq: 0, key: "line.offer", card: null };

/** The rows drawn for `lines` as the Step's lines, with what was sent to the arrival queue. */
function drawn(lines: LogLine[]) {
  const { ctx, got } = testContext();
  const arrived: string[] = [];
  ctx.arrivals = { ...ctx.arrivals, arrive: (_node, kind, id) => { arrived.push(`${kind}:${id}`); } };
  ctx.lines = () => lines;
  const rows = new OfferRows(ctx);
  const root = mounted(rows.root);
  rows.update(offered.view);
  return { rows, root, arrived, got };
}

{  // the row: its text, one button per answer with its cost, no dismiss; a tap answers
  const { root, got, arrived } = drawn([LINE]);
  expect("the offer's text", root.querySelector(".offer-text")?.textContent, "[fixture] A question with two answers: which one?");
  const buttons = root.querySelectorAll("button");
  expect("one button per answer, the cost from takes_s (none while null)", buttons.map((b) => b.textContent), ["Wait", "Go nowtakes 12 m 30 s"]);
  expect("revealed as an arrival when its line is in this Step", arrived, ["chip:offer:ask"]);
  buttons[1]?.click();
  expect("a tap sends answer_offer", got.decided, [{ kind: "answer_offer", offer: "ask", answer: "go" }]);
}

{  // a Step without its lines (it showed before the page's last view): at once, no turn in the queue
  const { root, arrived } = drawn([{ ...LINE, key: "line.4" }]);
  expect("not sent to the queue", arrived, []);
  expect("drawn at once", root.querySelector(".offer-row")?.hidden, false);
}

{  // answered, or arriving answered: no row
  const { rows, root } = drawn([LINE]);
  rows.update(answered);
  expect("gone once answered", root.querySelectorAll(".offer-row").length, 0);
  const fresh = new OfferRows(testContext().ctx);
  fresh.update(answered);
  expect("an offer that arrives answered draws none", mounted(fresh.root).querySelectorAll(".offer-row").length, 0);
}

{  // the real queue: the offer's line first, held for its reading time, then the row
  const { ctx } = testContext();
  const reveal = new Reveal();
  ctx.arrivals = reveal;
  ctx.lines = () => [LINE];
  const strip = document.createElement("p");
  const line = mounted(strip);
  line.rect = { left: 0, top: 10, width: 300, height: 20, right: 300, bottom: 30 };
  reveal.collect();
  reveal.line([strip], "1", 2000);
  const rows = new OfferRows(ctx);
  document.body.append(rows.root);
  rows.update(offered.view);
  const row = fakeDocument.body.querySelector(".offer-row");
  if (!row) throw new Error("no row");
  row.rect = { left: 0, top: 100, width: 300, height: 60, right: 300, bottom: 160 };
  const t = performance.now();
  reveal.start(t);
  expect("the line shows first", [line.classList.contains("held"), row.classList.contains("held")], [false, true]);
  reveal.tick(t + 2100);
  expect("then the row", row.classList.contains("held"), false);
}

{  // the mark: the row is set apart from the routine rows and takes the one glow; a held glow is not taken, it is waited for
  const { ctx } = testContext();
  const rows = new OfferRows(ctx);
  const root = mounted(rows.root);
  rows.update(offered.view);
  const row = root.querySelector(".offer-row");
  expect("the row wears the someone-asks look", row?.classList.contains("offer-ask"), true);
  expect("and takes the glow", row?.classList.contains("glow"), true);
  row?.click();
  expect("the glow is used up by the tap", row?.classList.contains("glow"), false);
}

{  // another control holds the glow (a lesson's step): the offer waits, and takes it once it is free
  const { ctx } = testContext();
  const other = document.createElement("button");
  mounted(other);
  ctx.glow.offer(other);
  const rows = new OfferRows(ctx);
  document.body.append(rows.root);
  rows.update(offered.view);
  const row = fakeDocument.body.querySelector(".offer-row");
  expect("held glow is kept by its owner", [other.classList.contains("glow"), row?.classList.contains("glow")], [true, false]);
  ctx.glow.clear(other);
  rows.tick();
  expect("then the offer has it", [other.classList.contains("glow"), row?.classList.contains("glow")], [false, true]);
  rows.update(answered);
  expect("answering lets it go", ctx.glow.busy, false);
}
