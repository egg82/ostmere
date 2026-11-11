// No function in src/ grows past LIMIT lines: large functions are where bugs hide. Functions already over it are held
// in gates/held/function_size.json as {file: {qualified name: lines}}. A new long function, or a held one that grew,
// fails naming it; one that shrank or went fails as stale, so a split in one place cannot pay for a new long function
// in another. `node gates/function-size.mjs --write` (from app/client) rewrites the ledger; never run it to let a
// longer function through. Functions are found with the TypeScript compiler's own parser. Run by `npm test`.
import ts from 'typescript';
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const CLIENT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(CLIENT, 'src');
const HELD = join(CLIENT, 'gates', 'held', 'function_size.json');
export const LIMIT = 80;

const FUNCTION_KINDS = new Set([
  ts.SyntaxKind.FunctionDeclaration, ts.SyntaxKind.FunctionExpression, ts.SyntaxKind.ArrowFunction,
  ts.SyntaxKind.MethodDeclaration, ts.SyntaxKind.Constructor, ts.SyntaxKind.GetAccessor, ts.SyntaxKind.SetAccessor,
]);

function nameOf(node) {
  if (ts.isConstructorDeclaration(node)) return 'constructor';
  if (node.name) return node.name.getText();
  const p = node.parent;
  if (ts.isVariableDeclaration(p) || ts.isPropertyAssignment(p) || ts.isPropertyDeclaration(p)) return p.name.getText();
  return '<anon>';
}

// Lines of every function over LIMIT in one file, by qualified name (`Class.method`, `outer.inner`); a repeated name
// takes `#2`, `#3` in source order.
export function sizes(source, fileName = 'x.ts') {
  const sf = ts.createSourceFile(fileName, source, ts.ScriptTarget.ES2022, true);
  const out = {};
  const seen = new Set();
  const visit = (node, scope) => {
    let inner = scope;
    if (FUNCTION_KINDS.has(node.kind) || ts.isClassDeclaration(node) || ts.isClassExpression(node)) {
      const local = ts.isClassDeclaration(node) || ts.isClassExpression(node) ? (node.name?.getText() ?? '<class>') : nameOf(node);
      let name = scope ? `${scope}.${local}` : local;
      for (let n = 2; seen.has(name); n++) name = `${scope ? `${scope}.` : ''}${local}#${n}`;
      seen.add(name);
      inner = name;
      if (!ts.isClassDeclaration(node) && !ts.isClassExpression(node)) {
        const start = sf.getLineAndCharacterOfPosition(node.getStart(sf)).line;
        const lines = sf.getLineAndCharacterOfPosition(node.getEnd()).line - start + 1;
        if (lines > LIMIT) out[name] = lines;
      }
    }
    ts.forEachChild(node, (c) => visit(c, inner));
  };
  visit(sf, '');
  return out;
}

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(join(dir, e.name)) : e.name.endsWith('.ts') ? [join(dir, e.name)] : []);
}

export const files = () => walk(SRC).sort();

export function counted(paths = files(), root = CLIENT) {
  const ledger = {};
  for (const p of paths) {
    const found = sizes(readFileSync(p, 'utf8'), p);
    if (Object.keys(found).length) ledger[relative(root, p)] = found;
  }
  return ledger;
}

// Every (file, name) over its held lines or new, then every one under it.
export function problems(found, held) {
  const rows = new Set();
  for (const led of [found, held]) for (const [f, fns] of Object.entries(led)) for (const k of Object.keys(fns)) rows.add(`${f}\0${k}`);
  const out = [];
  for (const row of [...rows].sort()) {
    const [f, k] = row.split('\0');
    const n = found[f]?.[k] ?? 0;
    const h = held[f]?.[k] ?? 0;
    if (n > h) out.push(`${f} ${k}: ${n} lines, held ${h}; over ${LIMIT} lines and not held: split it`);
    else if (n < h) out.push(`${f} ${k}: ${n}, held ${h}; stale, lower it (node gates/function-size.mjs --write)`);
  }
  return out;
}

function controls() {
  const body = (n) => Array.from({ length: n }, (_, i) => `  const x${i} = ${i};\n`).join('');
  const fn = (name, n) => `function ${name}() {\n${body(n - 2)}}\n`; // exactly n lines
  assert.deepEqual(sizes(fn('f', LIMIT + 1)), { f: LIMIT + 1 });
  assert.deepEqual(sizes(fn('f', LIMIT)), {});
  assert.deepEqual(sizes(`const g = () => {\n${body(LIMIT)}};\n`), { g: LIMIT + 2 });
  assert.deepEqual(Object.keys(sizes(`class V {\n  plan() {\n${body(LIMIT)}  }\n}\n${fn('plan', LIMIT + 1)}`)).sort(), ['V.plan', 'plan']);
  assert.deepEqual(Object.keys(sizes(fn('f', LIMIT + 1) + fn('f', LIMIT + 1))), ['f', 'f#2']);
  const held = { 'a.ts': { plan: LIMIT + 1 } };
  assert.deepEqual(problems(held, held), []);
  const swapped = { 'a.ts': { 'V.plan': LIMIT + 1 } };
  assert.equal(problems(swapped, held).length, 2);
  assert.match(problems(held, { 'a.ts': { plan: LIMIT + 9 } })[0], /stale, lower it/);
  assert.match(problems({ 'a.ts': { plan: LIMIT + 9 } }, held)[0], /split it/);
}

export function run() {
  controls();
  const paths = files();
  assert.ok(paths.length > 20, `only ${paths.length} files under src/: the gate would pass on nothing`);
  const wrong = problems(counted(paths), JSON.parse(readFileSync(HELD, 'utf8')));
  assert.deepEqual(wrong, [], `function-size ledger:\n${wrong.join('\n')}`);
}

if (process.argv[1] === fileURLToPath(import.meta.url) && process.argv[2] === '--write') {
  const sorted = Object.fromEntries(Object.entries(counted()).sort().map(([f, fns]) => [f, Object.fromEntries(Object.entries(fns).sort())]));
  writeFileSync(HELD, `${JSON.stringify(sorted, null, 1)}\n`);
  console.log(`wrote ${relative(CLIENT, HELD)}: ${Object.keys(sorted).length} files`);
}
