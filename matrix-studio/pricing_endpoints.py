"""
Enhanced Pricing & Tier API Endpoints for Atlantiplex Lightning Studio
Comprehensive pricing information, Stripe integration, and checkout management
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
pricing_bp = Blueprint('pricing', __name__, url_prefix='/api/v1')

class PricingManager:
    """Manages pricing plans and checkout sessions"""
    
    def __init__(self):
        self.plans = {
            'free': {
                'id': 'free',
                'name': 'Free',
                'price': 0,
                'currency': 'usd',
                'interval': 'month',
                'description': 'Get started with basic streaming',
                'features': [
                    '1 concurrent guest',
                    'SD streaming quality',
                    'YouTube platform only',
                    'Basic scene templates',
                    '10GB bandwidth/month',
                    'Community support'
                ],
                'limitations': [
                    'No HD streaming',
                    'No API access',
                    'No cloud storage',
                    'Basic analytics only'
                ],
                'stripe_price_id': None,
                'popular': False
            },
            'starter': {
                'id': 'starter',
                'name': 'Starter',
                'price': 9.99,
                'currency': 'usd',
                'interval': 'month',
                'description': 'Perfect for small creators',
                'features': [
                    '3 concurrent guests',
                    'HD streaming quality (720p)',
                    'YouTube + Twitch platforms',
                    'Basic + Premium scenes',
                    '100GB bandwidth/month',
                    '10GB cloud storage',
                    'Email support',
                    'Basic analytics',
                    'Unlimited stream duration'
                ],
                'limitations': [
                    'No custom scenes',
                    'No API access',
                    'Standard support only'
                ],
                'stripe_price_id': 'price_starter_monthly',
                'paypal_plan_id': 'P-STARTER-MONTHLY',
                'popular': False
            },
            'professional': {
                'id': 'professional',
                'name': 'Professional',
                'price': 29.99,
                'currency': 'usd',
                'interval': 'month',
                'description': 'For serious streamers and professionals',
                'features': [
                    '10 concurrent guests (was 8)',
                    'Full HD streaming (1080p)',
                    '4 platforms: YouTube, Twitch, Facebook, Instagram',
                    'All scene templates including custom',
                    '500GB bandwidth/month',
                    '100GB cloud storage',
                    'Priority email support',
                    'Advanced analytics dashboard',
                    'API access',
                    'Stream recording',
                    'Custom branding',
                    'OBS integration'
                ],
                'limitations': [],
                'stripe_price_id': 'price_professional_monthly',
                'paypal_plan_id': 'P-PROFESSIONAL-MONTHLY',
                'popular': True
            },
            'enterprise': {
                'id': 'enterprise',
                'name': 'Enterprise',
                'price': 99.99,
                'currency': 'usd',
                'interval': 'month',
                'description': 'For businesses and large organizations',
                'features': [
                    '50 concurrent guests',
                    '4K Ultra HD streaming',
                    'All 6 platforms including LinkedIn & Twitter',
                    'Unlimited custom scenes',
                    '2TB bandwidth/month',
                    '1TB cloud storage',
                    '24/7 phone support',
                    'Dedicated account manager',
                    'White-label options',
                    'Custom integrations',
                    'SLA guarantee',
                    'Team management',
                    'Advanced security features'
                ],
                'limitations': [],
                'stripe_price_id': 'price_enterprise_monthly',
                'paypal_plan_id': 'P-ENTERPRISE-MONTHLY',
                'popular': False
            }
        }
        
        # Annual plans (20% discount)
        self.annual_plans = {
            'starter': {
                **self.plans['starter'],
                'price': 95.90,  # ~20% discount
                'interval': 'year',
                'description': 'Starter plan - Annual billing (Save 20%)',
                'stripe_price_id': 'price_starter_yearly',
                'paypal_plan_id': 'P-STARTER-YEARLY'
            },
            'professional': {
                **self.plans['professional'],
                'price': 287.90,  # ~20% discount
                'interval': 'year',
                'description': 'Professional plan - Annual billing (Save 20%)',
                'stripe_price_id': 'price_professional_yearly',
                'paypal_plan_id': 'P-PROFESSIONAL-YEARLY'
            },
            'enterprise': {
                **self.plans['enterprise'],
                'price': 959.90,  # ~20% discount
                'interval': 'year',
                'description': 'Enterprise plan - Annual billing (Save 20%)',
                'stripe_price_id': 'price_enterprise_yearly',
                'paypal_plan_id': 'P-ENTERPRISE-YEARLY'
            }
        }
        
        self.stripe_available = False
        try:
            import stripe
            self.stripe = stripe
            self.stripe_available = True
        except ImportError:
            logger.warning("Stripe library not installed")
    
    def get_all_plans(self, billing_interval: str = 'month') -> List[Dict]:
        """Get all pricing plans"""
        if billing_interval == 'year':
            return list(self.annual_plans.values())
        return list(self.plans.values())
    
    def get_plan(self, plan_id: str, billing_interval: str = 'month') -> Dict:
        """Get specific plan details"""
        if billing_interval == 'year':
            return self.annual_plans.get(plan_id)
        return self.plans.get(plan_id)
    
    def compare_plans(self) -> Dict:
        """Generate detailed plan comparison"""
        comparison = {
            'plans': self.plans,
            'features': {
                'guests': {
                    'free': '1',
                    'starter': '3',
                    'professional': '10',
                    'enterprise': '50'
                },
                'quality': {
                    'free': 'SD (480p)',
                    'starter': 'HD (720p)',
                    'professional': 'Full HD (1080p)',
                    'enterprise': '4K Ultra HD'
                },
                'platforms': {
                    'free': 'YouTube',
                    'starter': 'YouTube, Twitch',
                    'professional': '4 platforms',
                    'enterprise': 'All 6 platforms'
                },
                'bandwidth': {
                    'free': '10GB/month',
                    'starter': '100GB/month',
                    'professional': '500GB/month',
                    'enterprise': '2TB/month'
                },
                'storage': {
                    'free': 'None',
                    'starter': '10GB',
                    'professional': '100GB',
                    'enterprise': '1TB'
                },
                'support': {
                    'free': 'Community',
                    'starter': 'Email',
                    'professional': 'Priority Email',
                    'enterprise': '24/7 Phone'
                },
                'api_access': {
                    'free': False,
                    'starter': False,
                    'professional': True,
                    'enterprise': True
                },
                'custom_branding': {
                    'free': False,
                    'starter': False,
                    'professional': True,
                    'enterprise': True
                },
                'white_label': {
                    'free': False,
                    'starter': False,
                    'professional': False,
                    'enterprise': True
                }
            }
        }
        return comparison
    
    def create_stripe_checkout_session(self, plan_id: str, user_email: str, 
                                     success_url: str, cancel_url: str,
                                     billing_interval: str = 'month') -> Dict:
        """Create Stripe checkout session"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        plan = self.get_plan(plan_id, billing_interval)
        if not plan:
            return {'success': False, 'error': 'Invalid plan'}
        
        if not plan.get('stripe_price_id'):
            return {'success': False, 'error': 'Stripe not configured for this plan'}
        
        try:
            session = self.stripe.checkout.Session.create(
                customer_email=user_email,
                payment_method_types=['card'],
                line_items=[{
                    'price': plan['stripe_price_id'],
                    'quantity': 1
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'plan_id': plan_id,
                    'billing_interval': billing_interval
                }
            )
            
            return {
                'success': True,
                'checkout_url': session.url,
                'session_id': session.id,
                'stripe_price_id': plan['stripe_price_id']
            }
        except Exception as e:
            logger.error(f"Stripe checkout error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_paypal_checkout(self, plan_id: str, billing_interval: str = 'month') -> Dict:
        """Create PayPal checkout order"""
        plan = self.get_plan(plan_id, billing_interval)
        if not plan:
            return {'success': False, 'error': 'Invalid plan'}
        
        if not plan.get('paypal_plan_id'):
            return {'success': False, 'error': 'PayPal not configured for this plan'}
        
        # Return PayPal subscription plan ID for client-side integration
        return {
            'success': True,
            'paypal_plan_id': plan['paypal_plan_id'],
            'plan_details': {
                'name': plan['name'],
                'price': plan['price'],
                'currency': plan['currency'],
                'interval': plan['interval']
            }
        }
    
    def calculate_price(self, plan_id: str, billing_interval: str = 'month', 
                       coupon_code: str = None) -> Dict:
        """Calculate price with discounts"""
        plan = self.get_plan(plan_id, billing_interval)
        if not plan:
            return {'success': False, 'error': 'Invalid plan'}
        
        base_price = plan['price']
        discount = 0
        
        # Apply coupon if valid
        if coupon_code:
            valid_coupons = {
                'WELCOME20': 0.20,  # 20% off
                'ANNUAL30': 0.30,   # 30% off annual
                'ENTERPRISE50': 0.50  # 50% off enterprise
            }
            
            if coupon_code.upper() in valid_coupons:
                discount_rate = valid_coupons[coupon_code.upper()]
                
                # Check if coupon applies to this plan
                if coupon_code.upper() == 'ANNUAL30' and billing_interval != 'year':
                    discount = 0
                else:
                    discount = base_price * discount_rate
        
        final_price = base_price - discount
        
        return {
            'success': True,
            'plan': plan_id,
            'billing_interval': billing_interval,
            'base_price': base_price,
            'discount': round(discount, 2),
            'final_price': round(final_price, 2),
            'currency': plan['currency'],
            'savings_percentage': round((discount / base_price) * 100, 1) if base_price > 0 else 0
        }


# Initialize pricing manager
pricing_manager = PricingManager()


@pricing_bp.route('/pricing/plans', methods=['GET'])
def get_pricing_plans():
    """Get all available pricing plans"""
    try:
        billing_interval = request.args.get('interval', 'month')
        plans = pricing_manager.get_all_plans(billing_interval)
        
        return jsonify({
            'success': True,
            'billing_interval': billing_interval,
            'plans': plans,
            'currency': 'USD'
        }), 200
        
    except Exception as e:
        logger.error(f"Get pricing plans error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get pricing plans'}), 500


@pricing_bp.route('/pricing/plans/<plan_id>', methods=['GET'])
def get_plan_details(plan_id):
    """Get specific plan details"""
    try:
        billing_interval = request.args.get('interval', 'month')
        plan = pricing_manager.get_plan(plan_id, billing_interval)
        
        if not plan:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404
        
        return jsonify({
            'success': True,
            'plan': plan
        }), 200
        
    except Exception as e:
        logger.error(f"Get plan details error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get plan details'}), 500


@pricing_bp.route('/pricing/compare', methods=['GET'])
def compare_plans():
    """Get detailed plan comparison"""
    try:
        comparison = pricing_manager.compare_plans()
        
        return jsonify({
            'success': True,
            'comparison': comparison
        }), 200
        
    except Exception as e:
        logger.error(f"Compare plans error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to compare plans'}), 500


@pricing_bp.route('/pricing/calculate', methods=['POST'])
def calculate_price():
    """Calculate price with discounts"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        billing_interval = data.get('interval', 'month')
        coupon_code = data.get('coupon_code')
        
        if not plan_id:
            return jsonify({'success': False, 'error': 'Plan ID required'}), 400
        
        result = pricing_manager.calculate_price(plan_id, billing_interval, coupon_code)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Calculate price error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to calculate price'}), 500


@pricing_bp.route('/pricing/checkout/stripe', methods=['POST'])
def create_stripe_checkout():
    """Create Stripe checkout session"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        user_email = data.get('email')
        success_url = data.get('success_url')
        cancel_url = data.get('cancel_url')
        billing_interval = data.get('interval', 'month')
        
        # Validate required fields
        if not all([plan_id, user_email, success_url, cancel_url]):
            return jsonify({
                'success': False, 
                'error': 'Missing required fields: plan_id, email, success_url, cancel_url'
            }), 400
        
        result = pricing_manager.create_stripe_checkout_session(
            plan_id, user_email, success_url, cancel_url, billing_interval
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create checkout session'}), 500


@pricing_bp.route('/pricing/checkout/paypal', methods=['POST'])
def create_paypal_checkout():
    """Get PayPal checkout configuration"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        billing_interval = data.get('interval', 'month')
        
        if not plan_id:
            return jsonify({'success': False, 'error': 'Plan ID required'}), 400
        
        result = pricing_manager.create_paypal_checkout(plan_id, billing_interval)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"PayPal checkout error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get PayPal checkout'}), 500


@pricing_bp.route('/pricing/validate-coupon', methods=['POST'])
def validate_coupon():
    """Validate a coupon code"""
    try:
        data = request.get_json()
        coupon_code = data.get('coupon_code')
        
        if not coupon_code:
            return jsonify({'success': False, 'error': 'Coupon code required'}), 400
        
        valid_coupons = {
            'WELCOME20': {
                'discount': 0.20,
                'description': '20% off your first month',
                'valid_plans': ['starter', 'professional', 'enterprise']
            },
            'ANNUAL30': {
                'discount': 0.30,
                'description': '30% off annual plans',
                'valid_plans': ['starter', 'professional', 'enterprise'],
                'valid_intervals': ['year']
            },
            'ENTERPRISE50': {
                'discount': 0.50,
                'description': '50% off Enterprise plan',
                'valid_plans': ['enterprise']
            },
            'STUDENT40': {
                'discount': 0.40,
                'description': '40% off for students',
                'valid_plans': ['starter', 'professional']
            }
        }
        
        coupon = valid_coupons.get(coupon_code.upper())
        
        if coupon:
            return jsonify({
                'success': True,
                'valid': True,
                'coupon': {
                    'code': coupon_code.upper(),
                    'discount_percentage': int(coupon['discount'] * 100),
                    'description': coupon['description'],
                    'valid_plans': coupon['valid_plans'],
                    'valid_intervals': coupon.get('valid_intervals', ['month', 'year'])
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'valid': False,
                'error': 'Invalid coupon code'
            }), 200
            
    except Exception as e:
        logger.error(f"Validate coupon error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to validate coupon'}), 500


@pricing_bp.route('/pricing/features', methods=['GET'])
def get_all_features():
    """Get list of all available features by tier"""
    try:
        features = {
            'guest_management': {
                'name': 'Guest Management',
                'description': 'Number of concurrent guests',
                'tiers': {
                    'free': '1 guest',
                    'starter': '3 guests',
                    'professional': '10 guests',
                    'enterprise': '50 guests'
                }
            },
            'streaming_quality': {
                'name': 'Streaming Quality',
                'description': 'Maximum streaming resolution',
                'tiers': {
                    'free': 'SD (480p)',
                    'starter': 'HD (720p)',
                    'professional': 'Full HD (1080p)',
                    'enterprise': '4K Ultra HD'
                }
            },
            'platforms': {
                'name': 'Platforms',
                'description': 'Supported streaming platforms',
                'tiers': {
                    'free': ['YouTube'],
                    'starter': ['YouTube', 'Twitch'],
                    'professional': ['YouTube', 'Twitch', 'Facebook', 'Instagram'],
                    'enterprise': ['YouTube', 'Twitch', 'Facebook', 'Instagram', 'LinkedIn', 'Twitter']
                }
            },
            'bandwidth': {
                'name': 'Bandwidth',
                'description': 'Monthly bandwidth allowance',
                'tiers': {
                    'free': '10GB',
                    'starter': '100GB',
                    'professional': '500GB',
                    'enterprise': '2TB'
                }
            },
            'storage': {
                'name': 'Cloud Storage',
                'description': 'Cloud storage for recordings',
                'tiers': {
                    'free': None,
                    'starter': '10GB',
                    'professional': '100GB',
                    'enterprise': '1TB'
                }
            },
            'analytics': {
                'name': 'Analytics',
                'description': 'Stream analytics and insights',
                'tiers': {
                    'free': 'Basic',
                    'starter': 'Basic',
                    'professional': 'Advanced',
                    'enterprise': 'Enterprise'
                }
            },
            'api_access': {
                'name': 'API Access',
                'description': 'Programmatic access to platform',
                'tiers': {
                    'free': False,
                    'starter': False,
                    'professional': True,
                    'enterprise': True
                }
            },
            'custom_branding': {
                'name': 'Custom Branding',
                'description': 'Custom logos and colors',
                'tiers': {
                    'free': False,
                    'starter': False,
                    'professional': True,
                    'enterprise': True
                }
            },
            'white_label': {
                'name': 'White Label',
                'description': 'Remove Atlantiplex branding',
                'tiers': {
                    'free': False,
                    'starter': False,
                    'professional': False,
                    'enterprise': True
                }
            },
            'support': {
                'name': 'Support',
                'description': 'Customer support level',
                'tiers': {
                    'free': 'Community',
                    'starter': 'Email',
                    'professional': 'Priority Email',
                    'enterprise': '24/7 Phone'
                }
            }
        }
        
        return jsonify({
            'success': True,
            'features': features
        }), 200
        
    except Exception as e:
        logger.error(f"Get features error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get features'}), 500


@pricing_bp.route('/pricing/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events for pricing/subscriptions"""
    try:
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
        
        if not webhook_secret:
            return jsonify({'error': 'Webhook secret not configured'}), 500
        
        if not pricing_manager.stripe_available:
            return jsonify({'error': 'Stripe not available'}), 500
        
        try:
            event = pricing_manager.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except Exception as e:
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            logger.info(f"Checkout completed for customer: {session['customer']}")
            # Update user subscription in database
            
        elif event['type'] == 'invoice.paid':
            invoice = event['data']['object']
            logger.info(f"Invoice paid: {invoice['id']}")
            # Update payment status
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            logger.info(f"Subscription cancelled: {subscription['id']}")
            # Downgrade user to free tier
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500


def register_pricing_routes(app):
    """Register pricing blueprint with Flask app"""
    app.register_blueprint(pricing_bp)
    logger.info("✅ Pricing API routes registered")