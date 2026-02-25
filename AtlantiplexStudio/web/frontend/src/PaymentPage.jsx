import React, { useState } from 'react';
import PaymentForm from './PaymentForm.jsx';
import PaymentCheckout from './PaymentCheckout.jsx';
import { getPalette, getFontFamily } from './branding.ts';

export default function PaymentPage() {
  const [view, setView] = useState('checkout'); // 'checkout' or 'simple'
  const palette = getPalette();

  return (
    <div 
      style={{
        minHeight: '100vh',
        background: palette.bg,
        fontFamily: getFontFamily(),
      }}
    >
      <div style={{ marginBottom: '20px', textAlign: 'center' }}>
        <button 
          onClick={() => setView('checkout')}
          style={{
            background: view === 'checkout' ? palette.primary : 'transparent',
            color: view === 'checkout' ? 'white' : palette.text,
            border: `1px solid ${palette.border}`,
            padding: '8px 16px',
            margin: '0 8px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Subscribe to Plans
        </button>
        <button 
          onClick={() => setView('simple')}
          style={{
            background: view === 'simple' ? palette.primary : 'transparent',
            color: view === 'simple' ? 'white' : palette.text,
            border: `1px solid ${palette.border}`,
            padding: '8px 16px',
            margin: '0 8px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          One-Time Payment
        </button>
      </div>

      {view === 'checkout' ? (
        <PaymentCheckout />
      ) : (
        <div style={{ padding: '20px', maxWidth: '500px', margin: '0 auto' }}>
          <PaymentForm 
            amount={29.99}
            onSuccess={() => console.log('Payment successful')}
            onError={(error) => console.error('Payment failed:', error)}
          />
        </div>
      )}
    </div>
  );
}