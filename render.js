// Render page.html to entry.png at 1024x1024 (Playwright/Chromium, headless).
// Run from ~/workspace/custom-skills/playwright-skill/ with NODE_PATH set.
// Usage: node render.js /path/to/page.html /path/to/out.png
const { chromium } = require('playwright');

(async () => {
  const [pagePath, outPath] = process.argv.slice(2);
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: 1 });
    await page.goto('file://' + pagePath);
    await page.waitForTimeout(400);
    await page.screenshot({ path: outPath });
    console.log('wrote', outPath);
  } finally {
    await browser.close();
  }
})();
