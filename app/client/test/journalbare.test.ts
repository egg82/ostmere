// A page with no sketch is laid out as text alone (CONTRACT.txt, "JOURNAL", THE CLIENT MAY): no empty room for a
// drawing, nothing loaded and nothing reported.
import { expect, fire, requests, rig, text } from "./journalrig";
import { NOTES_A, NOTES_D } from "../fixtures/journal";

const sketches = (root: HTMLElement): HTMLElement[] => [...root.querySelectorAll<HTMLElement>("img")].filter((i) => i.className.includes("journal-sketch"));

{  // the days page has none: no image at all, no request, the notes alone
  const r = rig({ notes: NOTES_D });
  requests.length = 0;
  r.open();
  expect("its notes are drawn", r.words(), NOTES_D.map(text));
  expect("no sketch element", sketches(r.sheet()).length, 0);
  expect("no image anywhere on the page", r.sheet().querySelectorAll("img").length, 0);
  expect("no room kept for a drawing", r.sheet().querySelector<HTMLElement>(".journal-left")?.hidden, true);
  expect("laid out as text alone", r.sheet().querySelector<HTMLElement>(".journal-spread")?.dataset["bare"], "true");
  expect("nothing reported", requests.filter((q) => q.startsWith("/api/client-errors")).length, 0);
  expect("no numbers on it", r.numbers().hidden, true);
}

{  // turning to a page with a sketch brings the room back, and back again leaves it
  const r = rig({ notes: [...NOTES_D, ...NOTES_A], read: [...NOTES_D, ...NOTES_A] });
  r.open();
  expect("days: bare", r.sheet().querySelector<HTMLElement>(".journal-spread")?.dataset["bare"], "true");
  r.next().click();
  const spread = r.sheet().querySelector<HTMLElement>(".journal-spread")!;
  expect("creatures: a sketch, loaded from its id", [spread.dataset["bare"], sketches(r.sheet()).map((i) => (i as HTMLImageElement).src)], ["false", ["/assets/journal/sketch_a.png"]]);
  expect("its room is kept", r.sheet().querySelector<HTMLElement>(".journal-left")?.hidden, false);
  r.prev().click();
  expect("days again: bare", [spread.dataset["bare"], sketches(r.sheet()).length], ["true", 0]);
  fire(r.sheet(), "close");
}
