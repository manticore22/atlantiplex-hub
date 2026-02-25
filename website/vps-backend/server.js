// Minimal Express server for Stripe Checkout and Lore CMS
const express = require('express');
const path = require('path');
const fs = require('fs');
const bodyParser = require('body-parser');
const stripeLib = require('stripe');

const app = express();
const fs = require('fs');
const path = require('path');
const stripeLib = require('stripe');
const bodyParser = require('body-parser');
const stripeSecret = process.env.STRIPE_SECRET || '';
const stripe = stripeSecret ? stripeLib(stripeSecret) : null;
const port = process.env.PORT || 3000;
const STRIPE_SECRET = process.env.STRIPE_SECRET || '';
const stripe = STRIPE_SECRET ? stripeLib(STRIPE_SECRET) : null;

// Support raw body for webhook verification when needed
app.use(bodyParser.json());

// Helper to load products
function loadProducts(){
  const p = path.join(__dirname, 'products.json');
  if (!fs.existsSync(p)) return [];
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

// In-memory simple subscriptions store (replace with proper DB for production)
let subscriptionsStore = {};
const subsPath = path.join(__dirname, 'subscriptions.json');
if (fs.existsSync(subsPath)) {
  try { subscriptionsStore = JSON.parse(fs.readFileSync(subsPath, 'utf8')); } catch { subscriptionsStore = {}; }
}
function saveSubs(){
  fs.writeFileSync(subsPath, JSON.stringify(subscriptionsStore, null, 2));
}
app.use('/static', express.static(path.join(__dirname, 'static')));

// Simple lore rendering from JSON
app.get('/lore', (req, res) => {
  const lorePath = path.join(__dirname, 'lore-content.json');
  if (!fs.existsSync(lorePath)) return res.status(500).send('Lore not available');
  const data = JSON.parse(fs.readFileSync(lorePath, 'utf-8'));
  let html = `<h1>Lore</h1>`;
  data.sections?.forEach(s => {
    html += `<section><h2>${s.title}</h2><p>${s.body}</p></section>`;
  });
  res.send(`<!doctype html><html><body>${html}</body></html>`);
});

// Prices endpoint for frontend to fetch available services
app.get('/prices', (req, res) => {
  const products = loadProducts();
  const response = products.map(p => ({ id: p.id, name: p.name, description: p.description, price: p.price, interval: p.interval, priceId: p.priceId }));
  res.json(response);
});

// Create checkout session for subscriptions
app.post('/create-checkout-session', async (req, res) => {
  // Support both paid (Stripe) and free-tier (no charge) paths
  const priceIds = req.body.priceIds && Array.isArray(req.body.priceIds) ? req.body.priceIds : (req.body.priceId ? [req.body.priceId] : []);
  const customer_email = req.body.customer_email;
  if (priceIds.length === 0) return res.status(400).json({ error: 'priceId(s) required' });

  const products = loadProducts();
  const hasFree = priceIds.find(pid => {
    const p = products.find(pp => pp.priceId === pid);
    return p && p.free;
  });
  // Handle free items
  if (hasFree) {
    // grant free access for each free priceId
    const entitlements = subscriptionsStore[customer_email] || [];
    priceIds.forEach(pid => {
      const p = products.find(pp => pp.priceId === pid);
      if (p && p.free) {
        entitlements.push({ sessionId: 'FREE-' + Date.now() + '-' + pid, priceId: pid, status: 'active', type: 'free' });
      }
    });
    subscriptionsStore[customer_email] = entitlements;
    saveSubs();
    return res.json({ id: 'FREE-' + Date.now(), free: true, next: '/account?email=' + encodeURIComponent(customer_email) });
  }

  // Paid items path
  if (!stripe) return res.status(500).json({ error: 'Stripe not configured' });
  try {
    const lineItems = priceIds.map(id => ({ price: id, quantity: 1 }));
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      line_items: lineItems,
      customer_email,
      success_url: 'https://verilysovereign.org/stripe-success?session_id={CHECKOUT_SESSION_ID}',
      cancel_url: 'https://verilysovereign.org/stripe-cancel',
    });
    res.json({ id: session.id, url: session.url });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Unable to create checkout session' });
  }
});

// Account portal-ish endpoint
app.get('/account', (req, res) => {
  const email = req.query.email || '';
  const entitlements = subscriptionsStore[email] || [];
  res.json({ email, entitlements });
});

// Webhook endpoint (basic)
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const body = req.body;
  // In production, verify signature with Stripe webhook secret
  // const sig = req.headers['stripe-signature'];
  // let event;
  // try { event = stripe.webhooks.constructEvent(body, sig, endpointSecret); } catch (err) { return res.status(400).send(`Webhook Error: ${err.message}`); }
  // Simple handling
  try {
    const evt = JSON.parse(body.toString());
    if (evt.type === 'checkout.session.completed' && evt.data.object && evt.data.object.mode === 'subscription') {
      const session = evt.data.object;
      const customerEmail = session.customer_details?.email || '';
      const priceId = session.display_items?.data?.[0]?.price?.id || (session.line_items?.data?.[0]?.price?.id);
      // Store access by email if possible
      if (customerEmail) {
        subscriptionsStore[customerEmail] = subscriptionsStore[customerEmail] || [];
        subscriptionsStore[customerEmail].push({ sessionId: session.id, priceId, status: 'active' });
        saveSubs();
      }
    }
  } catch (e) {
    // ignore parse errors
  }
  res.json({ received: true });
});

app.get('/', (req, res) => {
  res.send('<h1>Verily Sovereign - Stripe Backend</h1>');
});

// Lore content as JSON for CMS-like access
app.get('/lore-content', (req, res) => {
  const jsonPath = path.join(__dirname, 'lore-content.json');
  if (!fs.existsSync(jsonPath)) return res.status(404).json({ error: 'Lore content not found' });
  res.type('application/json');
  res.send(fs.readFileSync(jsonPath, 'utf-8'));
});

// Checkout session creation (Stripe Checkout)
app.post('/create-checkout-session', async (req, res) => {
  if (!stripe) return res.status(500).send('Stripe not configured');
  const { priceId } = req.body; // priceId should be a Stripe price id you set up
  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      mode: 'payment',
      success_url: 'https://verilysovereign.org/success',
      cancel_url: 'https://verilysovereign.org/cancel',
    });
    res.json({ id: session.id });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Unable to create checkout session' });
  }
});

app.get('/', (req, res) => {
  res.send('<h1>Verily Sovereign - Stripe Backend</h1><p>Backend for checkout + lore CMS</p>');
});

app.listen(port, () => {
  console.log(`vps-backend listening on port ${port}`);
});
