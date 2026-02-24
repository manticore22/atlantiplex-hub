# SERAPHONIX + ATLANTIPLEX STUDIO

Complete Docker deployment with Seraphonix Gateway and Atlantiplex Studio streaming platform.

## Architecture

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (Port 80)  │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌────────────┐  ┌───────────┐  ┌──────────────┐
    │  Seraphonix│  │  API      │  │ Atlantiplex │
    │  Frontend  │  │  (Auth)   │  │  Studio     │
    │  (Static)  │  │  (3000)   │  │  (5000)     │
    └────────────┘  └───────────┘  └──────────────┘
```

## URLs After Deployment

| Route | Service |
|-------|---------|
| `https://verilysovereign.org/` | Seraphonix Gateway |
| `https://verilysovereign.org/api/*` | Seraphonix API |
| `https://verilysovereign.org/atlantiplex/*` | Atlantiplex Studio |

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:
- `JWT_SECRET` - Your JWT secret
- `STRIPE_SECRET` - Stripe API key
- Domain name

### 2. Build & Run

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Access

- **Seraphonix Gateway**: http://localhost (or your domain)
- **Atlantis Studio**: http://localhost/atlantiplex/
- **API**: http://localhost/api/health

## Membership Tiers

| Tier | Price | Guests | Hours | Resolution |
|------|-------|--------|-------|------------|
| Initiate | $0/mo | 2 | 16/mo | 720p |
| Ascendant | $9.99/mo | 6 | 70/mo | 1080p |
| Covenant | $29/mo | 6 | Unlimited | 1080p |
| Infinite Relay | $70/mo | 8 | Unlimited | 4K |

## Tier Features

- **Initiate**: Basic streaming, YouTube/Twitch
- **Ascendant**: 1080p, 70+ hours, Multistream, AI Tools
- **Covenant**: Unlimited, Priority Support, Custom RTMP
- **Infinite Relay**: 4K, White-label, Full AI Suite

## Stripe Configuration

1. Create products in Stripe Dashboard
2. Get Price IDs for each tier
3. Update `verilysovereign-backend/server.js`:

```javascript
const PRICES = {
    'ascendant': 'price_xxx',
    'covenant': 'price_yyy',
    'infinite': 'price_zzz'
};
```

## SSL/TLS

```bash
# Get SSL certificates
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d verilysovereign.org
```

## Troubleshooting

```bash
# Check logs
docker-compose logs -f seraphonix-api
docker-compose logs -f atlantiplex

# Restart services
docker-compose restart

# Rebuild
docker-compose up -d --build
```

## Project Structure

```
.
├── verilysovereign/           # Seraphonix frontend
│   ├── index.html            # Gateway
│   ├── atlantiplex.html      # Studio link
│   ├── login.html            # Sign in
│   ├── signup.html           # Sign up
│   ├── membership.html       # Subscription tiers
│   ├── styles/              # CSS
│   └── images/              # Logos
├── verilysovereign-backend/ # API server
│   ├── server.js             # Express API
│   ├── data/                # User/Subscription data
│   └── integration/         # Atlantiplex integration
├── AtlantiplexStudio/       # Streaming platform
│   ├── app.py               # Flask app
│   └── web/                 # Frontend
├── docker-compose.yml       # Orchestration
└── nginx.conf               # Reverse proxy
```
