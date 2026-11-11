// The front page: the game's own camp on a stage, and a panel with the way in. A page load asks the server who this
// browser is (GET /api/me, which never makes an account). Without a save the stage shows a canned moment and Begin
// makes the save (and the account); under it, "I have a code" and "I have recovery words" join this browser to a game
// played elsewhere. With saves it lists them (ui/places.ts, beside the stage, or the Games button's sheet on a phone):
// the selected game's camp is the stage and Continue opens it (the save the tab's address names, #game=ID, else the
// newest), and selecting New game turns Continue into Begin. It is skipped, opening that save at once, when the address
// names a live save, when a join link came (its code waits in the game's "Another device" sheet), or when this device's
// "skip the front page" choice is on (app/straight.ts, set from the panel or the in-game Games sheet).
import { retryable, type GameApi } from "./api/api";
import type { Me, SaveInfo } from "./api/types";
import { browserStraight, type Straight } from "./app/straight";
import type { Session } from "./game/session";
import { play } from "./game";
import { joinWith, refusalLine, type Refused } from "./game/joining";
import { Text, UI } from "./game/text";
import { noteBegin } from "./telemetry";
import { dress } from "./ui/frontdress";

/** What opens a game on the page: the game's own `play`, or a spy in a test. */
export type PlayGame = (...args: Parameters<typeof play>) => Pick<Session, "begin">;

export function wireBegin(api: GameApi, sceneManifest?: string, join: string | null = null, straight: Straight = browserStraight(), playGame: PlayGame = play): void {
  const begin = document.getElementById("begin");
  if (!(begin instanceof HTMLButtonElement)) return;
  const body = document.body.classList;
  const limitedLine = document.getElementById("limited");
  let session: Pick<Session, "begin"> | null = null;
  let me: Me | null = null;
  const front = (): void => {
    body.remove("playing", "instant");
    body.add("front");
    begin.disabled = false;
    begin.hidden = false;
  };
  const limited = (): void => {   // Begin refused for now: one plain line, and Begin stays to be tried later
    front();
    if (limitedLine) limitedLine.hidden = false;
  };
  const unkept = (): void => {   // a game that cannot be kept in this frame: say so, offer its own tab, make no other game
    body.remove("playing", "instant");
    body.add("front");
    begin.hidden = true;
    const have = document.getElementById("have");   // a join here meets the same refused cookie
    if (have) have.hidden = true;
    void api.content().then((c) => showFramed(new Text(c)), () => undefined);
  };
  const start = (resume: number | null): void => {
    begin.disabled = true;
    if (limitedLine) limitedLine.hidden = true;
    noteBegin();
    body.add("playing");
    if (session) void session.begin();
    else session = playGame(api, document.body, { resume, limited, unkept, account: me?.account, join }, sceneManifest);
  };
  let resume: number | null = null;   // what the button opens: Continue's save, or (null) a new game
  begin.addEventListener("click", () => start(resume));
  void whoAmI(api).then((found) => {
    me = found;
    const saves = found?.saves ?? [];
    const chosen = entry(saves, location.hash, join !== null || straight.get());
    if (chosen.open) {
      body.add("playing", "instant");   // no front page flashes on the way in
      start(chosen.open.save_id);
      return;
    }
    front();
    if (!chosen.carryOn) wireHave(api, join);
    else resume = chosen.carryOn.save_id;
    void api.content().then((c) => {
      dress({ api, content: c, saves, max: found?.max_saves ?? saves.length, keptDays: found?.kept_days ?? 0, straight, carryOn: (id) => { resume = id; }, start });
    }, () => {
      if (chosen.carryOn) begin.textContent = begin.dataset["continue"] ?? begin.textContent;
    });
  });
}

/** Where a page load goes: `open` a save at once, or the front page, with `carryOn` the save its Continue opens
 * (none without saves). An address naming a live save, a join link and the device's choice all open at once. */
export function entry(saves: SaveInfo[], hash: string, straight: boolean): { open?: SaveInfo; carryOn?: SaveInfo } {
  const chosen = tabGame(saves, hash);
  if (chosen === undefined) return {};
  return straight || named(saves, hash) ? { open: chosen } : { carryOn: chosen };
}

function named(saves: SaveInfo[], hash: string): boolean {
  const m = /^#game=(\d+)$/.exec(hash);
  return m !== null && saves.some((s) => s.save_id === Number(m[1]));
}

/** index.html's #framed: the words and the link to the page's own address, opened in a tab of its own. */
function showFramed(text: Text): void {
  const box = document.getElementById("framed");
  const words = document.getElementById("framed-text");
  const link = document.getElementById("framed-link");
  if (!box || !words || !(link instanceof HTMLAnchorElement)) return;
  words.textContent = text.get(UI.frameKept);
  link.textContent = text.get(UI.frameOpen);
  link.href = location.origin + location.pathname;
  link.target = "_blank";
  link.rel = "noopener";
  box.hidden = false;
}

/** The save the tab's address names (#game=ID) when the account still has it live, else the most recently played. */
export function tabGame(saves: SaveInfo[], hash = location.hash): SaveInfo | undefined {
  const named = /^#game=(\d+)$/.exec(hash);
  return saves.find((s) => named !== null && s.save_id === Number(named[1])) ?? saves[0];
}

/** The front page's two join boxes (index.html #have); a join link's code opens the first, filled. */
function wireHave(api: GameApi, join: string | null): void {
  const have = document.getElementById("have");
  if (!have) return;
  have.hidden = false;
  const line = document.getElementById("join-said");
  const say = (refused: Refused | null): void => {   // the same words as the game's sheet, from the content
    if (!line) return;
    line.hidden = true;
    if (refused === null) return;
    if (refused.why === "ask") { location.reload(); return; }   // this browser has games after all: open them, ask there
    void api.content().then((c) => refusalLine(new Text(c), c.transfer_code_s, refused.why, refused.max),
      () => line.dataset["away"] ?? "")
      .then((said) => { line.textContent = said; line.hidden = false; });
  };
  for (const [formId, inputId] of [["join-code-form", "join-code"], ["join-words-form", "join-words"]] as const) {
    const form = document.getElementById(formId);
    const input = document.getElementById(inputId);
    if (!(form instanceof HTMLFormElement) || !(input instanceof HTMLInputElement)) continue;
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const typed = input.value.trim();
      say(null);
      if (typed) void joinWith(api, typed).then(say);
    });
  }
  const code = document.getElementById("join-code");
  const box = document.getElementById("have-code");
  if (join !== null && code instanceof HTMLInputElement && box instanceof HTMLDetailsElement) {
    box.open = true;
    code.value = join;
    code.focus();
  }
}

/** GET /api/me, asked again while the server cannot answer (a deploy): a returning player must not be shown Begin
 * because the server was briefly away. Null when it answers something else (the front page then shows). */
async function whoAmI(api: GameApi): Promise<Me | null> {
  for (let wait = 1000; ; wait = Math.min(wait * 2, 30000)) {
    try {
      return await api.me();
    } catch (e) {
      if (!retryable(e)) return null;
      await new Promise((r) => setTimeout(r, wait));
    }
  }
}
