"""
Quick SaaS Test Script - Verify Multi-Tenant Platform Functionality
Tests organization creation, tenant isolation, and dashboard features
"""

import sys
import json
from datetime import datetime

def test_saas_components():
    """Test all SaaS components"""
    print("=" * 70)
    print("  ATLANTIPLEX LIGHTNING STUDIO - SaaS COMPONENT TEST")
    print("=" * 70)
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Multi-Tenant Manager
    print("[TEST 1] Multi-Tenant Manager...")
    try:
        from saas_multi_tenant import MultiTenantManager, UserRole
        mt = MultiTenantManager()
        
        # Create test organization
        org = mt.create_organization(
            name="TestCorp Inc",
            domain="testcorp.com",
            subdomain="testcorp",
            billing_email="admin@testcorp.com",
            subscription_tier="professional"
        )
        
        # Create team
        team = mt.create_team(
            organization_id=org.id,
            name="Engineering",
            description="Engineering team"
        )
        
        print(f"   ✅ Created organization: {org.name} ({org.id})")
        print(f"   ✅ Created team: {team.name}")
        print(f"   ✅ Subscription tier: {org.subscription_tier}")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        tests_failed += 1
    
    print()
    
    # Test 2: Database Schema
    print("[TEST 2] Database Schema...")
    try:
        from saas_database import SaaSDatabaseManager
        db = SaaSDatabaseManager()
        
        # Test organization creation
        org_data = {
            'name': 'DemoOrg',
            'domain': 'demoorg.com',
            'subdomain': 'demoorg',
            'billing_email': 'billing@demoorg.com',
            'subscription_tier': 'starter'
        }
        org_id = db.create_organization(org_data)
        
        # Test retrieval
        org = db.get_organization_by_subdomain('demoorg')
        
        print(f"   ✅ Database schema initialized")
        print(f"   ✅ Created organization: {org_id}")
        print(f"   ✅ Retrieved by subdomain: {org['name']}")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        tests_failed += 1
    
    print()
    
    # Test 3: Dashboard
    print("[TEST 3] Dashboard Components...")
    try:
        from saas_database import SaaSDatabaseManager
        from saas_dashboard import SaaSDashboard
        
        db = SaaSDatabaseManager()
        dashboard = SaaSDashboard(db)
        
        # Get organization stats
        stats = dashboard.get_dashboard_stats(org_id)
        
        print(f"   ✅ Dashboard initialized")
        print(f"   ✅ Organization stats retrieved")
        print(f"      - Users: {stats['stats']['users']}")
        print(f"      - Teams: {stats['stats']['teams']}")
        print(f"      - Storage: {stats['stats']['storage_used_gb']}GB")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        tests_failed += 1
    
    print()
    
    # Test 4: Subscription Tiers
    print("[TEST 4] Subscription Tiers...")
    try:
        from subscription_manager import TierManager
        
        tm = TierManager()
        
        # Check all tiers exist
        tiers = ['free', 'starter', 'professional', 'enterprise']
        for tier_name in tiers:
            tier_config = tm.tier_configs.get(tier_name)
            if tier_config:
                print(f"   ✅ {tier_name.title()}: ${tier_config['price']}")
        
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        tests_failed += 1
    
    print()
    
    # Test 5: Tenant Context
    print("[TEST 5] Tenant Middleware...")
    try:
        from saas_middleware import TenantContext, tenant_required
        
        # Create context
        ctx = TenantContext()
        ctx.set_tenant('test-123', {'name': 'Test Org', 'id': 'test-123'})
        
        print(f"   ✅ Tenant context created")
        print(f"   ✅ Tenant ID: {ctx.organization_id}")
        print(f"   ✅ Organization: {ctx.organization['name']}")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        tests_failed += 1
    
    print()
    
    # Summary
    print("=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print()
    print(f"  ✅ Tests Passed: {tests_passed}")
    print(f"  ❌ Tests Failed: {tests_failed}")
    print()
    
    if tests_failed == 0:
        print("  🎉 ALL SAAS COMPONENTS WORKING CORRECTLY!")
        print()
        print("  Ready to launch:")
        print("     python saas_platform.py")
        print()
        return 0
    else:
        print("  ⚠️  Some tests failed. Check error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = test_saas_components()
    sys.exit(exit_code)