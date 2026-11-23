// A job offered to people nobody has set to it (docs/decisions/people.md, "A new job is said once"): the cards a person of
// the town gained between two views that no mix, rule, queue entry or run holds, grouped by job, the cards one town-card
// definition fans out over its lanes sharing a label_key. The story strip words one line for the step (ui/story.ts); a
// card that arrives at work, a card of a person who joined in the same step, and the player's own cards are no offer.
import type { View } from "../api/types";
import type { Catalog } from "./catalog";
import { inUse } from "./marks";
import { UI } from "./text";
import { people } from "./town";

export interface NewJob {
  /** The job's label key, shared by its card on every lane. */
  label: string;
  /** One of its cards: the job's words. */
  card: string;
  lanes: string[];
}

/** One entry per job offered since `prev`, in card order; empty with no `prev`. */
export function newJobs(catalog: Catalog, prev: View | null, view: View): NewJob[] {
  if (prev === null) return [];
  const had = new Set(prev.cards.map((c) => c.card));
  const used = inUse(view);
  const town = new Set(people(catalog, prev));
  const jobs = new Map<string, NewJob>();
  for (const { card } of view.cards) {
    const lane = catalog.laneOf(card);
    const label = catalog.cards.get(card)?.label_key;
    if (!town.has(lane) || !label || had.has(card) || used.has(card)) continue;
    const job = jobs.get(label) ?? { label, card, lanes: [] };
    if (!job.lanes.includes(lane)) job.lanes.push(lane);
    jobs.set(label, job);
  }
  return [...jobs.values()];
}

/** The story line for `jobs`, none for none: a job and a person named, a job for the town, a person's several, or the
 * town's several, so a step that offers many things never fills the strip. */
export function jobLine(catalog: Catalog, view: View, jobs: NewJob[]): string | null {
  const { text } = catalog;
  const [first, ...rest] = jobs;
  if (!first) return null;
  const lanes = [...new Set(jobs.flatMap((j) => j.lanes))];
  const only = lanes.length === 1 ? catalog.laneLabel(lanes[0]!, view) : null;
  if (rest.length === 0) return only !== null ? text.fill(UI.jobNew, { person: only, card: catalog.cardLabel(first.card) }) : text.fill(UI.jobNewTown, { card: catalog.cardLabel(first.card) });
  return only !== null ? text.fill(UI.jobNewMany, { person: only }) : text.get(UI.jobNewAll);
}
