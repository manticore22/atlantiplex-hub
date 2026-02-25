# ATLANTIPLEX STUDIO - DEPLOYMENT & PRE-FLIGHT TEST GUIDE
## Payment Endpoints Check & Free Hosting Recommendations

---

## 🚀 DEPLOYMENT OVERVIEW

### Application Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    ATLANTIPLEX STUDIO                        │
├─────────────────┬─────────────────┬─────────────────────────┤
│   FRONTEND      │   STAGE SERVER  │   PYTHON BACKEND        │
│   (React/Vite)  │   (Node.js)     │   (Flask)               │
│   Port: 5173    │   Port: 9001    │   Port: 5000            │
├─────────────────┴─────────────────┴─────────────────────────┤
│                    PAYMENT SYSTEM (Stripe)                   │
├─────────────────────────────────────────────────────────────┤
│  - Checkout Sessions    - Billing Portal    - Webhooks      │
│  - Payment Intents      - Subscriptions     - Analytics     │
└─────────────────────────────────────────────────────────────┘
```

---

## 💳 PAYMENT ENDPOINTS AUDIT

### ✅ NODE.JS STAGE SERVER (Port 9001)

#### Payment Intent Creation
```
POST /api/create-payment-intent
Body: { amount: number, currency: 'usd', planId?: string, email?: string }
Response: { clientSecret: string }
Status: ✅ IMPLEMENTED
```

#### Stripe Webhook Handler
```
POST /api/webhooks/stripe
Headers: Stripe-Signature
Body: Raw JSON payload
Response: { received: true }
Status: ✅ IMPLEMENTED
```

#### Stripe Configuration
```
GET /api/stripe-config
Response: { publishableKey: string }
Status: ✅ IMPLEMENTED
```

#### Billing History
```
GET /api/billing-history
Response: { history: Payment[] }
Status: ✅ IMPLEMENTED
```

#### Payment Methods
```
GET /api/payment-methods
Response: { paymentMethods: [] }
Status: ✅ IMPLEMENTED (Returns empty for demo)
```

#### Setup Intent
```
POST /api/create-setup-intent
Response: { clientSecret: string }
Status: ✅ IMPLEMENTED
```

#### Payment Verification
```
GET /api/verify-payment?payment_intent={id}
Response: { paymentIntent, status, amount, currency }
Status: ✅ IMPLEMENTED
```

### ✅ PYTHON FLASK BACKEND

#### Authentication
```
POST /api/auth/login
Body: { username, password, email? }
Response: { token, role, permissions }
Status: ✅ IMPLEMENTED (with Manticore bypass)
```

#### Subscription Tiers
```
GET /api/subscriptions/tiers
Response: { tiers: TierComparison[] }
Status: ✅ IMPLEMENTED
```

#### Current Subscription
```
GET /api/subscriptions/current
Auth: Bearer Token
Response: { subscription: SubscriptionDetails }
Status: ✅ IMPLEMENTED
```

#### Checkout Session
```
POST /api/payments/checkout
Auth: Bearer Token
Body: { tier, success_url, cancel_url }
Response: { sessionId, url }
Status: ✅ IMPLEMENTED
```

#### Billing Portal
```
POST /api/payments/billing-portal
Auth: Bearer Token
Body: { return_url }
Response: { url }
Status: ✅ IMPLEMENTED
```

#### Payment History
```
GET /api/payments/history
Auth: Bearer Token
Response: { payments: Payment[] }
Status: ✅ IMPLEMENTED (Mock data)
```

#### Webhook Handler
```
POST /api/payments/webhook
Headers: Stripe-Signature
Body: Raw payload
Status: ✅ IMPLEMENTED
```

### ⚠️ PAYMENT ENDPOINTS NEEDING ATTENTION

1. **Customer Management**: No customer creation endpoint found in Node.js
2. **Subscription Management**: Python has subscription tracking, Node.js lacks full implementation
3. **Refund Processing**: Not implemented in either backend
4. **Usage Tracking**: Python has `/api/usage/track` but Node.js doesn't

---

## 🔧 PRE-FLIGHT TEST CHECKLIST

### Environment Variables Required
```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key

