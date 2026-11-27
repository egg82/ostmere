// Kinds of one store in one ledger row (ui/ledgergroups.ts; contract/, "Ledger"): two or more drawn fold into one row
// at the first one's place, with their total, opened by a tap; one drawn alone keeps its own row.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import type { LedgerLine } from "../src/api/types";
import { LedgerGroups } from "../src/ui/ledger/ledgergroups";
import { testContext } from "./context";
import { Glow } from "../src/ui/feedback/fresh";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content = {
  ...fixtureContent,
  store_infos: fixtureContent.store_infos.map((s) => (s.store === "wood" || s.store === "stone" ? { ...s, group_key: "store.camp" } : s)),
};
const catalog = new Catalog(content);
const view = fixtureStep("covered", 100).view;
const line = (store: string): LedgerLine => view.ledger.find((l) => l.store === store)!;
const item = (store: string) => ({ line: line(store), node: Object.assign(document.createElement("div"), { id: store }) });
const folds = new LedgerGroups(testContext(new Glow(), catalog).ctx);

const warmth = item("warmth");
const wood = item("wood");
const stone = item("stone");
const out = folds.fold([warmth, wood, stone]);
expect("the two kinds fold into one row at the first's place", out.map((n) => n.id || n.className), ["warmth", "ledger-item ledger-fold"]);
const fold = out[1]!;
const body = fold.querySelector(".ledger-fold-lines")!;
expect("its lines are under it, closed", [[...body.children].map((n) => (n as HTMLElement).id), (body as HTMLElement).hidden], [["wood", "stone"], true]);
expect("named by its group's label", fold.querySelector(".line-name")?.textContent, catalog.label("store.camp"));
folds.tick(100);
const sum = catalog.format.amount(line("wood").segment.start_value + line("stone").segment.start_value, line("wood").cap + line("stone").cap);
expect("its total", fold.querySelector(".line-amount")?.textContent, sum);
const head = fold.querySelector<HTMLButtonElement>(".line-fold")!;
head.dispatchEvent(new Event("click"));
expect("a tap opens it", [(body as HTMLElement).hidden, head.getAttribute("aria-expanded")], [false, "true"]);
expect("open stays open across a redraw", (folds.fold([warmth, wood, stone])[1]!.querySelector(".ledger-fold-lines") as HTMLElement).hidden, false);
expect("one kind drawn alone keeps its own row", folds.fold([warmth, wood]).map((n) => n.id), ["warmth", "wood"]);
expect("and the fold is gone", fold.isConnected, false);
