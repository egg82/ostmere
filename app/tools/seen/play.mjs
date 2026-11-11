// play.mjs <name> [WxH] [maxMin]: the play bot with the "was it seen" pass (probe.js beside it; docs/research/
// story-to-the-eyes.md). A newcomer plays the opening in real time against the server on 127.0.0.1:18771 (run.sh
// starts one), at WxH (default 1280x800): taps what glows, the obvious one-off steps, the Set and Both offers;
// gathers/scavenges by need before the mix; adds new mixable cards to the mix; edits the greyed mix; adds the ledger's
// rules; plays on two minutes past the end. Every new thing is logged with its wall and game minute, with a
// screenshot after each burst, into OUT/<name>/.
// The pass: every story line the server sends is classed tap-written when it lands at the instant a tap of the bot's
// own lands (the card it tapped, by tap or failed, completing at that game second), and, when the server names the
// card that wrote it (LogLine.card), only when that is the card. The probe's verdict for each line it saw show is
// joined to the server's lines by key, in order. Output: seen.json (lines by key, never their text) and a summary.
import { chromium } from 'playwright';
import fs from 'node:fs';

const [NAME = 'run', VIEW = '1280x800', MAXMIN = '40'] = process.argv.slice(2);
const [VW, VH] = VIEW.split('x').map(Number);
const BASE = 'http://127.0.0.1:18771/';
const DIR = `${process.env.OUT ?? '/vp'}/${NAME}`;
const OUT = `${DIR}/shots`;
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(`${DIR}/states`, { recursive: true });
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: VW, height: VH }, deviceScaleFactor: 1 });
const page = await ctx.newPage();
await page.addInitScript({ path: new URL('./probe.js', import.meta.url).pathname });
const content = await (await page.request.get(BASE + 'api/content')).json();
const text = Object.fromEntries(content.text_entries.map((e) => [e.key, e.text]));
const byTitle = Object.fromEntries(content.card_infos.map((c) => [text[c.label_key], c.card]));
const info = Object.fromEntries(content.card_infos.map((c) => [c.card, c]));

let t0 = null;   // wall ms at Begin
const wmin = () => (t0 === null ? 0 : (Date.now() - t0) / 60000);
const fmt = (m) => `${Math.floor(m)}:${String(Math.floor((m % 1) * 60)).padStart(2, '0')}`;
const events = [];
const issues = [];
const log = (...a) => console.log(`[${fmt(wmin())}]`, ...a);
const note = (kind, what, gameAt) => { const e = { wall: +wmin().toFixed(3), game: gameAt ?? lastView?.at ?? null, kind, what }; events.push(e); log('NEW', kind, what, 'game', gameAt); };
const issue = (what) => { issues.push({ wall: +wmin().toFixed(3), game: lastView?.at ?? null, what }); log('ISSUE', what); };

page.on('pageerror', (e) => issue('pageerror ' + e.message));
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') issue(`console ${m.type()} ${m.text().slice(0, 200)}`); });

