const puppeteer = require('puppeteer');

(async () => {
  const base = 'http://verilysovereign.online';
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto(base, { waitUntil: 'networkidle2' });

  // Ensure Neon theme toggle exists
  const hasToggle = await page.$('#theme-toggle') !== null;
  if (!hasToggle) {
    console.error('Neon theme toggle not found on homepage');
    process.exit(1);
  }

  // Read initial theme
  let initialTheme = await page.evaluate(() => {
    return document.documentElement.getAttribute('data-theme');
  });

  // Click to switch theme
  await page.click('#theme-toggle');
  await page.waitForTimeout(800);

  // Verify theme toggled
  let newTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  if (newTheme !== 'neon' && initialTheme !== 'neon') {
    console.warn('Theme did not switch to neon as expected. Current:', newTheme);
  } else {
    console.log('Theme switched to', newTheme);
  }

  await browser.close();
})();
