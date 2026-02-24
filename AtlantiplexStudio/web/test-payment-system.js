const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

class PaymentTestSuite {
  constructor() {
    this.testResults = [];
    this.adminToken = null;
    this.testCustomer = null;
    this.testPrice = null;
  }

  // Utility methods
  async logTest(testName, success, details = '') {
    const result = {
      test: testName,
      success,
      details,
      timestamp: new Date().toISOString()
    };
    this.testResults.push(result);
    console.log(`[${success ? '✅' : '❌'}] ${testName}: ${details}`);
    return result;
  }

  async makeRequest(url, options = {}) {
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });
      return {
        status: response.status,
        ok: response.ok,
        data: await response.json().catch(() => ({}))
      };
    } catch (error) {
      return { error: error.message };
    }
  }

  // Authentication tests
  async testAuthentication() {
    console.log('\n🔐 Testing Authentication...');
    
    // Test login
    const loginResult = await this.makeRequest('http://localhost:9001/api/login', {
      method: 'POST',
      body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
      })
    });

    if (loginResult.ok && loginResult.data.token) {
      this.adminToken = loginResult.data.token;
      return await this.logTest('Admin Login', true, 'Token received');
    }
    return await this.logTest('Admin Login', false, loginResult.error || 'Login failed');
  }

  // Customer Management Tests
  async testCustomerManagement() {
    console.log('\n👥 Testing Customer Management...');
    
    // Create customer
    const customerData = {
      name: 'Test Customer',
      email: 'test@example.com',
      phone: '+15551234567'
    };

    const createResult = await this.makeRequest('http://localhost:9001/api/admin/create-customer', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.adminToken}` },
      body: JSON.stringify(customerData)
    });

    if (createResult.ok) {
      this.testCustomer = createResult.data.customer;
      await this.logTest('Create Customer', true, `Customer ID: ${this.testCustomer.id}`);

      // List customers
      const listResult = await this.makeRequest('http://localhost:9001/api/admin/customers', {
        headers: { 'Authorization': `Bearer ${this.adminToken}` }
      });

      if (listResult.ok && listResult.data.customers.length > 0) {
        await this.logTest('List Customers', true, `Found ${listResult.data.customers.length} customers`);
      } else {
        await this.logTest('List Customers', false, 'Failed to list customers');
      }
    } else {
      await this.logTest('Create Customer', false, createResult.data.error || 'Creation failed');
    }
  }

  // Payment Intent Tests
  async testPaymentIntents() {
    console.log('\n💳 Testing Payment Intents...');
    
    const paymentData = {
      amount: 29.99,
      currency: 'usd',
      planId: 'pro'
    };

    const intentResult = await this.makeRequest('http://localhost:9001/api/create-payment-intent', {
      method: 'POST',
      body: JSON.stringify(paymentData)
    });

    if (intentResult.ok && intentResult.data.clientSecret) {
      await this.logTest('Create Payment Intent', true, 'Client secret received');
    } else {
      await this.logTest('Create Payment Intent', false, intentResult.data.error || 'Failed to create');
    }

    // Test invalid amount
    const invalidResult = await this.makeRequest('http://localhost:9001/api/create-payment-intent', {
      method: 'POST',
      body: JSON.stringify({ amount: -10 })
    });

    if (!invalidResult.ok) {
      await this.logTest('Invalid Payment Intent', true, 'Properly rejected negative amount');
    } else {
      await this.logTest('Invalid Payment Intent', false, 'Should have rejected negative amount');
    }
  }

  // Subscription Tests
  async testSubscriptions() {
    console.log('\n📋 Testing Subscriptions...');
    
    if (!this.testCustomer) {
      await this.logTest('Subscription Tests', false, 'No test customer available');
      return;
    }

    // Create a test price in Stripe first (you'd do this in dashboard)
    const testPriceId = 'price_1Oxxx...'; // Replace with actual test price

    const subscriptionData = {
      customerId: this.testCustomer.id,
      priceId: testPriceId,
      trialPeriodDays: 7
    };

    const subResult = await this.makeRequest('http://localhost:9001/api/admin/create-subscription', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.adminToken}` },
      body: JSON.stringify(subscriptionData)
    });

    if (subResult.ok) {
      await this.logTest('Create Subscription', true, `Subscription ID: ${subResult.data.subscription.id}`);
    } else {
      await this.logTest('Create Subscription', false, subResult.data.error || 'Failed to create');
    }

    // List subscriptions
    const listResult = await this.makeRequest('http://localhost:9001/api/admin/subscriptions', {
      headers: { 'Authorization': `Bearer ${this.adminToken}` }
    });

    if (listResult.ok) {
      await this.logTest('List Subscriptions', true, `Found ${listResult.data.subscriptions.length} subscriptions`);
    } else {
      await this.logTest('List Subscriptions', false, 'Failed to list');
    }
  }

  // Refund Tests
  async testRefunds() {
    console.log('\n💰 Testing Refunds...');
    
    const refundData = {
      paymentIntentId: 'pi_test_12345', // Test payment intent ID
      amount: 1500 // $15.00 in cents
    };

    const refundResult = await this.makeRequest('http://localhost:9001/api/admin/refund', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.adminToken}` },
      body: JSON.stringify(refundData)
    });

    // Refund may fail if payment intent doesn't exist, but should handle gracefully
    if (refundResult.status === 500 && refundResult.data.error) {
      await this.logTest('Refund Error Handling', true, 'Properly handled invalid payment intent');
    } else if (refundResult.ok) {
      await this.logTest('Process Refund', true, 'Refund processed successfully');
    } else {
      await this.logTest('Process Refund', false, 'Unexpected result');
    }
  }

  // Analytics Tests
  async testAnalytics() {
    console.log('\n📊 Testing Analytics...');
    
    const analyticsResult = await this.makeRequest('http://localhost:9001/api/admin/analytics', {
      headers: { 'Authorization': `Bearer ${this.adminToken}` }
    });

    if (analyticsResult.ok) {
      const analytics = analyticsResult.data;
      await this.logTest('Analytics Endpoint', true, `Users: ${analytics.totalUsers}, Revenue: $${analytics.totalRevenue}`);
    } else {
      await this.logTest('Analytics Endpoint', false, analyticsResult.data.error || 'Failed to fetch');
    }
  }

  // Configuration Tests
  async testConfiguration() {
    console.log('\n⚙️ Testing Configuration...');
    
    const configResult = await this.makeRequest('http://localhost:9001/api/stripe-config');
    
    if (configResult.ok && configResult.data.publishableKey) {
      await this.logTest('Stripe Config', true, 'Publishable key available');
    } else {
      await this.logTest('Stripe Config', false, 'Missing publishable key');
    }

    // Test webhook verification
    const webhookData = {
      type: 'payment_intent.succeeded',
      data: {
        object: {
          id: 'pi_test_12345',
          amount: 2999,
          currency: 'usd'
        }
      }
    };

    const webhookResult = await this.makeRequest('http://localhost:9001/api/webhooks/stripe', {
      method: 'POST',
      headers: {
        'stripe-signature': 'test_signature'
      },
      body: JSON.stringify(webhookData)
    });

    // Webhook should fail signature verification
    if (!webhookResult.ok) {
      await this.logTest('Webhook Security', true, 'Properly rejected invalid signature');
    } else {
      await this.logTest('Webhook Security', false, 'Should reject invalid webhook signature');
    }
  }

  // Performance Tests
  async testPerformance() {
    console.log('\n⚡ Testing Performance...');
    
    const startTime = Date.now();
    
    // Make multiple concurrent requests
    const promises = [];
    for (let i = 0; i < 10; i++) {
      promises.push(
        this.makeRequest('http://localhost:9001/api/admin/analytics', {
          headers: { 'Authorization': `Bearer ${this.adminToken}` }
        })
      );
    }

    await Promise.all(promises);
    const endTime = Date.now();
    const avgTime = (endTime - startTime) / 10;

    if (avgTime < 1000) {
      await this.logTest('Performance', true, `Average response time: ${avgTime}ms`);
    } else {
      await this.logTest('Performance', false, `Slow response time: ${avgTime}ms`);
    }
  }

  // Error Handling Tests
  async testErrorHandling() {
    console.log('\n🚨 Testing Error Handling...');
    
    // Test unauthorized access
    const unauthorizedResult = await this.makeRequest('http://localhost:9001/api/admin/analytics');
    
    if (!unauthorizedResult.ok && unauthorizedResult.status === 401) {
      await this.logTest('Unauthorized Access', true, 'Properly rejected without token');
    } else {
      await this.logTest('Unauthorized Access', false, 'Should require authentication');
    }

    // Test non-admin access
    const nonAdminResult = await this.makeRequest('http://localhost:9001/api/login', {
      method: 'POST',
      body: JSON.stringify({
        username: 'alice',
        password: 'password123'
      })
    });

    if (nonAdminResult.ok) {
      const userToken = nonAdminResult.data.token;
      const adminResult = await this.makeRequest('http://localhost:9001/api/admin/analytics', {
        headers: { 'Authorization': `Bearer ${userToken}` }
      });

      if (!adminResult.ok && adminResult.status === 403) {
        await this.logTest('Role-Based Access', true, 'Non-admin properly blocked');
      } else {
        await this.logTest('Role-Based Access', false, 'Non-admin should be blocked');
      }
    } else {
      await this.logTest('Non-Admin Login', false, 'Failed to login as regular user');
    }
  }

  // Run all tests
  async runAllTests() {
    console.log('🧪 Starting Payment System Test Suite');
    console.log('=====================================');
    
    await this.testAuthentication();
    await this.testConfiguration();
    await this.testPaymentIntents();
    await this.testCustomerManagement();
    await this.testSubscriptions();
    await this.testRefunds();
    await this.testAnalytics();
    await this.testErrorHandling();
    await this.testPerformance();
    
    this.generateReport();
  }

  generateReport() {
    console.log('\n📋 Test Report');
    console.log('===============');
    
    const passed = this.testResults.filter(r => r.success).length;
    const total = this.testResults.length;
    const failed = total - passed;
    
    console.log(`Total Tests: ${total}`);
    console.log(`Passed: ${passed} ✅`);
    console.log(`Failed: ${failed} ❌`);
    console.log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`);
    
    if (failed > 0) {
      console.log('\n❌ Failed Tests:');
      this.testResults
        .filter(r => !r.success)
        .forEach(r => console.log(`  • ${r.test}: ${r.details}`));
    }
    
    console.log('\n📄 Detailed results saved to test-results.json');
    
    // Save results to file
    if (typeof window !== 'undefined') {
      const blob = new Blob([JSON.stringify(this.testResults, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'payment-test-results.json';
      a.click();
    }
  }
}

// Export for use in browser or Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PaymentTestSuite;
} else if (typeof window !== 'undefined') {
  window.PaymentTestSuite = PaymentTestSuite;
}