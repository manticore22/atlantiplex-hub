import React, { useState, useEffect } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function AccountPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [userData, setUserData] = useState({
    username: typeof window !== 'undefined' ? sessionStorage.getItem('username') || 'User' : 'User',
    email: 'user@example.com',
    plan: 'Free',
    joinDate: new Date().toLocaleDateString()
  });

  const palette = getPalette();

  const ProfileSection = () => (
    <div className="profile-section">
      <h2>Profile Information</h2>
      <div className="profile-card">
        <div className="profile-item">
          <label>Username:</label>
          <span>{userData.username}</span>
        </div>
        <div className="profile-item">
          <label>Email:</label>
          <span>{userData.email}</span>
        </div>
        <div className="profile-item">
          <label>Member Since:</label>
          <span>{userData.joinDate}</span>
        </div>
        <div className="profile-item">
          <label>Current Plan:</label>
          <span className="plan-badge">{userData.plan}</span>
        </div>
        <button className="edit-profile-btn">Edit Profile</button>
      </div>
    </div>
  );

  const BillingSection = () => {
    const [billingHistory, setBillingHistory] = useState([]);
    const [paymentMethods, setPaymentMethods] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      const fetchBillingData = async () => {
        try {
          const [historyResponse, methodsResponse] = await Promise.all([
            fetch('/api/billing-history'),
            fetch('/api/payment-methods')
          ]);

          const historyData = await historyResponse.json();
          const methodsData = await methodsResponse.json();

          setBillingHistory(historyData.history || []);
          setPaymentMethods(methodsData.paymentMethods || []);
        } catch (error) {
          console.error('Failed to fetch billing data:', error);
        } finally {
          setLoading(false);
        }
      };

      fetchBillingData();
    }, []);

    if (loading) {
      return (
        <div className="billing-section">
          <h2>Billing & Payments</h2>
          <p>Loading billing information...</p>
        </div>
      );
    }

    return (
      <div className="billing-section">
        <h2>Billing & Payments</h2>
        
        <div className="billing-card">
          <h3>Current Plan</h3>
          <div className="plan-info">
            <span className="plan-name">{userData.plan} Plan</span>
            <span className="plan-price">$0.00/month</span>
          </div>
          <button className="upgrade-btn" onClick={() => window.location.href = '?payment=true'}>
            Upgrade Plan
          </button>
        </div>

        <div className="billing-card">
          <h3>Payment Methods</h3>
          <div className="payment-methods">
            {paymentMethods.length > 0 ? (
              <div className="methods-list">
                {paymentMethods.map(method => (
                  <div key={method.id} className="payment-method-item">
                    <span>{method.type} ending in {method.last4}</span>
                    <button className="remove-method-btn">Remove</button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-methods">
                <p>No payment methods on file</p>
                <button className="add-payment-btn">Add Payment Method</button>
              </div>
            )}
          </div>
        </div>

        <div className="billing-card">
          <h3>Billing History</h3>
          <div className="billing-history">
            {billingHistory.length > 0 ? (
              <div className="history-list">
                {billingHistory.map(item => (
                  <div key={item.id} className="history-item">
                    <div className="history-details">
                      <span className="history-date">{item.created}</span>
                      <span className="history-description">{item.description}</span>
                    </div>
                    <div className="history-amount">
                      ${item.amount.toFixed(2)} {item.currency.toUpperCase()}
                    </div>
                    <span className={`history-status ${item.status}`}>
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-history">
                <p>No billing history available</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const SettingsSection = () => (
    <div className="settings-section">
      <h2>Settings</h2>
      
      <div className="settings-card">
        <h3>Notifications</h3>
        <div className="setting-item">
          <label>
            <input type="checkbox" defaultChecked />
            Email notifications
          </label>
        </div>
        <div className="setting-item">
          <label>
            <input type="checkbox" />
            Push notifications
          </label>
        </div>
      </div>

      <div className="settings-card">
        <h3>Privacy</h3>
        <div className="setting-item">
          <label>
            <input type="checkbox" defaultChecked />
            Profile visible to other users
          </label>
        </div>
        <div className="setting-item">
          <label>
            <input type="checkbox" />
            Share usage analytics
          </label>
        </div>
      </div>

      <div className="settings-card">
        <h3>Account Actions</h3>
        <button className="danger-btn">Delete Account</button>
      </div>
    </div>
  );

  return (
    <div 
      style={{
        minHeight: '100vh',
        background: palette.bg,
        fontFamily: getFontFamily(),
        padding: '20px',
      }}
    >
      <div className="account-container" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1>My Account</h1>
        
        <div className="account-tabs">
          <button 
            className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Profile
          </button>
          <button 
            className={`tab-btn ${activeTab === 'billing' ? 'active' : ''}`}
            onClick={() => setActiveTab('billing')}
          >
            Billing
          </button>
          <button 
            className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            Settings
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'profile' && <ProfileSection />}
          {activeTab === 'billing' && <BillingSection />}
          {activeTab === 'settings' && <SettingsSection />}
        </div>
      </div>

      <style jsx>{`
        .account-container h1 {
          color: ${palette.text};
          margin-bottom: 30px;
        }

        .account-tabs {
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

        .tab-btn:hover {
          background: ${palette.hover};
        }

        .profile-card,
        .billing-card,
        .settings-card {
          background: ${palette.surface};
          padding: 24px;
          border-radius: 8px;
          margin-bottom: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .profile-item {
          display: flex;
          justify-content: space-between;
          padding: 12px 0;
          border-bottom: 1px solid ${palette.border};
        }

        .profile-item:last-child {
          border-bottom: none;
        }

        .profile-item label {
          font-weight: 600;
          color: ${palette.text};
        }

        .plan-badge {
          background: ${palette.primary};
          color: white;
          padding: 4px 12px;
          border-radius: 16px;
          font-size: 14px;
        }

        .edit-profile-btn,
        .upgrade-btn,
        .add-payment-btn {
          background: ${palette.primary};
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 16px;
          transition: background 0.3s ease;
        }

        .edit-profile-btn:hover,
        .upgrade-btn:hover,
        .add-payment-btn:hover {
          background: ${palette.primaryHover};
        }

        .danger-btn {
          background: #f44336;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.3s ease;
        }

        .danger-btn:hover {
          background: #d32f2f;
        }

        .plan-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .plan-name {
          font-weight: 600;
          font-size: 18px;
        }

        .plan-price {
          color: ${palette.primary};
          font-weight: 600;
        }

        .no-methods,
        .no-history {
          text-align: center;
          padding: 20px;
          color: ${palette.text};
          opacity: 0.7;
        }

        .setting-item {
          padding: 12px 0;
          border-bottom: 1px solid ${palette.border};
        }

        .setting-item:last-child {
          border-bottom: none;
        }

        .setting-item label {
          display: flex;
          align-items: center;
          gap: 12px;
          cursor: pointer;
        }

        .setting-item input[type="checkbox"] {
          width: 18px;
          height: 18px;
        }

        h2 {
          color: ${palette.text};
          margin-bottom: 20px;
        }

        h3 {
          color: ${palette.text};
          margin-bottom: 16px;
        }

        .methods-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .payment-method-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background: ${palette.bg};
          border-radius: 4px;
          border: 1px solid ${palette.border};
        }

        .remove-method-btn {
          background: #f44336;
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }

        .history-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .history-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: ${palette.bg};
          border-radius: 4px;
          border: 1px solid ${palette.border};
        }

        .history-details {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .history-date {
          font-size: 12px;
          color: ${palette.text};
          opacity: 0.7;
        }

        .history-description {
          font-weight: 500;
        }

        .history-amount {
          font-weight: 600;
          color: ${palette.primary};
        }

        .history-status {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          text-transform: capitalize;
        }

        .history-status.succeeded {
          background: #4CAF50;
          color: white;
        }

        .history-status.pending {
          background: #FF9800;
          color: white;
        }

        .history-status.failed {
          background: #f44336;
          color: white;
        }
      `}</style>
    </div>
  );
}