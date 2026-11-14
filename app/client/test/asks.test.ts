// The Asks list (CONTRACT.txt, "OFFERS"; docs/design/redesign.md, "Asks"): the first open offer drawn in its slot with
// its text and one button per answer, each with its cost (a time from takes_s, left out while takes_s is null); the
// rest counted, and the count opening the whole list; who asks, what led to it and the texts an offer has only where
// it differs, each drawn only when the content gives it; each answer's figures from a dry run of it. Revealed through
// the arrival queue after the last of its lines in this Step, or at once when the Step holds none of them; no dismiss,
// never gone until answered; a tap sends answer_offer. An offer that arrives already answered draws nothing.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { asksStep } from "../fixtures/asks";
import { dayTwoStep } from "../fixtures/daytwo";
import type { Decision, LogLine, View } from "../src/api/types";
import { Asks } from "../src/ui/asks";
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
const one = asksStep("asksone", 100).view;
const many = asksStep("asksmany", 100).view;
const LINE: LogLine = { at: 100, seq: 0, key: "line.offer", card: null };
const settle = (): Promise<void> => new Promise((done) => setTimeout(done, 0));

/** The list drawn for `lines` as the Step's lines, with what was sent to the arrival queue. */
function drawn(lines: LogLine[], view: View = offered.view) {
  const { ctx, got } = testContext();
  const arrived: string[] = [];
  ctx.arrivals = { ...ctx.arrivals, arrive: (_node, kind, id) => { arrived.push(`${kind}:${id}`); } };
  ctx.lines = () => lines;
  const asks = new Asks(ctx);
  const root = mounted(asks.root);
  asks.update(view);
  return { asks, root, arrived, got, ctx };
}

const slot = (root: FakeEl) => root.querySelector(".asks-slot");
const texts = (root: FakeEl | null | undefined, selector: string) => root?.querySelectorAll(selector).filter((n) => !n.hidden).map((n) => n.textContent) ?? [];

{  // the ask: its text, one button per answer with its cost, no dismiss; a tap answers
  const { root, got, arrived } = drawn([LINE]);
  expect("the offer's text", root.querySelector(".ask-text")?.textContent, "[fixture] A question with two answers: which one?");
  const buttons = slot(root)?.querySelectorAll("button") ?? [];
  expect("one button per answer, the cost from takes_s (none while null)", buttons.map((b) => b.textContent), ["Wait", "Go nowtakes 12 m 30 s"]);
  expect("revealed as an arrival when its line is in this Step", arrived, ["chip:offer:ask"]);
  buttons[1]?.click();
  expect("a tap sends answer_offer", got.decided, [{ kind: "answer_offer", offer: "ask", answer: "go" }]);
}

{  // an ask with none of the optional fields draws none of their rows, and no count with nothing behind it
  const { root } = drawn([LINE]);
  expect("no who, cause, facts or figures drawn", [".ask-who", ".ask-cause", ".ask-facts", ".ask-figures"].map((s) => root.querySelectorAll(s).every((n) => n.hidden)), [true, true, true, true]);
  expect("no count", root.querySelector(".asks-more")?.hidden, true);
}

{  // an ask with every field: who asks by name with a face each, what led to it, and the three texts
  const { root } = drawn([], one);
  expect("who asks", texts(root, ".ask-names"), ["Helper, settled and Mason"]);
  expect("a face each, by initial", texts(root, ".ask-face"), ["H", "M"]);
  expect("what led to it", texts(root, ".ask-cause"), ["Tend the fire ×3"]);
  expect("the texts it has", texts(root, ".ask-fact"), ["[fixture] waiting costs a thing", "[fixture] gone by a time", "[fixture] settled for good"]);
}

{  // several open: the first in the slot, the rest counted, the count opening every one in the list
  const { root, asks, got } = drawn([], many);
  expect("one in the slot", slot(root)?.querySelectorAll(".ask").map((a) => a.dataset["offer"]), ["ask"]);
  expect("the rest counted", root.querySelector(".asks-more")?.textContent, "2 more");
  root.querySelector(".asks-more")?.click();
  const list = root.querySelector(".asks-sheet");
  expect("the list opens", list?.open, true);
  expect("with every open ask, in order", list?.querySelectorAll(".ask").map((a) => a.dataset["offer"]), ["ask", "bank", "trade"]);
  list?.querySelector('[data-offer="trade"] [data-answer="swap"]')?.click();
  expect("an answer in the list is sent", got.decided, [{ kind: "answer_offer", offer: "trade", answer: "swap" }]);
  asks.update(asksStep("asksmany", 100, { answered: ["ask:go", "bank:his"] }).view);
  expect("answered ones leave it", list?.querySelectorAll(".ask").map((a) => a.dataset["offer"]), ["trade"]);
  expect("the next takes the slot, and nothing is counted behind it", [slot(root)?.querySelector(".ask")?.dataset["offer"], root.querySelector(".asks-more")?.hidden], ["trade", true]);
  asks.update(asksStep("asksmany", 100, { answered: ["ask:go", "bank:his", "trade:swap"] }).view);
  expect("the list shuts with nothing left in it", list?.open, false);
}

