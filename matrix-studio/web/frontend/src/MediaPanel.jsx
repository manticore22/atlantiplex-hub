import React from 'react'
import { getPalette, getFontFamily } from './branding.ts'

/**
 * Simple media panel with Atlantiplex Studio styling
 */
export default function MediaPanel({ title }) {
  const palette = getPalette()
  return (
    <div
      aria-label={title || 'Media panel'}
      style={{
        background: `${palette.surface}`,
        border: `1px solid ${palette.accent}`,
        borderRadius: 8,
        minHeight: 120,
        padding: 8,
        boxShadow: palette.glow,
        fontFamily: getFontFamily(),
      }}
    >
      <div
        style={{
          fontSize: 12,
          color: palette.text,
          marginBottom: 6,
        }}
      >
        {title || 'Media'}
      </div>
      <div
        style={{
          height: 60,
          background: `${palette.bg}`,
          borderRadius: 4,
          border: `1px dashed ${palette.accent}`,
        }}
      />
    </div>
  )
}
