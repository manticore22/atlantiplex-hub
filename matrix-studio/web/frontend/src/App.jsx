import React from 'react'
import MainLayout from './MainLayout.jsx'
import StageDashboard from './StageDashboard.jsx'
import Login from './Login.jsx'
import { getPalette, getFontFamily } from './branding.ts'
import VerilyHub from './VerilyHub.jsx'

export default function App() {
  const token = typeof window !== 'undefined' ? sessionStorage.getItem('token') : null
  const hub = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('hub') : null
  const palette = getPalette()
  if (!token) {
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
