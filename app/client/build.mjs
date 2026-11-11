// Bundles the page's TypeScript into one directory that holds nothing hand-written (default build/, gitignored):
// src/main.ts -> game.js, and the CSS it imports -> game.css. The image copies that directory to
// ashfall_app/build/client, which the server serves at /build/<build>/.
// `--fixtures` bundles fixtures/dev-main.ts instead: the page against hand-built Steps, for screenshots. Never shipped.
// Usage: node build.mjs [--fixtures] [outdir]
import { build } from 'esbuild';
import { rmSync } from 'node:fs';

const args = process.argv.slice(2);
const fixtures = args.includes('--fixtures');
const outdir = args.find((a) => !a.startsWith('--')) ?? 'build';

rmSync(outdir, { recursive: true, force: true });
await build({
  entryPoints: { game: fixtures ? 'fixtures/dev-main.ts' : 'src/main.ts' },
  outdir,
  bundle: true,
  format: 'esm',
  target: 'es2022',
  minify: !fixtures,
  sourcemap: fixtures ? 'inline' : false,
  banner: { js: '// Built from src/ by build.mjs. Do not edit.' },
});
console.log(`bundled ${fixtures ? 'fixtures/dev-main.ts' : 'src/main.ts'} into ${outdir}/`);
