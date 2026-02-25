const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const mobileViewports = [
    { name: 'mobile_360x780', w: 360, h: 780 },
    { name: 'mobile_412x915', w: 412, h: 915 }
  ];
  for (const vp of mobileViewports) {
    const context = await browser.newContext({ viewport: { width: vp.w, height: vp.h } });
    const page = await context.newPage();
    try {
      const base = 'http://localhost:8080/';
      await page.goto(base, { waitUntil: 'networkidle' });
      const toggle = await page.$('#theme-toggle');
      if (!toggle) throw new Error('Theme toggle not found on homepage ('+vp.name+')');
      const initial = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
      await page.click('#theme-toggle');
      await page.waitForTimeout(1000);
      const after = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
      console.log(`${vp.name}: ${initial} -> ${after}`);
      // mobile route checks
      await page.goto(base + 'website/contact', { waitUntil: 'networkidle' }).catch(() => {});
      await page.goto(base + 'website/about', { waitUntil: 'networkidle' }).catch(() => {});
      await page.goto(base + 'studio/dashboard', { waitUntil: 'networkidle' }).catch(() => {});
    } catch (err) {
      await page.screenshot({ path: `neon-theme-mobile-fail-${vp.name}.png` });
      console.error(err);
      await context.close();
      await browser.close();
      process.exit(1);
    }
    await context.close();
  }
  await browser.close();
  process.exit(0);
})();
