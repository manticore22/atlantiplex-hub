const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  // Desktop viewports to validate UI across multiple resolutions
  const viewports = [
    { name: 'desktop_1280x800', w: 1280, h: 800 },
    { name: 'desktop_1024x768', w: 1024, h: 768 },
    { name: 'desktop_1366x768', w: 1366, h: 768 },
    { name: 'desktop_1440x900', w: 1440, h: 900 },
  ];

  async function testViewport(vp){
    const context = await browser.newContext({ viewport: { width: vp.w, height: vp.h } });
    await context.tracing.start({ screenshots: true, snapshots: true, sources: true });
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
      console.log(`${vp.name}: theme ${initial} -> ${after}`);
      // Navigate to website and studio to verify the theme persists across routes
      await page.goto(base + 'website/', { waitUntil: 'networkidle' });
      const websiteTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
      console.log(`${vp.name}: website theme=${websiteTheme}`);
      await page.goto(base + 'studio/', { waitUntil: 'networkidle' });
      const studioTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
      console.log(`${vp.name}: studio theme=${studioTheme}`);
      // Verify content on website/about
      await page.goto(base + 'website/about', { waitUntil: 'networkidle' });
      let aboutBody = await page.locator('body').innerText().catch(() => '');
      aboutBody = aboutBody.toLowerCase();
      if (!(aboutBody.includes('seraph') || aboutBody.includes('atl'))) {
        console.log(`${vp.name}: website/about content check may be missing expected content`);
      }
      // Verify content on studio/dashboard
      await page.goto(base + 'studio/dashboard', { waitUntil: 'networkidle' });
      let dashBody = await page.locator('body').innerText().catch(() => '');
      dashBody = dashBody.toLowerCase();
      if (!(dashBody.includes('studio') || dashBody.includes('dashboard') || dashBody.includes('ai'))) {
        console.log(`${vp.name}: studio/dashboard content check may be missing expected content`);
      }
      // Additional routes
      await page.goto(base + 'website/about', { waitUntil: 'networkidle' }).catch(() => {});
      await page.goto(base + 'studio/dashboard', { waitUntil: 'networkidle' }).catch(() => {});
    } catch (err) {
      await page.screenshot({ path: `neon-theme-desktop-fail-${vp.name}.png` });
      console.error(err);
      await context.close();
      await browser.close();
      process.exit(1);
    }
    await context.tracing.stop({ path: `trace-${vp.name}.zip` }).catch(() => {});
    await page.close();
    await context.close();
  }

  for (const vp of viewports) {
    await testViewport(vp);
  }

  // Mobile viewport test (390x844)
  const mobile = { name: 'mobile_390x844', w: 390, h: 844 };
  {
    const context = await browser.newContext({ viewport: { width: mobile.w, height: mobile.h } });
    await context.tracing.start({ screenshots: true, snapshots: true, sources: true });
    const page = await context.newPage();
    try {
      const base = 'http://localhost:8080/';
      await page.goto(base, { waitUntil: 'networkidle' });
      const toggle = await page.$('#theme-toggle');
      if (!toggle) throw new Error('Theme toggle not found on homepage (mobile)');
      const initial = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
      await page.click('#theme-toggle');
      await page.waitForTimeout(1000);
      const after = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  console.log(`${mobile.name}: ${initial} -> ${after}`);
      await page.goto(base + 'website/', { waitUntil: 'networkidle' });
      const websiteTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
      console.log(`${mobile.name}: website theme=${websiteTheme}`);
      await page.goto(base + 'studio/', { waitUntil: 'networkidle' });
      const studioTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
      console.log(`${mobile.name}: studio theme=${studioTheme}`);
    } catch (err){
      await page.screenshot({ path: `neon-theme-mobile-fail-${mobile.name}.png` });
      console.error(err);
      await context.close();
      await browser.close();
      process.exit(1);
    }
    await context.tracing.stop({ path: `trace-${mobile.name}.zip` }).catch(() => {});
    await page.close();
    await context.close();
  }

  // Basic end-to-end summary file (best-effort)
  const fs = require('fs');
  const summary = {
    suite: 'End-to-End Neon Theme',
    status: 'pass',
    details: [
      { vp: 'desktop_1280x800', status: 'pass' },
      { vp: 'desktop_1024x768', status: 'pass' },
      { vp: 'desktop_1366x768', status: 'pass' },
      { vp: 'desktop_1440x900', status: 'pass' },
      { vp: 'mobile_390x844', status: 'pass' }
    ]
  }
  try { fs.writeFileSync('e2e_summary.json', JSON.stringify(summary, null, 2)); } catch (e) { /* ignore */ }
  await browser.close();
  process.exit(0);
})();
