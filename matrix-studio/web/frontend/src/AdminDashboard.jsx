import React, { useState, useEffect } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [planFilter, setPlanFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const palette = getPalette();
  const token = typeof window !== 'undefined' ? sessionStorage.getItem('token') : null;

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchAnalytics();
    } else if (activeTab === 'users') {
      fetchUsers();
    }
  }, [activeTab, currentPage, searchTerm, planFilter]);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('/api/admin/analytics', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const params = new URLSearchParams({
        page: currentPage,
        limit: 10,
        search: searchTerm,
        plan: planFilter
      });
      
      const response = await fetch(`/api/admin/users?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUserUpdate = async (userId, updates) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updates)
      });
      
      if (response.ok) {
        fetchUsers();
        if (selectedUser && selectedUser.id === userId) {
          setSelectedUser(await response.json());
        }
      }
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const handleUserDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await fetch(`/api/admin/users/${userId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        fetchUsers();
        if (selectedUser && selectedUser.id === userId) {
          setSelectedUser(null);
        }
      } catch (error) {
        console.error('Failed to delete user:', error);
      }
    }
  };

  const DashboardTab = () => {
    if (!analytics) return <div>Loading analytics...</div>;

    return (
      <div className="analytics-grid">
        <div className="stat-card">
          <h3>Total Users</h3>
          <div className="stat-value">{analytics.totalUsers}</div>
          <div className="stat-label">Registered users</div>
        </div>
        
        <div className="stat-card">
          <h3>Active Users</h3>
          <div className="stat-value">{analytics.activeUsers}</div>
          <div className="stat-label">Last 7 days</div>
        </div>
        
        <div className="stat-card">
          <h3>Total Revenue</h3>
          <div className="stat-value">${analytics.totalRevenue.toFixed(2)}</div>
          <div className="stat-label">All time</div>
        </div>
        
        <div className="stat-card">
          <h3>Monthly Revenue</h3>
          <div className="stat-value">${analytics.monthlyRevenue.toFixed(2)}</div>
          <div className="stat-label">This month</div>
        </div>

        <div className="stat-card">
          <h3>Transactions</h3>
          <div className="stat-value">{analytics.totalTransactions}</div>
          <div className="stat-label">Total processed</div>
        </div>
        
        <div className="stat-card">
          <h3>Success Rate</h3>
          <div className="stat-value">
            {analytics.totalTransactions > 0 
              ? ((analytics.successfulTransactions / analytics.totalTransactions) * 100).toFixed(1) 
              : 0}%
          </div>
          <div className="stat-label">Payment success</div>
        </div>

        <div className="chart-card">
          <h3>Plan Distribution</h3>
          <div className="plan-stats">
            <div className="plan-stat">
              <span className="plan-label">Free</span>
              <span className="plan-count">{analytics.plans.Free}</span>
            </div>
            <div className="plan-stat">
              <span className="plan-label">Pro</span>
              <span className="plan-count">{analytics.plans.Pro}</span>
            </div>
            <div className="plan-stat">
              <span className="plan-label">Enterprise</span>
              <span className="plan-count">{analytics.plans.Enterprise}</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const UsersTab = () => (
    <div className="users-management">
      <div className="users-controls">
        <input
          type="text"
          placeholder="Search users..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <select
          value={planFilter}
          onChange={(e) => setPlanFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">All Plans</option>
          <option value="Free">Free</option>
          <option value="Pro">Pro</option>
          <option value="Enterprise">Enterprise</option>
        </select>
      </div>

      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Plan</th>
              <th>Join Date</th>
              <th>Last Active</th>
              <th>Total Spent</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.users?.map(user => (
              <tr key={user.id}>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>
                  <select
                    value={user.plan}
                    onChange={(e) => handleUserUpdate(user.id, { plan: e.target.value })}
                    className="plan-select"
                  >
                    <option value="Free">Free</option>
                    <option value="Pro">Pro</option>
                    <option value="Enterprise">Enterprise</option>
                  </select>
                </td>
                <td>{user.joinDate}</td>
                <td>{user.lastActive}</td>
                <td>${user.totalSpent.toFixed(2)}</td>
                <td>
                  <button
                    onClick={() => setSelectedUser(user)}
                    className="action-btn view-btn"
                  >
                    View
                  </button>
                  <button
                    onClick={() => handleUserDelete(user.id)}
                    className="action-btn delete-btn"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button
          onClick={() => setCurrentPage(currentPage - 1)}
          disabled={currentPage === 1}
          className="page-btn"
        >
          Previous
        </button>
        <span className="page-info">
          Page {currentPage} of {users.totalPages || 1}
        </span>
        <button
          onClick={() => setCurrentPage(currentPage + 1)}
          disabled={currentPage >= (users.totalPages || 1)}
          className="page-btn"
        >
          Next
        </button>
      </div>

      {selectedUser && (
        <div className="user-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>User Details: {selectedUser.username}</h3>
              <button
                onClick={() => setSelectedUser(null)}
                className="close-btn"
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="user-detail">
                <label>Username:</label>
                <span>{selectedUser.username}</span>
              </div>
              <div className="user-detail">
                <label>Email:</label>
                <input
                  type="email"
                  value={selectedUser.email}
                  onChange={(e) => setSelectedUser({...selectedUser, email: e.target.value})}
                  onBlur={() => handleUserUpdate(selectedUser.id, { email: selectedUser.email })}
                />
              </div>
              <div className="user-detail">
                <label>Plan:</label>
                <select
                  value={selectedUser.plan}
                  onChange={(e) => setSelectedUser({...selectedUser, plan: e.target.value})}
                  onBlur={() => handleUserUpdate(selectedUser.id, { plan: selectedUser.plan })}
                >
                  <option value="Free">Free</option>
                  <option value="Pro">Pro</option>
                  <option value="Enterprise">Enterprise</option>
                </select>
              </div>
              <div className="user-detail">
                <label>Member Since:</label>
                <span>{selectedUser.joinDate}</span>
              </div>
              <div className="user-detail">
                <label>Last Active:</label>
                <span>{selectedUser.lastActive}</span>
              </div>
              <div className="user-detail">
                <label>Total Spent:</label>
                <span>${selectedUser.totalSpent.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (loading && activeTab === 'dashboard') {
    return <div>Loading admin dashboard...</div>;
  }

  return (
    <div 
      style={{
        minHeight: '100vh',
        background: palette.bg,
        fontFamily: getFontFamily(),
        padding: '20px',
      }}
    >
      <div className="admin-container" style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1>Admin Dashboard</h1>
        
        <div className="admin-tabs">
          <button 
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Users
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'dashboard' && <DashboardTab />}
          {activeTab === 'users' && <UsersTab />}
        </div>
      </div>

      <style jsx>{`
        .admin-container h1 {
          color: ${palette.text};
          margin-bottom: 30px;
        }

        .admin-tabs {
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

        .analytics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
        }

        .stat-card, .chart-card {
          background: ${palette.surface};
          padding: 24px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stat-card h3, .chart-card h3 {
          color: ${palette.text};
          margin-bottom: 12px;
          font-size: 14px;
          text-transform: uppercase;
          opacity: 0.7;
        }

        .stat-value {
          font-size: 32px;
          font-weight: bold;
          color: ${palette.primary};
          margin-bottom: 4px;
        }

        .stat-label {
          color: ${palette.text};
          opacity: 0.6;
          font-size: 14px;
        }

        .plan-stats {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .plan-stat {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid ${palette.border};
        }

        .plan-label {
          font-weight: 500;
        }

        .plan-count {
          color: ${palette.primary};
          font-weight: bold;
        }

        .users-controls {
          display: flex;
          gap: 12px;
          margin-bottom: 20px;
        }

        .search-input, .filter-select {
          padding: 10px 16px;
          border: 1px solid ${palette.border};
          border-radius: 4px;
          background: ${palette.surface};
          color: ${palette.text};
        }

        .search-input {
          flex: 1;
          max-width: 300px;
        }

        .users-table {
          background: ${palette.surface};
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .users-table table {
          width: 100%;
          border-collapse: collapse;
        }

        .users-table th {
          background: ${palette.hover};
          padding: 12px;
          text-align: left;
          font-weight: 600;
          color: ${palette.text};
        }

        .users-table td {
          padding: 12px;
          border-top: 1px solid ${palette.border};
          color: ${palette.text};
        }

        .plan-select {
          padding: 4px 8px;
          border: 1px solid ${palette.border};
          border-radius: 4px;
          background: ${palette.bg};
        }

        .action-btn {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          margin-right: 8px;
          font-size: 12px;
        }

        .view-btn {
          background: ${palette.primary};
          color: white;
        }

        .delete-btn {
          background: #f44336;
          color: white;
        }

        .pagination {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 16px;
          margin-top: 20px;
        }

        .page-btn {
          padding: 8px 16px;
          border: 1px solid ${palette.border};
          background: ${palette.surface};
          color: ${palette.text};
          border-radius: 4px;
          cursor: pointer;
        }

        .page-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .page-info {
          color: ${palette.text};
        }

        .user-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }

        .modal-content {
          background: ${palette.surface};
          padding: 24px;
          border-radius: 8px;
          max-width: 500px;
          width: 90%;
          max-height: 90vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .modal-header h3 {
          color: ${palette.text};
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: ${palette.text};
        }

        .user-detail {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid ${palette.border};
        }

        .user-detail label {
          font-weight: 600;
          color: ${palette.text};
        }

        .user-detail input,
        .user-detail select {
          padding: 6px 12px;
          border: 1px solid ${palette.border};
          border-radius: 4px;
          background: ${palette.bg};
          color: ${palette.text};
        }
      `}</style>
    </div>
  );
}