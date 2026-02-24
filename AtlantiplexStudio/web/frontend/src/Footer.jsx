import React from 'react'
import { getBrandLabel, getPalette, getFontFamily } from './branding.ts'

/**
 * Footer component with Atlantiplex Studio branding and Verily note
 */
export default function Footer() {
  const palette = getPalette()
  return (
    <footer
      className="footer"
      style={{
        padding: '10px 12px',
        textAlign: 'center',
        fontSize: 12,
        color: palette.text,
        opacity: 0.9,
        fontFamily: getFontFamily(),
      }}
    >
      Verily integrated • Atlantiplex Deep Sea Facility • {getBrandLabel('studioTabLabel')}
    </footer>
  )
}