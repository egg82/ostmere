// Runs the client's tests: each test/*.test.ts is bundled for node in memory and imported; a failed expectation
// throws, which fails the run (an xfail one must throw). Usage: node test.mjs
import { build } from 'esbuild';
import { readdirSync } from 'node:fs';

const files = readdirSync('test').filter((f) => f.endsWith('.test.ts'));
if (files.length === 0) throw new Error('no tests found in test/');
// A crash names its test and keeps the bundle out of the stack: node prints a data: URL whole, and CI's log cuts the
// line, error and all.
let running = '(none)';
// A file's timers end with it: one it left pending (an open editor's preview, an arrival queue's next pop) would run
// during a later file, on that file's fake DOM, and crash there on a slow runner. Whatever a file awaits has already run.
const pending = new Set();
const realSet = globalThis.setTimeout;
const realClear = globalThis.clearTimeout;
globalThis.setTimeout = (fn, ms, ...args) => {
  const handle = realSet(() => { pending.delete(handle); fn(...args); }, ms);
  pending.add(handle);
  return handle;
};
globalThis.clearTimeout = (handle) => { pending.delete(handle); realClear(handle); };
const fail = (e) => {
  console.error(`FAIL ${running} (crashed): ${String(e?.stack ?? e).replace(/data:text\/javascript;base64,[A-Za-z0-9+/=]+/g, '<bundle>')}`);
  process.exit(1);
};
process.on('uncaughtException', fail);
process.on('unhandledRejection', fail);
for (const file of files) {
  running = file;
  const out = await build({
    entryPoints: [`test/${file}`], bundle: true, platform: 'node', format: 'esm', write: false, logLevel: 'warning',
  });
  const code = out.outputFiles[0].text;
  const loaded = import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`);
  // `*.xfail.test.ts` is a finding committed ahead of its fix: it must fail now, and the fix renames it to a plain test.
  const xfail = file.endsWith('.xfail.test.ts');
  if (xfail) {
    if (await loaded.then(() => true, () => false)) fail(new Error('an xfail test passed: drop ".xfail" from its name'));
  } else {
    await loaded.catch(fail);
  }
  for (const handle of pending) realClear(handle);
  pending.clear();
  console.log(`${xfail ? 'xfail' : 'ok'} ${file}`);
}

// The structural gates (gates/): held ledgers over src/.
const { run: functionSizeGate } = await import('./gates/function-size.mjs');
functionSizeGate();
console.log('ok gates/function-size');
