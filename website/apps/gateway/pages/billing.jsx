import React, { useEffect, useState } from 'react'

export default function Billing() {
  const [plans, setPlans] = useState([])
  useEffect(() => {
    fetch('/api/plans')
      .then(res => res.json())
      .then(setPlans)
  }, [])

  return (
    <div style={{ padding: 20 }}>
      <h1>Billing & Plans</h1>
      <p>This is a lightweight MVP. Sign up to start your free trial (16 hours, 2 guests/month).</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
        {plans.map(p => (
          <div key={p.id} className="plan" style={{ border: '1px solid #555', padding: 16, borderRadius: 12, minWidth: 240 }}>
            <strong style={{ display: 'block', marginBottom: 6 }}>{p.name}</strong>
            <div>{p.price} {p.cadence}</div>
            <ul>
              {p.features?.map((f,i)=> <li key={i}>{f}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
