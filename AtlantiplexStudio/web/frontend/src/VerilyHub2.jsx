import React, { useState, useMemo } from 'react'
import { VERILY_BRAND } from './verilyBranding'

function DisplayCard({ id, on, onToggle }) {
  return (
    <div role="region" aria-label={`Display ${id}`} style={{ border: '1px solid #2d4a6b', borderRadius: 8, padding: 8, background: '#111' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <strong>Display {id}</strong>
        <button aria-label={`Toggle display ${id}`} onClick={onToggle} style={{ padding: '4px 8px' }}>{on ? 'On' : 'Off'}</button>
      </div>
      <div style={{ height: 100, marginTop: 6, background: '#0a0a0a', borderRadius: 6 }} />
    </div>
  )
}

export default function VerilyHub2() {
  const [displays, setDisplays] = useState([
    { id: 'A', on: true },
    { id: 'B', on: true },
    { id: 'C', on: true },
    { id: 'D', on: true },
  ])
  const [latency, setLatency] = useState(20)

  const status = useMemo(() => {
    const up = displays.filter(d => d.on).length
    return { upDisplays: up, totalDisplays: displays.length, latency }
  }, [displays, latency])

  function toggle(i) {
    setDisplays(prev => prev.map((d, idx) => idx === i ? { ...d, on: !d.on } : d))
  }

  return (
    <section aria-label="Verily Hub">
      <header style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0' }}>
        <img src={VERILY_BRAND.logoPath} alt="Verily Hub logo" style={{ height: 40 }} />
        <h2 style={{ margin: 0 }}>{VERILY_BRAND.brandName} Hub</h2>
        <span style={{ marginLeft: 'auto', color: '#9bd7ff' }}>Diagnostics</span>
      </header>

      <div className="card" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
        {displays.map((d, idx) => (
          <DisplayCard key={d.id} id={d.id} on={d.on} onToggle={() => toggle(idx)} />
        ))}
      </div>

      <section className="card" style={{ marginTop: 12, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }} aria-label="Diagnostics">
        <div>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Stage Health</div>
          <div>Displays online: {status.upDisplays}/{status.totalDisplays}</div>
          <div>Latency: {status.latency} ms</div>
        </div>
        <div>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Panel Contacts</div>
          <div>Panellists connected: 4</div>
          <div>Last event: now</div>
        </div>
      </section>
    </section>
  )
}
