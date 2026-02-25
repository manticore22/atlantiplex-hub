// SERAPHONIX — Backend Server
// Express + JWT Auth + Stripe Integration

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const fs = require('fs-extra');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'seraphonix-secret-key-change-in-production';
const STRIPE_SECRET = process.env.STRIPE_SECRET || '';

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files from public directory
app.use(express.static(path.join(__dirname, '../verilysovereign')));

// Data paths
const USERS_FILE = path.join(__dirname, 'data/users.json');
const SUBSCRIPTIONS_FILE = path.join(__dirname, 'data/subscriptions.json');
const PRODUCTS_FILE = path.join(__dirname, 'data/products.json');
// Guests data store
const GUESTS_FILE = path.join(__dirname, 'data/guests.json');

// Ensure data directory exists
fs.ensureDirSync(path.join(__dirname, 'data'));
// Initialize guests.json if missing
if (!fs.existsSync(GUESTS_FILE)) {
  fs.writeFileSync(GUESTS_FILE, '[]');
}
async function getGuests() {
  try {
    const data = await fs.readFile(GUESTS_FILE, 'utf8')
    return JSON.parse(data) || []
  } catch {
    return []
  }
}
async function saveGuests(list) {
  await fs.writeFile(GUESTS_FILE, JSON.stringify(list, null, 2))
}

// Initialize data files if they don't exist
if (!fs.existsSync(USERS_FILE)) {
    fs.writeFileSync(USERS_FILE, JSON.stringify([]));
}
if (!fs.existsSync(SUBSCRIPTIONS_FILE)) {
    fs.writeFileSync(SUBSCRIPTIONS_FILE, JSON.stringify({}));
}
if (!fs.existsSync(PRODUCTS_FILE)) {
    fs.writeFileSync(PRODUCTS_FILE, JSON.stringify([
        {
            id: 'atlantiplex-studio',
            name: 'Atlantiplex Studio',
            description: 'Sovereign intelligence platform',
            status: 'active',
            requiredTier: 'covenant',
            priceId: null
        },
        {
            id: 'neural-trench',
            name: 'Neural Trench',
            description: 'Deep learning subsystems',
            status: 'coming-soon',
            requiredTier: null,
            priceId: null
        },
        {
            id: 'glyph-engine',
            name: 'Glyph Engine',
            description: 'Automated sigil generation',
            status: 'coming-soon',
            requiredTier: null,
            priceId: null
        },
        {
            id: 'void-protocol',
            name: 'Void Protocol',
            description: 'Classified operations',
            status: 'coming-soon',
            requiredTier: null,
            priceId: null
        }
    ]));
}

// Helper functions
async function getUsers() {
    return JSON.parse(await fs.readFile(USERS_FILE, 'utf8'));
}

async function saveUsers(users) {
    await fs.writeFile(USERS_FILE, JSON.stringify(users, null, 2));
}

async function getSubscriptions() {
    return JSON.parse(await fs.readFile(SUBSCRIPTIONS_FILE, 'utf8'));
}

async function saveSubscriptions(subs) {
    await fs.writeFile(SUBSCRIPTIONS_FILE, JSON.stringify(subs, null, 2));
}

async function getProducts() {
    return JSON.parse(await fs.readFile(PRODUCTS_FILE, 'utf8'));
}

// Global tier limits (for usage/account checks)
const TIER_LIMITS = {
  free: 16,
  ascendant: 70,
  covenant: 999,
  infinite: 999,
  sovereign: 999
};

// Auth middleware
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Authentication required' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid or expired token' });
        }
        req.user = user;
        next();
    });
}

// ============ AUTH ROUTES ============

