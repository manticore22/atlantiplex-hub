"""
Simple Enhanced Matrix Studio with Full Stripe Integration
Includes payment processing, subscription tiers, and admin bypass
"""

from flask import Flask, request, jsonify, g
import jwt
import hashlib
import logging
from datetime import datetime, timedelta
import sqlite3
import json
import os
import secrets

# Try to import stripe
try:
    import stripe
    stripe_available = True
except ImportError:
    stripe = None
    stripe_available = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StripeEnhancedMatrixStudio:
    """Matrix Studio with full Stripe payment integration"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.update({
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'matrix-studio-secret-key'),
            'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key'),
            'STRIPE_SECRET_KEY': os.environ.get('STRIPE_SECRET_KEY', 'sk_test_51234567890abcdef'),
            'STRIPE_PUBLISHABLE_KEY': os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_51234567890abcdef'),
            'STRIPE_WEBHOOK_SECRET': os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_test_...'),
            'DOMAIN': os.environ.get('DOMAIN', 'http://localhost:8081')
        })
        
        # Initialize Stripe
        if stripe_available and self.app.config['STRIPE_SECRET_KEY']:
            stripe.api_key = self.app.config['STRIPE_SECRET_KEY']
        
        self.init_database()
        self.register_routes()
    
    def init_database(self):
        """Initialize database with payment tables"""
        self.db_path = "matrix_studio_stripe.db"
        
        with sqlite3.connect(self.db_path) as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'user',
                    tier TEXT DEFAULT 'free',
                    stripe_customer_id TEXT,
                    stripe_subscription_id TEXT,
                    subscription_status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Guest sessions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS guest_sessions (
                    id INTEGER PRIMARY KEY,
                    host_user_id INTEGER,
                    guest_name TEXT,
                    guest_email TEXT,
                    invite_code TEXT UNIQUE,
                    session_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Payments
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    stripe_payment_intent_id TEXT,
                    amount_cents INTEGER,
                    currency TEXT DEFAULT 'usd',
                    status TEXT,
                    description TEXT,
                    tier TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Subscription tiers configuration
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscription_tiers (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    price_cents INTEGER,
                    currency TEXT DEFAULT 'usd',
                    billing_interval TEXT DEFAULT 'month',
                    stripe_price_id TEXT,
                    features TEXT,
                    limits TEXT,
                    max_concurrent_guests INTEGER DEFAULT 1,
                    max_quality TEXT DEFAULT 'SD',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
        # Insert default tiers with final pricing structure
        tiers = [
            {
                'name': 'free',
                'display_name': 'Free',
                'price_cents': 0,
                'billing_interval': 'month',
                'stripe_price_id': None,
                'features': json.dumps([
                    'Up to 15 hours of streaming per month',
                    '1–2 guests',
                    '720p streaming',
                    'Platform watermark',
                    'Basic overlays',
                    'Limited recording',
                    '1 streaming destination'
                ]),
                'limits': json.dumps({
                    'max_guests': 2,
                    'streaming_hours_per_month': 15,
                    'max_quality': '720p',
                    'max_destinations': 1,
                    'watermark': True,
                    'recording_hours_per_month': 10,
                    'bandwidth_gb': 20
                }),
                'max_concurrent_guests': 2,
                'max_quality': '720p'
            },
            {
                'name': 'basic',
                'display_name': 'Basic',
                'price_cents': 1200,  # $12.00
                'billing_interval': 'month',
                'stripe_price_id': 'price_basic_monthly',
                'features': json.dumps([
                    'Up to 4 guests',
                    '1080p streaming',
                    'Remove watermark',
                    'Custom branding (colors, logos)',
                    'Increased recording hours',
                    '2–3 streaming destinations',
                    'Basic scene switching'
                ]),
                'limits': json.dumps({
                    'max_guests': 4,
                    'streaming_hours_per_month': float('inf'),
                    'max_quality': '1080p',
                    'max_destinations': 3,
                    'watermark': False,
                    'recording_hours_per_month': 50,
                    'branding': True,
                    'bandwidth_gb': 100
                }),
                'max_concurrent_guests': 4,
                'max_quality': '1080p'
            },
            {
                'name': 'pro',
                'display_name': 'Pro',
                'price_cents': 1900,  # $19.00
                'billing_interval': 'month',
                'stripe_price_id': 'price_pro_monthly',
                'features': json.dumps([
                    'Up to 8 guests',
                    'Full branding (overlays, backgrounds, stingers)',
                    'High or unlimited recording',
                    'Multistreaming to 5–8 destinations',
                    'Local recordings',
                    'Audio cleanup tools',
                    'Custom RTMP'
                ]),
                'limits': json.dumps({
                    'max_guests': 8,
                    'streaming_hours_per_month': float('inf'),
                    'max_quality': '1080p',
                    'max_destinations': 8,
                    'watermark': False,
                    'recording_hours_per_month': float('inf'),
                    'branding': True,
                    'advanced_tools': True,
                    'custom_rtmp': True,
                    'bandwidth_gb': 500
                }),
                'max_concurrent_guests': 8,
                'max_quality': '1080p'
            },
            {
                'name': 'enterprise',
                'display_name': 'Enterprise',
                'price_cents': 12500,  # $125.00 average ($100-150/year)
                'billing_interval': 'year',
                'stripe_price_id': 'price_enterprise_yearly',
                'features': json.dumps([
                    'Unlimited guests',
                    'Unlimited recording',
                    'Unlimited destinations',
                    'Full branding + white-label',
                    'Priority support',
                    'API access',
                    'Optional 4K streaming'
                ]),
                'limits': json.dumps({
                    'max_guests': float('inf'),
                    'streaming_hours_per_month': float('inf'),
                    'max_quality': '4K',
                    'max_destinations': float('inf'),
                    'watermark': False,
                    'recording_hours_per_month': float('inf'),
                    'branding': True,
                    'white_label': True,
                    'api_access': True,
                    'priority_support': True,
                    'bandwidth_gb': float('inf')
                }),
                'max_concurrent_guests': float('inf'),
                'max_quality': '4K'
            },
            {
                'name': 'unlimited',
                'display_name': 'Admin Unlimited',
                'price_cents': 0,
                'billing_interval': 'month',
                'stripe_price_id': None,
                'features': json.dumps([
                    'Unlimited concurrent guests',
                    '8K streaming quality',
                    'All features unlocked',
                    'Admin access',
                    'Full system control',
                    'No payment processing required'
                ]),
                'limits': json.dumps({
                    'max_guests': float('inf'),
                    'streaming_hours_per_month': float('inf'),
                    'max_quality': '8K',
                    'max_destinations': float('inf'),
                    'watermark': False,
                    'recording_hours_per_month': float('inf'),
                    'bandwidth_gb': float('inf'),
                    'admin_access': True
                }),
                'max_concurrent_guests': float('inf'),
                'max_quality': '8K'
            }
        ]
        
        for tier in tiers:
            cursor = conn.execute("SELECT id FROM subscription_tiers WHERE name = ?", (tier['name'],))
            if not cursor.fetchone():
                conn.execute("""
                    INSERT INTO subscription_tiers (
                        name, display_name, price_cents, currency, billing_interval,
                        stripe_price_id, features, limits, max_concurrent_guests, max_quality
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tier['name'], tier['display_name'], tier['price_cents'], 'usd',
                    tier['billing_interval'], tier['stripe_price_id'], tier['features'],
                    tier['limits'], tier['max_concurrent_guests'], tier['max_quality']
                ))
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[3],
                    'role': user[4],
                    'tier': user[5],
                    'stripe_customer_id': user[6],
                    'stripe_subscription_id': user[7],
                    'subscription_status': user[8]
                }
        return None
    
    def create_token(self, user):
        """Create JWT token"""
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'tier': user['tier'],
            'exp': datetime.utcnow() + timedelta(days=365),  # 1 year for admin
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except:
            return None
    
    def get_tier_info(self, tier_name):
        """Get tier information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM subscription_tiers WHERE name = ?",
                (tier_name,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'display_name': row[2],
                    'price_cents': row[3],
                    'currency': row[4],
                    'billing_interval': row[5],
                    'stripe_price_id': row[6],
                    'features': json.loads(row[7]) if row[7] else [],
                    'limits': json.loads(row[8]) if row[8] else {},
                    'max_concurrent_guests': row[9],
                    'max_quality': row[10]
                }
        return None
    
    def get_all_tiers(self):
        """Get all subscription tiers"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM subscription_tiers ORDER BY price_cents")
            tiers = []
            for row in cursor.fetchall():
                tier_info = self.get_tier_info(row[1])
                if tier_info:
                    tiers.append(tier_info)
            return tiers
    
    def create_stripe_checkout_session(self, user_id, tier_name, success_url, cancel_url):
        """Create Stripe checkout session"""
        if not stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        tier_info = self.get_tier_info(tier_name)
        if not tier_info or tier_info['price_cents'] == 0:
            return {'success': False, 'error': 'Invalid tier for payment'}
        
        try:
            # Get user info
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                if not user_row:
                    return {'success': False, 'error': 'User not found'}
                
                # Create or get Stripe customer
                customer_id = user_row[6]  # stripe_customer_id
                if not customer_id:
                    customer = stripe.Customer.create(
                        email=user_row[3],  # email
                        metadata={'user_id': str(user_id)}
                    )
                    customer_id = customer.id
                    # Update user with customer ID
                    conn.execute(
                        "UPDATE users SET stripe_customer_id = ? WHERE id = ?",
                        (customer_id, user_id)
                    )
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='subscription',
                customer=customer_id,
                line_items=[{
                    'price': tier_info['stripe_price_id'],
                    'quantity': 1,
                }],
                metadata={
                    'user_id': str(user_id),
                    'tier': tier_name
                },
                success_url=success_url,
                cancel_url=cancel_url,
                allow_promotion_codes=True
            )
            
            return {
                'success': True,
                'session_id': checkout_session.id,
                'checkout_url': checkout_session.url
            }
            
        except Exception as e:
            logger.error(f"Stripe checkout error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_stripe_billing_portal_session(self, user_id, return_url):
        """Create Stripe billing portal session"""
        if not stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            # Get user's Stripe customer ID
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT stripe_customer_id FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if not row or not row[0]:
                    return {'success': False, 'error': 'No Stripe customer found'}
                
                customer_id = row[0]
            
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return {
                'success': True,
                'portal_url': session.url
            }
            
        except Exception as e:
            logger.error(f"Stripe billing portal error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def register_routes(self):
        """Register all routes with Stripe integration"""
        
        @self.app.route('/')
        def home():
            return jsonify({
                'message': 'Atlantiplex Matrix Studio - Stripe Enhanced',
                'version': '2.1.0',
                'stripe_enabled': stripe_available,
                'login': {
                    'admin': {'username': 'manticore', 'password': 'patriot8812'},
                    'demo': {'username': 'demo', 'password': 'demo123'}
                },
                'api_endpoints': {
                    'login': '/api/auth/login',
                    'tiers': '/api/subscriptions/tiers',
                    'checkout': '/api/payments/checkout',
                    'billing_portal': '/api/payments/billing-portal',
                    'guests': '/api/guests',
                    'streaming': '/api/streaming',
                    'health': '/api/health'
                }
            })
        
        @self.app.route('/api/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'features': {
                    'stripe_payments': stripe_available,
                    'admin_bypass': True,
                    'subscriptions': True,
                    'guest_management': True,
                    'streaming': True
                }
            })
        
        @self.app.route('/api/auth/login', methods=['POST'])
        def login():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': 'Username and password required'}), 400
            
            user = self.verify_user(username, password)
            
            if user:
                token = self.create_token(user)
                tier_info = self.get_tier_info(user['tier'])
                return jsonify({
                    'success': True,
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'role': user['role'],
                        'tier': user['tier'],
                        'stripe_customer_id': user['stripe_customer_id'],
                        'stripe_subscription_id': user['stripe_subscription_id'],
                        'subscription_status': user['subscription_status']
                    },
                    'tier_info': tier_info
                })
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        
        @self.app.route('/api/subscriptions/tiers', methods=['GET'])
        def get_tiers():
            tiers = self.get_all_tiers()
            return jsonify({
                'success': True,
                'tiers': tiers,
                'stripe_publishable_key': self.app.config['STRIPE_PUBLISHABLE_KEY']
            })
        
        @self.app.route('/api/payments/checkout', methods=['POST'])
        def create_checkout():
            # Get token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Token required'}), 401
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            data = request.get_json()
            tier_name = data.get('tier')
            
            if not tier_name:
                return jsonify({'error': 'Tier required'}), 400
            
            # Admin users don't need to pay
            if payload['tier'] == 'unlimited':
                return jsonify({
                    'success': True,
                    'message': 'Admin access - no payment required',
                    'tier_updated': True
                })
            
            success_url = f"{self.app.config['DOMAIN']}/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{self.app.config['DOMAIN']}/cancel"
            
            result = self.create_stripe_checkout_session(
                payload['user_id'],
                tier_name,
                success_url,
                cancel_url
            )
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify({'error': result['error']}), 400
        
        @self.app.route('/api/payments/billing-portal', methods=['POST'])
        def billing_portal():
            # Get token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Token required'}), 401
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            data = request.get_json()
            return_url = data.get('return_url', f"{self.app.config['DOMAIN']}/account")
            
            result = self.create_stripe_billing_portal_session(
                payload['user_id'],
                return_url
            )
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify({'error': result['error']}), 400
        
        @self.app.route('/api/payments/webhook', methods=['POST'])
        def stripe_webhook():
            if not stripe_available:
                return jsonify({'error': 'Stripe not available'}), 500
            
            payload = request.data
            sig_header = request.headers.get('Stripe-Signature')
            webhook_secret = self.app.config['STRIPE_WEBHOOK_SECRET']
            
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except Exception as e:
                logger.error(f"Webhook signature verification failed: {str(e)}")
                return jsonify({'error': 'Invalid signature'}), 400
            
            # Handle the event
            event_type = event['type']
            event_data = event['data']['object']
            
            if event_type == 'checkout.session.completed':
                # Update user subscription
                user_id = event_data.get('metadata', {}).get('user_id')
                tier = event_data.get('metadata', {}).get('tier')
                customer_id = event_data.get('customer')
                subscription_id = event_data.get('subscription')
                
                if user_id and tier:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE users 
                            SET stripe_customer_id = ?, stripe_subscription_id = ?, tier = ?, subscription_status = 'active'
                            WHERE id = ?
                        """, (customer_id, subscription_id, tier, int(user_id)))
                    
                    # Record payment
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            INSERT INTO payments (
                                user_id, stripe_payment_intent_id, amount_cents, status, description, tier
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            int(user_id),
                            event_data.get('payment_intent'),
                            event_data.get('amount_total'),
                            'completed',
                            f'Subscription upgrade to {tier}',
                            tier
                        ))
            
            elif event_type == 'invoice.payment_succeeded':
                # Renewal successful
                subscription_id = event_data.get('subscription')
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "UPDATE users SET subscription_status = 'active' WHERE stripe_subscription_id = ?",
                        (subscription_id,)
                    )
            
            elif event_type == 'invoice.payment_failed':
                # Payment failed
                subscription_id = event_data.get('subscription')
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "UPDATE users SET subscription_status = 'past_due' WHERE stripe_subscription_id = ?",
                        (subscription_id,)
                    )
            
            return jsonify({'status': 'success'}), 200
        
        @self.app.route('/api/guests', methods=['GET', 'POST'])
        def manage_guests():
            # Get token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Token required'}), 401
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            user_id = payload['user_id']
            tier_info = self.get_tier_info(payload['tier'])
            
            if request.method == 'GET':
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT * FROM guest_sessions WHERE host_user_id = ?",
                        (user_id,)
                    )
                    guests = []
                    for row in cursor.fetchall():
                        guests.append({
                            'id': row[0],
                            'guest_name': row[2],
                            'guest_email': row[3],
                            'invite_code': row[4],
                            'session_id': row[5],
                            'status': row[6],
                            'created_at': row[7]
                        })
                    
                    return jsonify({
                        'success': True,
                        'guests': guests,
                        'tier_info': tier_info,
                        'current_guests': len(guests),
                        'max_guests': tier_info['max_concurrent_guests']
                    })
            
            elif request.method == 'POST':
                data = request.get_json()
                guest_name = data.get('guest_name')
                guest_email = data.get('guest_email')
                
                if not guest_name:
                    return jsonify({'error': 'Guest name required'}), 400
                
                # Check limits
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM guest_sessions WHERE host_user_id = ? AND status IN ('pending', 'active')",
                        (user_id,)
                    )
                    current_guests = cursor.fetchone()[0]
                    
                    max_guests = tier_info['max_concurrent_guests']
                    
                    if current_guests >= max_guests:
                        return jsonify({
                            'error': 'Guest limit reached',
                            'current': current_guests,
                            'limit': max_guests,
                            'tier': payload['tier'],
                            'upgrade_needed': True,
                            'available_tiers': [t for t in self.get_all_tiers() if t['max_concurrent_guests'] > max_guests]
                        }), 402
                    
                    # Create guest session
                    invite_code = secrets.token_urlsafe(8)
                    session_id = f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"
                    
                    conn.execute(
                        "INSERT INTO guest_sessions (host_user_id, guest_name, guest_email, invite_code, session_id) VALUES (?, ?, ?, ?, ?)",
                        (user_id, guest_name, guest_email, invite_code, session_id)
                    )
                    
                    return jsonify({
                        'success': True,
                        'guest': {
                            'guest_name': guest_name,
                            'guest_email': guest_email,
                            'invite_code': invite_code,
                            'session_id': session_id,
                            'guest_url': f"{self.app.config['DOMAIN']}/guest/{invite_code}"
                        }
                    })
        
        @self.app.route('/api/streaming', methods=['GET', 'POST'])
        def manage_streaming():
            # Get token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Token required'}), 401
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            tier_info = self.get_tier_info(payload['tier'])
            
            if request.method == 'POST':
                data = request.get_json()
                quality = data.get('quality', 'SD')
                platform = data.get('platform', 'youtube')
                title = data.get('title', 'Matrix Studio Stream')
                
                # Check if quality is allowed for tier
                allowed_qualities = ['SD', 'HD', 'Full HD', '4K', '8K']
                quality_hierarchy = {'SD': 0, 'HD': 1, 'Full HD': 2, '4K': 3, '8K': 4}
                
                if quality not in allowed_qualities:
                    return jsonify({'error': 'Invalid quality'}), 400
                
                if quality_hierarchy[quality] > quality_hierarchy[tier_info['max_quality']]:
                    return jsonify({
                        'error': f'Quality {quality} not available in {payload["tier"]} tier',
                        'current_tier': payload['tier'],
                        'max_quality': tier_info['max_quality'],
                        'upgrade_needed': True,
                        'available_tiers': [t for t in self.get_all_tiers() if quality_hierarchy[t['max_quality']] >= quality_hierarchy[quality]]
                    }), 402
                
                # Create stream
                stream_key = f"stream_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(6)}"
                
                return jsonify({
                    'success': True,
                    'stream': {
                        'stream_key': stream_key,
                        'rtmp_url': f"rtmp://live.matrix-studio.com/live/{stream_key}",
                        'quality': quality,
                        'platform': platform,
                        'title': title,
                        'tier': payload['tier']
                    }
                })
            
            else:
                return jsonify({
                    'success': True,
                    'tier_info': tier_info,
                    'streaming_capabilities': {
                        'max_quality': tier_info['max_quality'],
                        'platforms': ['youtube', 'twitch', 'facebook', 'instagram'],
                        'max_duration_hours': tier_info['limits'].get('max_duration_hours', 2),
                        'bandwidth_gb': tier_info['limits'].get('bandwidth_gb', 10)
                    }
                })
        
        @self.app.route('/api/user/subscription', methods=['GET'])
        def user_subscription():
            # Get token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Token required'}), 401
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            tier_info = self.get_tier_info(payload['tier'])
            all_tiers = self.get_all_tiers()
            
            # Get upgrade options
            current_tier_index = next((i for i, t in enumerate(all_tiers) if t['name'] == payload['tier']), -1)
            upgrade_options = all_tiers[current_tier_index + 1:] if current_tier_index >= 0 else []
            
            return jsonify({
                'success': True,
                'current_tier': tier_info,
                'upgrade_options': upgrade_options,
                'can_manage_billing': bool(payload.get('stripe_customer_id'))
            })
    
    def run(self):
        """Run the application"""
        logger.info("Starting Stripe Enhanced Matrix Studio")
        logger.info("Admin Login: manticore / patriot8812")
        logger.info("Demo Login: demo / demo123")
        logger.info("Stripe Enabled: " + str(stripe_available))
        logger.info("Access: http://localhost:8081")
        
        self.app.run(host='0.0.0.0', port=8081, debug=False)

# Run the application
if __name__ == '__main__':
    app = StripeEnhancedMatrixStudio()
    app.run()