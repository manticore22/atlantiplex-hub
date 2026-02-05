# Complete Payment API Documentation

## 🔗 Payment System API Reference

### Base URLs
- **Frontend:** `http://localhost:5173`
- **Backend API:** `http://localhost:9001`
- **Stripe Webhook:** `http://localhost:9001/api/webhooks/stripe`

---

## 📋 Authentication

### POST /api/login
Admin authentication for accessing protected endpoints.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "admin"
}
```

**Usage:**
```javascript
const response = await fetch('/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { token } = await response.json();
```

---

## 💳 Payment Processing

### POST /api/create-payment-intent
Create a payment intent for one-time payments or subscriptions.

**Headers:**
```
Content-Type: application/json
```

**Request:**
```json
{
  "amount": 29.99,
  "currency": "usd",
  "planId": "pro",
  "email": "customer@example.com"
}
```

**Response:**
```json
{
  "clientSecret": "pi_1Oxxx_secret_xxx..."
}
```

### GET /api/stripe-config
Get Stripe publishable key for frontend initialization.

**Response:**
```json
{
  "publishableKey": "pk_live_51StL0tEfu4UzsT8NLxPdKLoxXwYcZyBzZxYZaX..."
}
```

### GET /api/verify-payment
Verify payment status after completion.

**Query Parameters:**
- `payment_intent` (string): Payment Intent ID

**Response:**
```json
{
  "paymentIntent": {
    "id": "pi_1Oxxx...",
    "status": "succeeded",
    "amount": 2999,
    "currency": "usd"
  }
}
```

---

## 👥 Customer Management (Admin Only)

### POST /api/admin/create-customer
Create a new customer in Stripe.

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+15551234567"
}
```

**Response:**
```json
{
  "customer": {
    "id": "cus_xxxxxxxxxxxx",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+15551234567"
  }
}
```

### GET /api/admin/customers
List all customers with pagination.

**Query Parameters:**
- `limit` (number, default: 50): Number of customers to return
- `starting_after` (string): Cursor for pagination

**Response:**
```json
{
  "customers": [
    {
      "id": "cus_xxxxxxxxxxxx",
      "name": "John Doe",
      "email": "john@example.com",
      "created": 1640995200
    }
  ]
}
```

### GET /api/admin/customer-payment-methods/:customerId
Get payment methods for a specific customer.

**Response:**
```json
{
  "paymentMethods": [
    {
      "id": "pm_xxxxxxxxxxxx",
      "type": "card",
      "card": {
        "brand": "visa",
        "last4": "4242",
        "exp_month": 12,
        "exp_year": 2024
      }
    }
  ]
}
```

---

## 📋 Subscription Management (Admin Only)

### POST /api/admin/create-subscription
Create a new subscription for a customer.

**Request:**
```json
{
  "customerId": "cus_xxxxxxxxxxxx",
  "priceId": "price_1Oxxx...",
  "trialPeriodDays": 14
}
```

**Response:**
```json
{
  "subscription": {
    "id": "sub_xxxxxxxxxxxx",
    "customer": "cus_xxxxxxxxxxxx",
    "status": "trialing",
    "current_period_start": 1640995200,
    "current_period_end": 1641600000,
    "trial_end": 1641600000
  }
}
```

### GET /api/admin/subscriptions
List all subscriptions with filtering.

**Query Parameters:**
- `limit` (number, default: 50): Number of subscriptions
- `status` (string): Filter by status (active, trialing, canceled, etc.)

**Response:**
```json
{
  "subscriptions": [
    {
      "id": "sub_xxxxxxxxxxxx",
      "customer": {
        "id": "cus_xxxxxxxxxxxx",
        "email": "john@example.com"
      },
      "status": "active",
      "current_period_end": 1640995200,
      "plan": {
        "nickname": "Pro Plan",
        "amount": 2999
      }
    }
  ]
}
```

### POST /api/admin/cancel-subscription/:subscriptionId
Cancel a subscription.

**Request:**
```json
{
  "at_period_end": true
}
```

**Response:**
```json
{
  "subscription": {
    "id": "sub_xxxxxxxxxxxx",
    "status": "canceled",
    "cancel_at_period_end": true
  }
}
```

---

## 💰 Payment Operations (Admin Only)

### POST /api/admin/refund
Process a refund for a payment.

**Request:**
```json
{
  "paymentIntentId": "pi_1Oxxx...",
  "amount": 1500
}
```

**Response:**
```json
{
  "refund": {
    "id": "re_xxxxxxxxxxxx",
    "payment_intent": "pi_1Oxxx...",
    "amount": 1500,
    "status": "succeeded"
  }
}
```

### POST /api/admin/create-invoice
Create a manual invoice for a customer.

**Request:**
```json
{
  "customerId": "cus_xxxxxxxxxxxx",
  "description": "Custom service charge"
}
```

**Response:**
```json
{
  "invoice": {
    "id": "in_xxxxxxxxxxxx",
    "customer": "cus_xxxxxxxxxxxx",
    "amount_due": 5000,
    "status": "open"
  }
}
```

---

## 🛍️ Product Management (Admin Only)

### GET /api/admin/products
List all available products.

**Response:**
```json
{
  "products": [
    {
      "id": "prod_xxxxxxxxxxxx",
      "name": "Pro Plan",
      "description": "Professional features",
      "active": true,
      "default_price": {
        "id": "price_1Oxxx...",
        "unit_amount": 2999,
        "currency": "usd"
      }
    }
  ]
}
```

### GET /api/admin/prices
List all pricing options.

**Query Parameters:**
- `active` (boolean, default: true): Only active prices
- `product` (string): Filter by product ID

**Response:**
```json
{
  "prices": [
    {
      "id": "price_1Oxxx...",
      "product": "prod_xxxxxxxxxxxx",
      "unit_amount": 2999,
      "currency": "usd",
      "recurring": {
        "interval": "month"
      }
    }
  ]
}
```

### POST /api/admin/create-product
Create a new product.

**Request:**
```json
{
  "name": "Premium Plan",
  "description": "All premium features",
  "images": ["https://example.com/image.jpg"]
}
```

---

## 📊 Analytics (Admin Only)

### GET /api/admin/analytics
Get comprehensive analytics data.

**Response:**
```json
{
  "totalUsers": 100,
  "activeUsers": 25,
  "totalRevenue": 2999.00,
  "monthlyRevenue": 599.00,
  "totalTransactions": 50,
  "successfulTransactions": 45,
  "failedTransactions": 5,
  "balance": 1500.00,
  "plans": {
    "Free": 70,
    "Pro": 25,
    "Enterprise": 5
  }
}
```

---

## 🔔 Webhooks

### POST /api/webhooks/stripe
Handle Stripe webhook events.

**Headers:**
```
stripe-signature: v1=xxx...
```

**Supported Events:**
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `invoice.payment_succeeded`
- `customer.subscription.deleted`

**Event Examples:**

**Payment Success:**
```json
{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1Oxxx...",
      "status": "succeeded",
      "amount": 2999,
      "currency": "usd",
      "metadata": {
        "plan_id": "pro"
      }
    }
  }
}
```

---

## 🚨 Error Responses

All endpoints return consistent error format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## 🔧 Usage Examples

### Complete Payment Flow
```javascript
// 1. Get Stripe config
const { publishableKey } = await fetch('/api/stripe-config').then(r => r.json());

// 2. Create payment intent
const { clientSecret } = await fetch('/api/create-payment-intent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ amount: 29.99, planId: 'pro' })
}).then(r => r.json());

// 3. Confirm payment with Stripe Elements
const { error } = await stripe.confirmCardPayment(clientSecret);

// 4. Verify payment
const { paymentIntent } = await fetch(`/api/verify-payment?payment_intent=${pi_id}`).then(r => r.json());
```

### Admin Subscription Management
```javascript
// Get admin token
const { token } = await fetch('/api/login', {
  method: 'POST',
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
}).then(r => r.json());

// Create customer
const { customer } = await fetch('/api/admin/create-customer', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ name: 'John Doe', email: 'john@example.com' })
}).then(r => r.json());

// Create subscription
const { subscription } = await fetch('/api/admin/create-subscription', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ customerId: customer.id, priceId: 'price_1Oxxx...' })
}).then(r => r.json());
```

---

## 🔒 Security Notes

- All admin endpoints require JWT authentication
- Webhooks use Stripe signature verification
- Payment data never touches your servers (PCI compliant)
- Rate limiting recommended for production
- HTTPS required for live webhooks

## 📈 Rate Limits

Recommended limits:
- Payment Intents: 100/minute per IP
- Admin API: 60/minute per user
- Webhooks: Process within 30 seconds

---

**API Version:** v1.0.0  
**Last Updated:** 2026-02-05  
**Environment:** Development/Test