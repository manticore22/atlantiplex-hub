import React, { useState, useEffect } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function PaymentSuccess() {
  const [paymentDetails, setPaymentDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const palette = getPalette();

  useEffect(() => {
    // Get payment details from URL params or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const payment_intent = urlParams.get('payment_intent');
    const payment_intent_client_secret = urlParams.get('payment_intent_client_secret');

    if (payment_intent) {
      // Verify payment with backend
      fetch(`/api/verify-payment?payment_intent=${payment_intent}`)
        .then(response => response.json())
        .then(data => {
          setPaymentDetails(data);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error verifying payment:', error);
          setLoading(false);
        });
    } else {
      // Try to get from localStorage (for subscription flow)
      const subscription = localStorage.getItem('subscription');
      if (subscription) {
        setPaymentDetails(JSON.parse(subscription));
        setLoading(false);
      } else {
        setLoading(false);
      }
    }
  }, []);

  const handleGoToDashboard = () => {
    window.location.href = '?account=true';
  };

  const handleDownloadReceipt = () => {
    // Generate and download PDF receipt
    window.print();
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: palette.bg,
        fontFamily: getFontFamily(),
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div>
          <div className="spinner"></div>
          <p>Confirming your payment...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: palette.bg,
      fontFamily: getFontFamily(),
      padding: '40px 20px'
    }}>
      <div style={{
        maxWidth: '600px',
        margin: '0 auto',
        background: 'white',
        borderRadius: '12px',
        padding: '40px',
        textAlign: 'center',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          borderRadius: '50%',
          background: '#10b981',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 24px',
          fontSize: '40px',
          color: 'white'
        }}>
          ✓
        </div>

        <h1 style={{
          color: '#1f2937',
          fontSize: '32px',
          marginBottom: '16px'
        }}>
          Payment Successful!
        </h1>

        <p style={{
          color: '#6b7280',
          fontSize: '18px',
          marginBottom: '32px'
        }}>
          Thank you for your payment. Your subscription has been activated.
        </p>

        {paymentDetails && (
          <div style={{
            background: '#f8f9fa',
            borderRadius: '8px',
            padding: '24px',
            margin: '32px 0',
            textAlign: 'left'
          }}>
            <h3 style={{ marginBottom: '16px', color: '#1f2937' }}>Payment Details</h3>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ color: '#6b7280' }}>Plan:</span>
              <span style={{ fontWeight: 'bold' }}>
                {paymentDetails.plan?.name || 'Premium Plan'}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ color: '#6b7280' }}>Amount:</span>
              <span style={{ fontWeight: 'bold' }}>
                ${paymentDetails.plan?.price?.toFixed(2) || '29.99'}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ color: '#6b7280' }}>Status:</span>
              <span style={{ 
                color: '#10b981',
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {paymentDetails.status || 'Active'}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ color: '#6b7280' }}>Date:</span>
              <span>
                {paymentDetails.date ? new Date(paymentDetails.date).toLocaleDateString() : new Date().toLocaleDateString()}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#6b7280' }}>Transaction ID:</span>
              <span style={{ fontSize: '12px', fontFamily: 'monospace' }}>
                {paymentDetails.paymentIntent?.id || 'TXN' + Date.now()}
              </span>
            </div>
          </div>
        )}

        <div style={{
          display: 'flex',
          gap: '16px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <button
            onClick={handleGoToDashboard}
            style={{
              background: palette.primary,
              color: 'white',
              border: 'none',
              padding: '16px 32px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'background 0.3s ease'
            }}
          >
            Go to Dashboard
          </button>
          
          <button
            onClick={handleDownloadReceipt}
            style={{
              background: 'transparent',
              color: palette.primary,
              border: `2px solid ${palette.primary}`,
              padding: '14px 30px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            Download Receipt
          </button>
        </div>

        <div style={{
          marginTop: '32px',
          padding: '24px',
          background: '#f0f9ff',
          borderRadius: '8px',
          border: '1px solid #bae6fd'
        }}>
          <h4 style={{ color: '#0369a1', marginBottom: '12px' }}>What's Next?</h4>
          <ul style={{
            textAlign: 'left',
            color: '#6b7280',
            paddingLeft: '20px'
          }}>
        <li>Your subscription is now active</li>
            <li>You'll receive a confirmation email shortly</li>
            <li>Access all premium features immediately</li>
            <li>Manage your subscription in Account Settings</li>
          </ul>
        </div>

        <p style={{
          marginTop: '24px',
          fontSize: '14px',
          color: '#9ca3af'
        }}>
          Questions? Contact our support team at support@yourapp.com
        </p>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #e5e7eb;
          border-top: 4px solid ${palette.primary};
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px;
        }
      `}</style>
    </div>
  );
}