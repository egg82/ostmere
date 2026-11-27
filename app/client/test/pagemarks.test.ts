// The journal's page marks (game/pagemarks.ts; docs/design/journal.md, "Marks on the page"): a mark is never placed over
// a blocked box, a page asks for its wear and at most three of its days' marks, and every draw is seeded.
import type { JournalDay } from "../src/api/types";
import { seeded } from "../src/game/ledger/fights";
import type { Page } from "../src/game/book/journal";
import { crosses, PAGE_EVENT_MARKS, placeMarks, REPEAT_APART, REPEAT_TURN, SOFT_EDGE, wantedOf, type Box, type MarkManifest } from "../src/game/book/pagemarks";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const ART: MarkManifest = {
  wear: [{ src: "wear-1.webp", w: 512, h: 512 }, { src: "wear-2.webp", w: 512, h: 300 }],
  blood: [{ src: "blood-1.webp", w: 400, h: 512 }], soot: [{ src: "soot-1.webp", w: 512, h: 200 }],
  mud: [{ src: "mud-1.webp", w: 300, h: 200 }], water: [{ src: "water-1.webp", w: 200, h: 512 }],
};
const PAGE = { w: 540, h: 700 };
const day = (n: number, marks: JournalDay["marks"]): JournalDay => ({ day: n, day_notes: [], marks });
const page = (days: number[]): Page => ({ id: `days:${days[0]}`, section: "days", title: null, sketch: null, runners: [],
  notes: days.map((d) => ({ id: `${d}.0`, key: "k", hand: "ink", sketch: null, day: d, count: null })) });

{  // over many pages of random lines, no placed mark's core crosses a line, and some marks are placed
  let placed = 0;
  for (let s = 0; s < 200; s++) {
    const r = seeded(`lines|${s}`);
    const lines: Box[] = Array.from({ length: 4 + Math.floor(r() * 12) }, () => ({ x: 20 + r() * 60, y: r() * 650, w: 100 + r() * 360, h: 26 }));
    const wanted = wantedOf(s, page([0, 1]), [day(0, ["blood", "soot"]), day(1, ["mud"])]);
    for (const p of placeMarks(wanted, ART, PAGE, lines)) {
      placed++;
      const core = { x: p.box.x + p.box.w * SOFT_EDGE, y: p.box.y + p.box.h * SOFT_EDGE, w: p.box.w * (1 - 2 * SOFT_EDGE), h: p.box.h * (1 - 2 * SOFT_EDGE) };
      if (lines.some((l) => crosses(core, l))) throw new Error(`save ${s}: ${p.src} at ${JSON.stringify(p.box)} crosses a line`);
    }
  }
  expect("marks found room on most pages", placed > 400, true);
}

{  // a page with no room draws no mark rather than one over the words
  const full = [{ x: -10, y: -10, w: PAGE.w + 20, h: PAGE.h + 20 }];
  expect("no room, no marks", placeMarks(wantedOf(1, page([0]), [day(0, ["blood"])]), ART, PAGE, full), []);
}

{  // wear on every page, then the page's days' marks in day order, at most PAGE_EVENT_MARKS; a day not on it adds none
  const days = [day(0, ["blood", "soot"]), day(1, ["mud", "water"]), day(2, ["soot"])];
  const wanted = wantedOf(7, page([0, 1]), days);
  const events = wanted.filter((w) => w.kind !== "wear");
  expect("wear first", wanted.slice(0, wanted.length - events.length).every((w) => w.kind === "wear") && wanted.length > events.length, true);
  expect("the page's days' marks, capped", events.map((w) => w.kind), ["blood", "soot", "mud"].slice(0, PAGE_EVENT_MARKS));
  expect("keyed by save, day and kind", events[0]!.key, "marks|7|0|blood");
}

{  // seeded: the same save, page and boxes place the same marks; another save marks the page differently
  const wanted = (s: number) => wantedOf(s, page([3]), [day(3, ["water"])]);
  const a = JSON.stringify(placeMarks(wanted(5), ART, PAGE, []));
  expect("same again", JSON.stringify(placeMarks(wanted(5), ART, PAGE, [])), a);
  expect("another save differs", JSON.stringify(placeMarks(wanted(6), ART, PAGE, [])) !== a, true);
}

{  // every mark carries its own seeded transform: a wide spread of turns, both mirrors, scales and opacities, the same each draw
  const places = Array.from({ length: 300 }, (_, i) => placeMarks(wantedOf(i, page([i]), [day(i, ["soot"])]), ART, PAGE, [])).flat();
  const angles = places.map((p) => p.angle);
  expect("turns span the circle", Math.max(...angles) - Math.min(...angles) > 300, true);
  expect("mirrored both ways", [places.some((p) => p.flipX), places.some((p) => p.flipY)], [true, true]);
  expect("scale varies", new Set(places.map((p) => p.scale.toFixed(1))).size > 3, true);
  expect("opacity varies", new Set(places.map((p) => p.opacity.toFixed(2))).size > 20, true);
  const again = Array.from({ length: 300 }, (_, i) => placeMarks(wantedOf(i, page([i]), [day(i, ["soot"])]), ART, PAGE, [])).flat();
  expect("same seed, same marks and transforms", JSON.stringify(again), JSON.stringify(places));
}

{  // an art is not drawn twice on a page while another of its kind is unused
  for (let s = 0; s < 300; s++) {
    const placed = placeMarks(wantedOf(s, page([0]), [day(0, [])]), ART, PAGE, []);
    const srcs = placed.map((p) => p.src);
    expect(`save ${s}: no art twice`, new Set(srcs).size, srcs.length);
  }
}

{  // when the pool is spent, the repeat is mirrored and turned against the first and lies far from it
  const one: MarkManifest = { wear: [{ src: "wear-1.webp", w: 512, h: 512 }] };
  const wanted = [{ kind: "wear" as const, key: "a" }, { kind: "wear" as const, key: "b" }];
  let pairs = 0;
  for (let s = 0; s < 100; s++) {
    const [a, b] = placeMarks(wanted.map((w) => ({ ...w, key: `${w.key}${s}` })), one, PAGE, []);
    if (a === undefined || b === undefined) continue;
    pairs++;
    const turn = Math.abs(((b.angle - a.angle + 540) % 360) - 180);
    expect(`pair ${s}: mirrored against the first`, a.flipX !== b.flipX, true);
    expect(`pair ${s}: turned away`, turn >= REPEAT_TURN - 1e-6, true);
    const gap = Math.hypot(a.box.x + a.box.w / 2 - b.box.x - b.box.w / 2, a.box.y + a.box.h / 2 - b.box.y - b.box.h / 2);
    expect(`pair ${s}: far apart`, gap >= REPEAT_APART * Math.hypot(PAGE.w, PAGE.h), true);
  }
  expect("repeats were placed", pairs > 20, true);
}
