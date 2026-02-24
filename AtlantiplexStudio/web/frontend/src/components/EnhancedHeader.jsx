import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Bell, Settings, User, LogOut, Menu, X, ChevronDown, Moon, Sun, Zap } from 'lucide-react';

const EnhancedHeader = ({ user, onLogout, onThemeToggle, theme }) => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [isScrolled, setIsScrolled] = useState(false);
  const searchRef = useRef(null);
  const profileRef = useRef(null);
  const notificationsRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsSearchOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setIsProfileOpen(false);
      }
      if (notificationsRef.current && !notificationsRef.current.contains(event.target)) {
        setIsNotificationsOpen(false);
      }
    };

    const handleKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        setIsSearchOpen(true);
      }
    };

    window.addEventListener('scroll', handleScroll);
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  useEffect(() => {
    // Simulate fetching notifications
    const mockNotifications = [
      { id: 1, type: 'stream', message: 'Your stream is starting in 5 minutes', time: '5m ago', read: false },
      { id: 2, type: 'payment', message: 'Payment processed successfully', time: '1h ago', read: false },
      { id: 3, type: 'update', message: 'New features available', time: '2h ago', read: true },
      { id: 4, type: 'system', message: 'Storage usage at 75%', time: '1d ago', read: true }
    ];
    setNotifications(mockNotifications);
  }, []);

  const handleSearch = useCallback((query) => {
    if (query.trim()) {
      console.log('Searching for:', query);
      // Implement search functionality
    }
  }, []);

  const markNotificationAsRead = useCallback((notificationId) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
  }, []);

  const markAllNotificationsAsRead = useCallback(() => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, read: true }))
    );
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className={`enhanced-header ${isScrolled ? 'scrolled' : ''}`}>
      <div className="header-left">
        <div className="brand-container">
          <div className="brand-logo">
            <div className="logo-icon">
              <Zap className="animate-pulse" size={24} />
            </div>
            <span className="brand-text">Atlantiplex</span>
          </div>
          <span className="brand-tagline">Studio</span>
        </div>

        <nav className="main-nav hidden-mobile">
          <button className="nav-item">Dashboard</button>
          <button className="nav-item">Streams</button>
          <button className="nav-item">Recordings</button>
          <button className="nav-item">Analytics</button>
          <button className="nav-item">Settings</button>
        </nav>
      </div>

      <div className="header-center">
        <div 
          ref={searchRef}
          className={`search-container ${isSearchOpen ? 'active' : ''}`}
        >
          <Search className="search-icon" size={20} />
          <input
            type="text"
            placeholder="Search... (⌘K)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch(searchQuery);
                setIsSearchOpen(false);
              }
            }}
            onFocus={() => setIsSearchOpen(true)}
            className="search-input"
          />
          
          {isSearchOpen && (
            <div className="search-dropdown">
              <div className="search-section">
                <h4>Quick Actions</h4>
                <button className="search-result-item">
                  <span>🎥</span>
                  <span>Start New Stream</span>
                </button>
                <button className="search-result-item">
                  <span>📊</span>
                  <span>View Analytics</span>
                </button>
                <button className="search-result-item">
                  <span>⚙️</span>
                  <span>Settings</span>
                </button>
              </div>
              
              {searchQuery && (
                <div className="search-section">
                  <h4>Search Results</h4>
                  <div className="search-loading">
                    <div className="loading-spinner animate-spin"></div>
                    <span>Searching...</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="header-right">
        <button 
          onClick={onThemeToggle}
          className="header-btn theme-toggle"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
        >
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        <div ref={notificationsRef} className="notifications-container">
          <button 
            onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
            className="header-btn notification-btn"
            title="Notifications"
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className="notification-badge">{unreadCount}</span>
            )}
          </button>

          {isNotificationsOpen && (
            <div className="notifications-dropdown">
              <div className="notifications-header">
                <h3>Notifications</h3>
                <button 
                  onClick={markAllNotificationsAsRead}
                  className="mark-all-read"
                >
                  Mark all as read
                </button>
              </div>
              
              <div className="notifications-list">
                {notifications.map(notification => (
                  <div 
                    key={notification.id}
                    className={`notification-item ${!notification.read ? 'unread' : ''}`}
                    onClick={() => markNotificationAsRead(notification.id)}
                  >
                    <div className="notification-icon">
                      {notification.type === 'stream' && '🎥'}
                      {notification.type === 'payment' && '💳'}
                      {notification.type === 'update' && '🔄'}
                      {notification.type === 'system' && '⚙️'}
                    </div>
                    <div className="notification-content">
                      <p className="notification-message">{notification.message}</p>
                      <span className="notification-time">{notification.time}</span>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="notifications-footer">
                <button className="view-all-notifications">View All</button>
              </div>
            </div>
          )}
        </div>

        <div ref={profileRef} className="profile-container">
          <button 
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className="profile-btn"
          >
            <div className="user-avatar">
              <img 
                src={user?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.id || 'default'}`}
                alt={user?.name || 'User'}
              />
            </div>
            <span className="user-name hidden-mobile">{user?.name || 'User'}</span>
            <ChevronDown size={16} className={`dropdown-arrow ${isProfileOpen ? 'open' : ''}`} />
          </button>

          {isProfileOpen && (
            <div className="profile-dropdown">
              <div className="profile-header">
                <div className="user-avatar large">
                  <img 
                    src={user?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.id || 'default'}`}
                    alt={user?.name || 'User'}
                  />
                </div>
                <div className="user-info">
                  <h4>{user?.name || 'User'}</h4>
                  <p>{user?.email || 'user@example.com'}</p>
                  <span className="user-status">Pro Plan • Active</span>
                </div>
              </div>

              <div className="profile-menu">
                <button className="menu-item">
                  <User size={16} />
                  <span>Profile</span>
                </button>
                <button className="menu-item">
                  <Settings size={16} />
                  <span>Settings</span>
                </button>
                <button className="menu-item">
                  <Bell size={16} />
                  <span>Preferences</span>
                </button>
                <div className="menu-divider"></div>
                <button onClick={onLogout} className="menu-item logout">
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>

        <button className="mobile-menu-btn hidden-desktop">
          <Menu size={20} />
        </button>
      </div>
    </header>
  );
};

export default EnhancedHeader;