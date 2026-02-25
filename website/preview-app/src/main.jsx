import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import '/design-system/tokens.css'
import './styles.css'

const root = document.getElementById('root')
createRoot(root).render(<App />)
