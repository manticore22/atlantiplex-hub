import React, { useState } from 'react'
import { getPalette, getFontFamily } from './branding.ts'

/**
 * Chat component with Atlantiplex Studio theming
 */
export default function ChatPanel() {
  const [messages, setMessages] = useState([
    { from: 'system', text: 'Welcome to Atlantiplex Studio' },
  ])
  const [input, setInput] = useState('')
  const palette = getPalette()
  function handleSend(event) {
    event.preventDefault()
    if (!input.trim()) return
    setMessages((prev) => [...prev, { from: 'user', text: input }])
    setInput('')
  }
  return (
    <div
      aria-label="Chat panel"
      style={{
        border: `1px solid ${palette.accent}`,
        borderRadius: 6,
        padding: 8,
        background: `${palette.surface}`,
        boxShadow: palette.glow,
        fontFamily: getFontFamily(),
      }}
    >
      <div
        style={{
          fontWeight: 600,
          marginBottom: 6,
          color: palette.text,
        }}
      >
        Chat
      </div>
      <div
        aria-live="polite"
        style={{
          maxHeight: 140,
          overflow: 'auto',
          marginBottom: 6,
          color: palette.text,
        }}
      >
        {messages.map((m, i) => (
          <div key={i} style={{ padding: '2px 0' }}>
            <span style={{ fontWeight: 600, color: palette.accent }}>{m.from}: </span>
            <span>{m.text}</span>
          </div>
        ))}
      </div>
      <form onSubmit={handleSend} style={{ display: 'flex', gap: 4 }}>
        <input
          aria-label="Chat input"
          placeholder="Message"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{
            flex: 1,
            padding: 6,
            borderRadius: 4,
            border: `1px solid ${palette.accent}`,
            background: `${palette.bg}`,
            color: palette.text,
            fontFamily: getFontFamily(),
          }}
        />
        <button
          type="submit"
          style={{
            padding: '6px 12px',
            borderRadius: 4,
            border: 'none',
            background: `${palette.accent}`,
            color: palette.bg,
            fontWeight: 600,
            fontFamily: getFontFamily(),
          }}
        >
          Send
        </button>
      </form>
    </div>
  )
}
