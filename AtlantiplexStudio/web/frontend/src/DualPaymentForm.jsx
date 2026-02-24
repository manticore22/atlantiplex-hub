import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';

const DualPaymentForm = ({ amount, onSuccess, onError }) => {
  const [stripe, setStripe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [clientSecret, setClientSecret] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('stripe');
  const [paypalSdkLoaded, setPaypalSdkLoaded] = useState(false);

  useEffect(() => {
    const initializePayment = async () => {
      try {
        // Initialize Stripe
        const configResponse = await fetch('/api/stripe-config');
        const { publishableKey } = await configResponse.json();
        const stripeInstance = await loadStripe(publishableKey);
        setStripe(stripeInstance);

        // Create payment intent for Stripe
        const paymentResponse = await fetch('/api/create-payment-intent', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ amount }),
        });
        const { clientSecret: secret } = await paymentResponse.json();
        setClientSecret(secret);

        // Load PayPal SDK
        if (!window.paypal) {
          const script = document.createElement('script');
          script.src = 'https://www.paypal.com/sdk/js?client-id=YOUR_PAYPAL_CLIENT_ID&currency=USD';
          script.onload = () => setPaypalSdkLoaded(true);
          document.body.appendChild(script);
        } else {
          setPaypalSdkLoaded(true);
        }

        setLoading(false);
      } catch (error) {
        console.error('Payment initialization error:', error);
        onError(error);
      }
    };

    initializePayment();
  }, [amount]);

  const handleStripePayment = async (event) => {
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

  const handlePayPalPayment = async () => {
    if (!window.paypal || !paypalSdkLoaded) return;

    setProcessing(true);
    try {
      // Create PayPal order
      const orderResponse = await fetch('/api/paypal/create-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ amount }),
      });

      const { orderID } = await orderResponse.json();

      // Render PayPal buttons
      window.paypal.Buttons({
        createOrder: () => orderID,
        onApprove: async (data) => {
          const captureResponse = await fetch('/api/paypal/capture-order', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ orderID: data.orderID }),
          });

          const { captured } = await captureResponse.json();
          if (captured) {
            onSuccess();
          } else {
            onError(new Error('PayPal payment capture failed'));
          }
          setProcessing(false);
        },
        onError: (err) => {
          onError(err);
          setProcessing(false);
        },
      }).render('#paypal-button-container');
    } catch (error) {
      onError(error);
      setProcessing(false);
    }
  };

  useEffect(() => {
    if (paymentMethod === 'paypal' && paypalSdkLoaded && !processing) {
      handlePayPalPayment();
    }
  }, [paymentMethod, paypalSdkLoaded]);

  if (loading) {
    return (
      <div className="payment-loading">
        <div className="loading-spinner"></div>
        <p>Loading payment options...</p>
      </div>
    );
  }

  return (
    <div className="dual-payment-form">
      <div className="payment-method-selector">
        <h3>Select Payment Method</h3>
        <div className="payment-methods">
          <button
            className={`payment-method-btn ${paymentMethod === 'stripe' ? 'active' : ''}`}
            onClick={() => setPaymentMethod('stripe')}
            disabled={processing}
          >
            <div className="payment-icon stripe-icon">💳</div>
            <span>Stripe</span>
          </button>
          <button
            className={`payment-method-btn ${paymentMethod === 'paypal' ? 'active' : ''}`}
            onClick={() => setPaymentMethod('paypal')}
            disabled={processing}
          >
            <div className="payment-icon paypal-icon">💰</div>
            <span>PayPal</span>
          </button>
        </div>
      </div>

      <div className="payment-summary">
        <h4>Payment Summary</h4>
        <div className="amount-display">
          <span className="currency">$</span>
          <span className="amount">{amount.toFixed(2)}</span>
        </div>
        <div className="payment-features">
          <p>✓ Secure payment processing</p>
          <p>✓ Instant activation</p>
          <p>✓ 24/7 support</p>
        </div>
      </div>

      <div className="payment-content">
        {paymentMethod === 'stripe' && (
          <form onSubmit={handleStripePayment} className="stripe-form">
            <div className="stripe-element">
              <div id="payment-element">
                <div className="card-inputs">
                  <input
                    type="text"
                    placeholder="Card Number"
                    className="card-number"
                    maxLength="19"
                    required
                  />
                  <div className="card-details">
                    <input
                      type="text"
                      placeholder="MM/YY"
                      className="card-expiry"
                      maxLength="5"
                      required
                    />
                    <input
                      type="text"
                      placeholder="CVC"
                      className="card-cvc"
                      maxLength="3"
                      required
                    />
                  </div>
                  <input
                    type="text"
                    placeholder="Cardholder Name"
                    className="card-name"
                    required
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={processing || !stripe || !clientSecret}
              className="payment-button stripe-button"
            >
              {processing ? 'Processing...' : `Pay $${amount.toFixed(2)} with Stripe`}
            </button>
          </form>
        )}

        {paymentMethod === 'paypal' && (
          <div className="paypal-form">
            <div className="paypal-info">
              <p>You will be redirected to PayPal to complete your payment.</p>
            </div>
            <div id="paypal-button-container" className="paypal-button"></div>
            {!paypalSdkLoaded && (
              <button
                className="payment-button paypal-button"
                disabled={processing}
                onClick={handlePayPalPayment}
              >
                {processing ? 'Processing...' : `Pay $${amount.toFixed(2)} with PayPal`}
              </button>
            )}
          </div>
        )}
      </div>

      <div className="payment-security">
        <div className="security-badges">
          <span className="security-badge">🔒 SSL Secured</span>
          <span className="security-badge">🛡️ PCI Compliant</span>
          <span className="security-badge">🔐 Fraud Protection</span>
        </div>
      </div>
    </div>
  );
};

export default DualPaymentForm;