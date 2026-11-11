// Moving a pick on the prestige sheet (docs/design/prestige-phases.md, "Moving a pick"): each node the skill's picks hold
// has a Move button; choosing one says what it costs and offers the menu's other nodes as places for the rank to go (closing the sheet drops the move). Ranks a
// move already parked are listed with the push they come back at. Every number is the view's.
import type { SkillPrestige } from "../api/types";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

export interface Moving {
  /** The picked node whose rank is being moved, or null while none is. */
  readonly node: string | null;
  start(node: string | null): void;
}

/** The sheet's lines about picks already made: parked ranks, then each picked node with Move, and while one is being
 * moved the cost and the menu's nodes to move it to. Empty while a pick is owed (a move waits for it to be filled). */
export function moveLines(ctx: PartContext, skill: string, p: SkillPrestige, moving: Moving): HTMLElement[] {
  if (p.pick_owed) return [];
  const { catalog } = ctx;
  const label = (node: string): string => catalog.label(catalog.nodes.get(node)?.label_key);
  const out = p.parked.map((k) => {
    const n = k.due - p.phase;
    return el("p", "prestige-parked", n === 1 ? catalog.text.fill(UI.prestigeParkedOne, { node: label(k.node) })
      : catalog.text.fill(UI.prestigeParked, { node: label(k.node), n: catalog.format.count(n) }));
  });
  if (moving.node !== null) return [...out, ...destinations(ctx, skill, p, moving, label)];
  return [...out, ...p.picked.map((node) => pickedRow(ctx, p, node, label(node), moving))];
}

function pickedRow(ctx: PartContext, p: SkillPrestige, node: string, name: string, moving: Moving): HTMLElement {
  const row = el("div", "prestige-node");
  const head = el("div", "prestige-head");
  head.append(el("span", "prestige-name", name));
  const move = el("button", "quiet", ctx.catalog.text.get(UI.prestigeMove));
  move.type = "button";
  move.disabled = p.menu_nodes.length === 0;
  move.dataset["node"] = node;
  move.addEventListener("click", () => { tapFeedback(); moving.start(node); });
  row.append(head, move);
  return row;
}

function destinations(ctx: PartContext, skill: string, p: SkillPrestige, moving: Moving, label: (node: string) => string): HTMLElement[] {
  const { catalog } = ctx;
  const from = moving.node ?? "";
  const ask = el("p", "prestige-intro", catalog.text.fill(UI.prestigeMoveTo, { node: label(from) }));
  const rows = p.menu_nodes.filter((n) => n.node !== from).map((n) => {
    const row = el("div", "prestige-node");
    const head = el("div", "prestige-head");
    head.append(el("span", "prestige-name", label(n.node)));
    const here = el("button", "primary", catalog.text.get(UI.prestigeMoveHere));
    here.type = "button";
    here.dataset["node"] = n.node;
    here.addEventListener("click", () => {
      tapFeedback();
      moving.start(null);
      ctx.actions.decide({ kind: "move_pick", skill, node: from, to: n.node });
    });
    row.append(head, here);
    return row;
  });
  return [ask, ...rows];
}
