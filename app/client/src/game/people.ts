// A day's mention (CONTRACT.txt, "PEOPLE"): the mention lines of one game day and one way, joined or left, are one
// line, worded by the band for how many lanes they count and drawn from it by a shuffle bag keyed by the save, the way
// and the band, so the same day reads the same on every device and the band's lines take turns. DayMentions keeps the
// days counted so far for the story strip and the chronicle (ui/story.ts); the rest is pure.
import type { Content, Mention } from "../api/types";
import type { Catalog } from "./catalog";
import type { Entry } from "./chronicle";
import { causeWords } from "./chronwords";
import { bagged } from "./fights";

/** Game seconds in a mention's day. */
export const DAY_S = 86400;

export type Way = "joined" | "left";

/** One day's mention of one way, as counted so far: the lanes, and the game second of the first. */
export interface DayMention {
  way: Way;
  day: number;
  at: number;
  lanes: readonly string[];
}

/** The id two mention lines share when they are the same day's of the same way. */
export function mentionId(way: Way, at: number): string {
  return `${way}:${Math.floor(at / DAY_S)}`;
}

/** `was` (null: the day's first) with `lane` counted in: a lane joins once and leaves once, so each line is one more. */
export function counted(was: DayMention | null, way: Way, lane: string, at: number): DayMention {
  return was === null ? { way, day: Math.floor(at / DAY_S), at, lanes: [lane] } : { ...was, lanes: [...was.lanes, lane] };
}

/** The text key the day's mention is worded by: of the way's bands the one with the highest at_least not over the
 * count, and of its keys the day's draw. Null with no bands (the content's checks refuse a mention then). */
export function mentionKey(people: Content["people"], save: number, m: DayMention): string | null {
  const bands = m.way === "joined" ? people?.came : people?.went;
  const band = (bands ?? []).filter((b) => b.at_least <= m.lanes.length).at(-1);
  return band ? bagged(`${save}|people|${m.way}|${band.at_least}`, band.keys, m.day) : null;
}

/** What one mention line changes: the entry that now shows its day, the entry it takes the place of (null: the day's
 * first), and the day's mentionId. */
export interface Counted {
  entry: Entry;
  was: Entry | null;
  id: string;
}

/** Each day's mention so far, with the chronicle entry that shows it. */
export class DayMentions {
  private readonly days = new Map<string, { mention: DayMention; entry: Entry }>();

  /** The mention line `key` counted into its day; null when no band words it. The entry stands at the day's first
   * second, under the first line's cause. */
  count(catalog: Catalog, save: number, key: string, told: Mention, at: number): Counted | null {
    const id = mentionId(told.way, at);
    const was = this.days.get(id);
    const mention = counted(was?.mention ?? null, told.way, told.lane, at);
    const words = mentionKey(catalog.content.people, save, mention);
    if (words === null) return null;
    const cause = was ? was.entry.cause : causeWords(catalog, catalog.lineCause(key));
    const entry: Entry = { text: catalog.text.get(words), at: mention.at, kind: "story", cause, person: true };
    this.days.set(id, { mention, entry });
    return { entry, was: was?.entry ?? null, id };
  }
}
