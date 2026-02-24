// Minimal stub signup endpoint
export default function handler(req, res) {
  const { name, email } = req.body || {}
  res.status(200).json({ ok: true, name, email })
}
