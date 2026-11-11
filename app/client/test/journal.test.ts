// The Journal (CONTRACT.txt, "JOURNAL", acceptance 6 to 11), run against the rendered strip and sheet on the fixture
// journal (fixtures/journal.ts): the button and its dot, the numbers in the fight card's words, nothing sent until the
// sheet closes and then one presentation write, the seeded layout, and the journal's lesson.
import { ALL, catalog, expect, fire, KEPT, requests, rig, stepWith, text } from "./journalrig";
import { NOTE_B, NOTES_A } from "../fixtures/journal";
import { oddsOf } from "../src/game/fights";
import { layoutOf } from "../src/game/journal";
import { JOURNAL, JOURNAL_NUMBERS } from "../src/game/lessons";
import { Glow } from "../src/ui/fresh";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

{  // 6: the button is absent with no entry unlocked (the book is plain text) and present with one
  const none = rig({ notes: [] });
  expect("no entry: no button", none.button(), null);
  expect("no entry: the book is plain text", none.q(".chip.keep")?.textContent, text("feature.book"));
  const one = rig({ notes: ["note_a1"] });
  expect("an entry: the button, in the book's word", one.button()?.textContent, text("feature.book"));
  expect("an entry: the plain word is gone", one.q(".chip.keep"), null);
  expect("the button is its lesson's trigger", one.button()?.dataset["teach"], "journal");
}

{  // 7: a runner never fought draws the card's unknowns and no digit; one fought draws the served odds; one not in the view nothing
  const r = rig();
  r.button()!.click();
  const odds = oddsOf(4000, catalog.content.scales.bp);
  expect("fought: the served odds as the card words them", r.numbers().querySelector(".journal-odds")?.textContent,
    odds.kind === "pair" ? catalog.text.fill("ui.fight.odds", { lost: String(odds.lost), of: String(odds.of) }) : "pct");
  expect("fought: both strengths named", r.numbers().querySelector(".journal-vs")?.textContent,
    catalog.text.fill("ui.fight.vs", { side_name: catalog.sideLabel("hands"), power: "8", threat_name: catalog.threatLabel("wolves"), threat: "9" }));
  expect("fought: the tally", r.numbers().querySelector(".journal-tally")?.textContent, catalog.text.fill("ui.fight.tally", { fought: "4", lost: "1" }));
  expect("the runner's label", r.numbers().querySelector(".journal-runner")?.textContent, catalog.cardLabel("hunt"));
  r.next().click();
  const unknown = (sel: string): string => r.numbers().querySelector(sel)?.textContent ?? "(none)";
  expect("unfought: the odds are unknown", unknown(".journal-odds"), text("ui.fight.odds_unknown"));
  expect("unfought: the threat is unknown", unknown(".journal-vs").endsWith(text("ui.fight.threat_unknown")), true);
  expect("unfought: no digit in its odds", /\d/.test(unknown(".journal-odds")), false);
  expect("unfought: no tally", r.numbers().querySelector(".journal-tally"), null);
  expect("unfought: the threat's side holds no digit", /\d/.test(unknown(".journal-vs").split(",")[1] ?? ""), false);
  r.screen.show(stepWith(ALL, 900, false));   // view.fights holds no runner: nothing is drawn
  expect("a runner view.fights lacks draws nothing", [r.numbers().querySelectorAll(".journal-row").length, r.numbers().hidden], [0, true]);
}

{  // 8: opening and turning send nothing; closing sends one presentation write, journal_read gaining exactly the shown notes
  const r = rig({ lessons: [...KEPT, JOURNAL] });
  const before = structuredClone({ ...r.keeps.kept.account, ...r.keeps.kept.save });   // the page's own first-view writes (a ledger line shown) are before this
  r.sent.length = 0;
  requests.length = 0;
  r.button()!.click();
  r.next().click();
  r.prev().click();
  r.next().click();
  expect("nothing sent from open to the last page", [r.sent.length, r.asked, requests.length], [0, { decided: 0, dry: 0 }, 0]);
  r.close().click();
  expect("one write on close", r.sent.length, 1);
  expect("its body is the kept presentation but for journal_read", r.sent[0], { ...before, journal_read: ALL });
  expect("still nothing for the saves", [r.asked, requests.length], [{ decided: 0, dry: 0 }, 0]);
  const partial = rig();
  partial.sent.length = 0;
  partial.button()!.click();
  partial.close().click();
  expect("only the pages turned to are read", partial.sent[0]?.journal_read, NOTES_A);
  const esc = rig();
  esc.sent.length = 0;
  esc.button()!.click();
  fire(esc.sheet(), "close");   // Escape closes the dialog without its buttons
  expect("Escape is a close too", esc.sent.length, 1);
}

