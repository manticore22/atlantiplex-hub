import React from 'react'
import { getBrandLabel, getPalette, getLogoPathTiny } from './branding.ts'

/**
 * Enhanced Header component with Atlantiplex Lightning Studio branding
 */
export default function Header() {
  const palette = getPalette()
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
    </header>
  )
}