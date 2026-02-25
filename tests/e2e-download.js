const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const url = 'http://localhost:8080/downloads/sample-app-v1.txt';
  const resp = await page.goto(url, { waitUntil: 'networkidle' }).catch(() => null);
  if (!resp || resp.status() !== 200) {
    console.error('Download URL failed or not 200');
    process.exit(1);
  }
  console.log('Download URL returned', resp.status());
  await browser.close();
  process.exit(0);
})();
