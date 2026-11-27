// Every option Plan offers works as worded (docs/decisions/principles.md): a card already running is listed and adds a
// run after the tap under way (not an entry that pops at that landing), and a card on a ruled lane is refused by the
// server (contract/a-lane-run-by-rules.txt, "A LANE RUN BY RULES"), so it is neither listed nor taken.
import { install } from "../../fake-dom";
import { fixtureContent } from "../../../fixtures/content";
import { fixtureStep } from "../../../fixtures/steps";
import type { Card, View } from "../../../src/api/types";
import { Catalog } from "../../../src/game/page/catalog";
import { planCards, tapUntil, whenReady } from "../../../src/game/mixes/queue";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const ended = fixtureStep("restoffer", 100).view;
const listed = (v: View) => planCards(catalog, v).map((c) => c.card);

const stool = ended.cards.find((c) => c.card === "stool")!;
expect("control: the idle stool is listed and taken", [listed(ended).includes("stool"), whenReady(catalog, ended, "stool") !== null], [true, true]);
const lane = catalog.laneOf("stool");
const lastRun: View = { ...ended, lanes: ended.lanes.map((l) => (l.lane === lane ? { ...l, running_card: "stool" } : l)) };
expect("control: the stool's cap is 1", stool.cap, 1);
expect("its last run under way: not listed (a run past the cap could never happen)", listed(lastRun).includes("stool"), false);
const running: View = { ...lastRun, cards: lastRun.cards.map((c) => (c.card === "stool" ? { ...c, cap: 3 } : c)) };
expect("a card running on its lane with room under its cap is listed", listed(running).includes("stool"), true);
expect("and taken as a run after the tap under way", whenReady(catalog, running, "stool"),
  { kind: "set_queue", entries: [...running.queue, tapUntil("stool", stool.completions + 2)] });

const fetch: Card = { ...stool, card: "fetch", cap: null, completions: 0 };
const fetchView: View = { ...ended, cards: [...ended.cards, fetch] };
expect("control: fetch is a step on a lane", [catalog.cards.get("fetch")?.presentation, catalog.ruled("fetch")], ["narrative", true]);
expect("a card on a ruled lane is not listed", listed(fetchView).includes("fetch"), false);
expect("nor taken", whenReady(catalog, fetchView, "fetch"), null);
