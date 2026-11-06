// Meridian CPD streaming-style mock. Static, not product code.
// Course and series data come from data.js (generated from the real catalogue).
// The member, their progress, dates and certificate numbers are SAMPLE data.
(function () {
const D = window.MOCK_DATA;
const byId = Object.fromEntries(D.courses.map(c => [c.id, c]));
const TODAY = '2026-11-06';

const WHERE = { EWS: 'England, Wales and Scotland', EW: 'England and Wales', E: 'England', S: 'Scotland', UK: 'UK-wide' };

// ── Sample member (not a real person; numbers follow the MER-YYYY-NNNN format) ──
const MEMBER = {
  name: 'Sample Member',
  plan: 'annual',
  completed: {
    'MER-DEA-001': { date: '2026-03-14', cert: 'MER-2026-0012' },
    'MER-DEA-002': { date: '2026-04-02', cert: 'MER-2026-0019' },
    'MER-RA-001':  { date: '2026-05-20', cert: 'MER-2026-0031' },
    'MER-ALL-022': { date: '2026-10-31', cert: 'MER-2026-0078' },
    'MER-ALL-023': { date: '2026-11-01', cert: 'MER-2026-0081' },
    'MER-ALL-024': { date: '2026-11-03', cert: 'MER-2026-0086' },
    'MER-ALL-019': { date: '2026-11-02', cert: 'MER-2026-0083' },
  },
  inProgress: { 'MER-ALL-020': 0.4, 'MER-SCO-001': 0.15 },
  favourites: ['MER-ALL-025', 'MER-ALL-018', 'MER-DEA-004'],
  readLater: ['MER-ALL-011', 'MER-SCO-002', 'MER-ALL-017'],
};

// ── One poster template for every cover ─────────────────────────────────────
// Carries a kicker, a short title, an optional part label and a line motif. No claims.
function shortTitle(c) {
  let t = c.title.replace(/^.*Series, Part \d+:\s*/, '');
  if (t.includes(':')) t = t.split(':')[0];
  return t;
}
function kicker(c) {
  if (c.series) return 'Field Work';
  if (c.where === 'S') return 'Scotland';
  return { DEA: 'For DEAs', RA: 'Retrofit', ALL: 'All assessors' }[c.strand] || '';
}
function motifFor(text) {
  const t = text.toLowerCase();
  if (/insulation|wall/.test(t)) return 'layers';
  if (/heat pump|heating|boiler|hot water|heat loss/.test(t)) return 'fan';
  if (/ventilat|airtight|breathe/.test(t)) return 'flow';
  if (/damp|moisture|condensation|mould|floors|roofs and lofts/.test(t)) return 'drop';
  if (/window/.test(t)) return 'window';
  if (/roof/.test(t)) return 'roof';
  if (/solar|renewable|lighting|pv/.test(t)) return 'sun';
  if (/scotland/.test(t)) return 'contour';
  return 'meridian';
}
const MOTIFS = {
  layers: '<g>' + [0,1,2,3,4].map(i => `<rect x="${300+i*26}" y="40" width="18" height="190" rx="2"/>`).join('') + '<path d="M290 80h150M290 135h150M290 190h150" opacity=".5"/></g>',
  fan: '<g><circle cx="370" cy="135" r="92"/><circle cx="370" cy="135" r="14"/>' + [0,72,144,216,288].map(a => `<path transform="rotate(${a} 370 135)" d="M370 121c10-40 40-62 58-50 10 18-20 42-58 50z"/>`).join('') + '</g>',
  flow: '<g>' + [0,1,2,3,4].map(i => `<path d="M280 ${60+i*38}c40-26 80 26 120 0s60-12 70 0"/>`).join('') + '<path d="M455 50l15 10-15 10M455 202l15 10-15 10"/></g>',
  drop: '<g><path d="M370 40c38 58 70 96 70 132a70 70 0 0 1-140 0c0-36 32-74 70-132z"/><path d="M335 175a36 36 0 0 0 30 34" opacity=".6"/><path d="M290 250h160" opacity=".5"/></g>',
  window: '<g><rect x="300" y="40" width="140" height="190" rx="3"/><path d="M370 40v190M300 135h140"/><path d="M285 245h170" opacity=".5"/></g>',
  roof: '<g><path d="M270 170l100-110 100 110"/><path d="M300 170v70h140v-70"/><path d="M330 128h80" opacity=".6"/></g>',
  sun: '<g><circle cx="370" cy="120" r="40"/>' + [0,45,90,135,180,225,270,315].map(a => `<path transform="rotate(${a} 370 120)" d="M370 60v-24"/>`).join('') + '<path d="M290 230l40-50h120l-40 50z" opacity=".7"/></g>',
  contour: '<g>' + [0,1,2,3,4].map(i => `<ellipse cx="380" cy="140" rx="${30+i*22}" ry="${18+i*16}" transform="rotate(-18 380 140)"/>`).join('') + '</g>',
  meridian: '<g><circle cx="370" cy="135" r="90"/><path d="M370 45v180"/><path d="M370 45q60 90 0 180"/><path d="M280 135h180" opacity=".4"/><circle cx="370" cy="135" r="6" fill="#D4FF00"/></g>',
};
function wrapWords(text, max) {
  const words = text.split(/\s+/); const lines = []; let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > max && cur) { lines.push(cur); cur = w; } else cur = (cur + ' ' + w).trim();
  }
  if (cur) lines.push(cur);
  return lines;
}
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function poster({ kicker, title, part, motif }) {
  let max = 13, size = 48, lines = wrapWords(title.toUpperCase(), max);
  if (lines.length > 3) { max = 17; size = 38; lines = wrapWords(title.toUpperCase(), max); }
  if (lines.length > 3) { lines = lines.slice(0, 3); lines[2] += '…'; }
  const y0 = 230 - (lines.length - 1) * size * 0.95 - (part ? 34 : 0);
  return `<svg viewBox="0 0 480 270" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(title)}">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16301A"/><stop offset="1" stop-color="#0A170B"/></linearGradient></defs>
  <rect width="480" height="270" fill="url(#g)"/>
  <g fill="none" stroke="#D4FF00" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" opacity=".35">${MOTIFS[motif] || MOTIFS.meridian}</g>
  <rect x="24" y="24" width="4" height="18" fill="#D4FF00"/>
  <text x="36" y="39" fill="#D4FF00" font-family="DM Sans, Arial" font-weight="700" font-size="13" letter-spacing="2">${esc(kicker.toUpperCase())}</text>
  ${lines.map((l, i) => `<text x="24" y="${y0 + i * size * 0.95}" fill="#FFFFFF" font-family="Bebas Neue, Impact, sans-serif" font-size="${size}" letter-spacing="1">${esc(l)}</text>`).join('')}
  ${part ? `<rect x="24" y="214" width="${part.length * 8.4 + 20}" height="26" rx="3" fill="#D4FF00"/><text x="34" y="232" fill="#0D1F0E" font-family="DM Sans, Arial" font-weight="700" font-size="12.5" letter-spacing="1.5">${esc(part.toUpperCase())}</text>` : ''}
  <text x="456" y="250" text-anchor="end" fill="#FFFFFF" opacity=".55" font-family="Bebas Neue, Impact, sans-serif" font-size="17" letter-spacing="2">MERIDIAN CPD</text>
</svg>`;
}
function coursePoster(c) {
  const s = c.series ? D.series[c.series] : null;
  return poster({ kicker: kicker(c), title: shortTitle(c), part: s ? `Part ${c.part} of ${s.courses.length}` : '', motif: motifFor(c.title) });
}
function seriesPoster(sid) {
  const s = D.series[sid];
  return poster({ kicker: 'Field Work series', title: s.title.replace('Field Work: ', ''), part: 'Three parts', motif: motifFor(s.title) });
}

