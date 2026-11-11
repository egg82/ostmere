// The stopped mix's lesson (game/lessons.ts, MIX_STOPPED), on the whole screen: the first running mix to grey over a done
// card marks Edit, and the lesson walks Edit, the add button of the card the content says takes its place (when it names
// one), the editor's ✕ on the done card and Save. Without a replacement, a mix with no other card left to run is not
// marked (its ✕ is off); a mix that is not greyed never is; kept or skipped, it never comes again.
import { fakeDocument, FakeEvent, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import type { Content } from "../src/api/types";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { CLOCK, FIRST_MIX, FIRST_RULE, LESSONS, MIX_STOPPED, mayStart } from "../src/game/lessons";
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
/** The same content with no card naming a replacement. */
const bare = new Catalog({ ...fixtureContent, card_infos: fixtureContent.card_infos.map((c) => ({ ...c, replaced_by: null })) } as Content);
const AT = 100;
const step = fixtureStep("greyed", AT);
const ACCOUNT = { ...NEW_FLAT, rule_seen: true, rules_opened: true, lessons: [FIRST_MIX, FIRST_RULE, CLOCK] };
const text = (key: string, slots: Record<string, string> = {}): string => catalog.text.fill(key, slots);
const done = catalog.cardLabel("tend");
const taker = catalog.cardLabel("look");

function rig(view: View, keeps: Keeps, cat: Catalog = catalog) {
  const decided: Decision[] = [];
  const screen = new Screen(cat, (d) => { decided.push(d); }, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show({ ...step, view });
  const lay = (n: Element = screen.root): void => {
    Object.assign(n, { rect: { left: 20, top: 300, width: 60, height: 16, right: 80, bottom: 316 } });
    for (const k of Array.from(n.children)) lay(k);
  };
  const frame = (ms = 1): void => { lay(); clock += ms; screen.tick(AT); };
  const mark = (): HTMLElement | null => screen.root.querySelector<HTMLElement>('[data-teach="mix-stopped"]');
  const note = (): string => { const n = screen.root.querySelector<HTMLElement>(".lesson-note"); return n && !n.hidden ? n.querySelector(".lesson-line")?.textContent ?? "" : ""; };
  const tap = (selector: string): void => {
    const n = screen.root.querySelector<HTMLElement>(selector);
    if (!n) throw new Error(`nothing to tap at ${selector}`);
    n.click();
    frame();
  };
  return { screen, decided, frame, mark, note, tap, keeps };
}

/** The walk to Save on the real controls: the done card's ✕ and Save, after the replacement's add button when `with` is set. */
function walk(r: ReturnType<typeof rig>, replacement: string | null): void {
  r.frame();
  expect("Edit carries the mark and the done card's name", [r.mark()?.className, r.mark()?.dataset["gone"], r.mark()?.dataset["with"]], ["hands-edit", done, replacement ?? undefined]);
  expect("step 1 names the done card" + (replacement ? " and the one that takes its place" : ""), r.note(),
    replacement ? text("ui.lesson.stopped_edit_with", { card: done, task: taker }) : text("ui.lesson.stopped_edit", { card: done }));
  r.tap(".hands-edit");
  r.frame();
  if (replacement) {
    expect("step 2: the add button of the card that takes its place", r.note(), text("ui.lesson.stopped_add", { task: taker }));
    fakeDocument.querySelector(`.editor .add-card[data-card="${replacement}"]`)?.dispatchEvent(new FakeEvent("click", { detail: 0 }));   // a key's tap: it joins
    r.frame();
  }
  expect("then the ✕ on the done card", r.note(), text("ui.lesson.stopped_drop", { card: done }));
  expect("the control it points at is that card's ✕", r.screen.root.querySelectorAll(".editor .editor-entry.struck .entry-remove").length, 1);
  r.tap(".editor .editor-entry.struck .entry-remove");
  r.frame();
  expect("then Save", r.note(), text("ui.lesson.stopped_save"));
  r.tap(".editor .editor-head .primary");
  r.frame(60_000);
  expect("done: kept in the save", r.keeps.lessonKept(MIX_STOPPED), true);
  const saved = r.decided.flatMap((d) => (d.kind === "save_mix" ? [d.mix.components.flatMap((c) => (c.kind === "card_share" ? [c.card] : []))] : []));
  expect("the mix was saved without the done card, and with its replacement when taught", [saved.at(-1)?.includes("tend"), saved.at(-1)?.includes("look")], [false, replacement !== null]);
}

walk(rig(step.view, keepsOf(ACCOUNT)), "look");   // the content names look as tend's replacement
walk(rig(step.view, keepsOf(ACCOUNT), bare), null);   // no replacement named: the three steps

{  // not marked: a mix that is not greyed; a greyed mix of the done card alone has the mark only when a replacement can be added first
  const running = rig({ ...step.view, greyed_mix_ids: [] }, keepsOf(ACCOUNT));
  running.frame();
  expect("a running mix: no mark", running.mark(), null);
  const only = step.view.mixes.map((m) => (m.id === step.view.active_mix_id ? { ...m, components: m.components.filter((c) => c.kind === "card_share" && c.card === "tend") } : m));
  const alone = rig({ ...step.view, mixes: only }, keepsOf(ACCOUNT));
  alone.frame();
  expect("a mix of the done card alone, a replacement to add first: marked", alone.mark()?.dataset["with"], "look");
  const bareAlone = rig({ ...step.view, mixes: only }, keepsOf(ACCOUNT), bare);
  bareAlone.frame();
  expect("alone, nothing to add first: no mark", bareAlone.mark(), null);
  const held = step.view.mixes.map((m) => (m.id === step.view.active_mix_id ? { ...m, components: [...m.components, { kind: "card_share" as const, card: "look", share_bp: 0 }] } : m));
  const has = rig({ ...step.view, mixes: held }, keepsOf(ACCOUNT));
  has.frame();
  expect("the replacement already in the mix: marked without an add step", [has.mark() !== null, has.mark()?.dataset["with"]], [true, undefined]);
}

{  // lessons off, or kept: it does not start
  const off = rig(step.view, keepsOf(ACCOUNT, null, { lessons: false }));
  off.frame();
  expect("lessons off: no note", off.note(), "");
  const kept = rig(step.view, keepsOf({ ...ACCOUNT, lessons: [...ACCOUNT.lessons, MIX_STOPPED] }));
  kept.frame();
  expect("kept: no note", kept.note(), "");
  const lesson = LESSONS.find((l) => l.id === MIX_STOPPED)!;
  expect("control: a save with a greyed mix may have it", mayStart(lesson, step.view, keepsOf(ACCOUNT)), true);
  expect("a save with no greyed mix may not", mayStart(lesson, { ...step.view, greyed_mix_ids: [] }, keepsOf(ACCOUNT)), false);
}
