// Renders the mock screens to PNG with Playwright (deviceScaleFactor 2).
// Usage: node mock/series-packaging/shoot.js [fontCacheDir]
// fontCacheDir (optional) holds fonts.css and the woff2 files from Google Fonts, for
// machines where the browser cannot reach fonts.googleapis.com directly.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const out = path.join(dir, 'screens');
const fontDir = process.argv[2];
const pages = [
  ['1-dashboard', 'dashboard.html'],
  ['2-series', 'series.html'],
  ['3a-course-completion', 'course.html'],
  ['3b-course-certificate-issued', 'course.html?state=issued'],
  ['4-my-certificates', 'certificates.html'],
  ['5-public-courses', 'courses.html'],
];
const sizes = [['desktop', 1440, 900], ['phone', 390, 844]];
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  for (const [label, w, h] of sizes) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: label === 'phone', hasTouch: label === 'phone' });
    if (fontDir) {
      await ctx.route(/fonts\.(googleapis|gstatic)\.com/, route => {
        const u = new URL(route.request().url());
        if (u.hostname === 'fonts.googleapis.com') {
          const css = fs.readFileSync(path.join(fontDir, 'fonts.css'), 'utf8');
          return route.fulfill({ contentType: 'text/css', body: css });
        }
        const f = path.join(fontDir, u.pathname.slice(1).replace(/\//g, '_'));
        return fs.existsSync(f) ? route.fulfill({ contentType: 'font/woff2', body: fs.readFileSync(f) }) : route.abort();
      });
    }
    for (const [name, file] of pages) {
      const page = await ctx.newPage();
      await page.goto('file://' + path.join(dir, file.split('?')[0]) + (file.includes('?') ? '?' + file.split('?')[1] : ''));
      await page.evaluate(() => document.fonts.ready);
      // A full-page shot would leave the fixed phone tab bar mid-page; pin it to the end.
      await page.addStyleTag({ content: 'body{position:relative}.tabbar{position:absolute!important}' });
      await page.waitForTimeout(300);
      const p = path.join(out, `${name}-${label}.png`);
      await page.screenshot({ path: p, fullPage: true });
      console.log(p);
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
})();
