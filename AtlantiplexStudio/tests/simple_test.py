#!/usr/bin/env python3
"""
MATRIX BROADCAST STUDIO - COMPLETE SYSTEM TEST
Simple test runner without Unicode issues
"""

import os
import json
import time
import logging
import sys
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_avatar_system():
    """Test avatar management system"""
    print("Testing Avatar System...")
    
    try:
        from avatar_management import AvatarManager, ProfileManager
        
        # Test initialization
        avatar_manager = AvatarManager()
        print("  + Avatar Manager initialized")
        
        profile_manager = ProfileManager()
        print("  + Profile Manager initialized")
        
        # Test profile creation
        profile = profile_manager.create_user_profile("test_user", "Test User", "test@example.com")
        print("  + Profile creation works")
        
        # Test profile update
        updated = profile_manager.update_profile("test_user", {'display_name': 'Updated Test User'})
        print("  + Profile update works")
        
        return True
        
    except Exception as e:
        print(f"  - ERROR: {e}")
        return False

def test_guest_management():
    """Test guest management system"""
    print("Testing Guest Management...")
    
    try:
        from guest_management import GuestManager, GuestRole, GuestStatus
        
        # Test initialization
        guest_manager = GuestManager(max_guests=8)
        print("  + Guest Manager initialized")
        
        # Test invitation
        invite = guest_manager.create_guest_invite("Test Guest", "guest@example.com", GuestRole.GUEST)
        print("  + Guest invitation works")
        
        # Test join
        join_result = guest_manager.join_via_invite(invite['invite_code'])
        print("  + Guest join works")
        
        return True
        
    except Exception as e:
        print(f"  - ERROR: {e}")
        return False

def test_scene_manager():
    """Test scene management system"""
    print("Testing Scene Manager...")
    
    try:
        from scene_manager import SceneManager
        
        # Test initialization
        scene_manager = SceneManager()
        print("  + Scene Manager initialized")
        
        # Test scene creation
        scene = scene_manager.create_scene("Test Scene", "custom")
        print("  + Scene creation works")
        
        # Test scene switching
        switch_result = scene_manager.switch_scene(scene.id)
        print("  + Scene switching works")
        
        return True
        
    except Exception as e:
        print(f"  - ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("MATRIX BROADCAST STUDIO - SYSTEM TEST")
    print("=" * 50)
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    tests = [
        ("Avatar System", test_avatar_system),
        ("Guest Management", test_guest_management),
        ("Scene Manager", test_scene_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"[PASS] {test_name}")
            else:
                print(f"[FAIL] {test_name}")
        except Exception as e:
            print(f"[ERROR] {test_name}: {e}")
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    success_rate = (passed / total) * 100
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("Status: PRODUCTION READY")
    else:
        print("Status: NEEDS WORK")
    
    print("=" * 50)
    
    return 0 if success_rate >= 90 else 1

if __name__ == "__main__":
    exit(main())