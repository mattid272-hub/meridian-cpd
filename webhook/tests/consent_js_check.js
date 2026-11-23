// Run by tests/test_meta_capi.py with node: the 404 page's forwarding script and consent.js, in a fake DOM.
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const site = path.join(__dirname, "..", "..", "landing-page");
const assert = (c, m) => { if (!c) { console.error("FAIL " + m); process.exit(1); } };

function el(tag) {
  return { tagName: tag.toUpperCase(), hidden: false, children: [], attrs: {}, parentNode: null,
    setAttribute(k, v) { this.attrs[k] = v; }, getAttribute(k) { return this.attrs[k]; },
    appendChild(c) { c.parentNode = this; this.children.push(c); return c; },
    insertBefore(c) { c.parentNode = this; this.children.push(c); return c; },
    addEventListener() {}, querySelector() { return { focus() {} }; }, focus() {} };
}
function page(pathname, hash, cookie) {
  const listeners = {}, scripts = [], replaced = [];
  const body = el("body"), head = el("head");
  const origAppend = body.appendChild.bind(body);
  body.appendChild = (c) => { if (c.tagName === "SCRIPT") scripts.push(c.src); return origAppend(c); };
  const document = { body, head, cookie: cookie || "", currentScript: null,
    createElement: el, createTextNode: () => el("#text"),
    getElementsByTagName: () => [{ parentNode: { insertBefore(c) { scripts.push(c.src); } } }],
    querySelector: () => null,
    addEventListener(t, f) { (listeners[t] = listeners[t] || []).push(f); } };
  const location = { pathname, hash: hash || "", search: "?x=1", hostname: "meridiancpd.co.uk",
    origin: "https://meridiancpd.co.uk", protocol: "https:", replace(u) { replaced.push(u); } };
  const window = { location, document, crypto: { getRandomValues: (a) => a } };
  window.window = window;
  const ctx = vm.createContext({ window, document, location, navigator: { sendBeacon: () => true },
    localStorage: { getItem: () => null, removeItem() {} }, fetch() {}, JSON, Uint8Array, Array });
  return { ctx, listeners, scripts, replaced, document, fire(t) { (listeners[t] || []).forEach((f) => f()); } };
}

// 1. 404.html: a forwarded address never loads consent.js; any other address loads it once.
const html = fs.readFileSync(path.join(site, "404.html"), "utf8");
assert(!/<script[^>]+src="\/consent\.js"/.test(html), "404.html still has a consent.js script tag");
const inline = html.match(/<script>([\s\S]*?)<\/script>/)[1];
for (const p of ["/verify/MER-2026-0001", "/complete/tok123", "/my-cpd", "/my-cpd/login/tok", "/download/x", "/unsubscribe"]) {
  const pg = page(p);
  vm.runInContext(inline, pg.ctx); pg.fire("DOMContentLoaded");
  assert(pg.replaced.length === 1 && pg.scripts.length === 0, "consent.js loaded on forwarded " + p);
}
for (const p of ["/no-such-page", "/verifyx", "/courses"]) {
  const pg = page(p);
  vm.runInContext(inline, pg.ctx); pg.fire("DOMContentLoaded");
  assert(pg.replaced.length === 0 && pg.scripts.length === 1 && pg.scripts[0] === "/consent.js", "consent.js not loaded on " + p);
}

// 2. consent.js: #cookie-settings opens the banner even when a choice is stored.
const js = fs.readFileSync(path.join(site, "consent.js"), "utf8");
function banner(hash, cookie) {
  const pg = page("/privacy.html", hash, cookie);
  vm.runInContext(js, pg.ctx);
  return pg.document.body.children.find((c) => c.className === "mcpd-cookie");
}
assert(banner("#cookie-settings", "mcpd_consent=no").hidden === false, "#cookie-settings did not open the banner (choice no)");
assert(banner("#cookie-settings", "mcpd_consent=yes").hidden === false, "#cookie-settings did not open the banner (choice yes)");
assert(banner("", "mcpd_consent=no").hidden === true, "banner shown with a stored choice and no hash");
assert(banner("#cookies", "mcpd_consent=no").hidden === true, "banner shown for #cookies");
assert(banner("", "").hidden === false, "banner hidden with no choice");
console.log("consent js: all checks passed");