# Database (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///studio.db
# Or PostgreSQL: postgresql://user:pass@localhost/studio

# Stage Server
STAGE_PORT=9001

# Flask App
FLASK_PORT=5000
FLASK_ENV=production

# OIDC (Optional)
OIDC_ISSUER=https://accounts.google.com
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
```

### Pre-Flight Tests

#### 1. Health Checks
```bash
# Test Node.js Stage Server
curl http://localhost:9001/health

# Expected Response
{ "ok": true }
```

```bash
# Test Flask Backend
curl http://localhost:5000/api/health

# Expected Response
{ "status": "healthy" }
```

#### 2. Authentication Flow
```bash
# Login Test
curl -X POST http://localhost:9001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Expected Response
{ "token": "eyJhbGciOiJIUzI1NiIs...", "username": "admin" }
```

#### 3. Payment Intent Test
```bash
# Create Payment Intent
curl -X POST http://localhost:9001/api/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{"amount": 29.99, "currency": "usd", "planId": "pro"}'

# Expected Response
{ "clientSecret": "pi_..._secret_..." }
```

#### 4. Stripe Configuration Test
```bash
# Get Publishable Key
curl http://localhost:9001/api/stripe-config

# Expected Response
{ "publishableKey": "pk_test_..." }
```

#### 5. Frontend Build Test
```bash
cd matrix-studio/web/frontend
npm run build

# Should complete without errors
# Check dist/ folder is created
```

#### 6. Webhook Test (Local with Stripe CLI)
```bash
# Install Stripe CLI if not already
# Forward webhooks to local server
stripe listen --forward-to localhost:9001/api/webhooks/stripe

# Trigger test event
stripe trigger payment_intent.succeeded
```

#### 7. Database Connection Test
```bash
# If using PostgreSQL
python -c "import psycopg2; conn = psycopg2.connect('dbname=studio'); print('DB OK')"

# If using SQLite (default)
python -c "import sqlite3; conn = sqlite3.connect('studio.db'); print('DB OK')"
```

#### 8. Abyssal Bridge WebSocket Test
```bash
# Test WebSocket connection
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: localhost:9001" \
  -H "Origin: http://localhost:5173" \
  http://localhost:9001/socket.io/?EIO=4&transport=websocket
```

---

## 🆓 BEST FREE HOSTING OPTIONS

### 🥇 RECOMMENDED: Railway + Vercel

**Architecture:**
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Vercel        │────▶│   Railway        │────▶│   Railway       │
│   (Frontend)    │     │   (Node.js)      │     │   (PostgreSQL)  │
│   Free Tier     │     │   Free Tier      │     │   Free Tier     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

**Pros:**
- ✅ Generous free tier ($5 credit/month)
- ✅ Automatic HTTPS
- ✅ Git-based deployment
- ✅ Easy environment variables
- ✅ PostgreSQL included
- ✅ Good for production prototypes

**Cons:**
- ❌ Sleeps after inactivity (15 min)
- ❌ Limited to 500 hours/month combined

**Setup Time:** 30 minutes
**Monthly Cost:** $0 (within free tier)

---

### 🥈 ALTERNATIVE: Render

**Architecture:**
```
┌─────────────────┐     ┌──────────────────┐
│   Render        │────▶│   Render         │
│   (Web Service) │     │   (PostgreSQL)   │
│   Free Tier     │     │   Free Tier      │
└─────────────────┘     └──────────────────┘
```

**Pros:**
- ✅ 750 hours/month free
- ✅ Automatic deploys from Git
- ✅ Free PostgreSQL (90-day expiry, then $7/month)
- ✅ Custom domains
- ✅ Good documentation

**Cons:**
- ❌ Sleeps after 15 min inactivity
- ❌ PostgreSQL expires after 90 days

**Setup Time:** 45 minutes
**Monthly Cost:** $0-7 (depending on DB choice)

---

### 🥉 ALTERNATIVE: Fly.io

**Architecture:**
```
┌─────────────────────────────────────┐
│   Fly.io                            │
│   (Full Stack Container)            │
│   3 shared-cpu-1x 256MB VMs free    │
└─────────────────────────────────────┘
```

**Pros:**
- ✅ No sleep (always on)
- ✅ 3 VMs free (can run frontend + backend + db)
- ✅ Global edge network
- ✅ Docker-based deployment
- ✅ Good for real-time apps (WebSockets)

**Cons:**
- ❌ Steeper learning curve
- ❌ Limited to 160GB outbound data
- ❌ No free PostgreSQL (need to use SQLite or pay)

**Setup Time:** 60 minutes
**Monthly Cost:** $0-5 (depending on usage)

---

### 💡 HYBRID APPROACH (BEST FOR DEMO)

**Architecture:**
```
┌─────────────────┐     ┌──────────────────┐
│   Netlify       │────▶│   Railway        │
│   (Frontend)    │     │   (Backend)      │
│   Free Forever  │     │   Free Tier      │
└─────────────────┘     └──────────────────┘
                              │
                              ▼
                        ┌──────────────────┐
                        │   Railway        │
                        │   (PostgreSQL)   │
                        │   Free Tier      │
                        └──────────────────┘