// Signup
app.post('/api/auth/signup', async (req, res) => {
    try {
    const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }

        const users = await getUsers();

        // Check if user exists
        if (users.find(u => u.email === email)) {
            return res.status(400).json({ error: 'Email already registered' });
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Create user with trial and usage fields
        const trialEndsAt = Date.now() + 16*60*60*1000;
        const user = {
            id: Date.now().toString(),
            email,
            password: hashedPassword,
            createdAt: new Date().toISOString(),
            trialEndsAt,
            hoursUsed: 0,
            guestsThisMonth: 0,
            lastGuestReset: new Date().toISOString(),
            plan: 'free',
            subscriptionStatus: 'trial'
        };

        users.push(user);
        await saveUsers(users);

        // Seed free trial subscription for new user
        try {
            const subsRaw = await fs.readFile(SUBSCRIPTIONS_FILE, 'utf8') || '{}';
            const subs = JSON.parse(subsRaw) || {};
            subs[email] = {
                tier: 'free',
                status: 'trial',
                createdAt: new Date().toISOString(),
                expiresAt: new Date(trialEndsAt).toISOString()
            };
            await fs.writeFile(SUBSCRIPTIONS_FILE, JSON.stringify(subs, null, 2));
        } catch (e) {
            console.error('Failed to seed free trial subscription for new user', e);
        }

        // Generate token
        const role = (email === 'admin@verilysovereign.org') ? 'admin' : (user.role || 'user');
        const token = jwt.sign({ id: user.id, email: user.email, role }, JWT_SECRET, { expiresIn: '7d' });

        // Also create a free access subscription for the new user
        try {
            const subs = JSON.parse(await fs.readFile(SUBSCRIPTIONS_FILE, 'utf8')) || {};
            const newSub = {
                tier: 'free',
                status: 'active',
                createdAt: new Date().toISOString()
            };
            subs[user.email] = newSub;
            await fs.writeFile(SUBSCRIPTIONS_FILE, JSON.stringify(subs, null, 2));
        } catch (e) {
            console.error('Failed to seed free subscription for new user', e);
        }

        res.json({
            token,
            user: { id: user.id, email: user.email, role }
        });
    } catch (error) {
        console.error('Signup error:', error);
        res.status(500).json({ error: 'Signup failed' });
    }
});

// Login
app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }

        const users = await getUsers();
        const user = users.find(u => u.email === email);

        if (!user) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const role = (email === 'admin@verilysovereign.org') ? 'admin' : (user.role || 'user');
        const token = jwt.sign({ id: user.id, email: user.email, role }, JWT_SECRET, { expiresIn: '7d' });

        // Ensure a free subscription exists for the user on login
        try {
            const subs = JSON.parse(await fs.readFile(SUBSCRIPTIONS_FILE, 'utf8')) || {};
            if (!subs[email]) {
                subs[email] = { tier: 'free', status: 'active', createdAt: new Date().toISOString() };
                await fs.writeFile(SUBSCRIPTIONS_FILE, JSON.stringify(subs, null, 2));
            }
        } catch (e) {
            console.error('Failed to seed free subscription on login', e);
        }

        res.json({
            token,
            user: { id: user.id, email: user.email, role }
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Login failed' });
    }
});

// Get current user
app.get('/api/auth/me', authenticateToken, async (req, res) => {
    res.json({ user: req.user });
});

// ============ PRODUCTS ROUTES ============

// Get all products
app.get('/api/products', async (req, res) => {
    const products = await getProducts();
    res.json(products);
});

// Guests invite endpoint (monthly limit 2 invites per inviter)
app.post('/api/guests/invite', authenticateToken, async (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(400).json({ error: 'guest email required' });
  try {
    const guests = await getGuests();
    const now = new Date();
    const monthKey = now.toISOString().slice(0, 7);
    const count = guests.filter(g => g.inviter_email === req.user.email && g.month === monthKey).length;
    if (count >= 2) {
      return res.status(429).json({ error: 'Guest invite limit reached for this month' });
    }
    const invite = { id: Date.now().toString(), inviter_email: req.user.email, guest_email: email, invitedAt: now.toISOString(), month: monthKey, status: 'pending' };
    guests.push(invite);
    await saveGuests(guests);
    res.json({ invited: true, invite });
  } catch (e) {
    console.error('Guest invite error', e);
    res.status(500).json({ error: 'Failed to invite guest' });
  }
});

