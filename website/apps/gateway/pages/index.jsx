import React from 'react'
import Link from 'next/link'

export default function Home() {
  return (
    <main style={{padding:16}}>
      <h1>Gateway Landing</h1>
      <p>Brand gateway for Seraphonix + Atlantiplex Studio and future programs.</p>
      <Link href="/atlantiplex">
        <a>Go to Atlantiplex Studio</a>
      </Link>
    </main>
  )
}
