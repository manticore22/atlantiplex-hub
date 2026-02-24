const express = require('express')
const router = express.Router()
const jwt = require('jsonwebtoken')
const fetch = require('node-fetch')

const JWT_SECRET = process.env.JWT_SECRET || 'seraphonix-secret-key-change-in-production'
const ADMIN_EMAILS = new Set(['Snark2470@gmail.com','seraphonixstudios@gmail.com'])

router.post('/google', async (req, res) => {
  const { credential } = req.body
  if (!credential) return res.status(400).json({ error: 'credential required' })
  try {
    const r = await fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + credential)
    const data = await r.json()
    const email = data.email
    if (email && ADMIN_EMAILS.has(email) && data.email_verified === 'true') {
      const token = jwt.sign({ id: 'admin', email, role: 'admin' }, JWT_SECRET, { expiresIn: '7d' })
      return res.json({ token, user: { email, role: 'admin' } })
    }
    return res.status(403).json({ error: 'Not authorized' })
  } catch (e) {
    console.error('Admin Google login error:', e)
    return res.status(500).json({ error: 'Admin login failed' })
  }
})

module.exports = router
