// The chronicle follows the story while it is open: a line that lands joins it, in the band's form, and the view stays
// where the player was: it opens at the top, newest first.
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
const opener = screen.root.querySelector<HTMLElement>("button[data-tab=\"book\"]");
const list = screen.root.querySelector<HTMLElement>("ol.chron-all");
const tasks = screen.root.querySelector<HTMLElement>("button[data-tab=\"cards\"]");
if (!opener || !list || !tasks) throw new Error("the rail holds Book, and the Book its chronicle");
const logged = (): string[] => [...list.querySelectorAll(".v-body .chron-text")].map((n) => n.textContent ?? "");

// A layout the fake DOM lacks: 100 plus 100 a line, in a 200 window.
Object.defineProperty(list, "scrollHeight", { get: () => 100 + 100 * list.querySelectorAll(".v-body .chron-text").length });
Object.defineProperty(list, "clientHeight", { value: 200 });

screen.show({ ...dayOneStep("landed", 200), lines: [line("line.1", 0)] }, true);
opener.click();
const before = logged();
expect("the open chronicle holds what landed before", before.includes(text("line.1")), true);
expect("it opens at the top", list.scrollTop, 0);

screen.show({ ...dayOneStep("landed", 300), lines: [line("line.2", 1)] }, true);
expect("a line that lands joins the open chronicle, last", logged().slice(-1), [text("line.2")]);
expect("the earlier lines stay", logged().length, before.length + 1);

list.scrollTop = 150;
screen.show({ ...dayOneStep("landed", 400), lines: [line("line.3", 2)] }, true);
expect("a line joins even when the player has scrolled", logged().slice(-1), [text("line.3")]);
expect("a player reading is not moved", list.scrollTop, 150);

// A closed chronicle is filled afresh on opening: the landing does not touch it.
tasks.click();
const closed = logged().length;
screen.show({ ...dayOneStep("landed", 500), lines: [line("line.1", 3)] }, true);
expect("a closed chronicle is left alone", logged().length, closed);
