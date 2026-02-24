Stripe Storefront — Quick Start

- Goal: A storefront with free and paid subscriptions, plus a gateway for lore and access.
- Endpoints:
  - GET /prices: catalog (free/paid)
  - POST /create-checkout-session: { priceIds, customer_email }
  - GET /account?email=...: entitlements
- Setup: ensure STRIPE_SECRET is set on the backend, and prices exist on Stripe for paid items.
- To start: open /index.html and use the UI to select items and proceed to checkout.
