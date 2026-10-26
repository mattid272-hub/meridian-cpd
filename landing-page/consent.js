/* Meridian CPD: the cookie choice and the Meta Pixel.
 *
 * Nothing loads from Meta until the visitor presses Accept. Reject loads nothing and clears Meta's cookies.
 * PIXEL_ID is the Meta dataset "Meridian CPD" in the Meridian CPD business portfolio. Leave it empty and this
 * file does nothing at all: no banner, no pixel, no "Cookie settings" link.
 *
 * Events sent (only after Accept): PageView; ViewContent when a course is opened on courses.html;
 * InitiateCheckout when a Stripe payment link is clicked; Contact when the email address is tapped.
 * autoConfig is off, so the pixel never reads what people type. Purchases are confirmed by Stripe, not here.
 */
(function () {
  "use strict";
  var PIXEL_ID = "";
  // Prices sent with InitiateCheckout. Update with the price rise on 1 January 2027 (annual to £99).
  var ANNUAL_LINK = "fZufZgbse3BpcXE7TY73G01", ANNUAL_PRICE = 79, COURSE_PRICE = 19.99;
  if (!PIXEL_ID) return;

  var KEY = "meridian-cookie-consent";
  var read = function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
  var save = function (v) { try { localStorage.setItem(KEY, v); } catch (e) {} };
  var on = false;

  function loadPixel() {
    if (on) return;
    on = true;
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    window.fbq("set", "autoConfig", false, PIXEL_ID);
    window.fbq("init", PIXEL_ID);
    window.fbq("track", "PageView");
  }
  function dropPixel() {
    if (window.fbq) window.fbq("consent", "revoke");
    on = false;
    var host = location.hostname.replace(/^www\./, "");
    ["_fbp", "_fbc"].forEach(function (c) { ["", "; domain=." + host, "; domain=" + location.hostname].forEach(function (d) { document.cookie = c + "=; Max-Age=0; path=/" + d; }); });
  }
  var track = function (name, params) { if (on && window.fbq) window.fbq("track", name, params || {}); };

  // The banner. Accept and Reject look the same.
  var css = ".mcpd-cookie{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#0D1F0E;color:#F5F5F0;border-top:1px solid #2a3d2b;box-shadow:0 -6px 24px rgba(0,0,0,.25);font-family:'DM Sans',Arial,sans-serif;font-size:15px;line-height:1.5}" +
    ".mcpd-cookie[hidden]{display:none}" +
    ".mcpd-cookie-in{max-width:1200px;margin:0 auto;padding:16px 5vw;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 24px}" +
    ".mcpd-cookie p{margin:0;max-width:70ch;color:#F5F5F0}" +
    ".mcpd-cookie a{color:#F5F5F0;text-decoration:underline}" +
    ".mcpd-cookie-btns{display:flex;gap:12px}" +
    ".mcpd-cookie button{font:inherit;font-weight:700;background:#D4FF00;color:#0D1F0E;border:0;border-radius:4px;padding:11px 20px;min-width:110px;cursor:pointer}" +
    ".mcpd-cookie button:hover{background:#C0F000}" +
    ".mcpd-cookie button:focus-visible,.mcpd-cookie a:focus-visible{outline:2px solid #D4FF00;outline-offset:3px}";
  var style = document.createElement("style"); style.textContent = css; document.head.appendChild(style);
  var banner = document.createElement("div");
  banner.className = "mcpd-cookie"; banner.setAttribute("role", "region"); banner.setAttribute("aria-label", "Cookie choice"); banner.hidden = true;
  banner.innerHTML = '<div class="mcpd-cookie-in"><p>Can we use Meta\'s advertising cookie to see which of our Facebook and Instagram adverts work? Nothing is set unless you accept. <a href="/privacy.html#cookies">How it is used</a>.</p>' +
    '<div class="mcpd-cookie-btns"><button type="button" data-consent="yes">Accept</button><button type="button" data-consent="no">Reject</button></div></div>';
  document.body.appendChild(banner);
  banner.addEventListener("click", function (e) {
    var b = e.target.closest("[data-consent]"); if (!b) return;
    var v = b.getAttribute("data-consent"); save(v); banner.hidden = true;
    if (v === "yes") loadPixel(); else dropPixel();
  });

  // "Cookie settings" next to the Privacy link in the footer
  var privacy = document.querySelector('footer a[href="privacy.html"], footer a[href="/privacy.html"]');
  if (privacy) {
    var link = document.createElement("a"); link.href = "/privacy.html#cookies"; link.textContent = "Cookie settings";
    link.addEventListener("click", function (e) { e.preventDefault(); banner.hidden = false; banner.querySelector("button").focus(); });
    if (privacy.parentNode && privacy.parentNode.tagName === "LI") { var li = document.createElement("li"); li.appendChild(link); privacy.parentNode.parentNode.insertBefore(li, privacy.parentNode.nextSibling); }
    else { privacy.parentNode.insertBefore(link, privacy.nextSibling); privacy.parentNode.insertBefore(document.createTextNode(" "), link); }
  }

  var choice = read();
  if (choice === "yes") loadPixel(); else if (choice !== "no") banner.hidden = false;

  // Payment link clicks and email taps
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]"); if (!a) return;
    var href = a.getAttribute("href");
    if (href.indexOf("buy.stripe.com") >= 0) {
      var annual = href.indexOf(ANNUAL_LINK) >= 0;
      var m = href.match(/client_reference_id=([\w-]+)/);
      var p = { currency: "GBP", value: annual ? ANNUAL_PRICE : COURSE_PRICE, content_name: annual ? "annual" : "course" };
      if (m) { p.content_ids = [m[1]]; p.content_type = "product"; }
      track("InitiateCheckout", p);
    } else if (href.indexOf("mailto:") === 0) {
      track("Contact", { content_name: "email" });
    }
  });
  // A course opened on courses.html
  if (typeof window.openModal === "function") {
    var open = window.openModal;
    window.openModal = function (id) { track("ViewContent", { content_ids: [id], content_type: "product" }); return open.apply(this, arguments); };
  }
})();
