// The front page's list of games (ui/places.ts): every game newest first and New game last, left out when the account is
// full; the newest selected at the start; a tap selects, a second tap on the selected row opens; on a phone a tap opens;
// a game with no camp level says nothing of one; a view that fails is a plain dark frame, never the empty camp.
import { FakeEl, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { ApiFailure } from "../src/api/api";
import type { SaveInfo, View } from "../src/api/types";
import { Text } from "../src/game/text";
import { Places, type Paint } from "../src/ui/places";
import { NEW_SAVE } from "../src/game/keeps";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

/** The fake element behind a node the page code made (install() put the fake document under it). */
function fake(node: unknown): FakeEl {
  if (!(node instanceof FakeEl)) throw new Error("not a fake element");
  return node;
}

const NOW = Date.parse("2026-11-06T12:00:00Z");
const text = new Text(fixtureContent);
const later = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 5));
const camp: View = fixtureStep("standing", 100, {}, 0).view;
const ruin: View = { ...camp, at: -1 };

function save(id: number, hoursAgo: number, campLevel: number | null): SaveInfo {
  const at = new Date(NOW - hoursAgo * 3_600_000).toISOString();
  return { save_id: id, number: id, decisions: 0, game_time: 0, ended_at: null, started_at: at, played_at: at, camp_level: campLevel };
}

function rig(saves: SaveInfo[], over: { failing?: number[]; max?: number; paint?: Paint | null; refuse?: ApiFailure; beginRefuse?: ApiFailure } = {}) {
  const asked: number[] = [];
  const deleted: number[] = [];
  const painted: { box: FakeEl; view: View }[] = [];
  const log: string[] = [];
  const order: string[] = [];
  const failing = over.failing ?? [];
  const paint: Paint | null = over.paint === undefined ? (box, view) => painted.push({ box: fake(box), view }) : over.paint;
  const places = new Places({
    keptDays: 30,
    api: {
      begin: () => { order.push("begin"); return over.beginRefuse ? Promise.reject(over.beginRefuse) : Promise.resolve({ save: save(99, 0, null), presentation: NEW_SAVE, step: fixtureStep("standing", 100, {}, 0) }); },
      deleteGame: (id) => {
        deleted.push(id);
        order.push(`delete ${id}`);
        if (over.refuse) return Promise.reject(over.refuse);
        return Promise.resolve({ saves: saves.filter((s) => s.save_id !== id), deleted: [], max_saves: over.max ?? 5, kept_days: 30 });
      },
      savedView: (id) => { asked.push(id); return failing.includes(id) ? Promise.reject(new ApiFailure("save_unavailable", "unavailable")) : Promise.resolve(camp); },
    },
    text, saves, max: over.max ?? 5, paint: Promise.resolve(paint), empty: ruin, now: () => NOW,
    open: (id) => log.push(`open ${id}`), picked: (s) => log.push(`picked ${s?.save_id ?? "new"}`),
    begin: () => { log.push("begin"); return Promise.resolve(); },
  });
  document.body.replaceChildren();
  const root = fake(places.root);
  fakeDocument.body.append(root);
  const rows = (): FakeEl[] => root.querySelectorAll("button.place");
  const buttons = (label: string): FakeEl[] => root.querySelectorAll("button").filter((b) => b.textContent === label);
  return { places, rows, asked, painted, log, root, deleted, buttons, order };
}

const three = [save(3, 3, 4), save(1, 48, 2), save(2, 26, null)];   // newest first

