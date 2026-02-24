import React, { useState } from 'react'
import { getPalette, getFontFamily } from './branding.ts'

/**
 * Grid‑based stage layout editor with Atlantiplex branding
 */
export default function StageLayoutEditor() {
  const [layout, setLayout] = useState([
    { id: 's1', x: 0, y: 0, w: 1, h: 1 },
    { id: 's2', x: 1, y: 0, w: 1, h: 1 },
    { id: 's3', x: 0, y: 1, w: 1, h: 1 },
    { id: 's4', x: 1, y: 1, w: 1, h: 1 },
  ])
  const palette = getPalette()
  return (
    <div
      aria-label="Stage layout editor"
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: 8,
        padding: 8,
        background: `${palette.bg}`,
        border: `1px solid ${palette.accent}`,
        borderRadius: 8,
        fontFamily: getFontFamily(),
      }}
    >
      {layout.map((tile) => (
        <div
          key={tile.id}
          style={{
            border: `1px solid ${palette.accent}`,
            borderRadius: 6,
            padding: 8,
            minHeight: 120,
            background: `${palette.surface}`,
            boxShadow: palette.glow,
            position: 'relative',
          }}
        >
          <div
            style={{
              fontSize: 12,
              color: palette.text,
              marginBottom: 6,
            }}
          >
            {tile.id}
          </div>
          <div
            style={{
              height: 60,
              background: `${palette.bg}`,
              borderRadius: 4,
              border: `1px dashed ${palette.accent}`,
            }}
          />
          <button
            aria-label={`Configure ${tile.id}`}
            style={{
              position: 'absolute',
              bottom: 4,
              right: 4,
              padding: '2px 6px',
              fontSize: 10,
              background: `${palette.accent}`,
              color: palette.bg,
              border: 'none',
              borderRadius: 4,
              cursor: 'pointer',
            }}
          >
            Config
          </button>
        </div>
      ))}
    </div>
  )
}
