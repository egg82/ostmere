// The phone frame (docs/design/redesign.md, "Phone frame"; ui/tabs.ts, ui/partseat.ts, ui/asks.ts): on a phone the tabs
// are the bottom bar, Tasks · Town · Rules · Book. Town holds the ledger and skills after the town's own rows; Book opens
// the chronicle's sheet, whose Done page holds the finished cards (shown once there are some), on every frame. On a
// landscape phone the ledger and skills stay off the tabs. The shown ask is one row whose way in names how many wait and
// opens the sheet of them all, even for one. On a phone only the mix's bar and its name ("Main ▾") stay pinned; its
// controls scroll under them. (The desktop's rail: railframe.test.ts.)
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { asksStep } from "../fixtures/asks";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Asks } from "../src/ui/asks";
import { PHONE } from "../src/ui/layout";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const media = (phone: boolean): void => {
  Object.assign(window, { matchMedia: (q: string) => ({ matches: phone && q === PHONE, addEventListener: () => {} }) });
};
const one = (sel: string): FakeEl => {
  const n = fakeDocument.body.querySelector(sel);
  if (!n) throw new Error(`no ${sel}`);
  return n;
};

function screenOn(phone: boolean, phase: "full" | "start"): Screen {
  media(phone);
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(fixtureStep(phase, 100));
  return screen;
}

{
  screenOn(true, "full");
  expect("phone: the ledger and skills are Town's", [one(".town-tab").querySelector(".ledger") !== null, one(".town-tab").querySelector(".skills") !== null], [true, true]);
  expect("phone: the finished cards are the Book's", one("dialog.chronicle").querySelector(".completed") !== null, true);
  expect("Tasks is on", one(".tabs [data-tab=\"cards\"]").getAttribute("aria-pressed"), "true");
  one(".tabs [data-tab=\"town\"]").click();
  expect("Town on: its panel shows and the cards do not", [one(".town-tab").hidden, one(".deck").hidden], [false, true]);
  expect("and its button is pressed", one(".tabs [data-tab=\"town\"]").getAttribute("aria-pressed"), "true");
  one(".tabs [data-tab=\"book\"]").click();
  const book = one("dialog.chronicle");
  expect("Book opens the chronicle's sheet", book.open, true);
  expect("on the chronicle", book.classList.contains("paged"), false);
  const pages = book.querySelectorAll(".book-page");
  expect("its pages: the chronicle, then Done", pages.map((p) => p.hidden), [false, false]);
  pages[1]?.click();
  expect("Done turns to the finished cards", [book.classList.contains("paged"), one("dialog.chronicle .completed").hidden], [true, false]);
  book.close();
  one(".tabs [data-tab=\"book\"]").click();
  expect("opened again, the Book starts on the chronicle", [book.classList.contains("paged"), one("dialog.chronicle .completed").hidden], [false, true]);
  expect("Town stays the tab on: Book is a sheet", one(".tabs [data-tab=\"town\"]").getAttribute("aria-pressed"), "true");
}
{
  const screen = screenOn(true, "full");
  const mix = fixtureStep("full", 100).view.running_mix_id ?? "";
  expect("phone: the mix's name beside the bar opens the Mixes list", one(".panel-top .hands-bar-row .hands-name").textContent, `${mix} ▾`);
  expect("phone: the mix's controls scroll under the pinned bar", [one(".hands-rows > .hands-meta") !== null, one(".panel-top").querySelector(".hands-meta")], [true, null]);
  media(false);
  screen.root.remove();
  screenOn(false, "full");
  expect("landscape: Mixes ▾ before the name, in the strip", [one(".hands-mix .hands-meta .hands-name").textContent?.endsWith("▾"), one(".hands-mix .hands-meta .hands-mix-name").textContent], [true, mix]);
}
{
  screenOn(true, "start");
  expect("nothing finished: no Done page", one("dialog.chronicle").querySelectorAll(".book-page").map((p) => p.hidden), [false, true]);
}
{
  screenOn(false, "full");
  expect("landscape: Town holds no ledger or skills", [one(".town-tab").querySelector(".ledger"), one(".town-tab").querySelector(".skills")], [null, null]);
  expect("landscape: the finished cards are the Book's too", one("dialog.chronicle").querySelector(".completed") !== null, true);
}
{
  media(true);
  const { ctx } = testContext();
  const asks = new Asks(ctx);
  document.body.replaceChildren(asks.root);
  for (const [view, n] of [[asksStep("asksmany", 100).view, "3"], [asksStep("asksone", 100).view, "1"]] as const) {
    asks.update(view);
    const opener = one(".asks-slot .asks-open");
    expect(`the row's way in names how many wait (${n})`, opener.textContent, n);
    opener.click();
    expect(`and opens the sheet of them all (${n})`, one("dialog.asks-sheet").open, true);
    one("dialog.asks-sheet").close();
  }
  asks.show();
  expect("the waiting link opens the sheet on a phone, even for one ask", one("dialog.asks-sheet").open, true);
}