{  // one game: that game and New game
  const r = rig([save(7, 3, 4)]);
  expect("one save gives two rows", r.rows().length, 2);
  expect("the last row is New game", r.rows()[1]?.querySelector(".pname")?.textContent, text.get("ui.games.new"));
}
{  // three games: four rows, newest first, the heading the content's "Games"
  const r = rig(three);
  expect("three saves give four rows", r.rows().length, 4);
  expect("names in order", r.rows().map((b) => b.querySelector(".pname")?.textContent), ["Game 3", "Game 1", "Game 2", "New game"]);
  expect("the heading", r.root.querySelector(".places-heading")?.textContent, "Games");
  expect("each game's own view was asked for, all at once", r.asked, [3, 1, 2]);
}
{  // a full account has no New game row
  const r = rig([1, 2, 3, 4, 5].map((i) => save(i, i, 1)), { max: 5 });
  expect("five games, no New game", r.rows().map((b) => b.querySelector(".pname")?.textContent), ["Game 1", "Game 2", "Game 3", "Game 4", "Game 5"]);
}
{  // the newest is selected at the start, and only it
  const r = rig(three);
  expect("selected at start", r.rows().map((b) => b.getAttribute("aria-pressed")), ["true", "false", "false", "false"]);
  expect("current", r.places.current?.save_id, 3);
}
{  // a first tap selects (and opens nothing); a second tap on the same row opens it
  const r = rig(three);
  r.rows()[1]?.click();
  expect("the first tap selects", [r.log, r.places.current?.save_id], [["picked 1"], 1]);
  expect("the mark moves", r.rows().map((b) => b.getAttribute("aria-pressed")), ["false", "true", "false", "false"]);
  r.rows()[1]?.click();
  expect("the second tap opens it", r.log, ["picked 1", "open 1"]);
}
{  // the newest is already selected: one tap on it is Continue
  const r = rig(three);
  r.rows()[0]?.click();
  expect("a tap on the selected newest opens it", r.log, ["open 3"]);
}
{  // New game is selected like a game: a first tap selects it, a second begins
  const r = rig(three);
  r.rows()[3]?.click();
  expect("the first tap on New game selects it", [r.log, r.places.current, r.rows().map((b) => b.getAttribute("aria-pressed"))], [["picked new"], null, ["false", "false", "false", "true"]]);
  r.rows()[3]?.click();
  await later();
  expect("the second tap begins", r.log, ["picked new", "begin"]);
}
{  // a phone's sheet is the picker: a tap opens, New game begins, and no row claims to be pressed
  const r = rig(three);
  r.places.opensDirectly(true);
  r.rows()[2]?.click();
  r.rows()[3]?.click();
  await later();
  expect("taps act at once", r.log, ["open 2", "begin"]);
  expect("nothing marked", r.rows().map((b) => b.getAttribute("aria-pressed")), [null, null, null, null]);
}
{  // a game with no camp level says nothing of one; played is relative
  const r = rig(three);
  const meta = (i: number) => r.rows()[i]?.querySelectorAll(".pmeta").map((m) => m.textContent);
  expect("camp level and when", meta(0), ["Camp level 4", "Last played 3 hours ago"]);
  expect("null camp level is omitted", meta(2), ["Last played yesterday"]);
  expect("New game has no lines", meta(3), []);
}
{  // each picture is drawn from the view it asked for; New game's is the empty camp
  const r = rig(three);
  await later();
  expect("a picture per row", r.painted.length, 4);
  expect("each game is drawn from its own view", r.painted.filter((p) => p.view === camp).length, 3);
  expect("New game draws the empty camp", r.painted.filter((p) => p.view === ruin).length, 1);
}
{  // a view that fails: a plain dark frame for that row only, and the empty camp is not drawn in its place
  const r = rig(three, { failing: [1] });
  await later();
  const pic = (i: number) => r.rows()[i]?.querySelector(".pic");
  expect("the failed row's frame", pic(1)?.classList.contains("failed"), true);
  expect("the others are not marked", [pic(0), pic(2), pic(3)].map((p) => p?.classList.contains("failed")), [false, false, false]);
  expect("nothing drawn into the failed frame", r.painted.some((p) => p.box === (pic(1) as FakeEl)), false);
  expect("no empty camp on the failed row", r.painted.filter((p) => p.view === ruin).length, 1);
  expect("the failed row is still a row, with its words", r.rows()[1]?.querySelector(".pname")?.textContent, "Game 1");
}
{  // no scene art at all: every frame is dark, none lies
  const r = rig(three, { paint: null });
  await later();
  expect("all dark", r.rows().map((b) => b.querySelector(".pic")?.classList.contains("failed")), [true, true, true, true]);
}

