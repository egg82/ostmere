// A cascade (docs/design/redesign.md, "Feel"): when one live step sets off several consequences, they light one by one,
// about 90 ms apart, in the order one causes the next (a card finishes, its stores move, a level lands, a rule acts),
// at most six turns, the rest with the sixth. Each link gets the lit mark at its turn; a lone effect is no chain and
// gets none. The links take turns in the arrival queue's own stagger (game/story/arrivals.ts) with the reveal's tick, never a
// timer of their own; what arrives in the same step still shows at once, as outside a return it always has. A tap shows
// every link at once. Reduced motion keeps every link and its mark and drops the stagger. Time is a stubbed clock.
import { install } from "../../fake-dom";
import { BP, fixtureContent } from "../../../fixtures/content";
import { fixtureStep } from "../../../fixtures/steps";
import type { View } from "../../../src/api/types";
import { ArrivalQueue, LINK_GAP_MS, LINK_PACE, MAX_LINKS } from "../../../src/game/story/arrivals";
import { Catalog } from "../../../src/game/page/catalog";
import { Keeps } from "../../../src/game/account/keeps";
import { Reveal } from "../../../src/ui/feedback/reveal";
import { Screen } from "../../../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });
let reduced = false;
Object.assign(window, { innerWidth: 400, innerHeight: 800, matchMedia: () => ({ matches: reduced, addEventListener: () => undefined }) });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

/** Every due time of a started queue, by stepping a fake clock in 10 ms steps. */
function times<T>(q: ArrivalQueue<T>, from: number): Array<[number, T]> {
  const out: Array<[number, T]> = [];
  for (let t = from; t <= from + 5000 && !q.idle; t += 10) for (const group of q.due(t)) for (const p of group) out.push([t - from, p]);
  return out;
}

{  // the links' pace: the first at once, then LINK_GAP_MS apart; past MAX_LINKS turns, the rest with the last
  const q = new ArrivalQueue<number>(LINK_PACE);
  for (let i = 0; i < 8; i += 1) q.push("card", `l${i}`, null, i);
  q.start(1000, false);
  const g = LINK_GAP_MS;
  expect("90 ms apart, six turns", times(q, 1000), [[0, 0], [g, 1], [2 * g, 2], [3 * g, 3], [4 * g, 4], [5 * g, 5], [5 * g, 6], [5 * g, 7]]);
  expect("the gap is about 90 ms and six links fit under a second", [g >= 80 && g <= 100, MAX_LINKS, (MAX_LINKS - 1) * g < 1000], [true, 6, true]);
  const still = new ArrivalQueue<number>(LINK_PACE);
  for (let i = 0; i < 3; i += 1) still.push("card", `l${i}`, null, i);
  still.start(0, true);
  expect("reduced motion: every link at once", still.due(0), [[0], [1], [2]]);
}

// The reveal on the page: nodes in sight, so each takes its turn.
const node = (): HTMLElement => {
  const n = document.createElement("div");
  Object.assign(n, { rect: { left: 10, top: 100, width: 200, height: 50, right: 210, bottom: 150 } });
  return n;
};
const ran: string[] = [];
const lit = (ns: HTMLElement[]): boolean[] => ns.map((n) => n.querySelector(".link-mark") !== null);

{  // a live step: links wait their turns in causal order; an arrival and an effect with no link show at once
  const r = new Reveal();
  const [rule, store, finish, level] = [node(), node(), node(), node()];
  const arrived = node();
  r.cascade();
  r.effect(rule, "card", () => ran.push("rule"), "rule");   // drawn first, caused last
  r.effect(store, "store", () => ran.push("store"), "store");
  r.effect(finish, "card", () => ran.push("finish"), "finish");
  r.effect(level, "skill", () => ran.push("level"), "level");
  r.arrive(arrived, "card", "new");
  r.effect(node(), "feature", () => ran.push("aim"));
  expect("drawing: nothing linked yet; the arrival and the plain effect at once", [ran, arrived.classList.contains("held")], [["aim"], false]);
  r.start(0);
  expect("the cause at once, lit", [ran, lit([finish])], [["aim", "finish"], [true]]);
  r.tick(LINK_GAP_MS - 1);
  expect("not before its turn", ran.length, 2);
  r.tick(LINK_GAP_MS);
  r.tick(2 * LINK_GAP_MS);
  expect("then each in turn, by cause", ran, ["aim", "finish", "store", "level"]);
  expect("each lit at its turn, the last not yet", lit([finish, store, level, rule]), [true, true, true, false]);
  expect("an arrival meanwhile is not held behind the links", r.busy, false);
  r.tick(3 * LINK_GAP_MS);
  expect("the rule last", [ran.at(-1), lit([rule])], ["rule", [true]]);
}

