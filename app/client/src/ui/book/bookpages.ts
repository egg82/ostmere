// The Book's pages that Screen adds after the chronicle and the journal (ui/book.ts): Done, then the Map. Each is a Part
// that hides its own button while it has nothing.
import type { Book } from "./book";
import { Completed } from "./completed";
import { MapPage } from "./mappage";
import type { Part, PartContext } from "../part";

export function bookPages(ctx: PartContext, book: Book): Part[] {
  return [new Completed(ctx, book), new MapPage(ctx, book)];
}
