// What the open story beats wait on, as the page marks it (CONTRACT.txt, "Goals"; decisions.md, "Progress is stated,
// never hinted"): the cards, the stores' lines and the skills' rows that move the story carry the story mark, and only
// they, so a bar without it is progress the story does not wait on. Read off View.goals alone.
import type { Goal, View } from "../api/types";
import type { Catalog } from "./catalog";

export interface StoryMarks {
  cards: ReadonlySet<string>;
  /** Unlocked stores a beat waits on, and the stores a clock waiting on them keeps moving on. */
  stores: ReadonlySet<string>;
  skills: ReadonlySet<string>;
  /** Store goals on a store the player has no line for yet: stated as a line of their own (ui/goals.ts), the cards
   * that make it marked. */
  unlined: Goal[];
  clock: Goal | null;
}

export function storyMarks(catalog: Catalog, view: View): StoryMarks {
  const lined = (store: string): boolean => catalog.unlocked(view, "store", store);
  const stores = view.goals.filter((g) => g.kind === "store" && g.store !== null && lined(g.store)).map((g) => g.store as string);
  const clock = view.goals.find((g) => g.kind === "clock") ?? null;
  const unlined = view.goals.filter((g) => g.kind === "store" && g.store !== null && !lined(g.store));
  const makers = unlined.flatMap((g) => catalog.stores.get(g.store ?? "")?.made_by ?? []);
  return {
    cards: new Set([...view.goals.flatMap((g) => (g.kind === "card" && g.card !== null ? [g.card] : [])), ...makers]),
    stores: new Set([...stores, ...(clock?.feeds ?? []).filter(lined)]),
    skills: new Set(view.goals.flatMap((g) => (g.kind === "level" && g.skill !== null ? [g.skill] : []))),
    unlined,
    clock,
  };
}
