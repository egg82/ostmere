// Blind contract tests, written from the contract alone (not the implementation): the hands strip says why a greyed mix
// stopped; a scene condition reads the standing actions and a grade can ease for as long as it says (a short store
// need's source: needsource.test.ts).
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Q } from "../fixtures/content";
import type { Card, Mix, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Hands } from "../src/ui/hands";
import { SceneFacts } from "../src/scene/conditions";
import { gradeStep, pickGrade } from "../src/scene/manifest";
import type { SceneGrade } from "../src/scene/manifest";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const mid = fixtureStep("mid", 100).view;
const greyedView = fixtureStep("greyed", 100).view;

// ---- 1. The strip's note on a greyed mix ----
function strip(view: View): string {
  const h = new Hands(testContext().ctx);
  h.update(view);
  h.update({ ...view, at: view.at + 1 });
  return h.root.querySelector(".hands-status")?.textContent ?? "";
}
const note = (card: string): string => `stopped · ${catalog.cardLabel(card)} done`;
{
  const mixId = greyedView.active_mix_id;
  const active = greyedView.mixes.find((m) => m.id === mixId);
  if (!mixId || !active) throw new Error("fixture: the greyed phase has no active mix");
  const held = active.components.flatMap((c) => (c.kind === "card_share" ? [c.card] : []));
  expect("fixture: the mix holds gather and tend", held, ["gather", "tend"]);

  expect("greyed: the strip names the done card", strip(greyedView), note("tend"));

  const bothGone: View = { ...greyedView, cards: greyedView.cards.filter((c) => c.card !== "gather" && c.card !== "tend") };
  expect("two cards out of play: the first the mix holds", strip(bothGone), note("gather"));

  const completed: View = { ...greyedView, completed: [{ card: "tend", completions: 1 }] };
  expect("a completed card is out of play too", strip(completed), note("tend"));

  const running: View = { ...mid, greyed_mix_ids: [] };
  expect("a running mix carries no such note", strip(running).includes("stopped"), false);
  expect("the plain mix's status is not the greyed one's", strip(running) === note("tend"), false);

  // a mix that nests the greyed mix names that mix
  const outer: Mix = { id: "Outer", components: [{ kind: "sub_mix", mix_id: mixId, share_bp: 10_000 }] };
  const nesting: View = { ...greyedView, mixes: [...greyedView.mixes, outer], active_mix_id: "Outer", greyed_mix_ids: ["Outer", mixId] };
  // Which of the nested mix or its card is named is not fixed by the contract; the note must still say it stopped.
  const nested = strip(nesting);
  expect("a mix nesting a greyed mix still says it stopped", nested.startsWith("stopped · ") && nested.endsWith(" done"), true);
}

// ---- 4. Scene: the standing-action condition, and a grade's fade ----
{
  const facts = new SceneFacts();
  const standing = { action: "kindle", run: "full" as const };
  facts.observe({ ...mid, standing: [standing] });
  expect("action:<id> holds while the action stands", facts.holds("action:kindle", 100, Q), true);
  expect("another action does not", facts.holds("action:other", 100, Q), false);
  facts.observe({ ...mid, standing: [] });
  expect("action:<id> stops holding when it leaves view.standing", facts.holds("action:kindle", 101, Q), false);
  facts.observe({ ...mid, standing: [{ ...standing, run: "paused" as const }] });
  expect("paused but in view.standing still holds", facts.holds("action:kindle", 102, Q), true);

  const grades: Record<string, SceneGrade> = {
    cold: { when: null, filter: "none", overlay: "" },
    dusk: { when: "action:kindle", filter: "brightness(0.6)", overlay: "" },
  };
  const pickedAt = (view: View): string | undefined => {
    const f = new SceneFacts();
    f.observe(view);
    return pickGrade(grades, (when) => f.holds(when, view.at, Q))?.[0];
  };
  const evening: View = { ...mid, standing: [standing], ended_at: null };
  expect("the evening starts: the grade keyed on it is picked, before the end", pickedAt(evening), "dusk");
  expect("before the evening: the default", pickedAt({ ...mid, standing: [] }), "cold");

  const dt = 1;
  expect("no ease_s: 2.5 s", gradeStep({ when: null, filter: "", overlay: "" }, dt), dt / 2.5);
  expect("ease_s given: that many seconds", gradeStep({ when: null, filter: "", overlay: "", ease_s: 10 }, dt), dt / 10);
  expect("ease_s given: a slower fade moves less per frame", gradeStep({ when: "action:kindle", filter: "none", overlay: "", ease_s: 20 }, 2), 0.1);
}
console.log("coldfixcontract ok");
