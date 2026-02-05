import React from 'react'
import MainLayout from './MainLayout.jsx'
import StageDashboard from './StageDashboard.jsx'
import Login from './Login.jsx'
import PaymentPage from './PaymentPage.jsx'
import PaymentSuccess from './PaymentSuccess.jsx'
import AccountPage from './AccountPage.jsx'
import AdminDashboard from './AdminDashboard.jsx'
import { getPalette, getFontFamily } from './branding.ts'
import VerilyHub from './VerilyHub.jsx'

export default function App() {
  const token = typeof window !== 'undefined' ? sessionStorage.getItem('token') : null
  const hub = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('hub') : null
  const payment = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('payment') : null
  const account = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('account') : null
  const admin = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('admin') : null
  const success = typeof window !== 'undefined' ? window.location.pathname === '/payment-success' : false
  const palette = getPalette()
  
  // Check if user is admin (simplified check)
  const username = typeof window !== 'undefined' ? sessionStorage.getItem('username') : null
  const isAdmin = username === 'admin'

  if (!token && !success) {
    return (
      <div
        style={{
          minHeight: '100vh',
          background: palette.bg,
          fontFamily: getFontFamily(),
        }}
      >
        <Login />
      </div>
    )
  }
  
  if (success) {
    return <PaymentSuccess />
  }
  
  if (admin && admin.toLowerCase() === 'true' && isAdmin) {
    return <AdminDashboard />
  }
  
  if (account && account.toLowerCase() === 'true') {
    return <AccountPage />
  }
  
  if (payment && payment.toLowerCase() === 'true') {
    return <PaymentPage />
  }
  
  if (hub && hub.toLowerCase() === 'verily') {
    return (
      <MainLayout>
        <VerilyHub />
      </MainLayout>
    )
  }
  
  return (
    <MainLayout>
      <StageDashboard />
    </MainLayout>
  )
}
