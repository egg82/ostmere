// The panel's scroll cue (ui/morecue.ts): the panel wears `more` while its content runs past the bottom and it is
// not scrolled to the end; game.css fades its foot then.
import { install } from "./fake-dom";
import { MoreCue } from "../src/ui/morecue";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const panel = document.createElement("section");
const cue = new MoreCue(panel, document.createElement("div"));
const more = (): boolean => panel.classList.contains("more");
const move = (to: { scrollHeight: number; clientHeight: number; scrollTop: number }): void => { Object.assign(panel, to); cue.update(); };

move({ scrollHeight: 1100, clientHeight: 900, scrollTop: 0 });
expect("content runs past the bottom: the cue", more(), true);
move({ scrollHeight: 1100, clientHeight: 900, scrollTop: 150 });
expect("part way down: still the cue", more(), true);
move({ scrollHeight: 1100, clientHeight: 900, scrollTop: 200 });
expect("scrolled to the end: no cue", more(), false);
move({ scrollHeight: 900, clientHeight: 900, scrollTop: 0 });
expect("content fits: no cue", more(), false);
