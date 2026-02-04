"""
Subscription Tier Management System for Atlantiplex Matrix Studio
Manages user subscription levels, feature access, and billing
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubscriptionTier(Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ADMIN_UNLIMITED = "admin_unlimited"

class TierManager:
    """Manages subscription tiers and feature access"""
    
    def __init__(self):
        # Define subscription tier configurations
        self.tier_configs = {
            SubscriptionTier.FREE: {
                'name': 'Free',
                'price': 0,
                'currency': 'usd',
                'billing_cycle': 'none',
                'features': {
                    'guest_management': {
                        'max_concurrent': 1,
                        'total_sessions_per_day': 3,
                        'session_duration_hours': 2
                    },
                    'streaming': {
                        'max_quality': 'SD',
                        'max_duration_hours': 2,
                        'platforms': ['youtube']
                    },
                    'features': {
                        'basic_scenes': True,
                        'premium_scenes': False,
                        'custom_scenes': False,
                        'analytics': False,
                        'cloud_storage': False,
                        'api_access': False
                    },
                    'support': {
                        'email_support': False,
                        'priority_support': False,
                        'phone_support': False
                    }
                },
                'limits': {
                    'bandwidth_gb_per_month': 10,
                    'storage_gb': 0,
                    'api_calls_per_day': 0
                }
            },
            
            SubscriptionTier.STARTER: {
                'name': 'Starter',
                'price': 9.99,
                'currency': 'usd',
                'billing_cycle': 'monthly',
                'stripe_price_id': 'price_starter_monthly',
                'features': {
                    'guest_management': {
                        'max_concurrent': 3,
                        'total_sessions_per_day': 10,
                        'session_duration_hours': 4
                    },
                    'streaming': {
                        'max_quality': 'HD',
                        'max_duration_hours': 4,
                        'platforms': ['youtube', 'twitch']
                    },
                    'features': {
                        'basic_scenes': True,
                        'premium_scenes': True,
                        'custom_scenes': False,
                        'analytics': True,
                        'cloud_storage': True,
                        'api_access': False
                    },
                    'support': {
                        'email_support': True,
                        'priority_support': False,
                        'phone_support': False
                    }
                },
                'limits': {
                    'bandwidth_gb_per_month': 100,
                    'storage_gb': 10,
                    'api_calls_per_day': 100
                }
            },
            
            SubscriptionTier.PROFESSIONAL: {
                'name': 'Professional',
                'price': 29.99,
                'currency': 'usd',
                'billing_cycle': 'monthly',
                'stripe_price_id': 'price_professional_monthly',
                'features': {
                    'guest_management': {
                        'max_concurrent': 10,
                        'total_sessions_per_day': 50,
                        'session_duration_hours': 8
                    },
                    'streaming': {
                        'max_quality': 'Full HD',
                        'max_duration_hours': 8,
                        'platforms': ['youtube', 'twitch', 'facebook', 'instagram']
                    },
                    'features': {
                        'basic_scenes': True,
                        'premium_scenes': True,
                        'custom_scenes': True,
                        'analytics': True,
                        'cloud_storage': True,
                        'api_access': True
                    },
                    'support': {
                        'email_support': True,
                        'priority_support': True,
                        'phone_support': False
                    }
                },
                'limits': {
                    'bandwidth_gb_per_month': 500,
                    'storage_gb': 100,
                    'api_calls_per_day': 1000
                }
            },
            
            SubscriptionTier.ENTERPRISE: {
                'name': 'Enterprise',
                'price': 99.99,
                'currency': 'usd',
                'billing_cycle': 'monthly',
                'stripe_price_id': 'price_enterprise_monthly',
                'features': {
                    'guest_management': {
                        'max_concurrent': 50,
                        'total_sessions_per_day': 200,
                        'session_duration_hours': 24
                    },
                    'streaming': {
                        'max_quality': '4K',
                        'max_duration_hours': 24,
                        'platforms': ['youtube', 'twitch', 'facebook', 'instagram', 'linkedin', 'twitter']
                    },
                    'features': {
                        'basic_scenes': True,
                        'premium_scenes': True,
                        'custom_scenes': True,
                        'analytics': True,
                        'cloud_storage': True,
                        'api_access': True,
                        'white_label': True,
                        'custom_branding': True
                    },
                    'support': {
                        'email_support': True,
                        'priority_support': True,
                        'phone_support': True,
                        'dedicated_account_manager': True
                    }
                },
                'limits': {
                    'bandwidth_gb_per_month': 2000,
                    'storage_gb': 1000,
                    'api_calls_per_day': 10000
                }
            },
            
            SubscriptionTier.ADMIN_UNLIMITED: {
                'name': 'Admin Unlimited',
                'price': 0,
                'currency': 'usd',
                'billing_cycle': 'none',
                'features': {
                    'guest_management': {
                        'max_concurrent': float('inf'),
                        'total_sessions_per_day': float('inf'),
                        'session_duration_hours': float('inf')
                    },
                    'streaming': {
                        'max_quality': '4K+',
                        'max_duration_hours': float('inf'),
                        'platforms': 'all'
                    },
                    'features': {
                        'basic_scenes': True,
                        'premium_scenes': True,
                        'custom_scenes': True,
                        'analytics': True,
                        'cloud_storage': True,
                        'api_access': True,
                        'white_label': True,
                        'custom_branding': True,
                        'reseller_access': True,
                        'system_admin': True
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
                    'bandwidth_gb_per_month': float('inf'),
                    'storage_gb': float('inf'),
                    'api_calls_per_day': float('inf')
                }
            }
        }
        
        # User subscriptions (in production, store in database)
        self.user_subscriptions = {}
        
        # Usage tracking
        self.usage_tracking = {}
    
    def get_user_tier(self, user_id: str) -> SubscriptionTier:
        """Get user's current subscription tier"""
        subscription = self.user_subscriptions.get(user_id)
        if subscription:
            return subscription['tier']
        
        # Default to free tier
        return SubscriptionTier.FREE
    
    def set_user_tier(self, user_id: str, tier: SubscriptionTier, subscription_id: str = None) -> Dict[str, Any]:
        """Set user's subscription tier"""
        # Check if admin bypass
        if user_id == 'admin_001':
            tier = SubscriptionTier.ADMIN_UNLIMITED
        
        self.user_subscriptions[user_id] = {
            'tier': tier,
            'subscription_id': subscription_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'active': True
        }
        
        logger.info(f"User {user_id} tier set to {tier.value}")
        
        return {
            'success': True,
            'tier': tier.value,
            'features': self.tier_configs[tier]['features']
        }
    
    def can_access_feature(self, user_id: str, feature_path: str) -> bool:
        """Check if user can access a specific feature"""
        tier = self.get_user_tier(user_id)
        tier_config = self.tier_configs[tier]
        
        # Admin bypass
        if tier == SubscriptionTier.ADMIN_UNLIMITED:
            return True
        
        # Navigate feature path
        feature_parts = feature_path.split('.')
        current = tier_config['features']
        
        for part in feature_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        return bool(current)
    
    def get_user_limits(self, user_id: str) -> Dict[str, Any]:
        """Get user's resource limits"""
        tier = self.get_user_tier(user_id)
        return self.tier_configs[tier]['limits']
    
    def check_limit(self, user_id: str, limit_type: str, current_usage: int) -> Dict[str, Any]:
        """Check if user has reached a specific limit"""
        limits = self.get_user_limits(user_id)
        limit = limits.get(limit_type, 0)
        
        if limit == float('inf'):
            return {'allowed': True, 'remaining': float('inf'), 'percentage': 0}
        
        remaining = max(0, limit - current_usage)
        percentage = (current_usage / limit) * 100 if limit > 0 else 100
        
        return {
            'allowed': remaining > 0,
            'remaining': remaining,
            'limit': limit,
            'current_usage': current_usage,
            'percentage': percentage
        }
    
    def get_tier_comparison(self) -> Dict[str, Any]:
        """Get comparison of all subscription tiers"""
        comparison = {}
        
        for tier, config in self.tier_configs.items():
            comparison[tier.value] = {
                'name': config['name'],
                'price': config['price'],
                'currency': config['currency'],
                'billing_cycle': config['billing_cycle'],
                'features': config['features'],
                'limits': config['limits']
            }
        
        return comparison
    
    def get_upgrade_options(self, user_id: str) -> Dict[str, Any]:
        """Get available upgrade options for user"""
        current_tier = self.get_user_tier(user_id)
        
        if current_tier == SubscriptionTier.ADMIN_UNLIMITED:
            return {'upgrades': [], 'message': 'Already at maximum tier'}
        
        upgrade_tiers = []
        
        # Define upgrade paths
        tier_order = [
            SubscriptionTier.FREE,
            SubscriptionTier.STARTER,
            SubscriptionTier.PROFESSIONAL,
            SubscriptionTier.ENTERPRISE
        ]
        
        current_index = tier_order.index(current_tier) if current_tier in tier_order else -1
        
        for i in range(current_index + 1, len(tier_order)):
            tier = tier_order[i]
            config = self.tier_configs[tier]
            
            upgrade_tiers.append({
                'tier': tier.value,
                'name': config['name'],
                'price': config['price'],
                'currency': config['currency'],
                'billing_cycle': config['billing_cycle'],
                'features': config['features'],
                'upgrade_benefits': self._get_upgrade_benefits(current_tier, tier)
            })
        
        return {
            'current_tier': current_tier.value,
            'current_features': self.tier_configs[current_tier]['features'],
            'available_upgrades': upgrade_tiers
        }
    
    def _get_upgrade_benefits(self, from_tier: SubscriptionTier, to_tier: SubscriptionTier) -> List[str]:
        """Get list of benefits when upgrading"""
        from_config = self.tier_configs[from_tier]
        to_config = self.tier_configs[to_tier]
        
        benefits = []
        
        # Compare guest management
        from_guests = from_config['features']['guest_management']['max_concurrent']
        to_guests = to_config['features']['guest_management']['max_concurrent']
        if to_guests > from_guests:
            if to_guests == float('inf'):
                benefits.append("Unlimited concurrent guests")
            else:
                benefits.append(f"Increase from {from_guests} to {to_guests} concurrent guests")
        
        # Compare streaming quality
        from_quality = from_config['features']['streaming']['max_quality']
        to_quality = to_config['features']['streaming']['max_quality']
        if to_quality != from_quality:
            benefits.append(f"Upgrade from {from_quality} to {to_quality} streaming quality")
        
        # Compare features
        for feature, value in to_config['features'].items():
            if feature in from_config['features']:
                from_value = from_config['features'][feature]
                if not from_value and value:
                    benefits.append(f"Add {feature.replace('_', ' ').title()} feature")
        
        return benefits
    
    def track_usage(self, user_id: str, usage_type: str, amount: int) -> Dict[str, Any]:
        """Track user usage"""
        if user_id not in self.usage_tracking:
            self.usage_tracking[user_id] = {}
        
        if usage_type not in self.usage_tracking[user_id]:
            self.usage_tracking[user_id][usage_type] = {
                'total': 0,
                'daily': 0,
                'last_reset': datetime.utcnow().date()
            }
        
        # Reset daily counter if new day
        today = datetime.utcnow().date()
        if self.usage_tracking[user_id][usage_type]['last_reset'] != today:
            self.usage_tracking[user_id][usage_type]['daily'] = 0
            self.usage_tracking[user_id][usage_type]['last_reset'] = today
        
        # Update usage
        self.usage_tracking[user_id][usage_type]['total'] += amount
        self.usage_tracking[user_id][usage_type]['daily'] += amount
        
        # Check limits
        limit_check = self.check_limit(user_id, usage_type, self.usage_tracking[user_id][usage_type]['daily'])
        
        return {
            'success': True,
            'usage': self.usage_tracking[user_id][usage_type],
            'limit_check': limit_check
        }
    
    def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's current usage statistics"""
        if user_id not in self.usage_tracking:
            return {'message': 'No usage data available'}
        
        usage_data = self.usage_tracking[user_id]
        limits = self.get_user_limits(user_id)
        
        stats = {}
        for usage_type, data in usage_data.items():
            limit_check = self.check_limit(user_id, usage_type, data['daily'])
            stats[usage_type] = {
                'daily': data['daily'],
                'total': data['total'],
                'limit': limits.get(usage_type, 0),
                'percentage_used': limit_check['percentage'],
                'remaining': limit_check['remaining']
            }
        
        return stats
    
    def get_tier_info(self, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get detailed information about a specific tier"""
        return self.tier_configs.get(tier, {})
    
    def calculate_downgrade_impact(self, user_id: str, new_tier: SubscriptionTier) -> Dict[str, Any]:
        """Calculate impact of downgrading to a lower tier"""
        current_tier = self.get_user_tier(user_id)
        current_config = self.tier_configs[current_tier]
        new_config = self.tier_configs[new_tier]
        
        impacts = []
        
        # Check current usage against new limits
        if user_id in self.usage_tracking:
            for limit_type, limit_value in new_config['limits'].items():
                current_usage = self.usage_tracking[user_id].get(limit_type, {}).get('daily', 0)
                if current_usage > limit_value:
                    impacts.append({
                        'type': 'exceeds_limit',
                        'limit_type': limit_type,
                        'current_usage': current_usage,
                        'new_limit': limit_value,
                        'impact': f"Current {limit_type} usage ({current_usage}) exceeds new limit ({limit_value})"
                    })
        
        # Compare features
        for feature, value in current_config['features'].items():
            if feature in new_config['features']:
                new_value = new_config['features'][feature]
                if value and not new_value:
                    impacts.append({
                        'type': 'feature_loss',
                        'feature': feature,
                        'impact': f"Will lose access to {feature.replace('_', ' ').title()}"
                    })
        
        return {
            'current_tier': current_tier.value,
            'new_tier': new_tier.value,
            'impacts': impacts,
            'has_impact': len(impacts) > 0
        }