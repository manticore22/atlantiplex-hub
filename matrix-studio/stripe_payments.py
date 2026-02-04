"""
Stripe Payment Integration Module for Atlantiplex Matrix Studio
Handles subscriptions, one-time payments, and billing management
"""

import json
import logging
from datetime import datetime, timedelta
from flask import current_app
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StripePaymentManager:
    """Manages all Stripe payment operations"""
    
    def __init__(self, api_key: str = None):
        """Initialize Stripe with API key"""
        self.api_key = api_key or current_app.config.get('STRIPE_SECRET_KEY')
        self.stripe_available = False
        
        try:
            import stripe
            self.stripe = stripe
            if self.api_key:
                stripe.api_key = self.api_key
            self.stripe_available = True
        except ImportError:
            logger.warning("Stripe library not installed. Install with: pip install stripe")
            self.stripe = None
        
        # Define subscription tiers
        self.subscription_tiers = {
            'starter': {
                'name': 'Starter',
                'price_id': 'price_starter_monthly',
                'amount': 999,  # $9.99 in cents
                'currency': 'usd',
                'interval': 'month',
                'features': [
                    '3 concurrent guests',
                    'Basic scene templates',
                    'Standard streaming quality',
                    'Email support'
                ]
            },
            'professional': {
                'name': 'Professional',
                'price_id': 'price_professional_monthly',
                'amount': 2999,  # $29.99 in cents
                'currency': 'usd',
                'interval': 'month',
                'features': [
                    '10 concurrent guests',
                    'Premium scene templates',
                    'HD streaming quality',
                    'Priority email support',
                    'Basic analytics',
                    'Cloud storage (100GB)'
                ]
            },
            'enterprise': {
                'name': 'Enterprise',
                'price_id': 'price_enterprise_monthly',
                'amount': 9999,  # $99.99 in cents
                'currency': 'usd',
                'interval': 'month',
                'features': [
                    'Unlimited concurrent guests',
                    'Custom scene templates',
                    '4K streaming quality',
                    '24/7 phone support',
                    'Advanced analytics',
                    'Cloud storage (1TB)',
                    'API access',
                    'White-label options'
                ]
            }
        }
    
    def create_checkout_session(self, user_id: str, tier: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        """Create Stripe checkout session for subscription"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            if tier not in self.subscription_tiers:
                raise ValueError(f"Invalid subscription tier: {tier}")
            
            tier_info = self.subscription_tiers[tier]
            
            checkout_session = self.stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='subscription',
                customer_email=self.get_user_email(user_id),
                line_items=[{
                    'price': tier_info['price_id'],
                    'quantity': 1,
                }],
                metadata={
                    'user_id': user_id,
                    'tier': tier,
                    'product': 'matrix_studio'
                },
                success_url=success_url,
                cancel_url=cancel_url,
                allow_promotion_codes=True,
                billing_address_collection='required',
                customer_creation='always'
            )
            
            logger.info(f"Created checkout session {checkout_session.id} for user {user_id}")
            return {
                'success': True,
                'session_id': checkout_session.id,
                'checkout_url': checkout_session.url
            }
            
        except Exception as e:
            logger.error(f"Failed to create checkout session: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_customer(self, user_id: str, email: str, name: str = None) -> Dict[str, Any]:
        """Create Stripe customer"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata={'user_id': user_id, 'product': 'matrix_studio'}
            )
            
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return {
                'success': True,
                'customer_id': customer.id
            }
            
        except Exception as e:
            logger.error(f"Failed to create customer: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_subscription_status(self, subscription_id: str) -> Dict[str, Any]:
        """Get current subscription status"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            
            return {
                'success': True,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'tier': subscription.metadata.get('tier'),
                'customer_id': subscription.customer
            }
            
        except Exception as e:
            logger.error(f"Failed to get subscription status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> Dict[str, Any]:
        """Cancel subscription (immediately or at period end)"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            if immediate:
                subscription = self.stripe.Subscription.delete(subscription_id)
            else:
                subscription = self.stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            logger.info(f"Cancelled subscription {subscription_id}")
            return {
                'success': True,
                'status': subscription.status,
                'cancelled_at': subscription.canceled_at
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_subscription(self, subscription_id: str, new_tier: str) -> Dict[str, Any]:
        """Update subscription to new tier"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            if new_tier not in self.subscription_tiers:
                raise ValueError(f"Invalid subscription tier: {new_tier}")
            
            new_price_id = self.subscription_tiers[new_tier]['price_id']
            
            subscription = self.stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': self.stripe.Subscription.retrieve(subscription_id)['items']['data'][0].id,
                    'price': new_price_id,
                }],
                metadata={'tier': new_tier}
            )
            
            logger.info(f"Updated subscription {subscription_id} to {new_tier}")
            return {
                'success': True,
                'new_tier': new_tier,
                'status': subscription.status
            }
            
        except Exception as e:
            logger.error(f"Failed to update subscription: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_billing_portal_session(self, customer_id: str, return_url: str) -> Dict[str, Any]:
        """Create Stripe customer billing portal session"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            session = self.stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return {
                'success': True,
                'portal_url': session.url
            }
            
        except Exception as e:
            logger.error(f"Failed to create billing portal session: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_webhook(self, payload: str, sig_header: str, webhook_secret: str) -> Dict[str, Any]:
        """Process Stripe webhook events"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            
            event_data = event['data']['object']
            event_type = event['type']
            
            if event_type == 'checkout.session.completed':
                return self._handle_checkout_completed(event_data)
            elif event_type == 'invoice.payment_succeeded':
                return self._handle_payment_succeeded(event_data)
            elif event_type == 'invoice.payment_failed':
                return self._handle_payment_failed(event_data)
            elif event_type == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event_data)
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return {'success': True, 'message': 'Event received'}
                
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_checkout_completed(self, session_data: Dict) -> Dict[str, Any]:
        """Handle completed checkout session"""
        user_id = session_data.get('metadata', {}).get('user_id')
        tier = session_data.get('metadata', {}).get('tier')
        customer_id = session_data.get('customer')
        subscription_id = session_data.get('subscription')
        
        logger.info(f"Checkout completed for user {user_id}, tier {tier}")
        
        # Update user subscription in database
        # This would connect to your user management system
        
        return {
            'success': True,
            'event': 'checkout.completed',
            'user_id': user_id,
            'tier': tier,
            'customer_id': customer_id,
            'subscription_id': subscription_id
        }
    
    def _handle_payment_succeeded(self, invoice_data: Dict) -> Dict[str, Any]:
        """Handle successful payment"""
        subscription_id = invoice_data.get('subscription')
        customer_id = invoice_data.get('customer')
        
        logger.info(f"Payment succeeded for subscription {subscription_id}")
        
        # Update subscription status in database
        # This would connect to your user management system
        
        return {
            'success': True,
            'event': 'payment.succeeded',
            'subscription_id': subscription_id,
            'customer_id': customer_id
        }
    
    def _handle_payment_failed(self, invoice_data: Dict) -> Dict[str, Any]:
        """Handle failed payment"""
        subscription_id = invoice_data.get('subscription')
        customer_id = invoice_data.get('customer')
        
        logger.warning(f"Payment failed for subscription {subscription_id}")
        
        # Notify user of payment failure
        # This would connect to your notification system
        
        return {
            'success': True,
            'event': 'payment.failed',
            'subscription_id': subscription_id,
            'customer_id': customer_id
        }
    
    def _handle_subscription_deleted(self, subscription_data: Dict) -> Dict[str, Any]:
        """Handle subscription deletion"""
        customer_id = subscription_data.get('customer')
        
        logger.info(f"Subscription deleted for customer {customer_id}")
        
        # Downgrade user to free tier
        # This would connect to your user management system
        
        return {
            'success': True,
            'event': 'subscription.deleted',
            'customer_id': customer_id
        }
    
    def get_user_email(self, user_id: str) -> str:
        """Get user email from database (placeholder)"""
        # This would connect to your user database
        # For now, return a placeholder
        return f"user{user_id}@example.com"
    
    def get_subscription_tiers(self) -> Dict[str, Dict]:
        """Get available subscription tiers"""
        return self.subscription_tiers
    
    def calculate_usage_based_pricing(self, usage_metrics: Dict[str, int]) -> Dict[str, Any]:
        """Calculate pricing for usage-based features"""
        base_prices = {
            'extra_guests': 5,  # $5 per additional guest beyond tier limit
            'extra_storage_gb': 0.1,  # $0.10 per GB beyond tier limit
            'premium_scenes': 10  # $10 per premium scene template
        }
        
        total_cost = 0
        breakdown = {}
        
        for metric, value in usage_metrics.items():
            if metric in base_prices:
                cost = value * base_prices[metric]
                breakdown[metric] = cost
                total_cost += cost
        
        return {
            'total_cost_cents': int(total_cost * 100),  # Convert to cents
            'breakdown': breakdown,
            'currency': 'usd'
        }