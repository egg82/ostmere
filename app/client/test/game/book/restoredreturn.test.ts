// A save opened again soon after a long return (too soon to be a return of its own, chronicle.ts AWAY_MIN_S): the
// return's lines now come back as the save's history (Opened.history), and the "Since you left" chapter is still that
// return's. A chip's off-lines that landed inside a kept return collapse to the chip's last change there, in the
// chronicle only, as they did when the return first showed them (game/book/awaylines.ts); a line from after the return,
// played live, is restored as it was shown, on the band. Driven through play() with a scripted api.
import type { GameApi } from "../../../src/api/api";
import type { Content, PastLine, Step } from "../../../src/api/types";
import { fixtureContent } from "../../../fixtures/content";
import { dayOneStep } from "../../../fixtures/dayone";
import { play } from "../../../src/game";
import { fakeDocument, install } from "../../fake-dom";
import { NEW_SAVE, NEW_ACCOUNT, NEW_SETTINGS } from "../../../src/game/account/keeps";

install();
const realInterval = globalThis.setInterval;   // the page's self-update polls forever; this run clears it to end
const polls: number[] = [];
Object.assign(globalThis, { setInterval: (f: () => void, ms: number) => { const id = realInterval(f, ms); polls.push(id); return id; } });
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } }, requestAnimationFrame: () => 0, addEventListener: () => undefined });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const OFF = "l_rested";
const OFF_TEXT = "[fixture] rested placeholder line.";
const content: Content = {
  ...fixtureContent,
  text_entries: [...fixtureContent.text_entries, { key: OFF, text: OFF_TEXT }],
  line_infos: [...fixtureContent.line_infos, { key: OFF, kind: "body" as const, cause: null, person: false, mention: null }],
  chip_infos: fixtureContent.chip_infos.map((c) => (c.chip === "tired" ? { ...c, off_line_keys: [OFF] } : c)),
};
const RETURN = { left: 1000, back: 4000 };
const inReturn: PastLine[] = Array.from({ length: 12 }, (_, i) => ({ n: i + 1, at: 1100 + i * 240, key: OFF }));
const live: PastLine = { n: 13, at: 4200, key: OFF };
const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };
const was = dayOneStep("returned", 4500).view;
const now0 = dayOneStep("returned", 5000);
const now: Step = { ...now0, save_id: 7, lines: [], view: { ...now0.view, chips: [] } };
const unused = (): Promise<never> => Promise.reject(new Error("not in this test"));

/** The page opened on a save whose history is `history`, its one kept return RETURN: the off-lines on the band and in
 * the chapter (every filter). */
async function opened(history: PastLine[]): Promise<{ band: number; chapter: number }> {
  const api: GameApi = { mixRows: () => Promise.reject(new Error("not in these tests")),
    content: () => Promise.resolve(content),
    me: unused, begin: unused,
    open: () => Promise.resolve({ save, was, history, presentation: { ...NEW_SAVE, visits: [RETURN] }, journal_days: [], step: now }),
    advance: () => Promise.resolve(now),
    savedView: unused,
    forecast: () => Promise.resolve({ decisions: 0, forecast: { horizon_at: 6000, level_ups: [], tops_out: [], fills: [], empties: [] } }),
    decide: unused, dryRun: unused,
    putMePresentation: (p) => Promise.resolve({ presentation: p, settings: NEW_SETTINGS, has_words: false, words_due: false }),
    putMeSettings: (settings) => Promise.resolve({ presentation: NEW_ACCOUNT, settings, has_words: false, words_due: false }),
    putSavePresentation: (_id, p) => Promise.resolve(p),
    sendFeedback: () => Promise.resolve(),
    makeCode: unused, makeWords: unused, games: unused, deleteGame: unused, restoreGame: unused, join: unused, devices: unused, removeDevice: unused,
  };
  fakeDocument.body.replaceChildren();
  const session = play(api, document.body, { resume: 7 }, "");
  await session.settled();
  const off = (sel: string): number => [...fakeDocument.querySelectorAll(sel)].filter((n) => n.textContent === OFF_TEXT).length;
  const band = off("ol.lines > li");
  (document.querySelector("button[data-tab=\"book\"]") as HTMLButtonElement).click();
  (document.querySelector("button.chron-filter[data-filter=\"all\"]") as HTMLButtonElement | null)?.click();
  return { band, chapter: off(".chapter .chron-text") };
}

expect("the return's off-lines: its last in the chapter, none on the band", await opened(inReturn), { band: 0, chapter: 1 });
expect("a live off-line after the return: on the band, and in the chapter's stretch", await opened([...inReturn, live]), { band: 1, chapter: 2 });
for (const id of polls) clearInterval(id);
