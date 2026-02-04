"""
Payment API Endpoints for Atlantiplex Matrix Studio
Flask routes for payment processing, subscription management, and billing
"""

from flask import Flask, request, jsonify, current_app, g
import logging
from datetime import datetime
from typing import Dict, Any

# Import our custom modules
from admin_auth import AdminBypassAuth, auth_required, admin_auth_required, permission_required
from stripe_payments import StripePaymentManager
from subscription_manager import TierManager, SubscriptionTier
from database_payments import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_payment_routes(app: Flask):
    """Register all payment and subscription routes"""
    
    # Initialize managers
    auth_manager = AdminBypassAuth()
    payment_manager = StripePaymentManager()
    tier_manager = TierManager()
    db_manager = DatabaseManager()
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login with admin bypass support and Manticore Control Interface"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')  # Check for Manticore email
            
            # Special Manticore Control Interface check
            if email and email.lower() == "digital.demiurge666@gmail.com":
                result = auth_manager.verify_admin_credentials(username, password, email)
                if result['success']:
                    logger.info(f"MANTICORE CONTROL INTERFACE LOGIN: {email}")
                    return jsonify(result), 200
            
            if not username or not password:
                return jsonify({'error': 'Username and password required'}), 400
            
            # Verify credentials (with admin bypass)
            result = auth_manager.verify_admin_credentials(username, password)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify({'error': result['error']}), 401
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return jsonify({'error': 'Login failed'}), 500
    
    @app.route('/api/auth/verify', methods=['POST'])
    def verify_token():
        """Verify JWT token"""
        try:
            data = request.get_json()
            token = data.get('token')
            
            if not token:
                return jsonify({'error': 'Token required'}), 400
            
            result = auth_manager.verify_token(token)
            
            if result['valid']:
                return jsonify(result), 200
            else:
                return jsonify({'error': result['error']}), 401
                
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return jsonify({'error': 'Token verification failed'}), 500
    
    @app.route('/api/subscriptions/tiers', methods=['GET'])
    def get_subscription_tiers():
        """Get available subscription tiers"""
        try:
            comparison = tier_manager.get_tier_comparison()
            return jsonify({
                'success': True,
                'tiers': comparison
            }), 200
            
        except Exception as e:
            logger.error(f"Get tiers error: {str(e)}")
            return jsonify({'error': 'Failed to get tiers'}), 500
    
    @app.route('/api/subscriptions/current', methods=['GET'])
    @auth_required
    def get_current_subscription():
        """Get user's current subscription"""
        try:
            user_id = g.current_user['user_id']
            user_role = g.current_user.get('role', '')
            
            # MANTICORE CONTROL INTERFACE - Bypass all payments
            if user_role == 'manticore_controller':
                return jsonify({
                    'success': True,
                    'subscription': {
                        'tier': 'manticore_unlimited',
                        'name': 'Manticore Control Interface',
                        'price': 0,
                        'billing_cycle': 'lifetime',
                        'features': {
                            'guest_management': {
                                'max_concurrent': 'unlimited',
                                'total_sessions_per_day': 'unlimited',
                                'session_duration_hours': 'unlimited'
                            },
                            'streaming': {
                                'max_quality': '8K',
                                'max_duration_hours': 'unlimited',
                                'platforms': 'all',
                                'priority_servers': True
                            },
                            'features': {
                                'basic_scenes': True,
                                'premium_scenes': True,
                                'custom_scenes': True,
                                'analytics': True,
                                'cloud_storage': True,
                                'api_access': True,
                                'white_label': True,
                                'experimental_features': True
                            },
                            'support': {
                                'email_support': True,
                                'priority_support': True,
                                'phone_support': True,
                                'dedicated_account_manager': True,
                                '24_7_support': True
                            }
                        },
                        'limits': {
                            'bandwidth_gb_per_month': 'unlimited',
                            'storage_gb': 'unlimited',
                            'api_calls_per_day': 'unlimited'
                        },
                        'control_interface': True,
                        'bypass_payments': True,
                        'message': 'MANTICORE CONTROL INTERFACE - All payment requirements removed'
                    }
                }), 200
            
            # Get from database
            if user_id.isdigit():
                db_user_id = int(user_id)
                subscription = db_manager.get_user_subscription(db_user_id)
                if subscription:
                    tier_config = tier_manager.get_tier_info(SubscriptionTier(subscription['tier']))
                    return jsonify({
                        'success': True,
                        'subscription': {
                            **subscription,
                            'features': tier_config.get('features', {}),
                            'limits': tier_config.get('limits', {})
                        }
                    }), 200
            
            # Fallback to in-memory data
            tier = tier_manager.get_user_tier(user_id)
            tier_info = tier_manager.get_tier_info(tier)
            
            return jsonify({
                'success': True,
                'subscription': {
                    'tier': tier.value,
                    'features': tier_info.get('features', {}),
                    'limits': tier_info.get('limits', {})
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Get current subscription error: {str(e)}")
            return jsonify({'error': 'Failed to get subscription'}), 500
    
    @app.route('/api/subscriptions/upgrade-options', methods=['GET'])
    @auth_required
    def get_upgrade_options():
        """Get available upgrade options"""
        try:
            user_id = g.current_user['user_id']
            options = tier_manager.get_upgrade_options(user_id)
            return jsonify({
                'success': True,
                'options': options
            }), 200
            
        except Exception as e:
            logger.error(f"Get upgrade options error: {str(e)}")
            return jsonify({'error': 'Failed to get upgrade options'}), 500
    
    @app.route('/api/payments/checkout', methods=['POST'])
    @auth_required
    def create_checkout_session():
        """Create Stripe checkout session"""
        try:
            data = request.get_json()
            tier = data.get('tier')
            success_url = data.get('success_url')
            cancel_url = data.get('cancel_url')
            
            if not tier or not success_url or not cancel_url:
                return jsonify({'error': 'Missing required fields'}), 400
            
            user_id = g.current_user['user_id']
            
            result = payment_manager.create_checkout_session(
                user_id=user_id,
                tier=tier,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            logger.error(f"Checkout session error: {str(e)}")
            return jsonify({'error': 'Failed to create checkout session'}), 500
    
    @app.route('/api/payments/billing-portal', methods=['POST'])
    @auth_required
    def create_billing_portal_session():
        """Create Stripe billing portal session"""
        try:
            data = request.get_json()
            return_url = data.get('return_url')
            
            if not return_url:
                return jsonify({'error': 'Return URL required'}), 400
            
            user_id = g.current_user['user_id']
            
            # Get customer ID from database
            if user_id.isdigit():
                db_user_id = int(user_id)
                subscription = db_manager.get_user_subscription(db_user_id)
                customer_id = subscription.get('stripe_customer_id') if subscription else None
                
                if customer_id:
                    result = payment_manager.create_billing_portal_session(customer_id, return_url)
                    
                    if result['success']:
                        return jsonify(result), 200
                    else:
                        return jsonify({'error': result['error']}), 400
            
            return jsonify({'error': 'No active subscription found'}), 404
                
        except Exception as e:
            logger.error(f"Billing portal error: {str(e)}")
            return jsonify({'error': 'Failed to create billing portal session'}), 500
    
    @app.route('/api/payments/webhook', methods=['POST'])
    def stripe_webhook():
        """Handle Stripe webhook events"""
        try:
            payload = request.data.decode('utf-8')
            sig_header = request.headers.get('Stripe-Signature')
            webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
            
            if not webhook_secret:
                return jsonify({'error': 'Webhook secret not configured'}), 500
            
            # Process webhook
            result = payment_manager.handle_webhook(payload, sig_header, webhook_secret)
            
            if result['success']:
                # Update database based on event type
                event_data = result.get('event_data', {})
                event_type = event_data.get('type', '').replace('.', '_')
                
                if 'checkout_completed' in event_type:
                    # Update user subscription
                    user_id = event_data.get('user_id')
                    tier = event_data.get('tier')
                    subscription_id = event_data.get('subscription_id')
                    
                    if user_id and tier:
                        db_user_id = int(user_id) if user_id.isdigit() else None
                        if db_user_id:
                            db_manager.update_subscription(db_user_id, tier, subscription_id)
                
                # Record webhook event
                stripe_event_id = event_data.get('id') or 'manual_' + str(datetime.utcnow())
                db_manager.record_webhook_event(stripe_event_id, event_type, event_data)
                db_manager.mark_webhook_processed(stripe_event_id)
                
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return jsonify({'error': 'Webhook processing failed'}), 500
    
    @app.route('/api/payments/history', methods=['GET'])
    @auth_required
    def get_payment_history():
        """Get user's payment history"""
        try:
            user_id = g.current_user['user_id']
            
            # For demo purposes, return sample data
            # In production, query the payments table
            return jsonify({
                'success': True,
                'payments': [
                    {
                        'id': 1,
                        'amount': 9.99,
                        'currency': 'USD',
                        'status': 'completed',
                        'description': 'Starter subscription',
                        'date': '2024-01-01T00:00:00Z'
                    }
                ]
            }), 200
            
        except Exception as e:
            logger.error(f"Payment history error: {str(e)}")
            return jsonify({'error': 'Failed to get payment history'}), 500
    
    @app.route('/api/usage/track', methods=['POST'])
    @auth_required
    def track_usage():
        """Track user usage"""
        try:
            data = request.get_json()
            usage_type = data.get('usage_type')
            amount = data.get('amount')
            description = data.get('description')
            
            if not usage_type or amount is None:
                return jsonify({'error': 'Usage type and amount required'}), 400
            
            user_id = g.current_user['user_id']
            db_user_id = int(user_id) if user_id.isdigit() else None
            
            if db_user_id:
                db_manager.track_usage(db_user_id, usage_type, amount, description)
                
                # Check limit
                daily_usage = db_manager.get_daily_usage(db_user_id, usage_type)
                limit_check = tier_manager.check_limit(user_id, usage_type, daily_usage)
                
                return jsonify({
                    'success': True,
                    'daily_usage': daily_usage,
                    'limit_check': limit_check
                }), 200
            
            return jsonify({'success': True, 'message': 'Usage tracked'}), 200
            
        except Exception as e:
            logger.error(f"Usage tracking error: {str(e)}")
            return jsonify({'error': 'Failed to track usage'}), 500
    
    @app.route('/api/usage/stats', methods=['GET'])
    @auth_required
    def get_usage_stats():
        """Get user's usage statistics"""
        try:
            user_id = g.current_user['user_id']
            db_user_id = int(user_id) if user_id.isdigit() else None
            
            if db_user_id:
                # Get usage from database
                with db_manager.get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT usage_type, COALESCE(SUM(amount), 0) as total,
                               DATE(created_at) as date
                        FROM usage_tracking 
                        WHERE user_id = ? 
                        AND DATE(created_at) >= DATE('now', '-30 days')
                        GROUP BY usage_type, DATE(created_at)
                        ORDER BY date DESC
                    """, (db_user_id,))
                    
                    usage_data = {}
                    for row in cursor.fetchall():
                        usage_type = row['usage_type']
                        if usage_type not in usage_data:
                            usage_data[usage_type] = {'total': 0, 'daily': []}
                        usage_data[usage_type]['total'] += row['total']
                        usage_data[usage_type]['daily'].append({
                            'date': row['date'],
                            'amount': row['total']
                        })
                
                return jsonify({
                    'success': True,
                    'usage': usage_data
                }), 200
            
            return jsonify({'success': True, 'usage': {}}), 200
            
        except Exception as e:
            logger.error(f"Usage stats error: {str(e)}")
            return jsonify({'error': 'Failed to get usage stats'}), 500
    
    @app.route('/api/admin/subscriptions', methods=['GET'])
    @admin_auth_required
    def admin_get_subscriptions():
        """Admin: Get all subscriptions"""
        try:
            metrics = db_manager.get_subscription_metrics()
            return jsonify({
                'success': True,
                'metrics': metrics
            }), 200
            
        except Exception as e:
            logger.error(f"Admin subscriptions error: {str(e)}")
            return jsonify({'error': 'Failed to get subscriptions'}), 500
    
    @app.route('/api/admin/users', methods=['GET'])
    @admin_auth_required
    def admin_get_users():
        """Admin: Get all users"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT u.id, u.username, u.email, u.role, u.created_at,
                           s.tier, s.status as subscription_status
                    FROM users u
                    LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'
                    ORDER BY u.created_at DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'id': row['id'],
                        'username': row['username'],
                        'email': row['email'],
                        'role': row['role'],
                        'tier': row['tier'],
                        'subscription_status': row['subscription_status'],
                        'created_at': row['created_at']
                    })
                
                return jsonify({
                    'success': True,
                    'users': users
                }), 200
            
        except Exception as e:
            logger.error(f"Admin users error: {str(e)}")
            return jsonify({'error': 'Failed to get users'}), 500
    
    @app.route('/api/admin/user/<int:user_id>/subscription', methods=['PUT'])
    @admin_auth_required
    def admin_update_user_subscription(user_id):
        """Admin: Update user subscription"""
        try:
            data = request.get_json()
            tier = data.get('tier')
            
            if not tier:
                return jsonify({'error': 'Tier required'}), 400
            
            success = db_manager.update_subscription(user_id, tier)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'User {user_id} subscription updated to {tier}'
                }), 200
            else:
                return jsonify({'error': 'Failed to update subscription'}), 500
                
        except Exception as e:
            logger.error(f"Admin update subscription error: {str(e)}")
            return jsonify({'error': 'Failed to update subscription'}), 500
    
    # Feature access checking middleware
    @app.before_request
    def check_feature_access():
        """Check if user has access to requested features"""
        if request.path.startswith('/api/'):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if token:
                verification = auth_manager.verify_token(token)
                if verification['valid']:
                    user_id = verification['user']['user_id']
                    
                    # Map API paths to feature permissions
                    feature_map = {
                        '/api/guests': 'guest_management',
                        '/api/streaming': 'streaming',
                        '/api/scenes': 'features.basic_scenes',
                        '/api/analytics': 'features.analytics',
                        '/api/admin': 'system.full_admin_access'
                    }
                    
                    for path, feature in feature_map.items():
                        if request.path.startswith(path):
                            if not tier_manager.can_access_feature(user_id, feature):
                                # Log denied access
                                db_user_id = int(user_id) if user_id.isdigit() else None
                                if db_user_id:
                                    db_manager.log_feature_access(
                                        db_user_id, request.path, False, 
                                        tier_manager.get_user_tier(user_id).value,
                                        'Feature not available in current tier'
                                    )
                                
                                return jsonify({'error': f'Feature {feature} not available in your subscription tier'}), 403
                            break
    
    logger.info("Payment API routes registered successfully")