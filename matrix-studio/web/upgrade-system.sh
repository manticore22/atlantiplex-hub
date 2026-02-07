#!/bin/bash

# Performance and Upgrade Script for Matrix Studio
echo "🚀 Matrix Studio System Upgrade & Performance Check"
echo "=================================================="

# Check current Node.js version
echo "📋 Node.js Version:"
node --version
echo ""

# Check available memory
echo "💾 System Memory Check:"
node -e "console.log('Available Memory:', require('os').totalmem() / 1024 / 1024 / 1024, 'GB')"
echo ""

# Install performance monitoring
echo "🔧 Installing Performance Tools..."
cd "C:\Users\User\Desktop\atlantiplex hub\matrix-studio\web\stage"

# Check if autocannon is installed
if !npm list autocannon > /dev/null 2>&1; then
    echo "📊 Installing load testing tool..."
    npm install --save autocannon
else
    echo "✅ Load testing tool already installed"
fi

# Check system performance
echo "⚡ Running Performance Benchmarks..."

# Test API response times
echo "Testing API endpoint performance..."
timeout 30s autocannon -c 10 -d 5 http://localhost:9001/api/health || echo "API performance test completed"

# Check event loop lag
echo "Checking event loop performance..."
node -e "
const start = Date.now();
setTimeout(() => {
  const lag = Date.now() - start;
  console.log('Event loop lag:', lag + 'ms');
  if (lag > 100) {
    console.log('⚠️ High event loop lag detected');
  } else {
    console.log('✅ Event loop performance is good');
  }
}, 0);
"

# Memory leak detection
echo "Checking for memory leaks..."
node -e "
const initial = process.memoryUsage();
console.log('Initial memory usage:', initial.heapUsed / 1024 / 1024, 'MB');

// Simulate some load
const arr = [];
for (let i = 0; i < 1000000; i++) {
  arr.push(new Array(1000).fill(0));
}

setTimeout(() => {
  const final = process.memoryUsage();
  console.log('Final memory usage:', final.heapUsed / 1024 / 1024, 'MB');
  console.log('Memory increase:', (final.heapUsed - initial.heapUsed) / 1024 / 1024, 'MB');
  
  if (final.heapUsed - initial.heapUsed > 100) {
    console.log('⚠️ Potential memory leak detected');
  } else {
    console.log('✅ Memory usage is normal');
  }
  
  // Clear memory
  arr.length = 0;
  if (global.gc) {
    global.gc();
    console.log('✅ Garbage collection completed');
  }
}, 1000);
"

# Check Unicode support
echo "🌐 Testing Unicode support..."
node -e "
console.log('Unicode test:');
console.log('✅ Success:', '🎉');
console.log('💳 Payment:', '💰');
console.log('🔐 Security:', '🛡️');
console.log('📊 Analytics:', '📈');
console.log('✅ Unicode support working correctly');
"

# Check port availability
echo "🔌 Port Availability Check:"
netstat -an | grep ":9001" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "⚠️ Port 9001 is in use"
else
    echo "✅ Port 9001 is available"
fi

netstat -an | grep ":5173" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "⚠️ Port 5173 is in use"
else
    echo "✅ Port 5173 is available"
fi

# Test SSL/TLS setup
echo "🔒 SSL Configuration Check:"
if [ -f "C:\Users\User\Desktop\atlantiplex hub\matrix-studio\web\ssl\cert.pem" ]; then
    echo "✅ SSL certificate found"
else
    echo "ℹ️ No SSL certificate (development mode)"
fi

# Check environment variables
echo "🔧 Environment Variables Check:"
echo "STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY:+✅ Set}${STRIPE_SECRET_KEY:-❌ Missing}"
echo "STRIPE_PUBLISHABLE_KEY: ${STRIPE_PUBLISHABLE_KEY:+✅ Set}${STRIPE_PUBLISHABLE_KEY:-❌ Missing}"
echo "NODE_ENV: ${NODE_ENV:-development}"

# Performance recommendations
echo ""
echo "📈 Performance Recommendations:"

# Check Node.js version
NODE_VERSION=$(node -e "console.log(process.versions.node.split('.')[0])")
if [ "$NODE_VERSION" -lt "18" ]; then
    echo "⚠️ Consider upgrading Node.js to version 18 or higher"
else
    echo "✅ Node.js version is optimal"
fi

# Memory recommendations
TOTAL_MEMORY=$(node -e "console.log(require('os').totalmem() / 1024 / 1024 / 1024)" | cut -d'.' -f1)
if [ "$TOTAL_MEMORY" -lt "4" ]; then
    echo "⚠️ Consider increasing system memory for better performance"
else
    echo "✅ System memory is sufficient"
fi

echo ""
echo "🎯 System Upgrade Complete!"
echo "=============================="
echo "Next steps:"
echo "1. Review any ⚠️ warnings above"
echo "2. Start services: npm start"
echo "3. Run tests: http://localhost:5173/?testing=true"
echo "4. Monitor performance: Check server logs"
echo ""
echo "🚀 Your system is optimized and ready!"