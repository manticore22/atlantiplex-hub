#!/usr/bin/env python3
"""
SIMPLIFIED GUEST MANAGEMENT TEST SUITE
Testing core Matrix Broadcast Studio guest functionality
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_guest_management_core():
    """Test core guest management functionality"""
    print("=" * 60)
    print("GUEST MANAGEMENT CORE FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        from guest_management import GuestManager, GuestRole, GuestStatus, MediaState
        print("✅ Guest management module imported successfully")
    except ImportError as e:
        print(f"❌ CRITICAL: Cannot import guest_management: {e}")
        return False
    
    # Test 1: Initialize Guest Manager
    print("\n1. Testing Guest Manager Initialization...")
    try:
        manager = GuestManager(max_guests=6)
        assert manager.max_guests == 6
        assert len(manager.guests) == 0
        assert len(manager.guest_slots) == 0
        assert len(manager.waiting_room) == 0
        print("   ✅ Guest Manager initialized correctly")
    except Exception as e:
        print(f"   ❌ Failed to initialize Guest Manager: {e}")
        return False
    
    # Test 2: Create Guest Invitations
    print("\n2. Testing Guest Invitation Creation...")
    test_guests = []
    try:
        for i in range(3):
            result = manager.create_guest_invite(
                f"TestUser{i+1}", f"test{i+1}@example.com", GuestRole.GUEST
            )
            assert 'guest_id' in result
            assert 'invite_code' in result
            assert len(result['invite_code']) == 8
            test_guests.append(result)
        print(f"   ✅ Created {len(test_guests)} guest invitations")
    except Exception as e:
        print(f"   ❌ Failed to create guest invitations: {e}")
        return False
    
    # Test 3: Guest Join System
    print("\n3. Testing Guest Join System...")
    joined_guests = []
    try:
        for i, guest in enumerate(test_guests):
            result = manager.join_via_invite(guest['invite_code'], f"192.168.1.{i+1}", "TestAgent")
            assert 'status' in result
            if result['status'] == 'connected':
                joined_guests.append(result)
        print(f"   ✅ {len(joined_guests)} guests joined successfully")
    except Exception as e:
        print(f"   ❌ Failed guest join test: {e}")
        return False
    
    # Test 4: Slot Management
    print("\n4. Testing Slot Management...")
    try:
        active_guests = manager.get_active_guests()
        print(f"   - Active guests: {len(active_guests)}")
        
        for guest in active_guests:
            assert guest.slot_number is not None
            assert 1 <= guest.slot_number <= 6
            print(f"   - Guest {guest.name} in slot {guest.slot_number}")
        
        print("   ✅ Slot management working correctly")
    except Exception as e:
        print(f"   ❌ Failed slot management test: {e}")
        return False
    
    # Test 5: Moderator Controls
    print("\n5. Testing Moderator Controls...")
    try:
        if active_guests:
            test_guest = active_guests[0]
            
            # Test mute
            success = manager.moderator_mute_guest(test_guest.id, "test_moderator")
            assert success == True
            assert test_guest.status == GuestStatus.MUTED
            print("   ✅ Moderator mute function working")
            
            # Test camera stop
            success = manager.moderator_stop_camera(test_guest.id, "test_moderator")
            assert success == True
            assert test_guest.device.camera_enabled == False
            print("   ✅ Moderator camera control working")
            
            # Test kick
            success = manager.moderator_kick_guest(test_guest.id, "test_moderator", "Test kick")
            assert success == True
            assert test_guest.status == GuestStatus.KICKED
            print("   ✅ Moderator kick function working")
    except Exception as e:
        print(f"   ❌ Failed moderator controls test: {e}")
        return False
    
    # Test 6: Media State Management
    print("\n6. Testing Media State Management...")
    try:
        if active_guests:
            test_guest = active_guests[0] if len(active_guests) > 1 else None
            
            if test_guest:
                # Test camera state changes
                manager.set_guest_media_state(test_guest.id, camera=MediaState.ON)
                assert test_guest.device.camera_enabled == True
                print("   ✅ Camera state ON working")
                
                manager.set_guest_media_state(test_guest.id, camera=MediaState.OFF)
                assert test_guest.device.camera_enabled == False
                print("   ✅ Camera state OFF working")
                
                # Test microphone state changes
                manager.set_guest_media_state(test_guest.id, microphone=MediaState.ON)
                assert test_guest.device.microphone_enabled == True
                print("   ✅ Microphone state ON working")
                
                manager.set_guest_media_state(test_guest.id, microphone=MediaState.MUTED)
                assert test_guest.device.microphone_enabled == False
                print("   ✅ Microphone state MUTED working")
    except Exception as e:
        print(f"   ❌ Failed media state test: {e}")
        return False
    
    # Test 7: Advanced Features
    print("\n7. Testing Advanced Features...")
    try:
        if active_guests:
            test_guest = active_guests[0]
            
            # Test hand raise/lower
            success = manager.raise_hand(test_guest.id)
            assert success == True
            assert test_guest.is_hand_raised == True
            print("   ✅ Hand raise working")
            
            success = manager.lower_hand(test_guest.id)
            assert success == True
            assert test_guest.is_hand_raised == False
            print("   ✅ Hand lower working")
            
            # Test pin functionality
            success = manager.pin_guest(test_guest.id, "test_moderator")
            assert success == True
            assert test_guest.is_pinned == True
            print("   ✅ Guest pin working")
    except Exception as e:
        print(f"   ❌ Failed advanced features test: {e}")
        return False
    
    # Test 8: Device Configuration
    print("\n8. Testing Device Configuration...")
    try:
        if active_guests:
            test_guest = active_guests[0]
            
            config = {
                'video_quality': '1080p',
                'audio_quality': 'high',
                'background_blur': True,
                'camera_device': 'HD Webcam',
                'microphone_device': 'Blue Yeti'
            }
            
            success = manager.update_guest_device_config(test_guest.id, config)
            assert success == True
            assert test_guest.device.video_quality == '1080p'
            assert test_guest.device.audio_quality == 'high'
            assert test_guest.device.background_blur == True
            print("   ✅ Device configuration working")
    except Exception as e:
        print(f"   ❌ Failed device configuration test: {e}")
        return False
    
    # Test 9: Studio Status Reporting
    print("\n9. Testing Studio Status Reporting...")
    try:
        status = manager.get_studio_status()
        
        required_fields = [
            'total_slots', 'occupied_slots', 'available_slots',
            'waiting_room_count', 'guests_in_studio', 'slot_layout'
        ]
        
        for field in required_fields:
            assert field in status
        
        assert status['total_slots'] == 6
        assert status['occupied_slots'] >= 0
        assert status['available_slots'] >= 0
        assert status['occupied_slots'] + status['available_slots'] == 6
        
        print(f"   ✅ Studio status: {status['occupied_slots']}/{status['total_slots']} slots occupied")
        print("   ✅ Studio status reporting working")
    except Exception as e:
        print(f"   ❌ Failed studio status test: {e}")
        return False
    
    # Test 10: Waiting Room System
    print("\n10. Testing Waiting Room System...")
    try:
        # Fill all slots
        for i in range(len(active_guests), 6):
            result = manager.create_guest_invite(
                f"FillUser{i}", f"fill{i}@example.com"
            )
            manager.join_via_invite(result['invite_code'])
        
        # Try to add one more - should go to waiting room
        result = manager.create_guest_invite(
            "WaitingGuest", "waiting@example.com"
        )
        join_result = manager.join_via_invite(result['invite_code'])
        
        assert join_result['status'] == 'waiting_room'
        assert len(manager.waiting_room) >= 1
        print(f"   ✅ Waiting room system working - {len(manager.waiting_room)} guests in queue")
    except Exception as e:
        print(f"   ❌ Failed waiting room test: {e}")
        return False
    
    # Test 11: Export Functionality
    print("\n11. Testing Export Functionality...")
    try:
        export_data = manager.export_guest_list()
        
        required_fields = ['total_guests', 'active_guests', 'waiting_guests', 'guests', 'export_time']
        for field in required_fields:
            assert field in export_data
        
        assert isinstance(export_data['guests'], list)
        assert export_data['export_time'] is not None
        
        print(f"   ✅ Export successful - {export_data['total_guests']} total guests")
    except Exception as e:
        print(f"   ❌ Failed export test: {e}")
        return False
    
    # Test 12: Security Considerations
    print("\n12. Testing Security Considerations...")
    try:
        # Test invalid guest ID handling
        success = manager.moderator_mute_guest("invalid_id", "moderator")
        assert success == False
        
        success = manager.raise_hand("invalid_id")
        assert success == False
        
        success = manager.set_guest_media_state("invalid_id", camera=MediaState.ON)
        assert success == False
        
        print("   ✅ Invalid guest ID handling working")
    except Exception as e:
        print(f"   ❌ Failed security test: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("ALL CORE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True

def test_matrix_studio_api():
    """Test Matrix Studio API integration"""
    print("\n" + "=" * 60)
    print("MATRIX STUDIO API INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from matrix_studio.matrix_studio_final import app
        print("✅ Matrix Studio app imported successfully")
        
        # Test that the Flask app is configured
        assert app is not None
        print("✅ Flask app is configured")
        
        # Test basic routes exist
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        required_routes = ['/api/health', '/api/guests/invite', '/api/guests/status']
        for route in required_routes:
            matching_routes = [r for r in routes if route in r]
            assert len(matching_routes) > 0, f"Route {route} not found"
        
        print(f"✅ Required API routes found ({len(required_routes)} routes)")
        print(f"✅ Total routes available: {len(routes)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import Matrix Studio: {e}")
        return False
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def test_guest_html_interface():
    """Test guest HTML interface"""
    print("\n" + "=" * 60)
    print("GUEST HTML INTERFACE TEST")
    print("=" * 60)
    
    guest_html_path = "matrix-studio/public/guest.html"
    
    if not os.path.exists(guest_html_path):
        print(f"❌ Guest HTML file not found: {guest_html_path}")
        return False
    
    try:
        with open(guest_html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential elements
        required_elements = [
            'id="guestName"',           # Guest name input
            'id="sessionCode"',          # Session code input
            'connectToSession()',       # Connection function
            'toggleAudio()',            # Audio control
            'toggleVideo()',            # Video control
            'socket.io',                # Socket.io connection
            'RTCPeerConnection'         # WebRTC functionality
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing elements: {missing_elements}")
            return False
        
        print("✅ Guest HTML interface contains all required elements")
        print("✅ Guest interface is properly structured")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test guest HTML interface: {e}")
        return False

def main():
    """Main test execution"""
    print("MATRIX BROADCAST STUDIO - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing all guest management functionality")
    print("Timestamp:", datetime.now().isoformat())
    print()
    
    test_results = []
    
    # Run all test suites
    test_suites = [
        ("Core Guest Management", test_guest_management_core),
        ("Matrix Studio API", test_matrix_studio_api),
        ("Guest HTML Interface", test_guest_html_interface)
    ]
    
    for suite_name, test_function in test_suites:
        print(f"\n{'='*20} {suite_name} {'='*20}")
        
        start_time = time.time()
        success = test_function()
        execution_time = time.time() - start_time
        
        test_results.append({
            'suite': suite_name,
            'success': success,
            'execution_time': execution_time
        })
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{suite_name}: {status} ({execution_time:.3f}s)")
    
    # Generate final report
    print("\n" + "=" * 60)
    print("FINAL TEST REPORT")
    print("=" * 60)
    
    total_suites = len(test_results)
    passed_suites = sum(1 for r in test_results if r['success'])
    failed_suites = total_suites - passed_suites
    
    print(f"Total Test Suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {failed_suites}")
    print(f"Success Rate: {(passed_suites/total_suites)*100:.1f}%")
    
    total_time = sum(r['execution_time'] for r in test_results)
    print(f"Total Execution Time: {total_time:.3f}s")
    
    if failed_suites == 0:
        print("\n🎉 ALL TESTS PASSED! System is functioning correctly.")
    else:
        print(f"\n⚠️  {failed_suites} test suite(s) failed. Review the issues above.")
    
    # Save test report
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_results': test_results,
        'summary': {
            'total_suites': total_suites,
            'passed_suites': passed_suites,
            'failed_suites': failed_suites,
            'success_rate': (passed_suites/total_suites)*100,
            'total_execution_time': total_time
        }
    }
    
    try:
        with open('guest_management_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Test report saved to: guest_management_test_report.json")
    except Exception as e:
        print(f"\n❌ Failed to save test report: {e}")
    
    return failed_suites == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)