// ---- the step stream: what is new
let lastView = null;
let pendingShot = null;   // {since, tags:Set}
const flag = (tag) => { if (!pendingShot) pendingShot = { since: Date.now(), tags: new Set() }; pendingShot.tags.add(tag); };
const allLines = [];
const mine = new Set();   // cards the bot tapped whose tap has not ended
const tapped = (v, card) => (v?.cards ?? []).find((c) => c.card === card && (c.by === 'tap' || c.by === 'failed')) ?? null;
const unlockKey = (u) => `${u.category}:${u.id}`;
function diff(view, lines) {
  const prev = lastView;
  for (const l of lines ?? []) {
    const by = [...mine].find((card) => tapped(prev, card)?.completes_at === l.at) ?? null;
    const named = 'card' in l;   // a build whose server names the card that wrote a line
    const tapWritten = by !== null && (!named || l.card === by);
    allLines.push({ key: l.key, game: view.at, wall: wmin(), tapWritten, by: tapWritten ? by : null, serverCard: named ? l.card : undefined });
    note('line', l.key, view.at); flag('line:' + l.key);
  }
  for (const card of [...mine]) if (tapped(prev, card) && !tapped(view, card)) mine.delete(card);
  if (!prev) { lastView = view; return; }
  const had = new Set(prev.cards.map((c) => c.card).concat(prev.completed.map((c) => c.card)));
  for (const c of view.cards) if (!had.has(c.card)) { note('card', c.card, view.at); flag('card:' + c.card); }
  const gone = prev.cards.filter((c) => !view.cards.some((v) => v.card === c.card));
  for (const c of gone) note('card-left', c.card, view.at);
  for (const ch of view.chips) if (!prev.chips.includes(ch)) { note('chip', ch, view.at); flag('chip:' + ch); }
  for (const ch of prev.chips) if (!view.chips.includes(ch)) { note('chip-cleared', ch, view.at); flag('chipclear:' + ch); }
  const pu = new Set(prev.unlocked.map(unlockKey));
  for (const u of view.unlocked) if (!pu.has(unlockKey(u))) { note('unlock', unlockKey(u), view.at); if (!u.category.startsWith('card')) flag('unlock:' + unlockKey(u)); }
  for (const s of view.skills) { const p = prev.skills.find((x) => x.skill === s.skill); if (!p) { note('skill-row', `${s.skill} L${s.level}`, view.at); } else if (s.level > p.level) { note('skill-level', `${s.skill} L${s.level}`, view.at); flag(`level:${s.skill}${s.level}`); } }
  for (const l of view.ledger) if (!prev.ledger.some((p) => p.store === l.store)) note('ledger-line', l.store, view.at);
  if (view.mixes.length !== prev.mixes.length) { note('mixes', view.mixes.map((m) => m.id).join(','), view.at); flag('mix'); }
  const shape = (v) => JSON.stringify((v.mixes.find((m) => m.id === v.active_mix_id)?.components ?? []).map((c) => c.card ?? c.mix_id));
  if (shape(view) !== shape(prev)) note('mix-shape', shape(view), view.at);
  if (view.greyed_mix_ids.length !== prev.greyed_mix_ids.length) { note('greyed', view.greyed_mix_ids.join(','), view.at); flag('greyed'); }
  if (view.orders.length !== prev.orders.length) { note('orders', view.orders.length, view.at); flag('order'); }
  if (view.all_covered !== prev.all_covered) note('all_covered', view.all_covered, view.at);
  if (JSON.stringify(view.orders_on) !== JSON.stringify(prev.orders_on)) note('orders_on', JSON.stringify(view.orders_on), view.at);
  if (view.running_mix_id !== prev.running_mix_id) note('running', `${view.running_mix_id} order=${view.mix_order}`, view.at);
  lastView = view;
}
page.on('response', async (r) => {
  const u = r.url();
  if (!/\/api\/saves(\/\d+\/(open|advance|decisions))?$/.test(u)) return;   // not the dry run: it answers a View
  if (r.status() >= 400) issue(`http ${r.status()} ${u}`);
  try { const j = await r.json(); const s = j.view ? j : j.step; if (s?.view) diff(s.view, s.lines); } catch { /* no body */ }
});

// ---- screenshots
let n = 0;
const shotsMade = [];
async function shot(slug, tags = []) {
  const vis = await page.evaluate(() => document.visibilityState);
  if (vis !== 'visible') { issue('not visible at shot ' + slug); return; }
  n += 1;
  const name = `${String(n).padStart(2, '0')}-${slug}`;
  await page.screenshot({ path: `${OUT}/${name}.png` });
  fs.writeFileSync(`${DIR}/states/${name}.json`, JSON.stringify({ view: lastView }));
  shotsMade.push({ name, wall: +wmin().toFixed(2), game: lastView?.at ?? null, tags });
  log('SHOT', name, tags.join(' '));
}
const slugOf = (tags) => {
  const t = [...tags];
  const pick = t.find((x) => !x.startsWith('line:')) ?? t[0] ?? 'moment';
  return pick.replace(/^(card|chip|unlock|level|chipclear|line):/, (m, k) => (k === 'chipclear' ? 'clear-' : k === 'level' ? 'lv-' : '')).replace(/[^a-z0-9_-]+/gi, '-').slice(0, 40);
};
async function maybeShot() {
  if (!pendingShot || Date.now() - pendingShot.since < 1400) return;
  const tags = [...pendingShot.tags];
  pendingShot = null;
  await shot(slugOf(tags), tags);
}

