// The Games sheet (src/ui/games.ts): the account's games with the one played marked, Open and Delete only on the others,
// Delete asked once more before it goes, a deleted game held with Restore, New game handed to the page and refused at
// the cap with the content's line; and the tab's game chosen from its address (begin.ts).
import { FakeEvent, fakeDocument, install, type FakeEl } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureGames } from "../fixtures/games";
import { ApiFailure, type GameApi } from "../src/api/api";
import type { NewSave, SaveInfo } from "../src/api/types";
import { tabGame } from "../src/begin";
import { Text } from "../src/game/text";
import { GamesSheet } from "../src/ui/games";
import { NEW_SAVE } from "../src/game/keeps";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const text = new Text(fixtureContent);
const later = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 5));
const no = (): Promise<never> => Promise.reject(new Error("not in these tests"));

function rig(begin: () => Promise<NewSave> = no) {
  const games = fixtureGames();
  const calls: string[] = [];
  const api: GameApi = {
    content: no, me: no, begin: () => { calls.push("begin"); return begin(); }, open: no, savedView: no, advance: no, forecast: no, decide: no, dryRun: no, putMePresentation: no, putMeSettings: no, putSavePresentation: no,
    sendFeedback: no, makeCode: no, makeWords: no, join: no, devices: no, removeDevice: no,
    games: () => { calls.push("games"); return games.games(); },
    deleteGame: (id) => { calls.push(`delete ${id}`); return games.deleteGame(id); },
    restoreGame: (id) => { calls.push(`restore ${id}`); return games.restoreGame(id); },
  };
  const opened: number[] = [];
  const begun: number[] = [];
  const sheet = new GamesSheet(api, text, { playing: () => 1, open: (id) => opened.push(id), begun: (m) => begun.push(m.save.save_id), straight: { get: () => false, set: () => undefined }, skipLessons: { get: () => false, set: () => undefined } });
  const holder = document.createElement("div");
  holder.append(sheet.button, sheet.root);
  document.body.replaceChildren(holder);
  return { sheet, calls, opened, begun };
}

function rows(): FakeEl[] {
  return fakeDocument.querySelectorAll("dialog > .games-list > .games-row");
}

function button(row: FakeEl, key: string): FakeEl {
  const found = row.querySelectorAll("button").find((b) => b.textContent === text.get(key));
  if (!found) throw new Error(`no ${key} button in the row`);
  return found;
}

function labels(row: FakeEl): string[] {
  return row.querySelectorAll("button").map((b) => b.textContent ?? "");
}