const DELETE = text.get("ui.games.delete");
const START_OVER = text.get("ui.games.start_over");
{  // a phone's sheet: every row has Delete; the first tap asks, a second deletes; Cancel asks nothing more
  const r = rig(three);
  r.places.opensDirectly(true);
  expect("a Delete per row", r.buttons(DELETE).length, 3);
  r.buttons(DELETE)[1]?.click();
  expect("one tap asks and deletes nothing", [r.deleted, r.root.textContent.includes(text.fill("ui.games.delete_ask", { days: "30" }))], [[], true]);
  r.buttons(text.get("ui.games.cancel"))[0]?.click();
  expect("Cancel puts Delete back, still nothing deleted", [r.deleted, r.buttons(DELETE).length], [[], 3]);
  r.buttons(DELETE)[1]?.click();
  r.buttons(DELETE)[1]?.click();   // the asked row's Delete now confirms
  await later();
  expect("the second tap deletes that game", r.deleted, [1]);
  expect("the list is redrawn without it", r.rows().map((b) => b.querySelector(".pname")?.textContent), ["Game 3", "Game 2", "New game"]);
}
{  // two games still offer Delete, not Start over
  const two = rig([save(7, 3, 4), save(8, 9, 2)]);
  two.places.opensDirectly(true);
  expect("Delete per row, no Start over", [two.buttons(DELETE).length, two.buttons(START_OVER).length], [2, 0]);
}
{  // the only game offers Start over, not Delete; and a refusal is a line, not a lost list
  const one = rig([save(7, 3, 4)]);
  one.places.opensDirectly(true);
  expect("Start over, no Delete, on the only game", [one.buttons(DELETE).length, one.buttons(START_OVER).length], [0, 1]);
  one.buttons(START_OVER)[0]?.click();
  expect("it asks first, and nothing is called", [one.root.textContent.includes(text.fill("ui.games.start_over_ask", { days: "30" })), one.order], [true, []]);
  one.buttons(START_OVER)[0]?.click();   // the asked row's Start over now confirms
  await later();
  expect("a begin, then the old game's delete, then the new game opens", [one.order, one.log], [["begin", "delete 7"], ["open 99"]]);
  const refused = rig([save(7, 3, 4)], { beginRefuse: new ApiFailure("rate_limited", "429") });
  refused.places.opensDirectly(true);
  refused.buttons(START_OVER)[0]?.click();
  refused.buttons(START_OVER)[0]?.click();
  await later();
  expect("a refused begin deletes nothing, opens nothing, and says why", [refused.order, refused.log, refused.root.querySelector(".places-note")?.textContent], [["begin"], [], text.get("ui.games.limited")]);
  const r = rig(three, { refuse: new ApiFailure("rate_limited", "429") });
  r.places.opensDirectly(true);
  r.buttons(DELETE)[0]?.click();
  r.buttons(DELETE)[0]?.click();   // the asked row's Delete now confirms
  await later();
  expect("the refusal's line", r.root.querySelector(".places-note")?.textContent, text.get("ui.games.limited"));
  expect("the list is as it was", r.rows().length, 4);
}
{  // at the cap there is no New game; a delete brings it back and selects the newest left
  const full = [1, 2, 3, 4, 5].map((i) => save(i, i, 1));
  const r = rig(full, { max: 5 });
  r.places.opensDirectly(true);
  expect("full: five rows", r.rows().length, 5);
  r.buttons(DELETE)[0]?.click();
  r.buttons(DELETE)[0]?.click();   // the asked row's Delete now confirms
  await later();
  expect("New game is back", r.rows().map((b) => b.querySelector(".pname")?.textContent), ["Game 2", "Game 3", "Game 4", "Game 5", "New game"]);
  expect("the newest left is selected", r.places.current?.save_id, 2);
}
