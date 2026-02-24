import React, { useState, useEffect } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function PaymentTestRunner() {
  const [testResults, setTestResults] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentTest, setCurrentTest] = useState('');
  const [testSuite, setTestSuite] = useState(null);
  const [environment, setEnvironment] = useState({
    backendUrl: 'http://localhost:9001',
    frontendUrl: 'http://localhost:5173'
  });

  const palette = getPalette();

  useEffect(() => {
    // Load test suite
    if (typeof window !== 'undefined') {
      const script = document.createElement('script');
      script.src = '/test-payment-system.js';
      script.onload = () => {
        setTestSuite(new window.PaymentTestSuite());
      };
      document.head.appendChild(script);
    }
  }, []);

  const runAllTests = async () => {
    if (!testSuite) {
      alert('Test suite not loaded yet');
      return;
    }

    setIsRunning(true);
    setTestResults([]);
    
    // Override console.log to capture results
    const originalLog = console.log;
    const results = [];
    
    console.log = (...args) => {
      originalLog(...args);
      
      // Parse test results from console output
      const message = args.join(' ');
      if (message.includes('✅') || message.includes('❌')) {
        const testName = message.split('] ')[1]?.split(':')[0];
        const success = message.includes('✅');
        const details = message.split(': ')[1];
        
        if (testName) {
          results.push({
            test: testName,
            success,
            details,
            timestamp: new Date().toISOString()
          });
        }
      }
      
      setTestResults([...results]);
    };

    try {
      await testSuite.runAllTests();
    } catch (error) {
      console.error('Test suite error:', error);
      results.push({
        test: 'Test Suite Execution',
        success: false,
        details: error.message,
        timestamp: new Date().toISOString()
      });
      setTestResults(results);
    } finally {
      // Restore console.log
      console.log = originalLog;
      setIsRunning(false);
    }
  };

  const runSingleTest = async (testName) => {
    if (!testSuite) return;
    
    setCurrentTest(testName);
    setIsRunning(true);
    
    try {
      switch (testName) {
        case 'Authentication':
          await testSuite.testAuthentication();
          break;
        case 'Payment Intents':
          await testSuite.testPaymentIntents();
          break;
        case 'Customer Management':
          await testSuite.testCustomerManagement();
          break;
        case 'Subscriptions':
          await testSuite.testSubscriptions();
          break;
        case 'Refunds':
          await testSuite.testRefunds();
          break;
        case 'Analytics':
          await testSuite.testAnalytics();
          break;
        case 'Error Handling':
          await testSuite.testErrorHandling();
          break;
        case 'Performance':
          await testSuite.testPerformance();
          break;
      }
    } catch (error) {
      console.error(`Error in ${testName} test:`, error);
    } finally {
      setCurrentTest('');
      setIsRunning(false);
    }
  };

  const exportResults = () => {
    const dataStr = JSON.stringify(testResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `payment-test-results-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const passedTests = testResults.filter(r => r.success).length;
  const totalTests = testResults.length;
  const successRate = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : 0;

  return (
    <div style={{
      minHeight: '100vh',
      background: palette.bg,
      fontFamily: getFontFamily(),
      padding: '20px'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1>🧪 Payment System Test Suite</h1>
        
        <div className="test-controls" style={{
          background: palette.surface,
          padding: '24px',
          borderRadius: '8px',
          marginBottom: '30px'
        }}>
          <h2>Test Configuration</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            <div>
              <label>Backend URL:</label>
              <input
                type="text"
                value={environment.backendUrl}
                onChange={(e) => setEnvironment({...environment, backendUrl: e.target.value})}
                style={{ width: '100%', padding: '8px' }}
              />
            </div>
            <div>
              <label>Frontend URL:</label>
              <input
                type="text"
                value={environment.frontendUrl}
                onChange={(e) => setEnvironment({...environment, frontendUrl: e.target.value})}
                style={{ width: '100%', padding: '8px' }}
              />
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={runAllTests}
              disabled={isRunning}
              style={{
                background: palette.primary,
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '6px',
                cursor: isRunning ? 'not-allowed' : 'pointer',
                opacity: isRunning ? 0.6 : 1
              }}
            >
              {isRunning ? (
                <span>
                  <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⚙️</span>
                  Running Tests...
                </span>
              ) : (
                '🚀 Run All Tests'
              )}
            </button>
            
            <button
              onClick={exportResults}
              disabled={testResults.length === 0}
              style={{
                background: '#6b7280',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '6px',
                cursor: testResults.length > 0 ? 'pointer' : 'not-allowed'
              }}
            >
              📄 Export Results
            </button>
          </div>
        </div>

        <div className="test-categories" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          {[
            { name: 'Authentication', icon: '🔐' },
            { name: 'Payment Intents', icon: '💳' },
            { name: 'Customer Management', icon: '👥' },
            { name: 'Subscriptions', icon: '📋' },
            { name: 'Refunds', icon: '💰' },
            { name: 'Analytics', icon: '📊' },
            { name: 'Error Handling', icon: '🚨' },
            { name: 'Performance', icon: '⚡' }
          ].map(category => (
            <div
              key={category.name}
              className="test-category"
              style={{
                background: palette.surface,
                padding: '20px',
                borderRadius: '8px',
                border: '2px solid transparent',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onClick={() => runSingleTest(category.name)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <span style={{ fontSize: '24px' }}>{category.icon}</span>
                <h3 style={{ margin: 0, color: palette.text }}>{category.name}</h3>
              </div>
              <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
                Test {category.name.toLowerCase()} functionality
              </p>
            </div>
          ))}
        </div>

        <div className="test-results" style={{ 
          background: palette.surface, 
          padding: '24px', 
          borderRadius: '8px',
          maxHeight: '500px',
          overflowY: 'auto'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2>Test Results</h2>
            <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
              <span style={{ color: palette.text }}>
                Total: <strong>{totalTests}</strong>
              </span>
              <span style={{ color: '#10b981' }}>
                Passed: <strong>{passedTests}</strong>
              </span>
              <span style={{ color: '#ef4444' }}>
                Failed: <strong>{totalTests - passedTests}</strong>
              </span>
              <div style={{
                padding: '4px 12px',
                borderRadius: '12px',
                background: successRate >= 80 ? '#10b981' : successRate >= 60 ? '#f59e0b' : '#ef4444',
                color: 'white',
                fontSize: '14px',
                fontWeight: 'bold'
              }}>
                {successRate}%
              </div>
            </div>
          </div>

          {testResults.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
              No tests run yet. Click "Run All Tests" to start testing.
            </div>
          ) : (
            <div>
              {testResults.map((result, index) => (
                <div
                  key={index}
                  className="test-result"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '12px',
                    borderRadius: '6px',
                    marginBottom: '8px',
                    background: result.success ? '#f0f9ff' : '#fef2f2',
                    border: `1px solid ${result.success ? '#bae6fd' : '#fecaca'}`
                  }}
                >
                  <span style={{ fontSize: '20px', marginRight: '12px' }}>
                    {result.success ? '✅' : '❌'}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: '600', color: palette.text, marginBottom: '4px' }}>
                      {result.test}
                    </div>
                    <div style={{ fontSize: '14px', color: '#6b7280' }}>
                      {result.details}
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#6b7280' }}>
                    {new Date(result.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {currentTest && (
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: palette.primary,
            color: 'white',
            padding: '16px 24px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 1000
          }}>
            Running {currentTest}...
          </div>
        )}

        <style jsx>{`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          
          .test-category:hover {
            border-color: ${palette.primary} !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
          }
        `}</style>
      </div>
    </div>
  );
}