// ---- in-page checks run every loop: one glow at most, layout shifts
await page.addInitScript(() => {
  window.__shifts = [];
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) {
        if (e.value < 0.001) continue;
        const src = (e.sources ?? []).map((s) => { const n = s.node; return n ? `${n.nodeName}.${(n.className && n.className.baseVal === undefined ? n.className : '').toString().replace(/ /g, '.')}` : '?'; });
        window.__shifts.push({ t: performance.now(), v: +e.value.toFixed(4), input: e.hadRecentInput, src });
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch { /* none */ }
});

const sleep = (ms) => page.waitForTimeout(ms);
let rngS = 12345;
const rnd = () => { rngS = (rngS * 1103515245 + 12345) % 2147483648; return rngS / 2147483648; };
const think = () => sleep(2500 + rnd() * 2500);

async function snapshot() {
  return page.evaluate(() => {
    const vis = (e) => !!e && e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden';
    const cards = [...document.querySelectorAll('.deck .card')].map((c, i) => ({
      i, title: c.querySelector('.card-title')?.textContent ?? '', cls: c.className,
      disabled: c.querySelector('.card-tap')?.disabled ?? true,
      mixVis: vis(c.querySelector('.card-mix')), mixOn: c.querySelector('.card-mix')?.classList.contains('on') ?? false,
      needs: c.querySelector('.card-needs')?.textContent ?? '', count: c.querySelector('.card-count')?.textContent ?? '',
      glow: c.querySelector('.card-tap')?.classList.contains('glow') ?? false,
    }));
    const glows = [...document.querySelectorAll('.glow')].filter(vis).map((g) => g.className + ':' + (g.textContent ?? '').slice(0, 30));
    const hands = document.querySelector('.hands');
    return {
      cards, glows, handsState: hands?.dataset.state, greyed: hands?.classList.contains('greyed'), handsText: hands?.textContent?.slice(0, 120),
      offer: vis(document.querySelector('.offer-both')), order: vis(document.querySelector('.line-order .primary')),
      editor: document.querySelector('.game')?.classList.contains('editing'),
      chips: [...document.querySelectorAll('.chip')].map((c) => c.textContent), camp: document.querySelector('.camp:not([hidden])')?.textContent ?? null,
      lines: [...document.querySelectorAll('.lines li')].map((l) => l.textContent.slice(0, 40)), dots: document.querySelectorAll('.new-dot').length,
      byRule: document.querySelector('.hands-runs.by-rule')?.textContent ?? '', runsText: document.querySelector('.hands-runs')?.textContent ?? '',
      mixName: document.querySelector('.hands-name-text')?.textContent ?? '', handsMixVisible: vis(document.querySelector('.hands-mix')),
      fullLine: [...document.querySelectorAll('.line-eta')].some((e) => vis(e) && e.textContent.trim() === 'full'),
      offerAdd: vis(document.querySelector('.line-order .primary')),
      shifts: window.__shifts.splice(0),
    };
  });
}
const idOf = (c) => byTitle[c.title] ?? c.title;
async function tapCard(i, why) {
  const loc = page.locator('.deck .card').nth(i).locator('.card-tap');
  const title = await page.locator('.deck .card').nth(i).locator('.card-title').textContent();
  log('TAP', byTitle[title] ?? title, '-', why);
  mine.add(byTitle[title] ?? title);
  await loc.click({ timeout: 3000 }).catch((e) => issue('tap failed ' + title + ' ' + e.message.split('\n')[0]));
}

// ---- go
await page.goto(BASE);
await sleep(2500);
await shot('front-page');
await page.click('#begin');
t0 = Date.now();
await sleep(2000);
await shot('begin', ['start']);

