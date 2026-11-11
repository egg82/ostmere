// The condition editor offers every subject a save holds (automation is never earned or gated; nothing exists
// in a save that a rule cannot watch): every store, the Camp's included, every skill, and every task in play by its
// count, and every chip the save has shown, whether or not it shows now. Read through the real subject list,
// ruleoffers.offeredSubjects and whenChoices in the full editor, on every fixture save. What is left out, and why, is
// condsubjects.ts's KINDS.
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import { offeredSubjects, whenChoices } from "../src/game/ruleoffers";
import { KINDS, missing, present, SAVES } from "./condsubjects";

const catalog = new Catalog(fixtureContent);

const seen = new Map(KINDS.map((k) => [k, 0]));
const failures: string[] = [];
for (const { phase, view } of SAVES) {
  for (const s of present(view)) seen.set(s.kind, (seen.get(s.kind) ?? 0) + 1);
  const offered = offeredSubjects(catalog, view);
  for (const kind of KINDS) {
    const left = missing(view, offered, kind);
    if (left.length > 0) failures.push(`${phase}: ${kind} not offered: ${left.join(", ")}`);
  }
}
let chipsSeen = 0;
for (const { phase, view } of SAVES) {
  const offered = new Set(whenChoices(catalog, view, true, null, null).chips.map((c) => c.chip));
  const off = { ...view, chips: [] };   // a chip shown before and off now is offered all the same
  const offeredOff = new Set(whenChoices(catalog, off, true, null, null).chips.map((c) => c.chip));
  for (const chip of view.chips_seen) {
    chipsSeen++;
    if (!offered.has(chip) || !offeredOff.has(chip)) failures.push(`${phase}: chip not offered: ${chip}`);
  }
}
if (chipsSeen < 5) throw new Error(`only ${chipsSeen} chips seen across ${SAVES.length} saves: the check looked at nothing`);
for (const [kind, n] of seen) if (n < 5) throw new Error(`only ${n} ${kind} subjects seen across ${SAVES.length} saves: the check looked at nothing`);
if (!SAVES.some((s) => s.view.ledger.some((l) => l.store === catalog.campStore))) throw new Error("no save holds the Camp store");
if (SAVES.some((s) => s.view.ledger.length === 0) === false) throw new Error("no fresh save (an empty ledger) among the saves");
if (failures.length > 0) throw new Error(failures.slice(0, 5).join("; "));