{  // the list: names, how far, the played one marked with no controls, the others with Open and Delete
  const r = rig();
  fakeDocument.querySelector("button.games-open")?.click();
  await later();
  expect("asked for the list", r.calls, ["games"]);
  const [playing, second, third] = rows();
  if (!playing || !second || !third) throw new Error("three live games and one held were not drawn");
  expect("the held game is listed under Deleted", fakeDocument.querySelectorAll(".games-held .games-row").length, 1);
  expect("the played game's name", playing.querySelector(".games-name")?.textContent, text.fill("ui.games.name", { number: "3" }));
  expect("its camp level", playing.querySelector(".games-camp")?.textContent, text.fill("ui.games.camp", { level: "2" }));
  expect("the played game is marked and has no controls", [playing.querySelector(".games-playing")?.textContent, labels(playing)],
    [text.get("ui.games.playing"), []]);
  expect("a camp level of none is not drawn", third.querySelector(".games-camp"), null);
  expect("another game's controls", labels(second), [text.get("ui.games.switch"), text.get("ui.games.delete")]);
  button(second, "ui.games.switch").click();
  expect("Open hands the game to the page", r.opened, [2]);
}
{  // Delete asks once more; Cancel takes it back; the second Delete deletes, and the game is held
  const r = rig();
  r.sheet.open();
  await later();
  button(rows()[1]!, "ui.games.delete").click();
  expect("the question", rows()[1]!.querySelector(".games-ask")?.textContent, text.fill("ui.games.delete_ask", { days: "30" }));
  expect("nothing deleted on the first tap", r.calls, ["games"]);
  button(rows()[1]!, "ui.games.cancel").click();
  expect("Cancel takes the question back", rows()[1]!.querySelector(".games-ask"), null);
  button(rows()[1]!, "ui.games.delete").click();
  button(rows()[1]!, "ui.games.delete").click();
  await later();
  expect("deleted once", r.calls, ["games", "delete 2"]);
  expect("two live left, two held", [rows().length, fakeDocument.querySelectorAll(".games-held .games-row").length], [2, 2]);
  const held = fakeDocument.querySelectorAll(".games-held .games-row")[0]!;
  button(held, "ui.games.restore").click();
  await later();
  expect("restored", [r.calls.at(-1), rows().length], ["restore 2", 3]);
  expect("a restored game does not come back asking", fakeDocument.querySelectorAll(".games-ask").length, 0);
}
{  // with one live game, it is the one played and offers Start over, not Delete
  const r = rig(() => Promise.resolve({ save: { save_id: 9 } as SaveInfo, presentation: NEW_SAVE, step: {} as NewSave["step"] }));
  r.sheet.open();
  await later();
  const other = (): FakeEl => rows().find((n) => !n.classList.contains("playing"))!;
  for (const id of [2, 3]) {
    button(other(), "ui.games.delete").click();
    button(other(), "ui.games.delete").click();   // the row is drawn again, asking
    await later();
    expect(`deleted ${id}`, r.calls.at(-1)?.startsWith("delete"), true);
  }
  const tapsNamed = (key: string): number => fakeDocument.querySelectorAll("dialog > .games-list button").filter((b) => b.textContent === text.get(key)).length;
  expect("one live game: Start over, no Delete", [rows().length, tapsNamed("ui.games.start_over"), tapsNamed("ui.games.delete")], [1, 1, 0]);
  const before = r.calls.length;
  button(rows()[0]!, "ui.games.start_over").click();
  expect("it asks first, and nothing is called", [fakeDocument.querySelector(".games-ask")?.textContent, r.calls.length], [text.fill("ui.games.start_over_ask", { days: "30" }), before]);
  button(rows()[0]!, "ui.games.start_over").click();
  await later();
  expect("a confirmed Start over begins, then deletes the old game", r.calls.slice(before), ["begin", "delete 1"]);
}
{  // Start over hands the new game to the page, as New game does; a refused begin deletes nothing and says why
  const made: NewSave = { save: { save_id: 9 } as SaveInfo, presentation: NEW_SAVE, step: {} as NewSave["step"] };
  const ok = rig(() => Promise.resolve(made));
  ok.sheet.open();
  await later();
  for (const id of [2, 3]) {
    rows().find((n) => !n.classList.contains("playing"))!.querySelectorAll("button").find((b) => b.textContent === text.get("ui.games.delete"))!.click();
    rows().find((n) => !n.classList.contains("playing"))!.querySelectorAll("button").find((b) => b.textContent === text.get("ui.games.delete"))!.click();
    await later();
    expect(`deleted ${id}`, ok.calls.at(-1), `delete ${id}`);
  }
  button(rows()[0]!, "ui.games.start_over").click();
  button(rows()[0]!, "ui.games.start_over").click();
  await later();
  expect("the new game goes to the page", ok.begun, [9]);
  const refused = rig(() => Promise.reject(new ApiFailure("rate_limited", "429")));
  refused.sheet.open();
  await later();
  for (const id of [2, 3]) {
    rows().find((n) => !n.classList.contains("playing"))!.querySelectorAll("button").find((b) => b.textContent === text.get("ui.games.delete"))!.click();
    rows().find((n) => !n.classList.contains("playing"))!.querySelectorAll("button").find((b) => b.textContent === text.get("ui.games.delete"))!.click();
    await later();
    expect(`deleted ${id}`, refused.calls.at(-1), `delete ${id}`);
  }
  const mark = refused.calls.length;
  button(rows()[0]!, "ui.games.start_over").click();
  button(rows()[0]!, "ui.games.start_over").click();
  await later();
  expect("a refused begin deletes nothing and is a line", [refused.calls.slice(mark), refused.begun, fakeDocument.querySelector(".games-note")?.textContent], [["begin"], [], text.get("ui.games.limited")]);
}
{  // New game: handed to the page; refused at the cap with the content's line
  const made: NewSave = { save: { save_id: 9 } as SaveInfo, presentation: NEW_SAVE, step: {} as NewSave["step"] };
  const r = rig(() => Promise.resolve(made));
  r.sheet.open();
  await later();
  const make = fakeDocument.querySelectorAll("button.primary").find((b) => b.textContent === text.get("ui.games.new"))!;
  make.dispatchEvent(new FakeEvent("click"));
  await later();
  expect("the new game goes to the page", r.begun, [9]);
  const full = rig(() => Promise.reject(new ApiFailure("too_many_saves", "409")));
  full.sheet.open();
  await later();
  fakeDocument.querySelectorAll("button.primary").find((b) => b.textContent === text.get("ui.games.new"))!.dispatchEvent(new FakeEvent("click"));
  await later();
  expect("the cap's line", fakeDocument.querySelector(".games-note")?.textContent, text.fill("ui.games.full", { max: "5" }));
  expect("nothing handed on", full.begun, []);
}
{  // the tab's game: the one its address names while it is live, else the most recently played
  const saves = [{ save_id: 5 }, { save_id: 8 }] as SaveInfo[];
  expect("named", tabGame(saves, "#game=8")?.save_id, 8);
  expect("named but gone", tabGame(saves, "#game=3")?.save_id, 5);
  expect("none named", tabGame(saves, "")?.save_id, 5);
  expect("another fragment", tabGame(saves, "#join=ABCD")?.save_id, 5);
  expect("no saves", tabGame([], "#game=8"), undefined);
}
