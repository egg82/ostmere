// The lessons' marks on the hands strip's controls (ui/hands.ts), read as subjects by game/lessons.ts: the switch-mix
// lesson's on Mixes ▾ or Edit, and the stopped-mix lesson's on Edit. Each mark is data attributes, cleared and set anew
// from each view.
import type { Mix, View } from "../api/types";
import { SWITCH_MIX, guided } from "../game/lessons";
import { switchCue } from "../game/teach";
import type { PartContext } from "./part";

/** The strip's controls a mark can sit on. */
export interface Marked {
  name: HTMLElement;
  plan: HTMLElement;
  edit: HTMLElement;
}

/** The switch-mix lesson's mark, while it may start: on Mixes ▾ (the mix's name beside it, with a mix running), or on Edit when
 * only the running mix could take the card that makes the store. The subject is the build, the store and what makes it.
 * Returns whether the mark is on Edit, which then shows. */
export function markSwitch(ctx: PartContext, view: View, mixShown: boolean, { name, plan, edit }: Marked): boolean {
  const { catalog } = ctx;
  const cue = guided(SWITCH_MIX, view, ctx.keeps) ? switchCue(catalog, view) : null;
  for (const b of [name, plan, edit]) for (const k of ["switch", "build", "store", "mix", "card", "task"]) delete b.dataset[k];
  if (cue === null) return false;
  const at = cue.to === "edit" ? edit : mixShown ? name : plan;
  const subject = { switch: cue.to, build: catalog.cardLabel(cue.build), store: catalog.storeLabel(cue.store) };
  Object.assign(at.dataset, subject, cue.to === "mixes" ? { mix: cue.mix } : { card: cue.card, task: catalog.cardLabel(cue.card) });
  return cue.to === "edit";
}

/** A lesson's mark on Edit while the mix is greyed over a done card: the card's name is the lesson's subject, with the
 * card the content says takes its place (in play, not in the mix yet) when there is one. The editor's ✕ is off on a mix's
 * only entry, so without a replacement to add first, the mark waits for another card in the mix. */
export function markStopped(ctx: PartContext, mix: Mix, view: View, greyed: boolean, edit: HTMLElement): void {
  const { catalog } = ctx;
  const gone = greyed ? goneCard(mix, view) : null;
  const next = gone === null ? null : catalog.replacedBy(gone);
  const added = next !== null && view.cards.some((c) => c.card === next) && !mix.components.some((c) => c.kind === "card_share" && c.card === next) ? next : null;
  delete edit.dataset["teach"]; delete edit.dataset["gone"]; delete edit.dataset["with"]; delete edit.dataset["withLabel"];
  if (gone === null || (added === null && mix.components.length < 2)) return;
  Object.assign(edit.dataset, { teach: "mix-stopped", gone: catalog.cardLabel(gone) }, added === null ? {} : { with: added, withLabel: catalog.cardLabel(added) });
}

function goneCard(mix: Mix, view: View): string | null {
  const gone = mix.components.find((c) => c.kind === "card_share" && !view.cards.some((v) => v.card === c.card));
  return gone?.kind === "card_share" ? gone.card : null;
}
