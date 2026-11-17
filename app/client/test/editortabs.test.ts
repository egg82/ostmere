// An editor never shows beside a tab it does not belong to: it takes the card area while open, and the tab row stays
// live (a phone's bottom bar), so a tap on another tab leaves it closed (a person's page from Camp, the mix's from Tasks).
import { FakeEl, fakeDocument, install } from "./fake-dom";
import { townStep } from "../fixtures/town";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { fixtureContent } from "../fixtures/content";
import { PHONE } from "../src/ui/layout";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
let phone = false;
Object.assign(window, {
  matchMedia: (query: string) => ({ matches: query === PHONE ? phone : false, addEventListener: () => undefined }),
  innerWidth: 400, innerHeight: 800,
});
FakeEl.prototype.getBoundingClientRect = () => ({ left: 10, top: 10, width: 100, height: 20, right: 110, bottom: 30 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}
const drawn = (n: FakeEl, top: FakeEl): boolean => {
  for (let x: FakeEl | null = n; x; x = x.parent) {
    if (x.hidden) return false;
    if (x === top) return true;
  }
  return true;
};
const tap = (top: FakeEl, sel: string): void => {
  const b = top.querySelector(sel);
  if (!b) throw new Error(`no ${sel}`);
  b.click();
};
const mixEdit = (top: FakeEl): FakeEl => {
  const b = top.querySelectorAll(".hands-edit").find((x) => !x.classList.contains("person-change"));
  if (!b) throw new Error("no Edit button");
  return b;
};
/** Which editors the page draws: "person" (a person's page) and "mix". */
function showing(top: FakeEl): string[] {
  const out: string[] = [];
  for (const e of top.querySelectorAll(".editor")) if (drawn(e, top)) out.push(e.classList.contains("person-page") ? "person" : "mix");
  return out;
}

for (const onPhone of [false, true]) {
  const where = onPhone ? "phone" : "desktop";
  phone = onPhone;
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  const top = mounted(screen.root);
  screen.show(townStep("town"));

  tap(top, '[data-tab="town"]');
  tap(top, ".person-change");
  expect(`${where}: Change opens the person's page`, showing(top), ["person"]);
  tap(top, '[data-tab="cards"]');
  expect(`${where}: the page is gone on Tasks`, showing(top), []);
  tap(top, '[data-tab="town"]');
  expect(`${where}: and does not return with Camp`, showing(top), []);

  mixEdit(top).click();
  expect(`${where}: Edit opens the mix editor`, showing(top), ["mix"]);
  tap(top, '[data-tab="town"]');
  expect(`${where}: the mix editor is gone on Camp`, showing(top), []);
}