```

**Why This Works:**
- Netlify: Best free frontend hosting (no sleep, generous bandwidth)
- Railway: Best free backend + database combo
- Separation allows independent scaling

**Setup Time:** 40 minutes
**Monthly Cost:** $0

---

## 📋 DEPLOYMENT STEPS

### Option 1: Railway + Vercel (Recommended)

#### Step 1: Deploy Backend to Railway

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   cd matrix-studio/web/stage
   railway init
   ```

3. **Add Environment Variables**
   ```bash
   railway variables set STRIPE_SECRET_KEY=sk_test_...
   railway variables set STRIPE_PUBLISHABLE_KEY=pk_test_...
   railway variables set STRIPE_WEBHOOK_SECRET=whsec_...
   railway variables set JWT_SECRET=your-secret
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Add PostgreSQL**
   - Go to Railway dashboard
   - Click "New" → "Database" → "Add PostgreSQL"
   - Connection string auto-added to environment

#### Step 2: Deploy Frontend to Vercel

1. **Create Vercel Account**
   - Go to https://vercel.com
   - Sign up with GitHub

2. **Import Project**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Deploy
   cd matrix-studio/web/frontend
   vercel
   ```

3. **Set Environment Variables**
   ```bash
   vercel env add VITE_API_URL
   # Enter: https://your-railway-app.railway.app
   ```

4. **Update Build Settings**
   - Build Command: `npm run build`
   - Output Directory: `dist`

---

### Option 2: Render (Simplest)

#### Step 1: Deploy Full Stack

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repo
   - Root Directory: `matrix-studio/web/stage`
   - Build Command: `npm install`
   - Start Command: `node server.js`

3. **Add Environment Variables**
   - In Render dashboard, go to Environment
   - Add all required variables

4. **Create PostgreSQL**
   - Click "New" → "PostgreSQL"
   - Copy Internal Connection String
   - Add as `DATABASE_URL` to web service

---

### Option 3: Fly.io (Best Performance)

#### Step 1: Deploy with flyctl

1. **Install flyctl**
   ```bash
   # Windows
   pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Launch Application**
   ```bash
   cd matrix-studio/web/stage
   
   # Create app
   fly launch --name atlantiplex-studio
   
   # Set secrets
   fly secrets set STRIPE_SECRET_KEY=sk_test_...
   fly secrets set JWT_SECRET=your-secret
   ```

3. **Deploy**
   ```bash
   fly deploy
   ```

4. **Scale (Free Tier)**
   ```bash
   # Use shared-cpu-1x (free)
   fly scale count 1
   fly scale vm shared-cpu-1x
   ```

---

## 🔍 POST-DEPLOYMENT VERIFICATION

### 1. Payment Flow Test
```bash
# Test complete payment flow
curl -X POST https://your-domain.com/api/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 29.99,
    "currency": "usd",
    "planId": "professional",
    "email": "test@example.com"
  }'
