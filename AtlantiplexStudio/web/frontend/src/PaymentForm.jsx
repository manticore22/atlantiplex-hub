import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';

const PaymentForm = ({ amount, onSuccess, onError }) => {
  const [stripe, setStripe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [clientSecret, setClientSecret] = useState('');

  useEffect(() => {
    const initializeStripe = async () => {
      try {
        // Get Stripe config
        const configResponse = await fetch('/api/stripe-config');
        const { publishableKey } = await configResponse.json();

        // Load Stripe.js
        const stripeInstance = loadStripe(publishableKey);
        setStripe(stripeInstance);

        // Create payment intent
        const paymentResponse = await fetch('/api/create-payment-intent', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ amount }),
        });

        const { clientSecret: secret } = await paymentResponse.json();
        setClientSecret(secret);
        setLoading(false);
      } catch (error) {
        console.error('Payment initialization error:', error);
        onError(error);
      }
    };

    initializeStripe();
  }, [amount]);

  const handlePayment = async (event) => {
    event.preventDefault();
    setProcessing(true);

    if (!stripe || !clientSecret) return;

    const { error } = await stripe.confirmPayment({
      clientSecret,
      confirmParams: {
        return_url: `${window.location.origin}/payment-success`,
      },
    });

    if (error) {
      onError(error);
    } else {
      onSuccess();
    }
    setProcessing(false);
  };

  if (loading) {
    return <div>Loading payment form...</div>;
  }

  return (
    <form onSubmit={handlePayment} className="payment-form">
      <div className="payment-summary">
        <h3>Payment Summary</h3>
        <p>Amount: ${amount.toFixed(2)}</p>
      </div>
      
      <div className="payment-element">
        {/* Stripe Elements will be mounted here */}
        <div id="payment-element">
          {/* This would be populated by Stripe Elements in a real implementation */}
          <p>Payment element placeholder</p>
        </div>
      </div>

      <button 
        type="submit" 
        disabled={processing || !stripe || !clientSecret}
        className="payment-button"
      >
        {processing ? 'Processing...' : `Pay $${amount.toFixed(2)}`}
      </button>
    </form>
  );
};

export default PaymentForm;