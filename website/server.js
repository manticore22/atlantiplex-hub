const http = require('http');
const fs = require('fs');
const path = require('path');

const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://localhost:11434';
const DEFAULT_MODEL = process.env.OLLAMA_MODEL || 'dolphin-llama3:30b';
const PORT = process.env.PORT || 3000;

const MIME_TYPES = {
    '.html': 'text/html',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

const server = http.createServer(async (req, res) => {
    console.log(`${req.method} ${req.url}`);

    if (req.url === '/api/chat' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const { message, model } = JSON.parse(body);
                
                if (!message) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Message is required' }));
                    return;
                }

                const response = await fetch(`${OLLAMA_HOST}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: model || DEFAULT_MODEL,
                        messages: [
                            {
                                role: 'system',
                                content: `You are Atlantiplex AI, an intelligent assistant for Seraphonix Studios. 
You represent an underwater AI innovation company. Be helpful, knowledgeable about AI tools, 
no-code solutions, and the Atlantiplex brand. Use an underwater/ocean theme in your responses.`
                            },
                            { role: 'user', content: message }
                        ],
                        stream: false
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Ollama error:', errorText);
                    res.writeHead(response.status, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'AI service unavailable', details: errorText }));
                    return;
                }

                const data = await response.json();
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ 
                    response: data.message?.content || 'No response from AI',
                    model: data.model || DEFAULT_MODEL
                }));
            } catch (error) {
                console.error('Server error:', error);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: error.message }));
            }
        });
        return;
    }

    if (req.url === '/api/models' && req.method === 'GET') {
        try {
            const response = await fetch(`${OLLAMA_HOST}/api/tags`);
            const data = await response.json();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(data));
        } catch (error) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: error.message }));
        }
        return;
    }

    if (req.url === '/api/status' && req.method === 'GET') {
        try {
            const response = await fetch(`${OLLAMA_HOST}/api/tags`);
            const available = response.ok;
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
                status: available ? 'connected' : 'disconnected',
                ollamaHost: OLLAMA_HOST,
                defaultModel: DEFAULT_MODEL
            }));
        } catch (error) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
                status: 'disconnected',
                error: error.message,
                ollamaHost: OLLAMA_HOST
            }));
        }
        return;
    }

    let filePath = req.url === '/' ? '/index.html' : req.url;
    filePath = path.join(__dirname, filePath);

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'text/plain';

    fs.readFile(filePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404);
                res.end('404 Not Found');
            } else {
                res.writeHead(500);
                res.end('500 Internal Server Error');
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content);
        }
    });
});

server.listen(PORT, () => {
    console.log(`
🌊 Atlantiplex Server Running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 http://localhost:${PORT}
🤖 Ollama: ${OLLAMA_HOST}
📦 Model: ${DEFAULT_MODEL}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    `);
});
