// Stage display server with basic signaling (socket.io)
// Serves the stage_display.html on a dedicated port (default 9001)
require('dotenv').config();
const express = require('express');
const http = require('http');
const path = require('path');
const jwt = require('jsonwebtoken');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const app = express();
const { Issuer } = require('openid-client');
const crypto = require('crypto');
const OIDC_ISSUER = process.env.OIDC_ISSUER;
const OIDC_CLIENT_ID = process.env.OIDC_CLIENT_ID;
const OIDC_CLIENT_SECRET = process.env.OIDC_CLIENT_SECRET;
let oidcClient = null;
const oidcSessions = new Map();
const port = process.env.STAGE_PORT ? parseInt(process.env.STAGE_PORT, 10) : 9001;
const JWT_SECRET = process.env.JWT_SECRET || 'atlantiplex-secret';
// Simple in-memory user store (demo); replace with real auth in production
const USERS = {
  alice: 'password123',
  bob: 'letmein',
  admin: 'admin123', // Admin user
};

// Admin middleware
const requireAdmin = (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    if (decoded.username !== 'admin') {
      return res.status(403).json({ error: 'Admin access required' });
    }
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Mock data for demo
let mockUsers = [
  { id: 1, username: 'alice', email: 'alice@example.com', plan: 'Free', joinDate: '2024-01-15', lastActive: '2024-02-05', totalSpent: 0 },
  { id: 2, username: 'bob', email: 'bob@example.com', plan: 'Pro', joinDate: '2024-01-20', lastActive: '2024-02-04', totalSpent: 29.99 },
  { id: 3, username: 'charlie', email: 'charlie@example.com', plan: 'Enterprise', joinDate: '2024-01-10', lastActive: '2024-02-05', totalSpent: 99.99 },
];

// Serve static assets from the shared static folder
app.use('/static', express.static(path.join(__dirname, '../static')));
// Serve the frontend app (web/app) for a full UI experience
app.use('/app', express.static(path.join(__dirname, '../app')));

// Lightweight API endpoints for auth (production should use a proper identity provider)
app.use(express.json());

// Add comprehensive logging middleware
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path} - IP: ${req.ip || 'unknown'}`);
  
  // Log request body for payment endpoints (excluding sensitive data)
  if (req.path.includes('/payment') || req.path.includes('/stripe')) {
    const logBody = { ...req.body };
    if (logBody.payment_method) delete logBody.payment_method;
    if (logBody.card) delete logBody.card;
    console.log('Request body:', JSON.stringify(logBody, null, 2));
  }
  
  next();
});

// Rate limiting middleware
const rateLimit = {};
const RATE_LIMIT = 100; // requests per minute per IP
app.use((req, res, next) => {
  const ip = req.ip || 'unknown';
  const now = Date.now();
  
  if (!rateLimit[ip]) {
    rateLimit[ip] = { count: 0, resetTime: now + 60000 };
  }
  
  if (now > rateLimit[ip].resetTime) {
    rateLimit[ip] = { count: 0, resetTime: now + 60000 };
  }
  
  rateLimit[ip].count++;
  
  if (rateLimit[ip].count > RATE_LIMIT) {
    return res.status(429).json({ 
      error: 'Too many requests. Please try again later.',
      resetTime: rateLimit[ip].resetTime 
    });
  }
  
  next();
});
app.post('/api/login', (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ error: 'Missing credentials' });
  }
  const pass = USERS[username];
  if (!pass || pass !== password) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: '1h' });
  return res.json({ token, username });
});

// Health check for orchestration
app.get('/health', (req, res) => res.json({ ok: true }));

// Stripe payment intent endpoint
app.post('/api/create-payment-intent', async (req, res) => {
  try {
    const { amount, currency = 'usd', planId, email } = req.body;
    
    if (!amount || amount <= 0) {
      return res.status(400).json({ error: 'Invalid amount' });
    }

    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(amount * 100), // Convert to cents
      currency,
      automatic_payment_methods: {
        enabled: true,
      },
      metadata: {
        plan_id: planId || 'one-time',
        user_email: email || ''
      }
    });

    res.json({
      clientSecret: paymentIntent.client_secret,
    });
  } catch (error) {
    console.error('Stripe error:', error);
    res.status(500).json({ error: 'Failed to create payment intent' });
  }
});

// Webhook endpoint for Stripe events
app.post('/api/webhooks/stripe', express.raw({type: 'application/json'}), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    console.log(`Webhook signature verification failed.`, err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the event
  switch (event.type) {
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      console.log('PaymentIntent was successful!');
      
      // Update user subscription status
      if (paymentIntent.metadata.plan_id && paymentIntent.metadata.plan_id !== 'one-time') {
        console.log(`User subscribed to plan: ${paymentIntent.metadata.plan_id}`);
        // Here you would update the user's subscription in your database
      }
      
      break;
    case 'payment_intent.payment_failed':
      console.log('PaymentIntent failed!');
      break;
    case 'invoice.payment_succeeded':
      console.log('Invoice payment succeeded - subscription renewed');
      break;
    case 'customer.subscription.deleted':
      console.log('Subscription cancelled');
      break;
    default:
      console.log(`Unhandled event type ${event.type}`);
  }

  // Return a 200 response to acknowledge receipt of the event
  res.json({received: true});
});

// Get Stripe publishable key
app.get('/api/stripe-config', (req, res) => {
  res.json({
    publishableKey: process.env.STRIPE_PUBLISHABLE_KEY,
  });
});

// Get customer billing history
app.get('/api/billing-history', async (req, res) => {
  try {
    // In a real app, you'd get the customer ID from the authenticated user
    const payments = await stripe.paymentIntents.list({
      limit: 10,
      expand: ['data.customer']
    });

    const history = payments.data.map(payment => ({
      id: payment.id,
      amount: payment.amount / 100, // Convert from cents
      currency: payment.currency,
      status: payment.status,
      created: new Date(payment.created * 1000).toLocaleDateString(),
      description: payment.description || 'Payment'
    }));

    res.json({ history });
  } catch (error) {
    console.error('Billing history error:', error);
    res.status(500).json({ error: 'Failed to retrieve billing history' });
  }
});

// Get customer payment methods
app.get('/api/payment-methods', async (req, res) => {
  try {
    // In a real app, you'd get the customer ID from the authenticated user
    // For demo purposes, return empty since we don't have customer setup
    res.json({ paymentMethods: [] });
  } catch (error) {
    console.error('Payment methods error:', error);
    res.status(500).json({ error: 'Failed to retrieve payment methods' });
  }
});

// Create customer and setup intent for adding payment method
app.post('/api/create-setup-intent', async (req, res) => {
  try {
    const setupIntent = await stripe.setupIntents.create({
      usage: 'off_session'
    });

    res.json({ clientSecret: setupIntent.client_secret });
  } catch (error) {
    console.error('Setup intent error:', error);
    res.status(500).json({ error: 'Failed to create setup intent' });
  }
});

// Verify payment endpoint
app.get('/api/verify-payment', async (req, res) => {
  try {
    const { payment_intent } = req.query;
    
    if (!payment_intent) {
      return res.status(400).json({ error: 'Payment intent ID required' });
    }

    const paymentIntent = await stripe.paymentIntents.retrieve(payment_intent);
    
    res.json({
      paymentIntent,
      status: paymentIntent.status,
      amount: paymentIntent.amount / 100,
      currency: paymentIntent.currency
    });
  } catch (error) {
    console.error('Payment verification error:', error);
    res.status(500).json({ error: 'Failed to verify payment' });
  }
});

// Admin API endpoints
app.get('/api/admin/users', requireAdmin, (req, res) => {
  const { page = 1, limit = 10, search = '', plan = '' } = req.query;
  
  let filteredUsers = mockUsers;
  
  if (search) {
    filteredUsers = filteredUsers.filter(user => 
      user.username.toLowerCase().includes(search.toLowerCase()) ||
      user.email.toLowerCase().includes(search.toLowerCase())
    );
  }
  
  if (plan) {
    filteredUsers = filteredUsers.filter(user => user.plan === plan);
  }
  
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + parseInt(limit);
  const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
  
  res.json({
    users: paginatedUsers,
    total: filteredUsers.length,
    page: parseInt(page),
    limit: parseInt(limit),
    totalPages: Math.ceil(filteredUsers.length / limit)
  });
});

app.get('/api/admin/analytics', requireAdmin, async (req, res) => {
  try {
    // Get Stripe analytics
    const balance = await stripe.balance.retrieve();
    const payments = await stripe.paymentIntents.list({
      limit: 100,
      expand: ['data.customer']
    });
    
    const totalRevenue = payments.data
      .filter(p => p.status === 'succeeded')
      .reduce((sum, p) => sum + p.amount, 0) / 100;
    
    const monthlyRevenue = payments.data
      .filter(p => p.status === 'succeeded')
      .reduce((sum, p) => sum + p.amount, 0) / 100;
    
    const analytics = {
      totalUsers: mockUsers.length,
      activeUsers: mockUsers.filter(u => {
        const lastActive = new Date(u.lastActive);
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return lastActive > weekAgo;
      }).length,
      totalRevenue,
      monthlyRevenue,
      totalTransactions: payments.data.length,
      successfulTransactions: payments.data.filter(p => p.status === 'succeeded').length,
      failedTransactions: payments.data.filter(p => p.status === 'failed').length,
      balance: balance.available.reduce((sum, b) => sum + b.amount, 0) / 100,
      plans: {
        Free: mockUsers.filter(u => u.plan === 'Free').length,
        Pro: mockUsers.filter(u => u.plan === 'Pro').length,
        Enterprise: mockUsers.filter(u => u.plan === 'Enterprise').length
      }
    };
    
    res.json(analytics);
  } catch (error) {
    console.error('Analytics error:', error);
    res.status(500).json({ error: 'Failed to retrieve analytics' });
  }
});

app.get('/api/admin/users/:id', requireAdmin, (req, res) => {
  const user = mockUsers.find(u => u.id === parseInt(req.params.id));
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

app.put('/api/admin/users/:id', requireAdmin, (req, res) => {
  const userIndex = mockUsers.findIndex(u => u.id === parseInt(req.params.id));
  if (userIndex === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  
  const { plan, email } = req.body;
  if (plan) mockUsers[userIndex].plan = plan;
  if (email) mockUsers[userIndex].email = email;
  
  res.json(mockUsers[userIndex]);
});

app.delete('/api/admin/users/:id', requireAdmin, (req, res) => {
  const userIndex = mockUsers.findIndex(u => u.id === parseInt(req.params.id));
  if (userIndex === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  
  const deletedUser = mockUsers.splice(userIndex, 1)[0];
  res.json({ message: 'User deleted successfully', user: deletedUser });
});

// Advanced Stripe Admin Operations

// Create customer
app.post('/api/admin/create-customer', requireAdmin, async (req, res) => {
  try {
    const { name, email, phone } = req.body;
    
    const customer = await stripe.customers.create({
      name,
      email,
      phone,
      metadata: {
        created_by: req.user.username
      }
    });

    res.json({ customer });
  } catch (error) {
    console.error('Error creating customer:', error);
    res.status(500).json({ error: 'Failed to create customer' });
  }
});

// Get all customers
app.get('/api/admin/customers', requireAdmin, async (req, res) => {
  try {
    const { limit = 50, starting_after } = req.query;
    
    const customers = await stripe.customers.list({
      limit: parseInt(limit),
      starting_after: starting_after,
      expand: ['data.default_source']
    });

    res.json({ customers: customers.data });
  } catch (error) {
    console.error('Error fetching customers:', error);
    res.status(500).json({ error: 'Failed to fetch customers' });
  }
});

// Create subscription
app.post('/api/admin/create-subscription', requireAdmin, async (req, res) => {
  try {
    const { customerId, priceId, trialPeriodDays = 0 } = req.body;
    
    const subscription = await stripe.subscriptions.create({
      customer: customerId,
      items: [{ price: priceId }],
      trial_period_days: trialPeriodDays > 0 ? trialPeriodDays : undefined,
      payment_behavior: 'default_incomplete',
      payment_settings: {
        save_default_payment_method: 'on_subscription',
        payment_method_types: ['card'],
      },
      expand: ['latest_invoice.payment_intent'],
      metadata: {
        created_by: req.user.username
      }
    });

    res.json({ subscription });
  } catch (error) {
    console.error('Error creating subscription:', error);
    res.status(500).json({ error: 'Failed to create subscription' });
  }
});

// Get all subscriptions
app.get('/api/admin/subscriptions', requireAdmin, async (req, res) => {
  try {
    const { limit = 50, status = 'all' } = req.query;
    
    const subscriptions = await stripe.subscriptions.list({
      limit: parseInt(limit),
      status: status !== 'all' ? status : undefined,
      expand: ['data.customer', 'data.plan.product', 'latest_invoice.payment_intent']
    });

    res.json({ subscriptions: subscriptions.data });
  } catch (error) {
    console.error('Error fetching subscriptions:', error);
    res.status(500).json({ error: 'Failed to fetch subscriptions' });
  }
});

// Cancel subscription
app.post('/api/admin/cancel-subscription/:subscriptionId', requireAdmin, async (req, res) => {
  try {
    const { subscriptionId } = req.params;
    const { at_period_end = false } = req.body;
    
    const subscription = await stripe.subscriptions.update(subscriptionId, {
      cancel_at_period_end: at_period_end,
      metadata: {
        canceled_by: req.user.username
      }
    });

    res.json({ subscription });
  } catch (error) {
    console.error('Error canceling subscription:', error);
    res.status(500).json({ error: 'Failed to cancel subscription' });
  }
});

// Process refund
app.post('/api/admin/refund', requireAdmin, async (req, res) => {
  try {
    const { paymentIntentId, amount } = req.body;
    
    const refund = await stripe.refunds.create({
      payment_intent: paymentIntentId,
      amount: amount || undefined, // If undefined, full refund
      reason: 'requested_by_customer',
      metadata: {
        processed_by: req.user.username
      }
    });

    res.json({ refund });
  } catch (error) {
    console.error('Error processing refund:', error);
    res.status(500).json({ error: 'Failed to process refund' });
  }
});

// Create payment method for customer
app.post('/api/admin/create-payment-method', requireAdmin, async (req, res) => {
  try {
    const { customerId, paymentMethodId } = req.body;
    
    const paymentMethod = await stripe.paymentMethods.attach(
      paymentMethodId,
      { customer: customerId }
    );

    // Set as default payment method
    await stripe.customers.update(customerId, {
      invoice_settings: {
        default_payment_method: paymentMethodId,
      },
    });

    res.json({ paymentMethod });
  } catch (error) {
    console.error('Error creating payment method:', error);
    res.status(500).json({ error: 'Failed to create payment method' });
  }
});

// Get customer payment methods
app.get('/api/admin/customer-payment-methods/:customerId', requireAdmin, async (req, res) => {
  try {
    const { customerId } = req.params;
    
    const paymentMethods = await stripe.paymentMethods.list({
      customer: customerId,
      type: 'card',
    });

    res.json({ paymentMethods: paymentMethods.data });
  } catch (error) {
    console.error('Error fetching payment methods:', error);
    res.status(500).json({ error: 'Failed to fetch payment methods' });
  }
});

// Create invoice for customer
app.post('/api/admin/create-invoice', requireAdmin, async (req, res) => {
  try {
    const { customerId, description } = req.body;
    
    const invoice = await stripe.invoices.create({
      customer: customerId,
      description,
      auto_advance: true,
      collection_method: 'charge_automatically',
      metadata: {
        created_by: req.user.username
      }
    });

    // Finalize the invoice
    const finalizedInvoice = await stripe.invoices.finalizeInvoice(invoice.id);

    res.json({ invoice: finalizedInvoice });
  } catch (error) {
    console.error('Error creating invoice:', error);
    res.status(500).json({ error: 'Failed to create invoice' });
  }
});

// Get list of prices
app.get('/api/admin/prices', requireAdmin, async (req, res) => {
  try {
    const { active = true, product } = req.query;
    
    const prices = await stripe.prices.list({
      active: active === 'true',
      product: product,
      expand: ['data.product']
    });

    res.json({ prices: prices.data });
  } catch (error) {
    console.error('Error fetching prices:', error);
    res.status(500).json({ error: 'Failed to fetch prices' });
  }
});

// Create product
app.post('/api/admin/create-product', requireAdmin, async (req, res) => {
  try {
    const { name, description, images = [] } = req.body;
    
    const product = await stripe.products.create({
      name,
      description,
      images,
      metadata: {
        created_by: req.user.username
      }
    });

    res.json({ product });
  } catch (error) {
    console.error('Error creating product:', error);
    res.status(500).json({ error: 'Failed to create product' });
  }
});

// Get list of products
app.get('/api/admin/products', requireAdmin, async (req, res) => {
  try {
    const { active = true } = req.query;
    
    const products = await stripe.products.list({
      active: active === 'true',
      expand: ['data.default_price']
    });

    res.json({ products: products.data });
  } catch (error) {
    console.error('Error fetching products:', error);
    res.status(500).json({ error: 'Failed to fetch products' });
  }
});

// Serve the stage page from this directory
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'stage_display.html'));
});

// Serve the stage UI for iframe embedding at /stage
app.get('/stage', (req, res) => {
  // Stage UI also loads via stage_display.html; pass through any query parameters (token/room)
  res.sendFile(path.join(__dirname, 'stage_display.html'));
});

// Setup HTTP server and Socket.IO for signaling
const server = http.createServer(app);
let io;
try {
  io = require('socket.io')(server, {
    cors: {
      origin: '*'
    }
  });
} catch (err) {
  // Fallback for older socket.io versions that expect different init
  io = require('socket.io')(server);
}
// OIDC login flow (production-ready scaffold)
async function ensureOidcClient(req) {
  if (oidcClient) return oidcClient;
  if (!OIDC_ISSUER || !OIDC_CLIENT_ID || !OIDC_CLIENT_SECRET) return null;
  const issuer = await Issuer.discover(OIDC_ISSUER);
  oidcClient = new issuer.Client({
    client_id: OIDC_CLIENT_ID,
    client_secret: OIDC_CLIENT_SECRET,
    redirect_uris: [`${req.protocol}://${req.get('host')}/auth/oidc/callback`],
    response_types: ['code'],
  });
  return oidcClient;
}

