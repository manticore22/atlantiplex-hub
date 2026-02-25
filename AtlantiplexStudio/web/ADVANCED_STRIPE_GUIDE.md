# Advanced Stripe Server Operations Guide

## 🚀 Server-Side Stripe Implementation Complete!

### ✅ New Admin Endpoints Added

**Customer Management:**
- `POST /api/admin/create-customer` - Create new customers
- `GET /api/admin/customers` - List all customers
- `GET /api/admin/customer-payment-methods/:customerId` - Get payment methods

**Subscription Management:**
- `POST /api/admin/create-subscription` - Create subscriptions
- `GET /api/admin/subscriptions` - List subscriptions
- `POST /api/admin/cancel-subscription/:id` - Cancel subscriptions

**Payment Operations:**
- `POST /api/admin/refund` - Process refunds
- `POST /api/admin/create-invoice` - Create invoices

**Product & Pricing:**
- `GET /api/admin/prices` - List all prices
- `POST /api/admin/create-product` - Create products
- `GET /api/admin/products` - List products

### 🔧 Advanced Features

**Subscription Creation:**
```javascript
// Create subscription with trial
await stripe.subscriptions.create({
  customer: 'cus_...',
  items: [{ price: 'price_...' }],
  trial_period_days: 14,
  payment_behavior: 'default_incomplete',
  metadata: { created_by: 'admin' }
});
```

**Customer Management:**
```javascript
// Create customer with metadata
await stripe.customers.create({
  name: 'John Doe',
  email: 'john@example.com',
  phone: '+1234567890',
  metadata: { source: 'admin_panel' }
});
```

**Refund Processing:**
```javascript
// Full or partial refund
await stripe.refunds.create({
  payment_intent: 'pi_...',
  amount: 1500, // Optional - full refund if omitted
  reason: 'requested_by_customer'
});
```

### 🎯 Usage Examples

**Access Subscription Management:**
- Navigate to: `http://localhost:5173/?admin=true`
- Click "Subscriptions" tab
- Create customers, manage subscriptions, process refunds

**Create Test Products:**
```javascript
// In Stripe Dashboard, create products first, then get price IDs
const priceOptions = [
  { id: 'price_1PRO...', name: 'Pro Plan - $29.99/month' },
  { id: 'price_1ENT...', name: 'Enterprise - $99.99/month' }
];
```

**Test Subscription Flow:**
1. Create customer in admin panel
2. Create subscription for customer
3. Check Stripe Dashboard → Customers
4. Monitor webhooks for events

### 🔒 Security & Auditing

**All operations include:**
- Admin JWT authentication
- Metadata tracking (created_by, processed_by)
- Error handling and logging
- Request validation

**Audit Trail:**
```javascript
metadata: {
  created_by: req.user.username,
  source: 'admin_panel',
  timestamp: new Date().toISOString()
}
```

### 📊 Integration Points

**Frontend Components:**
- `SubscriptionManager.jsx` - Full subscription UI
- `AdminDashboard.jsx` - Updated with subscription tab
- Real-time updates and error handling

**Backend Integration:**
- Server-side Stripe API calls with secret key
- Comprehensive error handling
- Webhook support for events
- Database-ready structure

### 🧪 Testing

**Test Operations:**
- Use test keys in `.env` file
- Create test customers/subscriptions
- Test refund workflows
- Verify webhook events

**Sample Test Data:**
```javascript
// Test customer creation
POST /api/admin/create-customer
{
  "name": "Test User",
  "email": "test@example.com",
  "phone": "+15551234567"
}
```

### 🚀 Production Deployment

**Required Environment Variables:**
```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Security Checklist:**
- [ ] Use live API keys
- [ ] Set up HTTPS webhooks
- [ ] Enable logging
- [ ] Monitor rate limits
- [ ] Set up billing alerts

Your advanced Stripe server operations are now complete! 🎉

Access the full subscription management interface at:
**Admin Dashboard → Subscriptions Tab**