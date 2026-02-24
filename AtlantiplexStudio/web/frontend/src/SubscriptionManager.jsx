import React, { useState, useEffect } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

export default function SubscriptionManager() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('subscriptions');
  const [newCustomerForm, setNewCustomerForm] = useState({
    email: '',
    name: '',
    phone: ''
  });
  const [newSubscriptionForm, setNewSubscriptionForm] = useState({
    customerId: '',
    priceId: '',
    trialPeriodDays: 0
  });

  const palette = getPalette();
  const token = typeof window !== 'undefined' ? sessionStorage.getItem('token') : null;

  // Sample price IDs (you'd get these from your Stripe dashboard)
  const priceOptions = [
    { id: 'price_1Oxxx...', name: 'Pro Plan - $29.99/month', amount: 2999 },
    { id: 'price_1Oyyy...', name: 'Enterprise - $99.99/month', amount: 9999 }
  ];

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'subscriptions') {
        await fetchSubscriptions();
      } else if (activeTab === 'customers') {
        await fetchCustomers();
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubscriptions = async () => {
    const response = await fetch('/api/admin/subscriptions', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setSubscriptions(data.subscriptions || []);
  };

  const fetchCustomers = async () => {
    const response = await fetch('/api/admin/customers', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setCustomers(data.customers || []);
  };

  const createCustomer = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/admin/create-customer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newCustomerForm)
      });

      if (response.ok) {
        setNewCustomerForm({ email: '', name: '', phone: '' });
        fetchCustomers();
      }
    } catch (error) {
      console.error('Error creating customer:', error);
    }
  };

  const createSubscription = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/admin/create-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newSubscriptionForm)
      });

      if (response.ok) {
        setNewSubscriptionForm({ customerId: '', priceId: '', trialPeriodDays: 0 });
        fetchSubscriptions();
      }
    } catch (error) {
      console.error('Error creating subscription:', error);
    }
  };

  const cancelSubscription = async (subscriptionId) => {
    if (!confirm('Are you sure you want to cancel this subscription?')) return;

    try {
      const response = await fetch(`/api/admin/cancel-subscription/${subscriptionId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchSubscriptions();
      }
    } catch (error) {
      console.error('Error cancelling subscription:', error);
    }
  };

  const refundPayment = async (paymentIntentId) => {
    const amount = prompt('Enter refund amount in cents (leave blank for full refund):');
    
    try {
      const response = await fetch('/api/admin/refund', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          paymentIntentId, 
          amount: amount ? parseInt(amount) : null 
        })
      });

      if (response.ok) {
        alert('Refund processed successfully');
        // You might want to refresh transaction history here
      }
    } catch (error) {
      console.error('Error processing refund:', error);
    }
  };

  const SubscriptionsTab = () => (
    <div className="subscriptions-section">
      <div className="section-header">
        <h2>Active Subscriptions</h2>
      </div>

      <div className="create-subscription-form">
        <h3>Create New Subscription</h3>
        <form onSubmit={createSubscription}>
          <select
            value={newSubscriptionForm.customerId}
            onChange={(e) => setNewSubscriptionForm({...newSubscriptionForm, customerId: e.target.value})}
            required
          >
            <option value="">Select Customer</option>
            {customers.map(customer => (
              <option key={customer.id} value={customer.id}>
                {customer.email} ({customer.name})
              </option>
            ))}
          </select>
          
          <select
            value={newSubscriptionForm.priceId}
            onChange={(e) => setNewSubscriptionForm({...newSubscriptionForm, priceId: e.target.value})}
            required
          >
            <option value="">Select Plan</option>
            {priceOptions.map(price => (
              <option key={price.id} value={price.id}>
                {price.name}
              </option>
            ))}
          </select>
          
          <input
            type="number"
            placeholder="Trial period (days, 0 for no trial)"
            value={newSubscriptionForm.trialPeriodDays}
            onChange={(e) => setNewSubscriptionForm({...newSubscriptionForm, trialPeriodDays: e.target.value})}
            min="0"
          />
          
          <button type="submit">Create Subscription</button>
        </form>
      </div>

      <div className="subscriptions-list">
        {subscriptions.map(sub => (
          <div key={sub.id} className="subscription-card">
            <div className="sub-header">
              <h4>{sub.customer?.email}</h4>
              <span className={`status ${sub.status}`}>{sub.status}</span>
            </div>
            <div className="sub-details">
              <p>Plan: {sub.plan?.nickname || sub.price?.nickname}</p>
              <p>Amount: ${(sub.plan?.amount || sub.price?.unit_amount || 0) / 100}</p>
              <p>Created: {new Date(sub.created * 1000).toLocaleDateString()}</p>
              {sub.trial_end && (
                <p>Trial ends: {new Date(sub.trial_end * 1000).toLocaleDateString()}</p>
              )}
            </div>
            <div className="sub-actions">
              {sub.status === 'active' && (
                <button 
                  onClick={() => cancelSubscription(sub.id)}
                  className="cancel-btn"
                >
                  Cancel
                </button>
              )}
              <button 
                onClick={() => refundPayment(sub.latest_invoice?.payment_intent)}
                className="refund-btn"
              >
                Refund Last Payment
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const CustomersTab = () => (
    <div className="customers-section">
      <div className="section-header">
        <h2>Customers</h2>
      </div>

      <div className="create-customer-form">
        <h3>Create New Customer</h3>
        <form onSubmit={createCustomer}>
          <input
            type="text"
            placeholder="Customer Name"
            value={newCustomerForm.name}
            onChange={(e) => setNewCustomerForm({...newCustomerForm, name: e.target.value})}
            required
          />
          <input
            type="email"
            placeholder="Email Address"
            value={newCustomerForm.email}
            onChange={(e) => setNewCustomerForm({...newCustomerForm, email: e.target.value})}
            required
          />
          <input
            type="tel"
            placeholder="Phone Number"
            value={newCustomerForm.phone}
            onChange={(e) => setNewCustomerForm({...newCustomerForm, phone: e.target.value})}
          />
          <button type="submit">Create Customer</button>
        </form>
      </div>

      <div className="customers-list">
        {customers.map(customer => (
          <div key={customer.id} className="customer-card">
            <div className="customer-header">
              <h4>{customer.name || customer.email}</h4>
              <span className={`status ${customer.currency}`}>{customer.currency}</span>
            </div>
            <div className="customer-details">
              <p>Email: {customer.email}</p>
              {customer.phone && <p>Phone: {customer.phone}</p>}
              <p>Created: {new Date(customer.created * 1000).toLocaleDateString()}</p>
              <p>Balance: ${(customer.balance || 0) / 100}</p>
            </div>
            <div className="customer-actions">
              <button className="view-btn">View Details</button>
              <button className="edit-btn">Edit</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: palette.bg,
      fontFamily: getFontFamily(),
      padding: '20px'
    }}>
      <div className="subscription-manager" style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1>Subscription Management</h1>
        
        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === 'subscriptions' ? 'active' : ''}`}
            onClick={() => setActiveTab('subscriptions')}
          >
            Subscriptions
          </button>
          <button
            className={`tab-btn ${activeTab === 'customers' ? 'active' : ''}`}
            onClick={() => setActiveTab('customers')}
          >
            Customers
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'subscriptions' && <SubscriptionsTab />}
          {activeTab === 'customers' && <CustomersTab />}
        </div>
      </div>

      <style jsx>{`
        .subscription-manager h1 {
          color: ${palette.text};
          margin-bottom: 30px;
        }

        .tabs {
          display: flex;
          gap: 10px;
          margin-bottom: 30px;
          border-bottom: 2px solid ${palette.border};
        }

        .tab-btn {
          background: none;
          border: none;
          padding: 12px 24px;
          cursor: pointer;
          color: ${palette.text};
          font-size: 16px;
          border-bottom: 3px solid transparent;
          transition: all 0.3s ease;
        }

        .tab-btn.active {
          border-bottom-color: ${palette.primary};
          color: ${palette.primary};
        }

        .create-customer-form, .create-subscription-form {
          background: ${palette.surface};
          padding: 24px;
          border-radius: 8px;
          margin-bottom: 30px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .create-customer-form form, .create-subscription-form form {
          display: grid;
          gap: 16px;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        }

        .create-customer-form input, .create-subscription-form input, 
        .create-customer-form select, .create-subscription-form select {
          padding: 10px 14px;
          border: 1px solid ${palette.border};
          border-radius: 4px;
          font-size: 14px;
        }

        .create-customer-form button, .create-subscription-form button {
          grid-column: span 1;
          background: ${palette.primary};
          color: white;
          border: none;
          padding: 12px 20px;
          border-radius: 4px;
          cursor: pointer;
        }

        .subscriptions-list, .customers-list {
          display: grid;
          gap: 20px;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        }

        .subscription-card, .customer-card {
          background: ${palette.surface};
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .sub-header, .customer-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .sub-header h4, .customer-header h4 {
          color: ${palette.text};
          margin: 0;
        }

        .status {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          text-transform: capitalize;
        }

        .status.active {
          background: #10b981;
          color: white;
        }

        .status.trialing {
          background: #3b82f6;
          color: white;
        }

        .status.canceled {
          background: #ef4444;
          color: white;
        }

        .status.usd {
          background: #6b7280;
          color: white;
        }

        .sub-details, .customer-details {
          margin-bottom: 16px;
        }

        .sub-details p, .customer-details p {
          margin: 4px 0;
          color: ${palette.text};
          opacity: 0.8;
        }

        .sub-actions, .customer-actions {
          display: flex;
          gap: 8px;
        }

        .cancel-btn, .refund-btn {
          background: #ef4444;
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }

        .view-btn, .edit-btn {
          background: ${palette.primary};
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }

        .refund-btn {
          background: #f59e0b;
        }
      `}</style>
    </div>
  );
}