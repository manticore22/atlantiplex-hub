import React from 'react'
export default function Atlantiplex() {
  return (
    <main style={{padding:20}}>
      <h1 Atlantiplex>Atlantiplex Studio</h1>
      <p>Login to access Studio features. Free tier available now, upgrades via product page.</p>
      <div style={{display:'flex',gap:12}}>
        <button className="btn">Login with Google</button>
        <button className="btn">Sign Up</button>
      </div>
    </main>
  )
}
