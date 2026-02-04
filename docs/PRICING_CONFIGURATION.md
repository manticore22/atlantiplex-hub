# Atlantiplex Lightning Studio - Pricing & Payment Configuration

## 💰 Pricing Tiers Overview

### Current Pricing Structure

| Tier | Monthly | Annual (Save 20%) | Guests | Quality | Support |
|------|---------|-------------------|--------|---------|---------|
| **Free** | $0 | $0 | 1 | SD | Community |
| **Starter** | $9.99 | $95.90 | 3 | HD | Email |
| **Professional** | $29.99 | $287.90 | 10 | Full HD | Priority |
| **Enterprise** | $99.99 | $959.90 | 50 | 4K | 24/7 Phone |

---

## 🔧 Stripe Configuration

### Step 1: Create Products in Stripe Dashboard

1. Go to https://dashboard.stripe.com/products
2. Create the following products:

#### Starter Plan
```
Product Name: Atlantiplex Starter
Description: Perfect for small creators - 3 guests, HD streaming
```

Create TWO prices:
- **Monthly**: $9.99 USD, Recurring, Monthly
- **Yearly**: $95.90 USD, Recurring, Yearly

#### Professional Plan
```
Product Name: Atlantiplex Professional
Description: For serious streamers - 10 guests, Full HD, API access
```

Create TWO prices:
- **Monthly**: $29.99 USD, Recurring, Monthly
- **Yearly**: $287.90 USD, Recurring, Yearly

#### Enterprise Plan
```
Product Name: Atlantiplex Enterprise
Description: For businesses - 50 guests, 4K, white-label
```

Create TWO prices:
- **Monthly**: $99.99 USD, Recurring, Monthly
- **Yearly**: $959.90 USD, Recurring, Yearly

### Step 2: Update Price IDs

After creating prices in Stripe, copy the Price IDs and update them in:

**File: `matrix-studio/pricing_endpoints.py`**

```python
'starter': {
    'stripe_price_id': 'price_XXXXXXXXXXXXXX',  # Replace with actual ID
    ...
}
```

**File: `matrix-studio/subscription_manager.py`**

```python
'stripe_price_id': 'price_XXXXXXXXXXXXXX',  # Replace with actual ID
```

### Step 3: Configure Stripe Keys

Add to your `.env` or environment variables:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_XXXXXXXXXXXXXX
STRIPE_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXX
```

For testing, use test keys:
```env
STRIPE_SECRET_KEY=sk_test_XXXXXXXXXXXXXX
STRIPE_PUBLISHABLE_KEY=pk_test_XXXXXXXXXXXXXX
```

---

## 🅿️ PayPal Configuration

### Step 1: Create PayPal App

1. Go to https://developer.paypal.com/dashboard/
2. Create a new app
3. Get Client ID and Secret

### Step 2: Create Subscription Plans

Using PayPal's API or dashboard, create plans:

#### Create Product
```bash
curl -X POST https://api-m.sandbox.paypal.com/v1/catalogs/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{
    "name": "Atlantiplex Professional",
    "description": "Professional streaming plan",
    "type": "SERVICE",
    "category": "SOFTWARE"
  }'
```

#### Create Plan
```bash
curl -X POST https://api-m.sandbox.paypal.com/v1/billing/plans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{
    "product_id": "PRODUCT_ID_FROM_ABOVE",
    "name": "Professional Monthly",
    "description": "Professional plan - monthly billing",
    "billing_cycles": [
      {
        "frequency": {
          "interval_unit": "MONTH",
          "interval_count": 1
        },
        "tenure_type": "REGULAR",
        "sequence": 1,
        "total_cycles": 0,
        "pricing_scheme": {
          "fixed_price": {
            "value": "29.99",
            "currency_code": "USD"
          }
        }
      }
    ],
    "payment_preferences": {
      "auto_bill_outstanding": true,
      "setup_fee": {
        "value": "0",
        "currency_code": "USD"
      },
      "setup_fee_failure_action": "CONTINUE",
      "payment_failure_threshold": 3
    }
  }'
```

### Step 3: Update PayPal Configuration

Add to your `.env`:

```env
# PayPal Configuration
PAYPAL_CLIENT_ID=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
PAYPAL_CLIENT_SECRET=EXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
PAYPAL_MODE=sandbox  # Change to 'live' for production
```

Update plan IDs in `pricing_endpoints.py`:

```python
'professional': {
    'paypal_plan_id': 'P-XXXXXXXXXXXXXXXXXXXX',  # Replace with actual ID
    ...
}
```

---

## 🎯 Available API Endpoints

### Get All Pricing Plans
```
GET /api/v1/pricing/plans
GET /api/v1/pricing/plans?interval=year
```

Response:
```json
{
  "success": true,
  "billing_interval": "month",
  "plans": [
    {
      "id": "starter",
      "name": "Starter",
      "price": 9.99,
      "currency": "usd",
      "interval": "month",
      "features": [...],
      "stripe_price_id": "price_XXX",
      "paypal_plan_id": "P-XXX"
    }
  ]
}
```

### Get Plan Details
```
GET /api/v1/pricing/plans/{plan_id}
GET /api/v1/pricing/plans/professional?interval=year
```

### Compare All Plans
```
GET /api/v1/pricing/compare
```

Response includes detailed feature matrix comparing all tiers.

### Calculate Price with Discount
```
POST /api/v1/pricing/calculate
Content-Type: application/json