// ── Helpers ──────────────────────────────────────────────────────────────────
const ICON = {
  heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z"/></svg>',
  heartOn: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z"/></svg>',
  mark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3h12v18l-6-4-6 4z"/></svg>',
  markOn: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 3h12v18l-6-4-6 4z"/></svg>',
  info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/></svg>',
  search: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>',
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 11l9-7 9 7v9h-6v-6H9v6H3z"/></svg>',
  stack: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M6 20h12"/></svg>',
  grid: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>',
  cert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="13" rx="1"/><circle cx="12" cy="19" r="2.5"/><path d="M7 9h10M7 12h6"/></svg>',
  deck: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="13" rx="1.5"/><path d="M8 21h8M12 17v4M6 8h7M6 11h10"/></svg>',
  notes: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 2h9l5 5v15H6z"/><path d="M15 2v5h5M9 12h8M9 16h8M9 8h3"/></svg>',
};
function hours(h) { return `${h % 1 ? h.toFixed(1) : h} CPD hour${h === 1 ? '' : 's'}`; }
function fmtDate(d) { const [y, m, dd] = d.split('-').map(Number); return `${dd} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m-1]} ${y}`; }
function status(id) {
  if (MEMBER.completed[id]) return '<span class="status done">Certificate issued</span>';
  if (MEMBER.inProgress[id] != null) return '<span class="status prog">In progress</span>';
  return '<span class="status none">No certificate yet</span>';
}
function primary(id, mode) {
  if (mode === 'public') {
    const c = byId[id];
    return c.free ? '<a class="btn btn-p btn-sm" href="#">Free with MERIDIAN10</a>' : '<a class="btn btn-p btn-sm" href="#">Buy, £19.99</a>';
  }
  if (MEMBER.completed[id]) return '<a class="btn btn-s btn-sm" href="certificates.html">View certificate</a>';
  if (MEMBER.inProgress[id] != null) return '<a class="btn btn-p btn-sm" href="course.html">Continue</a>';
  return '<a class="btn btn-p btn-sm" href="course.html">Open</a>';
}
function courseCard(id, mode) {
  const c = byId[id]; if (!c) return '';
  const fav = MEMBER.favourites.includes(id), later = MEMBER.readLater.includes(id);
  const p = MEMBER.inProgress[id];
  const metaBits = [hours(c.hours), WHERE[c.where] || ''];
  return `<div class="card">
    <div class="cover">${coursePoster(c)}${mode !== 'public' && p != null ? `<div class="mini-bar"><i style="width:${p * 100}%"></i></div>` : ''}</div>
    <div class="body">
      <div class="title">${esc(c.title)}</div>
      <div class="stmt">${esc(c.desc)}</div>
      <div class="meta">${metaBits.map(esc).join('<span class="dot"></span>')}</div>
      ${mode === 'public' ? '<div class="meta"><span class="status none">Certificate of completion</span></div>' : `<div class="meta">${status(id)}</div>`}
      <div class="acts">${primary(id, mode)}
        <button class="icon-btn" title="Info">${ICON.info}</button>
        ${mode === 'public' ? '' : `<button class="icon-btn ${fav ? 'on' : ''}" title="Favourite">${fav ? ICON.heartOn : ICON.heart}</button>
        <button class="icon-btn ${later ? 'on' : ''}" title="Read later">${later ? ICON.markOn : ICON.mark}</button>`}
      </div>
    </div></div>`;
}
function seriesHours(sid) { return D.series[sid].courses.reduce((a, id) => a + byId[id].hours, 0); }
function seriesDone(sid) { return D.series[sid].courses.filter(id => MEMBER.completed[id]).length; }
function seriesCard(sid, mode) {
  const s = D.series[sid];
  const done = seriesDone(sid);
  const parts = s.courses.map(id => {
    const c = byId[id];
    const cls = mode === 'public' ? '' : MEMBER.completed[id] ? 'done' : MEMBER.inProgress[id] != null ? 'prog' : '';
    return `<li class="${cls}">Part ${c.part}: ${esc(shortTitle(c))}</li>`;
  }).join('');
  const where = WHERE[byId[s.courses[0]].where];
  const bottom = mode === 'public'
    ? `<div style="display:flex;align-items:center;justify-content:space-between;margin-top:auto;padding-top:6px"><div class="price">£39.99<small>three parts</small></div></div>
       <div class="acts"><a class="btn btn-p btn-sm" href="#">Buy the series</a><a class="btn btn-s btn-sm" href="series.html">See the parts</a></div>`
    : `<div class="progress" style="margin-top:2px"><div class="bar"><div class="fill" style="width:${done / 3 * 100}%"></div></div><div class="lbl">${done} of 3 parts complete · ${done} certificate${done === 1 ? '' : 's'}</div></div>
       <div class="acts"><a class="btn ${done === 3 ? 'btn-s' : 'btn-p'} btn-sm" href="series.html">${done === 3 ? 'View series' : done ? 'Continue series' : 'Start series'}</a><button class="icon-btn" title="Info">${ICON.info}</button></div>`;
  return `<div class="card series">
    <div class="cover">${seriesPoster(sid)}</div>
    <div class="body">
      <div class="title">${esc(s.title)}</div>
      <ul class="series-parts">${parts}</ul>
      <div class="meta">${esc(hours(seriesHours(sid)))}<span class="dot"></span>${esc(where)}<span class="dot"></span>A certificate for each part</div>
      ${bottom}
    </div></div>`;
}
function row(title, cards, more) {
  if (!cards.length) return '';
  return `<section class="row"><div class="row-head"><h2>${esc(title)}</h2>${more ? `<a href="#">${esc(more)}</a>` : ''}</div><div class="rail">${cards.join('')}</div></section>`;
}
function memberTopbar(on) {
  const items = [['Home', 'dashboard.html'], ['Series', 'series.html'], ['Library', 'dashboard.html#library'], ['My certificates', 'certificates.html']];
  return `<div class="mock-ribbon">Mock for approval. Course and series data are real; the member, progress, dates and certificate numbers are sample data.</div>
  <header class="topbar"><a class="brand" href="dashboard.html">MERIDIAN <span>CPD</span></a>
    <nav class="nav">${items.map(([t, h]) => `<a href="${h}" class="${t === on ? 'on' : ''}">${t}</a>`).join('')}</nav>
    <div class="grow"></div>
    <div class="search">${ICON.search} Search courses and topics</div>
    <span class="who">${MEMBER.name}</span>
    <button class="icon-btn" title="Search" style="display:none">${ICON.search}</button>
  </header>
  <nav class="tabbar">
    <a href="dashboard.html" class="${on === 'Home' ? 'on' : ''}">${ICON.home}Home</a>
    <a href="series.html" class="${on === 'Series' ? 'on' : ''}">${ICON.stack}Series</a>
    <a href="dashboard.html#library">${ICON.grid}Library</a>
    <a href="certificates.html" class="${on === 'My certificates' ? 'on' : ''}">${ICON.cert}Certificates</a>
  </nav>`;
}
function totals() {
  const ids = Object.keys(MEMBER.completed).filter(id => MEMBER.completed[id].date.startsWith('2026'));
  return { hours: ids.reduce((a, id) => a + byId[id].hours, 0), certs: ids.length };
}

window.M = { D, byId, MEMBER, WHERE, TODAY, ICON, poster, coursePoster, seriesPoster, shortTitle, courseCard, seriesCard, row, memberTopbar, hours, fmtDate, status, esc, seriesHours, seriesDone, totals };
})();
