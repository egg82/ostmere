// The "was it seen" probe (docs/research/story-to-the-eyes.md, "The 'was it seen' probe"), injected into the game page
// before it loads (Playwright addInitScript). It watches every story line instance that shows (the band's `.lines li`
// and, where a build has them, `.card-line`) and, through that line's reading window, records whether it was
//   visible: its box wholly in the viewport, the page visible, and elementFromPoint at its start, middle and end hitting
//            it (nothing covers it), on at least 90% of 100 ms samples until its reading time ends or the player taps
//            again (`visibleStrict`: to the end of the reading time);
//   near:    its first word within 300 CSS px of the last tap before it showed, or of the bar on the card that tap hit
//            (Huang, White & Buscher 2012's cursor offsets; an assumed threshold, not one measured for touch);
//   alone:   no other onset outside the line's own place (its card, for a line on a card) from when it showed until its
//            reading time ends or the player taps again, whichever is sooner (`aloneStrict`: until its reading time ends).
// Onsets, counted only when on screen: an element gaining arrive, landed, flourish, burst, settle, fired, glow or done;
// a card leaving the deck; another line showing. A line counts as seen when one of its instances meets all three. The reading time is the
// page's own (game/reading.ts: 2.9 words a second, at least 3 s), used for every build so they share one yardstick.
// window.__seenReport() returns the lines (with their text, which the caller maps to keys and never prints).
(() => {
  const EDGE_MS = 50;   // an onset at the window's very end is the next thing, not a rival (frame timing)
  const WPS = 2.9, MIN_MS = 3000, NEAR_PX = 300, SAMPLE_MS = 100, VISIBLE_SHARE = 0.9, SAME_LINE_MS = 400;
  const ONSET = ['arrive', 'landed', 'flourish', 'burst', 'settle', 'fired', 'glow', 'done'];
  const readMs = (text) => Math.max(MIN_MS, Math.round((text.split(/\s+/).filter(Boolean).length / WPS) * 1000));
  const box = (r) => ({ l: r.left, t: r.top, r: r.right, b: r.bottom });
  const lines = [];
  const onsets = [];
  const taps = [];
  let lastTap = null;

  document.addEventListener('pointerdown', (e) => {
    const card = e.target instanceof Element ? e.target.closest('.card') : null;
    const track = card?.querySelector('.card-track');
    lastTap = { t: performance.now(), x: e.clientX, y: e.clientY, bar: track ? box(track.getBoundingClientRect()) : null };
    taps.push(lastTap.t);
  }, true);

  const isLine = (n) => n instanceof Element && n.matches('.lines li, .card-line');
  const showing = (n) => n.isConnected && !n.classList.contains('held') && !n.classList.contains('still');

  function pointToBox(x, y, b) {
    const dx = Math.max(b.l - x, 0, x - b.r), dy = Math.max(b.t - y, 0, y - b.b);
    return Math.hypot(dx, dy);
  }
  function boxToBox(a, b) {
    const dx = Math.max(a.l - b.r, 0, b.l - a.r), dy = Math.max(a.t - b.b, 0, b.t - a.b);
    return Math.hypot(dx, dy);
  }
  function firstWord(n) {
    const walker = document.createTreeWalker(n, NodeFilter.SHOW_TEXT);
    for (let t = walker.nextNode(); t; t = walker.nextNode()) {
      const m = /\S+/.exec(t.data);
      if (!m) continue;
      const range = document.createRange();
      range.setStart(t, m.index);
      range.setEnd(t, m.index + m[0].length);
      return box(range.getBoundingClientRect());
    }
    return box(n.getBoundingClientRect());
  }
  function hits(n, x, y) {
    const keep = n.style.pointerEvents;
    n.style.pointerEvents = 'auto';   // a line drawn over a card lets taps through; hit-test it as if it did not
    const hit = document.elementFromPoint(x, y);
    n.style.pointerEvents = keep;
    return hit !== null && (hit === n || n.contains(hit));
  }
  function visible(n) {
    if (document.visibilityState !== 'visible' || !n.isConnected) return false;
    const r = n.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0 || r.top < 0 || r.left < 0 || r.bottom > innerHeight || r.right > innerWidth) return false;
    const y = r.top + Math.min(r.height / 2, 10);
    return hits(n, r.left + 2, y) && hits(n, r.left + r.width / 2, r.top + r.height / 2) && hits(n, r.right - 2, r.bottom - Math.min(r.height / 2, 10));
  }

  function start(n) {
    if (n.__seen) return;
    const now = performance.now();
    const text = n.textContent ?? '';
    let ev = lines.find((l) => l.text === text && now - l.t < SAME_LINE_MS);
    if (!ev) {
      ev = { text, t: now, readMs: readMs(text), instances: [] };
      lines.push(ev);
    }
    const where = n.classList.contains('card-line') ? 'card' : 'band';
    const fw = firstWord(n);
    const tap = lastTap;
    const nearPx = tap ? Math.min(pointToBox(tap.x, tap.y, fw), tap.bar ? boxToBox(tap.bar, fw) : Infinity) : Infinity;
    const inst = { where, node: n, card: n.closest('.card'), samples: 0, visible: 0, samplesStrict: 0, visibleStrict: 0, nearPx, until: ev.t + ev.readMs };   // its card as it showed: the line leaves it later
    n.__seen = inst;
    ev.instances.push(inst);
    onsets.push({ t: now, node: n, line: ev });
  }

  /** Some of it on screen and not hidden: an onset nobody could see competes with nothing. */
  function onScreen(n) {
    if (!(n instanceof Element) || !n.isConnected || document.visibilityState !== 'visible') return false;
    const r = n.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0 || r.bottom <= 0 || r.right <= 0 || r.top >= innerHeight || r.left >= innerWidth) return false;
    return getComputedStyle(n).visibility !== 'hidden';
  }

  new MutationObserver((records) => {
    const now = performance.now();
    for (const m of records) {
      if (m.type === 'childList') {
        for (const n of m.addedNodes) if (isLine(n) && showing(n)) start(n);
        for (const n of m.removedNodes) {
          if (n instanceof Element && n.matches('.card') && m.target instanceof Element && m.target.closest('.deck') && onScreen(m.target)) onsets.push({ t: now, node: m.target, kind: 'card-left' });
        }
        continue;
      }
      const n = m.target;
      if (!(n instanceof Element)) continue;
      if (isLine(n)) {
        if (showing(n)) start(n);
        continue;
      }
      const before = new Set((m.oldValue ?? '').split(/\s+/));
      for (const c of ONSET) if (n.classList.contains(c) && !before.has(c) && onScreen(n)) onsets.push({ t: now, node: n, kind: c });
    }
  }).observe(document, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'], attributeOldValue: true });

  setInterval(() => {
    const now = performance.now();
    for (const ev of lines) {
      if (now > ev.t + ev.readMs) continue;
      for (const inst of ev.instances) {
        const v = visible(inst.node);
        inst.samplesStrict += 1;
        if (v) inst.visibleStrict += 1;
        if (taps.some((t) => t > ev.t + 50)) continue;   // the player has moved on: the window closed, as for alone
        inst.samples += 1;
        if (v) inst.visible += 1;
      }
    }
  }, SAMPLE_MS);

  /** Is this onset part of the instance's own place: the same line anywhere, or inside the card the line is on. */
  function own(inst, ev, o) {
    if (o.line === ev) return true;
    const card = inst.card;
    return card !== null && (card === o.node || card.contains(o.node));
  }

  window.__seenReport = () => lines.map((ev) => {
    const nextTap = taps.find((t) => t > ev.t + 50) ?? Infinity;
    const end = Math.min(ev.t + ev.readMs, nextTap);
    const instances = ev.instances.map((inst) => {
      const others = onsets.filter((o) => !own(inst, ev, o) && o.t >= ev.t - 50);
      const rivals = others.filter((o) => o.t < end - EDGE_MS);
      const competing = rivals.map((o) => o.kind ?? 'line');
      // where and when each rival came (classes only, never text), to tell what to move into the queue next
      const rivalsAt = rivals.map((o) => `${o.kind ?? 'line'}@${Math.round(o.t - ev.t)}ms:${o.node instanceof Element ? o.node.className.toString().split(' ').slice(0, 3).join('.') : '?'}`);
      const competingStrict = others.filter((o) => o.t < ev.t + ev.readMs - EDGE_MS).map((o) => o.kind ?? 'line');
      const visibleShare = inst.samples ? inst.visible / inst.samples : 0;
      const visibleStrict = inst.samplesStrict ? inst.visibleStrict / inst.samplesStrict >= VISIBLE_SHARE : false;
      const ok = { visible: visibleShare >= VISIBLE_SHARE, near: inst.nearPx <= NEAR_PX, alone: competing.length === 0 };
      return { where: inst.where, rivalsAt, visibleStrict, visibleShare: +visibleShare.toFixed(2), nearPx: Number.isFinite(inst.nearPx) ? Math.round(inst.nearPx) : null,
        competing, aloneStrict: competingStrict.length === 0, ...ok, seen: ok.visible && ok.near && ok.alone };
    });
    return { text: ev.text, t: Math.round(ev.t), readMs: ev.readMs, tappedAgainMs: Number.isFinite(nextTap) ? Math.round(nextTap - ev.t) : null,
      seen: instances.some((i) => i.seen), instances };
  });
})();
