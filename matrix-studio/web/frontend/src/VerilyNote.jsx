import React from 'react'
import { getPalette, getFontFamily } from './branding.ts'

/**
 * Verily integration note component
 */
export default function VerilyNote() {
  const palette = getPalette()
  return (
    <div
      aria-label="Verily integrated"
      style={{
        fontSize: 11,
        fontStyle: 'italic',
        color: palette.text,
        opacity: 0.85,
        fontFamily: getFontFamily(),
      }}
    >
      Verily integrated
    </div>
  )
}