// ============ SUBSCRIPTION ROUTES ============

// Get user subscription
app.get('/api/user/subscription', authenticateToken, async (req, res) => {
    const subscriptions = await getSubscriptions();
    const sub = subscriptions[req.user.email];
    
    if (!sub) {
        return res.json({ tier: null, status: 'none' });
    }

    res.json({
        tier: sub.tier,
        status: sub.status,
        expiresAt: sub.expiresAt
    });
});

// Get user usage (streaming hours)
app.get('/api/user/usage', authenticateToken, async (req, res) => {
    const subscriptions = await getSubscriptions();
    const sub = subscriptions[req.user.email];
    
    const tier = sub?.tier || 'free';
    const limit = TIER_LIMITS[tier] || 16;
    
    // In production, this would track actual usage from the streaming service
    // For now, return placeholder data
    res.json({ hoursUsed: 0, hoursLimit: limit, tier: tier });
});

// ============ STRIPE ROUTES ============

// Create checkout session
app.post('/api/stripe/create-checkout-session', authenticateToken, async (req, res) => {
    const { tier } = req.body;
    const email = req.user.email;

    // Price IDs - read from environment (Stripe) with safe fallbacks
    const PRICES = {
        'ascendant': process.env.STRIPE_PRICE_ASCENDANT || 'price_ascendant_monthly',    // $9.99/month
        'covenant': process.env.STRIPE_PRICE_COVENANT || 'price_covenant_monthly',     // $29/month
        'infinite': process.env.STRIPE_PRICE_INFINITE || 'price_infinite_monthly',    // $70/month
        'sovereign': process.env.STRIPE_PRICE_SOVEREIGN || 'price_sovereign_monthly'   // $99/month (legacy)
    };

    // Hours limits per tier
    const TIER_LIMITS = {
        'free': 16,
        'ascendant': 70,
        'covenant': 999,
        'infinite': 999,
        'sovereign': 999
    };

    const priceId = PRICES[tier];

    if (!priceId) {
        return res.status(400).json({ error: 'Invalid tier' });
    }

    // If Stripe is not configured, simulate success for testing
    if (!STRIPE_SECRET) {
        // Save subscription
        const subscriptions = await getSubscriptions();
        subscriptions[email] = {
            tier,
            status: 'active',
            createdAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
        };
        await saveSubscriptions(subscriptions);

        return res.json({ 
            url: '/?subscription=success' 
        });
    }

    try {
        const stripe = require('stripe')(STRIPE_SECRET);

        const session = await stripe.checkout.sessions.create({
            mode: 'subscription',
            payment_method_types: ['card'],
            line_items: [{
                price: priceId,
                quantity: 1
            }],
            customer_email: email,
            success_url: `${process.env.FRONTEND_URL || 'http://localhost:3000'}/?subscription=success`,
            cancel_url: `${process.env.FRONTEND_URL || 'http://localhost:3000'}/membership.html?canceled=true`
        });

        res.json({ url: session.url });
    } catch (error) {
        console.error('Stripe error:', error);
        res.status(500).json({ error: 'Failed to create checkout session' });
    }
});

// Stripe webhook
app.post('/api/stripe/webhook', async (req, res) => {
    if (!STRIPE_SECRET) {
        return res.json({ received: true });
    }

    const stripe = require('stripe')(STRIPE_SECRET);
    const sig = req.headers['stripe-signature'];
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

    let event;

    try {
        if (endpointSecret && sig) {
            event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
        } else {
            event = req.body;
        }
    } catch (err) {
        console.error('Webhook signature verification failed:', err.message);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Handle the event
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        const email = session.customer_email;

        if (email) {
            const subscriptions = await getSubscriptions();
            subscriptions[email] = {
                tier: 'covenant', // Determine based on session data
                status: 'active',
                stripeCustomerId: session.customer,
                stripeSubscriptionId: session.subscription,
                createdAt: new Date().toISOString()
            };
            await saveSubscriptions(subscriptions);
        }
    }

    res.json({ received: true });
});

