#!/usr/bin/env python3
"""
Atlantiplex Studio - Pre-Flight Test Suite
Checks all endpoints, configurations, and dependencies before deployment
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple

# Test configuration
TEST_CONFIG = {
    'stage_server': {
        'url': os.getenv('STAGE_URL', 'http://localhost:9001'),
        'timeout': 5
    },
    'flask_backend': {
        'url': os.getenv('FLASK_URL', 'http://localhost:5000'),
        'timeout': 5
    },
    'frontend': {
        'url': os.getenv('FRONTEND_URL', 'http://localhost:5173'),
        'timeout': 5
    }
}

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

class PreFlightTester:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }
    
    def run_all_tests(self):
        """Run all pre-flight tests"""
        print("="*70)
        print("ATLANTIPLEX STUDIO - PRE-FLIGHT TEST SUITE")
        print("="*70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Environment Tests
        self.test_environment_variables()
        
        # 2. Stage Server Tests (Node.js)
        self.test_stage_server_health()
        self.test_stage_server_login()
        self.test_stage_server_stripe_config()
        self.test_stage_server_payment_intent()
        
        # 3. Flask Backend Tests (Python)
        self.test_flask_health()
        self.test_flask_auth()
        self.test_flask_subscription_tiers()
        
        # 4. Frontend Tests
        self.test_frontend_build()
        
        # 5. Integration Tests
        self.test_cors_configuration()
        self.test_websocket_connection()
        
        # 6. Security Tests
        self.test_security_headers()
        
        # Print summary
        self.print_summary()
        
        return self.results['failed'] == 0
    
    def test_environment_variables(self):
        """Test 1: Check required environment variables"""
        print_info("Testing Environment Variables...")
        
        required_vars = [
            'STRIPE_SECRET_KEY',
            'STRIPE_PUBLISHABLE_KEY',
            'JWT_SECRET'
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print_error(f"Missing environment variables: {', '.join(missing)}")
            self.results['failed'] += 1
        else:
            print_success("All required environment variables are set")
            self.results['passed'] += 1
        
        # Optional variables
        optional_vars = ['STRIPE_WEBHOOK_SECRET', 'DATABASE_URL']
        for var in optional_vars:
            if os.getenv(var):
                print_success(f"{var} is configured")
            else:
                print_warning(f"{var} not set (optional)")
                self.results['warnings'] += 1
        
        print()
    
    def test_stage_server_health(self):
        """Test 2: Stage server health check"""
        print_info("Testing Stage Server Health...")
        
        try:
            response = requests.get(
                f"{TEST_CONFIG['stage_server']['url']}/health",
                timeout=TEST_CONFIG['stage_server']['timeout']
            )
            
            if response.status_code == 200:
                print_success("Stage server is healthy")
                self.results['passed'] += 1
            else:
                print_error(f"Stage server returned status {response.status_code}")
                self.results['failed'] += 1
        except requests.exceptions.ConnectionError:
            print_error("Cannot connect to Stage server. Is it running?")
            print_info(f"Expected at: {TEST_CONFIG['stage_server']['url']}")
            self.results['failed'] += 1
        except Exception as e:
            print_error(f"Health check failed: {str(e)}")
            self.results['failed'] += 1
        
        print()
    
    def test_stage_server_login(self):
        """Test 3: Authentication endpoint"""
        print_info("Testing Authentication Endpoint...")
        
        try:
            response = requests.post(
                f"{TEST_CONFIG['stage_server']['url']}/api/login",
                json={"username": "admin", "password": "admin123"},
                timeout=TEST_CONFIG['stage_server']['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    print_success("Login endpoint working")
                    self.results['passed'] += 1
                    # Store token for later tests
                    self.auth_token = data['token']
                else:
                    print_error("Login response missing token")
                    self.results['failed'] += 1
            else:
                print_error(f"Login failed with status {response.status_code}")
                self.results['failed'] += 1
        except Exception as e:
            print_error(f"Login test failed: {str(e)}")
            self.results['failed'] += 1
        
        print()
    
    def test_stage_server_stripe_config(self):
        """Test 4: Stripe configuration endpoint"""
        print_info("Testing Stripe Configuration...")
        
        try:
            response = requests.get(
                f"{TEST_CONFIG['stage_server']['url']}/api/stripe-config",
                timeout=TEST_CONFIG['stage_server']['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'publishableKey' in data:
                    key = data['publishableKey']
                    if key.startswith('pk_'):
                        print_success(f"Stripe publishable key configured ({key[:20]}...)")
                        self.results['passed'] += 1
                    else:
                        print_error("Invalid Stripe key format")
                        self.results['failed'] += 1
                else:
                    print_error("Stripe config missing publishableKey")
                    self.results['failed'] += 1
            else:
                print_error(f"Stripe config failed: {response.status_code}")
                self.results['failed'] += 1
        except Exception as e:
            print_error(f"Stripe config test failed: {str(e)}")
            self.results['failed'] += 1
        
        print()
    
    def test_stage_server_payment_intent(self):
        """Test 5: Payment intent creation"""
        print_info("Testing Payment Intent Creation...")
        
        try:
            response = requests.post(
                f"{TEST_CONFIG['stage_server']['url']}/api/create-payment-intent",
                json={
                    "amount": 29.99,
                    "currency": "usd",
                    "planId": "test-plan",
                    "email": "test@example.com"
                },
                timeout=TEST_CONFIG['stage_server']['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'clientSecret' in data:
                    print_success("Payment intent creation working")
                    self.results['passed'] += 1
                else:
                    print_error("Payment intent missing clientSecret")
                    self.results['failed'] += 1
            elif response.status_code == 500:
                error_data = response.json()
                if 'Stripe' in str(error_data) or 'stripe' in str(error_data):
                    print_warning("Stripe API error - check STRIPE_SECRET_KEY")
                    self.results['warnings'] += 1
                else:
                    print_error(f"Payment intent failed: {error_data}")
                    self.results['failed'] += 1
            else:
                print_error(f"Payment intent returned status {response.status_code}")
                self.results['failed'] += 1
        except Exception as e:
            print_error(f"Payment intent test failed: {str(e)}")
            self.results['failed'] += 1
        
        print()
    
    def test_flask_health(self):
        """Test 6: Flask backend health check"""
        print_info("Testing Flask Backend Health...")
        
        try:
            response = requests.get(
                f"{TEST_CONFIG['flask_backend']['url']}/api/health",
                timeout=TEST_CONFIG['flask_backend']['timeout']
            )
            
            if response.status_code == 200:
                print_success("Flask backend is healthy")
                self.results['passed'] += 1
            else:
                print_warning(f"Flask backend returned status {response.status_code}")
                self.results['warnings'] += 1
        except requests.exceptions.ConnectionError:
            print_warning("Cannot connect to Flask backend (may not be running)")
            self.results['warnings'] += 1
        except Exception as e:
            print_warning(f"Flask health check: {str(e)}")
            self.results['warnings'] += 1
        
        print()
    
    def test_flask_auth(self):
        """Test 7: Flask authentication"""
        print_info("Testing Flask Authentication...")
        
        try:
            response = requests.post(
                f"{TEST_CONFIG['flask_backend']['url']}/api/auth/login",
                json={"username": "admin", "password": "admin123"},
                timeout=TEST_CONFIG['flask_backend']['timeout']
            )
            
            if response.status_code == 200:
                print_success("Flask authentication working")
                self.results['passed'] += 1
            else:
                print_warning(f"Flask auth returned status {response.status_code}")
                self.results['warnings'] += 1
        except Exception as e:
            print_warning(f"Flask auth test: {str(e)}")
            self.results['warnings'] += 1
        
        print()
    
    def test_flask_subscription_tiers(self):
        """Test 8: Subscription tiers endpoint"""
        print_info("Testing Subscription Tiers...")
        
        try:
            response = requests.get(
                f"{TEST_CONFIG['flask_backend']['url']}/api/subscriptions/tiers",
                timeout=TEST_CONFIG['flask_backend']['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'tiers' in data:
                    print_success("Subscription tiers endpoint working")
                    self.results['passed'] += 1
                else:
                    print_warning("Subscription tiers response format unexpected")
                    self.results['warnings'] += 1
            else:
                print_warning(f"Subscription tiers returned status {response.status_code}")
                self.results['warnings'] += 1
        except Exception as e:
            print_warning(f"Subscription tiers test: {str(e)}")
            self.results['warnings'] += 1
        
        print()
    
    def test_frontend_build(self):
        """Test 9: Frontend build verification"""
        print_info("Testing Frontend Build...")
        
        frontend_path = "matrix-studio/web/frontend"
        dist_path = f"{frontend_path}/dist"
        
        if os.path.exists(dist_path):
            files = os.listdir(dist_path)
            if len(files) > 0:
                print_success(f"Frontend build exists ({len(files)} files)")
                self.results['passed'] += 1
            else:
                print_warning("Frontend dist folder is empty")
                self.results['warnings'] += 1
        else:
            print_warning(f"Frontend dist folder not found at {dist_path}")
            print_info("Run: cd matrix-studio/web/frontend && npm run build")
            self.results['warnings'] += 1
        
        print()
    
    def test_cors_configuration(self):
        """Test 10: CORS configuration"""
        print_info("Testing CORS Configuration...")
        
        try:
            response = requests.options(
                f"{TEST_CONFIG['stage_server']['url']}/api/login",
                headers={
                    'Origin': 'http://localhost:5173',
                    'Access-Control-Request-Method': 'POST'
                },
                timeout=TEST_CONFIG['stage_server']['timeout']
            )
            
            if 'Access-Control-Allow-Origin' in response.headers:
                print_success("CORS headers present")
                self.results['passed'] += 1
            else:
                print_warning("CORS headers may not be configured")
                self.results['warnings'] += 1
        except Exception as e:
            print_warning(f"CORS test: {str(e)}")
            self.results['warnings'] += 1
        
        print()
    
    def test_websocket_connection(self):
        """Test 11: WebSocket connection test"""
        print_info("Testing WebSocket Connection...")
        
        try:
            import websocket
            
            ws_url = TEST_CONFIG['stage_server']['url'].replace('http', 'ws')
            ws = websocket.create_connection(
                f"{ws_url}/socket.io/?EIO=4&transport=websocket",
                timeout=5
            )
            
            # Send ping
            ws.send("40")
            result = ws.recv()
            
            if result:
                print_success("WebSocket connection working")
                self.results['passed'] += 1
            else:
                print_warning("WebSocket connected but no response")
                self.results['warnings'] += 1
            
            ws.close()
        except ImportError:
            print_warning("websocket-client not installed, skipping WebSocket test")
            print_info("Install with: pip install websocket-client")
            self.results['warnings'] += 1
        except Exception as e:
            print_warning(f"WebSocket test: {str(e)}")
            self.results['warnings'] += 1
        
        print()
    
    def test_security_headers(self):
        """Test 12: Security headers"""
        print_info("Testing Security Headers...")
        
        try:
            response = requests.get(
                TEST_CONFIG['stage_server']['url'],
                timeout=TEST_CONFIG['stage_server']['timeout']
            )
            
            headers = response.headers
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            present = [h for h in security_headers if h in headers]
            
            if len(present) >= 2:
                print_success(f"Security headers present ({len(present)}/3)")
                self.results['passed'] += 1
            else:
                print_warning(f"Missing security headers ({len(present)}/3)")
                self.results['warnings'] += 1
        except Exception as e:
            print_warning(f"Security headers test: {str(e)}")
            self.results['warnings'] += 1
        
        print()
    
    def print_summary(self):
        """Print test summary"""
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.results['passed'] + self.results['failed'] + self.results['warnings']}")
        print(f"{Colors.GREEN}Passed: {self.results['passed']}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.results['failed']}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.results['warnings']}{Colors.END}")
        print()
        
        if self.results['failed'] == 0:
            print(f"{Colors.GREEN}✓ ALL CRITICAL TESTS PASSED - READY FOR DEPLOYMENT{Colors.END}")
            if self.results['warnings'] > 0:
                print(f"{Colors.YELLOW}⚠ Address warnings before production deployment{Colors.END}")
        else:
            print(f"{Colors.RED}✗ CRITICAL TESTS FAILED - FIX BEFORE DEPLOYMENT{Colors.END}")
            print()
            print("Critical failures:")
            print("1. Check that all servers are running")
            print("2. Verify environment variables are set")
            print("3. Review error messages above")
        
        print()
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

def main():
    """Main entry point"""
    tester = PreFlightTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
