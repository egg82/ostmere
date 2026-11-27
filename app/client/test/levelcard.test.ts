// A level shows on the card it speeds up (docs/design/redesign.md, "Feel"; contract/, "Skills"): when a skill's
// level rises, each card a level passed names in LevelPays.speeds, and whose Card.speed rose, shows "{skill} {n} ·
// {before} → {after}" for 2 s, the times one whole completion at each speed. Nothing on a card the level does not name,
// nor on one whose speed did not rise. The two times are told apart: a short card keeps the decimals that differ.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { BP, fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { speedups } from "../src/game/levelled";
import { Cards } from "../src/ui/cards";
import { NewMarks } from "../src/game/marks";

install();
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const before = fixtureStep("mid", 100).view;   // foraging 2; gather and tend mixed, 5 s and 7 s at BP
/** Foraging up to `level`, and `speeds` (card: new speed) applied to the cards. */
const after = (level: number, speeds: Record<string, number>): View => ({
  ...before,
  skills: before.skills.map((s) => (s.skill === "foraging" ? { ...s, level } : s)),
  cards: before.cards.map((c) => (c.card in speeds ? { ...c, speed: speeds[c.card] ?? c.speed } : c)),
});

{  // the named card, sped up: old → new, a whole completion at each speed
  const got = speedups(catalog, before, after(3, { gather: (BP * 11) / 10 }));
  expect("gather, at Foraging 3", got.map((s) => [s.card, s.skill, s.level]), [["gather", "foraging", 3]]);
  expect("5 s to 5/1.1 s", [got[0]?.beforeS, Math.round((got[0]?.afterS ?? 0) * 1000)], [5, 4545]);
}
expect("tend sped up too, but the level does not name it", speedups(catalog, before, after(3, { tend: BP * 2 })), []);
expect("named, but its speed did not rise", speedups(catalog, before, after(3, {})), []);
expect("a speed-up with no level", speedups(catalog, before, after(2, { gather: BP * 2 })), []);
expect("a level passed on the way counts", speedups(catalog, before, after(4, { gather: BP * 2 })).map((s) => [s.card, s.level]), [["gather", 4]]);

{  // the two times told apart: whole seconds where they differ, else the decimals that do, two at most
  const f = catalog.format;
  expect("5 s → 4.5 s", f.spans(5, 5 / 1.1), ["5 s", "4.5 s"]);
  expect("20 s → 18 s", f.spans(20, 20 / 1.1), ["20 s", "18 s"]);
  expect("5 s → 4.95 s", f.spans(5, 4.95), ["5 s", "4.95 s"]);
  expect("a minute and over reads as a duration", f.spans(600, 600 / 1.1), ["10 m 0 s", "9 m 6 s"]);
}

{  // on the card: the line takes the foot for 2 s, then the time comes back
  const { ctx } = testContext();
  const cards = new Cards(ctx, new NewMarks());
  cards.update(before, null);
  cards.tick(100);
  const gather = [...cards.root.querySelectorAll<HTMLElement>(".card")].find((n) => n.dataset["card"] === "gather");
  const tend = [...cards.root.querySelectorAll<HTMLElement>(".card")].find((n) => n.dataset["card"] === "tend");
  if (!gather || !tend) throw new Error("no gather or tend card");
  const foot = (n: HTMLElement): string => n.querySelector(".card-foot")?.textContent ?? "";
  clock = 1000;
  cards.update(after(3, { gather: (BP * 11) / 10 }), before);
  cards.tick(101);
  expect("levelled: the line in its foot", [gather.classList.contains("levelled"), foot(gather)], [true, "Foraging 3 · 5 s → 4.5 s"]);
  expect("the old time is set apart", gather.querySelector(".card-foot s")?.textContent, "5 s");
  expect("a card it does not name is untouched", [tend.classList.contains("levelled"), foot(tend)], [false, "5 s"]);
  clock = 2999;
  cards.tick(103);
  expect("still readable at 2 s", gather.classList.contains("levelled"), true);
  clock = 3001;
  cards.tick(103);
  expect("then its time again", [gather.classList.contains("levelled"), foot(gather)], [false, "5 s"]);
}
console.log("levelcard: ok");
