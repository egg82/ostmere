// The lesson runner's rules for every lesson's steps (ui/lessons.ts): when a step starts and its control, or the rows it
// keeps clear, is not what the page shows at that spot (off the window, under a pinned strip), the control is scrolled to
// the middle, once (at once under reduced motion); a read step never holds back a tap on a later step's
// control; and a step's `clear` keeps the note off what its line refers to (the cap rule's reaches step: the levels).
import { fakeDocument, install, type FakeEl } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { FIRST_MIX, FIRST_RULE } from "../src/game/lessons";
import { Glow } from "../src/ui/fresh";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const noMix: View = { ...fixtureStep("firstmix", 200).view, mixes: [], orders: [], active_mix_id: null };
const box = (left: number, top: number, w: number, h: number) => ({ left, top, width: w, height: h, right: left + w, bottom: top + h });
const text = (key: string, slots: Record<string, string> = {}): string => catalog.text.fill(key, slots);
let clock = 0;

function rig(account = NEW_FLAT) {
  fakeDocument.body.replaceChildren();
  const lessons = new Lessons({ catalog, glow: new Glow(), keeps: keepsOf(account) }, document.body, () => undefined, document, () => clock);
  Object.assign(lessons.root, { rect: box(0, 0, 200, 60) });
  const control = (cls: string, data: Record<string, string>, rect = box(150, 300, 80, 30), parent: FakeEl = fakeDocument.body): FakeEl => {
    const n = fakeDocument.createElement("button");
    n.className = cls;
    Object.assign(n.dataset, data);
    n.rect = rect;
    parent.append(n);
    return n;
  };
  const line = (): string => (lessons.root.hidden ? "" : lessons.root.querySelector(".lesson-line")?.textContent ?? "");
  const tick = (ms = 1): void => { clock += ms; lessons.tick(); };
  return { lessons, control, line, tick };
}

{  // a step's control above the window (the Rules tab on a phone, scrolled past): brought into view, once
  const r = rig();
  r.lessons.update(noMix);
  const offer = r.control("offer-both", { teach: "mix-offer", cards: "stand look" }, box(150, -120, 80, 30));
  fakeDocument.under = null;   // nothing of the page is at a point above the window
  r.tick();
  expect("the step starts on it", r.line(), text("ui.lesson.mix_offer"));
  expect("scrolled into view, smoothly", offer.scrolls, [{ block: "center", behavior: "smooth" }]);
  r.tick(); r.tick();
  expect("once: the player may scroll away again", offer.scrolls.length, 1);
  const editor = r.control("editor", {}, box(0, 0, 400, 800));
  const add = r.control("add-card", { card: "stand" }, box(150, 300, 80, 30), editor);
  fakeDocument.under = add;   // the page shows the control at its middle
  fakeDocument.over = [fakeDocument.querySelector(".lesson-note")!];   // the note, still where the last step had it, over it
  offer.click(); r.tick();
  expect("the next step", r.line(), text("ui.lesson.mix_add", { card: catalog.cardLabel("stand") }));
  expect("in sight under the note: no scroll", add.scrolls, []);
  fakeDocument.over = [];
  const look = r.control("add-card", { card: "look" }, box(150, 360, 80, 30), editor);
  fakeDocument.under = r.control("panel-top", {}, box(0, 300, 400, 100));   // the pinned hands strip over it
  r.control("stage", {}, box(0, 0, 400, 300));   // and the pinned scene above that
  r.control("stage", {}, box(400, 0, 400, 800));   // a part beside the control (a desktop's column) is not over it
  fakeDocument.over = [fakeDocument.querySelector(".lesson-note")!];   // the note over it too, which is no sight of it
  add.click(); r.tick();
  fakeDocument.over = [];
  expect("under a pinned strip: scrolled to the middle", look.scrolls, [{ block: "center", behavior: "smooth" }]);
  expect("of what the pinned parts over it leave", look.scrollMargins, ["400px"]);
  expect("and the margin is put back", look.style["scrollMarginTop"], "");
}