{  // 9: the dot shows while a note is unread; the sheet opens on the first page with one; a note unlocked while its page is open keeps the dot
  const r = rig();
  r.sent.length = 0;
  expect("unread: the dot", r.dotShows(), true);
  r.button()!.click();
  expect("it opens on the first entry with an unread note", r.words()[0], text("note_a1"));
  r.close().click();
  expect("page B's note is still unread: the dot stays", r.dotShows(), true);
  r.button()!.click();
  expect("it now opens on the page with the unread note", r.words(), [text(NOTE_B)]);
  expect("Prev is off on the first page only", [r.prev().disabled, r.next().disabled], [false, true]);
  r.close().click();
  expect("every unread page shown and closed: the dot is gone", r.dotShows(), false);
  expect("reopened, it is the page last shown", r.button() !== null && (r.button()!.click(), r.words()), [text(NOTE_B)]);
  r.close().click();
  const late = rig({ notes: ["note_a1"] });
  late.sent.length = 0;
  late.button()!.click();
  late.show(["note_a1", "note_a2"]);   // written while its page is open: it joins the page, no earlier note moves
  expect("a note written while the page is open joins it", late.words(), [text("note_a1"), text("note_a2")]);
  late.close().click();
  expect("it is not read by being drawn", late.sent[0]?.journal_read, ["note_a1"]);
  expect("its dot stays after the close", late.dotShows(), true);
}

{  // 10: the layout is the page's, not the save's, and a later note leaves earlier notes' draws alone
  const style = (r: ReturnType<typeof rig>): string[] => {
    r.button()!.click();
    const spread = r.sheet().querySelector<HTMLElement>(".journal-spread")!;
    const var_ = (n: HTMLElement, k: string): string => n.style.getPropertyValue(k);
    return [var_(spread, "--sk-w"), var_(spread, "--sk-x"), spread.dataset["above"] ?? "",
      ...[...r.sheet().querySelectorAll<HTMLElement>(".journal-note")].map((n) => `${var_(n, "--tilt")} ${var_(n, "--indent")}`)];
  };
  expect("the page is drawn with its seeded vars", style(rig()).slice(0, 2).every((v) => v !== "" && (v.endsWith("%") || Number.isFinite(Number(v)))), true);
  expect("two page loads draw one page", style(rig()), style(rig()));
  const ids = ["page_a", "page_b", "x_1", "x_2", "x_3", "x_4"];
  expect("pages differ over a list of ids", new Set(ids.map((i) => JSON.stringify(layoutOf(i, 2)))).size > 1, true);
  expect("a later note leaves every earlier note's draws unchanged", layoutOf("page_a", 3).notes.slice(0, 2), layoutOf("page_a", 2).notes);
  const l = layoutOf("page_a", 2);
  expect("the seeded ranges", [l.sketchWidth >= 86 && l.sketchWidth <= 100, l.notes.every((n) => n.tiltDeg >= -2 && n.tiltDeg <= 1), l.notes[1]!.indentRem >= 1], [true, true, true]);
}

{  // a sketch that fails to load leaves its room empty and is reported with its id
  const r = rig();
  requests.length = 0;
  r.button()!.click();
  const img = r.sheet().querySelector<HTMLElement>(".journal-sketch")!;
  fire(img, "error");
  expect("no stand-in: the image is only marked missing", img.classList.contains("missing"), true);
  expect("reported to the server with the sketch id", requests.filter((q) => q.startsWith("/api/client-errors") && q.includes("sketch_a")).length, 1);
}

{  // 11: the lesson starts on the button, walks its steps (the last two inside the sheet) and is kept; it never returns
  let clock = 0;
  const walk = (account: Flat) => {
    const r = rig({ lessons: account.lessons });
    const sent: Flat[] = [];
    const keeps = keepsOf(account, sent);
    const lessons = new Lessons({ catalog, glow: new Glow(), keeps }, document.body, () => undefined, document, () => clock);
    lessons.update(stepWith(NOTES_A, 500).view);   // the book as it first shows: one page written
    const line = (): string => (lessons.root.hidden ? "" : lessons.root.querySelector(".lesson-line")?.textContent ?? "");
    const tick = (t: number): void => {
      for (const sel of ['[data-teach="journal"]', ".journal-sheet [data-teach=\"journal-note\"]", ".journal-sheet .journal-numbers"])
        for (const n of document.querySelectorAll(sel)) Object.assign(n, { rect: { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 } });
      clock = t;
      lessons.tick();
    };
    const got = (): void => lessons.root.querySelector<HTMLElement>(".lesson-next")?.click();   // a read step ends on a tap of the note
    return { r, sent, lessons, line, tick, got };
  };
  const w = walk({ ...NEW_FLAT, lessons: KEPT });
  w.tick(0);
  expect("starts on the button's first showing", w.line(), text("ui.lesson.journal_open"));
  w.r.button()!.click();
  w.tick(1);
  expect("then the open page's last note", w.line(), text("ui.lesson.journal_notes"));
  expect("the note is drawn inside the sheet's own layer", w.lessons.root.closest("dialog")?.className, "sheet journal-sheet");
  w.got();
  w.tick(2);
  expect("then the page's numbers, a lesson of their own", w.line(), text("ui.lesson.journal_numbers"));
  w.got();
  w.tick(3);
  expect("done: both kept in the save", w.sent.at(-1)?.lessons, [...KEPT, JOURNAL, JOURNAL_NUMBERS]);
  const again = walk({ ...NEW_FLAT, lessons: [...KEPT, JOURNAL, JOURNAL_NUMBERS] });
  again.tick(0);
  expect("never again", again.line(), "");
}
