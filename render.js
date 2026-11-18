// Screenshot page.html into a 1024x1024 PNG with headless Chromium (Playwright).
// Run from ~/workspace/custom-skills/playwright-skill/ with NODE_PATH set, e.g.:
//   node render.js /abs/path/page.html /abs/path/entry.png
// Renders straight to the output path given — no intermediate /tmp copy.
const { chromium } = require('playwright');

(async () => {
  const pageFile = process.argv[2];
  const pngFile = process.argv[3];
  if (!pageFile || !pngFile) {
    console.error('usage: node render.js <page.html> <out.png>');
    process.exit(2);
  }
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: 1 });
    await page.goto('file://' + pageFile);
    await page.waitForTimeout(400);
    await page.screenshot({ path: pngFile });
    console.log('wrote', pngFile);
  } finally {
    await browser.close();
  }
})();
