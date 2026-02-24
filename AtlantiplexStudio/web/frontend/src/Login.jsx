import React, { useState } from 'react'
import { getPalette, getLogoPath, getBrandName } from './branding.ts'

/**
 * Modern login view with Atlantiplex Lightning Studio branding
 */
export default function Login() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const palette = getPalette()
  
  async function handleLogin(event) {
    event.preventDefault()
    setIsLoading(true)
    setError('')
    
    try {
      const form = event.target
      const username = form.username.value
      const password = form.password.value
      
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      
      if (response.ok) {
        const { token } = await response.json()
        sessionStorage.setItem('token', token)
        window.location.href = '/dashboard'
      } else {
        setError('Invalid credentials. Please try again.')
      }
    } catch (err) {
      setError('Connection error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="login-container">
      <div className="login-card scale-in">
        <div className="login-header">
          <img 
            src={getLogoPath()} 
            alt="Atlantiplex Lightning Studio Logo" 
            className="login-logo"
          />
          <h1 className="login-title">
            Welcome to<br />
            {getBrandName()}
          </h1>
          <p className="login-subtitle">Sign in to access your broadcast studio</p>
        </div>
        
        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="username" className="form-label">Username</label>
            <input
              id="username"
              name="username"
              placeholder="Enter your username"
              required
              className="input-field"
              autoComplete="username"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password" className="form-label">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="Enter your password"
              required
              className="input-field"
              autoComplete="current-password"
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button 
            type="submit" 
            className={`btn btn-primary ${isLoading ? 'btn-loading' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="loading-spinner"></span>
            ) : null}
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        <div className="login-footer">
          <p className="demo-hint">
            Demo credentials: <strong>demo / demo123</strong>
          </p>
        </div>
      </div>
    </div>
  )
}