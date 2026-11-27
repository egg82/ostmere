// The condition editor offers every subject a save holds (automation is never earned or gated; nothing exists
// in a save that a rule cannot watch): every store, the Camp's included while a level a rule can name is ahead, every skill, and every capped task in play by
// its count (docs/decisions/mixes.md: an uncapped task's count is soon past any n for good), and every chip the save has shown, whether or not it shows now. Read through the real subject list,
// ruleoffers.offeredSubjects and whenChoices in the full editor, on every fixture save. What is left out, and why, is
// condsubjects.ts's KINDS.
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/page/catalog";
import { offeredSubjects, whenChoices } from "../src/game/condition/ruleoffers";
import { subjectOpen } from "../src/game/condition/subjectrule";
import { KINDS, missing, present, SAVES } from "./condsubjects";

const catalog = new Catalog(fixtureContent);

const seen = new Map(KINDS.map((k) => [k, 0]));
const failures: string[] = [];
let uncappedSeen = 0;
for (const { phase, view } of SAVES) {
  for (const s of present(view)) seen.set(s.kind, (seen.get(s.kind) ?? 0) + 1);
  const offered = offeredSubjects(catalog, view);
  for (const kind of KINDS) {
    const left = missing(view, offered, kind, subjectOpen(catalog, view, { kind: "camp", n: 1 }) ? null : catalog.campStore);
    if (left.length > 0) failures.push(`${phase}: ${kind} not offered: ${left.join(", ")}`);
  }
  const uncapped = new Set(view.cards.filter((c) => c.cap === null).map((c) => c.card));
  uncappedSeen += uncapped.size;
  const counted = offered.flatMap((s) => (s.kind === "card_count" && uncapped.has(s.card) ? [s.card] : []));
  if (counted.length > 0) failures.push(`${phase}: an uncapped task offered by its count: ${counted.join(", ")}`);
}
if (uncappedSeen < 5) throw new Error(`only ${uncappedSeen} uncapped cards seen across ${SAVES.length} saves: the check looked at nothing`);
let chipsSeen = 0;
for (const { phase, view } of SAVES) {
  const offered = new Set(whenChoices(catalog, view, true, [], null).chips.map((c) => c.chip));
  const off = { ...view, chips: [] };   // a chip shown before and off now is offered all the same
  const offeredOff = new Set(whenChoices(catalog, off, true, [], null).chips.map((c) => c.chip));
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
