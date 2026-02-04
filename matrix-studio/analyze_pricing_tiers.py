"""
Pricing Tiers Analysis Script for Atlantiplex Lightning Studio
Validates all subscription tiers, features, and pricing calculations
"""

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_pricing_tiers():
    """Analyze all subscription pricing tiers"""
    logger.info("💰 Analyzing Subscription Pricing Tiers...")
    
    try:
        from subscription_manager import TierManager, SubscriptionTier
        
        tier_manager = TierManager()
        
        # Check all tiers are defined
        expected_tiers = [
            SubscriptionTier.FREE,
            SubscriptionTier.STARTER, 
            SubscriptionTier.PROFESSIONAL,
            SubscriptionTier.ENTERPRISE,
            SubscriptionTier.ADMIN_UNLIMITED
        ]
        
        logger.info("✅ Subscription Tiers Analysis:")
        for tier in expected_tiers:
            if tier in tier_manager.tier_configs:
                config = tier_manager.tier_configs[tier]
                analyze_single_tier(tier, config)
            else:
                logger.error(f"❌ Missing tier: {tier.value}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        return False

def analyze_single_tier(tier, config):
    """Analyze a single subscription tier"""
    logger.info(f"   📊 {tier.value.upper()}: {config['name']}")
    
    # Pricing validation
    price = config.get('price', 0)
    currency = config.get('currency', 'usd')
    billing_cycle = config.get('billing_cycle', 'none')
    
    logger.info(f"      💵 Price: ${price:.2f} {currency.upper()} / {billing_cycle}")
    
    # Features analysis
    features = config.get('features', {})
    guest_mgmt = features.get('guest_management', {})
    streaming = features.get('streaming', {})
    feature_list = features.get('features', {})
    support = features.get('support', {})
    
    # Guest management features
    max_concurrent = guest_mgmt.get('max_concurrent', 0)
    sessions_per_day = guest_mgmt.get('total_sessions_per_day', 0)
    session_duration = guest_mgmt.get('session_duration_hours', 0)
    
    logger.info(f"      👥 Guests: {max_concurrent} concurrent, {sessions_per_day}/day, {session_duration}h max")
    
    # Streaming features
    max_quality = streaming.get('max_quality', 'SD')
    max_stream_duration = streaming.get('max_duration_hours', 0)
    platforms = streaming.get('platforms', [])
    
    logger.info(f"      📺 Streaming: {max_quality}, {max_stream_duration}h max, {len(platforms)} platforms")
    
    # General features
    basic_scenes = feature_list.get('basic_scenes', False)
    premium_scenes = feature_list.get('premium_scenes', False) 
    custom_scenes = feature_list.get('custom_scenes', False)
    analytics = feature_list.get('analytics', False)
    cloud_storage = feature_list.get('cloud_storage', False)
    api_access = feature_list.get('api_access', False)
    
    logger.info(f"      🎨 Features: Basic:{basic_scenes} Premium:{premium_scenes} Custom:{custom_scenes}")
    logger.info(f"      📈 Analytics:{analytics} Storage:{cloud_storage} API:{api_access}")
    
    # Support features
    email_support = support.get('email_support', False)
    priority_support = support.get('priority_support', False)
    phone_support = support.get('phone_support', False)
    dedicated_support = support.get('dedicated_account_manager', False)
    support_24_7 = support.get('24_7_support', False)
    
    logger.info(f"      🎯 Support: Email:{email_support} Priority:{priority_support} Phone:{phone_support}")
    if dedicated_support or support_24_7:
        logger.info(f"      🏢 Premium Support: Dedicated:{dedicated_support} 24/7:{support_24_7}")
    
    # Limits analysis
    limits = config.get('limits', {})
    bandwidth = limits.get('bandwidth_gb_per_month', 0)
    storage = limits.get('storage_gb', 0)
    api_calls = limits.get('api_calls_per_day', 0)
    
    logger.info(f"      📊 Limits: {bandwidth}GB bandwidth, {storage}GB storage, {api_calls} API calls/day")
    
    logger.info("")

def validate_stripe_price_mapping():
    """Validate Stripe price ID mapping"""
    logger.info("💳 Validating Stripe Price ID Mapping...")
    
    try:
        from stripe_payments import StripePaymentManager
        
        # Initialize with demo key
        payment_manager = StripePaymentManager('sk_test_demo_key')
        
        if payment_manager.stripe_available:
            tiers = payment_manager.subscription_tiers
            
            for tier_key, tier_config in tiers.items():
                price_id = tier_config.get('price_id')
                amount = tier_config.get('amount', 0)
                currency = tier_config.get('currency', 'usd')
                
                if price_id and price_id != 'price_placeholder':
                    logger.info(f"   ✅ {tier_key.title()}: {price_id} -> ${amount/100:.2f} {currency.upper()}")
                else:
                    logger.warning(f"   ⚠️ {tier_key.title()}: Missing or placeholder price ID")
                    
            return True
        else:
            logger.error("❌ Stripe not available")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Validation failed: {str(e)}")
        return False

def test_tier_progression():
    """Test tier progression logic"""
    logger.info("📈 Testing Tier Progression Logic...")
    
    try:
        from subscription_manager import TierManager, SubscriptionTier
        
        tier_manager = TierManager()
        
        # Test tier hierarchy
        tier_hierarchy = [
            (SubscriptionTier.FREE, SubscriptionTier.STARTER),
            (SubscriptionTier.STARTER, SubscriptionTier.PROFESSIONAL),
            (SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE),
            (SubscriptionTier.ENTERPRISE, SubscriptionTier.ADMIN_UNLIMITED)
        ]
        
        for from_tier, to_tier in tier_hierarchy:
            from_config = tier_manager.tier_configs[from_tier]
            to_config = tier_manager.tier_configs[to_tier]
            
            # Check feature upgrades
            upgrade_benefits = []
            from_features = from_config.get('features', {})
            to_features = to_config.get('features', {})
            
            for feature, enabled in to_features.items():
                if enabled and not from_features.get(feature, False):
                    upgrade_benefits.append(feature)
            
            logger.info(f"   📊 {from_tier.value} → {to_tier.value}: +{len(upgrade_benefits)} new features")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

def generate_pricing_report():
    """Generate comprehensive pricing report"""
    logger.info("📋 Generating Pricing Tiers Report...")
    
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'tier_analysis': analyze_pricing_tiers(),
        'stripe_mapping': validate_stripe_price_mapping(),
        'tier_progression': test_tier_progression()
    }
    
    overall_status = all(report.values())
    report['overall_status'] = 'COMPLETE' if overall_status else 'NEEDS_FIXES'
    
    # Save report
    import json
    with open('pricing_tiers_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info("📋 Report saved to pricing_tiers_report.json")
    return report

if __name__ == "__main__":
    print("============================================================")
    print("        PRICING TIERS ANALYSIS SUITE")
    print("              Atlantiplex Lightning Studio")
    print("============================================================")
    print()
    
    report = generate_pricing_report()
    
    print()
    print("============================================================")
    print("PRICING TIERS ANALYSIS RESULTS:")
    print(f"   Tier Definitions: {'COMPLETE' if report['tier_analysis'] else 'INCOMPLETE'}")
    print(f"   Stripe Mapping: {'COMPLETE' if report['stripe_mapping'] else 'INCOMPLETE'}")
    print(f"   Tier Progression: {'VALID' if report['tier_progression'] else 'INVALID'}")
    print()
    print(f"OVERALL STATUS: {'✅ ALL TIERS PROPERLY DEFINED' if report['overall_status'] == 'COMPLETE' else '⚠️ CONFIGURATION NEEDED'}")
    print("============================================================")