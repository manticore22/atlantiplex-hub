import React from 'react'
import Header from './Header.jsx'
import Footer from './Footer.jsx'
import VerilyNote from './VerilyNote.jsx'
import { getPalette, getFontFamily } from './branding.ts'

export default function MainLayout({ children }) {
  const palette = getPalette()
  return (
    <div className="main-layout fade-in">
      <Header />
      <main className="main-content">
        <VerilyNote />
        {children}
      </main>
      <Footer />
    </div>
  )
}