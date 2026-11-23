/* Meridian CPD: the cookie choice, the Meta Pixel and its server copy.
 *
 * Nothing loads from Meta and nothing is sent to our server's Meta endpoint until the visitor presses Accept.
 * Reject loads nothing and clears Meta's cookies.
 * PIXEL_ID is the Meta dataset "Meridian CPD" in the Meridian CPD business portfolio. The app's pages load this
 * file with data-pixel set from its META_PIXEL_ID variable; without a pixel id this file does nothing at all:
 * no banner, no pixel, no "Cookie settings" link.
 *
 * The choice is kept in the cookie mcpd_consent ("yes" or "no") on .meridiancpd.co.uk, so one choice covers the
 * site and the app (app.meridiancpd.co.uk), and the app's server can read it. That cookie only records the choice.
 *
 * Events sent (only after Accept): PageView; ViewContent when a course is opened on courses.html (with its series);
 * InitiateCheckout when a Stripe payment link is clicked; Contact when the email address is tapped. Each one is
 * fired in the browser with an eventID and posted with the same id to the app (/meta/event), which sends it to
 * Meta's Conversions API; Meta keeps one of the two. Free-course orders (Lead) and purchases are sent by the app's
 * server from /thanks, not from here. autoConfig is off, so the pixel never reads what people type.
 */
