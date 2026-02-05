import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || 'pk_test_51StL0tEfu4UzsT8NLxPdKLoxXwYcZyBzZxYZaXwYcZyBzZxYZaXwYcZyBzZxYZaXwYcZyBzZxYZaXwYcZyBzZxYZaX');

const plans = [
  {
    id: 'free',
    name: 'Free Plan',
    price: 0,
    features: ['Basic access', 'Limited storage', 'Community support'],
    popular: false
  },
  {
    id: 'pro',
    name: 'Pro Plan', 
    price: 29.99,
    features: ['Full access', '100GB storage', 'Priority support', 'Advanced features'],
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise Plan',
    price: 99.99,
    features: ['Unlimited access', 'Unlimited storage', '24/7 support', 'Custom features', 'SLA guarantee'],
    popular: false
  }
];

const CheckoutForm = ({ selectedPlan, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);
  const [clientSecret, setClientSecret] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    const createPaymentIntent = async () => {
      if (selectedPlan && selectedPlan.price > 0) {
        try {
          const response = await fetch('/api/create-payment-intent', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              amount: selectedPlan.price,
              currency: 'usd',
              planId: selectedPlan.id
            }),
          });
          const { clientSecret: secret } = await response.json();
          setClientSecret(secret);
        } catch (error) {
          console.error('Error creating payment intent:', error);
          onError(error);
        }
      }
    };

    createPaymentIntent();
  }, [selectedPlan]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setProcessing(true);

    if (!stripe || !elements) {
      setProcessing(false);
      return;
    }

    const cardElement = elements.getElement(CardElement);

    if (selectedPlan.price === 0) {
      // Free plan - no payment needed
      setProcessing(false);
      onSuccess({ plan: selectedPlan, status: 'free' });
      return;
    }

    try {
      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment-success`,
          receipt_email: email,
        },
        redirect: 'if_required',
      });

      if (error) {
        onError(error);
      } else if (paymentIntent) {
        onSuccess({ 
          paymentIntent, 
          plan: selectedPlan,
          status: 'success'
        });
      }
    } catch (error) {
      onError(error);
    } finally {
      setProcessing(false);
    }
  };

  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
      },
      invalid: {
        color: '#9e2146',
      },
    },
  };

  return (
    <form onSubmit={handleSubmit} className="checkout-form">
      {selectedPlan.price > 0 && (
        <div className="form-group">
          <label>Email Address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="email-input"
          />
        </div>
      )}

      {selectedPlan.price > 0 && (
        <div className="form-group">
          <label>Card Information</label>
          <div className="card-element-container">
            <CardElement options={cardElementOptions} />
          </div>
        </div>
      )}

      <div className="order-summary">
        <h3>Order Summary</h3>
        <div className="summary-item">
          <span>{selectedPlan.name}</span>
          <span>
            {selectedPlan.price === 0 ? 'Free' : `$${selectedPlan.price.toFixed(2)}/month`}
          </span>
        </div>
        {selectedPlan.price > 0 && (
          <div className="summary-total">
            <span>Total due today</span>
            <span>${selectedPlan.price.toFixed(2)}</span>
          </div>
        )}
      </div>

      <button 
        type="submit" 
        disabled={processing || !stripe || (!elements && selectedPlan.price > 0)}
        className="submit-button"
      >
        {processing ? (
          <span className="spinner"></span>
        ) : selectedPlan.price === 0 ? (
          'Start Free Plan'
        ) : (
          `Pay $${selectedPlan.price.toFixed(2)}`
        )}
      </button>

      {selectedPlan.price > 0 && (
        <p className="disclaimer">
          Your payment information is encrypted and secure. You can cancel anytime.
        </p>
      )}
    </form>
  );
};

const PaymentCheckout = ({ planId: initialPlanId }) => {
  const [selectedPlan, setSelectedPlan] = useState(plans.find(p => p.id === initialPlanId) || plans[1]);
  const [paymentStatus, setPaymentStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [successData, setSuccessData] = useState(null);

  const handlePaymentSuccess = (data) => {
    setPaymentStatus('success');
    setSuccessData(data);
    setError(null);
    
    // Store subscription info
    if (typeof window !== 'undefined') {
      localStorage.setItem('subscription', JSON.stringify({
        plan: data.plan.id,
        status: data.status,
        date: new Date().toISOString()
      }));
    }
  };

  const handlePaymentError = (error) => {
    setPaymentStatus('error');
    setError(error.message || 'Payment failed');
  };

  if (paymentStatus === 'success') {
    return (
      <div className="payment-success">
        <div className="success-icon">✓</div>
        <h2>Payment Successful!</h2>
        <p>Thank you for subscribing to the {successData.plan.name}.</p>
        <div className="success-details">
          <p>Plan: {successData.plan.name}</p>
          <p>Status: {successData.status}</p>
        </div>
        <button 
          className="dashboard-btn"
          onClick={() => window.location.href = '?account=true'}
        >
          Go to Dashboard
        </button>
      </div>
    );
  }

  if (paymentStatus === 'error') {
    return (
      <div className="payment-error">
        <div className="error-icon">✕</div>
        <h2>Payment Failed</h2>
        <p>{error}</p>
        <button 
          className="retry-btn"
          onClick={() => {
            setPaymentStatus('idle');
            setError(null);
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="payment-checkout">
      <h1>Choose Your Plan</h1>
      
      <div className="plans-container">
        {plans.map(plan => (
          <div 
            key={plan.id}
            className={`plan-card ${selectedPlan.id === plan.id ? 'selected' : ''} ${plan.popular ? 'popular' : ''}`}
            onClick={() => setSelectedPlan(plan)}
          >
            {plan.popular && <div className="popular-badge">Most Popular</div>}
            <h3>{plan.name}</h3>
            <div className="price">
              {plan.price === 0 ? 'Free' : `$${plan.price.toFixed(2)}/month`}
            </div>
            <ul className="features">
              {plan.features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="payment-form-container">
        <h2>Complete Your Subscription</h2>
        <Elements stripe={stripePromise}>
          <CheckoutForm 
            selectedPlan={selectedPlan}
            onSuccess={handlePaymentSuccess}
            onError={handlePaymentError}
          />
        </Elements>
      </div>

      <style jsx>{`
        .payment-checkout {
          max-width: 1200px;
          margin: 0 auto;
          padding: 40px 20px;
        }

        h1 {
          text-align: center;
          margin-bottom: 40px;
          color: #333;
        }

        .plans-container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-bottom: 40px;
        }

        .plan-card {
          border: 2px solid #e1e5e9;
          border-radius: 8px;
          padding: 24px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
        }

        .plan-card:hover {
          border-color: #6366f1;
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
        }

        .plan-card.selected {
          border-color: #6366f1;
          background: #f8f9ff;
        }

        .plan-card.popular {
          border-color: #6366f1;
        }

        .popular-badge {
          position: absolute;
          top: -12px;
          left: 50%;
          transform: translateX(-50%);
          background: #6366f1;
          color: white;
          padding: 4px 16px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 600;
        }

        .plan-card h3 {
          margin: 0 0 8px 0;
          color: #333;
        }

        .price {
          font-size: 32px;
          font-weight: bold;
          color: #6366f1;
          margin: 16px 0;
        }

        .features {
          list-style: none;
          padding: 0;
          margin: 16px 0 0 0;
        }

        .features li {
          padding: 8px 0;
          color: #666;
          position: relative;
          padding-left: 20px;
        }

        .features li::before {
          content: '✓';
          position: absolute;
          left: 0;
          color: #10b981;
        }

        .payment-form-container {
          max-width: 500px;
          margin: 0 auto;
          background: white;
          padding: 32px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .checkout-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-weight: 500;
          color: #333;
        }

        .email-input {
          width: 100%;
          padding: 12px 16px;
          border: 1px solid #e1e5e9;
          border-radius: 6px;
          font-size: 16px;
        }

        .card-element-container {
          padding: 12px 16px;
          border: 1px solid #e1e5e9;
          border-radius: 6px;
        }

        .order-summary {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 8px;
          border: 1px solid #e1e5e9;
        }

        .order-summary h3 {
          margin: 0 0 16px 0;
          color: #333;
        }

        .summary-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
        }

        .summary-total {
          display: flex;
          justify-content: space-between;
          font-weight: bold;
          font-size: 18px;
          border-top: 1px solid #e1e5e9;
          padding-top: 16px;
          margin-top: 16px;
        }

        .submit-button {
          background: #6366f1;
          color: white;
          border: none;
          padding: 16px 24px;
          border-radius: 6px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .submit-button:hover:not(:disabled) {
          background: #5558e3;
        }

        .submit-button:disabled {
          background: #94a3b8;
          cursor: not-allowed;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #ffffff;
          border-top: 2px solid transparent;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-right: 8px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .disclaimer {
          font-size: 14px;
          color: #6b7280;
          text-align: center;
          margin: 0;
        }

        .payment-success, .payment-error {
          text-align: center;
          padding: 40px 20px;
          max-width: 400px;
          margin: 0 auto;
        }

        .success-icon, .error-icon {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 20px;
          font-size: 40px;
        }

        .success-icon {
          background: #10b981;
          color: white;
        }

        .error-icon {
          background: #ef4444;
          color: white;
        }

        .dashboard-btn, .retry-btn {
          background: #6366f1;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          font-size: 16px;
          cursor: pointer;
          margin-top: 20px;
        }

        .retry-btn {
          background: #ef4444;
        }

        .success-details {
          margin: 20px 0;
          padding: 16px;
          background: #f8f9fa;
          border-radius: 6px;
        }

        .success-details p {
          margin: 4px 0;
        }
      `}</style>
    </div>
  );
};

export default PaymentCheckout;