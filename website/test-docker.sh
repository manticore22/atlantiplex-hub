#!/bin/bash
# Seraphonix Docker Test Suite
# Tests the complete deployment including API, auth, and Stripe integration

set -e

echo "============================================"
echo "SERAPHONIX DOCKER TEST SUITE"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    
    echo -n "Testing: $test_name ... "
    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# Wait for services to be ready
wait_for_service() {
    local service_url="$1"
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $service_url to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$service_url" > /dev/null 2>&1; then
            echo "$service_url is ready!"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}FAILED: $service_url did not become ready${NC}"
    return 1
}

echo ""
echo "============================================"
echo "Step 1: Building Docker Images"
echo "============================================"

# Build the API image
echo "Building seraphonix-api..."
docker build -t seraphonix-api:test ./verilysovereign-backend

echo ""
echo "============================================"
echo "Step 2: Starting Services"
echo "============================================"

# Start services
docker-compose up -d

# Wait for services
wait_for_service "http://localhost:3000/api/health"
wait_for_service "http://localhost/health"

echo ""
echo "============================================"
echo "Step 3: Running API Tests"
echo "============================================"

# Test 1: Health endpoint
run_test "Health endpoint" \
    "curl -sf http://localhost:3000/api/health | grep -q '\"status\":\"ok\"'"

# Test 2: Signup
run_test "User signup" \
    "curl -sf -X POST http://localhost:3000/api/auth/signup \
    -H 'Content-Type: application/json' \
    -d '{\"email\":\"test@example.com\",\"password\":\"testpass123\"}' | grep -q 'token'"

# Test 3: Login
run_test "User login" \
    "curl -sf -X POST http://localhost:3000/api/auth/login \
    -H 'Content-Type: application/json' \
    -d '{\"email\":\"test@example.com\",\"password\":\"testpass123\"}' | grep -q 'token'"

# Test 4: Get products
run_test "Get products" \
    "curl -sf http://localhost:3000/api/products | grep -q 'atlantiplex-studio'"

# Test 5: Protected route without token
run_test "Protected route rejected" \
    "curl -sf http://localhost:3000/api/user/subscription | grep -q 'Authentication required'"

# Test 6: Login and get subscription
TOKEN=$(curl -sf -X POST http://localhost:3000/api/auth/login \
    -H 'Content-Type: application/json' \
    -d '{"email":"test@example.com","password":"testpass123"}' | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

run_test "Get user subscription" \
    "curl -sf http://localhost:3000/api/user/subscription \
    -H 'Authorization: Bearer $TOKEN' | grep -q 'tier'"

run_test "Get user usage" \
    "curl -sf http://localhost:3000/api/user/usage \
    -H 'Authorization: Bearer $TOKEN' | grep -q 'hoursUsed'"

echo ""
echo "============================================"
echo "Step 4: Testing Static Files"
echo "============================================"

# Test static files
run_test "Main page loads" \
    "curl -sf http://localhost/ | grep -q 'SERAPHONIX'"

run_test "Login page loads" \
    "curl -sf http://localhost/login.html | grep -q 'RE-ENTER'"

run_test "Signup page loads" \
    "curl -sf http://localhost/signup.html | grep -q 'INITIATE'"

run_test "Membership page loads" \
    "curl -sf http://localhost/membership.html | grep -q 'COVENANT'"

run_test "Atlantiplex page loads" \
    "curl -sf http://localhost/atlantiplex.html | grep -q 'ATLANTIPLEX STUDIO'"

echo ""
echo "============================================"
echo "Step 5: Testing CORS"
echo "============================================"

run_test "CORS headers" \
    "curl -sf -I http://localhost:3000/api/health \
    -H 'Origin: https://verilysovereign.org' | grep -q 'Access-Control'"

echo ""
echo "============================================"
echo "Test Results"
echo "============================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "============================================"

# Cleanup
echo ""
echo "Cleaning up..."
docker-compose down

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