{  // a lone effect is no chain: at once, unlit
  ran.length = 0;
  const r = new Reveal();
  const one = node();
  r.cascade();
  r.effect(one, "card", () => ran.push("finish"), "finish");
  r.start(0);
  expect("a lone link at once, no mark", [ran, lit([one])], [["finish"], [false]]);
}

{  // a tap shows every link still waiting
  ran.length = 0;
  const r = new Reveal();
  r.cascade();
  for (const id of ["a", "b", "c"]) r.effect(node(), "card", () => ran.push(id), "finish");
  r.start(0);
  document.body.dispatchEvent(new Event("click"));
  expect("all at once on a tap", ran, ["a", "b", "c"]);
}

{  // reduced motion: every link and its mark, together
  ran.length = 0;
  reduced = true;
  const r = new Reveal();
  const ns = [node(), node(), node()];
  r.cascade();
  ns.forEach((n, i) => r.effect(n, "card", () => ran.push(`l${i}`), "store"));
  r.start(0);
  expect("reduced: all at once, each lit", [ran, lit(ns)], [["l0", "l1", "l2"], [true, true, true]]);
  reduced = false;
}

{  // outside a live step's draw, an effect runs at once, link or not (a redraw)
  ran.length = 0;
  const r = new Reveal();
  const n = node();
  r.effect(n, "card", () => ran.push("finish"), "finish");
  expect("no cascade: at once, unlit", [ran, lit([n])], [["finish"], [false]]);
}
{  // on the screen: a live step where a mixed card lands and the level it trains speeds it up sets off a chain:
   // the landing, then the level on the card, then the skill row's burst, each LINK_GAP_MS after the last
  const AT = 100;
  const base = fixtureStep("mid", AT);
  const v: View = base.view;
  const next: View = {
    ...v,
    skills: v.skills.map((s) => (s.skill === "foraging" ? { ...s, level: 3 } : s)),
    cards: v.cards.map((c) => (c.card === "gather" ? { ...c, completions: c.completions + 1, speed: BP * 2 } : c)),
  };
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  clock = 0;
  screen.show({ ...base, lines: [] });
  screen.tick(AT);
  const gather = [...screen.root.querySelectorAll<HTMLElement>(".card")].find((n) => n.dataset["card"] === "gather");
  const skill = [...screen.root.querySelectorAll<HTMLElement>(".skill")].find((n) => n.querySelector(".skill-name")?.textContent === "Foraging");
  if (!gather || !skill) throw new Error("no gather card or Foraging row");
  for (const n of [gather, skill]) Object.assign(n, { rect: { left: 10, top: 100, width: 200, height: 50, right: 210, bottom: 150 } });
  const state = (): string[] => [gather.querySelector(".pop") ? "landed" : "", gather.classList.contains("levelled") ? "levelled" : "", skill.classList.contains("burst") ? "burst" : ""];
  screen.show({ ...base, view: next, lines: [] });
  expect("the landing at once, lit", [state(), lit([gather])], [["landed", "", ""], [true]]);
  clock = LINK_GAP_MS;
  screen.tick(AT + 1);
  expect("then the level on the card", state(), ["landed", "levelled", ""]);
  clock = 2 * LINK_GAP_MS;
  screen.tick(AT + 1);
  expect("then the skill row", [state(), lit([skill])], [["landed", "levelled", "burst"], [true]]);
}
console.log("cascade: ok");

{  // a cascade knows whether a tap started it: from a link sent as a tap's, never from what the link is
  const r = new Reveal();
  r.cascade();
  r.effect(node(), "card", () => undefined, "finish");
  r.effect(node(), "store", () => undefined, "store");
  r.start(0);
  expect("no tap's link: not a tap's cascade", r.tapStarted, false);
  r.cascade();
  r.effect(node(), "card", () => undefined, "finish", "tap");
  r.effect(node(), "store", () => undefined, "store");
  r.start(0);
  expect("a tap's completion started it", r.tapStarted, true);
  r.cascade();
  expect("the next cascade starts unmarked", r.tapStarted, false);
}