(function () {
  "use strict";
  var me = document.currentScript;
  var attr = function (n) { return me && me.getAttribute(n); };
  var PIXEL_ID = attr("data-pixel") || "1133939432819396";
  var CAPI = attr("data-capi") || "https://app.meridiancpd.co.uk/meta/event";
  var PRIVACY = "https://meridiancpd.co.uk/privacy.html#cookies";
  // Prices sent with InitiateCheckout. Update with the price rise on 1 January 2027 (annual to £99).
  var ANNUAL_LINK = "fZufZgbse3BpcXE7TY73G01", ANNUAL_PRICE = 79;
  var SERIES_LINK = "7sYaEWfIu8VJ7Dkdei73G02", SERIES_PRICE = 39.99, COURSE_PRICE = 19.99;
  if (!/^\d+$/.test(PIXEL_ID)) return;

  var NAME = "mcpd_consent", OLD_KEY = "meridian-cookie-consent", DAYS = 180;
  var host = location.hostname.replace(/^www\./, "");
  var base = /(^|\.)meridiancpd\.co\.uk$/.test(host) ? "meridiancpd.co.uk" : "";
  var read = function () {
    var m = document.cookie.match(/(?:^|;\s*)mcpd_consent=(yes|no)/);
    if (m) return m[1];
    try { var v = localStorage.getItem(OLD_KEY); if (v === "yes" || v === "no") { save(v); return v; } } catch (e) {}
    return null;
  };
  var save = function (v) {
    document.cookie = NAME + "=" + v + "; Max-Age=" + DAYS * 86400 + "; path=/; SameSite=Lax" +
      (location.protocol === "https:" ? "; Secure" : "") + (base ? "; domain=." + base : "");
    try { localStorage.removeItem(OLD_KEY); } catch (e) {}
  };
  var on = false;

  var newId = function () {
    var a = new Uint8Array(12);
    (window.crypto || window.msCrypto).getRandomValues(a);
    return Array.prototype.map.call(a, function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
  };
  // The server copy of a browser event, with the same id so Meta counts it once.
  var beacon = function (name, id, params) {
    var body = JSON.stringify({ event_name: name, event_id: id, event_source_url: location.origin + location.pathname, custom_data: params || {} });
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(CAPI, body)) return;
      fetch(CAPI, { method: "POST", body: body, credentials: "include", keepalive: true, mode: "no-cors" });
    } catch (e) {}
  };
  var track = function (name, params) {
    if (!on || !window.fbq) return;
    var id = newId();
    window.fbq("track", name, params || {}, { eventID: id });
    beacon(name, id, params);
  };

  function loadPixel() {
    if (on) return;
    on = true;
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    window.fbq("consent", "grant");
    window.fbq("set", "autoConfig", false, PIXEL_ID);
    window.fbq("init", PIXEL_ID);
    track("PageView");
  }
  function dropPixel() {
    if (window.fbq) window.fbq("consent", "revoke");
    on = false;
    var domains = ["", "; domain=" + location.hostname, "; domain=." + host];
    if (base) domains.push("; domain=." + base, "; domain=" + base);
    ["_fbp", "_fbc"].forEach(function (c) { domains.forEach(function (d) { document.cookie = c + "=; Max-Age=0; path=/" + d; }); });
  }

  // The banner. Accept and Reject look the same.
  var css = ".mcpd-cookie{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#0D1F0E;color:#F5F5F0;border-top:1px solid #2a3d2b;box-shadow:0 -6px 24px rgba(0,0,0,.25);font-family:'DM Sans',Arial,sans-serif;font-size:15px;line-height:1.5}" +
    ".mcpd-cookie[hidden]{display:none}" +
    ".mcpd-cookie-in{max-width:1200px;margin:0 auto;padding:16px 5vw;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 24px}" +
    ".mcpd-cookie p{margin:0;max-width:70ch;color:#F5F5F0}" +
    ".mcpd-cookie a{color:#F5F5F0;text-decoration:underline}" +
    ".mcpd-cookie-btns{display:flex;gap:12px}" +
    ".mcpd-cookie button{font:inherit;font-weight:700;background:#D4FF00;color:#0D1F0E;border:0;border-radius:4px;padding:11px 20px;min-width:110px;cursor:pointer;margin:0;width:auto}" +
    ".mcpd-cookie button:hover{background:#C0F000}" +
    ".mcpd-cookie button:focus-visible,.mcpd-cookie a:focus-visible{outline:2px solid #D4FF00;outline-offset:3px}";
  var style = document.createElement("style"); style.textContent = css; document.head.appendChild(style);
  var banner = document.createElement("div");
  banner.className = "mcpd-cookie"; banner.setAttribute("role", "region"); banner.setAttribute("aria-label", "Cookie choice"); banner.hidden = true;
  banner.innerHTML = '<div class="mcpd-cookie-in"><p>With your permission we use Meta\'s advertising cookie (_fbp) to see which of our Facebook and Instagram adverts work. Our server also tells Meta about your visit, and about an order if you make one. Nothing from Meta is set or sent unless you accept. <a href="' + PRIVACY + '">How it is used</a>.</p>' +
    '<div class="mcpd-cookie-btns"><button type="button" data-consent="yes">Accept</button><button type="button" data-consent="no">Reject</button></div></div>';
  document.body.appendChild(banner);
  var show = function () { banner.hidden = false; banner.querySelector("button").focus(); };
  banner.addEventListener("click", function (e) {
    var b = e.target.closest("[data-consent]"); if (!b) return;
    var v = b.getAttribute("data-consent"); save(v); banner.hidden = true;
    if (v === "yes") loadPixel(); else dropPixel();
  });

  // "Cookie settings" next to the Privacy link in the footer, and on anything marked data-cookie-settings
  var privacy = document.querySelector('footer a[href="privacy.html"], footer a[href="/privacy.html"]');
  if (privacy) {
    var link = document.createElement("a"); link.href = PRIVACY; link.textContent = "Cookie settings"; link.setAttribute("data-cookie-settings", "");
    if (privacy.parentNode && privacy.parentNode.tagName === "LI") { var li = document.createElement("li"); li.appendChild(link); privacy.parentNode.parentNode.insertBefore(li, privacy.parentNode.nextSibling); }
    else { privacy.parentNode.insertBefore(link, privacy.nextSibling); privacy.parentNode.insertBefore(document.createTextNode(" "), link); }
  }
  document.addEventListener("click", function (e) {
    var s = e.target.closest && e.target.closest("[data-cookie-settings]"); if (!s) return;
    e.preventDefault(); show();
  });

  var choice = read();
  if (choice === "yes") loadPixel(); else if (choice !== "no") banner.hidden = false;
  // Arriving from a "Cookie settings" link on a page that does not load this file (unsubscribe.html)
  if (location.hash === "#cookie-settings") show();

  // Payment link clicks and email taps
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]"); if (!a) return;
    var href = a.getAttribute("href");
    // A Payment Link, or the app's /buy/<id> link that checkout.js uses when it is switched on
    var buy = href.match(/app\.meridiancpd\.co\.uk\/buy\/([\w-]+)/);
    if (href.indexOf("buy.stripe.com") >= 0 || buy) {
      var annual = href.indexOf(ANNUAL_LINK) >= 0, series = href.indexOf(SERIES_LINK) >= 0 || !!(buy && /^FW-/i.test(buy[1]));
      var m = href.match(/client_reference_id=([\w-]+)/) || buy;
      var p = { currency: "GBP", value: annual ? ANNUAL_PRICE : series ? SERIES_PRICE : COURSE_PRICE,
                content_name: annual ? "subscription" : series ? "series" : "course" };
      if (m) { p.content_ids = [m[1]]; p.content_type = "product"; }
      track("InitiateCheckout", p);
    } else if (href.indexOf("mailto:") === 0) {
      track("Contact", { content_name: "email" });
    }
  });
  // A course opened on courses.html, with the series it belongs to
  if (typeof window.openModal === "function") {
    var open = window.openModal;
    window.openModal = function (id) {
      var p = { content_ids: [id], content_type: "product" };
      try { var c = (typeof COURSES !== "undefined") && COURSES.find(function (x) { return x.id === id; }); if (c && c.series) p.content_category = c.series; } catch (e) {}
      track("ViewContent", p);
      return open.apply(this, arguments);
    };
  }
})();
