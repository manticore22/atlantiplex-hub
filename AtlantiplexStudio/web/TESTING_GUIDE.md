# Payment System Testing Guide

## 🧪 Complete Testing Suite Ready!

### Quick Start Testing

**1. Start Your Servers:**
```bash
# Backend (port 9001)
cd "C:\Users\User\Desktop\atlantiplex hub\matrix-studio\web\stage"
npm start

# Frontend (port 5173) - in separate terminal
cd "C:\Users\User\Desktop\atlantiplex hub\matrix-studio\web\frontend"
npm start
```

**2. Access Test Runner:**
- Navigate to: `http://localhost:5173/?testing=true`
- Or add to your App.jsx routing

**3. Run Tests:**
- Click "🚀 Run All Tests" for complete suite
- Or click individual test categories

---

## 📋 Test Categories

### 🔐 Authentication Tests
- Admin login verification
- Token validation
- Role-based access control

### 💳 Payment Processing Tests
- Payment intent creation
- Invalid amount handling
- Stripe configuration verification

### 👥 Customer Management Tests
- Customer creation
- Customer listing
- Payment method retrieval

### 📋 Subscription Tests
- Subscription creation
- Subscription listing
- Cancellation workflows

### 💰 Refund Tests
- Refund processing
- Error handling for invalid payments
- Partial refund support

### 📊 Analytics Tests
- Revenue calculations
- User statistics
- Transaction metrics

### 🚨 Error Handling Tests
- Unauthorized access blocking
- Invalid request handling
- Server error responses

### ⚡ Performance Tests
- Response time measurement
- Concurrent request handling
- Load testing

---

## 🎯 Manual Testing Checklist

### Frontend Payment Flow
1. **Navigate to:** `http://localhost:5173/?payment=true`
2. **Test Plan Selection:**
   - Click "Subscribe to Plans"
   - Select Free, Pro, or Enterprise plan
   - Verify pricing displays correctly

3. **Test Payment Form:**
   - Enter test card: `4242 4242 4242 4242`
   - Expiry: `12/34`
   - CVC: `123`
   - Email: `test@example.com`
   - Click "Pay $29.99"

4. **Verify Success:**
   - Redirect to success page
   - Display receipt information
   - Check Stripe Dashboard for transaction

### Admin Dashboard Testing
1. **Navigate to:** `http://localhost:5173/?admin=true`
2. **Login:** `admin` / `admin123`
3. **Test Each Tab:**
   - Dashboard: Verify analytics display
   - Users: Test user management
   - Subscriptions: Test subscription operations

### API Testing (Postman/curl)
```bash
# Test authentication
curl -X POST http://localhost:9001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test payment intent
curl -X POST http://localhost:9001/api/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{"amount":29.99,"currency":"usd","planId":"pro"}'

# Test admin analytics (with token)
curl -X GET http://localhost:9001/api/admin/analytics \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔧 Environment Setup

### Required Environment Variables (.env)
```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_51StL0tEfu4UzsT8NLxJp5WlyO45dPy6SY6nLpQ1jyI3IIH43hoNyamPthJbZd0KmBoSRllfdWZCkbsJCCACdfgPK00K8a4QbOd
STRIPE_PUBLISHABLE_KEY=pk_test_51StL0tEfu4UzsT8NLxPdKLoxXwYcZyBzZxYZaXwYcZyBzZxYZaXwYcZyBzZxYZaXwYcZyBzZxYZaXwYcZyBzZxYZaX
STRIPE_WEBHOOK_SECRET=whsec_test_... # Get from Stripe webhook setup

# Server Configuration
NODE_ENV=development
PORT=3000
JWT_SECRET=dev-jwt-secret-key
```

### Test Cards (Stripe Test Mode)
```
Successful Payment: 4242 4242 4242 4242
Card Declined:      4000 0000 0000 0002
Insufficient Funds: 4000 0000 0000 9995
Expired Card:       4000 0000 0000 0069
```

---

## 📊 Expected Test Results

### Successful Test Suite Should Show:
- ✅ Authentication: Token received
- ✅ Stripe Config: Publishable key available
- ✅ Payment Intent: Client secret generated
- ✅ Customer Creation: Customer ID returned
- ✅ Subscription Management: Operations successful
- ✅ Analytics: Data retrieved
- ✅ Error Handling: Proper rejections
- ✅ Performance: Response times < 1000ms

### Common Issues & Solutions:

**"No token provided" Error:**
- Ensure admin login before accessing protected endpoints
- Check token is included in Authorization header

**"Stripe error" in payment tests:**
- Verify STRIPE_SECRET_KEY is correct
- Check if you're in test mode (use sk_test_ keys)

**"Webhook signature verification failed":**
- Expected behavior for test webhooks
- Real webhooks work with proper signatures

**"Connection refused":**
- Ensure backend server is running on port 9001
- Check firewall settings

---

## 🚀 Production Testing

### Before Going Live:
1. **Switch to Live Keys:**
   - Update `.env` with `sk_live_` and `pk_live_` keys
   - Test with small amounts first

2. **Webhook Setup:**
   - Configure HTTPS endpoint
   - Set up production webhooks in Stripe
   - Test webhook delivery

3. **Security Testing:**
   - Verify rate limiting works
   - Test authentication bypasses
   - Check for sensitive data exposure

4. **Load Testing:**
   - Test with concurrent users
   - Monitor response times
   - Verify error handling under load

---

## 📈 Monitoring & Logging

### Built-in Monitoring:
- Request logging with timestamps
- Rate limiting protection
- Error tracking and reporting
- Performance metrics

### Log Examples:
```
[2026-02-05T10:30:00.000Z] POST /api/login - IP: 127.0.0.1
[2026-02-05T10:30:01.000Z] POST /api/create-payment-intent - IP: 127.0.0.1
Request body: {"amount":29.99,"currency":"usd","planId":"pro"}
[2026-02-05T10:30:02.000Z] GET /api/admin/analytics - IP: 127.0.0.1
```

---

## 🎯 Success Criteria

Your payment system is ready when:

✅ **All Tests Pass:** 100% success rate in test runner
✅ **Payment Flow Works:** End-to-end payment completes
✅ **Admin Functions:** All admin operations work
✅ **Error Handling:** Graceful failure handling
✅ **Security:** Authentication and authorization work
✅ **Performance:** Response times under 1 second
✅ **Documentation:** API docs complete and accurate

---

## 🆘 Troubleshooting

**Test Runner Not Loading:**
- Ensure `test-payment-system.js` is in web root
- Check browser console for script errors
- Verify frontend server is running

**Backend Tests Failing:**
- Check backend server logs
- Verify environment variables
- Ensure Stripe keys are valid

**Payment Tests Failing:**
- Use test mode Stripe keys
- Check webhook configuration
- Verify test card numbers

**Admin Tests Failing:**
- Ensure admin user exists
- Check JWT secret configuration
- Verify token format

---

**Your complete payment testing suite is ready!** 🎉

Access the interactive test runner and start verifying your payment system works perfectly!