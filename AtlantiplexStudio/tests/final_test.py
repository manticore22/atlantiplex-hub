#!/usr/bin/env python3
"""
MATRIX BROADCAST STUDIO - FINAL SYSTEM TEST
"""

def test_avatar_system():
    print("Testing Avatar System...")
    try:
        from avatar_management import AvatarManager, ProfileManager
        avatar_manager = AvatarManager()
        profile_manager = ProfileManager()
        profile = profile_manager.create_user_profile("test_user", "Test User", "test@example.com")
        updated = profile_manager.update_profile("test_user", {'display_name': 'Updated Test User'})
        print("  + Avatar System: WORKING")
        return True
    except Exception as e:
        print(f"  - Avatar System: ERROR - {e}")
        return False

def test_guest_management():
    print("Testing Guest Management...")
    try:
        from guest_management import GuestManager, GuestRole
        guest_manager = GuestManager(max_guests=8)
        invite = guest_manager.create_guest_invite("Test Guest", "guest@example.com", GuestRole.GUEST)
        join_result = guest_manager.join_via_invite(invite['invite_code'])
        print("  + Guest Management: WORKING")
        return True
    except Exception as e:
        print(f"  - Guest Management: ERROR - {e}")
        return False

def test_scene_manager():
    print("Testing Scene Manager...")
    try:
        from scene_manager import SceneManager
        scene_manager = SceneManager()
        scene = scene_manager.create_scene("Test Scene", "custom")
        switch_result = scene_manager.switch_scene(scene.id)
        print("  + Scene Manager: WORKING")
        return True
    except Exception as e:
        print(f"  - Scene Manager: ERROR - {e}")
        return False

def main():
    print("MATRIX BROADCAST STUDIO - SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        ("Avatar System", test_avatar_system),
        ("Guest Management", test_guest_management),
        ("Scene Manager", test_scene_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
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