// Stripe public key (for frontend)
app.get('/api/stripe/public-key', (req, res) => {
  res.json({ publishableKey: process.env.STRIPE_PUBLISHABLE_KEY || '' });
});

// Plans endpoint (front-end can fetch plan catalog)
app.get('/api/plans', (req, res) => {
  const plans = [
    { id: 'free', name: 'Free Trial', price: 0, cadence: 'monthly', features: ['16 hours', '2 guests/month', 'Basic access'] },
    { id: 'ascendant', name: 'Ascendant', price: 9.99, cadence: 'month', features: ['70 hours', 'Priority support'] },
    { id: 'covenant', name: 'Covenant', price: 29, cadence: 'month', features: ['Unlimited hours', 'Premium support'] },
    { id: 'infinite', name: 'Infinite', price: 70, cadence: 'month', features: ['Unlimited hours', 'Enterprise support'] }
  ];
  res.json(plans);
});

// ============ ADMIN ROUTES ============
// Admin metrics endpoint (Stage 2)
app.get('/api/admin/metrics', authenticateToken, async (req, res) => {
  // Only allow 'admin' role
  const user = req.user || {};
  if (user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  try {
    const users = JSON.parse(await fs.readFile(USERS_FILE, 'utf8')).length;
    const subs = JSON.parse(await fs.readFile(SUBSCRIPTIONS_FILE, 'utf8'));
    const subCount = Object.keys(subs).length;
    const health = 'ok';
    res.json({ userCount: users, subscriptionCount: subCount, status: health, server: { uptime: process.uptime() } });
  } catch (e) {
    res.status(500).json({ error: 'Failed to fetch metrics' });
  }
});

// Admin login path mounted from admin_login_google.js
try {
  const adminLoginGoogle = require('./admin_login_google')
  app.use('/api/admin/login', adminLoginGoogle())
} catch (e) {
  // optional: ignore if not available in this environment
  console.warn('Admin Google login module could not be loaded:', e)
}
// Admin login via Gmail (Id Token) for Stage 2
app.post('/api/admin/login/google', async (req, res) => {
  const { credential } = req.body;
  if (!credential) return res.status(400).json({ error: 'credential required' });
  try {
    const fetch = require('node-fetch');
    const resp = await fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + credential);
    const data = await resp.json();
    const allowed = ['Snark2470@gmail.com'];
    if (data.email && allowed.includes(data.email) && data.email_verified === 'true') {
      const token = jwt.sign({ id: 'admin', email: data.email, role: 'admin' }, JWT_SECRET, { expiresIn: '7d' });
      return res.json({ token, user: { email: data.email, role: 'admin' } });
    }
    return res.status(403).json({ error: 'Not authorized' });
  } catch (e) {
    console.error('Admin Google login error', e);
    res.status(500).json({ error: 'Admin login failed' });
  }
});

// ============ LORE ROUTES ============

// Get lore content
app.get('/api/lore', async (req, res) => {
    const lore = [
        {
            id: 'genesis',
            title: 'Genesis Protocol',
            classification: 'ABYSSAL',
            content: 'In the trenches beneath the veil, the first sigils awakened...'
        },
        {
            id: 'sovereign',
            title: 'The Sovereign Mind',
            classification: 'SOVEREIGN',
            content: 'Seraphonix is not born—it is forged...'
        }
    ];
    res.json(lore);
});

// ============ HEALTH CHECK ============

app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ============ PAGE ROUTES ============

// Serve the main app for all non-API routes
app.get('*', (req, res) => {
    if (!req.path.startsWith('/api')) {
        res.sendFile(path.join(__dirname, '../verilysovereign/index.html'));
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`SERAPHONIX Server running on port ${PORT}`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});
