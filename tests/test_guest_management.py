#!/usr/bin/env python3
"""
COMPREHENSIVE GUEST MANAGEMENT TEST SUITE
Testing all Matrix Broadcast Studio guest functionality
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from guest_management import (
        GuestManager, GuestRole, GuestStatus, MediaState,
        StreamGuest, GuestDevice, GuestPermissions
    )
    GUEST_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    print(f"❌ CRITICAL: Cannot import guest_management: {e}")
    GUEST_MANAGEMENT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuestManagementTester:
    """Comprehensive test suite for guest management"""
    
    def __init__(self):
        self.test_results = []
        self.guest_manager = None
        self.test_guests = {}
        self.performance_metrics = {}
        
    def run_test(self, test_name: str, test_function, expected_result=None):
        """Run a single test and record results"""
        start_time = time.time()
        status = "❌ FAIL"
        error_message = ""
        actual_result = None
        
        try:
            if not GUEST_MANAGEMENT_AVAILABLE:
                raise Exception("Guest management module not available")
                
            actual_result = test_function()
            if expected_result is None or actual_result == expected_result:
                status = "✅ PASS"
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Test {test_name} failed: {e}")
        
        execution_time = time.time() - start_time
        
        result = {
            'test_name': test_name,
            'status': status,
            'execution_time': execution_time,
            'expected_result': expected_result,
            'actual_result': actual_result,
            'error_message': error_message
        }
        
        self.test_results.append(result)
        return result
    
    def setup_test_environment(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        if not GUEST_MANAGEMENT_AVAILABLE:
            print("❌ Cannot setup test environment - guest management module not available")
            return False
            
        self.guest_manager = GuestManager(max_guests=6)
        print(f"✅ Guest manager initialized with {self.guest_manager.max_guests} slots")
        return True
    
    def test_guest_invitation_system(self):
        """Test guest invitation creation and validation"""
        print("\nTesting Guest Invitation System...")
        
        # Test 1: Create guest invite
        def test_create_invite():
            result = self.guest_manager.create_guest_invite(
                "John Doe", "john@example.com", GuestRole.GUEST
            )
            self.test_guests['john'] = result
            assert result['guest_id'] is not None
            assert result['invite_code'] is not None
            assert len(result['invite_code']) == 8
            assert result['guest']['name'] == "John Doe"
            return True
        
        self.run_test("Create Guest Invite", test_create_invite, True)
        
        # Test 2: Create moderator invite
        def test_create_moderator_invite():
            result = self.guest_manager.create_guest_invite(
                "Jane Smith", "jane@example.com", GuestRole.MODERATOR
            )
            self.test_guests['jane'] = result
            assert result['guest']['role'] == 'moderator'
            return True
        
        self.run_test("Create Moderator Invite", test_create_moderator_invite, True)
        
        # Test 3: Test invalid invite code
        def test_invalid_invite():
            try:
                self.guest_manager.join_via_invite("INVALID", "127.0.0.1", "TestAgent")
                return False
            except ValueError as e:
                assert "Invalid invite code" in str(e)
                return True
        
        self.run_test("Invalid Invite Code", test_invalid_invite, True)
        
        # Test 4: Test duplicate guest connection
        def test_duplicate_connection():
            guest = self.test_guests['john']
            try:
                # First connection should work
                result1 = self.guest_manager.join_via_invite(guest['invite_code'])
                assert result1['status'] in ['connected', 'waiting_room']
                
                # Second connection should fail
                self.guest_manager.join_via_invite(guest['invite_code'])
                return False
            except ValueError as e:
                assert "already connected" in str(e)
                return True
        
        self.run_test("Duplicate Guest Connection", test_duplicate_connection, True)
    
    def test_slot_management(self):
        """Test 6-slot system functionality"""
        print("\nTesting Slot Management System...")
        
        # Test 1: Fill all slots
        def test_fill_all_slots():
            guests_created = 0
            
            for i in range(1, 7):
                try:
                    result = self.guest_manager.create_guest_invite(
                        f"Guest{i}", f"guest{i}@example.com"
                    )
                    join_result = self.guest_manager.join_via_invite(result['invite_code'])
                    
                    if join_result['status'] == 'connected':
                        guests_created += 1
                        assert join_result['slot_number'] is not None
                        assert 1 <= join_result['slot_number'] <= 6
                except Exception as e:
                    logger.error(f"Failed to create/join guest {i}: {e}")
            
            assert guests_created == 6, f"Expected 6 guests, got {guests_created}"
            
            # Check all slots are occupied
            active_guests = self.guest_manager.get_active_guests()
            assert len(active_guests) == 6
            
            return True
        
        self.run_test("Fill All 6 Slots", test_fill_all_slots, True)
        
        # Test 2: Test available slot detection
        def test_slot_detection():
            slots = [1, 2, 3, 4, 5, 6]
            occupied_slots = []
            
            for guest in self.guest_manager.get_active_guests():
                occupied_slots.append(guest.slot_number)
            
            assert len(occupied_slots) == 6
            assert set(occupied_slots) == set(slots)
            
            # Check no available slots
            available_slot = self.guest_manager._get_available_slot()
            assert available_slot is None
            
            return True
        
        self.run_test("Slot Detection", test_slot_detection, True)
        
        # Test 3: Test 7th guest goes to waiting room
        def test_waiting_room():
            result = self.guest_manager.create_guest_invite(
                "ExtraGuest", "extra@example.com"
            )
            join_result = self.guest_manager.join_via_invite(result['invite_code'])
            
            assert join_result['status'] == 'waiting_room'
            assert len(self.guest_manager.waiting_room) == 1
            
            return True
        
        self.run_test("7th Guest to Waiting Room", test_waiting_room, True)
    
    def test_moderator_controls(self):
        """Test moderator mute, stop camera, kick functions"""
        print("\n👮 Testing Moderator Controls...")
        
        # Get a test guest to moderate
        test_guest = None
        for guest in self.guest_manager.get_active_guests():
            if guest.role == GuestRole.GUEST:
                test_guest = guest
                break
        
        if not test_guest:
            logger.error("No test guest found for moderator tests")
            return
        
        moderator_id = self.test_guests.get('jane', {}).get('guest_id', 'test_moderator')
        
        # Test 1: Mute guest
        def test_mute_guest():
            success = self.guest_manager.moderator_mute_guest(
                test_guest.id, moderator_id
            )
            assert success == True
            
            # Check guest status
            guest = self.guest_manager.guests[test_guest.id]
            assert guest.status == GuestStatus.MUTED
            assert guest.device.microphone_enabled == False
            
            return True
        
        self.run_test("Moderator Mute Guest", test_mute_guest, True)
        
        # Test 2: Stop camera
        def test_stop_camera():
            success = self.guest_manager.moderator_stop_camera(
                test_guest.id, moderator_id
            )
            assert success == True
            
            # Check guest status
            guest = self.guest_manager.guests[test_guest.id]
            assert guest.status == GuestStatus.VIDEO_OFF
            assert guest.device.camera_enabled == False
            
            return True
        
        self.run_test("Moderator Stop Camera", test_stop_camera, True)
        
        # Test 3: Kick guest
        def test_kick_guest():
            original_slot = test_guest.slot_number
            
            success = self.guest_manager.moderator_kick_guest(
                test_guest.id, moderator_id, "Test kick"
            )
            assert success == True
            
            # Check guest status
            guest = self.guest_manager.guests[test_guest.id]
            assert guest.status == GuestStatus.KICKED
            assert guest.slot_number not in self.guest_manager.guest_slots
            
            # Check waiting room admission
            assert len(self.guest_manager.waiting_room) == 0  # Should have been admitted
            
            return True
        
        self.run_test("Moderator Kick Guest", test_kick_guest, True)
    
    def test_waiting_room_management(self):
        """Test waiting room queue management and auto-admission"""
        print("\n🪑 Testing Waiting Room Management...")
        
        # Clear existing guests for clean test
        self.guest_manager.guests.clear()
        self.guest_manager.guest_slots.clear()
        self.guest_manager.waiting_room.clear()
        self.test_guests.clear()
        
        # Fill all slots
        filled_slots = []
        for i in range(6):
            result = self.guest_manager.create_guest_invite(
                f"SlotGuest{i}", f"slot{i}@example.com"
            )
            self.guest_manager.join_via_invite(result['invite_code'])
            filled_slots.append(result['guest_id'])
        
        # Test 1: Add guests to waiting room
        def test_waiting_room_queue():
            waiting_guests = []
            
            for i in range(3):
                result = self.guest_manager.create_guest_invite(
                    f"WaitGuest{i}", f"wait{i}@example.com"
                )
                self.guest_manager.join_via_invite(result['invite_code'])
                waiting_guests.append(result['guest_id'])
            
            assert len(self.guest_manager.waiting_room) == 3
            assert len(waiting_guests) == 3
            
            return True
        
        self.run_test("Waiting Room Queue", test_waiting_room_queue, True)
        
        # Test 2: Test auto-admission
        def test_auto_admission():
            # Kick one guest to free a slot
            active_guests = self.guest_manager.get_active_guests()
            guest_to_kick = active_guests[0]
            
            # Before kick
            waiting_before = len(self.guest_manager.waiting_room)
            
            # Kick guest
            self.guest_manager.moderator_kick_guest(
                guest_to_kick.id, "test_moderator", "Test for auto-admission"
            )
            
            # After kick - should auto-admit from waiting room
            assert len(self.guest_manager.waiting_room) == waiting_before - 1
            
            return True
        
        self.run_test("Auto-Admission from Waiting Room", test_auto_admission, True)
    
    def test_guest_media_controls(self):
        """Test camera/microphone state management"""
        print("\n🎥 Testing Guest Media Controls...")
        
        # Create a test guest
        result = self.guest_manager.create_guest_invite(
            "MediaTest", "media@example.com"
        )
        self.guest_manager.join_via_invite(result['invite_code'])
        guest_id = result['guest_id']
        
        # Test 1: Camera ON
        def test_camera_on():
            success = self.guest_manager.set_guest_media_state(
                guest_id, camera=MediaState.ON
            )
            assert success == True
            
            guest = self.guest_manager.guests[guest_id]
            assert guest.device.camera_enabled == True
            assert guest.status == GuestStatus.ONLINE
            
            return True
        
        self.run_test("Camera ON", test_camera_on, True)
        
        # Test 2: Microphone Muted
        def test_microphone_muted():
            success = self.guest_manager.set_guest_media_state(
                guest_id, microphone=MediaState.MUTED
            )
            assert success == True
            
            guest = self.guest_manager.guests[guest_id]
            assert guest.device.microphone_enabled == False
            assert guest.status == GuestStatus.MUTED
            
            return True
        
        self.run_test("Microphone Muted", test_microphone_muted, True)
        
        # Test 3: Camera OFF
        def test_camera_off():
            success = self.guest_manager.set_guest_media_state(
                guest_id, camera=MediaState.OFF
            )
            assert success == True
            
            guest = self.guest_manager.guests[guest_id]
            assert guest.device.camera_enabled == False
            assert guest.status == GuestStatus.VIDEO_OFF
            
            return True
        
        self.run_test("Camera OFF", test_camera_off, True)
        
        # Test 4: Microphone ON
        def test_microphone_on():
            success = self.guest_manager.set_guest_media_state(
                guest_id, microphone=MediaState.ON
            )
            assert success == True
            
            guest = self.guest_manager.guests[guest_id]
            assert guest.device.microphone_enabled == True
            
            return True
        
        self.run_test("Microphone ON", test_microphone_on, True)
    
    def test_role_based_permissions(self):
        """Test guest, moderator, host roles"""
        print("\n👑 Testing Role-Based Permissions...")
        
        # Create guests with different roles
        roles_to_test = [
            (GuestRole.GUEST, "TestGuest", "guest@example.com"),
            (GuestRole.MODERATOR, "TestModerator", "mod@example.com"),
            (GuestRole.HOST, "TestHost", "host@example.com")
        ]
        
        created_guests = {}
        
        for role, name, email in roles_to_test:
            result = self.guest_manager.create_guest_invite(name, email, role)
            self.guest_manager.join_via_invite(result['invite_code'])
            created_guests[role.value] = self.guest_manager.guests[result['guest_id']]
        
        # Test 1: Role assignment
        def test_role_assignment():
            for role_value, guest in created_guests.items():
                assert guest.role.value == role_value
                assert guest.role in [GuestRole.GUEST, GuestRole.MODERATOR, GuestRole.HOST]
            
            return True
        
        self.run_test("Role Assignment", test_role_assignment, True)
        
        # Test 2: Default permissions
        def test_default_permissions():
            guest_guest = created_guests['guest']
            moderator = created_guests['moderator']
            host = created_guests['host']
            
            # Regular guest should not have moderation powers
            assert guest_guest.permissions.can_moderate == False
            assert guest_guest.permissions.can_invite == False
            assert guest_guest.permissions.can_record == False
            
            # Moderator should have more permissions
            assert moderator.permissions.can_moderate == True
            assert moderator.permissions.can_invite == True
            
            # Host should have all permissions
            assert host.permissions.can_moderate == True
            assert host.permissions.can_invite == True
            assert host.permissions.can_record == True
            
            return True
        
        self.run_test("Default Permissions", test_default_permissions, True)
    
    def test_guest_status_tracking(self):
        """Test status transitions and updates"""
        print("\n📊 Testing Guest Status Tracking...")
        
        # Create test guest
        result = self.guest_manager.create_guest_invite(
            "StatusTest", "status@example.com"
        )
        guest_id = result['guest_id']
        
        # Test 1: Initial status
        def test_initial_status():
            guest = self.guest_manager.guests[guest_id]
            assert guest.status == GuestStatus.OFFLINE
            assert guest.join_time is None
            assert guest.last_active is not None  # Should be set on creation
            
            return True
        
        self.run_test("Initial Status", test_initial_status, True)
        
        # Test 2: Join transition
        def test_join_transition():
            self.guest_manager.join_via_invite(result['invite_code'])
            guest = self.guest_manager.guests[guest_id]
            
            assert guest.status in [GuestStatus.CONNECTING, GuestStatus.ONLINE]
            assert guest.join_time is not None
            
            return True
        
        self.run_test("Join Status Transition", test_join_transition, True)
        
        # Test 3: Media state transitions
        def test_media_transitions():
            # Camera off
            self.guest_manager.set_guest_media_state(guest_id, camera=MediaState.OFF)
            guest = self.guest_manager.guests[guest_id]
            assert guest.status == GuestStatus.VIDEO_OFF
            
            # Microphone muted
            self.guest_manager.set_guest_media_state(guest_id, microphone=MediaState.MUTED)
            guest = self.guest_manager.guests[guest_id]
            assert guest.status == GuestStatus.MUTED
            
            return True
        
        self.run_test("Media State Transitions", test_media_transitions, True)
    
    def test_advanced_features(self):
        """Test hand raise/lower, pin/unpin functionality"""
        print("\n✋ Testing Advanced Features...")
        
        # Create test guest
        result = self.guest_manager.create_guest_invite(
            "AdvancedTest", "advanced@example.com"
        )
        self.guest_manager.join_via_invite(result['invite_code'])
        guest_id = result['guest_id']
        moderator_id = "test_moderator"
        
        # Test 1: Hand raise
        def test_hand_raise():
            success = self.guest_manager.raise_hand(guest_id)
            assert success == True
            
            guest = self.guest_manager.guests[guest_id]
            assert guest.is_hand_raised == True
            
            return True
        
        self.run_test("Hand Raise", test_hand_raise, True)
        
        # Test 2: Hand lower
        def test_hand_lower():
            success = self.guest_manager.lower_hand(guest_id)
            assert success == True
            
            guest = self.guest_manager.guests[guest_id]
            assert guest.is_hand_raised == False
            
            return True
        
        self.run_test("Hand Lower", test_hand_lower, True)
        
        # Test 3: Pin guest
        def test_pin_guest():
            success = self.guest_manager.pin_guest(guest_id, moderator_id)
            assert success == True
            
            guest = self.guest_manager.guests[guest_id]
            assert guest.is_pinned == True
            
            return True
        
        self.run_test("Pin Guest", test_pin_guest, True)
    
    def test_device_configuration(self):
        """Test device configuration updates"""
        print("\n⚙️ Testing Device Configuration...")
        
        # Create test guest
        result = self.guest_manager.create_guest_invite(
            "DeviceTest", "device@example.com"
        )
        self.guest_manager.join_via_invite(result['invite_code'])
        guest_id = result['guest_id']
        
        # Test 1: Update video quality
        def test_video_quality():
            config = {
                'video_quality': '1080p',
                'audio_quality': 'high',
                'background_blur': True,
                'virtual_background': 'matrix.jpg',
                'camera_device': 'HD Pro Webcam',
                'microphone_device': 'Blue Yeti'
            }
            
            success = self.guest_manager.update_guest_device_config(guest_id, config)
            assert success == True
            
            guest = self.guest_manager.guests[guest_id]
            assert guest.device.video_quality == '1080p'
            assert guest.device.audio_quality == 'high'
            assert guest.device.background_blur == True
            assert guest.device.virtual_background == 'matrix.jpg'
            assert guest.device.camera_device == 'HD Pro Webcam'
            assert guest.device.microphone_device == 'Blue Yeti'
            
            return True
        
        self.run_test("Device Configuration Update", test_video_quality, True)
    
    def test_studio_status_reporting(self):
        """Test studio status and reporting functions"""
        print("\n📈 Testing Studio Status Reporting...")
        
        # Ensure we have some guests for testing
        status = self.guest_manager.get_studio_status()
        
        # Test 1: Status structure
        def test_status_structure():
            required_fields = [
                'total_slots', 'occupied_slots', 'available_slots',
                'waiting_room_count', 'guests_in_studio', 'waiting_room',
                'moderator_controls', 'slot_layout'
            ]
            
            for field in required_fields:
                assert field in status
            
            assert status['total_slots'] == 6
            assert status['occupied_slots'] >= 0
            assert status['available_slots'] >= 0
            assert status['occupied_slots'] + status['available_slots'] == 6
            
            return True
        
        self.run_test("Status Structure", test_status_structure, True)
        
        # Test 2: Slot layout
        def test_slot_layout():
            layout = status['slot_layout']
            
            # Should have 6 slots
            assert len(layout) == 6
            
            for slot_key, slot_data in layout.items():
                assert slot_key.startswith('slot_')
                assert slot_data is None or isinstance(slot_data, dict)
            
            return True
        
        self.run_test("Slot Layout", test_slot_layout, True)
        
        # Test 3: Export functionality
        def test_export_function():
            export_data = self.guest_manager.export_guest_list()
            
            required_fields = [
                'total_guests', 'active_guests', 'waiting_guests',
                'guests', 'export_time'
            ]
            
            for field in required_fields:
                assert field in export_data
            
            assert isinstance(export_data['guests'], list)
            assert export_data['export_time'] is not None
            
            return True
        
        self.run_test("Export Function", test_export_function, True)
    
    def test_security_considerations(self):
        """Test security aspects of guest management"""
        print("\n🔒 Testing Security Considerations...")
        
        # Test 1: Invalid guest ID handling
        def test_invalid_guest_id():
            # Try to moderate non-existent guest
            success = self.guest_manager.moderator_mute_guest("invalid_id", "moderator")
            assert success == False
            
            success = self.guest_manager.raise_hand("invalid_id")
            assert success == False
            
            return True
        
        self.run_test("Invalid Guest ID Handling", test_invalid_guest_id, True)
        
        # Test 2: Role validation
        def test_role_validation():
            try:
                # Try to create invite with invalid role
                self.guest_manager.create_guest_invite("Test", "test@example.com", "invalid_role")
                return False
            except (ValueError, AttributeError):
                return True
        
        self.run_test("Role Validation", test_role_validation, True)
        
        # Test 3: Media state validation
        def test_media_state_validation():
            guest_id = list(self.guest_manager.guests.keys())[0] if self.guest_manager.guests else None
            
            if not guest_id:
                return True  # Skip if no guests
            
            # Invalid media states should be handled gracefully
            success = self.guest_manager.set_guest_media_state("invalid_id")
            assert success == False
            
            return True
        
        self.run_test("Media State Validation", test_media_state_validation, True)
    
    def generate_performance_report(self):
        """Generate performance metrics report"""
        print("\n⚡ Performance Analysis...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == '✅ PASS')
        failed_tests = total_tests - passed_tests
        
        total_execution_time = sum(r['execution_time'] for r in self.test_results)
        avg_execution_time = total_execution_time / total_tests if total_tests > 0 else 0
        
        slow_tests = sorted(
            [r for r in self.test_results if r['execution_time'] > 0.1],
            key=lambda x: x['execution_time'],
            reverse=True
        )[:5]
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Execution Time: {total_execution_time:.3f}s")
        print(f"Average Test Time: {avg_execution_time:.3f}s")
        
        if slow_tests:
            print("\nSlowest Tests:")
            for test in slow_tests:
                print(f"  - {test['test_name']}: {test['execution_time']:.3f}s")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100 if total_tests > 0 else 0,
            'total_execution_time': total_execution_time,
            'avg_execution_time': avg_execution_time
        }
    
    def generate_final_assessment(self):
        """Generate final system assessment"""
        print("\n🎯 FINAL ASSESSMENT")
        print("=" * 60)
        
        if not GUEST_MANAGEMENT_AVAILABLE:
            print("❌ CRITICAL: Guest management module not available")
            print("   - Cannot assess system without core functionality")
            return {
                'reliability_score': 0,
                'critical_issues': ['Guest management module not available'],
                'recommendations': ['Fix module imports and dependencies'],
                'production_ready': False
            }
        
        performance = self.generate_performance_report()
        
        # Analyze failed tests
        failed_tests = [r for r in self.test_results if r['status'] == '❌ FAIL']
        critical_issues = []
        recommendations = []
        
        if failed_tests:
            print(f"\n❌ Failed Tests Analysis ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['error_message']}")
                
                # Categorize issues
                if 'import' in test['error_message'].lower():
                    critical_issues.append(f"Module import issue: {test['test_name']}")
                elif 'permission' in test['test_name'].lower():
                    recommendations.append("Review and fix permission system")
                elif 'slot' in test['test_name'].lower():
                    recommendations.append("Investigate slot management logic")
                else:
                    recommendations.append(f"Fix {test['test_name']} functionality")
        
        # Calculate reliability score
        base_score = performance['success_rate']
        
        # Deduct points for critical issues
        if critical_issues:
            base_score -= len(critical_issues) * 10
        
        # Consider performance
        if performance['avg_execution_time'] > 0.5:
            base_score -= 10  # Performance penalty
        
        reliability_score = max(0, min(100, base_score))
        
        # Determine production readiness
        production_ready = (
            reliability_score >= 80 and
            len(critical_issues) == 0 and
            performance['success_rate'] >= 95
        )
        
        # Add standard recommendations
        if not production_ready:
            if reliability_score < 50:
                recommendations.insert(0, "Major system overhaul required")
            elif reliability_score < 80:
                recommendations.insert(0, "Significant improvements needed")
            else:
                recommendations.insert(0, "Minor fixes before production")
        
        recommendations.extend([
            "Add comprehensive logging for debugging",
            "Implement automated testing in CI/CD pipeline",
            "Add load testing for high-concurrency scenarios",
            "Review and strengthen security measures"
        ])
        
        print(f"\n📊 System Reliability Score: {reliability_score:.1f}/100")
        
        if critical_issues:
            print(f"\n🚨 Critical Issues ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"  - {issue}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations[:10], 1):  # Top 10
            print(f"  {i}. {rec}")
        
        print(f"\n🏭 Production Ready: {'✅ YES' if production_ready else '❌ NO'}")
        
        if production_ready:
            print("   ✅ System meets production standards")
            print("   ✅ High reliability score")
            print("   ✅ No critical issues")
        else:
            print("   ❌ System requires improvements before production")
            print(f"   ❌ Reliability score below 80% ({reliability_score:.1f}%)")
            if critical_issues:
                print(f"   ❌ {len(critical_issues)} critical issues found")
        
        return {
            'reliability_score': reliability_score,
            'critical_issues': critical_issues,
            'recommendations': recommendations,
            'production_ready': production_ready,
            'performance_metrics': performance
        }

def main():
    """Main test execution"""
    print("MATRIX BROADCAST STUDIO - GUEST MANAGEMENT TEST SUITE")
    print("=" * 60)
    print("Comprehensive testing of all guest management functionality")
    print()
    
    tester = GuestManagementTester()
    
    # Setup test environment
    if not tester.setup_test_environment():
        print("❌ Test setup failed - aborting tests")
        return
    
    # Run all test suites
    test_suites = [
        tester.test_guest_invitation_system,
        tester.test_slot_management,
        tester.test_moderator_controls,
        tester.test_waiting_room_management,
        tester.test_guest_media_controls,
        tester.test_role_based_permissions,
        tester.test_guest_status_tracking,
        tester.test_advanced_features,
        tester.test_device_configuration,
        tester.test_studio_status_reporting,
        tester.test_security_considerations
    ]
    
    for test_suite in test_suites:
        try:
            test_suite()
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
    
    # Generate final assessment
    assessment = tester.generate_final_assessment()
    
    # Save detailed report
    report_file = "guest_management_test_report.json"
    try:
        with open(report_file, 'w') as f:
            json.dump({
                'test_results': tester.test_results,
                'assessment': assessment,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()