// The "Since you left" chapter at the top of the chronicle (docs/design/opening-screen.md, "The chronicle"): the newest
// return's stretch, never folded, under an ember spine, titled with how long the player was away. Its lines are drawn as
// any stretch's; under Story its figures follow as rows (game/chronwords.ts, chapterRows), the levels and rules rows'
// labels opening their filters, the waiting row's count showing what waits, then the people section when anyone came
// or went (the lines that tell it, taken out of the lines above), then the counts of the filters no row opens. With figures kept and nothing at all to show, one line says so; with none kept (a return from before they
// were), it says nothing, since nothing is known.
import type { Chapter, Visit } from "../api/types";
import type { Catalog } from "../game/catalog";
import { held, tally, type Entry, type Filter } from "../game/chronicle";
import { awaySpan, chapterRows, filterCount, SECTION_LABEL, type ChapterSection } from "../game/chronwords";
import { UI } from "../game/text";
import { el } from "./dom";

export interface ChapterView {
  visit: Visit;
  lines: Entry[];
  /** The return's kept figures; null when this return has none. */
  figures: Chapter | null;
  /** How many asks wait now. */
  waiting: number;
}

export interface ChapterActions {
  line(entry: Entry): HTMLElement;
  pick(filter: Filter): void;
  showWaiting(): void;
}

const OPENS: Partial<Record<ChapterSection, Filter>> = { levels: "levels", rules: "rules" };

export function chapterNode(catalog: Catalog, c: ChapterView, filter: Filter | null, act: ChapterActions): HTMLElement {
  const { text } = catalog;
  const item = el("li", "chron-stretch chapter");
  const head = el("div", "chapter-head");
  head.append(el("h3", "chapter-title", text.get(UI.chapter)), el("span", "v-ago", awaySpan(text, c.visit.back - c.visit.left)));
  const people = filter === "story" ? c.lines.filter((l) => l.person) : [];
  item.append(head, ...held(c.lines, filter).filter((l) => !people.includes(l)).map((l) => act.line(l)));
  if (c.figures && c.lines.length === 0 && chapterRows(catalog, c.figures, 0).length === 0) item.append(el("p", "chapter-still", text.get(UI.chapterStill)));
  if (filter !== "story") return item;
  const rows = chapterRows(catalog, c.figures, c.waiting);
  const counted = tally(c.lines);
  if (rows.length > 0) item.append(rowsNode(catalog, rows, counted.map(([f]) => f), act));
  if (people.length > 0) item.append(peopleNode(catalog, people, act));
  const opened = new Set(rows.flatMap(([s]) => OPENS[s] ?? []));
  const rest = counted.filter(([f]) => f !== "story" && !opened.has(f));
  if (rest.length > 0) item.append(countsNode(catalog, rest, act));
  return item;
}

function rowsNode(catalog: Catalog, rows: Array<[ChapterSection, string[]]>, filled: Filter[], act: ChapterActions): HTMLElement {
  const list = el("dl", "chapter-rows");
  for (const [section, said] of rows) {
    const opens = OPENS[section];
    const label = el("dt");
    if (opens && filled.includes(opens)) label.append(button("chapter-link", catalog.text.get(SECTION_LABEL[section]), () => act.pick(opens), opens));
    else label.textContent = catalog.text.get(SECTION_LABEL[section]);
    const value = el("dd");
    value.dataset["section"] = section;
    said.forEach((s, i) => {
      if (i > 0 && section !== "rules") value.append(" ", el("span", "chapter-sep", "·"), " ");
      value.append(section === "waiting" ? button("chapter-link", s, () => act.showWaiting()) : el("span", "chapter-item", s));
    });
    list.append(label, value);
  }
  return list;
}

/** Who came and went while the player was away: the lines that tell a person joining or leaving, and each day's
 * mention, as story lines under a label of their own. */
function peopleNode(catalog: Catalog, lines: Entry[], act: ChapterActions): HTMLElement {
  const box = el("section", "chapter-people");
  box.append(el("h4", "chapter-sec", catalog.text.get(UI.chapterPeople)), ...lines.map((l) => act.line(l)));
  return box;
}

function countsNode(catalog: Catalog, counts: Array<[Filter, number]>, act: ChapterActions): HTMLElement {
  const foot = el("div", "chron-foot");
  foot.append(...counts.map(([f, n]) => button("chron-count", filterCount(catalog.text, f, n), () => act.pick(f), f)));
  return foot;
}

function button(cls: string, label: string, onClick: () => void, filter?: Filter): HTMLButtonElement {
  const b = el("button", cls, label);
  b.type = "button";
  if (filter) b.dataset["filter"] = filter;
  b.addEventListener("click", onClick);
  return b;
}
