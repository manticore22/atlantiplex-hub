# Enhanced Matrix Studio - Payment Integration Setup
# ATLANTIPLEX MATRIX STUDIO WITH STRIPE PAYMENTS AND ADMIN BYPASS

## 🎯 Overview

Your Atlantiplex Matrix Studio has been enhanced with:
- ✅ **Stripe Payment Integration** - Professional billing system
- ✅ **Admin Bypass Access** - Login: `manticore` / `patriot8812` (Unlimited)
- ✅ **Subscription Tiers** - Free, Starter ($9.99), Professional ($29.99), Enterprise ($99.99)
- ✅ **Feature-Based Access Control** - Tier-limited functionality
- ✅ **Usage Tracking & Analytics** - Monitor resource consumption
- ✅ **Database Integration** - Complete payment and subscription management

## 🔑 Access Credentials

### Admin Access (Unrestricted)
- **Username**: `manticore`
- **Password**: `patriot8812`
- **Access**: All features unlocked, unlimited usage, free

### Demo Access (Limited)
- **Username**: `demo`
- **Password**: `demo123`
- **Access**: Basic tier features, 3 guests max

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_payments.txt
```

### 2. Set Environment Variables
```bash
# Stripe Configuration
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# Security
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret"

# Database
export DATABASE_URL="sqlite:///matrix_studio.db"
```

### 3. Run Enhanced Application
```bash
python enhanced_app.py
```

### 4. Access Points
- **Main App**: http://localhost:8081
- **API Health**: http://localhost:8081/api/health
- **Login API**: http://localhost:8081/api/auth/login

## 📋 Subscription Tiers

### Free Tier
- 1 concurrent guest
- SD streaming quality
- Basic scenes only
- 3 sessions per day

### Starter Tier - $9.99/month
- 3 concurrent guests
- HD streaming quality
- Premium scenes
- Email support

### Professional Tier - $29.99/month
- 10 concurrent guests
- Full HD streaming
- Custom scenes + API access
- Priority support

### Enterprise Tier - $99.99/month
- 50 concurrent guests
- 4K streaming quality
- White-label + reseller
- 24/7 phone support

## 🔐 Admin Bypass System

The admin user (`manticore`/`patriot8812`) has:
- **Unlimited Access**: All features unlocked
- **Free Usage**: No payment processing required
- **Full Control**: Manage all users and subscriptions
- **System Admin**: Complete backend access

## 💳 Payment Integration Features

### Stripe Integration
- ✅ Checkout sessions for subscriptions
- ✅ Billing portal for customer management
- ✅ Webhook processing for real-time updates
- ✅ Automatic subscription management
- ✅ Payment history and invoices

### API Endpoints
```
POST /api/auth/login           # User authentication
GET  /api/subscriptions/tiers  # Available tiers
GET  /api/subscriptions/current # User's subscription
POST /api/payments/checkout    # Create payment
POST /api/payments/billing-portal # Customer portal
POST /api/payments/webhook     # Stripe webhooks
GET  /api/usage/stats          # Usage analytics
```

## 📊 Usage Tracking

The system tracks:
- Guest sessions and limits
- Streaming quality and duration
- Feature access attempts
- Bandwidth and storage usage
- Payment history and subscriptions

## 🗄️ Database Schema

Enhanced database includes:
- `users` - User accounts and roles
- `subscriptions` - Subscription management
- `payments` - Payment transactions
- `usage_tracking` - Resource usage
- `guest_sessions` - Guest management
- `streaming_sessions` - Streaming logs
- `webhook_events` - Stripe events

## 🔧 Configuration Files

### Key Files Created:
1. **`stripe_payments.py`** - Stripe payment integration
2. **`admin_auth.py`** - Admin bypass authentication
3. **`subscription_manager.py`** - Tier management
4. **`database_payments.py`** - Database schema
5. **`payment_api.py`** - Payment API routes
6. **`enhanced_app.py`** - Main enhanced application

### Environment Variables:
- `STRIPE_SECRET_KEY` - Your Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Webhook signing secret
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT token secret
- `DATABASE_URL` - Database connection string

## 🚀 Deployment Ready

### Oracle Cloud Deployment
Use the existing deployment files with enhanced configuration:
```bash
# Update docker-compose.yml with payment dependencies
# Deploy with: ./deploy-oracle-cloud.sh
```

### Domain Configuration
Your system is ready for:
- **Domain**: verilysovereign.org
- **SSL**: Automatic Let's Encrypt certificates
- **Payment Processing**: Live Stripe integration
- **Admin Access**: Unrestricted backend control

## 🔒 Security Features

- JWT-based authentication
- Admin bypass for unrestricted access
- Feature-based access control
- Payment processing via Stripe (PCI compliant)
- Usage monitoring and limits
- Webhook signature verification

## 📈 Monetization Ready

Your Matrix Studio can now:
- Accept payments via Stripe
- Manage recurring subscriptions
- Control feature access by tier
- Track usage and billing
- Provide customer billing portal
- Handle automatic subscription management

## 🎮 Usage Examples

### Admin Login (Unlimited Access)
```bash
curl -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "manticore", "password": "patriot8812"}'
```

### Create Subscription Payment
```bash
curl -X POST http://localhost:8081/api/payments/checkout \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tier": "professional", "success_url": "https://verilysovereign.org/success", "cancel_url": "https://verilysovereign.org/cancel"}'
```

## 🎯 Next Steps

1. **Setup Stripe Account**: Get API keys from stripe.com
2. **Configure Environment**: Set all environment variables
3. **Test Payments**: Use Stripe test mode
4. **Deploy to Oracle Cloud**: Use existing deployment files
5. **Configure Domain**: Point verilysovereign.org to your server
6. **Go Live**: Switch to Stripe live mode

Your Atlantiplex Matrix Studio is now a professional, monetizable broadcasting platform with unlimited admin access!