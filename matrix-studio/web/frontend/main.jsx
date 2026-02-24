import React from 'react'
import ReactDOM from 'react-dom/client'

export default function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Atlantiplex Studio</h1>
      <p>Frontend running successfully</p>
      <p>API URL: {import.meta.env.VITE_API_URL}</p>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