app.get('/auth/oidc/login', async (req, res) => {
  const client = await ensureOidcClient(req);
  if (!client) return res.status(500).send('OIDC not configured');
  const state = crypto.randomBytes(16).toString('hex');
  const nonce = crypto.randomBytes(16).toString('hex');
  oidcSessions.set(state, { nonce, client });
  const url = client.authorizationUrl({ scope: 'openid profile email', state, nonce });
  res.redirect(url);
});

app.get('/auth/oidc/callback', async (req, res) => {
  const { code, state } = req.query;
  const sess = oidcSessions.get(state);
  if (!sess) return res.status(400).send('Invalid state');
  oidcSessions.delete(state);
  try {
    const { client } = sess;
    const tokens = await client.callback(`${req.protocol}://${req.get('host')}/auth/oidc/callback`, { code, state }, { nonce: sess.nonce });
    const userinfo = await client.userinfo(tokens.access_token);
    const username = userinfo.preferred_username || userinfo.name || userinfo.email || userinfo.sub;
    const token = jwt.sign({ username, oidc: true }, JWT_SECRET, { expiresIn: '1h' });
    res.redirect('/app/index.html?token=' + encodeURIComponent(token));
  } catch (err) {
    console.error(err);
    res.status(500).send('OIDC login failed');
  }
});
// Optional Redis adapter for horizontal scaling
try {
  if (process.env.REDIS_URL) {
    const redisAdapter = require('socket.io-redis');
    io.adapter(redisAdapter(process.env.REDIS_URL));
    console.log('Stage signaling: using Redis adapter at', process.env.REDIS_URL);
  }
} catch (err) {
  console.warn('Stage signaling: Redis adapter not loaded:', err?.message);
}

