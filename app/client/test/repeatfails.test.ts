// A failed tap's line is not stacked: the same failed line again, directly after itself, is not appended to the
// band or the Log; a story line between (or a different line) lets it speak again.
import { fixtureStep } from "../fixtures/steps";
import { fixtureContent } from "../fixtures/content";
import type { Content, LogLine, Step } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";
import { install } from "./fake-dom";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content: Content = {
  ...fixtureContent,
  text_entries: [...fixtureContent.text_entries, ...["l_fail", "l_story"].map((key) => ({ key, text: `[fixture] ${key}.` }))],
  line_infos: [...fixtureContent.line_infos, { key: "l_fail", kind: "tap" }, { key: "l_story", kind: "story" }],
};
const catalog = new Catalog(content);
const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
document.body.replaceChildren(screen.root);

const first = fixtureStep("mid", 50);
const c0 = first.view.cards[0];
if (!c0) throw new Error("fixture has no card");
const line = (key: string, seq: number): LogLine => ({ at: 60, seq, key, card: key === "l_fail" ? c0.card : null });
const step = (_at: number, failed: boolean, lines: LogLine[]): Step => ({ ...first, lines, failed_tap: failed ? c0.card : null });
const band = (): string[] => [...screen.root.querySelectorAll("ol.lines > li")].map((n) => n.textContent ?? "");
const failLines = (): number => band().filter((t) => t.includes("l_fail")).length;
const logged = (): string[] => screen.storyPast.map((p) => p.key);

screen.show(first);
screen.show(step(60, true, [line("l_fail", 0)]));
screen.show(step(61, true, [line("l_fail", 1)]));
screen.show(step(62, true, [line("l_fail", 2)]));
expect("a failed line repeated directly after itself shows once", failLines(), 1);
expect("and is kept once in the story keys", logged().filter((k) => k === "l_fail").length, 1);

screen.show(step(70, false, [line("l_story", 0)]));
screen.show(step(80, true, [line("l_fail", 0)]));
expect("after a story line it speaks again", logged().filter((k) => k === "l_fail").length, 2);

screen.show(step(90, false, [line("l_story", 0)]));
screen.show(step(91, false, [line("l_story", 1)]));
expect("story lines are never dropped", logged().filter((k) => k === "l_story").length, 3);