{
  "plan_id": "professional",
  "interval": "year",
  "coupon_code": "WELCOME20"
}
```

### Validate Coupon
```
POST /api/v1/pricing/validate-coupon
Content-Type: application/json

{
  "coupon_code": "WELCOME20"
}
```

Valid coupons:
- `WELCOME20` - 20% off first month
- `ANNUAL30` - 30% off annual plans
- `ENTERPRISE50` - 50% off Enterprise
- `STUDENT40` - 40% off for students

### Create Stripe Checkout
```
POST /api/v1/pricing/checkout/stripe
Content-Type: application/json

{
  "plan_id": "professional",
  "email": "user@example.com",
  "success_url": "https://yoursite.com/success",
  "cancel_url": "https://yoursite.com/cancel",
  "interval": "month"
}
```

Response:
```json
{
  "success": true,
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_XXXXX",
  "stripe_price_id": "price_XXXXX"
}
```

### Get PayPal Checkout
```
POST /api/v1/pricing/checkout/paypal
Content-Type: application/json

{
  "plan_id": "professional",
  "interval": "month"
}
```

Response:
```json
{
  "success": true,
  "paypal_plan_id": "P-XXXXX",
  "plan_details": {
    "name": "Professional",
    "price": 29.99,
    "currency": "usd",
    "interval": "month"
  }
}
```

### Get All Features
```
GET /api/v1/pricing/features
```

Returns detailed feature list with tier availability.

---

## 🔄 Webhook Configuration

### Stripe Webhook

Configure webhook endpoint in Stripe Dashboard:

**Endpoint URL**: `https://yourdomain.com/api/v1/pricing/webhook/stripe`

**Events to listen for**:
- `checkout.session.completed`
- `invoice.paid`
- `invoice.payment_failed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

### PayPal Webhook

Configure webhook in PayPal Dashboard:

**Endpoint URL**: `https://yourdomain.com/api/v1/pricing/webhook/paypal`

**Events to listen for**:
- `BILLING.SUBSCRIPTION.CREATED`
- `BILLING.SUBSCRIPTION.ACTIVATED`
- `BILLING.SUBSCRIPTION.UPDATED`
- `BILLING.SUBSCRIPTION.EXPIRED`
- `BILLING.SUBSCRIPTION.CANCELLED`
- `BILLING.SUBSCRIPTION.SUSPENDED`
- `BILLING.SUBSCRIPTION.PAYMENT.FAILED`

---

## 📊 Tier Limits Summary

| Feature | Free | Starter | Professional | Enterprise |
|---------|------|---------|--------------|------------|
| **Guests** | 1 | 3 | 10 | 50 |
| **Quality** | SD (480p) | HD (720p) | Full HD (1080p) | 4K Ultra HD |
| **Platforms** | YouTube | YouTube, Twitch | 4 platforms | All 6 platforms |
| **Bandwidth** | 10GB/mo | 100GB/mo | 500GB/mo | 2TB/mo |
| **Storage** | None | 10GB | 100GB | 1TB |
| **API Access** | ❌ | ❌ | ✅ | ✅ |
| **Custom Branding** | ❌ | ❌ | ✅ | ✅ |
| **White Label** | ❌ | ❌ | ❌ | ✅ |
| **Support** | Community | Email | Priority Email | 24/7 Phone |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install stripe paypal-rest-sdk
```

### 2. Register Blueprint
In your main app file:

```python
from pricing_endpoints import register_pricing_routes

app = Flask(__name__)
register_pricing_routes(app)
```

### 3. Test Endpoints

Test the pricing API:
```bash
curl http://localhost:5000/api/v1/pricing/plans
```

Test checkout creation:
```bash
curl -X POST http://localhost:5000/api/v1/pricing/checkout/stripe \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "starter",
    "email": "test@example.com",
    "success_url": "http://localhost:5000/success",
    "cancel_url": "http://localhost:5000/cancel"
  }'
```

---

## ⚠️ Important Notes

1. **Free Tier**: No payment required, but limited features
2. **Trial Period**: Consider offering 14-day free trial for paid plans
3. **Proration**: Handle plan upgrades/downgrades with proration
4. **Cancellation**: Allow users to cancel anytime, keep access until period ends
5. **Failed Payments**: Implement grace period and retry logic
6. **Tax**: Configure tax collection based on user location
7. **Currency**: Currently USD only, can add more currencies

---

## 📞 Support

For payment integration issues:
- Stripe Docs: https://stripe.com/docs
- PayPal Docs: https://developer.paypal.com/docs/
- Webhook testing: https://webhook.site/