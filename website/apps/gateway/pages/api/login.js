// Minimal stub login endpoint
export default function handler(req, res) {
  const { email } = req.body || {}
  res.status(200).json({ ok: true, email })
}
