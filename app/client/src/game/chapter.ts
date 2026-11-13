// The figures of a return (docs/decisions.md, "The chronicle and unwrap, as built"): what the return found against what
// the player left, taken once as it lands and kept in the save's presentation (Chapter), so the chronicle's "Since you
// left" chapter shows them after a reload too. Each store the player has met whose whole items changed, each skill and
// the Camp that levelled, and each rule that came on or let go while they were away, with how many times it came on
// where the Step before says. Pure.
import type { Chapter, Content, Figure, RuleChange, RuleRun, View } from "../api/types";
import { Catalog } from "./catalog";
import { sample } from "./clock";
import { subjectNow } from "./subjectrule";

/** What `next` found against `prev`, the view the player left; `prevRuns` the rule runs the page had then. */
export function chapterOf(content: Content, prev: View, prevRuns: readonly RuleRun[], next: View, nextRuns: readonly RuleRun[]): Chapter {
  const catalog = new Catalog(content);
  const campWas = subjectNow(catalog, prev, { kind: "camp", n: 0 });
  const campNow = subjectNow(catalog, next, { kind: "camp", n: 0 });
  const camp = catalog.campStore;
  return {
    left: prev.at, back: next.at, stores: stores(catalog, prev, next),
    levels: next.skills.flatMap((s): Figure[] => {
      const was = prev.skills.find((p) => p.skill === s.skill)?.level;
      return was !== undefined && s.level > was ? [{ id: s.skill, was, now: s.level }] : [];
    }),
    camp: camp !== null && campNow > campWas ? { id: camp, was: campWas, now: campNow } : null,
    rules: rules(prevRuns, nextRuns, prev.at, next.at),
  };
}

function stores(catalog: Catalog, prev: View, next: View): Figure[] {
  const per = catalog.content.scales.quantity_per_item;
  return next.ledger.flatMap((line): Figure[] => {
    if (line.store === catalog.campStore || !catalog.unlocked(next, "store", line.store)) return [];
    const before = prev.ledger.find((p) => p.store === line.store);
    const was = Math.max(0, Math.floor(before ? sample(before.segment, prev.at) : 0));
    const now = Math.max(0, Math.floor(sample(line.segment, next.at)));
    return Math.floor(was / per) === Math.floor(now / per) ? [] : [{ id: line.store, was, now }];
  });
}

function rules(prevRuns: readonly RuleRun[], nextRuns: readonly RuleRun[], left: number, back: number): RuleChange[] {
  const within = (t: number | null): boolean => t !== null && t > left && t <= back;
  const same = (a: RuleRun, b: RuleRun): boolean => JSON.stringify(a.order) === JSON.stringify(b.order);
  return nextRuns.flatMap((run): RuleChange[] => {
    const cameOn = within(run.on_at);
    if (!cameOn && !within(run.off_at)) return [];
    const before = prevRuns.find((r) => same(r, run))?.starts ?? 0;
    return [{ order: run.order, came_on: cameOn, times: Math.max(1, run.starts - before) }];
  });
}
