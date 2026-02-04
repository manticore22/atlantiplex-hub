const express = require('express');
const http = require('http');
const path = require('path');
const fs = require('fs');

console.log('🌊 STARTING MATRIX STUDIO...');
console.log('================================');

const app = express();
const server = http.createServer(app);

// Static files
app.use(express.static('public'));

// Main routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'matrix.html'));
});

app.get('/studio', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'studio.html'));
});

app.get('/guest', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'guest.html'));
});

// Basic session API
app.post('/api/session/create', (req, res) => {
    const sessionId = 'MATRIX_' + Math.random().toString(36).substr(2, 9).toUpperCase();
    res.json({
        success: true,
        sessionId: sessionId,
        studioUrl: `http://localhost:8080/studio`,
        guestUrl: `http://localhost:8080/guest`
    });
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: Date.now(),
        port: 8080
    });
});

// Start server
const PORT = 8080;

server.listen(PORT, () => {
    console.log('');
    console.log('╔═════════════════════════════════════════════════════════╗');
    console.log('║                                                              ║');
    console.log('║     ✨ MATRIX STUDIO ONLINE ✨                        ║');
    console.log('║                                                              ║');
    console.log(`║     🌊 Studio: http://localhost:${PORT}                    ║`);
    console.log(`║     🏥 Health:  http://localhost:${PORT}/api/health          ║`);
    console.log('║                                                              ║');
    console.log('╚════════════════════════════════════════════════════════╝');
    console.log('');
    console.log('🌊 Matrix Studio is ready!');
    console.log('⏹️  Press Ctrl+C to stop');
    console.log('');
}).on('error', (err) => {
    console.log('❌ FAILED TO START SERVER');
    console.log('Error:', err.message);
    
    if (err.code === 'EADDRINUSE') {
        console.log('');
        console.log('🔧 SOLUTION: Port 8080 is already in use');
        console.log('   1. Close other apps using port 8080');
        console.log('   2. Restart your computer');
        console.log('   3. Try the emergency server: node EMERGENCY-SERVER.js');
    }
});