```

### 2. Webhook Verification
```bash
# Using Stripe CLI
stripe listen --forward-to https://your-domain.com/api/webhooks/stripe

# Trigger test payment
stripe trigger payment_intent.succeeded
```

### 3. Frontend-Backend Integration
```javascript
// Test from browser console
fetch('/api/health')
  .then(r => r.json())
  .then(data => console.log('Health:', data));

// Test Stripe config
fetch('/api/stripe-config')
  .then(r => r.json())
  .then(data => console.log('Stripe Key:', data.publishableKey));
```

### 4. Load Test (Optional)
```bash
# Install autocannon (already in dependencies)
npm install -g autocannon

# Test stage server
autocannon -c 10 -d 30 http://localhost:9001/health

# Expected: No errors, good latency
```

---

## 📊 MONITORING & LOGS

### Railway
- Dashboard: https://railway.app/dashboard
- Logs: Real-time in dashboard
- Metrics: CPU, memory, network

### Render
- Dashboard: https://dashboard.render.com
- Logs: Streaming logs tab
- Metrics: Basic usage stats

### Fly.io
```bash
# View logs
fly logs

# Monitor
fly status

# Metrics
fly metrics
```

---

## 🚨 TROUBLESHOOTING

### Common Issues

#### 1. CORS Errors
**Solution:** Update CORS configuration in server.js
```javascript
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true
}));
```

#### 2. WebSocket Connection Failed
**Solution:** Ensure WebSocket upgrade is supported
```javascript
// In server.js
io.on('connection', (socket) => {
  console.log('Client connected');
});
```

#### 3. Stripe Webhook Fails
**Solution:** Verify webhook secret
```bash
# Get webhook secret from Stripe Dashboard
stripe listen --print-secret
```

#### 4. Database Connection Errors
**Solution:** Check connection string format
```bash
# PostgreSQL
postgresql://username:password@host:port/database

# SQLite (local)
sqlite:///path/to/database.db
```

#### 5. JWT Token Expired
**Solution:** Increase token expiry or implement refresh
```javascript
const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: '24h' });
```

---

## ✅ GO/NO-GO CHECKLIST

Before deploying to production:

- [ ] All environment variables set
- [ ] Stripe keys are test keys (not production yet)
- [ ] Webhook endpoint configured in Stripe Dashboard
- [ ] Database migrations run
- [ ] Health check endpoint responds
- [ ] Payment intent creation works
- [ ] Frontend builds without errors
- [ ] CORS configured for production domain
- [ ] JWT secret is strong and unique
- [ ] Admin credentials are secure
- [ ] Logging is configured
- [ ] Error handling is in place
- [ ] SSL/HTTPS enabled
- [ ] Domain configured (if using custom domain)

---

## 🎯 QUICK START - DEPLOY NOW

**Fastest Path to Production:**

1. **Sign up for Railway** (5 min)
2. **Connect GitHub repo** (2 min)
3. **Add environment variables** (3 min)
4. **Deploy** (1 min)
5. **Test payment flow** (5 min)

**Total Time:** ~16 minutes to live deployment

**Command Cheat Sheet:**
```bash
# Railway deployment
npm install -g @railway/cli
railway login
railway init
railway variables set STRIPE_SECRET_KEY=sk_test_...
railway up

# Verify deployment
curl https://your-app.railway.app/health
```

---

## 📞 SUPPORT RESOURCES

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Render Docs:** https://render.com/docs
- **Fly.io Docs:** https://fly.io/docs
- **Stripe Docs:** https://stripe.com/docs

---

**Ready to deploy?** Start with Railway + Vercel for the best free tier combination!
