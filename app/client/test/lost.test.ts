// A session lost on a page: reload, except a game just begun inside another site's frame (src/game/lost.ts).
import { framed, onLost, type FrameView } from "../src/game/lost";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const top = {};
const inFrame = { top, self: {} };
const alone = { top, self: top };
const unreadable = { get top(): unknown { throw new Error("cross-origin"); }, self: {} };

function lose(win: FrameView, fresh: boolean): string {
  const did: string[] = [];
  onLost(win, fresh, () => did.push("unkept"), () => did.push("reload"));
  return did.join();
}

check(framed(inFrame) && !framed(alone), "framed is top differing from self");
check(framed(unreadable), "a window whose top cannot be read is taken to be framed");
check(lose(inFrame, true) === "unkept", "a game just begun and lost inside a frame shows the message and does not reload");
check(lose(alone, true) === "reload", "unframed, a lost session still reloads");
check(lose(inFrame, false) === "reload", "framed but long established, a lost session still reloads");
