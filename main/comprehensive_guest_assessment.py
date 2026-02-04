#!/usr/bin/env python3
"""
DETAILED GUEST MANAGEMENT ASSESSMENT
Comprehensive testing and analysis of Matrix Broadcast Studio guest functionality
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_guest_scenarios():
    """Test all guest management scenarios comprehensively"""
    print("=" * 80)
    print("COMPREHENSIVE GUEST MANAGEMENT ASSESSMENT")
    print("Matrix Broadcast Studio - Guest Functionality Testing")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        from guest_management import GuestManager, GuestRole, GuestStatus, MediaState
        print("[SUCCESS] Guest management module imported successfully")
    except ImportError as e:
        print(f"[CRITICAL] Cannot import guest_management: {e}")
        return False
    
    test_results = []
    performance_metrics = {}
    
    # Initialize test environment
    print("\n1. INITIALIZATION TESTS")
    print("-" * 40)
    
    start_time = time.time()
    try:
        manager = GuestManager(max_guests=6)
        init_time = time.time() - start_time
        
        assert manager.max_guests == 6
        assert len(manager.guests) == 0
        assert len(manager.guest_slots) == 0
        assert len(manager.waiting_room) == 0
        
        test_results.append({
            'test': 'Guest Manager Initialization',
            'status': 'PASS',
            'time': init_time,
            'details': f'Initialized with {manager.max_guests} slots'
        })
        performance_metrics['initialization'] = init_time
        print(f"[PASS] Guest Manager initialized in {init_time:.4f}s")
        
    except Exception as e:
        test_results.append({
            'test': 'Guest Manager Initialization',
            'status': 'FAIL',
            'error': str(e)
        })
        print(f"[FAIL] Initialization failed: {e}")
        return False
    
    # Test 2: Guest Invitation System
    print("\n2. GUEST INVITATION SYSTEM TESTS")
    print("-" * 40)
    
    invitation_tests = [
        ('Create Regular Guest', GuestRole.GUEST, "Regular User", "regular@example.com"),
        ('Create Moderator', GuestRole.MODERATOR, "Moderator User", "mod@example.com"),
        ('Create Host', GuestRole.HOST, "Host User", "host@example.com"),
    ]
    
    created_guests = {}
    
    for test_name, role, name, email in invitation_tests:
        start_time = time.time()
        try:
            result = manager.create_guest_invite(name, email, role)
            invite_time = time.time() - start_time
            
            assert 'guest_id' in result
            assert 'invite_code' in result
            assert len(result['invite_code']) == 8
            assert result['guest']['name'] == name
            assert result['guest']['email'] == email
            assert result['guest']['role'] == role.value
            
            created_guests[test_name] = result
            
            test_results.append({
                'test': test_name,
                'status': 'PASS',
                'time': invite_time,
                'details': f'Created {role.value} with code {result["invite_code"]}'
            })
            print(f"[PASS] {test_name}: {role.value} - Code: {result['invite_code']}")
            
        except Exception as e:
            test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'error': str(e)
            })
            print(f"[FAIL] {test_name}: {e}")
    
    # Test 3: Guest Join Validation
    print("\n3. GUEST JOIN VALIDATION TESTS")
    print("-" * 40)
    
    join_tests = [
        ('Valid Guest Join', created_guests.get('Create Regular Guest')),
        ('Invalid Invite Code', 'INVALID_CODE'),
        ('Duplicate Guest Join', created_guests.get('Create Regular Guest')),
    ]
    
    for test_name, guest_data in join_tests:
        start_time = time.time()
        try:
            if test_name == 'Invalid Invite Code':
                manager.join_via_invite('INVALID_CODE', '127.0.0.1', 'TestAgent')
                success = False
            else:
                result = manager.join_via_invite(
                    guest_data['invite_code'], 
                    '127.0.0.1', 
                    'TestAgent'
                )
                success = 'status' in result
                join_time = time.time() - start_time
                
                test_results.append({
                    'test': test_name,
                    'status': 'PASS' if success else 'FAIL',
                    'time': join_time,
                    'details': f"Status: {result.get('status', 'Unknown')}"
                })
                print(f"[PASS] {test_name}: {result.get('status', 'Unknown')}")
                continue
            
        except ValueError as e:
            if 'Invalid invite code' in str(e) or 'already connected' in str(e):
                test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'time': time.time() - start_time,
                    'details': f'Correctly rejected: {e}'
                })
                print(f"[PASS] {test_name}: Correctly rejected - {e}")
            else:
                test_results.append({
                    'test': test_name,
                    'status': 'FAIL',
                    'error': str(e)
                })
                print(f"[FAIL] {test_name}: {e}")
        except Exception as e:
            test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'error': str(e)
            })
            print(f"[FAIL] {test_name}: {e}")
    
    # Test 4: Slot Management System
    print("\n4. SLOT MANAGEMENT SYSTEM TESTS")
    print("-" * 40)
    
    # Fill all 6 slots
    slot_fill_time = 0
    filled_slots = []
    
    for i in range(6):
        start_time = time.time()
        try:
            result = manager.create_guest_invite(
                f"SlotGuest{i}", f"slot{i}@example.com"
            )
            join_result = manager.join_via_invite(result['invite_code'])
            
            if join_result['status'] == 'connected':
                filled_slots.append({
                    'guest_id': result['guest_id'],
                    'slot_number': join_result['slot_number']
                })
                slot_fill_time += time.time() - start_time
                print(f"[PASS] Slot {join_result['slot_number']}: SlotGuest{i}")
            else:
                print(f"[INFO] SlotGuest{i} in waiting room")
                
        except Exception as e:
            print(f"[FAIL] Failed to fill slot {i}: {e}")
    
    test_results.append({
        'test': 'Fill 6 Slots',
        'status': 'PASS' if len(filled_slots) == 6 else 'PARTIAL',
        'time': slot_fill_time,
        'details': f'Filled {len(filled_slots)}/6 slots'
    })
    
    # Test 7th guest
    start_time = time.time()
    try:
        result = manager.create_guest_invite("ExtraGuest", "extra@example.com")
        join_result = manager.join_via_invite(result['invite_code'])
        
        if join_result['status'] == 'waiting_room':
            test_results.append({
                'test': '7th Guest to Waiting Room',
                'status': 'PASS',
                'time': time.time() - start_time,
                'details': 'Correctly placed in waiting room'
            })
            print("[PASS] 7th guest correctly placed in waiting room")
        else:
            test_results.append({
                'test': '7th Guest to Waiting Room',
                'status': 'FAIL',
                'time': time.time() - start_time,
                'details': f"Unexpected status: {join_result['status']}"
            })
            print(f"[FAIL] 7th guest status: {join_result['status']}")
            
    except Exception as e:
        test_results.append({
            'test': '7th Guest to Waiting Room',
            'status': 'FAIL',
            'error': str(e)
        })
        print(f"[FAIL] 7th guest test: {e}")
    
    # Test 5: Moderator Controls
    print("\n5. MODERATOR CONTROLS TESTS")
    print("-" * 40)
    
    active_guests = manager.get_active_guests()
    if active_guests:
        test_guest = active_guests[0]
        moderator_id = list(created_guests.get('Create Moderator', {}).values())[0] if 'Create Moderator' in created_guests else 'test_mod'
        
        moderator_tests = [
            ('Mute Guest', lambda: manager.moderator_mute_guest(test_guest.id, moderator_id)),
            ('Stop Camera', lambda: manager.moderator_stop_camera(test_guest.id, moderator_id)),
            ('Kick Guest', lambda: manager.moderator_kick_guest(test_guest.id, moderator_id, "Test kick")),
        ]
        
        for test_name, test_func in moderator_tests:
            start_time = time.time()
            try:
                result = test_func()
                execution_time = time.time() - start_time
                
                if result == True:
                    test_results.append({
                        'test': test_name,
                        'status': 'PASS',
                        'time': execution_time,
                        'details': f'Successfully executed on guest {test_guest.name}'
                    })
                    print(f"[PASS] {test_name}: Success")
                else:
                    test_results.append({
                        'test': test_name,
                        'status': 'FAIL',
                        'time': execution_time,
                        'details': 'Function returned False'
                    })
                    print(f"[FAIL] {test_name}: Function returned False")
                    
            except Exception as e:
                test_results.append({
                    'test': test_name,
                    'status': 'FAIL',
                    'error': str(e)
                })
                print(f"[FAIL] {test_name}: {e}")
    
    # Test 6: Media State Management
    print("\n6. MEDIA STATE MANAGEMENT TESTS")
    print("-" * 40)
    
    # Create fresh guest for media testing
    try:
        result = manager.create_guest_invite("MediaTest", "media@example.com")
        join_result = manager.join_via_invite(result['invite_code'])
        
        if join_result['status'] == 'connected':
            media_guest_id = result['guest_id']
            
            media_tests = [
                ('Camera ON', lambda: manager.set_guest_media_state(media_guest_id, camera=MediaState.ON)),
                ('Camera OFF', lambda: manager.set_guest_media_state(media_guest_id, camera=MediaState.OFF)),
                ('Microphone ON', lambda: manager.set_guest_media_state(media_guest_id, microphone=MediaState.ON)),
                ('Microphone Muted', lambda: manager.set_guest_media_state(media_guest_id, microphone=MediaState.MUTED)),
            ]
            
            for test_name, test_func in media_tests:
                start_time = time.time()
                try:
                    result = test_func()
                    execution_time = time.time() - start_time
                    
                    if result == True:
                        test_results.append({
                            'test': test_name,
                            'status': 'PASS',
                            'time': execution_time,
                            'details': 'Media state updated successfully'
                        })
                        print(f"[PASS] {test_name}: Success")
                    else:
                        test_results.append({
                            'test': test_name,
                            'status': 'FAIL',
                            'time': execution_time,
                            'details': 'Function returned False'
                        })
                        print(f"[FAIL] {test_name}: Function returned False")
                        
                except Exception as e:
                    test_results.append({
                        'test': test_name,
                        'status': 'FAIL',
                        'error': str(e)
                    })
                    print(f"[FAIL] {test_name}: {e}")
                    
    except Exception as e:
        print(f"[FAIL] Media test setup failed: {e}")
    
    # Test 7: Advanced Features
    print("\n7. ADVANCED FEATURES TESTS")
    print("-" * 40)
    
    active_guests = manager.get_active_guests()
    if active_guests:
        test_guest = active_guests[0]
        
        advanced_tests = [
            ('Hand Raise', lambda: manager.raise_hand(test_guest.id)),
            ('Hand Lower', lambda: manager.lower_hand(test_guest.id)),
            ('Pin Guest', lambda: manager.pin_guest(test_guest.id, 'test_moderator')),
        ]
        
        for test_name, test_func in advanced_tests:
            start_time = time.time()
            try:
                result = test_func()
                execution_time = time.time() - start_time
                
                if result == True:
                    test_results.append({
                        'test': test_name,
                        'status': 'PASS',
                        'time': execution_time,
                        'details': 'Feature executed successfully'
                    })
                    print(f"[PASS] {test_name}: Success")
                else:
                    test_results.append({
                        'test': test_name,
                        'status': 'FAIL',
                        'time': execution_time,
                        'details': 'Function returned False'
                    })
                    print(f"[FAIL] {test_name}: Function returned False")
                    
            except Exception as e:
                test_results.append({
                    'test': test_name,
                    'status': 'FAIL',
                    'error': str(e)
                })
                print(f"[FAIL] {test_name}: {e}")
    
    # Test 8: Device Configuration
    print("\n8. DEVICE CONFIGURATION TESTS")
    print("-" * 40)
    
    active_guests = manager.get_active_guests()
    if active_guests:
        test_guest = active_guests[0]
        
        start_time = time.time()
        try:
            config = {
                'video_quality': '1080p',
                'audio_quality': 'high',
                'background_blur': True,
                'virtual_background': 'matrix.jpg',
                'camera_device': 'HD Pro Webcam',
                'microphone_device': 'Blue Yeti'
            }
            
            result = manager.update_guest_device_config(test_guest.id, config)
            execution_time = time.time() - start_time
            
            if result == True:
                test_results.append({
                    'test': 'Device Configuration',
                    'status': 'PASS',
                    'time': execution_time,
                    'details': 'Device configuration updated successfully'
                })
                print("[PASS] Device Configuration: Success")
            else:
                test_results.append({
                    'test': 'Device Configuration',
                    'status': 'FAIL',
                    'time': execution_time,
                    'details': 'Function returned False'
                })
                print("[FAIL] Device Configuration: Function returned False")
                
        except Exception as e:
            test_results.append({
                'test': 'Device Configuration',
                'status': 'FAIL',
                'error': str(e)
            })
            print(f"[FAIL] Device Configuration: {e}")
    
    # Test 9: Studio Status Reporting
    print("\n9. STUDIO STATUS REPORTING TESTS")
    print("-" * 40)
    
    start_time = time.time()
    try:
        status = manager.get_studio_status()
        status_time = time.time() - start_time
        
        required_fields = [
            'total_slots', 'occupied_slots', 'available_slots',
            'waiting_room_count', 'guests_in_studio', 'slot_layout'
        ]
        
        missing_fields = [field for field in required_fields if field not in status]
        
        if not missing_fields:
            test_results.append({
                'test': 'Studio Status Reporting',
                'status': 'PASS',
                'time': status_time,
                'details': f'Status: {status["occupied_slots"]}/{status["total_slots"]} slots occupied'
            })
            print(f"[PASS] Studio Status: {status['occupied_slots']}/{status['total_slots']} slots occupied")
        else:
            test_results.append({
                'test': 'Studio Status Reporting',
                'status': 'FAIL',
                'time': status_time,
                'error': f'Missing fields: {missing_fields}'
            })
            print(f"[FAIL] Studio Status: Missing fields {missing_fields}")
            
    except Exception as e:
        test_results.append({
            'test': 'Studio Status Reporting',
            'status': 'FAIL',
            'error': str(e)
        })
        print(f"[FAIL] Studio Status: {e}")
    
    # Test 10: Export Functionality
    print("\n10. EXPORT FUNCTIONALITY TESTS")
    print("-" * 40)
    
    start_time = time.time()
    try:
        export_data = manager.export_guest_list()
        export_time = time.time() - start_time
        
        required_fields = ['total_guests', 'active_guests', 'waiting_guests', 'guests', 'export_time']
        missing_fields = [field for field in required_fields if field not in export_data]
        
        if not missing_fields:
            test_results.append({
                'test': 'Export Functionality',
                'status': 'PASS',
                'time': export_time,
                'details': f'Exported {export_data["total_guests"]} guests'
            })
            print(f"[PASS] Export: {export_data['total_guests']} total guests")
        else:
            test_results.append({
                'test': 'Export Functionality',
                'status': 'FAIL',
                'time': export_time,
                'error': f'Missing fields: {missing_fields}'
            })
            print(f"[FAIL] Export: Missing fields {missing_fields}")
            
    except Exception as e:
        test_results.append({
            'test': 'Export Functionality',
            'status': 'FAIL',
            'error': str(e)
        })
        print(f"[FAIL] Export: {e}")
    
    # Test 11: Security Considerations
    print("\n11. SECURITY CONSIDERATIONS TESTS")
    print("-" * 40)
    
    security_tests = [
        ('Invalid Guest ID - Mute', lambda: manager.moderator_mute_guest("invalid_id", "moderator")),
        ('Invalid Guest ID - Hand Raise', lambda: manager.raise_hand("invalid_id")),
        ('Invalid Guest ID - Media State', lambda: manager.set_guest_media_state("invalid_id", camera=MediaState.ON)),
    ]
    
    for test_name, test_func in security_tests:
        start_time = time.time()
        try:
            result = test_func()
            execution_time = time.time() - start_time
            
            if result == False:  # Should return False for invalid IDs
                test_results.append({
                    'test': test_name,
                    'status': 'PASS',
                    'time': execution_time,
                    'details': 'Correctly rejected invalid guest ID'
                })
                print(f"[PASS] {test_name}: Correctly rejected")
            else:
                test_results.append({
                    'test': test_name,
                    'status': 'FAIL',
                    'time': execution_time,
                    'details': 'Should have returned False'
                })
                print(f"[FAIL] {test_name}: Should have returned False")
                
        except Exception as e:
            test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'error': str(e)
            })
            print(f"[FAIL] {test_name}: {e}")
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST RESULTS ANALYSIS")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r['status'] == 'PASS')
    failed_tests = sum(1 for r in test_results if r['status'] == 'FAIL')
    partial_tests = sum(1 for r in test_results if r['status'] == 'PARTIAL')
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    total_execution_time = sum(r.get('time', 0) for r in test_results)
    avg_execution_time = total_execution_time / total_tests if total_tests > 0 else 0
    
    print(f"Total Tests Executed: {total_tests}")
    print(f"Passed: {passed_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    print(f"Failed: {failed_tests} ({(failed_tests/total_tests)*100:.1f}%)")
    print(f"Partial: {partial_tests} ({(partial_tests/total_tests)*100:.1f}%)")
    print(f"Overall Success Rate: {success_rate:.1f}%")
    print(f"Total Execution Time: {total_execution_time:.4f}s")
    print(f"Average Test Time: {avg_execution_time:.4f}s")
    
    # Failed tests analysis
    if failed_tests > 0:
        print(f"\n[CRITICAL ISSUES] - {failed_tests} Failed Tests:")
        for result in test_results:
            if result['status'] == 'FAIL':
                print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
    
    # Performance analysis
    print(f"\n[PERFORMANCE ANALYSIS]")
    slowest_tests = sorted(
        [r for r in test_results if 'time' in r and r['time'] > 0],
        key=lambda x: x['time'],
        reverse=True
    )[:5]
    
    if slowest_tests:
        print("Slowest Tests:")
        for test in slowest_tests:
            print(f"  - {test['test']}: {test['time']:.4f}s")
    
    # System Reliability Assessment
    reliability_score = success_rate
    
    # Deductions for critical failures
    critical_failures = [r for r in test_results if r['status'] == 'FAIL' and 
                       any(keyword in r.get('test', '').lower() for keyword in 
                           ['initialization', 'invitation', 'join', 'slot'])]
    
    if critical_failures:
        reliability_score -= len(critical_failures) * 5
    
    # Performance considerations
    if avg_execution_time > 0.1:  # If average test time is > 100ms
        reliability_score -= 5
    
    reliability_score = max(0, min(100, reliability_score))
    
    print(f"\n[SYSTEM RELIABILITY SCORE: {reliability_score:.1f}/100]")
    
    # Production readiness assessment
    production_ready = (
        reliability_score >= 85 and
        failed_tests == 0 and
        success_rate >= 95
    )
    
    if production_ready:
        print("[PRODUCTION READY: YES]")
        print("  [PASS] High reliability score")
        print("  [PASS] No critical failures")
        print("  [PASS] Excellent success rate")
    else:
        print("[PRODUCTION READY: NO]")
        if reliability_score < 50:
            print("  [FAIL] Major system overhaul required")
        elif reliability_score < 75:
            print("  [FAIL] Significant improvements needed")
        else:
            print("  [WARN] Minor fixes before production")
        
        if failed_tests > 0:
            print(f"  [FAIL] {failed_tests} test failures to address")
        if success_rate < 95:
            print("  [WARN] Success rate below 95%")
    
    # Recommendations
    recommendations = []
    
    if failed_tests > 0:
        recommendations.append("Fix all failed tests before production deployment")
    
    if critical_failures:
        recommendations.append("Address critical functionality failures immediately")
    
    if avg_execution_time > 0.05:
        recommendations.append("Optimize performance for faster response times")
    
    if reliability_score < 90:
        recommendations.append("Improve error handling and edge case management")
    
    recommendations.extend([
        "Add comprehensive logging for production monitoring",
        "Implement automated testing in CI/CD pipeline",
        "Add load testing for high-concurrency scenarios",
        "Review and strengthen security measures",
        "Add detailed documentation for API endpoints",
        "Implement rate limiting for guest join attempts"
    ])
    
    print(f"\n[RECOMMENDATIONS]")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Save detailed report
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'test_summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'partial_tests': partial_tests,
            'success_rate': success_rate,
            'total_execution_time': total_execution_time,
            'avg_execution_time': avg_execution_time
        },
        'reliability_assessment': {
            'reliability_score': reliability_score,
            'production_ready': production_ready,
            'critical_failures': len(critical_failures)
        },
        'detailed_results': test_results,
        'recommendations': recommendations,
        'performance_metrics': performance_metrics
    }
    
    try:
        with open('comprehensive_guest_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"\n[DETAILED REPORT SAVED TO: comprehensive_guest_test_report.json]")
    except Exception as e:
        print(f"\n[ERROR] Failed to save report: {e}")
    
    print("\n" + "=" * 80)
    print("ASSESSMENT COMPLETE")
    print("=" * 80)
    
    return production_ready

if __name__ == "__main__":
    success = test_all_guest_scenarios()
    sys.exit(0 if success else 1)