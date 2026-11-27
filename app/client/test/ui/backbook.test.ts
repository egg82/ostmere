// On a phone the Book is a sheet over the tab the player was on: back closes it and the tab stays; its own Close or the
// backdrop gives the entry back.
import { install } from "../fake-dom";
import { dayTwoStep } from "../../fixtures/daytwo";
import { fixtureContent } from "../../fixtures/content";
import { Catalog } from "../../src/game/page/catalog";
import { Keeps } from "../../src/game/account/keeps";
import { PHONE } from "../../src/ui/layout";
import { Screen } from "../../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { matchMedia: (q: string) => ({ matches: q === PHONE, addEventListener: () => undefined }) });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
document.body.replaceChildren(screen.root);
screen.show(dayTwoStep("ruled", 100));

const all = (s: string): HTMLElement[] => [...screen.root.querySelectorAll<HTMLElement>(s)];
const depth = (): number => (history.state as { ostmere?: number } | null)?.ostmere ?? 0;
const sheet = (): HTMLDialogElement => all("dialog.book-sheet")[0] as HTMLDialogElement;
const settle = (): Promise<void> => new Promise((done) => setTimeout(done, 0));
async function back(): Promise<void> {
  history.back();
  await settle();
}
const tab = (name: string): HTMLElement => all(`button[data-tab="${name}"]`)[0]!;

tab("book").click();
await settle();
expect("the Book is a sheet holding one entry, the tab stays", [sheet().open, depth(), screen.root.dataset["tab"]], [true, 1, "cards"]);
await back();
expect("back closes the Book", [sheet().open, depth(), screen.root.dataset["tab"]], [false, 0, "cards"]);

tab("book").click();
await settle();
all(".book .sheet-actions .quiet")[0]!.click();
await settle();
expect("its Close gives the entry back", [sheet().open, depth()], [false, 0]);
await back();
expect("back after Close reopens nothing", [sheet().open, depth()], [false, 0]);

tab("town").click();
tab("book").click();
await settle();
expect("the Book over the Town tab", [sheet().open, depth(), screen.root.dataset["tab"]], [true, 2, "town"]);
await back();
expect("back closes the Book, the tab stays", [sheet().open, depth(), screen.root.dataset["tab"]], [false, 1, "town"]);
await back();
expect("back leaves the tab for Tasks", [depth(), screen.root.dataset["tab"]], [0, "cards"]);
