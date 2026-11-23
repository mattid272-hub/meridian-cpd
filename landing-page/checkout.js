// Where the site's £19.99 course and £39.99 series buy buttons go. One switch for every page.
//
// viaApp false (today): straight to the Stripe Payment Link, with the course or series id
// as client_reference_id, as before.
// viaApp true: to https://app.meridiancpd.co.uk/buy/<id>, which opens a Stripe checkout on the
// same price with the course or series named above the Pay button (webhook/main.py, /buy).
// Turn it on only after CHECKOUT_SESSIONS=on is set in Railway and /buy/MER-DEA-001 has been
// tried in a browser. The annual subscription buttons are never changed here.
(function () {
  var VIA_APP = false;
  var APP = "https://app.meridiancpd.co.uk";
  var SINGLE = "https://buy.stripe.com/9B6bJ0bsefk72j02zE73G00";
  var SERIES = "https://buy.stripe.com/7sYaEWfIu8VJ7Dkdei73G02";

  function appLink(id, code) {
    return APP + "/buy/" + encodeURIComponent(id) + (code ? "?code=" + encodeURIComponent(code) : "");
  }
  // A Payment Link for one course or one series, as the app link when switched on.
  function buyLink(paymentLink, id, code) {
    if (VIA_APP) return appLink(id, code);
    var p = new URLSearchParams({ client_reference_id: id });
    if (code) p.set("prefilled_promo_code", code);
    return paymentLink + "?" + p.toString();
  }
  // Fixed buttons in the page (the home page course cards): rewrite them once the page is read.
  function rewriteStatic() {
    if (!VIA_APP) return;
    var links = document.querySelectorAll('a[href^="' + SINGLE + '?"], a[href^="' + SERIES + '?"]');
    Array.prototype.forEach.call(links, function (a) {
      var q = new URLSearchParams(a.getAttribute("href").split("?")[1] || "");
      var id = q.get("client_reference_id");
      if (id) a.setAttribute("href", appLink(id, q.get("prefilled_promo_code") || ""));
    });
  }
  window.MeridianCheckout = { viaApp: VIA_APP, single: SINGLE, series: SERIES, buyLink: buyLink };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", rewriteStatic);
  else rewriteStatic();
})();
