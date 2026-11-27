## The Town view

The town's people get a room of their own (`ui/town/townview.ts`): the Town tab on every frame, the desktop's taking the
middle and the right beside the rail. Its title and the note of a stopped mix share the first row; under them a row per
person who runs their own split, the marked, then a row per group with a member (`ui/town/townstrip.ts`). A marked person's row:
their face (the ask's, so a person looks the same wherever they appear), who they are and what they work now, their own
Change, their time split into the cards that hold a share with the idle rest, the split that runs now while one of their
cards is stopped, and the bar of the card they work. A group's row has the same form: the group's label, a stack of its first
two members' faces with the head count ("3 people"), the group's one split bar (each share a part of each member's time) and
the card it works. A group of one draws as that person (their face, their name, no count, their one-off with "then {split}"
when they are on one): the row is keyed by the group, so the second member to join changes the name to the group's label
and adds the count, and the split and its bar do not move. A person whose mark is off has no row of their own, and a marked
person who names the group is not counted in it. Then a row per lane run by rules whose
person has not joined (`ui/town/lanerows.ts`, below), in the same row form (`ui/town/personrow.ts`) with its own Change where a
split would be. On a desktop what each works sits over its card's bar, on the right. On a phone the ledger and skills follow. Change opens the person's page in
the view's place: a person's page, or a group's. These rows are their one home: the main screen and the rail never list anyone's jobs, and the Rules
tab keeps the rules of their tasks, not their people. A row arriving while another tab is open dots Town (the new-card dot), never
on the first view.

At a town's size the view scrolls in its own column with the panel's fade at its foot; the rail keeps its one Town
entry however big the town gets. Folding the light tier into groups by role, with search and pin, waits for a town that
size (`decisions.md`, "The town"). Rejected: a Town view that copies the town strip beside the main screen's (two homes
for one person's jobs); placeholder pages for buildings and outposts before either exists (`decisions.md`, "The screen
arrives when it means something").

**A group's page** is the person page for a pooled lane (`ui/town/personpage.ts`, `ui/town/personmix.ts`): the group's split as the one
share bar, with "each of {crew}" under it (the crew is the group's free members now, `Card.crew`; "everyone is busy" at none),
and the group's tasks as the Tasks card face, a tap joining one to the split or taking it out, each face's rate the total over
the crew. Under the bar the members (`ui/town/groupmembers.ts`): a head count that opens one line each, open for a group of up to
three and a tap away for a bigger one. A line is the member's face, their name and what they do now: the group's split, or a
one-off of their own with its time left and "then {split}"; their own capped one-offs are tapped from that line. There is no
per-member split and no page for an unmarked person. A group of one is the same page titled with the member's name. No rule
names a pooled lane, so the page has no rules section. The head leaves room for a person tied to the group, to be named from
an authored field when content has one; nothing is inferred.

## The Book

One place for what the game has written down (`ui/book/book.ts`; `docs/design/redesign.md`, "Book"): the **Chronicle**,
the **Journal** and **Done** (the finished cards), each a page, and later the **Map**. Its head is the title, `Book`, and
beside it the row of pages, over a hairline; the row is the one way between them, and it shows once a second page is
offered: the Journal from its first entry, Done once a card is finished, the Map with its first place. Book always opens
on the chronicle. On a desktop or a landscape phone it is a view like Town, taking the middle and the right while
the rail marks Book as the tab on, and the journal's spread sits centred in it with Prev and Next under it; another tab
leaves it. On a phone it is a sheet from the bottom, with Close, full height while the Journal is open. Turning from the
Journal or closing the Book is when the notes read are kept (The journal). The Journal's page button and the Book's tab
carry the dot while a note is unread.

Rejected: a Book that stays a sheet on a desktop while Tasks, Town and Rules change the view in place (the owner's
report: Book has to behave like its neighbours); the journal's own button on the art beside it (two doors to one
Book's contents); a dimmed Map in the row before a map exists (a page the player can't open reads as broken or as a
promise; "The screen arrives when it means something"); a "back 2m ago" beside the title (the chapter already says how
long the player was away).

