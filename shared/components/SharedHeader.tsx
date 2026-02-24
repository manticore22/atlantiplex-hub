// Shared Header/Gateway - Routes all traffic through unified header
import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

interface NavItem {
  label: string;
  path: string;
  app: string;
  icon: string;
}

const navItems: NavItem[] = [
  {
    label: 'Atlantiplex Studio',
    path: '/studio',
    app: 'atlantiplex-studio',
    icon: '🎬'
  },
  {
    label: 'Product Catalog',
    path: '/products',
    app: 'product-catalog',
    icon: '🛍️'
  },
  {
    label: 'Admin Dashboard',
    path: '/admin',
    app: 'admin-dashboard',
    icon: '⚙️'
  },
  {
    label: 'Dashboard & Social',
    path: '/dashboard',
    app: 'dashboard-social',
    icon: '📊'
  }
];

export const SharedHeader: React.FC = () => {
  return (
    <header className="gateway-header">
      <div className="header-container">
        <div className="logo-section">
          <h1>ATLANTIPLEX HUB</h1>
          <span className="subtitle">Integrated Platform Suite</span>
        </div>
        
        <nav className="main-nav">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="nav-item"
              title={item.app}
            >
              <span className="icon">{item.icon}</span>
              <span className="label">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="header-actions">
          <button className="user-menu">👤 Account</button>
          <button className="settings">⚙️ Settings</button>
        </div>
      </div>
    </header>
  );
};

export const GatewayRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <SharedHeader />
      <main className="gateway-main">
        <Routes>
          <Route path="/studio/*" element={<StudioApp />} />
          <Route path="/products/*" element={<ProductCatalogApp />} />
          <Route path="/admin/*" element={<AdminDashboardApp />} />
          <Route path="/dashboard/*" element={<DashboardSocialApp />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
};

// Placeholder app components - these will be lazy-loaded
const StudioApp = () => <div>Studio App</div>;
const ProductCatalogApp = () => <div>Product Catalog App</div>;
const AdminDashboardApp = () => <div>Admin Dashboard App</div>;
const DashboardSocialApp = () => <div>Dashboard Social App</div>;
const HomePage = () => <div>Home Page</div>;
