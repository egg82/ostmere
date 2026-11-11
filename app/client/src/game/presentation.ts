// What the page keeps only grows (CONTRACT.txt, AccountPresentation and SavePresentation), so two copies of it join by union: flags OR
// together, a list is the first's entries then the second's that are new. The server does the same on every write;
// the page does it to take the server's answer without losing a keep made while that write was in flight.
import type { AccountPresentation, SavePresentation } from "../api/types";
import { MAX_VISITS } from "./loggroups";

function union<T>(own: T[], more: T[], name: (item: T) => string): T[] {
  const seen = new Set(own.map(name));
  return [...own, ...more.filter((item) => !seen.has(name(item)) && seen.add(name(item)))];
}

const names = (own: string[], more: string[]): string[] => union(own, more, (n) => n);

export function mergePresentation(own: AccountPresentation, more: AccountPresentation): AccountPresentation {
  return {
    rules_opened: own.rules_opened || more.rules_opened,
    devices_opened: own.devices_opened || more.devices_opened,
    reminder_mentioned: (own.reminder_mentioned ?? false) || (more.reminder_mentioned ?? false),
    ledger_lines: names(own.ledger_lines, more.ledger_lines),
    mix_stopped: names(own.mix_stopped, more.mix_stopped),
    switch_offered: union(own.switch_offered, more.switch_offered, (s) => JSON.stringify([s.chip, s.mix_id])),
    journal_read: names(own.journal_read, more.journal_read),
  };
}

export function mergeSavePresentation(own: SavePresentation, more: SavePresentation): SavePresentation {
  return {
    rule_seen: own.rule_seen || more.rule_seen,
    mix_offered: names(own.mix_offered, more.mix_offered),
    lessons: names(own.lessons, more.lessons),
    lesson_ends: union(own.lesson_ends, more.lesson_ends, (e) => e.lesson),
    visits: union(own.visits ?? [], more.visits ?? [], (v) => String(v.left)).slice(-MAX_VISITS),   // an older pod answers none
  };
}

/** What a save's write sends: `visits` only once one is kept, since a build from before them refuses a body naming it. */
export function sendableSave(p: SavePresentation): SavePresentation {
  if ((p.visits ?? []).length > 0) return p;
  const { visits: _none, ...older } = p;
  return older as SavePresentation;
}

/** What a write sends: `reminder_mentioned` only once it is set, since a build from before reminders refuses a body
 * naming it (its model forbids extra fields), and a page from this build still talks to one while a deploy rolls. */
export function sendable(p: AccountPresentation): AccountPresentation {
  if (p.reminder_mentioned) return p;
  const { reminder_mentioned: _unset, ...older } = p;
  return older as AccountPresentation;
}
