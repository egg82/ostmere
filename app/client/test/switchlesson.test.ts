// The switch-mix lesson (game/lessons.ts, SWITCH_MIX), on the whole screen: after the end, a build waits on a store nothing at
// work makes, and the strip marks the way to the saved mix that makes it (Mixes ▾, or the mix's name) or Edit. Taught on the real
// controls: the list's Run on that mix, or Edit, the add button of the card that makes the store, and Save. Kept or skipped, it
// never comes again; lessons off, it never starts.
import { fakeDocument, FakeEvent, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { dayOneStep } from "../fixtures/dayone";
import type { Decision, Mix, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import type { Keeps } from "../src/game/keeps";
import { CLOCK, FIRST_MIX, FIRST_RULE, SWITCH_MIX } from "../src/game/lessons";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800 });
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const step = dayOneStep("whenready", AT);
const builds = step.view;
const running = builds.running_mix_id!;
const woodMix = builds.mixes.find((m) => m.id !== running && m.id !== builds.active_mix_id && m.components.some((c) => c.kind === "card_share" && c.card === "gather"))!;
const runningOnly: View = { ...builds, mixes: builds.mixes.filter((m) => m.id === running) };
const ACCOUNT = { ...NEW_FLAT, rule_seen: true, rules_opened: true, lessons: [FIRST_MIX, FIRST_RULE, CLOCK] };
const text = (key: string, slots: Record<string, string> = {}): string => catalog.text.fill(key, slots);
const build = catalog.cardLabel("lean_to"), store = catalog.storeLabel("wood");

function rig(view: View, keeps: Keeps) {
  const decided: Decision[] = [];
  const screen = new Screen(catalog, (d) => { decided.push(d); }, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show({ ...step, view });
  const lay = (n: Element = document.body): void => {
    Object.assign(n, { rect: { left: 20, top: 300, width: 60, height: 16, right: 80, bottom: 316 } });
    for (const k of Array.from(n.children)) lay(k);
  };
  const frame = (ms = 1): void => { lay(); clock += ms; screen.tick(AT); };
  const mark = (): HTMLElement | null => document.querySelector<HTMLElement>("[data-switch]");
  const note = (): string => { const n = document.querySelector<HTMLElement>(".lesson-note"); return n && !n.hidden ? n.querySelector(".lesson-line")?.textContent ?? "" : ""; };
  const tap = (selector: string): void => {
    const n = document.querySelector<HTMLElement>(selector);
    if (!n) throw new Error(`nothing to tap at ${selector}`);
    n.click();
    frame();
  };
  return { screen, decided, frame, mark, note, tap, keeps };
}

{  // a saved mix makes the wood: the way to the list, then that mix's Run
  const r = rig(builds, keepsOf(ACCOUNT));
  r.frame();
  expect("the mark is on the mix's name, with the build, the store and the mix", [r.mark()?.classList.contains("hands-name"), r.mark()?.dataset["switch"], r.mark()?.dataset["mix"]], [true, "mixes", woodMix.id]);
  expect("step 1 names the build, the store and the mix", r.note(), text("ui.lesson.switch_mixes", { build, store, mix: woodMix.id }));
  r.tap(".hands-mix .hands-name");
  r.frame();
  expect("step 2: that mix's Run", r.note(), text("ui.lesson.switch_run", { mix: woodMix.id }));
  r.tap(`.selector-run[data-mix="${woodMix.id}"]`);
  r.frame(60_000);
  expect("done: kept in the save", r.keeps.lessonKept(SWITCH_MIX), true);
  expect("the tap switched to that mix", r.decided.filter((d) => d.kind === "switch_mix").map((d) => (d.kind === "switch_mix" ? d.mix_id : "")), [woodMix.id]);
}

{  // only the running mix: Edit, the card's add button, Save
  const r = rig(runningOnly, keepsOf(ACCOUNT));
  r.frame();
  expect("the mark is on Edit", [r.mark()?.classList.contains("hands-edit"), r.mark()?.dataset["switch"], r.mark()?.dataset["card"]], [true, "edit", "gather"]);
  expect("step 1", r.note(), text("ui.lesson.switch_edit", { build, store, task: catalog.cardLabel("gather") }));
  r.tap(".hands-edit");
  r.frame();
  expect("step 2: the add button", r.note(), text("ui.lesson.stopped_add", { task: catalog.cardLabel("gather") }));
  fakeDocument.querySelector(`.editor .add-card[data-card="gather"]`)?.dispatchEvent(new FakeEvent("click", { detail: 0 }));
  r.frame();
  expect("step 3: Save", r.note(), text("ui.lesson.switch_save", { store }));
  r.tap(".editor .editor-head .primary");
  r.frame(60_000);
  expect("done: kept in the save", r.keeps.lessonKept(SWITCH_MIX), true);
  const saved = r.decided.flatMap((d) => (d.kind === "save_mix" ? [d.mix as Mix] : []));
  expect("the saved mix holds the card", saved.at(-1)?.components.some((c) => c.kind === "card_share" && c.card === "gather"), true);
}

{  // no cue, no mark; lessons off or kept, no mark either; the old glow is gone
  const quiet = rig({ ...builds, ended_at: null }, keepsOf(ACCOUNT));
  quiet.frame();
  expect("before the end: no mark", quiet.mark() === null, true);
  const off = rig(builds, keepsOf(ACCOUNT, null, { lessons: false }));
  off.frame();
  expect("lessons off: no mark, no note, no glow on the strip", [off.mark() === null, off.note(), off.screen.root.querySelector(".hands-name.glow, .hands-edit.glow") === null], [true, "", true]);
  const kept = rig(builds, keepsOf({ ...ACCOUNT, lessons: [...ACCOUNT.lessons, SWITCH_MIX] }));
  kept.frame();
  expect("kept: no mark, no glow on the strip", [kept.mark() === null, kept.screen.root.querySelector(".hands-name.glow, .hands-edit.glow") === null], [true, true]);
}
