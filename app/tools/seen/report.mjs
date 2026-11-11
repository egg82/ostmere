// report.mjs <seen.json>...: the "was it seen" runs side by side (run.sh writes them), against the targets in
// docs/research/story-to-the-eyes.md: at least 80% of tap-written lines seen, at least 90% of lines with their reading
// window to themselves. Lines are named by key; a failed line lists the conditions it failed.
// Before a server names the card that wrote a line, a run classes lines by the tap landing alone; a key that a later
// run's server attributes to no card or another card is reclassed by that run (content is the same across builds).
import fs from 'node:fs';

const runs = process.argv.slice(2).map((f) => ({ file: f, ...JSON.parse(fs.readFileSync(f, 'utf8')) }));
const writer = new Map();   // key -> the card the server says wrote it (from runs whose server names cards)
for (const r of runs) for (const l of r.lines) if (l.serverCard !== undefined) writer.set(l.key, l.serverCard);
const pct = (n, d) => (d ? `${n}/${d} (${Math.round((100 * n) / d)}%)` : '—');

for (const r of runs) {
  const lines = r.lines.map((l) => ({ ...l, tapWritten: l.tapWritten && (!writer.has(l.key) || writer.get(l.key) === l.by) }));
  const tw = lines.filter((l) => l.tapWritten);
  const alone = (l) => l.instances.some((x) => x.alone);
  const fails = (l) => (l.shown ? ['visible', 'near', 'alone'].filter((c) => !l.instances.some((x) => x[c])) : ['never shown']);
  console.log(`\n== ${r.summary.name} (${r.summary.view}) ${r.file}`);
  console.log(`tap-written seen      ${pct(tw.filter((l) => l.seen).length, tw.length)}   target >= 80%`);
  console.log(`all lines seen        ${pct(lines.filter((l) => l.seen).length, lines.length)}`);
  const strict = (l) => l.instances.some((x) => x.visibleStrict && x.near && x.aloneStrict);
  console.log(`strict (whole reading time, a tap does not close it): tap-written ${pct(tw.filter(strict).length, tw.length)}, all ${pct(lines.filter(strict).length, lines.length)}`);
  console.log(`window to themselves  ${pct(lines.filter(alone).length, lines.length)}   target >= 90%  (strict, to the end of the reading time: ${pct(lines.filter((l) => l.instances.some((x) => x.aloneStrict)).length, lines.length)})`);
  console.log(`visible ${pct(lines.filter((l) => l.instances.some((x) => x.visible)).length, lines.length)}  near ${pct(lines.filter((l) => l.instances.some((x) => x.near)).length, lines.length)}  on a card ${lines.filter((l) => l.instances.some((x) => x.where === 'card')).length}`);
  for (const l of lines.filter((x) => !x.seen)) {
    const comp = [...new Set(l.instances.flatMap((x) => x.competing ?? []))].join(',');
    console.log(`  not seen: ${l.key}${l.tapWritten ? ' (tap)' : ''} game ${l.game}: ${fails(l).join('+')}${comp ? ` [${comp}]` : ''} near ${l.instances.map((x) => `${x.where}:${x.nearPx}`).join(' ')}`);
  }
  if (r.summary.probe_lines_unmatched?.length) console.log(`  probe lines with no server line: ${r.summary.probe_lines_unmatched.join(', ')}`);
}
