// The editors' goal rows (ui/goaltimes.ts; CONTRACT.txt, "Goal rows"): a row for each goal whose time or limit the
// dry run changes, matched by goal, and under it the after row's binding line as the server states it.
import { install } from "./fake-dom";
import { fixtureStep } from "../fixtures/steps";
import { Catalog } from "../src/game/catalog";
import { fixtureContent, Q } from "../fixtures/content";
import type { GoalRow, View } from "../src/api/types";
import { goalRows } from "../src/ui/goaltimes";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const R = fixtureContent.scales.rate_per_item_hour;
const H = 3600;
const base = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const wood = (lands: number | null, over: Partial<GoalRow> = {}): GoalRow => ({
  kind: "store", store: "wood", skill: null, target: 30 * Q, lands_at: lands, per_hour: 60 * R, limit: null,
  until: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 30 * Q, release: 30 * Q }, ...over,
});
const level = (lands: number | null, over: Partial<GoalRow> = {}): GoalRow => ({
  kind: "level", store: null, skill: "foraging", target: 4, lands_at: lands, per_hour: 120 * R, limit: null,
  until: { kind: "at_least", watched: { kind: "skill_level", skill: "foraging" }, value: 4, release: 4 }, ...over,
});
const at = (rows: GoalRow[]): View => ({ ...base, goal_rows: rows });
const text = (els: HTMLElement[]): string[] => els.map((e) => e.textContent ?? "");

// no dry run yet, or nothing moved: no rows, not even the head
expect("no answer yet", goalRows(catalog, at([wood(100 + H)]), null, "after").length, 0);
expect("nothing moved", goalRows(catalog, at([wood(100 + H), level(100 + 2 * H)]), at([wood(100 + H), level(100 + 2 * H)]), "after").length, 0);

// a moved goal: the head, its row (label, now, arrow, after) and its own line under it; an unmoved one stays out
{
  const got = text(goalRows(catalog, at([wood(100 + H), level(100 + 2 * H)]), at([wood(100 + H), level(100 + 3 * H, { per_hour: 80 * R })]), "if run"));
  expect("head, row, line", got, ["goalsnow→if run", "Foraging 42 h→3 h", "XP +1.33/min"]);
}

// a store goal with a dry input after the edit: its time and the store that binds it
{
  const after = at([wood(null, { per_hour: 0, limit: { store: "stone", in_per_hour: 30 * R } })]);
  const got = text(goalRows(catalog, at([wood(100 + H)]), after, "after"));
  expect("never, limited by", got, ["goalsnow→after", "Dead wood 301 h→never", "limited by Flint, +0.5/min"]);
}

// only the limit moved: still a row, the time the same on both sides
{
  const after = at([wood(100 + H, { limit: { store: "stone", in_per_hour: 0 } })]);
  expect("a limit alone moves a row", text(goalRows(catalog, at([wood(100 + H)]), after, "after")).length, 3);
}

// a goal in the dry run that the live view lacks has no "now" to compare: left out
expect("unmatched goal", goalRows(catalog, at([]), at([level(100 + H)]), "after").length, 0);

// each side's time is from its own view's `at`
{
  const later = { ...at([wood(100 + 2 * H)]), at: 100 + H };
  expect("same landing, later view: moved", text(goalRows(catalog, at([wood(100 + 2 * H)]), later, "after"))[1], "Dead wood 302 h→1 h");
}
