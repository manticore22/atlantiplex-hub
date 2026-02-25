import React, { useState } from 'react'

export default function SignUp() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  const onSubmit = async (e) => {
    e.preventDefault()
    const resp = await fetch('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    const data = await resp.json()
    if (!resp.ok) {
      setError(data.error || 'Signup failed')
    } else {
      localStorage.setItem('token', data.token)
      window.location.href = '/billing'
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ maxWidth: 420, margin: '40px auto', padding: 20 }}>
      <h2>Sign Up</h2>
      {error && <div role="alert" style={{ color: 'red' }}>{error}</div>}
      <input name="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required style={{ width: '100%', padding: 12, marginBottom: 12 }} />
      <input name="password" placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: '100%', padding: 12, marginBottom: 12 }} />
      <button type="submit" style={{ padding: 12, width: '100%' }}>Sign Up</button>
    </form>
  )
}
