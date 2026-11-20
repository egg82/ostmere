// A group's members on its page (personpage.ts): a head count that opens the list, a line each: face, name, and what they
// are doing now: the group's split, or a one-off of their own with its time left and "then {split}", as a person's page draws a
// tap. A member's own capped one-offs are tapped from their line (a group has no per-member split and no page of its own).
// A group of a few opens its list; a bigger one is a count with the names a tap away.
import type { View } from "../api/types";
import { laneOneOff, laneTap } from "../game/holder";
import { members } from "../game/town";
import { UI } from "../game/text";
import { face } from "./asknode";
import { el, setText, tapFeedback } from "./dom";
import type { PartContext } from "./part";
import { splitWords } from "./townsplit";

/** A group this small has its members' lines open; a bigger one shows them a tap away. */
const OPEN_UP_TO = 3;

interface Line { node: HTMLElement; doing: HTMLElement; held: { card: string; endsAt: number | null } | null }

export class GroupMembers {
  readonly root = el("section", "group-members");
  private readonly toggle = el("button", "quiet group-count");
  private readonly list = el("div", "group-lines");
  private lines = new Map<string, Line>();
  private opened: boolean | null = null;

  constructor(private readonly ctx: PartContext) {
    this.toggle.type = "button";
    this.toggle.addEventListener("click", () => {
      tapFeedback();
      this.opened = this.list.hidden;
      this.list.hidden = !this.opened;
      this.toggle.setAttribute("aria-expanded", String(this.opened));
    });
    this.root.append(this.toggle, this.list);
  }

  /** Draws `group`'s members as of `view`. */
  update(view: View, group: string): void {
    const { catalog } = this.ctx;
    const all = members(catalog, view, group);
    setText(this.toggle, catalog.text.fill(UI.townCount, { n: String(all.length) }));
    const open = this.opened ?? all.length <= OPEN_UP_TO;
    this.list.hidden = !open;
    this.toggle.setAttribute("aria-expanded", String(open));
    this.lines = new Map(all.map((lane) => [lane, this.line(view, group, lane)]));
    this.list.replaceChildren(...[...this.lines.values()].map((l) => l.node));
  }

  /** A holding one-off's time left moves on with the clock. */
  tick(t: number): void {
    for (const line of this.lines.values()) if (line.held) setText(line.doing, this.oneOff(line.held.card, line.held.endsAt, t));
  }

  private oneOff(card: string, endsAt: number | null, t: number): string {
    const { catalog } = this.ctx;
    return endsAt === null ? catalog.cardLabel(card) : `${catalog.cardLabel(card)} ${catalog.format.duration(endsAt - t)}`;
  }

  private line(view: View, group: string, lane: string): Line {
    const { catalog, actions } = this.ctx;
    const name = catalog.laneLabel(lane, view);
    const node = el("div", "group-line");
    node.dataset.lane = lane;
    const tap = laneOneOff(view, lane);
    const split = splitWords(this.ctx, view, group, lane);
    const doing = el("span", "group-doing", tap ? this.oneOff(tap.card, tap.endsAt, view.at) : split || catalog.text.get(UI.laneIdle));
    const who = el("span", "group-who");
    who.append(el("span", "town-name", name), doing);
    node.append(face(this.ctx, lane, name), who);
    if (tap) node.append(el("span", "hands-then group-then", catalog.text.fill(UI.handsThen, { mix: split })));
    const held = laneTap(view, lane);
    const tasks = el("span", "group-tasks");
    for (const c of view.cards.filter((x) => x.cap !== null && catalog.laneOf(x.card) === lane)) {
      const b = el("button", "quiet group-task", catalog.cardLabel(c.card));
      b.type = "button";
      b.dataset.card = c.card;
      b.disabled = held !== null;
      b.addEventListener("click", () => { tapFeedback(); actions.decide({ kind: "tap_card", card: c.card }); });
      tasks.append(b);
    }
    if (tasks.children.length > 0) node.append(tasks);
    return { node, doing, held: tap && { card: tap.card, endsAt: tap.endsAt } };
  }
}
