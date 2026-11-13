// Run by tests/test_buy_links.py with node: landing-page/checkout.js switched off (as shipped)
// and on, and consent.js reading an app /buy link as a checkout.
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const site = path.join(__dirname, "..", "..", "landing-page");
const assert = (c, m) => { if (!c) { console.error("FAIL " + m); process.exit(1); } };
const SINGLE = "https://buy.stripe.com/9B6bJ0bsefk72j02zE73G00", SERIES = "https://buy.stripe.com/7sYaEWfIu8VJ7Dkdei73G02";

function run(src) {
  const links = [SINGLE + "?client_reference_id=MER-DEA-004", "https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01"].map((h) => {
    const a = { attrs: { href: h }, getAttribute(k) { return this.attrs[k]; }, setAttribute(k, v) { this.attrs[k] = v; } };
    return a;
  });
  const document = { readyState: "complete", addEventListener() {},
    querySelectorAll: (sel) => links.filter((a) => sel.split(",").some((s) => a.attrs.href.indexOf(s.match(/"([^"]+)"/)[1]) === 0)) };
  const window = {};
  vm.runInContext(src, vm.createContext({ window, document, URLSearchParams, encodeURIComponent, Array }));
  return { co: window.MeridianCheckout, links };
}
const src = fs.readFileSync(path.join(site, "checkout.js"), "utf8");
let t = run(src);
assert(t.co.viaApp === false, "ships off");
assert(t.co.buyLink(SINGLE, "MER-ALL-022", "") === SINGLE + "?client_reference_id=MER-ALL-022", "off: course link");
assert(t.co.buyLink(SINGLE, "MER-DEA-001", "MERIDIAN10") === SINGLE + "?client_reference_id=MER-DEA-001&prefilled_promo_code=MERIDIAN10", "off: promo");
assert(t.co.buyLink(SERIES, "FW-HEATING", "") === SERIES + "?client_reference_id=FW-HEATING", "off: series link");
assert(t.links[0].attrs.href === SINGLE + "?client_reference_id=MER-DEA-004", "off: home page buttons untouched");

t = run(src.replace("var VIA_APP = false;", "var VIA_APP = true;"));
assert(t.co.buyLink(SINGLE, "MER-ALL-022", "") === "https://app.meridiancpd.co.uk/buy/MER-ALL-022", "on: course link");
assert(t.co.buyLink(SINGLE, "MER-DEA-001", "MERIDIAN10") === "https://app.meridiancpd.co.uk/buy/MER-DEA-001?code=MERIDIAN10", "on: promo");
assert(t.co.buyLink(SERIES, "FW-HEATING", "") === "https://app.meridiancpd.co.uk/buy/FW-HEATING", "on: series link");
assert(t.links[0].attrs.href === "https://app.meridiancpd.co.uk/buy/MER-DEA-004", "on: home page course button rewritten");
assert(t.links[1].attrs.href === "https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01", "on: annual left alone");

// consent.js: the click handler reads /buy links as a course or series checkout
const consent = fs.readFileSync(path.join(site, "consent.js"), "utf8");
assert(/var buy = href\.match\(\/app\\\.meridiancpd\\\.co\\\.uk\\\/buy\\\/\(\[\\w-\]\+\)\/\);/.test(consent), "consent.js matches /buy links");
assert(consent.indexOf('href.indexOf("buy.stripe.com") >= 0 || buy') >= 0 && consent.indexOf("|| buy;") >= 0, "consent.js uses the /buy id");
console.log("checkout.js off and on, consent.js /buy");
