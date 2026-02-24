#!/usr/bin/env node
// Minimal interactive launcher for Stripe API keys
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const envPath = path.resolve(__dirname, '../.env');
const existing = fs.existsSync(envPath) ? fs.readFileSync(envPath, 'utf8') : '';

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

function ask(q) {
  return new Promise(resolve => rl.question(q, ans => resolve(ans)));
}

async function main(){
  console.log('\nSeraphonix Backend: Stripe keys launcher');
  let currentSecret = /STRIPE_SECRET=([\S]+)/.exec(existing)?.[1] ?? '';
  let currentWebhook = /STRIPE_WEBHOOK_SECRET=([\S]+)/.exec(existing)?.[1] ?? '';
  // Prompt for keys; if empty, keep existing
  const stripeSecret = await ask(`Enter Stripe Secret Key [${currentSecret || 'none'}]: `) || currentSecret;
  const stripeWebhook = await ask(`Enter Stripe Webhook Secret [${currentWebhook || 'none'}]: `) || currentWebhook;
  const frontendUrl = await ask(`Frontend URL (${process.env.FRONTEND_URL || 'https://verilysovereign.org'}): `) || process.env.FRONTEND_URL || 'https://verilysovereign.org';

  const lines = [
    `JWT_SECRET=${process.env.JWT_SECRET || 'seraphonix-secret-key'}`,
    `FRONTEND_URL=${frontendUrl}`,
    stripeSecret ? `STRIPE_SECRET=${stripeSecret}` : '',
    stripeWebhook ? `STRIPE_WEBHOOK_SECRET=${stripeWebhook}` : '',
    `ATLANTIPLEX_SECRET=`,
    `DATABASE_URL=sqlite:///seraphonix.db`,
  ];
  const out = lines.filter(l => l.trim() !== '').join('\n') + '\n';
  fs.writeFileSync(envPath, out);
  console.log('\nWrote environment to', envPath);
  console.log('You may need to restart services to apply new keys.');
  rl.close();
}

main();
