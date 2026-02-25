# Atlantiplex Studio - Quick Deployment Guide

## 🚀 Deploy in 15 Minutes

### Prerequisites
- Node.js 18+ installed
- Git repository initialized
- Stripe account (free)
- Railway or Vercel account (free)

### Step 1: Clone and Setup (3 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd atlantiplex-hub

# Install dependencies
npm run setup

# Or manually:
cd matrix-studio/web/stage && npm install
cd ../frontend && npm install
```

### Step 2: Environment Configuration (5 minutes)

```bash
# Create environment file
cp matrix-studio/web/.env.example matrix-studio/web/.env

# Edit the file with your values:
# - STRIPE_SECRET_KEY (from Stripe Dashboard)
# - STRIPE_PUBLISHABLE_KEY (from Stripe Dashboard)
# - JWT_SECRET (generate a random string)
```

### Step 3: Pre-Flight Test (3 minutes)

```bash
# Start the backend server
cd matrix-studio/web/stage
npm start

# In another terminal, run tests
python pre_flight_test.py
```

Expected output:
```
✓ All required environment variables are set
✓ Stage server is healthy
✓ Login endpoint working
✓ Stripe publishable key configured
✓ Payment intent creation working
✓ Frontend build exists
```

### Step 4: Deploy Backend to Railway (4 minutes)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project (from project root)
railway init

# Set environment variables
railway variables set STRIPE_SECRET_KEY=sk_test_...
railway variables set STRIPE_PUBLISHABLE_KEY=pk_test_...
railway variables set JWT_SECRET=your-secret-key

# Deploy
railway up

# Get your URL
railway domain
```

### Step 5: Deploy Frontend to Vercel (3 minutes)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy (from frontend directory)
cd matrix-studio/web/frontend
vercel

# Set environment variable
vercel env add VITE_API_URL
# Enter your Railway URL: https://your-app.railway.app

# Deploy to production
vercel --prod
```

### Step 6: Configure Stripe Webhooks (2 minutes)

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-railway-app.railway.app/api/webhooks/stripe`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `invoice.payment_succeeded`
4. Copy webhook secret
5. Add to Railway: `railway variables set STRIPE_WEBHOOK_SECRET=whsec_...`

## ✅ Verification

### Test Payment Flow

1. Open your Vercel URL
2. Navigate to payment page
3. Use Stripe test card: `4242 4242 4242 4242`
4. Any future date, any CVC, any ZIP
5. Complete payment
6. Check Stripe Dashboard for successful payment

### Test Admin Features

1. Login with admin/admin123
2. Navigate to `/?command=true`
3. Verify Abyssal Bridge loads
4. Test real-time metrics

## 🆘 Troubleshooting

### Issue: CORS errors
**Fix:** Update `ALLOWED_ORIGINS` in environment variables with your Vercel URL

### Issue: WebSocket connection fails
**Fix:** Ensure WebSocket is enabled in Railway dashboard (Settings → Networking)

### Issue: Stripe payments fail
**Fix:** 
- Verify you're using test keys (sk_test_..., pk_test_...)
- Check Stripe Dashboard for failed payments
- Review Railway logs: `railway logs`

### Issue: Database errors
**Fix:** 
- Add PostgreSQL in Railway dashboard
- Copy connection string to DATABASE_URL
- Or use SQLite: `DATABASE_URL=sqlite:///data.db`

## 📊 Monitoring

### Railway Dashboard
```bash
# View logs
railway logs

# View metrics
railway status
```

### Stripe Dashboard
- View payments: https://dashboard.stripe.com/test/payments
- Monitor webhooks: https://dashboard.stripe.com/test/webhooks

## 🔒 Production Checklist

Before going live:

- [ ] Switch to Stripe production keys
- [ ] Update webhook URL to production domain
- [ ] Enable HTTPS (automatic on Railway/Vercel)
- [ ] Set strong JWT_SECRET (32+ random characters)
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/alerts
- [ ] Test complete user flow
- [ ] Review Stripe fraud protection settings

## 💰 Cost Estimation

**Free Tier (MVP):**
- Railway: $0 (within $5 credit)
- Vercel: $0 (within free tier)
- Stripe: $0 (pay-as-you-go, ~2.9% + 30¢ per transaction)
- Domain: $12/year (optional)

**Production (Estimated):**
- Railway: $5-20/month
- Vercel: $0-20/month
- Stripe: Transaction fees only
- Total: $5-40/month + transaction fees

## 🎯 Next Steps

1. **Customize branding** in `matrix-studio/web/frontend/src/branding.ts`
2. **Add your own scenes** to the Abyssal Bridge
3. **Configure streaming platforms** (YouTube, Twitch)
4. **Set up custom domain**
5. **Enable production Stripe keys**

## 📞 Support

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Stripe Docs:** https://stripe.com/docs
- **Project Issues:** Check GitHub Issues

---

**🎉 You're now live! Share your URL and start streaming!**
