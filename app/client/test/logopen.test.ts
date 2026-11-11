// The Log sheet follows the story while it is open: a line that lands joins it, in the band's form, and the view stays
// at the bottom if the player was there, or where they scrolled to read.
import { install } from "./fake-dom";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import type { LogLine } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const text = (key: string): string => catalog.text.get(key);
const line = (key: string, seq: number): LogLine => ({ at: 100 + seq, seq, key, card: null });

const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
document.body.replaceChildren(screen.root);
screen.show(dayOneStep("returned", 100));
const opener = screen.root.querySelector<HTMLElement>("button.log-open");
const list = screen.root.querySelector<HTMLElement>("ol.log-all");
const sheet = screen.root.querySelector<HTMLDialogElement>("dialog.log-sheet");
if (!opener || !list || !sheet) throw new Error("the band holds the Log button and its sheet");
const logged = (): string[] => [...list.querySelectorAll(".v-body > p")].map((n) => n.textContent ?? "");

// A layout the fake DOM lacks: 100 plus 100 a line, in a 200 window.
Object.defineProperty(list, "scrollHeight", { get: () => 100 + 100 * list.querySelectorAll(".v-body > p").length });
Object.defineProperty(list, "clientHeight", { value: 200 });

screen.show({ ...dayOneStep("landed", 200), lines: [line("line.1", 0)] }, true);
opener.click();
const before = logged();
expect("the open Log holds what landed before", before.includes(text("line.1")), true);

screen.show({ ...dayOneStep("landed", 300), lines: [line("line.2", 1)] }, true);
expect("a line that lands joins the open Log, last", logged().slice(-1), [text("line.2")]);
expect("the earlier lines stay", logged().length, before.length + 1);
expect("the player at the bottom follows", list.scrollTop, list.scrollHeight);

list.scrollTop = 0;
screen.show({ ...dayOneStep("landed", 400), lines: [line("line.3", 2)] }, true);
expect("a line joins even when the player has scrolled up", logged().slice(-1), [text("line.3")]);
expect("a player reading above is not moved", list.scrollTop, 0);

// A closed Log is filled afresh on opening: the landing does not touch it.
sheet.close();
const closed = logged().length;
screen.show({ ...dayOneStep("landed", 500), lines: [line("line.1", 3)] }, true);
expect("a closed Log is left alone", logged().length, closed);
