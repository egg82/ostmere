// The stated aim, as a contract (written blind, from the contract alone, not the implementation): at any view the page
// states the text of the last Content.aim_infos entry whose `after` is in view.unlocked (only the first has none); it
// is set from the first view, a page opened on a later save shows the latest at once, and a changed aim waits behind
// the arrival queue while the first does not; content with no aims leaves the line empty and keeps its room; on a
// phone the line sits in the stage after the band's head row and before the scene box, on a desktop in .left before
// the stage.
import { FakeEl, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { AimInfo, Content, Step, Unlock } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { PHONE } from "../src/ui/layout";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

// ---- environment: a clock and a phone switch ----
let now = 0;
let phone = false;
Object.assign(globalThis, { performance: { now: () => now } });
Object.assign(window, {
  matchMedia: (query: string) => ({ matches: query === PHONE ? phone : false, addEventListener: () => undefined }),
  innerWidth: 400, innerHeight: 800,
});
// Everything is on screen: the arrival queue shows a thing at once when it is out of sight (below the fold on a phone),
// and the fake DOM has no layout, so every rectangle would read as out of sight.
FakeEl.prototype.getBoundingClientRect = () => ({ left: 10, top: 10, width: 100, height: 20, right: 110, bottom: 30 });

const AT = 100;
const start = fixtureStep("start", AT);
const mid = fixtureStep("mid", AT);
const has = (view: Step["view"], u: Unlock): boolean => view.unlocked.some((x) => x.category === u.category && x.id === u.id);
const fresh = mid.view.unlocked.filter((u) => !has(start.view, u));
const [U1, U2] = fresh;
if (!U1 || !U2) throw new Error("the fixture's mid step should unlock two things its start does not");
const stepAt = (unlocked: Unlock[]): Step => ({ ...mid, view: { ...mid.view, unlocked } });
const startPlus = (...more: Unlock[]): Step => ({ ...start, view: { ...start.view, unlocked: [...start.view.unlocked, ...more] } });

const TEXTS = { a0: "Aim zero text", a1: "Aim one text", a2: "Aim two text" };
const infos = (...aims: [keyof typeof TEXTS, Unlock | null][]): AimInfo[] => aims.map(([id, after]) => ({ aim: id, text_key: `aim.${id}`, after }));
function contentWith(aims: AimInfo[]): Content {
  const entries = Object.entries(TEXTS).map(([id, text]) => ({ key: `aim.${id}`, text }));
  return { ...fixtureContent, aim_infos: aims, text_entries: [...fixtureContent.text_entries, ...entries] };
}

/** The one node mounted on the page: a real-typed root seen as the fake element it is. */
function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

function open(aims: AimInfo[], first: Step, onPhone = false): { screen: Screen; top: FakeEl } {
  phone = onPhone;
  now = 0;
  const screen = new Screen(new Catalog(contentWith(aims)), () => undefined, () => Promise.resolve(null), new Keeps());
  const top = mounted(screen.root);
  screen.show(first);
  return { screen, top };
}

const walk = (n: FakeEl): FakeEl[] => [n, ...n.children.flatMap(walk)];
const drawn = (n: FakeEl, top: FakeEl): boolean => {
  for (let x: FakeEl | null = n; x; x = x.parent) {
    if (x.hidden) return false;
    if (x === top) return true;
  }
  return true;
};
/** Which of the three aims' texts the page states (a leaf element whose whole text is it, drawn). */
function stated(top: FakeEl): string[] {
  const all = Object.values(TEXTS);
  return walk(top).filter((n) => n.children.length === 0 && all.includes(n.textContent) && drawn(n, top)).map((n) => n.textContent);
}
const settle = (screen: Screen): void => { now += 600_000; for (let i = 0; i < 20; i += 1) screen.tick(AT); };

const THREE = infos(["a0", null], ["a1", U1], ["a2", U2]);

// ---- 1. the last entry whose `after` is unlocked
{
  const cases: [string, Unlock[], string][] = [
    ["neither after unlocked: the first", start.view.unlocked, TEXTS.a0],
    ["only the first after: its aim", [...start.view.unlocked, U1], TEXTS.a1],
    ["only the second after: its aim", [...start.view.unlocked, U2], TEXTS.a2],
    ["both: the last in content order", [...start.view.unlocked, U1, U2], TEXTS.a2],
  ];
  for (const [label, unlocked, want] of cases) {
    const { top } = open(THREE, stepAt(unlocked));
    expect(`at a view: ${label}`, stated(top), [want]);
  }
  // Content order decides, not unlock order and not the aim's id: here a1 comes after a2 in the content.
  const swapped = infos(["a0", null], ["a2", U2], ["a1", U1]);
  const { top } = open(swapped, stepAt([...start.view.unlocked, U1, U2]));
  expect("both unlocked: the later entry in content order wins", stated(top), [TEXTS.a1]);
}

// ---- 2. set from the first view of a new game, with no wait
{
  const { top } = open(THREE, start);
  expect("first view of a new game: the first aim, at once", stated(top), [TEXTS.a0]);
}

// ---- 3. a page opened on a save further along shows the latest aim at once
{
  const { top } = open(THREE, stepAt([...start.view.unlocked, U1, U2]));
  expect("opened further along: the latest aim at once, no tick, no waiting", stated(top), [TEXTS.a2]);
}

// ---- 4. a changed aim waits behind the arrival queue
{
  const { screen, top } = open(THREE, start);
  expect("before the step: the first", stated(top), [TEXTS.a0]);
  screen.show(stepAt([...start.view.unlocked, U1, U2]));   // mid brings story lines: the queue is busy
  expect("the step brings lines the queue is still showing", screen.revealing, true);
  expect("while the queue is busy: the old aim still stands", stated(top), [TEXTS.a0]);
  settle(screen);
  expect("once the queue has run: the new aim", stated(top), [TEXTS.a2]);
  expect("the queue is spent", screen.revealing, false);
}
{
  const { screen, top } = open(THREE, start);
  screen.show(stepAt([...start.view.unlocked, U1]));
  settle(screen);
  expect("a step later: one aim is stated, the one for what is unlocked", stated(top), [TEXTS.a1]);
}

// ---- 5. no aims: the line is empty and keeps its room (checked below beside the placement)

// ---- 6. placement
/** The line's slot: the child of `parent` the aim sits in, found by position, so an empty line is found too. */
function sceneBoxOf(stage: FakeEl): FakeEl {
  const box = stage.children.find((c) => c.classList.contains("scene-box"));
  if (!box) throw new Error("the stage holds no scene box");
  return box;
}
function slotOf(top: FakeEl, onPhone: boolean): { slot: FakeEl | undefined; around: string } {
  const stage = top.querySelector(".stage");
  const left = top.querySelector(".left");
  if (!stage || !left) throw new Error("no .stage or .left");
  if (onPhone) {
    const box = sceneBoxOf(stage);
    const at = stage.children.indexOf(box);
    return { slot: stage.children[at - 1], around: `stage children before the scene box: ${at}` };
  }
  return { slot: left.children[0] === stage ? undefined : left.children[0], around: `left holds ${left.children.length} children` };
}
const within = (leaf: FakeEl, slot: FakeEl): boolean => slot.contains(leaf);

for (const onPhone of [true, false]) {
  const where = onPhone ? "phone" : "desktop";
  const { top } = open(THREE, start, onPhone);
  const leaf = walk(top).find((n) => n.children.length === 0 && n.textContent === TEXTS.a0);
  if (!leaf) throw new Error(`${where}: the aim is not on the page`);
  const stage = top.querySelector(".stage");
  const left = top.querySelector(".left");
  if (!stage || !left) throw new Error("no .stage or .left");
  const { slot } = slotOf(top, onPhone);
  expect(`${where}: the aim sits in its slot`, slot !== undefined && within(leaf, slot), true);
  if (onPhone) {
    const box = sceneBoxOf(stage);
    const at = stage.children.findIndex((c) => within(leaf, c));
    expect("phone: the aim is in the stage", at >= 0, true);
    expect("phone: the band's head row comes first in the stage", at > 0, true);
    expect("phone: the aim is just before the scene box", at + 1, stage.children.indexOf(box));
    expect("phone: the stage is where it was (inside .left)", left.contains(stage), true);
  } else {
    expect("desktop: the aim is the first thing in .left", left.children.findIndex((c) => within(leaf, c)), 0);
    expect("desktop: before the stage", left.children.indexOf(stage), left.children.findIndex((c) => within(leaf, c)) + 1);
    expect("desktop: not inside the stage", stage.contains(leaf), false);
  }
}

// ---- 7. no aims: empty, and the room is kept (same slot as with aims)
for (const onPhone of [true, false]) {
  const where = onPhone ? "phone" : "desktop";
  const withAims = open(THREE, start, onPhone);
  const full = slotOf(withAims.top, onPhone).slot;
  const bare = open([], start, onPhone);
  const { slot, around } = slotOf(bare.top, onPhone);
  if (!slot || !full) throw new Error(`${where}: with no aims the slot is gone (${around})`);
  expect(`${where}: no aims, the line says nothing`, slot.textContent, "");
  expect(`${where}: no aims, no aim text on the page`, stated(bare.top), []);
  expect(`${where}: no aims, the slot is not hidden`, drawn(slot, bare.top), true);
  expect(`${where}: no aims, the slot is not display:none`, slot.style["display"] === "none", false);
  expect(`${where}: the slot is the same kind of element with or without aims`, [slot.tagName, slot.className], [full.tagName, full.className]);
}

console.log("aimcontract: ok");
