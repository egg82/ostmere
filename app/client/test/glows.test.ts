// The strip's Edit glow when the running mix greys (ui/fresh.ts, GlowWhile; hands.ts): it appears on greying, waits
// while another control holds the one glow or the reveal holds the button back, and clears when the editor is opened
// (from Edit or elsewhere) or the mix is no longer grey; a mix that stays grey after that does not glow again.
import { fixtureStep } from "../fixtures/steps";
import { Glow, GlowWhile } from "../src/ui/fresh";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

class Fake {
  className = ""; isConnected = true; parent: Fake | null = null;
  private on: (() => void)[] = [];
  get classList() {
    const names = () => new Set(this.className.split(" ").filter(Boolean));
    return {
      add: (c: string) => { this.className = [...names().add(c)].join(" "); },
      remove: (c: string) => { const s = names(); s.delete(c); this.className = [...s].join(" "); },
      contains: (c: string) => names().has(c),
    };
  }
  closest(sel: string): Fake | null {
    const c = sel.replace(".", "");
    for (let n: Fake | null = this; n; n = n.parent) if (n.classList.contains(c)) return n;
    return null;
  }
  addEventListener(_: string, f: () => void) { this.on.push(f); }
  click() { const fs = this.on; this.on = []; for (const f of fs) f(); }
}

const greyedOf = (phase: "mid" | "greyed") => {
  const v = fixtureStep(phase, 100).view;
  return v.active_mix_id !== null && v.greyed_mix_ids.includes(v.active_mix_id);
};
expect("the fixture's greyed phase greys the running mix", [greyedOf("mid"), greyedOf("greyed")], [false, true]);

const rig = () => {
  const glow = new Glow();
  const edit = new Fake();
  edit.parent = new Fake();
  const g = new GlowWhile(glow, edit as unknown as HTMLElement);   // a fake DOM double -- it has only what this test reads
  return { glow, edit, g, lit: () => edit.classList.contains("glow") };
};

// Appears on greying; clears on opening the editor; staying grey does not bring it back.
{
  const r = rig();
  r.g.update(greyedOf("mid"));
  expect("no glow while the mix runs", r.lit(), false);
  r.g.update(greyedOf("greyed"));
  expect("glows on greying", r.lit(), true);
  r.g.used();
  expect("cleared when the editor opens", r.lit(), false);
  r.g.update(true);
  r.g.tick();
  expect("still grey: not again", r.lit(), false);
  r.g.update(false);
  r.g.update(true);
  expect("a new greying glows again", r.lit(), true);
}

// Edit's own click clears it (the Glow's listener), and the mix leaving grey clears it.
{
  const r = rig();
  r.g.update(true);
  r.edit.click();
  expect("Edit tapped", r.lit(), false);
  const r2 = rig();
  r2.g.update(true);
  r2.g.update(false);
  expect("no longer grey", r2.lit(), false);
}

// Waits while another control holds the glow, and while the reveal holds the button.
{
  const r = rig();
  const other = new Fake();
  r.glow.offer(other as unknown as HTMLElement);   // a fake DOM double -- it has only what this test reads
  r.g.update(true);
  expect("not while another holds it", r.lit(), false);
  other.click();
  r.g.tick();
  expect("once it is free", r.lit(), true);
  const r2 = rig();
  r2.edit.parent!.classList.add("held");
  r2.g.update(true);
  r2.g.tick();
  expect("not while held", r2.lit(), false);
  r2.edit.parent!.classList.remove("held");
  r2.g.tick();
  expect("once shown", r2.lit(), true);
}
