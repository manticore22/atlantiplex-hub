import React from 'react'
import { getBrandLabel, getPalette, getLogoPathTiny } from './branding.ts'

/**
 * Enhanced Header component with Atlantiplex Lightning Studio branding
 */
export default function Header() {
  const palette = getPalette()
  const token = typeof window !== 'undefined' ? sessionStorage.getItem('token') : null
  const username = typeof window !== 'undefined' ? sessionStorage.getItem('username') : null
  const isAdmin = username === 'admin'

  const handleNavigation = (path) => {
    if (typeof window !== 'undefined') {
      window.location.href = path
    }
  }

  return (
    <header className="app-header slide-up">
      <img 
        src={getLogoPathTiny()} 
        alt="Atlantiplex Lightning Studio Logo" 
        className="brand-logo"
      />
      <div className="brand">
        {getBrandLabel('brandName')}
        <span className="subtle">
          {getBrandLabel('studioTabLabel')}
        </span>
      </div>
      {token && (
        <nav className="header-nav">
          <button 
            className="nav-btn"
            onClick={() => handleNavigation('/')}
          >
            Dashboard
          </button>
          <button 
            className="nav-btn"
            onClick={() => handleNavigation('?payment=true')}
          >
            Payments
          </button>
          <button 
            className="nav-btn account-btn"
            onClick={() => handleNavigation('?account=true')}
          >
            Account
          </button>
          {isAdmin && (
            <button 
              className="nav-btn admin-btn"
              onClick={() => handleNavigation('?admin=true')}
            >
              Admin
            </button>
          )}
        </nav>
      )}

      <style jsx>{`
        .header-nav {
          display: flex;
          gap: 12px;
          margin-left: auto;
        }

        .nav-btn {
          background: none;
          border: 1px solid ${palette.border};
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          color: ${palette.text};
          transition: all 0.3s ease;
        }

        .nav-btn:hover {
          background: ${palette.hover};
          border-color: ${palette.primary};
        }

        .account-btn {
          background: ${palette.primary};
          color: white;
          border-color: ${palette.primary};
        }

        .account-btn:hover {
          background: ${palette.primaryHover};
        }

        .admin-btn {
          background: #FF9800;
          color: white;
          border-color: #FF9800;
        }

        .admin-btn:hover {
          background: #F57C00;
        }
      `}</style>
    </header>
  )
}