// In-memory room management for signaling
const rooms = new Map(); // roomName -> Set(socketId)
const socketRooms = new Map(); // socketId -> Set(roomName)

// Stage signaling namespace
const stageIo = io.of('/stage');

stageIo.on('connection', (socket) => {
  // Authenticate via JWT (passed via socket.auth or query)
  const token = (socket.handshake.auth && socket.handshake.auth.token) || (socket.handshake.query && socket.handshake.query.token);
  if (!token) {
    socket.disconnect(true);
    return;
  }
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    socket.user = decoded.username;
  } catch (e) {
    socket.disconnect(true);
    return;
  }
  console.log(`Stage signaling: ${socket.id} connected as ${socket.user}`);

  socket.on('join-stage', ({ room }) => {
    const rm = room || 'default';
    if (!rooms.has(rm)) rooms.set(rm, new Set());
    const members = rooms.get(rm);
    members.add(socket.id);

    // track membership per socket
    if (!socketRooms.has(socket.id)) socketRooms.set(socket.id, new Set());
    socketRooms.get(socket.id).add(rm);
    socket.join(rm);

    // Notify existing peers
    stageIo.to(rm).emit('user-joined', { id: socket.id, count: members.size });
    // Inform the new peer about other peers in the room
    const peers = Array.from(members).filter(id => id !== socket.id);
    socket.emit('peers', { peers });
  });

  socket.on('offer', ({ room, to, offer }) => {
    if (to) stageIo.to(to).emit('offer', { from: socket.id, offer });
  });

  socket.on('answer', ({ room, to, answer }) => {
    if (to) stageIo.to(to).emit('answer', { from: socket.id, answer });
  });

  socket.on('ice-candidate', ({ room, to, candidate }) => {
    if (to) stageIo.to(to).emit('ice-candidate', { from: socket.id, candidate });
  });

  socket.on('disconnecting', () => {
    // remove from all rooms
    if (socketRooms.has(socket.id)) {
      for (const rm of socketRooms.get(socket.id)) {
        const members = rooms.get(rm);
        if (members) {
          members.delete(socket.id);
          stageIo.to(rm).emit('user-left', { id: socket.id, count: members.size });
        }
      }
      socketRooms.delete(socket.id);
    }
  });
  socket.on('disconnect', () => {
    // ensure cleanup in case disconnect happens
    if (socketRooms.has(socket.id)) {
      for (const rm of socketRooms.get(socket.id)) {
        const members = rooms.get(rm);
        if (members) {
          members.delete(socket.id);
          stageIo.to(rm).emit('user-left', { id: socket.id, count: members.size });
        }
      }
      socketRooms.delete(socket.id);
    }
    console.log(`Stage signaling: ${socket.id} disconnected`);
  });
});

server.listen(port, () => {
  console.log(`Stage display server listening on port ${port}`);
}).on('error', (e) => {
  console.error('Failed to start stage server:', e);
});
