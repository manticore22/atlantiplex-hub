# Stripe storefront API surface (MVP)

- GET /prices
  - Returns the catalog of items, including free and paid entries.
- POST /create-checkout-session
  - Body: { priceIds: string[], customer_email?: string }
  - Paid path: Creates a Stripe Checkout session and returns { id, url }
  - Free path: Grants access to the requested free items and returns { id, free: true, next: '/account?email=...'}
- GET /account?email=...
  - Returns entitlements for the given email, e.g. { email, entitlements: [...] }
- GET /lore
  - Renders lore content as HTML
- GET /lore-content
  - Returns lore content as JSON

Notes
- This MVP backend stores entitlements in memory / files. For production, replace with a database and authentication layer.
- Webhook handling scaffolding is included for Stripe events; you should add signature verification in production.