{  // the chronicle's waiting count: one waiting is brought into view, several open the list
  const single = drawn([], one);
  single.asks.show();
  expect("one: its first answer focused", fakeDocument.activeElement?.dataset["answer"], "hers");
  expect("and the list stays shut", single.root.querySelector(".asks-sheet")?.open, false);
  const several = drawn([], many);
  several.asks.show();
  expect("several: the list", several.root.querySelector(".asks-sheet")?.open, true);
}

{  // a Step without its lines (it showed before the page's last view): at once, no turn in the queue
  const { root, arrived } = drawn([{ ...LINE, key: "line.4" }]);
  expect("not sent to the queue", arrived, []);
  expect("drawn at once", root.hidden, false);
}

{  // one joining behind the shown ask only moves the count, even with its line in this Step
  const { asks, arrived, ctx, root } = drawn([], one);
  ctx.lines = () => [LINE];
  const ask = many.offers.find((o) => o.offer === "ask");
  if (!ask) throw new Error("no ask");
  asks.update({ ...one, offers: [...one.offers, ask] });
  expect("nothing held for it", arrived, []);
  expect("counted", root.querySelector(".asks-more")?.textContent, "1 more");
}

{  // answered, or arriving answered: nothing drawn, and the list takes no room
  const { asks, root } = drawn([LINE]);
  asks.update(answered);
  expect("gone once answered", [root.querySelectorAll(".ask").length, root.hidden], [0, true]);
  const fresh = drawn([], answered);
  expect("an offer that arrives answered draws nothing", [fresh.root.querySelectorAll(".ask").length, fresh.root.hidden], [0, true]);
}

{  // the figures: one dry run per answer that installs a modifier, read against the view, asked again only when it moves
  const { ctx } = testContext();
  const ran: Decision[][] = [];
  ctx.actions.dryRun = (ds) => { ran.push(ds); return Promise.resolve(asksStep("asksone", 100, { answered: ds.map((d) => (d.kind === "answer_offer" ? `${d.offer}:${d.answer}` : "")) }).view); };
  const asks = new Asks(ctx);
  const root = mounted(asks.root);
  asks.update(one);
  await settle();
  expect("each answer's figures, before → after", [texts(root, '[data-answer="hers"] .ask-figure'), texts(root, '[data-answer="his"] .ask-figure')],
    [["Dead wood -2/min → -1.8/min", "Rest 5 s → 4 s"], ["Dead wood holds 40 → 50"]]);
  asks.update(one);
  await settle();
  expect("not asked again while nothing moved", ran.length, 2);
  asks.update({ ...one, ledger: one.ledger.map((l) => ({ ...l, net_per_hour: l.net_per_hour * 2 })) });
  await settle();
  expect("asked again once a rate moved", ran.length, 4);
  const bare = testContext();
  const none: Decision[][] = [];
  bare.ctx.actions.dryRun = (ds) => { none.push(ds); return Promise.resolve(null); };
  new Asks(bare.ctx).update(offered.view);
  await settle();
  expect("an ask whose answers install nothing is not dry-run", none.length, 0);
}

{  // the real queue: the offer's line first, held for its reading time, then the ask
  const { ctx } = testContext();
  const reveal = new Reveal();
  ctx.arrivals = reveal;
  ctx.lines = () => [LINE];
  const strip = document.createElement("p");
  const line = mounted(strip);
  line.rect = { left: 0, top: 10, width: 300, height: 20, right: 300, bottom: 30 };
  reveal.collect();
  reveal.line([strip], "1", 2000);
  const asks = new Asks(ctx);
  document.body.append(asks.root);
  asks.update(offered.view);
  const held = fakeDocument.body.querySelector(".asks-slot");
  if (!held) throw new Error("no slot");
  held.rect = { left: 0, top: 100, width: 300, height: 60, right: 300, bottom: 160 };
  const t = performance.now();
  reveal.start(t);
  expect("the line shows first", [line.classList.contains("held"), held.classList.contains("held")], [false, true]);
  reveal.tick(t + 2100);
  expect("then the ask", held.classList.contains("held"), false);
}

{  // the mark: the shown ask takes the one glow; a held glow is not taken, it is waited for
  const { ctx } = testContext();
  const asks = new Asks(ctx);
  const root = mounted(asks.root);
  asks.update(offered.view);
  const ask = root.querySelector(".ask");
  expect("the ask takes the glow", ask?.classList.contains("glow"), true);
  ask?.click();
  expect("the glow is used up by the tap", ask?.classList.contains("glow"), false);
}

{  // another control holds the glow (a lesson's step): the ask waits, and takes it once it is free
  const { ctx } = testContext();
  const other = document.createElement("button");
  mounted(other);
  ctx.glow.offer(other);
  const asks = new Asks(ctx);
  document.body.append(asks.root);
  asks.update(offered.view);
  const ask = fakeDocument.body.querySelector(".ask");
  expect("held glow is kept by its owner", [other.classList.contains("glow"), ask?.classList.contains("glow")], [true, false]);
  ctx.glow.clear(other);
  asks.tick();
  expect("then the ask has it", [other.classList.contains("glow"), ask?.classList.contains("glow")], [false, true]);
  asks.update(answered);
  expect("answering lets it go", ctx.glow.busy, false);
}
