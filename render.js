// Renders page.html (the 1024x1024 newspaper front page) to entry.png
// with headless Chromium, via the playwright skill's runner.
// (CommonJS so `playwright` resolves through the runner's NODE_PATH.)
const { chromium } = require('playwright');
const { join } = require('node:path');

(async () => {
  const dir = __dirname;
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: 1 });
    await page.goto('file://' + join(dir, 'page.html'));
    await page.waitForTimeout(400);
    await page.screenshot({ path: join(dir, 'entry.png') });
    console.log('wrote', join(dir, 'entry.png'));
  } finally {
    await browser.close();
  }
})();
