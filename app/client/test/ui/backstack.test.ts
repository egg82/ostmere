// Back steps out of what the player opened, one layer at a time, and a rule's editor returns to whatever opened it:
// the pot's (a person's) page, or the Rules tab. Back is the history's: every layer holds one entry (ui/back.ts).
import { install } from "../fake-dom";
import { dayTwoStep } from "../../fixtures/daytwo";
import { fixtureContent } from "../../fixtures/content";
import { Catalog } from "../../src/game/page/catalog";
import { Keeps } from "../../src/game/account/keeps";
import { openSheet } from "../../src/ui/back";
import { Screen } from "../../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
document.body.replaceChildren(screen.root);
screen.show(dayTwoStep("ruled", 100));

const all = (s: string): HTMLElement[] => [...screen.root.querySelectorAll<HTMLElement>(s)];
const one = (s: string): HTMLElement => {
  const n = all(s)[0];
  if (!n) throw new Error(`nothing matches ${s}`);
  return n;
};
const tab = (name: string): HTMLElement => one(`button[data-tab="${name}"]`);
const pageOpen = (): boolean => !one(".person-page").hidden;
/** The Rules tab shows its list (no editor drawn). */
const editorOpen = (): boolean => all(".cond").length > 0 && all(".cond").some((n) => n.isConnected);
const depth = (): number => (history.state as { ostmere?: number } | null)?.ostmere ?? 0;
const settle = (): Promise<void> => new Promise((done) => setTimeout(done, 0));
/** The player's back: the history steps back, and the page hears it a tick later. */
async function back(): Promise<void> {
  history.back();
  await settle();
}
/** The pot's page open, and the editor for its chop rule open on top of it. */
async function editorFromPage(): Promise<void> {
  one(".lane-change").click();
  await settle();
  all(".person-rules .rule-cond").find((b) => (b.textContent ?? "").startsWith("Chop"))?.click();
  await settle();
}
/** Another task chosen, then Save. */
const save = (): void => {
  all(".pick").find((b) => b.dataset["card"] === "haul")?.querySelector<HTMLElement>(".card-tap")?.click();
  one(".cond-actions .primary").click();
};
const cancel = (): void => one(".cond .editor-close").click();

expect("nothing open: no history entry, back would leave", depth(), 0);

{  // the person's page: back closes it, and only it
  one(".lane-change").click();
  expect("the page opens", [pageOpen(), depth()], [true, 1]);
  await back();
  expect("back closes the page", [pageOpen(), depth()], [false, 0]);
}

{  // the rule editor opened from the page returns to the page: after Save, after cancel, after back
  await editorFromPage();
  expect("the editor is open over the Rules tab", [editorOpen(), pageOpen(), screen.root.dataset["tab"]], [true, false, "rules"]);
  save();
  await settle();
  expect("Save returns to the page", [pageOpen(), editorOpen(), screen.root.dataset["tab"]], [true, false, "cards"]);
  expect("the page holds one entry", depth(), 1);

  await editorFromPage();
  cancel();
  await settle();
  expect("cancel returns to the page", [pageOpen(), editorOpen()], [true, false]);

  await editorFromPage();
  await back();
  expect("back from the editor returns to the page", [pageOpen(), editorOpen(), depth()], [true, false, 1]);
  await back();
  expect("then back closes the page", [pageOpen(), depth(), screen.root.dataset["tab"]], [false, 0, "cards"]);
}

{  // opened from the Rules tab, the editor returns to the Rules list
  tab("rules").click();
  await settle();
  expect("the Rules tab is a layer", [screen.root.dataset["tab"], depth()], ["rules", 1]);
  one(".rule-cond").click();
  await settle();
  expect("the editor is open", [editorOpen(), depth()], [true, 2]);
  cancel();
  await settle();
  expect("cancel returns to the Rules list", [editorOpen(), pageOpen(), screen.root.dataset["tab"], depth()], [false, false, "rules", 1]);
  one(".rule-cond").click();
  await settle();
  await back();
  expect("back closes the editor to the Rules list", [editorOpen(), screen.root.dataset["tab"], depth()], [false, "rules", 1]);
  await back();
  expect("back from the Rules tab lands on Tasks", [screen.root.dataset["tab"], depth()], ["cards", 0]);
}

{  // a sheet: back closes it, whatever it was opened over
  tab("town").click();
  const sheet = document.createElement("dialog");
  openSheet(sheet);
  expect("a sheet is a layer over the tab", [sheet.open, depth()], [true, 2]);
  await back();
  expect("back closes the sheet, the tab stays", [sheet.open, screen.root.dataset["tab"], depth()], [false, "town", 1]);
  openSheet(sheet);
  sheet.close();
  await settle();
  expect("closing a sheet by hand gives its entry back", [sheet.open, depth()], [false, 1]);
  await back();
  expect("back from Camp lands on Tasks", [screen.root.dataset["tab"], depth()], ["cards", 0]);
}
