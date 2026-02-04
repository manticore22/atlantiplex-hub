"""
ATLANTIPLEX STUDIO - COMPREHENSIVE DEBUG & REFINEMENT SUITE
"""

import requests
import json
import time
import random
from datetime import datetime

class AtlantiplexDebugger:
    def __init__(self, base_url="http://127.0.0.1:63859"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def log(self, message, level="DEBUG"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def test_connectivity(self):
        """Test server connectivity"""
        self.log("Testing server connectivity...")
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log(f"[OK] Server connected: {data['status']}")
                self.log(f"[OK] Version: {data['version']}")
                return True
            else:
                self.log(f"[ERROR] Health check failed: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.ConnectionError:
            self.log("[ERROR] Server not responding", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Connection error: {e}", "ERROR")
            return False
    
    def test_database_systems(self):
        """Test all database systems"""
        self.log("Testing database systems...")
        
        tests = [
            ("/test/database", "Database Connection"),
            ("/test/session", "Session Management"),
            ("/test/azure", "Azure Integration"),
            ("/test/full", "Full System Scan")
        ]
        
        results = {}
        
        for endpoint, name in tests:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results[name] = data.get('success', False)
                    status = "[OK]" if data.get('success', False) else "[ERROR]"
                    self.log(f"{status} {name}: {data.get('message', 'No message')}")
                else:
                    results[name] = False
                    self.log(f"[ERROR] {name}: HTTP {response.status_code}", "ERROR")
            except Exception as e:
                results[name] = False
                self.log(f"[ERROR] {name}: Exception - {e}", "ERROR")
        
        return results
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        self.log("Testing API endpoints...")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                self.log("[OK] Health API operational")
                self.log(f"  Features: {len(data['features'])} loaded")
                self.log(f"  Components: {len(data['components'])} active")
            else:
                self.log("[ERROR] Health API failed", "ERROR")
        except Exception as e:
            self.log(f"✗ Health API error: {e}", "ERROR")
    
    def test_login_functionality(self):
        """Test login functionality"""
        self.log("Testing login functionality...")
        
        # Get login page
        try:
            response = self.session.get(f"{self.base_url}/login")
            if response.status_code == 200:
                self.log("[OK] Login page accessible")
            else:
                self.log("[ERROR] Login page failed", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ Login page error: {e}", "ERROR")
            return False
        
        # Test login with correct credentials
        login_data = {
            'username': 'manticore',
            'password': 'patriot8812'
        }
        
        try:
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            if response.status_code == 302:  # Redirect to dashboard
                self.log("[OK] Login successful with correct credentials")
                return True
            else:
                self.log("[ERROR] Login failed", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ Login error: {e}", "ERROR")
            return False
    
    def test_streaming_apis(self):
        """Test streaming API endpoints"""
        self.log("Testing streaming APIs...")
        
        # Test stream status
        try:
            response = self.session.get(f"{self.base_url}/api/stream/status")
            if response.status_code == 200:
                data = response.json()
                self.log("✓ Stream status API working")
                self.log(f"  Active streams: {data.get('total_active', 0)}")
            else:
                self.log("✗ Stream status API failed", "ERROR")
        except Exception as e:
            self.log(f"✗ Stream status error: {e}", "ERROR")
    
    def test_guest_system(self):
        """Test guest management system"""
        self.log("Testing guest management...")
        
        # Test guest list
        try:
            response = self.session.get(f"{self.base_url}/api/guests")
            if response.status_code == 200:
                data = response.json()
                self.log("✓ Guest list API working")
                self.log(f"  Total guests: {len(data.get('guests', []))}")
            elif response.status_code == 302:  # Need to login first
                self.log("⚠ Guest API requires authentication")
            else:
                self.log("✗ Guest list API failed", "ERROR")
        except Exception as e:
            self.log(f"✗ Guest API error: {e}", "ERROR")
    
    def stress_test(self, iterations=10):
        """Stress test the server"""
        self.log(f"Running stress test ({iterations} iterations)...")
        
        success_count = 0
        error_count = 0
        
        for i in range(iterations):
            try:
                response = self.session.get(f"{self.base_url}/api/health", timeout=2)
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except:
                error_count += 1
            
            # Random delay
            time.sleep(random.uniform(0.1, 0.5))
        
        self.log(f"Stress test results: {success_count} success, {error_count} errors")
        success_rate = (success_count / iterations) * 100
        self.log(f"Success rate: {success_rate:.1f}%")
        
        return success_rate >= 90
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        self.log("=" * 60)
        self.log("ATLANTIPLEX STUDIO - COMPREHENSIVE DEBUG SUITE")
        self.log("=" * 60)
        
        all_tests_passed = True
        
        # 1. Connectivity Test
        if not self.test_connectivity():
            self.log("❌ Server connectivity failed - aborting tests", "FATAL")
            return False
        all_tests_passed &= True
        
        # 2. Database Systems Test
        db_results = self.test_database_systems()
        db_passed = all(db_results.values())
        all_tests_passed &= db_passed
        self.log(f"Database Systems: {'✓ PASSED' if db_passed else '✗ FAILED'}")
        
        # 3. API Endpoints Test
        self.test_api_endpoints()
        
        # 4. Login Test
        login_passed = self.test_login_functionality()
        all_tests_passed &= login_passed
        
        # 5. Streaming APIs Test
        self.test_streaming_apis()
        
        # 6. Guest System Test
        self.test_guest_system()
        
        # 7. Stress Test
        stress_passed = self.stress_test()
        all_tests_passed &= stress_passed
        
        # Final Results
        self.log("=" * 60)
        self.log("FINAL RESULTS")
        self.log("=" * 60)
        
        overall_status = "✅ ALL SYSTEMS OPERATIONAL" if all_tests_passed else "❌ ISSUES DETECTED"
        self.log(f"Overall Status: {overall_status}")
        
        if not all_tests_passed:
            self.log("\nRecommended Actions:")
            if not db_passed:
                self.log("- Check database configuration and permissions")
            if not login_passed:
                self.log("- Verify authentication system")
            if not stress_passed:
                self.log("- Optimize server performance")
        
        return all_tests_passed

if __name__ == "__main__":
    debugger = AtlantiplexDebugger()
    debugger.run_comprehensive_test()