const tried = new Set();      // unready one-offs tried once
const added = new Set();      // cards added to the mix by its toggle
const seenAt = new Map();     // card id -> wall ms first seen
let ruleN = 0;
const addedViaEditor = new Set();
const ruleShots = { offer: false, list: false, running: false, back: false, full: false, newmix: false };
let dragged = false, lastLinesLen = 0, editorShot = false;
const deadline = Date.now() + +MAXMIN * 60000;
let afterEnd = false, endDeadline = 0;
const POSTMIN = 2;
const rw = { seenAt: null, started: false, done: false };
while (Date.now() < deadline) {
  if (afterEnd && Date.now() > endDeadline) break;
  await maybeShot();
  const s = await snapshot();
  if (s.seen === '1' && rw.seenAt === null) { rw.seenAt = lastView?.at ?? null; log('WRITING RULES OPEN at game', rw.seenAt, 'orders_on', JSON.stringify(lastView?.orders_on)); note('rule-seen', 'open', rw.seenAt); }
  for (const sh of s.shifts) if (sh.v >= 0.005) issue(`layout-shift ${sh.v} input=${sh.input} ${sh.src.join(',')}`);
  if (s.glows.length > 1) issue('more than one glow: ' + s.glows.join(' | '));
  if (s.byRule && !ruleShots.running) { ruleShots.running = true; log('RULE RUNNING', s.byRule, s.mixName); await sleep(900); await shot('rule-mix-running', ['rule-running']); }
  if (ruleShots.running && !ruleShots.back && !s.byRule && s.handsMixVisible) { ruleShots.back = true; log('OWN MIX BACK', s.mixName, s.runsText); await sleep(900); await shot('own-mix-back', ['own-back']); }
  if (s.fullLine && !ruleShots.full) { ruleShots.full = true; log('FULL LINE'); await sleep(600); await shot('full-store-line', ['full']); }
  let fresh = 0;
  for (const c of s.cards) if (!seenAt.has(idOf(c))) { seenAt.set(idOf(c), Date.now()); fresh += 1; }
  if (fresh && t0 !== null && wmin() > 0.1) { await sleep(2500); continue; }   // a newcomer reads a new card before acting
  // reading time for new lines
  if (allLines.length > lastLinesLen) { const k = allLines.length - lastLinesLen; lastLinesLen = allLines.length; await sleep(Math.min(6000, 1800 * k)); continue; }

  if (!afterEnd && lastView?.ended_at != null) {
    log('END'); await sleep(800); await shot('end', ['end']); fs.writeFileSync(`${DIR}/endsnap.json`, JSON.stringify(s));
    afterEnd = true; endDeadline = Date.now() + POSTMIN * 60000; continue;
  }
  if (s.order) {
    await maybeShot();
    const sentence = await page.locator('.line-order .rule-sentence').first().textContent().catch(() => '');
    ruleN += 1; const k = ruleN;
    log('OFFER', k, sentence);
    if (k <= 4) await shot('draining-line-offer-' + k, ['rule-offer']);
    log('ADD RULE', k); await page.locator('.line-order .primary').first().click(); await sleep(2500);
    if (k <= 4) {
      await page.locator('.hands-name:visible, .hands-plan:visible').first().click().catch((e) => issue('open list failed ' + e.message.split('\n')[0]));
      await sleep(1200);
      log('LIST after rule', k, 'run-when buttons', await page.locator('.run-when').count(), 'condition chips', await page.locator('.rule-cond').count());
      await shot('mixes-list-after-rule-' + k, ['mixes-list']);
      await page.keyboard.press('Escape'); await sleep(800);
    }
    await think(); continue;
  }
  if (s.offer) { log('BOTH'); await page.locator('.offer-both').first().click(); await sleep(2500);
    // the newcomer then drags the split once, toward whatever is shorter (stones, for the ring)
    if (!dragged) { dragged = true; const d = page.locator('.hands .share-divider').first();
      if (await d.count()) { const bx = await d.boundingBox(); if (bx) { await page.mouse.move(bx.x + bx.width / 2, bx.y + bx.height / 2); await page.mouse.down(); await page.mouse.move(bx.x + bx.width / 2 - 40, bx.y + bx.height / 2, { steps: 8 }); await page.mouse.up(); log('DRAGGED divider -40px'); } }
      else issue('no divider on the strip after Both'); }
    await think(); continue; }
  if (s.greyed && !s.editor) {
    log('EDIT greyed mix'); await maybeShot(); if (!editorShot) { await sleep(500); await shot('greyed-mix', ['greyed']); }
    await page.locator('.hands-edit').first().click(); await sleep(1500);
    if (!editorShot) { editorShot = true; await shot('editor-open', ['editor']); }
    for (let k = 0; k < 4 && await page.locator('.editor-entry .entry-note').count(); k++) {
      await page.locator('.editor-entry:has(.entry-note) .entry-remove').first().click().catch(() => {}); await sleep(600);
    }
    const adds = page.locator('.editor .add-card');
    const names = await adds.allTextContents();
    log('editor adds offered', names.join(' | '));
    const wc = names.findIndex((x) => /wood|cut|fell|chop/i.test(x));
    if (wc >= 0) { await adds.nth(wc).click(); await sleep(1500); }
    await shot('editor-edited', ['editor-after']);
    await page.locator('.editor .primary').first().click().catch((e) => issue('editor save failed ' + e.message.split('\n')[0]));
    await sleep(1500);
    if (!ruleShots.newmix) {
      ruleShots.newmix = true;
      await page.locator('.hands-name:visible, .hands-plan:visible').first().click().catch((e) => issue('open list2 failed ' + e.message.split('\n')[0]));
      await sleep(1200); await shot('mixes-list-late', ['mixes-list-late']);
      await page.locator('.selector .selector-new').first().click().catch((e) => issue('new mix click failed ' + e.message.split('\n')[0]));
      await sleep(1500); await shot('new-mix-opened', ['new-mix']);
      await page.locator('.editor-close').click().catch((e) => issue('editor close failed ' + e.message.split('\n')[0])); await sleep(1000);
    }
    await think(); continue;
  }
  if (s.editor) { log('editor open unexpectedly; closing'); await page.locator('.editor-close').click().catch(() => {}); await think(); continue; }
  // a new mixable task appears: the player adds it to the mix in the editor
  if (s.handsState === 'mix' && !s.greyed && !s.editor) {
    for (const id of ['rest']) {
      const c = s.cards.find((x) => idOf(x) === id);
      if (c && !addedViaEditor.has(id) && Date.now() - (seenAt.get(id) ?? Date.now()) > 8000) {
        addedViaEditor.add(id); log('EDITOR ADD', id);
        await page.locator('.hands-edit').first().click(); await sleep(1200);
        const adds = page.locator('.editor .add-card'); const names = await adds.allTextContents();
        const want = names.findIndex((x) => x.includes(text[info[id].label_key]));
        if (want >= 0) { await adds.nth(want).click(); await sleep(1000); await shot('editor-add-' + id, ['editor-add']); }
        else issue('editor offers no ' + id + ': ' + names.join('|'));
        await page.locator('.editor .primary').first().click().catch((e) => issue('editor save failed ' + e.message.split('\n')[0]));
        await think(); break;
      }
    }
  }
  // the glow
  const g = s.cards.find((c) => c.glow && !c.disabled);
  if (g) { await tapCard(g.i, 'glow'); await think(); continue; }
  // the obvious steps: ready one-offs (capped), then the rack
  const oneOff = (c) => /card-(narrative|craft)/.test(c.cls) && !/done/.test(c.cls);
  const ready = s.cards.filter((c) => oneOff(c) && /\bready\b/.test(c.cls) && !c.disabled);
  if (ready.length) { await tapCard(ready[0].i, 'ready step'); await think(); continue; }
  const rack = s.cards.find((c) => idOf(c) === 'lay_to_dry' && /\bready\b/.test(c.cls) && !c.disabled);
  if (rack) { await tapCard(rack.i, 'rack ready'); await think(); continue; }
  // one early try of an unready step a newcomer would poke (seen 10 s or more)
  const poke = s.cards.find((c) => oneOff(c) && /unready/.test(c.cls) && !c.disabled && !tried.has(idOf(c)) && ['ring_it', 'strike_fire', 'roast_roots'].includes(idOf(c)) && Date.now() - (seenAt.get(idOf(c)) ?? Date.now()) > 10000);
  if (poke) { tried.add(idOf(poke)); await tapCard(poke.i, 'early try'); await think(); continue; }
  // roots for the roast: forage by hand (it is not in the mix), when the roast lacks roots
  const roastC = s.cards.find((c) => idOf(c) === 'roast_roots' && !/done/.test(c.cls));
  const forageC = s.cards.find((c) => idOf(c) === 'forage' && !c.disabled);
  if (roastC && forageC && /roots/.test(roastC.needs) && !/\bready\b/.test(roastC.cls) && !afterEnd) { await tapCard(forageC.i, 'roots by hand'); await think(); continue; }
  // before the mix: gather or scavenge by what is short
  if (s.handsState !== 'mix') {
    const gather = s.cards.find((c) => idOf(c) === 'gather_wood' && !c.disabled && !/done/.test(c.cls));
    const scav = s.cards.find((c) => idOf(c) === 'scavenge' && !c.disabled && !/done/.test(c.cls));
    const rackNeed = s.cards.find((c) => idOf(c) === 'lay_to_dry')?.needs ?? '';
    const ringNeed = s.cards.find((c) => idOf(c) === 'ring_it')?.needs ?? '';
    const dampShort = /(\d+)\/(\d+)/.exec(rackNeed); const stoneShort = /(\d+)\/(\d+)/.exec(ringNeed);
    const wantWood = dampShort && +dampShort[1] < +dampShort[2];
    const wantStone = stoneShort && +stoneShort[1] < +stoneShort[2];
    let pick = null;
    if (gather && scav) pick = wantStone && !wantWood ? scav : wantWood && !wantStone ? gather : rnd() < 0.5 ? gather : scav;
    else pick = gather ?? scav;
    if (pick) { await tapCard(pick.i, 'by hand'); await think(); continue; }
  }
  await sleep(1500);   // waiting: the mix and the rack run
}
await maybeShot();
fs.writeFileSync(`${DIR}/events.json`, JSON.stringify({ events, issues, shots: shotsMade, lines: allLines }, null, 1));
fs.writeFileSync(`${DIR}/lastview.json`, JSON.stringify(lastView, null, 1));
await sleep(11_000);   // the last line's reading window closes
const probed = await page.evaluate(() => window.__seenReport());
const keysOf = (t) => content.text_entries.filter((e) => e.text === t).map((e) => e.key);
const used = new Set();
const seen = allLines.map((l, i) => {
  const j = probed.findIndex((p, k) => !used.has(k) && keysOf(p.text).includes(l.key));
  if (j >= 0) used.add(j);
  const { text: _text, ...p } = j >= 0 ? probed[j] : { seen: false, instances: [], shown: false };
  return { i, key: l.key, game: l.game, tapWritten: l.tapWritten, by: l.by, serverCard: l.serverCard, shown: j >= 0, ...p };
});
const unmatched = probed.filter((_, k) => !used.has(k)).map((p) => keysOf(p.text)[0] ?? '(no key)');
const rate = (xs, f) => `${xs.filter(f).length}/${xs.length}`;
const tw = seen.filter((l) => l.tapWritten);
const summary = {
  name: NAME, view: VIEW, lines: seen.length, tapWritten: tw.length,
  seen_all: rate(seen, (l) => l.seen), seen_tapWritten: rate(tw, (l) => l.seen), seen_other: rate(seen.filter((l) => !l.tapWritten), (l) => l.seen),
  alone_all: rate(seen, (l) => l.instances.some((x) => x.alone)), aloneStrict_all: rate(seen, (l) => l.instances.some((x) => x.aloneStrict)),
  visible_all: rate(seen, (l) => l.instances.some((x) => x.visible)), near_all: rate(seen, (l) => l.instances.some((x) => x.near)),
  never_shown: seen.filter((l) => !l.shown).map((l) => l.key), probe_lines_unmatched: unmatched,
  server_names_cards: seen.some((l) => l.serverCard !== undefined),
};
fs.writeFileSync(`${DIR}/seen.json`, JSON.stringify({ summary, lines: seen, issues }, null, 1));
log('SEEN', JSON.stringify(summary));
log('DONE events', events.length, 'issues', issues.length, 'shots', n);
await b.close();
