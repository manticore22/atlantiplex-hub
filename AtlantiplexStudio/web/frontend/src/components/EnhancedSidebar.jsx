import React, { useState, useEffect, useRef } from 'react';
import { Home, Activity, Mic, Video, Settings, BarChart, Cloud, Users, Shield, CreditCard, HelpCircle, ChevronDown, ChevronRight, Zap } from 'lucide-react';

const EnhancedSidebar = ({ isCollapsed, onToggle, activeItem, onItemClick }) => {
  const [expandedSections, setExpandedSections] = useState(['main']);
  const [quickStats, setQuickStats] = useState({
    activeStreams: 0,
    totalViews: 0,
    storageUsed: 0,
    revenue: 0
  });

  useEffect(() => {
    // Simulate fetching quick stats
    const mockStats = {
      activeStreams: 3,
      totalViews: 1250,
      storageUsed: 67,
      revenue: 2847
    };
    setQuickStats(mockStats);
  }, []);

  const toggleSection = useCallback((section) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  }, []);

  const mainMenuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, badge: null },
    { id: 'streams', label: 'Streams', icon: Activity, badge: quickStats.activeStreams },
    { id: 'recordings', label: 'Recordings', icon: Video, badge: null },
    { id: 'analytics', label: 'Analytics', icon: BarChart, badge: null },
    { id: 'storage', label: 'Cloud Storage', icon: Cloud, badge: `${quickStats.storageUsed}%` },
  ];

  const secondaryMenuItems = [
    { id: 'multistream', label: 'Multistream', icon: Zap, badge: 'NEW' },
    { id: 'ai-clips', label: 'AI Clips', icon: Video, badge: 'BETA' },
    { id: 'collaboration', label: 'Collaboration', icon: Users, badge: null },
  ];

  const settingsMenuItems = [
    { id: 'account', label: 'Account', icon: Settings, badge: null },
    { id: 'security', label: 'Security', icon: Shield, badge: null },
    { id: 'billing', label: 'Billing', icon: CreditCard, badge: null },
    { id: 'help', label: 'Help Center', icon: HelpCircle, badge: null },
  ];

  const MenuItem = ({ item, level = 0 }) => {
    const isActive = activeItem === item.id;
    const hasBadge = item.badge;

    return (
      <button
        onClick={() => onItemClick?.(item.id)}
        className={`menu-item ${isActive ? 'active' : ''} level-${level}`}
        title={isCollapsed ? item.label : undefined}
      >
        <div className="menu-item-content">
          <item.icon size={20} className="menu-icon" />
          {!isCollapsed && (
            <>
              <span className="menu-label">{item.label}</span>
              {hasBadge && (
                <span className="menu-badge">{item.badge}</span>
              )}
            </>
          )}
        </div>
        {isActive && <div className="active-indicator"></div>}
      </button>
    );
  };

  const QuickStats = () => {
    if (isCollapsed) return null;

    return (
      <div className="quick-stats">
        <h4>Quick Stats</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{quickStats.activeStreams}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{quickStats.totalViews}</div>
            <div className="stat-label">Views</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{quickStats.storageUsed}%</div>
            <div className="stat-label">Storage</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">${quickStats.revenue}</div>
            <div className="stat-label">Revenue</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <aside className={`enhanced-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button 
          onClick={onToggle}
          className="collapse-btn"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronRight 
            size={20} 
            className={isCollapsed ? '' : 'rotate-180'} 
          />
        </button>
        
        {!isCollapsed && (
          <div className="sidebar-brand">
            <div className="brand-mini">
              <Zap size={24} />
            </div>
            <span className="brand-text">Atlantiplex</span>
          </div>
        )}
      </div>

      <nav className="sidebar-nav">
        {/* Main Menu Section */}
        <div className="menu-section">
          {!isCollapsed && (
            <div className="section-title">
              <span>Main</span>
            </div>
          )}
          
          <div className="menu-group">
            {mainMenuItems.map(item => (
              <MenuItem key={item.id} item={item} />
            ))}
          </div>
        </div>

        {/* Quick Stats - Hidden when collapsed */}
        <QuickStats />

        {/* Features Section */}
        <div className="menu-section">
          {!isCollapsed && (
            <div className="section-title">
              <span>Features</span>
            </div>
          )}
          
          <div className="menu-group">
            {secondaryMenuItems.map(item => (
              <MenuItem key={item.id} item={item} />
            ))}
          </div>
        </div>

        {/* Settings Section */}
        <div className="menu-section">
          {!isCollapsed && (
            <div className="section-title">
              <span>Settings</span>
            </div>
          )}
          
          <div className="menu-group">
            {settingsMenuItems.map(item => (
              <MenuItem key={item.id} item={item} />
            ))}
          </div>
        </div>

        {/* Storage Indicator */}
        {!isCollapsed && (
          <div className="storage-indicator">
            <div className="storage-header">
              <span>Cloud Storage</span>
              <span>{quickStats.storageUsed}%</span>
            </div>
            <div className="storage-bar">
              <div 
                className="storage-fill" 
                style={{ width: `${quickStats.storageUsed}%` }}
              ></div>
            </div>
            <div className="storage-text">
              6.7 GB of 10 GB used
            </div>
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        {!isCollapsed && (
          <div className="footer-content">
            <div className="status-indicator online">
              <div className="status-dot"></div>
              <span>All systems operational</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};

export default EnhancedSidebar;