{  // a control in a scroll box that starts below the pinned parts (the editor on a phone): centred in that box, no margin
  const r = rig();
  r.lessons.update(noMix);
  const offer = r.control("offer-both", { teach: "mix-offer", cards: "stand look" });
  fakeDocument.under = offer;
  r.tick();
  r.control("stage", {}, box(0, 0, 400, 300));
  r.control("panel-top", {}, box(0, 300, 400, 100));
  const editor = r.control("editor", {}, box(0, 400, 400, 400));
  editor.style["overflowY"] = "auto";
  const add = r.control("add-card", { card: "stand" }, box(150, 380, 80, 30), editor);   // scrolled past the editor's top
  fakeDocument.under = null;
  offer.click(); r.tick();
  expect("clipped by the editor: centred in it", add.scrolls, [{ block: "center", behavior: "smooth" }]);
  expect("with no margin for the parts above the editor", add.scrollMargins, ["0px"]);
  fakeDocument.under = null;
}

{  // below the window, under reduced motion: at once
  const was = window.matchMedia;
  Object.assign(window, { matchMedia: () => ({ matches: true, addEventListener: () => undefined }) });
  const r = rig();
  r.lessons.update(noMix);
  const offer = r.control("offer-both", { teach: "mix-offer", cards: "stand look" }, box(150, 900, 80, 30));
  r.tick();
  expect("reduced motion: no smooth scroll", offer.scrolls, [{ block: "center", behavior: "instant" }]);
  Object.assign(window, { matchMedia: was });
}

{  // a tap on Save while the bar's read line is up ends the bar's step and Save's: the walk never asks for Save again
  const r = rig();
  r.lessons.update(noMix);
  const offer = r.control("offer-both", { teach: "mix-offer", cards: "stand look" });
  r.tick(); offer.click(); r.tick();
  const editor = r.control("editor", {}, box(0, 0, 400, 800));
  const head = r.control("editor-head", {}, box(0, 0, 400, 40), editor);
  const save = r.control("primary", {}, box(300, 5, 60, 30), head);
  const stand = r.control("add-card", { card: "stand" }, box(10, 100, 80, 30), editor);
  const look = r.control("add-card", { card: "look" }, box(100, 100, 80, 30), editor);
  r.tick(); stand.click(); r.tick(); look.click(); r.tick();
  r.control("share-bar", {}, box(10, 60, 380, 30), editor);
  r.tick();
  expect("the bar's read step", r.line(), text("ui.lesson.mix_bar"));
  save.click();
  r.control("hands-mix", {}, box(10, 400, 300, 30), r.control("hands", {}, box(0, 380, 400, 80)));
  r.tick();
  expect("Save's step is behind too", r.line(), text("ui.lesson.mix_runs"));
}

{  // the cap rule's reaches step: the note stays off the When and Until rows under it, so the level it names is in view
  const r = rig({ ...NEW_FLAT, rule_seen: true, lessons: [FIRST_MIX, FIRST_RULE] });
  r.lessons.update(fixtureStep("capfull", 100).view);
  const away = box(10, 700, 60, 30);   // the walk's earlier controls, out of the way of the placement read below
  r.control("line", { teach: "cap-line", store: "wood" }, away);
  r.tick(); r.tick(60_000); r.tick();
  const walk = (cls: string, data: Record<string, string>, parent: FakeEl): void => { const n = r.control(cls, data, away, parent); r.tick(); n.click(); r.tick(); };
  walk("tab", { tab: "rules" }, r.control("tabs", {}, away));
  walk("rules-new", {}, r.control("rules", {}, away));
  const cond = r.control("cond", {}, box(0, 0, 400, 800));
  walk("cond-more", {}, cond);
  walk("cond-store", { store: "wood" }, cond);
  walk("cond-fold", {}, cond);
  r.control("cond-test", { test: "reaches" }, box(150, 300, 80, 30), r.control("cond-tests", {}, box(100, 295, 250, 40), cond));
  const reaches = fakeDocument.querySelector('.cond-test[data-test="reaches"]')!;
  r.control("cond-steppers", {}, box(100, 340, 250, 40), cond);
  fakeDocument.under = reaches;   // the control is in sight, the levels are not (the hit test answers the control everywhere)
  r.tick();
  expect("the levels out of sight: the control goes to the middle so they come up with it", reaches.scrolls, [{ block: "center", behavior: "smooth" }]);
  fakeDocument.under = null;
  expect("the reaches step", r.line(), text("ui.lesson.cap_reaches", { store: catalog.storeLabel("wood") }));
  expect("above it, not over the levels below", [parseInt(r.lessons.root.style.left, 10), parseInt(r.lessons.root.style.top, 10)], [150, 232]);
}
