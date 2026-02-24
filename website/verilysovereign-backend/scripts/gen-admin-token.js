#!/usr/bin/env node
// Generate a temporary admin JWT for testing
const jwt = require('jsonwebtoken');
const secret = process.env.JWT_SECRET || 'seraphonix-secret-key';
const payload = { id: 'admin-temp', email: 'Snark2470@gmail.com', role: 'admin' };
const token = jwt.sign(payload, secret, { expiresIn: '1h' });
console.log(token);
